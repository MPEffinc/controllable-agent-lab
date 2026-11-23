import json
import tempfile
import unittest
from pathlib import Path

from scripts.kata_daemon_config import KATA_RUNTIME, merge_config, read_config, summary


class KataConfigTest(unittest.TestCase):
    def test_merge_preserves_existing_settings_and_runtimes(self):
        original = {"live-restore": True, "log-driver": "json-file", "runtimes": {"other": {"path": "/bin/true"}}}
        merged, changed = merge_config(original)
        self.assertTrue(changed)
        self.assertEqual(merged["runtimes"]["kata"], KATA_RUNTIME)
        self.assertEqual(merged["runtimes"]["other"], original["runtimes"]["other"])
        self.assertEqual(merged["live-restore"], True)
        self.assertNotIn("kata", original["runtimes"])
        self.assertFalse(merge_config(merged)[1])

    def test_conflicting_runtime_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "manual review"):
            merge_config({"runtimes": {"kata": {"path": "/other"}}})

    def test_duplicate_keys_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "daemon.json"
            source.write_text('{"runtimes": {}, "runtimes": {}}')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                read_config(source)
            link = Path(directory) / "link.json"
            link.symlink_to(source)
            with self.assertRaisesRegex(ValueError, "symlink"):
                read_config(link)

    def test_inspection_exposes_only_key_names(self):
        config = {"registry-mirrors": ["https://private.example.invalid/secret"], "runtimes": {"other": {}}}
        rendered = json.dumps(summary(config, True))
        self.assertIn("registry-mirrors", rendered)
        self.assertNotIn("private.example.invalid", rendered)


if __name__ == "__main__":
    unittest.main()
