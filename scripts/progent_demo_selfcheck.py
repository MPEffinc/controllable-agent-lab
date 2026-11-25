#!/usr/bin/env python3
"""Offline checks for the external demo controls; NEVER run a benchmark/tool.

HTTP responses below are fixed transport fixtures, not LLM/attack rollouts.
All real socket connections are prohibited for the whole check process.
"""
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


def no_network(*args, **kwargs):
    raise AssertionError("Network forbidden in selfcheck")


socket.socket.connect = no_network
socket.create_connection = no_network

import httpx
from progent_demo import Redactor, make_config, parser, load_environment
from progent_demo_session import GuardedTransport, RunStop, SanitizedLog, Session, install_observers, interruptible_request


class Inner(httpx.BaseTransport):
    def __init__(self, status=200, body=None):
        self.sent = []
        self.status = status
        self.body = body if body is not None else {"choices": [], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}

    def handle_request(self, request):
        self.sent.append(json.loads(request.content))
        return httpx.Response(self.status, json=self.body)


class Controls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="progent-demo-selfcheck-")
        self.root = Path(self.tmp.name)
        self.env = {"LLM_API_KEY": 'fake-local-key-"never-log-me"'}
        self.redactor = Redactor(self.env)
        self.config = make_config(parser().parse_args(["normal", "--output", str(self.root / "run")]), self.env)
        self.session = Session(self.config, self.redactor, io.StringIO())

    def tearDown(self):
        self.session.transcript.close()
        self.tmp.cleanup()

    def request(self, model="gpt-6-luna"):
        return httpx.Request("POST", self.config["base_url"] + "/chat/completions", json={
            "model": model, "temperature": 1, "seed": 99, "max_tokens": 999999,
            "messages": [{"role": "user", "content": "offline transport fixture"}]})

    def test_config_and_dry_run_do_not_import_benchmark_or_create_target(self):
        self.assertNotIn("agentdojo", sys.modules)
        self.assertNotIn("secagent", sys.modules)
        config = make_config(parser().parse_args(["attack", "--dry-run", "--output", str(self.root / "uncreated")]), {})
        self.assertFalse(Path(config["output"]).exists())
        self.assertEqual(config["attack"], "important_instructions")

    def test_existing_output_is_rejected(self):
        with self.assertRaises(ValueError):
            make_config(parser().parse_args(["normal", "--output", str(self.session.out)]), self.env)

    def test_dotenv_is_data_only_and_shell_wins(self):
        path = self.root / "credentials.env"
        path.write_text('LLM_MODEL=gpt-4o-2024-08-06\nLLM_API_KEY=local-fake-secret\nIGNORED=unsafe\n')
        with patch.dict("os.environ", {"LLM_MODEL": "gpt-6-luna"}, clear=True):
            loaded = load_environment(path)
        self.assertEqual(loaded["LLM_MODEL"], "gpt-6-luna")
        self.assertEqual(loaded["LLM_API_KEY"], "local-fake-secret")
        self.assertNotIn("IGNORED", loaded)

    def test_endpoint_credentials_and_wrong_luna_options_are_rejected(self):
        for flags in [["--base-url", "https://u:password@example.invalid/v1"],
                      ["--agent-options", '{"reasoning_effort":"low"}']]:
            with self.assertRaises(ValueError):
                make_config(parser().parse_args(["normal", *flags]), self.env)

    def test_model_override_and_independent_policy_options(self):
        config = make_config(parser().parse_args(["normal", "--agent-model", "gpt-4o-2024-08-06",
            "--policy-model", "gpt-6-luna", "--profile", "auto-deny"]), self.env)
        self.assertEqual(config["models"]["agent"]["request_options"]["temperature"], 0)
        self.assertEqual(config["models"]["policy"]["request_options"]["reasoning_effort"], "none")
        self.assertIsNone(config["models"]["agent"]["price_per_million"]["input"])
        self.assertEqual(config["policy_environment"]["SECAGENT_ONLY_ALLOW_NARROW"], "True")

    def test_secret_redacted_in_json_and_split_stream(self):
        key = self.env["LLM_API_KEY"]
        self.session.write("secret-check.json", {"error": key, "nested": {"authorization": "Bearer other-secret"}})
        output = SanitizedLog(self.root / "stream.log", self.redactor)
        output.write(key[:9])
        output.flush()
        output.write(key[9:] + "\n")
        output.finish()
        for path in [self.session.out / "secret-check.json", self.root / "stream.log"]:
            self.assertNotIn(key, path.read_text())
            self.assertNotIn(json.dumps(key)[1:-1], path.read_text())
            self.assertIn("[REDACTED]", path.read_text())

    def test_q_and_eof_send_nothing(self):
        for error in [None, EOFError]:
            inner = Inner()
            transport = GuardedTransport(self.session, inner)
            with patch("builtins.input", return_value="q", side_effect=error):
                with self.assertRaises(RunStop):
                    transport.handle_request(self.request())
            self.assertFalse(inner.sent)
            self.assertEqual(self.session.counters["requests"], 0)
            # A cancelled prepared request is intentionally retained as evidence.
            if error is None:
                (self.session.out / "api-01-request.json").unlink()

    def test_budget_request_count_and_wrong_endpoint_stop_before_send(self):
        for value in ["budget", "requests", "endpoint"]:
            inner = Inner()
            if value == "budget":
                self.config["limits"]["budget_usd"] = 0.0000001
            elif value == "requests":
                self.config["limits"]["budget_usd"] = 0.85
                self.config["limits"]["max_requests"] = 0
            else:
                self.config["limits"]["max_requests"] = 20
            request = self.request() if value != "endpoint" else httpx.Request("POST", "https://elsewhere.invalid/v1/chat/completions")
            with self.assertRaises(RunStop):
                GuardedTransport(self.session, inner).handle_request(request)
            self.assertFalse(inner.sent)

    def test_options_rewrite_and_usage_counted_once(self):
        inner = Inner()
        with patch("builtins.input", return_value=""):
            GuardedTransport(self.session, inner).handle_request(self.request())
        self.assertEqual(len(inner.sent), 1)
        self.assertNotIn("temperature", inner.sent[0])
        self.assertNotIn("seed", inner.sent[0])
        self.assertEqual(inner.sent[0]["reasoning_effort"], "none")
        self.assertEqual(inner.sent[0]["max_completion_tokens"], 4096)
        self.assertEqual(self.session.counters["requests"], 1)
        self.assertEqual(self.session.counters["prompt_tokens"], 10)

    def test_provider_restriction_stops_without_retry(self):
        inner = Inner(body={"choices": [{"message": {"refusal": "offline refusal fixture"}}]})
        with patch("builtins.input", return_value=""), self.assertRaises(RunStop):
            GuardedTransport(self.session, inner).handle_request(self.request())
        self.assertEqual(len(inner.sent), 1)

    def test_policy_role_and_options_are_selected_from_original_call_stack(self):
        self.config["models"]["policy"]["model"] = "other-policy-fixture"
        inner = Inner()
        def generate_security_policy():
            return GuardedTransport(self.session, inner).handle_request(self.request("other-policy-fixture"))
        with patch("builtins.input", return_value=""):
            generate_security_policy()
        self.assertEqual(self.session.counters["by_role"]["policy_initial"]["requests"], 1)

    def test_original_retry_predicate_cannot_retry_operator_or_resource_stops(self):
        from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_none
        calls = []
        @retry(retry=retry_if_not_exception_type(ValueError), stop=stop_after_attempt(3), wait=wait_none(), reraise=True)
        def request():
            calls.append("attempt")
            raise RunStop("offline stop fixture")
        with self.assertRaises(RunStop):
            interruptible_request(request)()
        self.assertEqual(len(calls), 1)

    def test_tool_body_is_not_called_when_operator_stops_after_allow(self):
        # Tiny stand-ins only: no original tool, fixture or policy is executed.
        control = types.SimpleNamespace(security_policy={"fixture": []},
            check_tool_call=lambda *a: None, get_current_config=lambda: {},
            generate_security_policy=lambda *a, **k: None,
            generate_update_security_policy=lambda *a, **k: None)
        secagent = types.SimpleNamespace(generate_security_policy=control.generate_security_policy,
            generate_update_security_policy=control.generate_update_security_policy)
        effects = []
        class Runtime:
            def run_function(self, env, function, kwargs, raise_on_error=False):
                control.check_tool_call(function, kwargs)
                effects.append("tool body")
                return "fixture result", None
        suite = types.SimpleNamespace(run_task_with_pipeline=lambda *a, **k: None)
        env = types.SimpleNamespace(model_dump=lambda: {"bank_account": {"transactions": []}})
        modules = {name: types.ModuleType(name) for name in ["agentdojo", "agentdojo.agent_pipeline",
            "agentdojo.agent_pipeline.basic_elements", "agentdojo.agent_pipeline.tool_execution"]}
        modules["agentdojo"].agent_pipeline = modules["agentdojo.agent_pipeline"]
        modules["agentdojo.agent_pipeline"].basic_elements = modules["agentdojo.agent_pipeline.basic_elements"]
        modules["agentdojo.agent_pipeline"].tool_execution = modules["agentdojo.agent_pipeline.tool_execution"]
        modules["agentdojo.agent_pipeline.basic_elements"].generate_security_policy = control.generate_security_policy
        modules["agentdojo.agent_pipeline.tool_execution"].generate_update_security_policy = control.generate_update_security_policy
        with patch.dict(sys.modules, modules), ExitStack() as stack:
            install_observers(stack, self.session, control, secagent, suite, Runtime)
            with patch("builtins.input", side_effect=["", "q"]), self.assertRaises(RunStop):
                Runtime().run_function(env, "fixture", {})
        self.assertFalse(effects)


if __name__ == "__main__":
    unittest.main(verbosity=2)
