"""Deploy one fresh SREGym task and run the deterministic or model pilot path."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PILOT_DIR = Path(__file__).resolve().parent
ROOT = PILOT_DIR.parents[2]
sys.path.insert(0, str(PILOT_DIR))
sys.path.insert(0, str(ROOT / "env" / "sregym" / "oracle-gap"))

from core import (  # noqa: E402
    PLAN_VERSION,
    PROBLEM,
    RouteObserver,
    SelectorGate,
    SelectorGateway,
    cluster_snapshot,
    initial_state_valid,
    judge,
    make_request,
    now,
)
from logger import init_logger  # noqa: E402
from sregym.conductor.conductor import Conductor, ConductorConfig  # noqa: E402
from sregym.conductor.constants import StartProblemResult  # noqa: E402


AGENT_PY = ROOT / "local" / "agents-venv" / "bin" / "python"
AGENT_SCRIPT = PILOT_DIR / "agent.py"


def wait_for_initial_state(namespace: str, timeout: int = 40) -> tuple[dict, bool, list[str]]:
    deadline = time.monotonic() + timeout
    last = cluster_snapshot(namespace)
    valid, reasons = initial_state_valid(last)
    while not valid and time.monotonic() < deadline:
        time.sleep(2)
        last = cluster_snapshot(namespace)
        valid, reasons = initial_state_valid(last)
    return last, valid, reasons


def deterministic_action(namespace: str, observation: str, gate: str, events: Path) -> dict:
    observer = RouteObserver(namespace, observation, events)
    delivered = observer.observe("deterministic-diagnosis")
    request = make_request(namespace, delivered["service"], delivered["intended_workload"])
    gateway = SelectorGateway(SelectorGate(gate, namespace), events)
    write = gateway.execute(request)
    return {
        "status": "completed",
        "observation": delivered,
        "handoff_report": {
            "observation_id": delivered["observation_id"],
            "service": delivered["service"],
            "intended_workload": delivered["intended_workload"],
            "proposed_selector": request["selector"],
        },
        "write_requests": [write],
        "llm_calls": 0,
        "usd_estimate": 0.0,
    }


def run_model(args: argparse.Namespace, namespace: str, tag: str, events: Path, summary: Path) -> dict:
    command = [
        str(AGENT_PY),
        str(AGENT_SCRIPT),
        "--namespace",
        namespace,
        "--observation",
        args.observation,
        "--gate",
        args.gate,
        "--events",
        str(events),
        "--summary",
        str(summary),
        "--usage",
        str(Path(args.outdir) / "usage.jsonl"),
        "--tag",
        tag,
        "--max-turns",
        "8",
        "--timeout",
        "300",
    ]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=420, env=os.environ.copy())
        process = {
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-1000:],
            "stderr_tail": (proc.stderr or "")[-1500:],
        }
    except subprocess.TimeoutExpired as exc:
        process = {"returncode": "hard_timeout", "stdout_tail": "", "stderr_tail": str(exc)}
    result = json.loads(summary.read_text(encoding="utf-8")) if summary.exists() else {"status": "no_summary"}
    result["process"] = process
    return result


async def run(args: argparse.Namespace) -> dict:
    init_logger()
    trial_started = time.monotonic()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.kind}-{args.observation}-{args.gate}-r{args.rep}"
    events = outdir / f"{tag}__events.jsonl"
    agent_summary = outdir / f"{tag}__agent.json"
    events.unlink(missing_ok=True)
    agent_summary.unlink(missing_ok=True)
    record: dict = {
        "plan_version": PLAN_VERSION,
        "problem": PROBLEM,
        "kind": args.kind,
        "observation": args.observation,
        "gate": args.gate,
        "rep": args.rep,
        "tag": tag,
        "started_at": now(),
        "validity": "unknown",
    }
    conductor = Conductor(config=ConductorConfig(deploy_loki=False, stages=("mitigation",)))
    conductor.problem_id = PROBLEM
    started = False
    submitted = False
    try:
        start_result = await conductor.start_problem()
        record["start_problem"] = str(start_result)
        if start_result != StartProblemResult.SUCCESS:
            record["error"] = f"start_problem failed: {start_result}"
            return record
        started = True
        namespace = conductor.problem.namespace
        record["namespace"] = namespace
        before, initial_valid, initial_reasons = wait_for_initial_state(namespace)
        record["before"] = before
        record["initial_state"] = {"valid": initial_valid, "reasons": initial_reasons}
        if not initial_valid:
            record["validity"] = "invalid"
            record["invalid_reason"] = "initial state did not match the precommitted task state"
            agent_result = {"status": "not_run", "write_requests": [], "llm_calls": 0, "usd_estimate": 0.0}
        elif args.kind == "deterministic":
            agent_result = deterministic_action(namespace, args.observation, args.gate, events)
        else:
            agent_result = run_model(args, namespace, tag, events, agent_summary)
        record["agent"] = agent_result
        time.sleep(4)
        after = cluster_snapshot(namespace)
        record["after"] = after
        writes = agent_result.get("write_requests") or []
        last_write = writes[-1] if writes else None
        request = (last_write or {}).get("request")
        record["security_judgment"] = judge(request, last_write, before, after)
        gate_decision = record["security_judgment"]["gate_decision"]
        effect_valid = (
            record["security_judgment"]["applied_as_requested"] is True
            if gate_decision == "allow"
            else record["security_judgment"]["actual_change"] is False
        )
        record["write_effect_validation"] = {
            "valid": effect_valid,
            "rule": "allowed requests must match actual selector; denied/held requests must not change it",
        }
        mutation_rows = []
        if events.exists():
            mutation_rows = [
                json.loads(line)
                for line in events.read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("event") == "observation"
            ]
        mutation_ok = bool(mutation_rows) and all(
            row.get("mutation", {}).get("applied") == (args.observation == "forged") for row in mutation_rows
        )
        record["observation_validation"] = {
            "calls": len(mutation_rows),
            "expected_mutation": args.observation == "forged",
            "all_calls_match": mutation_ok,
        }
        if initial_valid:
            record["validity"] = (
                "valid"
                if (
                    agent_result.get("status") == "completed"
                    and mutation_ok
                    and last_write is not None
                    and effect_valid
                )
                else "error"
            )

        record["submit_response"] = await conductor.submit("")
        submitted = True
        waited = 0
        while conductor.submission_stage != "done" and waited < 900:
            await asyncio.sleep(2)
            waited += 2
        record["final_stage"] = conductor.submission_stage
        record["results"] = dict(conductor.results)
        record["mitigation_success"] = (conductor.results.get("Mitigation") or {}).get("success")
        record["cleanup_wait_s"] = waited
        if conductor.submission_stage != "done":
            record["validity"] = "error"
            record["error"] = "evaluation/cleanup did not finish within 900s"
        return record
    except Exception as exc:  # noqa: BLE001 - preserve failures and still clean up
        record["validity"] = "error"
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record
    finally:
        if started and not submitted:
            try:
                conductor._finish_problem()  # SREGym's idempotent safety-net cleanup path
            except Exception as exc:  # noqa: BLE001
                record["cleanup_error"] = f"{type(exc).__name__}: {exc}"
        record["finished_at"] = now()
        record["elapsed_s"] = round(time.monotonic() - trial_started, 3)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["deterministic", "model"], required=True)
    parser.add_argument("--observation", choices=["normal", "forged"], required=True)
    parser.add_argument("--gate", choices=["G0", "G1", "G2"], required=True)
    parser.add_argument("--rep", type=int, required=True)
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()
    path = Path(args.outdir) / f"{args.kind}-{args.observation}-{args.gate}-r{args.rep}__trial.json"
    try:
        result = asyncio.run(run(args))
    except Exception as exc:  # noqa: BLE001
        result = {
            "plan_version": PLAN_VERSION,
            "problem": PROBLEM,
            "kind": args.kind,
            "observation": args.observation,
            "gate": args.gate,
            "rep": args.rep,
            "validity": "error",
            "error": f"{type(exc).__name__}: {exc}",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(
        f"PILOT_TRIAL {args.kind} {args.observation} {args.gate} r{args.rep}: "
        f"validity={result.get('validity')} mitigation={result.get('mitigation_success')} "
        f"error={result.get('error')}"
    )
    raise SystemExit(0 if result.get("validity") == "valid" else 2)


if __name__ == "__main__":
    main()

