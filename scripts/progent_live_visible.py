#!/usr/bin/env python3
"""Run one original Progent/AgentDojo benign task with visible checkpoints.

No ground-truth replay. The upstream pipeline, policy functions, wrappers, tools
and scorer execute through their original functions. This external adapter adds
an explicit policy-output format, model compatibility and observation gates.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import functools
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "third_party/progent"
PIN = "b02783b896d4bf01a2adf24738015e258db8d35b"
MODEL = "gpt-6-luna"


class RunStop(BaseException):
    """Do not let upstream generic Exception retries override a resource stop."""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget-usd", type=float, default=1.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--stepwise", action="store_true")
    parser.add_argument("--skip-probe", action="store_true")
    parser.add_argument("--policy-format", choices=["original", "explicit-args"], default="explicit-args")
    args = parser.parse_args()
    if not 0 < args.budget_usd <= 1.0:
        parser.error("This approved session is limited to USD1")
    key, base = os.environ.get("LLM_API_KEY", ""), os.environ.get("LLM_BASE_URL", "")
    if not key or not base or os.environ.get("LLM_MODEL") != MODEL:
        parser.error("Load the previously authorized LLM environment; values will not be displayed")
    parsed = urlparse(base)
    if parsed.scheme != "https" or parsed.hostname != "api.openai.com":
        parser.error("Endpoint pricing is not covered by this audited budget; no request sent")
    sha = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(UPSTREAM), "status", "--porcelain"], text=True).strip()
    if sha != PIN or dirty:
        parser.error("Expected clean, pinned upstream source")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)

    def safe(text):
        text = str(text).replace(key, "[REDACTED_KEY]")
        return re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED_KEY]", text)

    def write(name, value):
        encoded = json.dumps(value, ensure_ascii=False, indent=2, default=lambda x: x.model_dump() if hasattr(x, "model_dump") else str(x))
        with (out / name).open("x") as f:
            f.write(safe(encoded) + "\n")

    seq = 0
    checkpoint_count = 0
    paused_seconds = 0.0
    def checkpoint(kind, data):
        nonlocal checkpoint_count, paused_seconds
        if not args.stepwise:
            return
        checkpoint_count += 1
        stem = f"checkpoint-{checkpoint_count:02d}"
        write(stem + ".json", dict(checkpoint=checkpoint_count, event=kind, **data))
        print("GUIDED_CHECKPOINT " + stem, flush=True)
        began = time.monotonic()
        while not (out / (stem + ".continue")).exists():
            if time.monotonic() - began > 600:
                raise RunStop("Guided checkpoint was not resumed within ten minutes")
            time.sleep(0.2)
        paused_seconds += time.monotonic() - began

    def event(kind, **data):
        nonlocal seq
        seq += 1
        item = dict(seq=seq, utc=dt.datetime.now(dt.timezone.utc).isoformat(), event=kind, **data)
        encoded = json.dumps(item, ensure_ascii=False, default=lambda x: x.model_dump() if hasattr(x, "model_dump") else str(x))
        with (out / "events.jsonl").open("a") as f:
            f.write(safe(encoded) + "\n")
        if kind in {"api_request", "generate_security_policy_after", "tool_request", "tool_return", "generate_update_security_policy_after"}:
            checkpoint(kind, data)

    os.environ.update(
        SECAGENT_SUITE="banking", SECAGENT_GENERATE="True", SECAGENT_UPDATE="True",
        SECAGENT_POLICY_MODEL=MODEL, SECAGENT_ONLY_ALLOW_NARROW="False",
        SECAGENT_IGNORE_UPDATE_ERROR="True", PYTHON_DOTENV_DISABLED="1",
        PYTHONDONTWRITEBYTECODE="1", AWS_EC2_METADATA_DISABLED="true",
        HF_HUB_OFFLINE="1", LANGSMITH_TRACING="false", LANGCHAIN_TRACING_V2="false",
        OPENAI_API_KEY=key, OPENAI_BASE_URL=base,
    )
    import httpx
    import openai
    import secagent
    from secagent import tool as control
    from agentdojo.task_suite import get_suite
    from agentdojo.agent_pipeline.agent_pipeline import AgentPipeline, PipelineConfig
    from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM
    from agentdojo.benchmark import benchmark_suite_without_injections
    from agentdojo.functions_runtime import FunctionsRuntime
    from agentdojo.logging import OutputLogger

    if not Path(secagent.__file__).resolve().is_relative_to(UPSTREAM / "secagent"):
        raise RuntimeError("Unexpected Progent import path")
    suite = get_suite("v1.1.2", "banking")
    task = suite.get_user_task_by_id("user_task_0")
    # Reuse the output-contract wording already provided for upstream models.
    # This is a recorded external prompt adaptation, not upstream modification.
    format_initial = '\nOutput format: ```json [{"name": tool_name, "args": restrictions}, ...] ```'
    format_update = '\nThe policy should be in JSON format: ```json [{"name": tool_name, "args": restrictions}, ...] ```'
    original_initial_prompt = control.get_SYS_PROMPT
    original_update_prompt = control.get_SYS_PROMPT_2
    if args.policy_format == "explicit-args":
        control.get_SYS_PROMPT = lambda: original_initial_prompt() + format_initial
        control.get_SYS_PROMPT_2 = lambda: original_update_prompt() + format_update
    write("policy-prompt-adaptation.json", dict(
        mode=args.policy_format, original_initial=original_initial_prompt(),
        original_update=original_update_prompt(), actual_initial=control.get_SYS_PROMPT(),
        actual_update=control.get_SYS_PROMPT_2(),
        source="secagent/tool.py:310 and :360; external model-compatibility addition"))
    write("configuration.json", dict(
        upstream_sha=sha, model=MODEL, benchmark_version="v1.1.2", suite="banking",
        task=task.ID, user_prompt=task.PROMPT, attack=None, generic_policy=control.get_current_config(),
        profile="generated-and-updated-policy-auto-approve", budget_usd=args.budget_usd,
        key_present=True, official_https_endpoint=True, source_modified=False,
        compatibility=dict(reasoning_effort="none", removed_sampling_fields=["seed", "temperature"],
                           max_completion_tokens=4096, sdk_retries=0, max_http_requests=20,
                           max_wall_seconds=300, max_request_json_bytes=120000),
        pricing_source="https://developers.openai.com/api/docs/models/gpt-6-luna",
        standard_price_per_million=dict(input=0.10, output=0.50),
        cache_price_per_million=dict(read=0.01, write=0.125),
        conservative_budget_rates=dict(input=0.20, output=1.00),
        scope="Original components with substituted model, explicit output-contract prompt and external observer/client adapter",
        stepwise=args.stepwise, skip_probe=args.skip_probe, policy_format=args.policy_format,
    ))
    if not args.execute:
        write("summary.json", {"status": "PREPARED_NO_API_CALL", "http_requests": 0})
        print(json.dumps({"status": "PREPARED_NO_API_CALL", "output": str(out)}))
        return

    start = time.monotonic()
    counters = dict(requests=0, reserved_usd=0.0, measured_standard_usd=0.0,
                    prompt_tokens=0, completion_tokens=0, usage_missing=0,
                    estimated_cache_aware_usd=0.0)
    phase = {"value": "original_benign_task" if args.skip_probe else "compatibility_probe"}

    class GuardedTransport(httpx.BaseTransport):
        def __init__(self):
            self.inner = httpx.HTTPTransport(retries=0)

        def handle_request(self, request):
            if request.url.host != "api.openai.com" or request.url.path != "/v1/chat/completions":
                raise RunStop("Unexpected API endpoint refused")
            if time.monotonic() - start - paused_seconds > 300:
                raise RunStop("Session deadline reached")
            body = json.loads(request.content)
            if body.get("model") != MODEL:
                raise RunStop("Unexpected model refused")
            body.pop("temperature", None)
            body.pop("seed", None)
            body.pop("max_tokens", None)
            body["reasoning_effort"] = "none"
            body["max_completion_tokens"] = min(body.get("max_completion_tokens", 4096), 4096)
            data = json.dumps(body, ensure_ascii=False).encode()
            if len(data) > 120000:
                raise RunStop("Request size limit reached")
            # Deliberate overestimate of the complete serialized input, plus
            # protocol framing allowance; stays below long-context price tier.
            input_bound = 2 * len(data) + 4096
            reserve = (input_bound * 0.20 + body["max_completion_tokens"] * 1.00) / 1e6
            if counters["requests"] >= 20 or counters["reserved_usd"] + reserve > args.budget_usd:
                raise RunStop("Request-count or conservative budget limit reached")
            counters["requests"] += 1
            counters["reserved_usd"] += reserve
            names = {frame.function for frame in inspect.stack()}
            role = phase["value"]
            if role != "compatibility_probe":
                role = ("policy_initial" if "generate_security_policy" in names else
                        "policy_update_decision" if "decide_whether_to_update" in names else
                        "policy_update_candidate" if "generate_update_security_policy" in names else "agent")
            rid = counters["requests"]
            write(f"api-{rid:02d}-request.json", {"role": role, "body": body})
            event("api_request", request_id=rid, role=role, reserved_usd=reserve)
            headers = dict(request.headers)
            headers["content-length"] = str(len(data))
            rewritten = httpx.Request(request.method, request.url, headers=headers, content=data, extensions=request.extensions)
            try:
                response = self.inner.handle_request(rewritten)
                response.read()
                payload = response.json()
                write(f"api-{rid:02d}-response.json", dict(status=response.status_code, body=payload))
                usage = payload.get("usage")
                if usage:
                    inp, output_tokens = usage["prompt_tokens"], usage["completion_tokens"]
                    counters["prompt_tokens"] += inp
                    counters["completion_tokens"] += output_tokens
                    counters["measured_standard_usd"] += (inp * 0.10 + output_tokens * 0.50) / 1e6
                    details = usage.get("prompt_tokens_details") or {}
                    cached = details.get("cached_tokens", 0)
                    cache_write = details.get("cache_write_tokens", 0)
                    counters["estimated_cache_aware_usd"] += ((inp-cached-cache_write)*0.10 + cached*0.01 + cache_write*0.125 + output_tokens*0.50) / 1e6
                    if inp > input_bound:
                        raise RunStop("Observed input exceeded conservative accounting bound")
                else:
                    counters["usage_missing"] += 1
                event("api_response", request_id=rid, role=role, status=response.status_code, usage=usage)
                return response
            except RunStop:
                raise
            except Exception as exc:
                event("api_transport_error", request_id=rid, error=safe(exc))
                raise

        def close(self):
            self.inner.close()

    http_client = httpx.Client(transport=GuardedTransport(), timeout=60, follow_redirects=False)
    real_client_class = openai.OpenAI
    client = real_client_class(api_key=key, base_url=base, max_retries=0, timeout=60, http_client=http_client)

    # Upstream policy api_request creates OpenAI() internally; supply the same
    # audited client while leaving its prompts/parsing/generation unchanged.
    def policy_client_factory(*a, **kw):
        if a or kw:
            raise RunStop("Unexpected policy client configuration")
        return client

    openai.OpenAI = policy_client_factory
    original_check = control.check_tool_call

    @functools.wraps(original_check)
    def observed_check(name, kwargs):
        observed_args = {k: v for k, v in kwargs.items() if not hasattr(v, "model_dump")}
        try:
            result = original_check(name, kwargs)
        except Exception as exc:
            event("policy_check", tool=name, arguments=observed_args, decision="DENY",
                  error=safe(exc), policy=copy.deepcopy(control.security_policy))
            raise
        event("policy_check", tool=name, arguments=observed_args,
              decision="ALLOW" if control.security_policy is not None else "UNINITIALIZED_ALLOW",
              policy=copy.deepcopy(control.security_policy))
        return result

    control.check_tool_call = observed_check
    for name in ["generate_security_policy", "generate_update_security_policy"]:
        original = getattr(control, name)
        def decorate(fn, label):
            @functools.wraps(fn)
            def observed(*a, **kw):
                event(label + "_before", policy=copy.deepcopy(control.security_policy))
                try:
                    return fn(*a, **kw)
                finally:
                    event(label + "_after", policy=copy.deepcopy(control.security_policy))
            return observed
        hook = decorate(original, name)
        setattr(control, name, hook)
        setattr(secagent, name, hook)
    # These modules imported the upstream functions before observation hooks.
    import agentdojo.agent_pipeline.basic_elements as basic
    import agentdojo.agent_pipeline.tool_execution as execution
    basic.generate_security_policy = control.generate_security_policy
    execution.generate_update_security_policy = control.generate_update_security_policy

    original_run = FunctionsRuntime.run_function
    states = {}

    @functools.wraps(original_run)
    def observed_run(self, env, function, kwargs, raise_on_error=False):
        before = env.model_dump() if env is not None else None
        if "initial" not in states:
            states["initial"] = copy.deepcopy(before)
        event("tool_request", tool=function, arguments=kwargs)
        try:
            result, error = original_run(self, env, function, kwargs, raise_on_error)
        except BaseException:
            states["final"] = env.model_dump() if env is not None else None
            raise
        states["final"] = env.model_dump() if env is not None else None
        before_n = len(before["bank_account"]["transactions"]) if before else 0
        after_n = len(states["final"]["bank_account"]["transactions"]) if states["final"] else 0
        event("tool_return", tool=function, result=result, error=error,
              transaction_delta=after_n-before_n, policy=copy.deepcopy(control.security_policy))
        return result, error

    FunctionsRuntime.run_function = observed_run
    summary = {"status": "STARTED", "model": MODEL, "attack": None}
    try:
        if not args.skip_probe:
            probe = client.chat.completions.create(
                model=MODEL, reasoning_effort="none", max_completion_tokens=128,
                messages=[{"role": "user", "content": "Call connection_probe with ok=true. This is only an API compatibility check."}],
                tools=[{"type": "function", "function": {"name": "connection_probe", "description": "API compatibility probe; never executed", "parameters": {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}}}],
                tool_choice={"type": "function", "function": {"name": "connection_probe"}},
            )
            if not probe.choices[0].message.tool_calls:
                raise RunStop("Compatibility probe did not return a tool call")
            event("compatibility_probe_passed", tool_executed=False)
        else:
            event("compatibility_probe_skipped", reason="Prior live run established the same model/endpoint function-call compatibility")
        phase["value"] = "original_benign_task"
        llm = OpenAILLM(client, MODEL, reasoning_effort="none")
        llm.name = MODEL
        pipeline = AgentPipeline.from_config(PipelineConfig(
            llm=llm, defense=None, system_message_name=None, system_message=None))
        with OutputLogger(str(out / "native")):
            results = benchmark_suite_without_injections(
                pipeline, suite, logdir=out / "native", user_tasks=["user_task_0"], force_rerun=False)
        summary.update(status="COMPLETED", utility=bool(results["utility_results"][("user_task_0", "")]),
                       attack_success=None, security_score_note="No attack condition; native security boolean is not an attack measurement")
    except BaseException as exc:
        summary.update(status="STOPPED" if isinstance(exc, RunStop) else "FAILED",
                       error_type=type(exc).__name__, error=safe(exc))
        event("session_stopped", **summary)
    finally:
        if states:
            write("environment-snapshots.json", states)
            initial = states.get("initial", {}).get("bank_account", {}).get("transactions", [])
            final = states.get("final", {}).get("bank_account", {}).get("transactions", [])
            ids = {x["id"] for x in initial}
            summary["new_transactions"] = [x for x in final if x["id"] not in ids]
            summary["transaction_delta"] = len(final) - len(initial)
        summary.update(counters, seconds=round(time.monotonic()-start, 3),
                       paused_seconds=round(paused_seconds, 3),
                       final_policy=control.get_current_config(),
                       adaptation="Explicit policy-output-format prompt, model/client/resource-limit/observer; original source preserved",
                       policy_format=args.policy_format)
        write("summary.json", summary)
        openai.OpenAI = real_client_class
        client.close()
    print(safe(json.dumps({k:summary.get(k) for k in ["status", "utility", "transaction_delta", "requests", "measured_standard_usd", "error"]}, ensure_ascii=False)))
    if summary["status"] != "COMPLETED":
        sys.exit(1)


if __name__ == "__main__":
    main()
