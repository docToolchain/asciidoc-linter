# test_format_rules.py - Tests for format rules (FMT004: Markdown syntax detection)
"""
Tests for format rules that detect Markdown syntax in AsciiDoc files.
"""

import pytest
from asciidoc_linter.rules.format_rules import (
    MarkdownSyntaxRule,
    ExplicitNumberedListRule,
    NonSemanticDefinitionListRule,
    CounterInTitleRule,
)
from asciidoc_linter.rules.base import Severity


@pytest.fixture
def rule():
    """Create a MarkdownSyntaxRule instance for testing."""
    return MarkdownSyntaxRule()


# Tests for Markdown heading detection


class TestMarkdownHeadingDetection:
    """Tests for detecting Markdown-style headings."""

    def test_detects_markdown_h1(self, rule):
        """Test detection of Markdown # heading."""
        content = ["# This is a Markdown heading"]
        findings = rule.check(content)

        assert len(findings) == 1
        assert findings[0].rule_id == "FMT004"
        assert "# " in findings[0].message
        assert "= " in findings[0].message

    def test_detects_markdown_h2(self, rule):
        """Test detection of Markdown ## heading."""
        content = ["## Subheading"]
        findings = rule.check(content)

        assert len(findings) == 1
        assert "## " in findings[0].message
        assert "== " in findings[0].message

    def test_detects_markdown_h3_to_h6(self, rule):
        """Test detection of Markdown ### to ###### headings."""
        content = [
            "### Level 3",
            "#### Level 4",
            "##### Level 5",
            "###### Level 6",
        ]
        findings = rule.check(content)

        assert len(findings) == 4

    def test_ignores_asciidoc_comment(self, rule):
        """Test that AsciiDoc comments starting with // are not flagged."""
        content = ["// This is a comment, not a heading"]
        findings = rule.check(content)

        # Should not detect this as Markdown
        markdown_findings = [f for f in findings if "heading" in f.message.lower()]
        assert len(markdown_findings) == 0

    def test_ignores_hash_in_middle_of_line(self, rule):
        """Test that # in the middle of a line is not flagged as heading."""
        content = ["This is a sentence with # symbol"]
        findings = rule.check(content)

        markdown_findings = [f for f in findings if "heading" in f.message.lower()]
        assert len(markdown_findings) == 0

    def test_ignores_asciidoc_attribute(self, rule):
        """Test that AsciiDoc attributes are not flagged."""
        content = [":icons: font", ":toc: left"]
        findings = rule.check(content)

        assert len(findings) == 0


# Tests for Markdown link detection


class TestMarkdownLinkDetection:
    """Tests for detecting Markdown-style links."""

    def test_detects_markdown_link(self, rule):
        """Test detection of Markdown [text](url) link."""
        content = ["Check out [this link](https://example.com) for more info."]
        findings = rule.check(content)

        assert len(findings) == 1
        assert "[text](url)" in findings[0].message or "link:" in findings[0].message

    def test_detects_multiple_markdown_links(self, rule):
        """Test detection of multiple Markdown links on one line."""
        content = ["See [link1](url1) and [link2](url2) for details."]
        findings = rule.check(content)

        assert len(findings) == 2

    def test_ignores_asciidoc_link(self, rule):
        """Test that AsciiDoc links are not flagged."""
        content = ["Check out link:https://example.com[this link] for more info."]
        findings = rule.check(content)

        link_findings = [f for f in findings if "link" in f.message.lower()]
        assert len(link_findings) == 0

    def test_ignores_asciidoc_macro_brackets(self, rule):
        """Test that AsciiDoc macro brackets are not flagged."""
        content = ["image::diagram.png[Architecture Diagram]"]
        findings = rule.check(content)

        link_findings = [f for f in findings if "[text](url)" in f.message]
        assert len(link_findings) == 0


# Tests for Markdown image detection


class TestMarkdownImageDetection:
    """Tests for detecting Markdown-style images."""

    def test_detects_markdown_image(self, rule):
        """Test detection of Markdown ![alt](path) image."""
        content = ["![Screenshot](images/screenshot.png)"]
        findings = rule.check(content)

        assert len(findings) == 1
        assert "image" in findings[0].message.lower()

    def test_detects_markdown_image_with_empty_alt(self, rule):
        """Test detection of Markdown image with empty alt text."""
        content = ["![](path/to/image.jpg)"]
        findings = rule.check(content)

        assert len(findings) == 1

    def test_ignores_asciidoc_image(self, rule):
        """Test that AsciiDoc images are not flagged."""
        content = [
            "image::diagram.png[Diagram]",
            "image:icon.png[Icon]",
        ]
        findings = rule.check(content)

        image_findings = [f for f in findings if "![" in f.message]
        assert len(image_findings) == 0


