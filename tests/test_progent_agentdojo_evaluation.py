import unittest

from scripts.progent_agentdojo_evaluation import tool_outcomes


class ToolOutcomeTest(unittest.TestCase):
    def test_function_call_object_from_agentdojo_is_supported(self):
        class FunctionCallLike:
            def model_dump(self):
                return {"function": "stop_resource", "args": {"resource_id": "x"}}

        messages = [{"role": "tool", "tool_call": FunctionCallLike(),
                     "error": "ValidationError: The tool 'stop_resource' is not allowed."}]
        self.assertEqual(tool_outcomes(messages)[0]["classification"], "POLICY_DENIED")

    def test_source_policy_error_is_separate_from_task_utility(self):
        messages = [
            {"role": "tool", "tool_call": {"function": "list_resources", "args": {}}, "error": None},
            {"role": "tool", "tool_call": {"function": "stop_resource", "args": {"resource_id": "x"}},
             "error": "ValidationError: The tool 'stop_resource' is not allowed."},
            {"role": "tool", "tool_call": {"function": "get_resource_status", "args": {"resource_id": "x"}},
             "error": "ValueError: unknown resource"},
        ]
        self.assertEqual([x["classification"] for x in tool_outcomes(messages)],
                         ["SUCCESS", "POLICY_DENIED", "TOOL_ERROR"])


if __name__ == "__main__":
    unittest.main()
