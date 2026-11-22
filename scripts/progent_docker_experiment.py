"""Actual Docker effects versus original Progent decisions, without LLM calls."""

import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from secagent import get_current_config, update_security_policy
from secagent.tool import ValidationError as ProgentDeny

from scripts.progent_docker_backend import DockerBackend, DockerBackendError, IMAGE
from scripts.progent_resource_tools import build_tools


def runtime_status(name):
    result = subprocess.run(["docker", "inspect", "--format", "{{.State.Status}}", name],
                            capture_output=True, text=True, timeout=15, check=True)
    return result.stdout.strip()


def policy(name, *, deny_stop=False, broad_status=False):
    scoped = {"resource_id": {"type": "string", "const": name}}
    rules = {"list_resources": [(1, 0, {}, 0)],
             "get_resource_status": [(10, 0, {} if broad_status else scoped, 0)],
             "start_resource": [(10, 0, scoped, 0)],
             "stop_resource": [(10, 0, scoped, 0)],
             "restart_resource": [(10, 0, scoped, 0)]}
    if deny_stop:
        rules["stop_resource"].insert(0, (1, 1, scoped, 0))
    return rules


def run_event(backend, tools, event_id, name, args, selected_policy, expected):
    update_security_policy(copy.deepcopy(selected_policy))
    before = runtime_status(name) if name in backend.owned else None
    command_count = len(backend.invocations)
    try:
        value = tools[name_tool := event_id.split("-")[0]](**args)
        classification, error = "SUCCESS", None
    except ProgentDeny as exc:
        value, classification, error = None, "POLICY_DENIED", str(exc)
    except DockerBackendError as exc:
        value, classification, error = None, "BACKEND_EXECUTION_FAILED", str(exc)
    except Exception as exc:
        value, classification, error = None, "INPUT_VALIDATION_FAILED", f"{type(exc).__name__}: {exc}"
    after = runtime_status(name) if name in backend.owned else None
    commands = backend.invocations[command_count:]
    record = {"event_id": event_id, "tool": name_tool, "args": args,
              "policy": get_current_config(), "classification": classification,
              "error": error, "tool_result": value, "docker_commands": commands,
              "runtime_before": before, "runtime_after": after, "expected": expected}
    record["matches_expectation"] = (classification == expected["classification"] and
        after == expected["after"] and
        len([x for x in commands if x["argv"][1] in {"start", "stop", "restart"}]) == expected["mutations"])
    return record


def main():
    run_id = "docker-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    backend = DockerBackend(run_id)
    log = {"run_id": run_id, "time_utc": datetime.now(timezone.utc).isoformat(),
           "image": IMAGE, "input_origin": "direct harness, not LLM", "events": []}
    path = Path("local/progent-vm/docker") / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        first, second = backend.create("01"), backend.create("02")
        backend.start(first)
        backend.start(second)
        log["owned"] = dict(backend.owned)
        tools = build_tools(backend)
        update_security_policy(policy(first))
        log["discovered"] = tools["list_resources"]()
        log["events"].append(run_event(backend, tools, "get_resource_status-UC-A", first,
            {"resource_id": first}, policy(first), {"classification": "SUCCESS", "after": "running", "mutations": 0}))
        log["events"].append(run_event(backend, tools, "stop_resource-UC-B", first,
            {"resource_id": first}, policy(first), {"classification": "SUCCESS", "after": "exited", "mutations": 1}))
        log["events"].append(run_event(backend, tools, "start_resource-UC-D", first,
            {"resource_id": first}, policy(first), {"classification": "SUCCESS", "after": "running", "mutations": 1}))
        log["events"].append(run_event(backend, tools, "stop_resource-UC-C", first,
            {"resource_id": first}, policy(first, deny_stop=True),
            {"classification": "POLICY_DENIED", "after": "running", "mutations": 0}))
        log["events"].append(run_event(backend, tools, "get_resource_status-UC-E", second,
            {"resource_id": second}, policy(first),
            {"classification": "POLICY_DENIED", "after": "running", "mutations": 0}))
        log["events"].append(run_event(backend, tools, "get_resource_status-BACKEND-FAIL", first,
            {"resource_id": "missing-resource"}, policy(first, broad_status=True),
            {"classification": "BACKEND_EXECUTION_FAILED", "after": "running", "mutations": 0}))
        log["status"] = "PASS" if all(x["matches_expectation"] for x in log["events"]) else "FAIL"
        for event in log["events"]:
            print(event["event_id"], event["classification"], event["runtime_before"],
                  "->", event["runtime_after"], "mutations", event["expected"]["mutations"],
                  "match", event["matches_expectation"])
    except Exception as exc:
        log["status"] = "ERROR"
        log["error"] = f"{type(exc).__name__}: {exc}"
        print("ERROR", log["error"])
    finally:
        try:
            backend.cleanup()
            log["cleanup"] = "owned resources removed"
        except Exception as exc:
            log["cleanup"] = f"FAILED: {type(exc).__name__}: {exc}"
        log["docker_invocations"] = backend.invocations
        update_security_policy({})
        path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
        print("log", path, "status", log["status"], "cleanup", log["cleanup"])
    if log["status"] != "PASS" or log["cleanup"] != "owned resources removed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
