"""공용 LLM 호출. 모델 호출은 모두 call_llm() 하나를 지난다 (CLAUDE.md '비용')."""
import functools
import json
import os
import sys
import time
from pathlib import Path

import openai
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
USAGE_LOG = ROOT / "runs" / "usage.jsonl"
ERROR_LOG = ROOT / "runs" / "llm_errors.jsonl"
LLM_ENV = Path.home() / ".config" / "controllable_agent" / "llm.env"

# 가격 (USD / 100만 토큰). 2026-10-21 확인. 제3자 요약 기준이므로 OpenAI 가격 페이지로 재확인 필요.
PRICE_INPUT = 0.10
PRICE_CACHED_INPUT = 0.01
PRICE_OUTPUT = 0.50


class TokenBudgetExceeded(Exception):
    """누적 USD 가 LAB_MAX_USD 에, 또는 누적 토큰이 LAB_MAX_TOKENS 에 도달했다."""


class LLMHTTPError(Exception):
    """non-2xx 응답. 상태 코드와 오류 본문만 들고 있다."""

    def __init__(self, status_code: int, body: str):
        super().__init__(f"HTTP {status_code}: {body[:200]}")
        self.status_code = status_code
        self.body = body


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _usd(input_tokens: int, cached_tokens: int, output_tokens: int) -> float:
    """캐시 입력은 입력 토큰의 부분집합, 출력 토큰에는 추론 토큰이 포함된 것으로 계산한다."""
    uncached = input_tokens - cached_tokens
    return round((uncached * PRICE_INPUT + cached_tokens * PRICE_CACHED_INPUT
                  + output_tokens * PRICE_OUTPUT) / 1_000_000, 9)


def _usage_totals() -> tuple[int, float]:
    """usage.jsonl 의 (누적 토큰, 누적 USD). usd_estimate 가 없는 옛 줄은 토큰으로 계산한다."""
    tokens, usd = 0, 0.0
    if USAGE_LOG.exists():
        for line in USAGE_LOG.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            tokens += rec["input_tokens"] + rec["output_tokens"]
            usd += rec.get("usd_estimate", _usd(rec["input_tokens"], 0, rec["output_tokens"]))
    return tokens, usd


def _anomaly(usage: dict, requested_max: int) -> str | None:
    """응답 usage 가 이상하면 사유 문자열, 정상이면 None."""
    problems = []
    if usage["output_tokens"] > requested_max:
        problems.append(f"output_tokens({usage['output_tokens']}) > max_output_tokens({requested_max})")
    reasoning = usage["reasoning_tokens"]
    if reasoning is not None and reasoning > usage["output_tokens"]:
        problems.append(f"reasoning_tokens({reasoning}) > output_tokens({usage['output_tokens']})")
    return "; ".join(problems) or None


@functools.cache
def _load_env() -> None:
    load_dotenv(LLM_ENV, override=False)


def reasoning_effort() -> str:
    """LLM_REASONING_EFFORT 값. 미설정이면 서버 기본값을 쓰므로 'default' 로 적는다."""
    _load_env()
    return os.environ.get("LLM_REASONING_EFFORT") or "default"


def set_reasoning_effort(effort: str) -> None:
    """'default' 는 LLM_REASONING_EFFORT 미설정(서버 기본값)을 뜻한다. llm.env 를 먼저 읽어 둔다."""
    _load_env()
    if effort == "default":
        os.environ.pop("LLM_REASONING_EFFORT", None)
    else:
        os.environ["LLM_REASONING_EFFORT"] = effort


def max_output_tokens() -> int:
    _load_env()
    return int(os.environ.get("LAB_MAX_OUTPUT_TOKENS", 25000))


def llm_meta() -> dict:
    """이력 JSON 메타데이터용. call_llm 이 실제로 쓰는 설정값이다."""
    _load_env()
    return {
        "model": os.environ["LLM_MODEL"],
        "effort": reasoning_effort(),
        "max_output_tokens": max_output_tokens(),
    }


@functools.cache
def get_client() -> openai.OpenAI:
    _load_env()
    return openai.OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        max_retries=0,
        timeout=60,
    )


