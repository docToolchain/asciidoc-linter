# test_heading_rules.py - Tests for heading rules in BDD style
"""
Tests for all heading-related rules including:
- HeadingHierarchyRule (HEAD001): Ensures headings follow proper hierarchy
- HeadingFormatRule (HEAD002): Validates heading format conventions
- HeadingMultipleTopLevelRule (HEAD003): Checks for multiple top-level headings
"""

import unittest
from asciidoc_linter.rules import Severity
from asciidoc_linter.rules.heading_rules import (
    HeadingHierarchyRule,
    HeadingFormatRule,
    MultipleTopLevelHeadingsRule,
)


class TestHeadingFormatRule(unittest.TestCase):
    """Tests for HEAD002: Heading Format Rule.
    This rule ensures that headings follow proper formatting conventions:
    - Space after heading markers (=, ==, etc.)
    - Proper capitalization
    """

    def setUp(self):
        """
        Given a HeadingFormatRule instance
        """
        self.rule = HeadingFormatRule()

    def test_valid_format(self):
        """
        Given a document with properly formatted headings
        When the heading format rule is checked
        Then no findings should be reported
        """
        # Given: A document with properly formatted headings
        content = """
= Level 1
== Level 2
"""
        # When: We check the heading format
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Properly formatted headings should not produce findings"
        )

    def test_invalid_format(self):
        """
        Given a document with improperly formatted headings
        When the heading format rule is checked
        Then four findings should be reported
        And two findings should be about missing spaces
        And two findings should be about improper capitalization
        """
        # Given: A document with formatting issues
        content = """=level 1
==level 2"""

        # When: We check the heading format
        findings = self.rule.check(content)

        # Then: We should have exactly four findings
        self.assertEqual(
            len(findings), 4, "Expected four findings for formatting issues"
        )

        # And: All findings should have the correct rule ID
        self.assertTrue(
            all(f.rule_id == "HEAD002" for f in findings),
            "All findings should be from HEAD002 rule",
        )

        # And: We should have two space-related findings
        space_findings = [f for f in findings if "Missing space" in f.message]
        self.assertEqual(
            len(space_findings), 2, "Should have two 'missing space' findings"
        )

        # And: We should have two capitalization-related findings
        case_findings = [f for f in findings if "uppercase" in f.message]
        self.assertEqual(len(case_findings), 2, "Should have two 'uppercase' findings")


class TestHeadingHierarchyRule(unittest.TestCase):
    """Tests for HEAD001: Heading Hierarchy Rule.
    This rule ensures that heading levels are properly nested without skipping levels.
    """

    def setUp(self):
        """
        Given a HeadingHierarchyRule instance
        """
        self.rule = HeadingHierarchyRule()

    def test_valid_heading_sequence(self):
        """
        Given a document with properly nested heading levels
        When the heading hierarchy rule is checked
        Then no findings should be reported
        """
        # Given: A document with proper heading hierarchy
        content = """
= Level 1
Some content

== Level 2
More content

=== Level 3
Even more content
"""
        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Valid heading sequence should not produce findings"
        )

    def test_skipped_heading_level(self):
        """
        Given a document with a skipped heading level
        When the heading hierarchy rule is checked
        Then one error should be reported
        And the error should mention skipped levels
        """
        # Given: A document with a skipped heading level
        content = """
= Level 1
Some content

=== Level 3
Skipped level 2!
"""
        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: We should get exactly one error
        self.assertEqual(
            len(findings), 1, "Expected one finding for skipped heading level"
        )

        # And: It should be an error severity
        self.assertEqual(
            findings[0].severity,
            Severity.ERROR,
            "Skipped heading level should be reported as error",
        )

        # And: The message should mention skipped levels
        self.assertTrue(
            "skipped" in findings[0].message.lower(),
            "Error message should mention skipped levels",
        )

    def test_multiple_skipped_levels(self):
        """
        Given a document with multiple skipped heading levels
        When the heading hierarchy rule is checked
        Then one error should be reported
        And the error should be of severity ERROR
        """
        # Given: A document with multiple skipped levels
        content = """
= Level 1
Some content

==== Level 4
Skipped two levels!
"""
        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: We should get exactly one error
        self.assertEqual(
            len(findings), 1, "Expected one finding for multiple skipped heading levels"
        )

        # And: It should be an error severity
        self.assertEqual(
            findings[0].severity,
            Severity.ERROR,
            "Multiple skipped heading levels should be reported as error",
        )

    def test_empty_document(self):
        """
        Given an empty document
        When the heading hierarchy rule is checked
        Then no findings should be reported
        """
        # Given: An empty document
        content = ""

        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(len(findings), 0, "Empty document should not produce findings")

    def test_no_headings(self):
        """
        Given a document without any headings
        When the heading hierarchy rule is checked
        Then no findings should be reported
        """
        # Given: A document with no headings
        content = """
This is a document
with no headings
just regular text
"""
        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Document without headings should not produce findings"
        )

    def test_heading_underline_not_counted(self):
        """
        Given a document with heading underlines
        When the heading hierarchy rule is checked
        Then no findings should be reported
        And underlines should not be counted as headings
        """
        # Given: A document with heading underlines
        content = """
Level 1
=======
Some content

Level 2
-------
More content
"""
        # When: We check the heading hierarchy
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Heading underlines should not be counted as headings"
        )


class TestMultipleTopLevelHeadingsRule(unittest.TestCase):
    """Tests for HEAD003: Multiple Top-Level Headings Rule.
    This rule ensures that a document has only one top-level heading.
    """

    def setUp(self):
        """
        Given a MultipleTopLevelHeadingsRule instance
        """
        self.rule = MultipleTopLevelHeadingsRule()

    def test_single_top_level(self):
        """
        Given a document with a single top-level heading
        When the multiple top-level headings rule is checked
        Then no findings should be reported
        """
        # Given: A document with one top-level heading
        content = """
= Document Title
== Section 1
== Section 2
"""
        # When: We check for multiple top-level headings
        findings = self.rule.check(content)

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "Single top-level heading should not produce findings"
        )

    def test_multiple_top_level(self):
        """
        Given a document with multiple top-level headings
        When the multiple top-level headings rule is checked
        Then one error should be reported
        And the error should be of severity ERROR
        """
        # Given: A document with multiple top-level headings
        content = """
= First Title
== Section 1
= Second Title
== Section 2
"""
        # When: We check for multiple top-level headings
        findings = self.rule.check(content)

        # Then: We should get exactly one error
        self.assertEqual(
            len(findings), 1, "Expected one finding for multiple top-level headings"
        )

        # And: It should be an error severity
        self.assertEqual(
            findings[0].severity,
            Severity.ERROR,
            "Multiple top-level headings should be reported as error",
        )


if __name__ == "__main__":
    unittest.main()
