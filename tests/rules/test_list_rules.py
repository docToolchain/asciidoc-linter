# test_list_rules.py - Tests for list rules
"""
Tests for ListAfterParagraphRule (LIST001), issue #51
"""

import unittest

from asciidoc_linter.rules.list_rules import ListAfterParagraphRule


class TestListAfterParagraphRule(unittest.TestCase):
    """LIST001: a list needs an empty line after a paragraph"""

    def setUp(self):
        self.rule = ListAfterParagraphRule()

    def lines_flagged(self, content):
        return [f.position.line for f in self.rule.check(content)]

    def test_issue_51_example_is_flagged(self):
        """Issue #51: 'Clang++' glues the list to a paragraph"""
        content = [
            "=== Prerequisites",
            "",
            "Required tools:",
            "",
            "Clang++",
            "* make",
            "* zip",
        ]
        self.assertEqual(self.lines_flagged(content), [6])

    def test_list_after_empty_line_not_flagged(self):
        content = ["Required tools:", "", "* Clang++", "* make", "* zip"]
        self.assertEqual(self.lines_flagged(content), [])

    def test_all_list_markers_detected(self):
        for item in ["- item", ". item", "** item", "1. item", "* [x] done"]:
            with self.subTest(item=item):
                self.assertEqual(self.lines_flagged(["Some text", item]), [2])

    def test_list_after_prefix_lines_not_flagged(self):
        for prefix in ["== Section", ".Title", "[square]", "// comment", ":a: b"]:
            with self.subTest(prefix=prefix):
                content = ["", prefix, "* item", "* item"]
                self.assertEqual(self.lines_flagged(content), [])

    def test_nested_list_and_continuation_not_flagged(self):
        content = [
            "* item",
            "continued item text",
            "** nested",
            "+",
            "attached paragraph",
            "* next",
        ]
        self.assertEqual(self.lines_flagged(content), [])

    def test_list_under_definition_term_not_flagged(self):
        content = ["Tools::", "* make", "* zip"]
        self.assertEqual(self.lines_flagged(content), [])

    def test_bold_text_not_flagged(self):
        content = ["Some text", "*bold* text continues"]
        self.assertEqual(self.lines_flagged(content), [])

    def test_verbatim_block_and_table_content_ignored(self):
        content = [
            "----",
            "text",
            "* not a list",
            "----",
            "",
            "|===",
            "a|cell text",
            "* list in cell",
            "|===",
        ]
        self.assertEqual(self.lines_flagged(content), [])

    def test_csv_and_dsv_table_content_ignored(self):
        for delimiter in [",===", ":==="]:
            with self.subTest(delimiter=delimiter):
                content = [delimiter, "text", "* not a list", delimiter]
                self.assertEqual(self.lines_flagged(content), [])

    def test_nested_table_content_ignored(self):
        content = [
            "|===",
            "a|",
            "!===",
            "! cell text",
            "* not a list",
            "!===",
            "cell text",
            "* not a list either",
            "|===",
            "",
            "Text after the table",
            "* flagged",
        ]
        self.assertEqual(self.lines_flagged(content), [12])

    def test_list_directly_after_block_delimiter_not_flagged(self):
        content = ["====", "* item", "===="]
        self.assertEqual(self.lines_flagged(content), [])

    def test_description_list_after_paragraph_is_flagged(self):
        """A glued description list is paragraph text as well"""
        for term in ["Term:: value", "Term::", "Term;; value", "Term::: value"]:
            with self.subTest(term=term):
                self.assertEqual(self.lines_flagged(["Some text", term]), [2])

    def test_double_colon_in_prose_not_flagged(self):
        """'::' preceded by a space or inside a word is not a term"""
        for line in ["the scope operator :: works", "use std::vector here"]:
            with self.subTest(line=line):
                self.assertEqual(self.lines_flagged(["Some text", line]), [])

    def test_prefix_lines_inside_paragraph_do_not_end_it(self):
        """.Title, [attrs] and comments after paragraph text are paragraph text"""
        for prefix in [".Title", "[square]"]:
            with self.subTest(prefix=prefix):
                content = ["Paragraph", prefix, "* item"]
                self.assertEqual(self.lines_flagged(content), [3])


if __name__ == "__main__":
    unittest.main()
