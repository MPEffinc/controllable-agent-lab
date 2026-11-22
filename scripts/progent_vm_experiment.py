"""Execute UC01-UC06 with upstream Progent, no LLM or external backend."""

from __future__ import annotations

import argparse
import copy
import importlib.metadata
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from agentdojo.functions_runtime import make_function
from secagent import get_current_config, update_security_policy
from secagent.tool import ValidationError as PolicyValidationError

from scripts.progent_vm_usecase import PIN, MockVMBackend, make_wrapped_tool, manual_policy


def attempt(run_id, event_id, args, policy, expected, reason, schema_probe=False):
    backend = MockVMBackend(run_id)
    tool = make_wrapped_tool(backend, event_id)
    update_security_policy(copy.deepcopy(policy))
    applied = copy.deepcopy(get_current_config())
    before = dict(backend.state)
    schema = None
    if schema_probe:
        try:
            make_function(tool).parameters.model_validate(args)
            schema = "accepted"
        except Exception as exc:
            schema = f"rejected: {type(exc).__name__}"
    error, result, error_origin = None, None, None
    try:
        result = tool(**args)
        decision = "ALLOW"
    except Exception as exc:
        decision = "DENY_OR_INPUT_ERROR"
        error = {"type": type(exc).__name__, "message": str(exc)}
        error_origin = ("progent_policy" if isinstance(exc, PolicyValidationError) else
                        "python_signature" if isinstance(exc, TypeError) else
                        "backend" if isinstance(exc, ValueError) else "unknown")
    record = {
        "run_id": run_id, "event_id": event_id, "time_utc": datetime.now(timezone.utc).isoformat(),
        "input_origin": "direct test harness, not an LLM agent", "tool_call": {"name": "vm_action", "args": args},
        "policy": applied, "rule_explanation": reason,
        "explanation_source": "experiment annotation; original Progent does not expose a matched-rule API",
        "schema_probe": schema, "wrapper_result": decision, "result": result,
        "error": error, "error_origin": error_origin,
        "tool_function_calls": backend.tool_calls, "backend_calls": backend.backend_calls,
        "backend_call_count": len(backend.backend_calls), "before": before,
        "after": dict(backend.state), "history": backend.history,
        "expected": expected,
    }
    record["matches_expectation"] = (decision == expected["decision"] and
        len(backend.backend_calls) == expected["backend_calls"] and
        backend.state == expected["after"] and
        (schema == expected.get("schema") if "schema" in expected else True))
    return record


def run_cases(run_id):
    base = manual_policy()
    initial = {"lab-vm-01": "running", "lab-vm-02": "running"}
    stopped = {**initial, "lab-vm-01": "stopped"}
    deny = lambda: {"decision": "DENY_OR_INPUT_ERROR", "backend_calls": 0, "after": initial}
    records = {
        "UC01": [attempt(run_id, "UC01-1", {"vm_id": "lab-vm-01", "action": "status"}, base,
            {"decision": "ALLOW", "backend_calls": 1, "after": initial}, "priority 1 shutdown Deny does not match; priority 2 status Allow matches")],
        "UC02": [attempt(run_id, "UC02-1", {"vm_id": "lab-vm-01", "action": "shutdown"}, base,
            deny(), "priority 1 explicit shutdown Deny matches before status Allow")],
        "UC03": [attempt(run_id, "UC03-1", {"vm_id": "lab-vm-02", "action": "status"}, base,
            deny(), "tool has rules, but neither lab-vm-01 rule matches; last rule fallback 0 denies")],
        "UC04": [
            attempt(run_id, "UC04-missing-vm", {"action": "status"}, base, deny(),
                "signature.bind rejects missing vm_id before policy checker", True),
            attempt(run_id, "UC04-missing-action", {"vm_id": "lab-vm-01"}, base, deny(),
                "signature.bind rejects missing action before policy checker", True),
            attempt(run_id, "UC04-unknown-action", {"vm_id": "lab-vm-01", "action": "destroy"}, base, deny(),
                "tool schema accepts string; no policy condition matches; fallback 0 denies", True),
            attempt(run_id, "UC04-wrong-type", {"vm_id": 7, "action": "status"}, base, deny(),
                "tool schema rejects integer; direct wrapper reaches Progent argument restriction and fallback 0 denies", True),
        ],
        "UC05": [
            attempt(run_id, "UC05-tie", {"vm_id": "lab-vm-01", "action": "status"},
                {"vm_action": [(10, 0, {}, 0), (10, 1, {"action": {"const": "status"}}, 0)]},
                deny(), "same priority: original sort_policy puts Deny before Allow"),
            attempt(run_id, "UC05-allow-first", {"vm_id": "lab-vm-01", "action": "status"},
                {"vm_action": [(2, 1, {"action": {"const": "status"}}, 0), (1, 0, {}, 0)]},
                {"decision": "ALLOW", "backend_calls": 1, "after": initial},
                "lower numeric priority Allow matches before later Deny"),
        ],
        "UC06": [attempt(run_id, "UC06-1", {"vm_id": "lab-vm-01", "action": "shutdown"}, None,
            {"decision": "ALLOW", "backend_calls": 1, "after": stopped},
            "security_policy=None; original check_tool_call warns and returns without denial")],
    }
    update_security_policy({})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    run_id = "phase2-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    records = run_cases(run_id)
    for case, items in records.items():
        target = args.output_root / case
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{run_id}.json").write_text(json.dumps({"run_id": run_id, "case": case,
            "command": "PYTHONPATH=. " + sys.executable + " -m scripts.progent_vm_experiment --output-root " +
                       str(args.output_root) + " --source-commit " + args.source_commit,
            "source_commit": args.source_commit, "progent_pin": PIN, "python": sys.version.split()[0],
            "packages": {name: importlib.metadata.version(name) for name in ("secagent", "agentdojo", "jsonschema")},
            "llm_model": None, "utility": "not applicable", "security_score": "not applicable",
            "records": items}, indent=2, ensure_ascii=False) + "\n")
        for item in items:
            print(f'{case} {item["event_id"]}: {item["wrapper_result"]}, backend={item["backend_call_count"]}, '
                  f'after={item["after"]}, expected={item["matches_expectation"]}')
    if not all(x["matches_expectation"] for items in records.values() for x in items):
        raise SystemExit(1)
    print(f"run_id={run_id}; all {sum(map(len, records.values()))} attempts matched expectations")


if __name__ == "__main__":
    main()
