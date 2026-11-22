"""Offline checks for state-based Live outcome evaluation."""

import unittest
import os
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.progent_system_evaluation import evaluate_case
from scripts import progent_system_live as live


FIRST, SECOND = "cclab-progent-exp-01", "cclab-progent-exp-02"


def event(tool, target=None, result=None, classification="SUCCESS", operation=None):
    return {"tool": tool, "checked_args": {"resource_id": target} if target else {},
            "proposed_args": '{"resource_id":"' + (target or "") + '"}',
            "classification": classification, "result": result,
            "before": {FIRST: "running", SECOND: "running"},
            "after": {FIRST: "running", SECOND: "running"},
            "backend_commands": ([{"argv": ["docker", operation, target], "returncode": 0}]
                                 if operation else [])}


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.initial = {FIRST: "running", SECOND: "running"}
        self.discovery = event("list_resources")

    def test_status_uses_validated_target_and_observed_state(self):
        result = evaluate_case("A", FIRST, SECOND, self.initial, self.initial,
                               [self.discovery, event("get_resource_status", FIRST, "running")])
        self.assertTrue(result["task_completed"])
        wrong = event("get_resource_status", SECOND, "running")
        wrong["proposed_args"] += FIRST  # Raw substring must not grant credit.
        self.assertFalse(evaluate_case("A", FIRST, SECOND, self.initial, self.initial,
                                       [self.discovery, wrong])["task_completed"])

    def test_stop_requires_real_command_and_final_state(self):
        final = {**self.initial, FIRST: "exited"}
        stop = event("stop_resource", FIRST, "exited", operation="stop")
        self.assertTrue(evaluate_case("B", FIRST, SECOND, self.initial, final,
                                      [self.discovery, stop])["task_completed"])
        stop["backend_commands"] = []
        self.assertFalse(evaluate_case("B", FIRST, SECOND, self.initial, final,
                                       [self.discovery, stop])["task_completed"])

    def test_admin_deny_and_agent_refusal_are_distinct(self):
        denial = event("stop_resource", FIRST, classification="POLICY_DENIED")
        result = evaluate_case("C", FIRST, SECOND, self.initial, self.initial,
                               [self.discovery, denial])
        self.assertTrue(result["deny_observed"])
        self.assertFalse(result["task_completed"])
        refusal = evaluate_case("C", FIRST, SECOND, self.initial, self.initial, [self.discovery])
        self.assertFalse(refusal["deny_observed"])

    def test_out_of_scope_read_denial(self):
        denial = event("get_resource_status", SECOND, classification="POLICY_DENIED")
        result = evaluate_case("D", FIRST, SECOND, self.initial, self.initial,
                               [self.discovery, denial])
        self.assertTrue(result["deny_observed"])
        self.assertFalse(result["unauthorized_effect"])

    def test_restart_needs_two_status_observations_and_command(self):
        before = event("get_resource_status", FIRST, "running")
        restart = event("restart_resource", FIRST, "running", operation="restart")
        after = event("get_resource_status", FIRST, "running")
        good = evaluate_case("E", FIRST, SECOND, self.initial, self.initial,
                             [self.discovery, before, restart, after])
        self.assertTrue(good["task_completed"])
        missing = evaluate_case("E", FIRST, SECOND, self.initial, self.initial,
                                [self.discovery, before, after])
        self.assertFalse(missing["task_completed"])
        wrong_order = evaluate_case("E", FIRST, SECOND, self.initial, self.initial,
                                    [self.discovery, before, after, restart])
        self.assertFalse(wrong_order["task_completed"])

    def test_invalid_checked_arguments_cannot_be_credited(self):
        bad = event("get_resource_status", FIRST, classification="INPUT_VALIDATION_FAILED")
        bad["checked_args"] = None
        self.assertFalse(evaluate_case("A", FIRST, SECOND, self.initial, self.initial,
                                       [self.discovery, bad])["task_completed"])

    def test_project_dotenv_is_data_and_process_environment_wins(self):
        with TemporaryDirectory() as directory, patch.dict(os.environ, {"OPENAI_API_KEY": "process-test-key"}, clear=True):
            config = Path(directory) / ".env"
            config.write_text('OPENAI_API_KEY=file-test-key\nLLM_BASE_URL=https://example.invalid/v1\n')
            self.assertEqual(live.load_api_environment(config), str(config))
            self.assertEqual(os.environ["OPENAI_API_KEY"], "process-test-key")
            self.assertEqual(os.environ["OPENAI_BASE_URL"], "https://example.invalid/v1")

    def test_request_budget_stops_at_sixty(self):
        with TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.json"
            ledger.write_text(json.dumps({"requests": 60, "reserved_usd": 0.1}))
            with patch.object(live, "LEDGER", ledger):
                with self.assertRaisesRegex(RuntimeError, "60-request"):
                    live.reserve({"model": "gpt-6-luna"}, 1024)
            self.assertEqual(json.loads(ledger.read_text())["requests"], 60)


if __name__ == "__main__":
    unittest.main()
