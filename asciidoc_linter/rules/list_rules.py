# list_rules.py - Rules for checking AsciiDoc lists
"""
Rules for detecting broken AsciiDoc lists.
"""

import re
from typing import List, Union
from .base import Rule, Finding, Severity, Position
from ..blocks import find_code_block_content_lines

# Unordered (*, -), ordered (., 1.) and checklist items: marker plus space
LIST_ITEM_PATTERN = re.compile(r"^\s*(\*{1,5}|-|\.{1,5}|\d+\.)\s+\S")

# Definition list term: "Term::" or "Term;;" (optionally followed by text).
# Mirrors Asciidoctor: the term ends with a character other than space or colon.
DLIST_TERM_PATTERN = re.compile(r"^(?!//[^/])\s*(\S|\S.*[^\s:])(:{2,4}|;;)(\s|$)")

# Table delimiters: |=== (PSV), ,=== (CSV), :=== (DSV), !=== (nested)
TABLE_DELIMITER_PATTERN = re.compile(r"^[|,:!]={3,}\s*$")

# Delimiters of blocks whose content forms its own paragraphs
BLOCK_DELIMITER_PATTERN = re.compile(
    r"^(-{4,}|={4,}|\*{4,}|\.{4,}|_{4,}|\+{4,}|/{4,}|--|[|,:!]===)\s*$"
)


class ListAfterParagraphRule(Rule):
    """
    LIST001: Detect lists that directly follow a paragraph line.

    AsciiDoc needs an empty line between a paragraph and a list (including
    description lists). Without it, the list items are rendered as part of
    the paragraph text:

        Required tools:
        Clang++
        * make
        * zip
    """

    id = "LIST001"
    name = "List After Paragraph"
    description = "Detects lists that are not separated from a preceding paragraph"
    severity = Severity.WARNING

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        """Check the entire document for lists glued to a paragraph."""
        lines = [self._get_line_content(line) for line in document]
        skipped = find_code_block_content_lines(lines)
        findings = []

        # Kind of the current run of non-blank lines: None (no run yet),
        # "paragraph" or "list" (runs starting with a list item or term)
        run = None
        in_table = False
        for line_number, line in enumerate(lines):
            stripped = line.strip()
            if line_number in skipped:
                run = None
                continue
            if TABLE_DELIMITER_PATTERN.match(stripped):
                in_table = not in_table
                run = None
                continue
            if in_table:
                continue
            if not stripped or BLOCK_DELIMITER_PATTERN.match(stripped):
                run = None
                continue
            if run is None:
                if self._is_block_prefix(stripped):
                    continue
                run = "list" if self._starts_list(line) else "paragraph"
                continue
            # Inside a paragraph, titles, attribute lines and comments are
            # paragraph text too, so they don't end the paragraph
            if run == "paragraph" and self._starts_list(line):
                findings.append(
                    Finding(
                        rule_id=self.id,
                        position=Position(line=line_number + 1),
                        message=(
                            "List directly follows a paragraph line and "
                            "will be rendered as paragraph text; "
                            "add an empty line before the list"
                        ),
                        severity=self.severity,
                        context=line,
                    )
                )
                # Report each broken list once
                run = "list"
        return findings

    @staticmethod
    def _starts_list(line: str) -> bool:
        return bool(LIST_ITEM_PATTERN.match(line) or DLIST_TERM_PATTERN.match(line))

    @staticmethod
    def _is_block_prefix(stripped: str) -> bool:
        """Lines that precede a block without being paragraph text"""
        is_attribute_list = stripped.startswith("[") and stripped.endswith("]")
        is_title = len(stripped) > 1 and stripped[0] == "." and stripped[1] not in ". "
        is_heading = re.match(r"^=+\s+\S", stripped) is not None
        is_comment = stripped.startswith("//")
        is_attribute_entry = re.match(r"^:!?[\w-]+!?:", stripped) is not None
        return (
            is_attribute_list
            or is_title
            or is_heading
            or is_comment
            or is_attribute_entry
        )

    @staticmethod
    def _get_line_content(line: Union[str, object]) -> str:
        if hasattr(line, "content"):
            return line.content
        return str(line)
