"""Check tool schemas consumed by the original AgentDojo FunctionsRuntime."""

import unittest

from agentdojo.functions_runtime import make_function
from pydantic import ValidationError

from scripts.progent_resource_tools import MockResourceBackend, build_tools
from scripts.progent_system_suite import task_suite


class AgentDojoSchemaTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