# Tests for Markdown code block detection


class TestMarkdownCodeBlockDetection:
    """Tests for detecting Markdown-style code blocks."""

    def test_detects_markdown_code_fence(self, rule):
        """Test detection of Markdown ``` code fence."""
        content = ["```python", "def hello():", "    print('Hello')", "```"]
        findings = rule.check(content)

        # Should detect the opening and closing ```
        code_findings = [f for f in findings if "```" in f.message]
        assert len(code_findings) == 2

    def test_detects_markdown_code_fence_without_language(self, rule):
        """Test detection of Markdown ``` without language specifier."""
        content = ["```", "some code", "```"]
        findings = rule.check(content)

        code_findings = [f for f in findings if "```" in f.message]
        assert len(code_findings) == 2

    def test_ignores_asciidoc_listing_block(self, rule):
        """Test that AsciiDoc listing blocks are not flagged."""
        content = ["----", "some code", "----"]
        findings = rule.check(content)

        code_findings = [f for f in findings if "```" in f.message]
        assert len(code_findings) == 0


# Tests for Markdown blockquote detection


class TestMarkdownBlockquoteDetection:
    """Tests for detecting Markdown-style blockquotes."""

    def test_detects_markdown_blockquote(self, rule):
        """Test detection of Markdown > blockquote."""
        content = ["> This is a quoted text"]
        findings = rule.check(content)

        assert len(findings) == 1
        assert ">" in findings[0].message

    def test_detects_nested_markdown_blockquote(self, rule):
        """Test detection of nested Markdown >> blockquote."""
        content = [">> Nested quote"]
        findings = rule.check(content)

        assert len(findings) == 1

    def test_ignores_greater_than_in_content(self, rule):
        """Test that > in the middle of content is not flagged."""
        content = ["The value is 5 > 3"]
        findings = rule.check(content)

        quote_findings = [f for f in findings if "blockquote" in f.message.lower()]
        assert len(quote_findings) == 0


# Tests for rule metadata


class TestRuleMetadata:
    """Tests for rule metadata and configuration."""

    def test_rule_id(self, rule):
        """Test that rule has correct ID."""
        assert rule.id == "FMT004"

    def test_rule_name(self, rule):
        """Test that rule has a name."""
        assert rule.name != ""

    def test_rule_description(self, rule):
        """Test that rule has a description."""
        assert rule.description != ""

    def test_rule_severity(self, rule):
        """Test that rule has WARNING severity by default."""
        assert rule.severity == Severity.WARNING


# Integration tests


class TestCodeBlockSkipping:
    """Tests for skipping content inside code blocks."""

    def test_skips_markdown_inside_listing_block(self, rule):
        """Test that Markdown inside ---- blocks is not flagged."""
        content = [
            "Some text",
            "",
            "[source,bash]",
            "----",
            "# This is a bash comment, not a Markdown heading",
            "echo 'hello'",
            "----",
            "",
            "More text",
        ]
        findings = rule.check(content)

        # Should not detect any Markdown patterns
        assert len(findings) == 0

    def test_skips_markdown_inside_literal_block(self, rule):
        """Test that Markdown inside .... blocks is not flagged."""
        content = [
            "....",
            "# Not a heading",
            "[link](url)",
            "....",
        ]
        findings = rule.check(content)

        assert len(findings) == 0

    def test_detects_markdown_outside_code_block(self, rule):
        """Test that Markdown outside code blocks is still detected."""
        content = [
            "# This IS a Markdown heading",
            "",
            "----",
            "# This is inside a code block",
            "----",
            "",
            "## This is also a Markdown heading",
        ]
        findings = rule.check(content)

        # Should detect the headings outside the code block
        assert len(findings) == 2
        assert "# " in findings[0].message
        assert "## " in findings[1].message


