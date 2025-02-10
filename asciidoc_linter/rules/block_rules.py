# block_rules.py - Rules for checking AsciiDoc blocks

from typing import List, Dict, Any, Union
from .base import Rule, Finding, Severity, Position


class UnterminatedBlockRule(Rule):
    """Rule to check for unterminated blocks in AsciiDoc files."""

    def __init__(self):
        super().__init__()
        self.id = "BLOCK001"
        self.block_markers = {
            "----": "listing block",
            "====": "example block",
            "****": "sidebar block",
            "....": "literal block",
            "____": "quote block",
            "|===": "table block",
            "////": "comment block",
            "++++": "passthrough block",
        }
        self.open_blocks = {}

    @property
    def description(self) -> str:
        return "Checks for blocks that are not properly terminated"

    def check_line(
        self, line: str, line_num: int, document: List[str]
    ) -> List[Finding]:
        findings = []
        stripped_line = line.strip()

        if stripped_line in self.block_markers:
            if stripped_line in self.open_blocks:
                # This is a closing delimiter
                del self.open_blocks[stripped_line]
            else:
                # This is an opening delimiter
                self.open_blocks[stripped_line] = line_num

                # Look ahead for matching end delimiter
                is_terminated = False
                for i, next_line in enumerate(
                    document[line_num + 1 :], start=line_num + 1
                ):
                    if next_line.strip() == stripped_line:
                        is_terminated = True
                        break

                if not is_terminated:
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_num + 1),
                            message=f"Unterminated {self.block_markers[stripped_line]} starting",
                            severity=Severity.ERROR,
                            context=line,
                        )
                    )

        return findings

    def check(self, document: Union[Dict[str, Any], List[Any]]) -> List[Finding]:
        findings = []
        self.open_blocks = {}  # Reset open blocks

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        for line_num, line in enumerate(lines):
            if isinstance(line, str):
                findings.extend(self.check_line(line, line_num, lines))

        return findings


class BlockSpacingRule(Rule):
    """Rule to check for proper spacing around blocks."""

    def __init__(self):
        super().__init__()
        self.id = "BLOCK002"
        self.block_markers = {
            "----",
            "====",
            "****",
            "....",
            "____",
            "|===",
            "////",
            "++++",
        }
        self.open_blocks = {}

    @property
    def description(self) -> str:
        return "Checks for proper blank lines around blocks"

    def check_line(
        self, line: str, line_num: int, document: List[str]
    ) -> List[Finding]:
        findings = []
        stripped_line = line.strip()

        if stripped_line in self.block_markers:
            if stripped_line in self.open_blocks:
                # This is a closing delimiter
                if line_num + 1 < len(document):
                    next_line = document[line_num + 1].strip()
                    if next_line and not next_line.startswith("="):
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_num + 2),
                                message="Block should be followed by a blank line",
                                severity=Severity.WARNING,
                                context=document[line_num + 1],
                            )
                        )
                del self.open_blocks[stripped_line]
            else:
                # This is an opening delimiter
                if line_num > 0:
                    prev_line = document[line_num - 1].strip()
                    if prev_line and not prev_line.startswith("="):
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_num + 1),
                                message="Block should be preceded by a blank line",
                                severity=Severity.WARNING,
                                context=line,
                            )
                        )
                self.open_blocks[stripped_line] = line_num

        return findings

    def check(self, document: Union[Dict[str, Any], List[Any]]) -> List[Finding]:
        findings = []
        self.open_blocks = {}  # Reset open blocks

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        for line_num, line in enumerate(lines):
            if isinstance(line, str):
                findings.extend(self.check_line(line, line_num, lines))

        return findings
