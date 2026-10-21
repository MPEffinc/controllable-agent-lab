"""P3 구동기: 한 문제에 대해 별도 프로세스 에이전트를 한 번 실행하고 복구만 채점한다.

실행(격리 래퍼를 거친다):
  env/sregym/sregym.sh --py /절대경로/env/sregym/agent/run_agent_trial.py \
      --problem network_policy_block --agent dummy|single --rep 1 --outdir /절대경로/local/overnight/p3

SREGym 은 업스트림 수정 없이 Conductor 를 코드로 호출한다(PLAN.md 의 P2 구동기와 같은 방식, stages=("mitigation",)).
에이전트는 SREGym 컨테이너 밖의 별도 프로세스(agents-venv)이고, 도구로만 클러스터에 닿는다(tools.py).
"submit" 은 구동기가 에이전트 종료 후 `conductor.submit("")` 으로 대신한다(복구 단계 제출은 빈 문자열, SREGym 의 드라이버와 같음).
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "oracle-gap"))
from logger import init_logger  # noqa: E402
from run_variant import snapshot  # noqa: E402
from sregym.conductor.conductor import Conductor, ConductorConfig  # noqa: E402
from sregym.conductor.constants import StartProblemResult  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
AGENT_PY = ROOT / "local" / "agents-venv" / "bin" / "python"
AGENT_MAIN = ROOT / "env" / "sregym" / "agent" / "agent_main.py"
EXEC_PROBLEMS = ("storage_user_unregistered",)  # DB 클라이언트 실행이 필요한 문제만 kubectl_exec 를 켠다


async def main_async(a) -> dict:
    init_logger()
    out = Path(a.outdir)
    rec = {"problem": a.problem, "agent": a.agent, "rep": a.rep, "start": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    conductor = Conductor(config=ConductorConfig(deploy_loki=False, stages=("mitigation",)))
    conductor.problem_id = a.problem
    res = await conductor.start_problem()
    if res != StartProblemResult.SUCCESS:
        rec["error"] = f"start_problem 실패: {res}"
        return rec
    ns = conductor.problem.namespace
    app = conductor.app
    rec["namespace"] = ns
    rec["before"] = snapshot(a.problem, ns)

    tag = f"p3-{a.problem}-{a.agent}-r{a.rep}"
    events = out / f"{tag}__events.jsonl"
    summary = out / f"{tag}__agent.json"
    for f in (events, summary):
        f.unlink(missing_ok=True)
    cmd = [str(AGENT_PY), str(AGENT_MAIN), "--agent", a.agent, "--namespace", ns, "--app-name", str(app.app_name),
           "--description", str(app.description), "--events", str(events), "--summary", str(summary), "--tag", tag,
           "--allow-exec", "1" if a.problem.startswith(EXEC_PROBLEMS) else "0",
           "--max-turns", str(a.max_turns), "--timeout", str(a.timeout)]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout + 120, env=os.environ.copy())
        rec["agent_rc"] = p.returncode
        rec["agent_stdout_tail"] = (p.stdout or "")[-400:]
        rec["agent_stderr_tail"] = (p.stderr or "")[-800:]
    except subprocess.TimeoutExpired:
        rec["agent_rc"] = "hard_timeout"
    rec["agent_elapsed_s"] = round(time.time() - t0, 1)
    rec["agent"] = json.loads(summary.read_text()) if summary.exists() else {"status": "no_summary"}

    time.sleep(10)
    rec["after"] = snapshot(a.problem, ns)
    t1 = time.time()
    rec["submit_response"] = await conductor.submit("")
    waited = 0
    while conductor.submission_stage != "done" and waited < 900:
        await asyncio.sleep(5)
        waited += 5
    rec["final_stage"] = conductor.submission_stage
    rec["eval_cleanup_s"] = round(time.time() - t1, 1)
    rec["results"] = dict(conductor.results)
    rec["mitigation_success"] = (conductor.results.get("Mitigation") or {}).get("success")
    return rec


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--problem", required=True)
    p.add_argument("--agent", choices=["dummy", "single"], required=True)
    p.add_argument("--rep", type=int, required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-turns", type=int, default=25)
    p.add_argument("--timeout", type=int, default=720)
    a = p.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"p3-{a.problem}-{a.agent}-r{a.rep}__trial.json"
    try:
        rec = asyncio.run(main_async(a))
    except Exception as e:  # noqa: BLE001
        rec = {"problem": a.problem, "agent": a.agent, "rep": a.rep, "error": f"{type(e).__name__}: {e}"}
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"RESULT {a.problem} {a.agent} r{a.rep}: mitigation_success={rec.get('mitigation_success')} "
          f"agent_status={(rec.get('agent') or {}).get('status')} error={rec.get('error')}")
    sys.exit(0 if "error" not in rec else 2)


if __name__ == "__main__":
    main()