def record_http_error(e: openai.APIStatusError, *, api: str, tag: str = "") -> LLMHTTPError:
    """상태 코드와 본문만 기록한다. 헤더는 저장하지 않고, 본문 속 키 값은 가린다."""
    body = e.response.text[:2000].replace(os.environ["LLM_API_KEY"], "***")
    _append_jsonl(ERROR_LOG, {
        "ts": _now(), "tag": tag, "api": api, "model": os.environ["LLM_MODEL"],
        "status_code": e.status_code, "body": body,
    })
    return LLMHTTPError(e.status_code, body)


def _normalize(output_items: list[dict], usage: dict, status: str, incomplete_reason: str | None) -> dict:
    text = "".join(
        part["text"]
        for item in output_items if item["type"] == "message"
        for part in item["content"] if part["type"] == "output_text"
    )
    tool_calls = [
        {"call_id": item["call_id"], "name": item["name"], "arguments": item["arguments"]}
        for item in output_items if item["type"] == "function_call"
    ]
    return {
        "text": text, "tool_calls": tool_calls, "output_items": output_items, "usage": usage,
        "status": status, "incomplete_reason": incomplete_reason,
    }


def call_llm(input_items: list[dict], tools: list[dict] | None = None, *, tag: str = "") -> dict:
    client = get_client()
    used_tokens, used_usd = _usage_totals()
    max_usd = float(os.environ.get("LAB_MAX_USD", 5.00))
    if used_usd >= max_usd:
        raise TokenBudgetExceeded(f"누적 비용 {used_usd:.4f} USD 가 상한 {max_usd} USD 에 도달했다")
    max_tokens = int(os.environ.get("LAB_MAX_TOKENS", 50000000))
    if used_tokens >= max_tokens:
        raise TokenBudgetExceeded(f"누적 토큰 {used_tokens} 이 상한 {max_tokens} 에 도달했다")
    model = os.environ["LLM_MODEL"]
    requested_max = max_output_tokens()
    kwargs = {
        "model": model,
        "input": input_items,
        "max_output_tokens": requested_max,
    }
    effort = reasoning_effort()
    if effort != "default":
        kwargs["reasoning"] = {"effort": effort}
    if tools:
        kwargs["tools"] = [{"type": "function", **tool} for tool in tools]
    try:
        resp = client.responses.create(**kwargs)
    except openai.APIStatusError as e:
        raise record_http_error(e, api="responses", tag=tag) from e
    data = resp.model_dump(exclude_none=True)
    raw = data["usage"]
    usage = {
        "input_tokens": raw["input_tokens"],
        "cached_tokens": raw.get("input_tokens_details", {}).get("cached_tokens", 0),
        "output_tokens": raw["output_tokens"],
        "reasoning_tokens": raw.get("output_tokens_details", {}).get("reasoning_tokens"),
    }
    usage["usd_estimate"] = _usd(usage["input_tokens"], usage["cached_tokens"], usage["output_tokens"])
    usage["warning"] = _anomaly(usage, requested_max)
    if usage["warning"]:
        print(f"[경고] {tag}: {usage['warning']}", file=sys.stderr)
    status = data["status"]
    incomplete_reason = data.get("incomplete_details", {}).get("reason")
    log_usage = {k: v for k, v in usage.items() if not (k == "warning" and v is None)}
    _append_jsonl(USAGE_LOG, {
        "ts": _now(), "tag": tag, "model": model, "status": status, "effort": effort, **log_usage,
    })
    return _normalize(data["output"], usage, status, incomplete_reason)


def system_item(text: str) -> dict:
    return {"role": "system", "content": text}


def user_item(text: str) -> dict:
    return {"role": "user", "content": text}


def tool_result_item(call_id: str, output) -> dict:
    """도구 결과를 call_id 로 짝지어 붙이는 항목. 문자열이 아니면 JSON 으로 바꾼다."""
    if not isinstance(output, str):
        output = json.dumps(output, ensure_ascii=False)
    return {"type": "function_call_output", "call_id": call_id, "output": output}
