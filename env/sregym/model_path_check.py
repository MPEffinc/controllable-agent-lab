"""gpt-6-luna 모델 경로 확인: Responses / Chat Completions / LiteLLM 에서 함수 도구 1개 호출이 되는가.

실행(저장소 루트에서):
  .venv/bin/python env/sregym/model_path_check.py direct          # openai SDK 로 직접
  local/litellm-venv/bin/python env/sregym/model_path_check.py litellm   # LiteLLM(임시 환경)

- 호출마다 토큰과 USD 추정을 local/precheck-raw/e-model-usage.jsonl 에 기록한다(커밋 안 함).
- 누적 USD 가 BUDGET_USD 에 닿으면 이후 시험을 건너뛴다.
- 실제로 간 엔드포인트는 httpx 요청의 경로만 기록한다(헤더·키·호스트 이름은 기록하지 않는다).
- 환경 변수는 이전 실습의 로더(legacy/lab-v0/lab/common.py)로 채운다. 값은 출력하지 않는다.
"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "local" / "precheck-raw"
USAGE_OUT = RAW / "e-model-usage.jsonl"
BUDGET_USD = 0.05
MAX_OUT = 1500  # 추론 토큰 포함 상한. 낮으면 답 없이 incomplete 로 끝날 수 있다.

sys.path.insert(0, str(ROOT / "legacy" / "lab-v0"))
from lab.common import _load_env, _usd  # noqa: E402  (이전 실습의 로더와 가격 상수 재사용)

_load_env()
MODEL = os.environ["LLM_MODEL"]
BASE_URL = os.environ["LLM_BASE_URL"]
API_KEY = os.environ["LLM_API_KEY"]

PROMPT = "계정 acct-7 의 상태를 조회 도구로 확인해 줘."
PARAMS = {"type": "object", "properties": {"account_id": {"type": "string"}}, "required": ["account_id"]}
TOOL_DESC = "계정의 큐 처리 권한 상태를 조회한다."

REQUESTS: list[dict] = []  # httpx 로 실제 나간 요청(메서드, 호스트 구분, 경로)


def _install_request_recorder() -> None:
    """설치된 HTTP 라이브러리(httpx, openai 3.x 의 httpx2)의 Client.send 를 감싸 요청 경로만 기록한다."""
    import importlib

    def wrap(mod):
        orig = mod.Client.send

        def send(self, request, *a, **kw):
            host = "api.openai.com" if request.url.host == "api.openai.com" else "custom-base-url"
            REQUESTS.append({"method": request.method, "host": host, "path": request.url.path})
            return orig(self, request, *a, **kw)

        mod.Client.send = send

    for name in ("httpx", "httpx2"):
        try:
            wrap(importlib.import_module(name))
        except ImportError:
            pass


def _spent() -> float:
    if not USAGE_OUT.exists():
        return 0.0
    return sum(json.loads(l)["usd"] for l in USAGE_OUT.read_text().splitlines())


def _redact(text: str) -> str:
    return text.replace(API_KEY, "***")[:600]


def _log_usage(test: str, usage: dict) -> float:
    usd = _usd(usage["input_tokens"], usage.get("cached_tokens", 0), usage["output_tokens"])
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "test": test, "model": MODEL, **usage, "usd": usd}
    with USAGE_OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return usd


def _run(name: str, fn) -> dict:
    """한 시험을 실행해 결과 dict 를 만든다. 실패해도 예외를 밖으로 내지 않는다."""
    if _spent() >= BUDGET_USD:
        return {"test": name, "skipped": f"누적 비용이 {BUDGET_USD} USD 에 도달"}
    REQUESTS.clear()
    result = {"test": name}
    try:
        result.update(fn())
    except Exception as e:  # noqa: BLE001  시험 도구이므로 모든 실패를 기록하고 계속한다
        status = getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)
        body = getattr(getattr(e, "response", None), "text", None) or getattr(e, "message", None) or str(e)
        result.update({"ok": False, "http_status": status, "error_type": type(e).__name__, "error": _redact(str(body))})
    result["endpoints"] = [f'{r["method"]} {r["path"]}' for r in REQUESTS]
    result["hosts"] = sorted({r["host"] for r in REQUESTS})
    return result


def _tool_summary(calls) -> list[dict]:
    return [{"name": n, "arguments": a} for n, a in calls]


# ---------- 직접(openai SDK) ----------
def _client():
    import openai
    return openai.OpenAI(base_url=BASE_URL, api_key=API_KEY, max_retries=0, timeout=60)


def _responses(effort: str | None):
    def fn():
        kwargs = {"model": MODEL, "input": [{"role": "user", "content": PROMPT}], "max_output_tokens": MAX_OUT,
                  "tools": [{"type": "function", "name": "get_account_status", "description": TOOL_DESC, "parameters": PARAMS}]}
        if effort:
            kwargs["reasoning"] = {"effort": effort}
        d = _client().responses.create(**kwargs).model_dump(exclude_none=True)
        calls = [(i["name"], i["arguments"]) for i in d["output"] if i["type"] == "function_call"]
        u = d["usage"]
        usage = {"input_tokens": u["input_tokens"], "output_tokens": u["output_tokens"],
                 "reasoning_tokens": u.get("output_tokens_details", {}).get("reasoning_tokens"),
                 "cached_tokens": u.get("input_tokens_details", {}).get("cached_tokens", 0)}
        return {"ok": bool(calls), "http_status": 200, "status": d["status"], "tool_calls": _tool_summary(calls),
                "usage": usage, "usd": _log_usage(f"responses effort={effort or 'default'}", usage)}
    return fn


def _chat(effort: str | None):
    def fn():
        kwargs = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT}], "max_completion_tokens": MAX_OUT,
                  "tools": [{"type": "function", "function": {"name": "get_account_status", "description": TOOL_DESC, "parameters": PARAMS}}]}
        if effort:
            kwargs["reasoning_effort"] = effort
        d = _client().chat.completions.create(**kwargs).model_dump(exclude_none=True)
        msg = d["choices"][0]["message"]
        calls = [(c["function"]["name"], c["function"]["arguments"]) for c in msg.get("tool_calls", [])]
        u = d["usage"]
        usage = {"input_tokens": u["prompt_tokens"], "output_tokens": u["completion_tokens"],
                 "reasoning_tokens": u.get("completion_tokens_details", {}).get("reasoning_tokens"),
                 "cached_tokens": u.get("prompt_tokens_details", {}).get("cached_tokens", 0)}
        return {"ok": bool(calls), "http_status": 200, "finish_reason": d["choices"][0]["finish_reason"],
                "tool_calls": _tool_summary(calls), "usage": usage,
                "usd": _log_usage(f"chat effort={effort or 'default'}", usage)}
    return fn


# ---------- LiteLLM ----------
def _llm_common():
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")  # 시작 시 외부에서 가격표를 받지 않는다
    import litellm
    litellm.telemetry = False
    return litellm


def _litellm_chat(effort: str | None, model_prefix: str = "openai/", extra: dict | None = None):
    """extra: completion() 에 덧붙일 인자. SREGym 의 Stratus 설정을 흉내 낼 때(drop_params 등) 쓴다."""
    def fn():
        litellm = _llm_common()
        # max_tokens 대신 max_completion_tokens: 이 모델은 max_tokens 를 받지 않는다(LiteLLM 1.91.0 이 그대로 전달해 400)
        kwargs = {"model": f"{model_prefix}{MODEL}", "api_base": BASE_URL, "api_key": API_KEY, "max_completion_tokens": MAX_OUT,
                  "messages": [{"role": "user", "content": PROMPT}],
                  "tools": [{"type": "function", "function": {"name": "get_account_status", "description": TOOL_DESC, "parameters": PARAMS}}]}
        if effort:
            kwargs["reasoning_effort"] = effort
        kwargs.update(extra or {})
        d = litellm.completion(**kwargs).model_dump()
        msg = d["choices"][0]["message"]
        calls = [(c["function"]["name"], c["function"]["arguments"]) for c in (msg.get("tool_calls") or [])]
        u = d["usage"]
        usage = {"input_tokens": u["prompt_tokens"], "output_tokens": u["completion_tokens"],
                 "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                 "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0}
        return {"ok": bool(calls), "http_status": 200, "tool_calls": _tool_summary(calls), "usage": usage,
                "usd": _log_usage(f"litellm.completion {model_prefix}{MODEL} effort={effort or 'default'}", usage)}
    return fn


def _litellm_responses(effort: str | None):
    def fn():
        litellm = _llm_common()
        kwargs = {"model": f"openai/{MODEL}", "api_base": BASE_URL, "api_key": API_KEY, "max_output_tokens": MAX_OUT,
                  "input": [{"role": "user", "content": PROMPT}],
                  "tools": [{"type": "function", "name": "get_account_status", "description": TOOL_DESC, "parameters": PARAMS}]}
        if effort:
            kwargs["reasoning"] = {"effort": effort}
        r = litellm.responses(**kwargs)
        d = r.model_dump() if hasattr(r, "model_dump") else dict(r)
        calls = [(i["name"], i["arguments"]) for i in d["output"] if i.get("type") == "function_call"]
        u = d["usage"]
        usage = {"input_tokens": u["input_tokens"], "output_tokens": u["output_tokens"],
                 "reasoning_tokens": (u.get("output_tokens_details") or {}).get("reasoning_tokens"),
                 "cached_tokens": (u.get("input_tokens_details") or {}).get("cached_tokens") or 0}
        return {"ok": bool(calls), "http_status": 200, "tool_calls": _tool_summary(calls), "usage": usage,
                "usd": _log_usage(f"litellm.responses effort={effort or 'default'}", usage)}
    return fn


TESTS = {
    "direct": [
        ("Responses + 함수 도구, 추론 기본", _responses(None)),
        ("Responses + 함수 도구, effort=low", _responses("low")),
        ("Chat Completions + 함수 도구, 추론 기본", _chat(None)),
        ("Chat Completions + 함수 도구, reasoning_effort=none", _chat("none")),
        ("Chat Completions + 함수 도구, reasoning_effort=low", _chat("low")),
    ],
    "litellm": [
        ("LiteLLM completion('openai/<model>') + 도구, 추론 기본", _litellm_chat(None)),
        ("LiteLLM completion('openai/<model>') + 도구, reasoning_effort=none", _litellm_chat("none")),
        ("LiteLLM completion('openai/<model>') + 도구, reasoning_effort=low", _litellm_chat("low")),
        ("LiteLLM completion('openai/responses/<model>') + 도구, reasoning_effort=low", _litellm_chat("low", "openai/responses/")),
        ("LiteLLM responses('openai/<model>') + 도구, reasoning effort=low", _litellm_responses("low")),
        # SREGym Stratus 흉내. third_party/SREGym/llm_backend/get_llm_backend.py 에서 직접 읽은 설정:
        # litellm.drop_params=True(전역), temperature=0.0, top_p=0.95, tool_choice="auto", max_tokens 미전달,
        # 추론 강도는 전달하지 않음. 아래 둘째 항목은 "추론 강도를 주면 어떻게 되는가"를 보는 대조다.
        ("[Stratus 흉내] completion + 도구, drop_params=True, temperature=0.0, top_p=0.95, tool_choice=auto",
         _litellm_chat(None, extra={"drop_params": True, "temperature": 0.0, "top_p": 0.95, "tool_choice": "auto"})),
        ("[Stratus 흉내] 위 설정에 reasoning_effort=low 를 더함(drop_params=True)",
         _litellm_chat("low", extra={"drop_params": True, "temperature": 0.0, "top_p": 0.95, "tool_choice": "auto"})),
        ("completion + 도구, reasoning_effort=none, allowed_openai_params=['reasoning_effort']",
         _litellm_chat("none", extra={"allowed_openai_params": ["reasoning_effort"]})),
    ],
}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "direct"
    RAW.mkdir(parents=True, exist_ok=True)
    _install_request_recorder()
    results = [_run(name, fn) | {"name": name} for name, fn in TESTS[mode]]
    extra = {}
    if mode == "litellm":
        import importlib.metadata as md
        extra["litellm_version"] = md.version("litellm")
    out = RAW / f"e-model-results-{mode}.json"
    out.write_text(json.dumps({"mode": mode, "model": MODEL, "max_out": MAX_OUT, **extra, "results": results},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        u = r.get("usage") or {}
        print(f'- {r["name"]}\n    ok={r.get("ok")} http={r.get("http_status")} endpoints={r.get("endpoints")} hosts={r.get("hosts")}'
              f'\n    tool_calls={r.get("tool_calls")} usage(in/out/reasoning)={u.get("input_tokens")}/{u.get("output_tokens")}/{u.get("reasoning_tokens")} usd={r.get("usd")}'
              f'\n    error={r.get("error")}{r.get("skipped") or ""}')
    print(f"누적 USD(이번 세션 모델 경로 시험): {_spent():.6f} / 상한 {BUDGET_USD}")


if __name__ == "__main__":
    main()
