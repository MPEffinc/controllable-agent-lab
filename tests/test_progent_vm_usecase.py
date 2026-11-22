import unittest

from secagent import get_current_config, update_security_policy

from scripts.progent_vm_usecase import MockVMBackend, install_manual_policy, make_wrapped_tool


class MockVMToolTest(unittest.TestCase):
    def tearDown(self):
        update_security_policy({})

    def test_backend_changes_only_memory(self):
        backend = MockVMBackend("phase1-unit")
        self.assertEqual(backend.execute("lab-vm-01", "shutdown", "e1"), "stopped")
        self.assertEqual(backend.state["lab-vm-01"], "stopped")
        self.assertEqual(backend.execute("lab-vm-01", "restart", "e2"), "running")
        self.assertEqual(len(backend.backend_calls), 2)
        backend.reset()
        self.assertEqual(backend.state["lab-vm-01"], "running")
        self.assertEqual(backend.backend_calls, [])

    def test_upstream_wrapper_invokes_allowed_tool(self):
        backend = MockVMBackend("phase1-wrapper")
        tool = make_wrapped_tool(backend, "e1")
        install_manual_policy()
        self.assertIsNotNone(get_current_config())
        self.assertEqual(tool("lab-vm-01", "status"), "running")
        self.assertEqual(len(backend.tool_calls), 1)
        self.assertEqual(len(backend.backend_calls), 1)
        self.assertEqual(backend.state["lab-vm-01"], "running")


if __name__ == "__main__":
    unittest.main()
