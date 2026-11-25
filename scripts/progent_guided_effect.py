#!/usr/bin/env python3
"""Teaching adapter around unchanged upstream policy, requests, runtime and tool.

This is NOT an upstream example, LLM run, prompt-injection attack, or paper
benchmark reproduction. Default mode only displays the upstream policy.
Each --case replays one upstream ground-truth tool request in a fresh fixture.
"""
import argparse
import ast
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/progent"
PIN = "b02783b896d4bf01a2adf24738015e258db8d35b"


def upstream_policy():
    """Read the literal example without running its __main__ analyzer."""
    path = SOURCE / "secagent/policy_analysis.py"
    tree = ast.parse(path.read_text())
    examples = [
        kw.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "security_policy_analysis"
        for kw in node.keywords
        if kw.arg == "security_policy"
    ]
    if len(examples) != 1:
        raise RuntimeError("Expected exactly one upstream literal policy example")
    return {"send_money": ast.literal_eval(examples[0])["send_money"]}


def no_network(*args, **kwargs):
    raise RuntimeError("Network is disabled in this teaching adapter")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["benign", "attack-goal"])
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are refused")
    args = parser.parse_args()
    revision = subprocess.check_output(
        ["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != PIN:
        parser.error("Upstream SHA differs from the reviewed pin")
    if subprocess.check_output(
        ["git", "-C", str(SOURCE), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    ).strip():
        parser.error("Upstream tracked files have changes; review before replay")
    policy = upstream_policy()
    provenance = {
        "kind": "teaching_adapter_for_upstream_components_not_paper_evaluation",
        "upstream_sha": revision,
        "policy_source": "third_party/progent/secagent/policy_analysis.py::__main__",
        "policy_source_sha256": hashlib.sha256(
            (SOURCE / "secagent/policy_analysis.py").read_bytes()
        ).hexdigest(),
        "policy": policy,
    }
    if args.case is None:
        print(json.dumps(provenance, indent=2))
        return
    if args.output is None:
        parser.error("--case requires --output pointing to a new result file")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Refuse overwrite before any tool request is executed.
    with args.output.open("x") as output:
        for name in list(os.environ):
            if any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")):
                os.environ.pop(name)
        os.environ.update(
            SECAGENT_SUITE="banking", SECAGENT_GENERATE="False",
            SECAGENT_UPDATE="False", PYTHON_DOTENV_DISABLED="1",
            AWS_EC2_METADATA_DISABLED="true", HF_HUB_OFFLINE="1",
            LANGSMITH_TRACING="false", LANGCHAIN_TRACING_V2="false",
        )
        socket.socket.connect = no_network
        socket.create_connection = no_network

        import secagent
        import agentdojo
        for module, expected in (
            (secagent, SOURCE / "secagent"),
            (agentdojo, SOURCE / "agentdojo/src/agentdojo"),
        ):
            if not Path(module.__file__).resolve().is_relative_to(expected.resolve()):
                raise RuntimeError(f"Wrong upstream module location: {module.__name__}")
        from secagent import check_tool_call, update_security_policy
        from secagent.tool import ValidationError
        # Bootstrap the upstream registry before importing suite-specific tasks,
        # as the original benchmark entry point does. Directly importing banking
        # first re-enters its unfinished module through version registration.
        from agentdojo.task_suite import get_suite
        task_suite = get_suite("v1", "banking")
        from agentdojo.default_suites.v1.banking.user_tasks import UserTask0
        from agentdojo.default_suites.v1.banking.injection_tasks import InjectionTask0
        from agentdojo.functions_runtime import FunctionsRuntime

        env = task_suite.load_and_inject_default_environment({})
        task = UserTask0() if args.case == "benign" else InjectionTask0()
        request = next(call for call in task.ground_truth(env) if call.function == "send_money")
        update_security_policy(policy)
        # Diagnostic precheck, followed by actual runtime -> original wrapper.
        # The selected upstream rules contain no dynamic-update fields.
        try:
            check_tool_call(request.function, request.args)
            precheck, precheck_error = "ALLOW", None
        except ValidationError as exc:
            precheck, precheck_error = "DENY", str(exc)
        before = len(env.bank_account.transactions)
        result, error = FunctionsRuntime(task_suite.tools).run_function(
            env, request.function, request.args
        )
        report = dict(
            provenance, observed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
            case=args.case, request_source=type(task).__name__ + ".ground_truth",
            imported_modules={"secagent": secagent.__file__, "agentdojo": agentdojo.__file__},
            request=request.model_dump(), precheck_decision=precheck,
            precheck_error=precheck_error, runtime_result=result, runtime_error=error,
            transactions_before=before, transactions_after=len(env.bank_account.transactions),
            tool_effect_count=len(env.bank_account.transactions) - before,
            new_transactions=[t.model_dump() for t in env.bank_account.transactions[before:]],
        )
        json.dump(report, output, indent=2)
        output.write("\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
