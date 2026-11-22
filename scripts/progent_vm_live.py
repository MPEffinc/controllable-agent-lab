"""User-run, bounded paid LLM exercise. Never invoked by the Phase 2 tests."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-model", default="gpt-4o-2024-08-06")
    parser.add_argument("--policy-model", default="gpt-4o-2024-08-06")
    parser.add_argument("--policy-mode", choices=("generated", "admin-plus-generated"), default="generated")
    parser.add_argument("--max-turns", type=int, default=3)
    parser.add_argument("--max-policy-requests", type=int, default=2)
    parser.add_argument("--max-tool-calls", type=int, default=3)
    parser.add_argument("--check-models", action="store_true")
    args = parser.parse_args()
    if min(args.max_turns, args.max_policy_requests, args.max_tool_calls) < 1:
        parser.error("request and turn limits must be positive")
    endpoint = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    parsed = urlsplit(endpoint)
    endpoint_display = urlunsplit((parsed.scheme, parsed.netloc.rsplit("@", 1)[-1], parsed.path, "", ""))
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("set OPENAI_API_KEY in your own terminal; the key is never printed or logged")
    task = "" if args.check_models else input("[USER TASK] Natural-language request: ").strip()
    if not args.check_models and not task:
        parser.error("a task is required")
    print("Endpoint:", endpoint_display)
    print("Agent model:", args.agent_model, "Policy model:", args.policy_model)
    print("Policy mode:", args.policy_mode)
    print("Maximum paid requests:", 2 if args.check_models else args.max_policy_requests + args.max_turns)
    print("Maximum tool calls:", args.max_tool_calls, "; charges may apply")
    if input("Type RUN to authorize these API requests: ").strip() != "RUN":
        print("Cancelled before any API request.")
        return

    from openai import OpenAI
    client = OpenAI()
    if args.check_models:
        for model in dict.fromkeys((args.policy_model, args.agent_model)):
            try:
                client.models.retrieve(model)
                print("Model visible:", model)
            except Exception as exc:
                print("Model check failed:", model, type(exc).__name__)
        return

    os.environ["SECAGENT_POLICY_MODEL"] = args.policy_model
    os.environ["SECAGENT_GENERATE"] = "True"
    import secagent.tool as core
    from agentdojo.functions_runtime import make_function
    from scripts.progent_vm_usecase import MockVMBackend, make_wrapped_tool, manual_policy

    run_id = "live-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]
    path = Path("local/progent-vm/live") / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    backend = MockVMBackend(run_id)
    log = {"run_id": run_id, "mode": args.policy_mode, "agent_model": args.agent_model,
           "policy_model": args.policy_model, "endpoint": endpoint_display, "task": task,
           "events": [], "status": "started"}
    original_api_request = core.api_request
    policy_requests = 0

    def bounded_policy_request(*request_args, **request_kwargs):
        nonlocal policy_requests
        if policy_requests >= args.max_policy_requests:
            raise RuntimeError("adapter policy request cap reached")
        policy_requests += 1
        return original_api_request(*request_args, **request_kwargs)

    core.api_request = bounded_policy_request  # adapter transport counter; generation/checker remain upstream
    tool = make_wrapped_tool(backend, "registration")  # register TOOLS before policy generation
    schema = make_function(tool).parameters.model_json_schema()
    core.update_security_policy(manual_policy() if args.policy_mode == "admin-plus-generated" else {})
    policy_input = {"system_prompt": core.get_SYS_PROMPT(), "tools": core.get_available_tools(),
                    "user_query": task}
    log["policy_input"] = policy_input
    print("[POLICY GENERATION] original generate_security_policy; input:", policy_input)
    print("[USER TASK]", task)
    if args.policy_mode == "admin-plus-generated":
        print("Experimental composition: priority 1 administrator Deny and priority 100 generated Allow; no general safety guarantee.")
    try:
        core.generate_security_policy(task)
        log["policy"] = core.get_current_config()
        print("[GENERATED POLICY]", log["policy"])
        messages = [{"role": "system", "content": "You manage only two in-memory mock VMs. Use vm_action when needed. Report what actually happened."},
                    {"role": "user", "content": task}]
        tool_spec = {"type": "function", "function": {"name": "vm_action",
                     "description": "Read or change an isolated mock VM", "parameters": schema}}
        tool_count = 0
        for turn in range(args.max_turns):
            response = client.chat.completions.create(model=args.agent_model, messages=messages,
                tools=[tool_spec], tool_choice="auto", parallel_tool_calls=False)
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))
            if not message.tool_calls:
                print("Agent response:", message.content)
                log["final_response"] = message.content
                log["status"] = "completed"
                break
            for call in message.tool_calls:
                if tool_count >= args.max_tool_calls:
                    raise RuntimeError("adapter tool call cap reached")
                tool_count += 1
                event_id = f"agent-{turn + 1}-tool-{tool_count}"
                if call.function.name != "vm_action":
                    raise ValueError("agent proposed an unavailable tool")
                call_args = json.loads(call.function.arguments)
                print("[AGENT TOOL CALL]", call_args)
                before = dict(backend.state)
                count_before = len(backend.backend_calls)
                try:
                    checked_args = make_function(tool).parameters.model_validate(call_args).model_dump()
                    backend.active_event_id = event_id
                    print("[POLICY CHECK] original secure_tool_wrapper / check_tool_call")
                    result = tool(**checked_args)
                    decision, content = "ALLOW", str(result)
                    print("[ALLOW]", content)
                except Exception as exc:
                    decision, content = "DENY_OR_INPUT_ERROR", f"{type(exc).__name__}: {exc}"
                    print("[DENY / INPUT ERROR]", content)
                event = {"event_id": event_id, "proposed_call": call_args, "decision": decision,
                         "tool_response": content, "backend_calls_delta": len(backend.backend_calls) - count_before,
                         "before": before, "after": dict(backend.state)}
                log["events"].append(event)
                backend.active_event_id = None
                print("[BACKEND EXECUTION]", event["backend_calls_delta"])
                messages.append({"role": "tool", "tool_call_id": call.id, "content": content})
        else:
            log["status"] = "turn_limit"
    except Exception as exc:
        log["status"] = "error"
        log["error"] = f"{type(exc).__name__}: {exc}"
        print("Live run error:", log["error"])
    finally:
        log["policy_requests"] = policy_requests
        log["backend_calls"] = backend.backend_calls
        log["final_state"] = backend.state
        path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
        core.update_security_policy({})
        print("[FINAL STATE]", backend.state)
        print("Local raw log:", path, "; do not commit without review")


if __name__ == "__main__":
    main()
