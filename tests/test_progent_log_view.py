import unittest

from scripts.progent_log_view import ANSI, highlight_native, source_text


class NativeLogViewTest(unittest.TestCase):
    def test_color_removal_restores_exact_original_text(self):
        original = ("USER_QUERY: stop resource\n"
                    "security policy updated: {'stop_resource': [(1, 1, {}, 0)]}\n"
                    "ValidationError: The tool 'stop_resource' is not allowed.\n")
        rendered = highlight_native(original, enabled=True)
        self.assertNotEqual(rendered, original)
        self.assertEqual(ANSI.sub("", rendered), original)
        self.assertEqual(highlight_native(original, enabled=False), original)

    def test_original_source_segments_are_concatenated_without_edit(self):
        original = {"source_policy_setup_stderr": "setup\n",
                    "source_generation_stderr": "generation\n"}
        self.assertEqual(source_text(original), "setup\ngeneration\n")


if __name__ == "__main__":
    unittest.main()
