# test_block_rules.py - Tests for block rules in BDD style
"""
Tests for all block-related rules including:
- UnterminatedBlockRule: Ensures that all blocks are properly terminated
- BlockSpacingRule: Validates proper spacing around blocks
"""

import unittest
from asciidoc_linter.rules.block_rules import UnterminatedBlockRule, BlockSpacingRule


class TestUnterminatedBlockRule(unittest.TestCase):
    """Tests for UnterminatedBlockRule.
    This rule ensures that all blocks (like listing blocks, example blocks, etc.)
    are properly terminated with their respective end markers.
    """

    def setUp(self):
        """
        Given an UnterminatedBlockRule instance
        """
        self.rule = UnterminatedBlockRule()

    def test_terminated_block(self):
        """
        Given a document with a properly terminated block
        When the unterminated block rule is checked
        Then no findings should be reported
        """
        # Given: A document with a properly terminated block
        content = [
            "Some text",
            "----",
            "This is a listing block",
            "with multiple lines",
            "----",
            "More text",
        ]

        # When: We check each line for unterminated blocks
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Properly terminated block should not produce findings"
        )

    def test_unterminated_block(self):
        """
        Given a document with an unterminated block
        When the unterminated block rule is checked
        Then one finding should be reported
        And the finding should point to the block start line
        """
        # Given: A document with an unterminated block
        content = [
            "Some text",
            "----",
            "This is an unterminated block",
            "with no end marker",
            "More text",
        ]

        # When: We check each line for unterminated blocks
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: One finding should be reported
        self.assertEqual(
            len(findings), 1, "Unterminated block should produce one finding"
        )

        # And: The finding should point to the block start line
        self.assertEqual(
            findings[0].line_number,
            2,
            "Finding should point to the line where the block starts",
        )

    def test_multiple_blocks(self):
        """
        Given a document with multiple blocks
        When the unterminated block rule is checked
        Then only unterminated blocks should be reported
        """
        # Given: A document with multiple blocks, one unterminated
        content = [
            "====",
            "Example block",
            "====",
            "",
            "----",
            "Unterminated listing block",
            "",
            "****",
            "Sidebar content",
            "****",
        ]

        # When: We check each line for unterminated blocks
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Only one finding should be reported
        self.assertEqual(
            len(findings), 1, "Only the unterminated listing block should be reported"
        )


class TestBlockSpacingRule(unittest.TestCase):
    """Tests for BlockSpacingRule.
    This rule ensures that blocks have proper spacing before and after them,
    with some exceptions for headings.
    """

    def setUp(self):
        """
        Given a BlockSpacingRule instance
        """
        self.rule = BlockSpacingRule()

    def test_correct_spacing(self):
        """
        Given a document with correct block spacing
        When the block spacing rule is checked
        Then no findings should be reported
        """
        # Given: A document with proper spacing around blocks
        content = ["Some text", "", "----", "Block content", "----", "", "More text"]

        # When: We check each line for spacing issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Properly spaced block should not produce findings"
        )

    def test_missing_space_before(self):
        """
        Given a document with missing space before a block
        When the block spacing rule is checked
        Then one finding should be reported
        And the finding should mention missing preceding space
        """
        # Given: A document with missing space before block
        content = ["Some text", "----", "Block content", "----", "", "More text"]

        # When: We check each line for spacing issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: One finding should be reported
        self.assertEqual(
            len(findings), 1, "Missing space before block should produce one finding"
        )

        # And: The finding should mention missing preceding space
        self.assertTrue(
            "preceded by" in findings[0].message,
            "Finding should mention missing preceding space",
        )

    def test_missing_space_after(self):
        """
        Given a document with missing space after a block
        When the block spacing rule is checked
        Then one finding should be reported
        And the finding should mention missing following space
        """
        # Given: A document with missing space after block
        content = ["Some text", "", "----", "Block content", "----", "More text"]

        # When: We check each line for spacing issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: One finding should be reported
        self.assertEqual(
            len(findings), 1, "Missing space after block should produce one finding"
        )

        # And: The finding should mention missing following space
        self.assertTrue(
            "followed by" in findings[0].message,
            "Finding should mention missing following space",
        )

    def test_heading_exception(self):
        """
        Given a document with blocks adjacent to headings
        When the block spacing rule is checked
        Then no findings should be reported
        Because headings are an exception to the spacing rule
        """
        # Given: A document with blocks adjacent to headings
        content = ["= Heading", "----", "Block content", "----", "= Another Heading"]

        # When: We check each line for spacing issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Blocks adjacent to headings should not produce findings"
        )


if __name__ == "__main__":
    unittest.main()
