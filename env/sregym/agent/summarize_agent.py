"""P3/P4 결과(local/overnight/p3, p4)를 집계한다. 사용: python3 summarize_agent.py <디렉터리> <agent: single|split|dummy>
능력 실패(에이전트 status 가 completed 가 아님, 도구 오류·incomplete)와 오라클 FAIL(복구 실패)을 구분하고,
에이전트가 실제로 한 변경(쓰기·exec·apply 도구 호출)을 나열한다."""
import json
import sys
from pathlib import Path

d, agent = Path(sys.argv[1]), sys.argv[2]
usage = [json.loads(l) for l in (Path(__file__).resolve().parents[3] / "local/overnight/usage.jsonl").read_text().splitlines() if l.strip()]
WRITE_TOOLS = {"kubectl_write", "kubectl_apply_manifest", "kubectl_exec"}

print("| 문제 | 반복 | 오라클 | 에이전트 상태 | LLM 호출 | 입력/출력(추론) 토큰 | USD | 도구 호출(읽기/쓰기류) | 에이전트가 한 변경 |")
print("|---|---|---|---|---|---|---|---|---|")
tot = {"pass": 0, "n": 0, "cap_fail": 0, "usd": 0.0}
for f in sorted(d.glob(f"p3-*-{agent}-r*__trial.json")):
    t = json.loads(f.read_text())
    if "error" in t and "agent" not in t:
        print(f"| {t['problem']} | {t['rep']} | 판정불가 | 구동 오류 | | | | | {t['error'][:80]} |")
        continue
    a = t["agent"]
    tag = f"p3-{t['problem']}-{agent}-r{t['rep']}"
    u = [x for x in usage if x["tag"] == tag]
    tin, tout, tr = sum(x["input_tokens"] for x in u), sum(x["output_tokens"] for x in u), sum((x.get("reasoning_tokens") or 0) for x in u)
    usd = sum(x["usd"] for x in u)
    calls = a.get("tool_calls", [])
    writes = [c for c in calls if c["tool"] in WRITE_TOOLS]
    wtxt = "; ".join(f"{c['tool']}({json.dumps(c['args'], ensure_ascii=False)[:90]}){'' if c['ok'] else ' 거부/실패'}" for c in writes) or "없음"
    ok = t.get("mitigation_success")
    cap = a.get("status") != "completed"
    tot["n"] += 1
    tot["pass"] += 1 if ok else 0
    tot["cap_fail"] += 1 if cap else 0
    tot["usd"] += usd
    print(f"| {t['problem']} | {t['rep']} | {'PASS' if ok else 'FAIL' if ok is False else '판정불가'} | {a.get('status')} | {a.get('llm_calls')} | "
          f"{tin}/{tout}({tr}) | {usd:.4f} | {len(calls)-len(writes)}/{len(writes)} | {wtxt} |")
print(f"\n합계: 실행 {tot['n']}회, 오라클 PASS {tot['pass']}회, 능력 실패(에이전트 비정상 종료) {tot['cap_fail']}회, 비용 {tot['usd']:.4f} USD")
