import tempfile
import unittest
from pathlib import Path

from scripts.progent_api_env_check import credential_status


class ApiEnvironmentCheckTest(unittest.TestCase):
    def test_file_presence_is_reported_without_key_value(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            secret = "synthetic-secret-for-test-only"
            path.write_text(f"OPENAI_API_KEY={secret}\n")
            present, source, mode = credential_status((path,), {})
            self.assertTrue(present)
            self.assertEqual(source, str(path))
            self.assertNotIn(secret, repr((present, source, mode)))

    def test_empty_file_is_absent_and_explicit_key_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text("OPENAI_API_KEY=\n")
            self.assertFalse(credential_status((path,), {})[0])
            self.assertEqual(credential_status((path,), {"OPENAI_API_KEY": "synthetic"})[1],
                             "process environment")


if __name__ == "__main__":
    unittest.main()
