import unittest

from agentdojo.functions_runtime import FunctionsRuntime
from agentdojo.task_suite import get_suite
from secagent import update_security_policy

import scripts.progent_system_suite as system_suite


class SystemSuiteTest(unittest.TestCase):
    def tearDown(self):
        update_security_policy({})

    def test_registration_and_discovery(self):
        suite = get_suite("v1.1.2", "progent_system")
        self.assertEqual(len(suite.user_tasks), 5)
        env = suite.load_and_inject_default_environment({})
        system_suite.bind_environment(env)
        update_security_policy({"list_resources": [(1, 0, {}, 0)]})
        runtime = FunctionsRuntime(suite.tools)
        value, error = runtime.run_function(env, "list_resources", {})
        self.assertIsNone(error)
        self.assertEqual(value, ["lab-vm-01", "lab-vm-02"])

    def test_utility_uses_post_environment(self):
        suite = get_suite("v1.1.2", "progent_system")
        task = suite.get_user_task_by_id("user_task_1")
        pre = suite.load_and_inject_default_environment({})
        post = pre.model_copy(deep=True)
        post.resources["lab-vm-01"] = "stopped"
        post.events.append({"action": "stop", "resource_id": "lab-vm-01"})
        self.assertTrue(task.utility("", pre, post))
        self.assertFalse(task.utility("", pre, pre))


if __name__ == "__main__":
    unittest.main()
