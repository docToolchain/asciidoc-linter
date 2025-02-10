# heading_rules.py - Implementation of heading rules
"""
This module contains rules for checking AsciiDoc heading structure and format.
"""

from typing import List, Optional, Tuple, Dict, Any, Union
from .base import Rule, Finding, Severity, Position
import re


class HeadingFormatRule(Rule):
    """
    HEAD002: Check heading format.
    Ensures that headings follow AsciiDoc conventions:
    - Space after = characters
    - Proper capitalization
    """

    def __init__(self):
        super().__init__()
        self.id = "HEAD002"
        self.heading_pattern = re.compile(r"^(=+)(\s*)(.*)$")

    @property
    def description(self) -> str:
        return "Ensures proper heading format (spacing and capitalization)"

    def check_line(self, line: str, line_num: int) -> List[Finding]:
        findings = []
        match = self.heading_pattern.match(line)

        if match:
            equals, space, text = match.groups()
            level = len(equals)

            # Check for space after = characters
            if not space:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        message=f"Missing space after {'=' * level}",
                        severity=Severity.ERROR,
                        position=Position(line=line_num + 1),
                        context=line,
                    )
                )

            # Check if heading starts with lowercase (only if we have text)
            if text:
                # Split into words and check first word
                words = text.strip().split()
                if words and words[0][0].islower():
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            message="Heading should start with uppercase letter",
                            severity=Severity.WARNING,
                            position=Position(line=line_num + 1),
                            context=line,
                        )
                    )

        return findings

    def check(self, document: Union[Dict[str, Any], List[Any]]) -> List[Finding]:
        findings = []

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        for line_num, line in enumerate(lines):
            if isinstance(line, str):
                findings.extend(self.check_line(line, line_num))

        return findings


class HeadingHierarchyRule(Rule):
    """
    HEAD001: Check for proper heading incrementation.
    Ensures that heading levels are not skipped (e.g., h1 -> h3).
    """

    def __init__(self):
        super().__init__()
        self.id = "HEAD001"
        self.heading_pattern = re.compile(r"^(=+)\s")

    @property
    def description(self) -> str:
        return "Ensures proper heading level incrementation (no skipped levels)"

    def get_heading_levels(self, document: List[str]) -> List[Tuple[int, int, str]]:
        """Extract heading levels with line numbers."""
        headings = []
        for line_num, line in enumerate(document):
            if isinstance(line, str):
                match = self.heading_pattern.match(line)
                if match:
                    level = len(match.group(1))
                    headings.append((level, line_num, line))
        return headings

    def check(self, document: Union[Dict[str, Any], List[Any]]) -> List[Finding]:
        findings = []

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        headings = self.get_heading_levels(lines)
        if not headings:
            return findings

        current_level = headings[0][0]
        for level, line_num, line in headings[1:]:
            if level > current_level + 1:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        message=f"Heading level skipped: found h{level} after h{current_level}",
                        severity=Severity.ERROR,
                        position=Position(line=line_num + 1),
                        context=line,
                    )
                )
            current_level = level

        return findings


class MultipleTopLevelHeadingsRule(Rule):
    """
    HEAD003: Check for multiple top-level headings.
    Ensures that a document has only one top-level (=) heading.
    """

    def __init__(self):
        super().__init__()
        self.id = "HEAD003"
        self.heading_pattern = re.compile(r"^=\s")

    @property
    def description(self) -> str:
        return "Ensures document has only one top-level heading"

    def check(self, document: Union[Dict[str, Any], List[Any]]) -> List[Finding]:
        findings = []
        first_top_level: Optional[Tuple[int, str]] = None

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        for line_num, line in enumerate(lines):
            if isinstance(line, str) and self.heading_pattern.match(line):
                if first_top_level is None:
                    first_top_level = (line_num + 1, line.strip())
                else:
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            message=f"Multiple top-level headings found. First heading at line {first_top_level[0]}: '{first_top_level[1]}'",
                            severity=Severity.ERROR,
                            position=Position(line=line_num + 1),
                            context=line,
                        )
                    )

        return findings
