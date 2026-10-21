"""공용 LLM 호출. 모델 호출은 모두 call_llm() 하나를 지난다 (CLAUDE.md '비용')."""
import functools
import json
import os
import time
from pathlib import Path

import openai
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
USAGE_LOG = ROOT / "runs" / "usage.jsonl"
ERROR_LOG = ROOT / "runs" / "llm_errors.jsonl"
LLM_ENV = Path.home() / ".config" / "controllable_agent" / "llm.env"


class TokenBudgetExceeded(Exception):
    """누적 토큰이 LAB_MAX_TOKENS 에 도달했다."""


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


def _used_tokens() -> int:
    if not USAGE_LOG.exists():
        return 0
    total = 0
    for line in USAGE_LOG.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        total += rec["input_tokens"] + rec["output_tokens"]
    return total


@functools.cache
def _load_env() -> None:
    load_dotenv(LLM_ENV, override=False)


def reasoning_effort() -> str:
    """LLM_REASONING_EFFORT 값. 미설정이면 서버 기본값을 쓰므로 'default' 로 적는다."""
    _load_env()
    return os.environ.get("LLM_REASONING_EFFORT") or "default"


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
    limit = int(os.environ.get("LAB_MAX_TOKENS", 300000))
    if _used_tokens() >= limit:
        raise TokenBudgetExceeded(f"누적 토큰이 상한 {limit} 에 도달했다")
    model = os.environ["LLM_MODEL"]
    kwargs = {
        "model": model,
        "input": input_items,
        "max_output_tokens": int(os.environ.get("LAB_MAX_OUTPUT_TOKENS", 800)),
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
    usage = {
        "input_tokens": data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
        "reasoning_tokens": data["usage"].get("output_tokens_details", {}).get("reasoning_tokens"),
    }
    status = data["status"]
    incomplete_reason = data.get("incomplete_details", {}).get("reason")
    _append_jsonl(USAGE_LOG, {
        "ts": _now(), "tag": tag, "model": model, "status": status, "effort": effort, **usage,
    })
    return _normalize(data["output"], usage, status, incomplete_reason)
