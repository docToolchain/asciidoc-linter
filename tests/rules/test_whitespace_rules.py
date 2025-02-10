# test_whitespace_rules.py - Tests for whitespace rules in BDD style
"""
Tests for whitespace-related rules including:
- Multiple consecutive empty lines
- List marker spacing
- Admonition block spacing
- Trailing whitespace
- Tab usage
- Section title spacing
"""

import unittest
from asciidoc_linter.rules.whitespace_rules import WhitespaceRule


class TestWhitespaceRule(unittest.TestCase):
    """Tests for WhitespaceRule.
    This rule ensures proper whitespace usage throughout the document,
    including line spacing, indentation, and formatting conventions.
    """

    def setUp(self):
        """
        Given a WhitespaceRule instance
        """
        self.rule = WhitespaceRule()

    def test_multiple_empty_lines(self):
        """
        Given a document with multiple consecutive empty lines
        When the whitespace rule is checked
        Then one finding should be reported
        And the finding should mention consecutive empty lines
        """
        # Given: A document with multiple consecutive empty lines
        content = ["First line", "", "", "", "Last line"]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: One finding should be reported
        self.assertEqual(
            len(findings),
            1,
            "Multiple consecutive empty lines should produce one finding",
        )

        # And: The finding should mention consecutive empty lines
        self.assertTrue(
            "consecutive empty line" in findings[0].message,
            "Finding should mention consecutive empty lines",
        )

    def test_list_marker_spacing(self):
        """
        Given a document with both valid and invalid list markers
        When the whitespace rule is checked
        Then three findings should be reported
        And each finding should mention space after the marker
        """
        # Given: A document with various list markers
        content = [
            "* Valid item",
            "*Invalid item",
            "- Valid item",
            "-Invalid item",
            ". Valid item",
            ".Invalid item",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Three findings should be reported
        self.assertEqual(
            len(findings), 3, "Three invalid list markers should produce three findings"
        )

        # And: Each finding should mention space after the marker
        for finding in findings:
            self.assertTrue(
                "space after the marker" in finding.message,
                "Finding should mention missing space after marker",
            )

    def test_admonition_block_spacing(self):
        """
        Given a document with admonition blocks
        When the whitespace rule is checked
        Then findings should be reported for blocks without proper spacing
        And findings should mention blank line requirements
        """
        # Given: A document with various admonition blocks
        content = [
            "Some text",
            "NOTE: This needs a blank line",
            "",
            "IMPORTANT: This is correct",
            "More text",
            "WARNING: This needs a blank line",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Two findings should be reported
        self.assertEqual(
            len(findings),
            2,
            "Two admonition blocks without proper spacing should produce two findings",
        )

        # And: Each finding should mention blank line requirements
        for finding in findings:
            self.assertTrue(
                "preceded by a blank line" in finding.message,
                "Finding should mention missing blank line requirement",
            )

    def test_trailing_whitespace(self):
        """
        Given a document with lines containing trailing whitespace
        When the whitespace rule is checked
        Then findings should be reported for lines with trailing spaces
        And findings should mention trailing whitespace
        """
        # Given: A document with trailing whitespace
        content = [
            "Line without trailing space",
            "Line with trailing space ",
            "Another clean line",
            "More trailing space  ",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Two findings should be reported
        self.assertEqual(
            len(findings),
            2,
            "Two lines with trailing whitespace should produce two findings",
        )

        # And: Each finding should mention trailing whitespace
        for finding in findings:
            self.assertTrue(
                "trailing whitespace" in finding.message,
                "Finding should mention trailing whitespace",
            )

    def test_tabs(self):
        """
        Given a document with lines containing tabs
        When the whitespace rule is checked
        Then findings should be reported for lines with tabs
        And findings should mention tab usage
        """
        # Given: A document with tab characters
        content = [
            "Normal line",
            "\tLine with tab",
            "    Spaces are fine",
            "\tAnother tab",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Two findings should be reported
        self.assertEqual(
            len(findings), 2, "Two lines with tabs should produce two findings"
        )

        # And: Each finding should mention tab usage
        for finding in findings:
            self.assertTrue(
                "contains tabs" in finding.message, "Finding should mention tab usage"
            )

    def test_section_title_spacing(self):
        """
        Given a document with section titles
        When the whitespace rule is checked
        Then findings should be reported for improper spacing around titles
        And findings should mention both preceding and following space requirements
        """
        # Given: A document with section titles
        content = [
            "Some text",
            "== Section Title",
            "No space after",
            "",
            "=== Another Section",
            "",
            "This is correct",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Two findings should be reported
        self.assertEqual(
            len(findings),
            2,
            "Two spacing issues around section titles should produce two findings",
        )

        # And: Findings should mention both preceding and following space requirements
        self.assertTrue(
            any("preceded by" in f.message for f in findings),
            "Should report missing preceding space",
        )
        self.assertTrue(
            any("followed by" in f.message for f in findings),
            "Should report missing following space",
        )

    def test_valid_document(self):
        """
        Given a well-formatted document
        When the whitespace rule is checked
        Then no findings should be reported
        Because all whitespace conventions are followed
        """
        # Given: A well-formatted document
        content = [
            "= Document Title",
            "",
            "== Section 1",
            "",
            "* List item 1",
            "* List item 2",
            "",
            "NOTE: Important note",
            "",
            "=== Subsection",
            "",
            "Normal paragraph.",
        ]

        # When: We check each line for whitespace issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Well-formatted document should not produce any findings"
        )


if __name__ == "__main__":
    unittest.main()
