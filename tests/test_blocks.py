# test_blocks.py - Tests for verbatim block detection and its effects
"""
Tests for the shared verbatim-block detection helper and its use in the
parser. Content inside ----, ...., and ++++ blocks must be treated as
literal text (issues #52 and #54).
"""

import unittest

from asciidoc_linter.blocks import find_code_block_content_lines
from asciidoc_linter.parser import AsciiDocParser, Header


class TestFindCodeBlockContentLines(unittest.TestCase):
    """Tests for find_code_block_content_lines."""

    def test_listing_block_content_detected(self):
        """Lines strictly inside a ---- block are reported, delimiters are not."""
        lines = [
            "before",  # 0
            "----",  # 1 opening delimiter
            "inside 1",  # 2
            "inside 2",  # 3
            "----",  # 4 closing delimiter
            "after",  # 5
        ]
        self.assertEqual(find_code_block_content_lines(lines), {2, 3})

    def test_literal_and_passthrough_blocks(self):
        """.... and ++++ blocks are treated as verbatim too."""
        lines = ["....", "lit", "....", "x", "++++", "pass", "++++"]
        self.assertEqual(find_code_block_content_lines(lines), {1, 5})

    def test_unterminated_block_runs_to_eof(self):
        """An unterminated block extends to the end of the document."""
        lines = ["----", "a", "b"]
        self.assertEqual(find_code_block_content_lines(lines), {1, 2})

    def test_nested_delimiter_of_other_type_is_content(self):
        """A different delimiter inside a block is just verbatim content."""
        lines = ["----", "....", "----"]
        # The inner '....' is content of the ---- block, not a new block.
        self.assertEqual(find_code_block_content_lines(lines), {1})

    def test_no_blocks(self):
        self.assertEqual(find_code_block_content_lines(["a", "== b", "c"]), set())

    def test_long_delimiter_runs(self):
        """Delimiters may be any run of >= 4 chars (AsciiDoc), not just four."""
        lines = [
            "[source,]",  # 0
            "----------------",  # 1 opening delimiter (16 dashes)
            "-----BEGIN CERTIFICATE-----",  # 2 content, not a delimiter
            "base64data",  # 3
            "-----END CERTIFICATE-----",  # 4
            "----------------",  # 5 closing delimiter
            "after",  # 6
        ]
        self.assertEqual(find_code_block_content_lines(lines), {2, 3, 4})

    def test_closing_delimiter_must_match_length(self):
        """A shorter run inside a longer block is content, not a close."""
        lines = [
            "--------",  # 0 opening (8 dashes)
            "---",  # 1 content: 3 dashes is not even a delimiter
            "----",  # 2 content: 4 dashes, wrong length, does not close
            "--------",  # 3 real close (8 dashes)
            "outside",  # 4
        ]
        self.assertEqual(find_code_block_content_lines(lines), {1, 2})

    def test_short_runs_are_not_delimiters(self):
        """Runs shorter than four characters never open a block."""
        lines = ["---", "not in a block", "..."]
        self.assertEqual(find_code_block_content_lines(lines), set())


class TestParserSkipsVerbatimBlocks(unittest.TestCase):
    """The parser must not emit Headers for section titles inside blocks."""

    def test_section_title_inside_block_is_not_a_header(self):
        content = (
            "= Title\n"
            "\n"
            "[source,asciidoc]\n"
            "----\n"
            "=== S-01: Example heading\n"
            "----\n"
            "\n"
            "== Real section\n"
        )
        headers = AsciiDocParser().parse(content)
        contents = [h.content for h in headers if isinstance(h, Header)]
        self.assertIn("= Title", contents)
        self.assertIn("== Real section", contents)
        self.assertNotIn("=== S-01: Example heading", contents)

    def test_line_numbers_are_preserved(self):
        content = "= Title\n----\n=== inside\n----\n\n== Real\n"
        headers = {h.content: h.line_number for h in AsciiDocParser().parse(content)}
        self.assertEqual(headers["= Title"], 1)
        self.assertEqual(headers["== Real"], 6)


if __name__ == "__main__":
    unittest.main()
