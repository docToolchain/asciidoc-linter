# test_table_rules.py - Tests for table rules
"""Tests for the table rules module"""

import unittest
from asciidoc_linter.rules.table_rules import (
    TableFormatRule,
    TableStructureRule,
    TableContentRule,
)


class TestTableFormatRule(unittest.TestCase):
    """Test the TableFormatRule class"""

    def setUp(self):
        """Set up test data"""
        self.rule = TableFormatRule()

    def test_extract_table_lines(self):
        """Test table extraction from document"""
        content = [
            "Some text before",
            "|===",
            "| Header 1 | Header 2",
            "",
            "| Cell 1 | Cell 2",
            "|===",
            "Some text between",
            "|===",
            "| Another table",
            "|===",
        ]

        tables = self.rule.extract_table_lines(
            [(i, line) for i, line in enumerate(content)]
        )

        self.assertEqual(len(tables), 2)
        self.assertEqual(len(tables[0]), 5)  # First table with 5 lines
        self.assertEqual(len(tables[1]), 3)  # Second table with 3 lines

    def test_check_column_alignment(self):
        """Test column alignment checking"""
        # Well-aligned table
        aligned_table = [
            (0, "|==="),
            (1, "| Col 1    | Col 2    |"),
            (2, "| Data 1   | Data 2   |"),
            (3, "|==="),
        ]
        findings = self.rule.check_column_alignment(aligned_table)
        self.assertEqual(len(findings), 0)

        # Misaligned table
        misaligned_table = [
            (0, "|==="),
            (1, "| Col 1    | Col 2    |"),
            (2, "| Data 1| Data 2|"),  # Misaligned
            (3, "|==="),
        ]
        findings = self.rule.check_column_alignment(misaligned_table)
        self.assertEqual(len(findings), 1)
        self.assertIn("Column alignment", findings[0].message)

    def test_check_header_separator(self):
        """Test header separator checking"""
        # Table with proper header separation
        good_table = [
            (0, "|==="),
            (1, "| Header 1 | Header 2"),
            (2, ""),
            (3, "| Cell 1 | Cell 2"),
            (4, "|==="),
        ]
        findings = self.rule.check_header_separator(good_table)
        self.assertEqual(len(findings), 0)

        # Table without header separation
        bad_table = [
            (0, "|==="),
            (1, "| Header 1 | Header 2"),
            (2, "| Cell 1 | Cell 2"),  # Missing empty line
            (3, "|==="),
        ]
        findings = self.rule.check_header_separator(bad_table)
        self.assertEqual(len(findings), 1)
        self.assertIn("Header row", findings[0].message)

    def test_check_complete(self):
        """Test complete table checking"""
        document = "\n".join(
            [
                "Some text",
                "|===",
                "| Header 1 | Header 2",
                "| Cell 1   | Cell 2  ",
                "|===",
            ]
        )

        findings = self.rule.check(document)
        self.assertEqual(len(findings), 1)  # Should find missing header separator


class TestTableStructureRule(unittest.TestCase):
    """Test the TableStructureRule class"""

    def setUp(self):
        """Set up test data"""
        self.rule = TableStructureRule()

    def test_count_columns(self):
        """Test column counting"""
        self.assertEqual(self.rule.count_columns("| Col 1 | Col 2 | Col 3"), 3)
        self.assertEqual(self.rule.count_columns("|==="), 0)
        self.assertEqual(self.rule.count_columns("| Single column"), 1)

    def test_check_table_structure_consistent(self):
        """Test table with consistent structure"""
        table = [
            (0, "|==="),
            (1, "| Col 1 | Col 2"),
            (2, "| Cell 1 | Cell 2"),
            (3, "|==="),
        ]

        findings = self.rule.check_table_structure(table)
        self.assertEqual(len(findings), 0)

    def test_check_table_structure_inconsistent(self):
        """Test table with inconsistent structure"""
        table = [
            (0, "|==="),
            (1, "| Col 1 | Col 2"),
            (2, "| Cell 1 | Cell 2 | Cell 3"),  # Extra column
            (3, "|==="),
        ]

        findings = self.rule.check_table_structure(table)
        self.assertEqual(len(findings), 1)
        self.assertIn("Inconsistent column count", findings[0].message)

    def test_empty_table(self):
        """Test empty table detection"""
        table = [(0, "|==="), (1, ""), (2, "|===")]

        findings = self.rule.check_table_structure(table)
        self.assertEqual(len(findings), 1)
        self.assertIn("Empty table", findings[0].message)

    def test_check_complete(self):
        """Test complete table checking"""
        document = "\n".join(
            [
                "|===",
                "| Col 1 | Col 2",
                "| Cell 1 | Cell 2 | Cell 3",  # Inconsistent
                "|===",
            ]
        )

        findings = self.rule.check(document)
        self.assertEqual(len(findings), 1)
        self.assertIn("Inconsistent column count", findings[0].message)


class TestTableContentRule(unittest.TestCase):
    """Test the TableContentRule class"""

    def setUp(self):
        """Set up test data"""
        self.rule = TableContentRule()

    def test_extract_cells(self):
        """Test cell extraction"""
        # Simple cells
        cells = self.rule.extract_cells("| Cell 1 | Cell 2")
        self.assertEqual(len(cells), 2)
        self.assertEqual(cells[0], ("", "Cell 1"))
        self.assertEqual(cells[1], ("", "Cell 2"))

        # Cells with prefixes
        cells = self.rule.extract_cells("| Simple | a| Complex | l| List")
        self.assertEqual(len(cells), 3)
        self.assertEqual(cells[1], ("a", "Complex"))
        self.assertEqual(cells[2], ("l", "List"))

    def test_check_cell_content_simple(self):
        """Test checking simple cell content"""
        finding = self.rule.check_cell_content(
            "", "Simple content", 1, "| Simple content"
        )
        self.assertIsNone(finding)

    def test_check_cell_content_list_without_prefix(self):
        """Test checking cell with list but no prefix"""
        finding = self.rule.check_cell_content("", "* List item", 1, "| * List item")
        self.assertIsNotNone(finding)
        self.assertIn("List in table cell", finding.message)

    def test_check_cell_content_list_with_prefix(self):
        """Test checking cell with list and correct prefix"""
        finding = self.rule.check_cell_content("a", "* List item", 1, "a| * List item")
        self.assertIsNone(finding)

        finding = self.rule.check_cell_content("l", "* List item", 1, "l| * List item")
        self.assertIsNone(finding)

    def test_check_complete(self):
        """Test complete content checking"""
        document = "\n".join(
            [
                "|===",
                "| Normal | * List without prefix",
                "| Normal | a| * List with prefix",
                "|===",
            ]
        )

        findings = self.rule.check(document)
        self.assertEqual(len(findings), 1)  # Should find one list without prefix
        self.assertIn("List in table cell", findings[0].message)


if __name__ == "__main__":
    unittest.main()
