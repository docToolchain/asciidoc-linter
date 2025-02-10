# test_table_rules.py - Tests for table rules in BDD style
"""
Tests for all table-related rules including:
- TableFormatRule: Ensures consistent table formatting
- TableStructureRule: Validates table structure and column counts
- TableContentRule: Checks for complex content in cells
"""

import unittest
from asciidoc_linter.rules.table_rules import (
    TableFormatRule,
    TableStructureRule,
    TableContentRule,
)


class TestTableFormatRule(unittest.TestCase):
    """Tests for TableFormatRule.
    This rule ensures that tables are consistently formatted:
    - Column separators are properly aligned
    - Header row is properly marked
    - Cells are properly aligned
    """

    def setUp(self):
        """
        Given a TableFormatRule instance
        """
        self.rule = TableFormatRule()

    def test_valid_table(self):
        """
        Given a properly formatted table
        When the table format rule is checked
        Then no findings should be reported
        """
        content = [
            "|===",
            "|Column 1 |Column 2 |Column 3",
            "",
            "|Cell 1.1 |Cell 1.2 |Cell 1.3",
            "|Cell 2.1 |Cell 2.2 |Cell 2.3",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 0, "Well-formatted table should not produce findings"
        )

    def test_misaligned_columns(self):
        """
        Given a table with misaligned columns
        When the table format rule is checked
        Then one finding should be reported
        And the finding should mention column alignment
        """
        content = [
            "|===",
            "|Column 1|Column 2   |Column 3",
            "",
            "|Cell 1.1 |Cell 1.2|Cell 1.3",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 1, "Misaligned columns should produce one finding"
        )
        self.assertTrue(
            "alignment" in findings[0].message.lower(),
            "Finding should mention column alignment",
        )

    def test_missing_header_separator(self):
        """
        Given a table with missing header separator
        When the table format rule is checked
        Then one finding should be reported
        And the finding should mention header separator
        """
        content = [
            "|===",
            "|Column 1 |Column 2 |Column 3",
            "|Cell 1.1 |Cell 1.2 |Cell 1.3",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 1, "Missing header separator should produce one finding"
        )
        self.assertTrue(
            "header" in findings[0].message.lower(),
            "Finding should mention header separator",
        )


class TestTableStructureRule(unittest.TestCase):
    """Tests for TableStructureRule.
    This rule ensures that tables have consistent structure:
    - All rows have the same number of columns
    - No empty tables
    - No missing cells
    """

    def setUp(self):
        """
        Given a TableStructureRule instance
        """
        self.rule = TableStructureRule()

    def test_consistent_columns(self):
        """
        Given a table with consistent column count
        When the table structure rule is checked
        Then no findings should be reported
        """
        content = [
            "|===",
            "|Column 1 |Column 2 |Column 3",
            "",
            "|Cell 1.1 |Cell 1.2 |Cell 1.3",
            "|Cell 2.1 |Cell 2.2 |Cell 2.3",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings),
            0,
            "Table with consistent columns should not produce findings",
        )

    def test_inconsistent_columns(self):
        """
        Given a table with inconsistent column count
        When the table structure rule is checked
        Then one finding should be reported
        And the finding should mention column count
        """
        content = [
            "|===",
            "|Column 1 |Column 2 |Column 3",
            "",
            "|Cell 1.1 |Cell 1.2",  # Missing one column
            "|Cell 2.1 |Cell 2.2 |Cell 2.3",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 1, "Inconsistent column count should produce one finding"
        )
        self.assertTrue(
            "column" in findings[0].message.lower(),
            "Finding should mention column count",
        )

    def test_empty_table(self):
        """
        Given an empty table
        When the table structure rule is checked
        Then one finding should be reported
        And the finding should mention empty table
        """
        content = [
            "|===",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(len(findings), 1, "Empty table should produce one finding")
        self.assertTrue(
            "empty" in findings[0].message.lower(), "Finding should mention empty table"
        )


class TestTableContentRule(unittest.TestCase):
    """Tests for TableContentRule.
    This rule ensures that table cells don't contain complex content
    without proper declarations:
    - Lists in cells
    - Code blocks in cells
    - Nested tables
    """

    def setUp(self):
        """
        Given a TableContentRule instance
        """
        self.rule = TableContentRule()

    def test_simple_content(self):
        """
        Given a table with simple cell content
        When the table content rule is checked
        Then no findings should be reported
        """
        content = [
            "|===",
            "|Column 1 |Column 2",
            "",
            "|Simple text |More text",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 0, "Simple cell content should not produce findings"
        )

    def test_undeclared_list(self):
        """
        Given a table with an undeclared list in a cell
        When the table content rule is checked
        Then one finding should be reported
        And the finding should mention list declaration
        """
        content = [
            "|===",
            "|Column 1 |Column 2",
            "",
            "|* List item 1 |Simple text",  # Undeclared list
            "|* List item 2 |",
            "|===",
        ]

        findings = self.rule.check(content)

        self.assertEqual(
            len(findings), 1, "Undeclared list in cell should produce one finding"
        )
        self.assertTrue(
            "list" in findings[0].message.lower(),
            "Finding should mention list declaration",
        )


if __name__ == "__main__":
    unittest.main()
