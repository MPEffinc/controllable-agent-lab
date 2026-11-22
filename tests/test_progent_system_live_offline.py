import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.progent_resource_tools import MockResourceBackend
from scripts import progent_system_live


class LiveOfflineTest(unittest.TestCase):
    def test_mock_start_and_restart_have_distinct_preconditions(self):
        backend = MockResourceBackend()
        with self.assertRaises(ValueError):
            backend.start("lab-vm-01")
        self.assertEqual(backend.restart("lab-vm-01"), "running")
        self.assertEqual(backend.stop("lab-vm-01"), "stopped")
        with self.assertRaises(ValueError):
            backend.restart("lab-vm-01")
        self.assertEqual(backend.start("lab-vm-01"), "running")

    def test_global_request_ledger_stops_at_thirty(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(progent_system_live, "LEDGER", Path(directory) / "budget.json"):
                for _ in range(30):
                    progent_system_live.reserve({"messages": [{"content": "test"}]}, 1024)
                with self.assertRaises(RuntimeError):
                    progent_system_live.reserve({"messages": [{"content": "test"}]}, 1024)


if __name__ == "__main__":
    unittest.main()
