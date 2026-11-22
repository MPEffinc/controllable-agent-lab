import unittest

from secagent import update_security_policy

from scripts.progent_vm_experiment import attempt
from scripts.progent_vm_usecase import manual_policy


class EnforcementTest(unittest.TestCase):
    def tearDown(self):
        update_security_policy({})

    def test_explicit_deny_does_not_enter_backend(self):
        expected = {"decision": "DENY_OR_INPUT_ERROR", "backend_calls": 0,
                    "after": {"lab-vm-01": "running", "lab-vm-02": "running"}}
        record = attempt("unit", "deny", {"vm_id": "lab-vm-01", "action": "shutdown"},
                         manual_policy(), expected, "priority 1 deny")
        self.assertTrue(record["matches_expectation"])
        self.assertEqual(record["error_origin"], "progent_policy")
        self.assertEqual(record["tool_function_calls"], [])

    def test_missing_argument_stops_before_checker(self):
        expected = {"decision": "DENY_OR_INPUT_ERROR", "backend_calls": 0,
                    "after": {"lab-vm-01": "running", "lab-vm-02": "running"}}
        record = attempt("unit", "missing", {"action": "status"}, manual_policy(),
                         expected, "signature bind", True)
        self.assertEqual(record["error_origin"], "python_signature")
        self.assertTrue(record["schema_probe"].startswith("rejected:"))

    def test_none_policy_reaches_mock_backend(self):
        expected = {"decision": "ALLOW", "backend_calls": 1,
                    "after": {"lab-vm-01": "stopped", "lab-vm-02": "running"}}
        record = attempt("unit", "none", {"vm_id": "lab-vm-01", "action": "shutdown"},
                         None, expected, "policy not set")
        self.assertTrue(record["matches_expectation"])
        self.assertEqual(record["tool_function_calls"][0]["event_id"], "none")


if __name__ == "__main__":
    unittest.main()
