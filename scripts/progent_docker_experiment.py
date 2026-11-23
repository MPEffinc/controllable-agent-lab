"""Actual runc/Kata Docker effects versus original Progent decisions, without LLM calls."""

import argparse
import copy
import json
import subprocess
import platform
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


def kata_attestation(backend, name):
    """Independent Guest and Host evidence for an already owned Kata container."""
    info = backend._check_owned(name)
    container_id = info["Id"]
    guest = subprocess.run(["docker", "exec", name, "uname", "-r"],
                           capture_output=True, text=True, timeout=30, check=True)
    processes = subprocess.run(["ps", "-eo", "pid,ppid,args"],
                               capture_output=True, text=True, timeout=15, check=True)
    evidence = {"container_id": container_id, "docker_runtime": info["HostConfig"]["Runtime"],
                "host_kernel": platform.release(), "guest_kernel": guest.stdout.strip(),
                "shim_pids": [], "hypervisor_pids": []}
    for line in processes.stdout.splitlines():
        if container_id not in line:
            continue
        columns = line.strip().split(maxsplit=2)
        if len(columns) < 3:
            continue
        if "/opt/kata/runtime-rs/bin/containerd-shim-kata-v2" in columns[2]:
            evidence["shim_pids"].append(int(columns[0]))
        if "/opt/kata/bin/qemu-system-x86_64" in columns[2]:
            evidence["hypervisor_pids"].append(int(columns[0]))
    evidence["guest_boot_verified"] = (evidence["docker_runtime"] == "kata"
        and bool(evidence["shim_pids"]) and bool(evidence["hypervisor_pids"])
        and evidence["guest_kernel"] != evidence["host_kernel"])
    return evidence


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
    controller_count = len(backend.tool_calls)
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
    controller_calls = backend.tool_calls[controller_count:]
    record = {"event_id": event_id, "tool": name_tool, "args": args,
              "policy": get_current_config(), "classification": classification,
              "error": error, "tool_result": value,
              "controller_tool_calls": controller_calls, "docker_commands": commands,
              "runtime_before": before, "runtime_after": after, "expected": expected}
    record["matches_expectation"] = (classification == expected["classification"] and
        after == expected["after"] and
        (classification != "POLICY_DENIED" or not controller_calls) and
        len([x for x in commands if x["argv"][1] in {"start", "stop", "restart"}]) == expected["mutations"])
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=("runc", "kata"), default="runc")
    args = parser.parse_args()
    run_id = ("kata-" if args.runtime == "kata" else "docker-") + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    backend = DockerBackend(run_id, runtime=args.runtime)
    log = {"run_id": run_id, "time_utc": datetime.now(timezone.utc).isoformat(),
           "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
           "source_dirty": bool(subprocess.check_output(
               ["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip()),
           "image": IMAGE, "runtime": args.runtime,
           "input_origin": "direct harness, not LLM", "events": []}
    path = Path("local/progent-vm/kata" if args.runtime == "kata" else "local/progent-vm/docker") / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        first, second = backend.create("01"), backend.create("02")
        backend.start(first)
        backend.start(second)
        log["owned"] = dict(backend.owned)
        if args.runtime == "kata":
            log["kata_attestation"] = kata_attestation(backend, first)
            if not log["kata_attestation"]["guest_boot_verified"]:
                raise RuntimeError("Kata guest attestation did not confirm Shim, QEMU and guest kernel")
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
