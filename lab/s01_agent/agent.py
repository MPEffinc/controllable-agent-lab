"""S1 에이전트 루프. 이력은 항목 목록으로 직접 관리하고, 매 호출에 전체를 다시 보낸다."""
import copy
import json
import sys
import time
from pathlib import Path

from lab.common import ROOT, LLMHTTPError, call_llm, llm_meta, system_item, tool_result_item, user_item
from lab.s01_agent.tools import HANDLERS, TOOLS

MAX_STEPS = 6
SYSTEM = "너는 운영 보조 에이전트다. 계정 정보가 필요하면 도구로 조회하고, 결과를 한국어로 짧게 답해라."


def run_tool(handlers: dict, call: dict) -> tuple[str, str | None]:
    """도구 하나를 실행해 (결과 문자열, 오류 종류) 를 돌려준다. 오류도 모델에게 결과로 보여 준다."""
    handler = handlers.get(call["name"])
    if handler is None:
        return json.dumps({"error": f"unknown tool {call['name']}"}), "unknown_tool"
    try:
        result = handler(**json.loads(call["arguments"]))
    except (json.JSONDecodeError, TypeError) as e:
        return json.dumps({"error": f"bad arguments ({type(e).__name__})"}), "bad_arguments"
    return json.dumps(result, ensure_ascii=False), None


def run_agent(task: str, system: str, tools: list[dict], handlers: dict, *,
              tag: str, max_steps: int = MAX_STEPS) -> dict:
    items = [system_item(system), user_item(task)]
    steps = []
    outcome, final_text = "max_steps", ""
    for _ in range(max_steps):
        step = {"input_items": copy.deepcopy(items)}
        steps.append(step)
        try:
            r = call_llm(items, tools, tag=tag)
        except LLMHTTPError as e:
            step["http_error"] = {"status_code": e.status_code, "body": e.body}
            outcome = "http_error"
            break
        step.update(
            output_items=r["output_items"], usage=r["usage"], status=r["status"],
            incomplete_reason=r["incomplete_reason"], tool_runs=[],
        )
        if r["status"] != "completed":
            outcome = "incomplete"
            break
        items.extend(r["output_items"])
        if not r["tool_calls"]:
            outcome, final_text = "final_answer", r["text"]
            break
        for call in r["tool_calls"]:
            output, error = run_tool(handlers, call)
            items.append(tool_result_item(call["call_id"], output))
            step["tool_runs"].append({**call, "output": output, "error": error})
    return {"outcome": outcome, "final_text": final_text, "steps": steps}


def save_run(result: dict, *, tag: str, tools: list[dict], max_steps: int = MAX_STEPS) -> Path:
    """이력 JSON 저장. steps[].input_items 가 모델이 그 단계에서 실제로 받은 입력 전체다."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    record = {
        "meta": {**llm_meta(), "tag": tag, "saved_at": stamp, "max_steps": max_steps,
                 "outcome": result["outcome"]},
        "tools": tools,
        "final_text": result["final_text"],
        "steps": result["steps"],
    }
    path = ROOT / "runs" / f"s01_{tag}_{stamp}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    task = sys.argv[1] if len(sys.argv) > 1 else "계정 acct-7 의 상태를 알려 줘."
    tag = "s1-basic"
    result = run_agent(task, SYSTEM, TOOLS, HANDLERS, tag=tag)
    path = save_run(result, tag=tag, tools=TOOLS)
    print(f"outcome: {result['outcome']} (단계 {len(result['steps'])})")
    for i, step in enumerate(result["steps"], 1):
        print(f"  step {i}: usage={step.get('usage')} status={step.get('status')} "
              f"tool_runs={[(t['name'], t['arguments'], t['output']) for t in step.get('tool_runs', [])]}")
        if "http_error" in step:
            print(f"  http_error: {step['http_error']['status_code']}\n{step['http_error']['body']}")
    print(f"final_text: {result['final_text']!r}")
    print(f"saved: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
