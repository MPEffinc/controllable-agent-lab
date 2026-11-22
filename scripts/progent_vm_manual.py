"""Interactive, API-free VM policy exercise using upstream Progent."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from secagent import get_current_config, update_security_policy

from scripts.progent_vm_usecase import MockVMBackend, make_wrapped_tool, manual_policy


def main():
    run_id = "manual-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    backend = MockVMBackend(run_id)
    path = Path("local/progent-vm/manual") / f"{run_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Run ID: {run_id}; local log: {path}")
    print("Profiles: scoped (lab-vm-01 status allow/shutdown deny), status-both (both VMs status allow).")
    print("Enter reset to restore both VMs, or quit to stop. No LLM/API/SSH is used.")
    event_no = 0
    try:
        while True:
            vm_id = input("VM ID [lab-vm-01/lab-vm-02/reset/quit]: ").strip()
            if vm_id == "quit":
                break
            if vm_id == "reset":
                before = dict(backend.state)
                backend.reset()
                with path.open("a") as output:
                    output.write(json.dumps({"run_id": run_id, "decision": "RESET", "before": before,
                                             "after": dict(backend.state)}, ensure_ascii=False) + "\n")
                print("[FINAL STATE] reset", backend.state)
                continue
            action = input("Action [status/shutdown/restart]: ").strip()
            profile = input("Policy profile [scoped/status-both]: ").strip() or "scoped"
            if profile not in {"scoped", "status-both"}:
                print("Unknown profile; no call made.")
                continue
            policy = manual_policy()
            if profile == "status-both":
                policy["vm_action"].append((2, 0, {"vm_id": {"enum": ["lab-vm-01", "lab-vm-02"]},
                                                      "action": {"const": "status"}}, 0))
            update_security_policy(policy)
            event_no += 1
            event_id = f"event-{event_no:03d}"
            tool = make_wrapped_tool(backend, event_id)
            before = dict(backend.state)
            count_before = len(backend.backend_calls)
            print("[POLICY CHECK] upstream wrapper; matched-rule explanation is not exposed by its API")
            print("[POLICY]", get_current_config())
            print("[TOOL CALL]", {"vm_id": vm_id, "action": action})
            try:
                result = tool(vm_id, action)
                decision, error = "ALLOW", None
                print("[ALLOW]", result)
            except Exception as exc:
                decision, error = "DENY_OR_INPUT_ERROR", f"{type(exc).__name__}: {exc}"
                print("[DENY / INPUT ERROR]", error)
            record = {"run_id": run_id, "event_id": event_id, "profile": profile,
                      "input_origin": "human direct input", "policy": get_current_config(),
                      "tool_call": {"vm_id": vm_id, "action": action}, "decision": decision,
                      "error": error, "backend_calls_delta": len(backend.backend_calls) - count_before,
                      "before": before, "after": dict(backend.state)}
            with path.open("a") as output:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
            print("[BACKEND EXECUTION] calls this event:", record["backend_calls_delta"])
            print("[FINAL STATE]", backend.state)
    except EOFError:
        pass
    finally:
        update_security_policy({})
        print("Session ended; state was only in this process.")


if __name__ == "__main__":
    main()
