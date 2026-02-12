# test_precommit_hooks.py - Tests for pre-commit hooks configuration
"""Tests to validate the .pre-commit-hooks.yaml configuration"""

import os
import re
import unittest

import yaml


class TestPreCommitHooksConfig(unittest.TestCase):
    """Test that .pre-commit-hooks.yaml is valid and correctly configured"""

    def setUp(self):
        """Load the pre-commit hooks configuration"""
        hooks_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".pre-commit-hooks.yaml",
        )
        self.assertTrue(
            os.path.exists(hooks_path),
            ".pre-commit-hooks.yaml must exist in the repository root",
        )
        with open(hooks_path, "r") as f:
            self.hooks = yaml.safe_load(f)

    def test_hooks_is_list(self):
        """Hooks file must contain a list of hook definitions"""
        self.assertIsInstance(self.hooks, list)
        self.assertGreaterEqual(len(self.hooks), 1)

    def test_hook_has_required_fields(self):
        """Each hook must have all required fields per pre-commit spec"""
        required_fields = ["id", "name", "entry", "language", "files"]
        for hook in self.hooks:
            for field in required_fields:
                self.assertIn(
                    field,
                    hook,
                    f"Hook '{hook.get('id', 'unknown')}' missing required "
                    f"field '{field}'",
                )

    def test_asciidoc_linter_hook(self):
        """Validate the asciidoc-linter hook configuration"""
        hook = self.hooks[0]
        self.assertEqual(hook["id"], "asciidoc-linter")
        self.assertEqual(hook["language"], "python")
        self.assertEqual(hook["entry"], "asciidoc-linter")

    def test_file_pattern_matches_asciidoc_files(self):
        """File pattern must match .adoc and .asciidoc extensions"""
        hook = self.hooks[0]
        pattern = hook["files"]
        regex = re.compile(pattern)
        # Should match
        self.assertTrue(regex.search("doc.adoc"))
        self.assertTrue(regex.search("doc.asciidoc"))
        self.assertTrue(regex.search("path/to/doc.adoc"))
        # Should not match
        self.assertIsNone(regex.search("doc.md"))
        self.assertIsNone(regex.search("doc.txt"))
        self.assertIsNone(regex.search("doc.py"))

    def test_hook_description_present(self):
        """Hook should have a description"""
        hook = self.hooks[0]
        self.assertIn("description", hook)
        self.assertTrue(len(hook["description"]) > 0)


if __name__ == "__main__":
    unittest.main()