class TestIntegration:
    """Integration tests with mixed content."""

    def test_mixed_markdown_patterns(self, rule):
        """Test detection of multiple Markdown patterns in one document."""
        content = [
            "# Markdown Heading",
            "",
            "This has a [link](https://example.com) and an image:",
            "",
            "![Screenshot](image.png)",
            "",
            "> This is a quote",
            "",
            "```python",
            "print('hello')",
            "```",
        ]
        findings = rule.check(content)

        # Should detect: heading, link, image, quote, 2x code fence
        assert len(findings) >= 6

    def test_valid_asciidoc_not_flagged(self, rule):
        """Test that valid AsciiDoc content is not flagged."""
        content = [
            "= AsciiDoc Heading",
            "",
            "This has a link:https://example.com[link] and an image:",
            "",
            "image::image.png[Screenshot]",
            "",
            "[quote]",
            "____",
            "This is a quote",
            "____",
            "",
            "[source,python]",
            "----",
            "print('hello')",
            "----",
        ]
        findings = rule.check(content)

        # Should not detect any Markdown patterns
        assert len(findings) == 0


# =============================================================================
# FMT001: Explicit Numbered List Detection Tests
# =============================================================================


@pytest.fixture
def numbered_list_rule():
    """Create an ExplicitNumberedListRule instance for testing."""
    return ExplicitNumberedListRule()


