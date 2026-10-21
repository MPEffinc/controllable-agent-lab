"""P3 단일 에이전트(진단·수리 도구 모두 보유). OpenAI Agents SDK + gpt-6-luna + Responses API.

SREGym 과 별개의 프로세스로 실행된다(구동기 run_agent_trial.py 가 띄운다). 실행은 agents-venv 에서:
  local/agents-venv/bin/python env/sregym/agent/agent_main.py --agent single --namespace hotel-reservation ...

--agent dummy : LLM 을 쓰지 않는 더미. 도구 한 번 호출 후 종료(등록·연결 확인용).
--agent single: 단일 에이전트.
환경 변수는 이전 실습의 로더로 채우고(키 값 출력·기록 없음), SDK 트레이싱은 끈다(외부 전송 방지).
비용은 호출마다 local/overnight/usage.jsonl 에 기록하고, 누적이 상한(기본 3.0 USD)에 닿으면 중단한다.
"""
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "legacy" / "lab-v0"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab.common import _load_env, _usd  # noqa: E402  (키는 로더가 환경 변수로만 채운다)

from tools import ToolBox  # noqa: E402

USAGE_FILE = ROOT / "local" / "overnight" / "usage.jsonl"
BUDGET_USD = float(os.environ.get("OVERNIGHT_BUDGET_USD", "3.0"))
MAX_OUTPUT_TOKENS = 25000  # 추론 토큰 포함. 낮으면 답 없이 incomplete 가 된다(CLAUDE.md)

INSTRUCTIONS = """You are an SRE agent tasked with fixing an issue in a Kubernetes application.

Application: {app_name}
Namespace: {namespace}

{description}

CRITICAL: You are running in an AUTOMATED environment. Work autonomously and make all decisions yourself.
DO NOT ask for confirmation or approval.

TASK: MITIGATION
- Investigate the application in namespace '{namespace}', identify the root cause, and implement a fix.
- Your mitigation is evaluated on whether the application is healthy after your changes.
- When you have applied the fix and verified it, stop and reply with a short summary of what you changed.
  The harness submits the result for you; you do not need to submit anything.

Tools: kubectl_read (get/describe/logs/top), kubectl_write (delete/scale/patch/rollout/label/annotate/set/create),
kubectl_apply_manifest (apply a YAML manifest){exec_note}. All tools are limited to namespace '{namespace}'.
Pass kubectl arguments as a list without the leading 'kubectl' (for example ["get", "pods"]).
"""


def spent_total() -> float:
    if not USAGE_FILE.exists():
        return 0.0
    return sum(json.loads(l).get("usd", 0.0) for l in USAGE_FILE.read_text().splitlines() if l.strip())


def log_usage(tag: str, usage: dict) -> float:
    usd = _usd(usage["input_tokens"], usage.get("cached_tokens", 0), usage["output_tokens"])
    USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USAGE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "tag": tag, **usage, "usd": usd}) + "\n")
    return usd


def run_dummy(tb: ToolBox, out: dict) -> None:
    out["final_output"] = tb.kubectl_read(["get", "pods"], role="dummy")[:500]
    out["status"] = "completed"


async def run_single(a, tb: ToolBox, out: dict) -> None:
    from agents import Agent, ModelSettings, OpenAIResponsesModel, RunHooks, Runner, function_tool, set_tracing_disabled
    from openai import AsyncOpenAI

    set_tracing_disabled(True)
    _load_env()
    model_name = os.environ["LLM_MODEL"]
    client = AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"], max_retries=0, timeout=120)
    out["model"] = model_name

    @function_tool
    def kubectl_read(args: list[str]) -> str:
        """Run a read-only kubectl command (get, describe, logs, top, explain). args exclude the leading 'kubectl'."""
        return tb.kubectl_read(args)

    @function_tool
    def kubectl_write(args: list[str]) -> str:
        """Run a modifying kubectl command (delete, scale, patch, rollout, label, annotate, set, create). args exclude 'kubectl'."""
        return tb.kubectl_write(args)

    @function_tool
    def kubectl_apply_manifest(manifest: str) -> str:
        """Apply a YAML manifest (kubectl apply -f -) in the application namespace."""
        return tb.kubectl_apply_manifest(manifest)

    tools = [kubectl_read, kubectl_write, kubectl_apply_manifest]
    if tb.allow_exec:
        @function_tool
        def kubectl_exec(deployment: str, command: list[str]) -> str:
            """Run a database client inside a deployment's pod. command[0] must be 'mongo' or 'mongosh'; no shell is available."""
            return tb.kubectl_exec(deployment, command)
        tools.append(kubectl_exec)

    class Budget(RunHooks):
        def __init__(self):
            self.run_usd = 0.0
            self.calls = 0
            self.stop = False

        async def on_llm_end(self, context, agent, response):
            u = response.usage
            usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                     "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                     "cached_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
            self.run_usd += log_usage(a.tag, usage)
            self.calls += 1
            if spent_total() >= BUDGET_USD:
                self.stop = True
                raise RuntimeError(f"밤 누적 비용 상한 {BUDGET_USD} USD 도달")

    exec_note = ", kubectl_exec (run `mongo`/`mongosh` inside a deployment's pod)" if tb.allow_exec else ""
    agent = Agent(
        name="sre-single",
        instructions=INSTRUCTIONS.format(app_name=a.app_name, namespace=a.namespace, description=a.description, exec_note=exec_note),
        model=OpenAIResponsesModel(model=model_name, openai_client=client),
        model_settings=ModelSettings(max_tokens=MAX_OUTPUT_TOKENS),
        tools=tools,
    )
    hooks = Budget()
    out["status"] = "running"
    try:
        result = await asyncio.wait_for(
            Runner.run(agent, "Fix the issue in the application now.", max_turns=a.max_turns, hooks=hooks),
            timeout=a.timeout)
        out["final_output"] = str(result.final_output)[:2000]
        out["status"] = "completed"
        out["n_raw_responses"] = len(result.raw_responses)
    except asyncio.TimeoutError:
        out["status"] = "timeout"
    except Exception as e:  # noqa: BLE001  능력 실패(max_turns, 호출 오류)와 보안/복구 실패를 구분하려고 종류를 남긴다
        out["status"] = "error"
        out["error_type"] = type(e).__name__
        out["error"] = str(e)[:600]
    out["llm_calls"] = hooks.calls
    out["run_usd"] = round(hooks.run_usd, 6)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--agent", choices=["dummy", "single"], required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--app-name", default="unknown")
    p.add_argument("--description", default="")
    p.add_argument("--allow-exec", type=int, default=0)
    p.add_argument("--events", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--tag", default="p3")
    p.add_argument("--max-turns", type=int, default=25)
    p.add_argument("--timeout", type=int, default=720)
    a = p.parse_args()

    Path(a.events).parent.mkdir(parents=True, exist_ok=True)
    tb = ToolBox(a.namespace, Path(a.events), allow_exec=bool(a.allow_exec))
    out = {"agent": a.agent, "tag": a.tag, "start": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    t0 = time.time()
    if spent_total() >= BUDGET_USD:
        out["status"] = "budget_exhausted_before_start"
    elif a.agent == "dummy":
        run_dummy(tb, out)
    else:
        asyncio.run(run_single(a, tb, out))
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["tool_calls"] = [{"tool": c["tool"], "args": c["args"], "ok": c["ok"]} for c in tb.calls]
    Path(a.summary).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"AGENT {a.agent} status={out.get('status')} calls={out.get('llm_calls')} usd={out.get('run_usd')}")


if __name__ == "__main__":
    main()
