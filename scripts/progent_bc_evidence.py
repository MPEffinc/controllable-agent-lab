"""Show the stored end-to-end chain for the two Luna/Kata B and C raw runs.

This is a read-only presentation view, not a replay or a new LLM execution.
It never prints full API requests/responses or the historically aliased
administrator_policy field.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_IDS = {
    "B": "luna-20261123T012323Z-c5b336",
    "C": "luna-20261123T012353Z-756b79",
}


def load(case: str) -> dict:
    run_id = RUN_IDS[case]
    path = ROOT / "local/progent-vm/live" / f"{run_id}.json"
    try:
        run = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"cannot read preserved {case} run at {path}: {exc}") from exc
    if run.get("run_id") != run_id or run.get("case") != case or run.get("backend") != "kata":
        raise RuntimeError(f"{path} does not match the expected Kata {case} run")
    return run


def model_calls(run: dict) -> list[dict]:
    """Read Tool Calls from stored model responses, not from harness events."""
    calls = []
    for request in run.get("api", []):
        if request.get("role") != "agent":
            continue
        for choice in (request.get("response") or {}).get("choices", []):
            for call in (choice.get("message") or {}).get("tool_calls") or []:
                calls.append(call["function"])
    return calls


def render(case: str, color: bool, verbose: bool = False) -> str:
    run = load(case)
    target = run["resource_ids"][0]
    stop_events = [e for e in run["events"] if e.get("tool") == "stop_resource"]
    if len(stop_events) != 1:
        raise RuntimeError(f"{case} has {len(stop_events)} stop events; expected one")
    event = stop_events[0]
    calls = model_calls(run)
    actual_stop_calls = [c for c in calls if c.get("name") == "stop_resource"]
    if len(actual_stop_calls) != 1:
        raise RuntimeError(f"{case} has {len(actual_stop_calls)} model stop calls; expected one")
    if json.loads(actual_stop_calls[0]["arguments"]) != json.loads(event["proposed_args"]):
        raise RuntimeError(f"{case} model response and harness Tool event disagree")
    policy_api = [x for x in run["api"] if x.get("role") == "policy"]
    if len(policy_api) != 1:
        raise RuntimeError(f"{case} has {len(policy_api)} policy model responses; expected one")
    policy_response = policy_api[0]["response"]["choices"][0]["message"]["content"]
    source_updates = [line for line in run["source_generation_stderr"].splitlines()
                      if line.startswith("security policy updated:")]
    if len(source_updates) != 1:
        raise RuntimeError(f"{case} has {len(source_updates)} source policy updates; expected one")

    def mark(value: str, code: str) -> str:
        return f"\x1b[{code}m{value}\x1b[0m" if color else value

    docker_stop = [c for c in event["backend_commands"]
                   if c.get("argv", [None, None])[1:2] == ["stop"]]
    lines = [
        f"[RUN] {case} | {run['run_id']} | Kata | source commit {run['source_commit']}",
        "[VIEW] Selected fields from the original Custom Runner JSON; not an unmodified Progent/AgentDojo console log.",
        "[USER TASK] " + run["task"],
        "[1. POLICY GENERATION AND APPLIED POLICY]",
        "Policy LLM model: " + policy_api[0]["request"]["model"],
        "Policy LLM user input: " + run["policy_input"]["user_query"],
        "Available Tool names: " + ", ".join(t["name"] for t in run["policy_input"]["tools"]),
        "Original Progent setup stderr: " + run["source_policy_setup_stderr"].strip(),
        "Policy LLM raw response: " + policy_response,
        "Parsed generated policy: " + json.dumps(run["generated_policy"], ensure_ascii=False),
        "Original Progent update stderr: " + source_updates[0],
        "Applied stop_resource rules:",
    ]
    for priority, effect, args, fallback in run["applied_policy"]["stop_resource"]:
        label = mark("DENY", "31") if effect else mark("ALLOW", "32")
        lines.append(f"  priority {priority} {label}; args={json.dumps(args, ensure_ascii=False)}; fallback={fallback}")
    lines.extend(["[2. ACTUAL MODEL TOOL CALLS]"])
    for call in calls:
        lines.append("  " + mark(call["name"], "36") + "(" + call["arguments"] + ")")
    lines.extend(["  stop_resource model response matches Tool event: YES",
                  "[3. TOOL EXECUTION AND RUNTIME EFFECT]",
                  "Enforcement path (source code): apply_secure_tool_wrapper -> check_tool_call; source rule ID not emitted"])
    for tool_event in run["events"]:
        outcome = mark(tool_event["classification"],
                       "31" if tool_event["classification"] == "POLICY_DENIED" else "32")
        lines.extend([
            "Tool input: " + tool_event["tool"] + "(" + tool_event["proposed_args"] + ")",
            "Schema checked args: " + json.dumps(tool_event["checked_args"], ensure_ascii=False),
            "Adapter classification: " + outcome,
            "Tool reply: " + tool_event["response"],
            "Controller calls: " + json.dumps(tool_event["controller_tool_calls"], ensure_ascii=False),
            "Backend commands: " + json.dumps(tool_event["backend_commands"], ensure_ascii=False),
        ])
    lines.extend([
        "Stop Tool outcome: " + mark(event["classification"],
                                     "31" if event["classification"] == "POLICY_DENIED" else "32"),
        f"Controller calls during stop: {len(event['controller_tool_calls'])}",
        f"Docker stop invocations: {len(docker_stop)}" +
            (f"; exit codes {[c['returncode'] for c in docker_stop]}" if docker_stop else ""),
        f"Target before/after stop call: {event['before'][target]} -> {event['after'][target]}",
        f"Target final runtime state: {run['runtime_final'][target]}",
        "Runtime observation source: independent docker inspect in the Custom Runner",
        f"Task completed: {run['task_success']}; unauthorized effect: {run['unauthorized_effect']}",
        "Final Agent response: " + str(run.get("final_response")),
        "[SOURCE] local/progent-vm/live/" + run["run_id"] + ".json",
        "[NOTE] Historical administrator_policy alias omitted; --verbose prints full stored Progent prompt/stderr.",
    ])
    if verbose:
        lines.extend([
            "[VERBOSE: ORIGINAL POLICY INPUT]",
            "Progent system prompt:\n" + run["policy_input"]["system_prompt"],
            "Progent Tool metadata:\n" + json.dumps(run["policy_input"]["tools"], ensure_ascii=False, indent=2),
            "[VERBOSE: ORIGINAL PROGENT STDERR, UNEDITED]",
            run["source_policy_setup_stderr"] + run["source_generation_stderr"],
        ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("B", "C", "both"), default="both")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--verbose", action="store_true", help="append full stored Progent prompt, tools and stderr")
    args = parser.parse_args()
    color = args.color == "always" or (args.color == "auto" and sys.stdout.isatty()
                                        and "NO_COLOR" not in os.environ)
    try:
        cases = ("B", "C") if args.case == "both" else (args.case,)
        print("\n\n".join(render(case, color, args.verbose) for case in cases))
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
