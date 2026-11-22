"""Check tool schemas consumed by the original AgentDojo FunctionsRuntime."""

import unittest

from agentdojo.functions_runtime import make_function
from pydantic import ValidationError
from secagent import update_security_policy
from secagent.tool import ValidationError as ProgentDeny

from scripts.progent_resource_tools import MockResourceBackend, build_tools
from scripts.progent_system_suite import task_suite


class AgentDojoSchemaTests(unittest.TestCase):
    def tearDown(self):
        update_security_policy({})

    def test_source_suite_tools_require_resource_id(self):
        for tool in task_suite.tools:
            schema = tool.parameters.model_json_schema()
            if tool.name == "list_resources":
                self.assertEqual(schema.get("required", []), [])
            else:
                self.assertIn("resource_id", schema["required"], tool.name)
                with self.assertRaises(ValidationError):
                    tool.parameters.model_validate({})

    def test_custom_live_tools_require_resource_id(self):
        for name, tool in build_tools(MockResourceBackend()).items():
            schema = make_function(tool).parameters.model_json_schema()
            if name != "list_resources":
                self.assertIn("resource_id", schema["required"], name)

    def test_denied_call_does_not_enter_controller(self):
        backend = MockResourceBackend()
        tools = build_tools(backend)
        update_security_policy({"stop_resource": [(1, 1, {"resource_id":
            {"type": "string", "const": "lab-vm-01"}}, 0)]})
        with self.assertRaises(ProgentDeny):
            tools["stop_resource"]("lab-vm-01")
        self.assertEqual(backend.tool_calls, [])
        self.assertEqual(backend.resources["lab-vm-01"], "running")


if __name__ == "__main__":
    unittest.main()
