# test_markdown_table_rules.py - Tests for FMT005: Markdown table detection
"""
Tests for detecting Markdown table syntax in AsciiDoc files.
"""

import pytest
from asciidoc_linter.rules.markdown_table_rules import MarkdownTableRule
from asciidoc_linter.rules.base import Severity


@pytest.fixture
def markdown_table_rule():
    """Create a MarkdownTableRule instance for testing."""
    return MarkdownTableRule()


class TestMarkdownTableSeparatorDetection:
    """Tests for detecting Markdown table separator lines."""

    def test_detects_simple_separator(self, markdown_table_rule):
        """Test detection of simple |---|---| separator."""
        content = [
            "| Header 1 | Header 2 |",
            "|----------|----------|",
            "| Cell 1   | Cell 2   |",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) > 0
        assert any(f.rule_id == "FMT005" for f in findings)

    def test_detects_separator_with_colons(self, markdown_table_rule):
        """Test detection of separator with alignment colons |:---|:---:|."""
        content = [
            "| Left | Center | Right |",
            "|:-----|:------:|------:|",
            "| a    | b      | c     |",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) > 0
        assert any(f.rule_id == "FMT005" for f in findings)

    def test_detects_separator_with_spaces(self, markdown_table_rule):
        """Test detection of separator with spaces | --- | --- |."""
        content = [
            "| A | B |",
            "| --- | --- |",
            "| 1 | 2 |",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) > 0

    def test_detects_separator_without_trailing_pipe(self, markdown_table_rule):
        """Test detection of separator without trailing pipe |---|---."""
        content = [
            "| A | B",
            "|---|---",
            "| 1 | 2",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) > 0


class TestMarkdownTableRowDetection:
    """Tests for detecting Markdown table data/header rows."""

    def test_flags_all_rows_in_markdown_table(self, markdown_table_rule):
        """Test that all rows adjacent to separator are flagged."""
        content = [
            "| Dimension | Score | Level |",
            "|-----------|-------|-------|",
            "| Code Type | 2     | Logic |",
            "| Language  | 2     | Typed |",
        ]
        findings = markdown_table_rule.check(content)

        # Should flag separator + adjacent rows
        assert len(findings) >= 3

    def test_separator_finding_message_mentions_asciidoc(self, markdown_table_rule):
        """Test that finding message suggests AsciiDoc table syntax."""
        content = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
        ]
        findings = markdown_table_rule.check(content)

        messages = " ".join(f.message for f in findings)
        assert "AsciiDoc" in messages or "|===" in messages

    def test_reports_correct_line_numbers(self, markdown_table_rule):
        """Test that findings report correct line numbers."""
        content = [
            "Some text",
            "",
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
        ]
        findings = markdown_table_rule.check(content)

        line_numbers = [f.position.line for f in findings]
        # Lines 3, 4, 5 (1-indexed)
        assert 4 in line_numbers  # separator at line 4


class TestMarkdownTableIgnoresValidAsciiDoc:
    """Tests for ensuring valid AsciiDoc table syntax is not flagged."""

    def test_ignores_asciidoc_table(self, markdown_table_rule):
        """Test that proper AsciiDoc tables are not flagged."""
        content = [
            "|===",
            "| Header 1 | Header 2",
            "",
            "| Cell 1 | Cell 2",
            "| Cell 3 | Cell 4",
            "|===",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_ignores_asciidoc_table_with_cols(self, markdown_table_rule):
        """Test that AsciiDoc table with [cols] is not flagged."""
        content = [
            '[cols="2,1,2,4"]',
            "|===",
            "| Dimension | Score | Level | Evidence",
            "",
            "| Code Type | 2 | Business Logic | Click commands",
            "|===",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_ignores_pipe_in_regular_text(self, markdown_table_rule):
        """Test that pipes in regular text are not flagged."""
        content = [
            "Use the | operator for bitwise OR",
            "The command is: cat file | grep pattern",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_ignores_single_pipe_line(self, markdown_table_rule):
        """Test that a single pipe line is not flagged as a table."""
        content = ["| Just a single cell row"]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0


class TestMarkdownTableCodeBlockSkipping:
    """Tests for skipping Markdown tables inside code blocks."""

    def test_ignores_markdown_table_inside_listing_block(self, markdown_table_rule):
        """Test that Markdown tables inside ---- blocks are not flagged."""
        content = [
            "Some text",
            "",
            "----",
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "----",
            "",
            "More text",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_ignores_markdown_table_inside_literal_block(self, markdown_table_rule):
        """Test that Markdown tables inside .... blocks are not flagged."""
        content = [
            "....",
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "....",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_detects_markdown_table_outside_code_block(self, markdown_table_rule):
        """Test that Markdown tables outside code blocks are detected."""
        content = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "",
            "----",
            "| X | Y |",
            "|---|---|",
            "| 3 | 4 |",
            "----",
        ]
        findings = markdown_table_rule.check(content)

        # Should only flag the table outside the code block
        flagged_lines = {f.position.line for f in findings}
        assert 2 in flagged_lines  # separator on line 2
        assert 6 not in flagged_lines  # inside code block


class TestMarkdownTableEdgeCases:
    """Tests for edge cases in Markdown table detection."""

    def test_multiple_tables_in_document(self, markdown_table_rule):
        """Test detection of multiple Markdown tables."""
        content = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "",
            "Some text between tables",
            "",
            "| X | Y |",
            "|---|---|",
            "| 3 | 4 |",
        ]
        findings = markdown_table_rule.check(content)

        separator_findings = [f for f in findings if "separator" in f.message.lower()]
        assert len(separator_findings) >= 2

    def test_empty_document(self, markdown_table_rule):
        """Test with empty document."""
        content = []
        findings = markdown_table_rule.check(content)

        assert len(findings) == 0

    def test_separator_only_no_data(self, markdown_table_rule):
        """Test with separator line but no adjacent data rows."""
        content = [
            "Some text",
            "|---|---|",
            "More text",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) >= 1

    def test_real_world_adr_table(self, markdown_table_rule):
        """Test with real-world ADR table from the issue."""
        content = [
            "| Dimension | Score | Level | Evidence |",
            "|-----------|-------|-------|----------|",
            "| Code Type | 2 | Business Logic | Click commands... |",
            "| Language | 2 | Dynamically typed | Python 3.12+ |",
        ]
        findings = markdown_table_rule.check(content)

        assert len(findings) >= 3  # header + separator + 2 data rows


class TestMarkdownTableRuleMetadata:
    """Tests for FMT005 rule metadata."""

    def test_rule_id(self, markdown_table_rule):
        """Test that rule has correct ID."""
        assert markdown_table_rule.id == "FMT005"

    def test_rule_name(self, markdown_table_rule):
        """Test that rule has a name."""
        assert markdown_table_rule.name != ""

    def test_rule_description(self, markdown_table_rule):
        """Test that rule has a description."""
        assert markdown_table_rule.description != ""

    def test_rule_severity(self, markdown_table_rule):
        """Test that rule has ERROR severity."""
        assert markdown_table_rule.severity == Severity.ERROR