class TestExplicitNumberedListDetection:
    """Tests for detecting explicit numbered lists."""

    def test_detects_simple_numbered_list(self, numbered_list_rule):
        """Test detection of simple 1. 2. 3. numbered list."""
        content = ["1. First item", "2. Second item", "3. Third item"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 3
        assert findings[0].rule_id == "FMT001"
        assert ". " in findings[0].message

    def test_detects_single_numbered_item(self, numbered_list_rule):
        """Test detection of a single numbered item."""
        content = ["1. Only item"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 1

    def test_detects_high_numbers(self, numbered_list_rule):
        """Test detection of high numbered items like 10. or 100."""
        content = ["10. Tenth item", "100. Hundredth item"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 2

    def test_ignores_asciidoc_ordered_list(self, numbered_list_rule):
        """Test that AsciiDoc . syntax is not flagged."""
        content = [". First item", ". Second item", ". Third item"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_decimal_numbers(self, numbered_list_rule):
        """Test that decimal numbers like 1.5 are not flagged."""
        content = ["The value is 1.5 kg", "Version 2.0 released"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_number_dot_no_space(self, numbered_list_rule):
        """Test that number.word (no space) is not flagged."""
        content = ["See section 1.Introduction", "Chapter 2.Methods"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_numbered_list_in_code_block(self, numbered_list_rule):
        """Test that numbered lists inside code blocks are not flagged."""
        content = [
            "Some text",
            "",
            "----",
            "1. This is inside a code block",
            "2. Should not be flagged",
            "----",
            "",
            "More text",
        ]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_numbered_list_in_literal_block(self, numbered_list_rule):
        """Test that numbered lists inside literal blocks are not flagged."""
        content = [
            "....",
            "1. Inside literal block",
            "....",
        ]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_detects_outside_code_block(self, numbered_list_rule):
        """Test that numbered lists outside code blocks are detected."""
        content = [
            "1. Before code block",
            "",
            "----",
            "1. Inside code block",
            "----",
            "",
            "2. After code block",
        ]
        findings = numbered_list_rule.check(content)

        # Should detect only the ones outside
        assert len(findings) == 2

    def test_ignores_numbered_in_middle_of_line(self, numbered_list_rule):
        """Test that numbers in the middle of a line are not flagged."""
        content = ["See step 1. for details", "Refer to item 2. above"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 0

    def test_message_suggests_dot_syntax(self, numbered_list_rule):
        """Test that the message suggests using . syntax."""
        content = ["1. First item"]
        findings = numbered_list_rule.check(content)

        assert len(findings) == 1
        assert ". " in findings[0].message or "dot" in findings[0].message.lower()


class TestExplicitNumberedListRuleMetadata:
    """Tests for FMT001 rule metadata."""

    def test_rule_id(self, numbered_list_rule):
        """Test that rule has correct ID."""
        assert numbered_list_rule.id == "FMT001"

    def test_rule_name(self, numbered_list_rule):
        """Test that rule has a name."""
        assert numbered_list_rule.name != ""

    def test_rule_description(self, numbered_list_rule):
        """Test that rule has a description."""
        assert numbered_list_rule.description != ""

    def test_rule_severity(self, numbered_list_rule):
        """Test that rule has WARNING severity by default."""
        assert numbered_list_rule.severity == Severity.WARNING


# =============================================================================
# FMT002: Non-Semantic Definition List Detection Tests
# =============================================================================


@pytest.fixture
def definition_list_rule():
    """Create a NonSemanticDefinitionListRule instance for testing."""
    return NonSemanticDefinitionListRule()


class TestNonSemanticDefinitionListDetection:
    """Tests for detecting non-semantic definition list patterns."""

    def test_detects_single_asterisk_term_colon(self, definition_list_rule):
        """Test detection of *Term*: pattern."""
        content = ["*Term*: This is the definition"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 1
        assert findings[0].rule_id == "FMT002"
        assert "::" in findings[0].message

    def test_detects_double_asterisk_term_colon(self, definition_list_rule):
        """Test detection of **Term**: pattern."""
        content = ["**Term**: This is the definition"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 1

    def test_detects_list_item_with_bold_term(self, definition_list_rule):
        """Test detection of - *Term*: pattern."""
        content = ["- *Term*: This is the definition"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 1

    def test_detects_asterisk_list_with_bold_term(self, definition_list_rule):
        """Test detection of * *Term*: pattern."""
        content = ["* *Term*: This is the definition"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 1

    def test_detects_multiple_patterns(self, definition_list_rule):
        """Test detection of multiple non-semantic patterns."""
        content = [
            "*First*: Definition one",
            "**Second**: Definition two",
            "- *Third*: Definition three",
        ]
        findings = definition_list_rule.check(content)

        assert len(findings) == 3

    def test_ignores_proper_definition_list(self, definition_list_rule):
        """Test that proper AsciiDoc definition lists are not flagged."""
        content = [
            "Term:: Definition here",
            "Another Term::",
            "  Definition on next line",
        ]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_inline_bold_in_sentence(self, definition_list_rule):
        """Test that inline bold with colon in middle of sentence is not flagged."""
        content = ["This sentence has *bold*: but it's not at the start"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_url_with_colon(self, definition_list_rule):
        """Test that URLs are not flagged."""
        content = ["Check out https://example.com for more info"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_time_format(self, definition_list_rule):
        """Test that time formats are not flagged."""
        content = ["The meeting starts at 10:30"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_inside_code_block(self, definition_list_rule):
        """Test that patterns inside code blocks are not flagged."""
        content = [
            "Some text",
            "----",
            "*Term*: This is inside a code block",
            "----",
            "More text",
        ]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_ignores_inside_literal_block(self, definition_list_rule):
        """Test that patterns inside literal blocks are not flagged."""
        content = [
            "....",
            "**Term**: Inside literal block",
            "....",
        ]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0

    def test_detects_outside_code_block(self, definition_list_rule):
        """Test that patterns outside code blocks are detected."""
        content = [
            "*Before*: Before code block",
            "----",
            "*Inside*: Inside code block",
            "----",
            "*After*: After code block",
        ]
        findings = definition_list_rule.check(content)

        # Should detect only the ones outside
        assert len(findings) == 2

    def test_message_suggests_definition_list_syntax(self, definition_list_rule):
        """Test that the message suggests using :: syntax."""
        content = ["*Term*: Definition"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 1
        assert (
            "::" in findings[0].message
            or "definition list" in findings[0].message.lower()
        )

    def test_ignores_asciidoc_attributes(self, definition_list_rule):
        """Test that AsciiDoc attributes are not flagged."""
        content = [":icons: font", ":toc: left"]
        findings = definition_list_rule.check(content)

        assert len(findings) == 0


class TestNonSemanticDefinitionListRuleMetadata:
    """Tests for FMT002 rule metadata."""

    def test_rule_id(self, definition_list_rule):
        """Test that rule has correct ID."""
        assert definition_list_rule.id == "FMT002"

    def test_rule_name(self, definition_list_rule):
        """Test that rule has a name."""
        assert definition_list_rule.name != ""

    def test_rule_description(self, definition_list_rule):
        """Test that rule has a description."""
        assert definition_list_rule.description != ""

    def test_rule_severity(self, definition_list_rule):
        """Test that rule has WARNING severity by default."""
        assert definition_list_rule.severity == Severity.WARNING


# =============================================================================
# FMT003: Counter Syntax in Title Detection Tests
# =============================================================================


@pytest.fixture
def counter_rule():
    """Create a CounterInTitleRule instance for testing."""
    return CounterInTitleRule()


class TestCounterInTitleDetection:
    """Tests for detecting counter syntax in section titles."""

    def test_detects_counter_in_level2_heading(self, counter_rule):
        """Test detection of {counter:name} in level 2 heading."""
        content = ["== Phase {counter:phase}"]
        findings = counter_rule.check(content)

        assert len(findings) == 1
        assert findings[0].rule_id == "FMT003"
        assert "counter" in findings[0].message.lower()

    def test_detects_counter_in_level3_heading(self, counter_rule):
        """Test detection of {counter:name} in level 3 heading."""
        content = ["=== Step {counter:step}: Setup"]
        findings = counter_rule.check(content)

        assert len(findings) == 1

    def test_detects_counter_in_level1_heading(self, counter_rule):
        """Test detection of {counter:name} in level 1 heading."""
        content = ["= Document {counter:doc}"]
        findings = counter_rule.check(content)

        assert len(findings) == 1

    def test_detects_counter_at_start_of_title(self, counter_rule):
        """Test detection of counter at start of title."""
        content = ["== {counter:section} Overview"]
        findings = counter_rule.check(content)

        assert len(findings) == 1

    def test_detects_multiple_counters_in_document(self, counter_rule):
        """Test detection of multiple counters in different headings."""
        content = [
            "== Phase {counter:phase}",
            "",
            "Some content",
            "",
            "=== Step {counter:step}",
            "",
            "== Phase {counter:phase}",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 3

    def test_detects_counter_with_format_specifier(self, counter_rule):
        """Test detection of counter with format specifier."""
        content = ["== Step {counter:step:%02d}: Setup"]
        findings = counter_rule.check(content)

        assert len(findings) == 1

    def test_detects_counter2_variant(self, counter_rule):
        """Test detection of {counter2:name} variant."""
        content = ["== Section {counter2:section}"]
        findings = counter_rule.check(content)

        assert len(findings) == 1

    def test_ignores_counter_in_regular_content(self, counter_rule):
        """Test that counters in regular content are not flagged."""
        content = [
            "== Regular Heading",
            "",
            "The current phase is {counter:phase}.",
            "Step {counter:step} is complete.",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 0

    def test_ignores_heading_without_counter(self, counter_rule):
        """Test that headings without counters are not flagged."""
        content = [
            "= Document Title",
            "== Section One",
            "=== Subsection",
            "== Section Two",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 0

    def test_ignores_counter_inside_code_block(self, counter_rule):
        """Test that counters inside code blocks are not flagged."""
        content = [
            "== Regular Heading",
            "",
            "----",
            "== Phase {counter:phase}",
            "----",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 0

    def test_ignores_counter_inside_literal_block(self, counter_rule):
        """Test that counters inside literal blocks are not flagged."""
        content = [
            "....",
            "== Step {counter:step}",
            "....",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 0

    def test_detects_outside_code_block(self, counter_rule):
        """Test that counters outside code blocks are detected."""
        content = [
            "== Before {counter:a}",
            "",
            "----",
            "== Inside {counter:b}",
            "----",
            "",
            "== After {counter:c}",
        ]
        findings = counter_rule.check(content)

        assert len(findings) == 2

    def test_message_suggests_review(self, counter_rule):
        """Test that the message suggests reviewing counter usage."""
        content = ["== Phase {counter:phase}"]
        findings = counter_rule.check(content)

        assert len(findings) == 1
        msg = findings[0].message.lower()
        assert "counter" in msg
        # Should suggest review or alternative
        assert "review" in msg or "consider" in msg or "suggest" in msg


class TestCounterInTitleRuleMetadata:
    """Tests for FMT003 rule metadata."""

    def test_rule_id(self, counter_rule):
        """Test that rule has correct ID."""
        assert counter_rule.id == "FMT003"

    def test_rule_name(self, counter_rule):
        """Test that rule has a name."""
        assert counter_rule.name != ""

    def test_rule_description(self, counter_rule):
        """Test that rule has a description."""
        assert counter_rule.description != ""

    def test_rule_severity(self, counter_rule):
        """Test that rule has WARNING severity by default."""
        assert counter_rule.severity == Severity.WARNING
