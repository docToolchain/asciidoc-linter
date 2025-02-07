# linter.py - Main linter module
"""
Main linter module that processes AsciiDoc files and applies rules
"""

from typing import List
from pathlib import Path

from .rules.base import Finding, Severity
from .rules.heading_rules import (
    HeadingFormatRule,
    HeadingHierarchyRule,
    MultipleTopLevelHeadingsRule,
)
from .rules.block_rules import UnterminatedBlockRule, BlockSpacingRule
from .rules.whitespace_rules import WhitespaceRule
from .rules.image_rules import ImageAttributesRule
from .parser import AsciiDocParser
from .reporter import LintReport


class AsciiDocLinter:
    """Main linter class that coordinates parsing and rule checking"""

    def __init__(self):
        self.parser = AsciiDocParser()
        self.rules = [
            HeadingFormatRule(),
            HeadingHierarchyRule(),
            MultipleTopLevelHeadingsRule(),
            UnterminatedBlockRule(),
            BlockSpacingRule(),
            WhitespaceRule(),
            ImageAttributesRule(),
        ]

    def lint(self, file_paths: List[str]) -> LintReport:
        """
        Lint content and return formatted output using the current reporter

        This is the main entry point used by the CLI
        """
        all_findings = []
        for file_path in file_paths:
            all_findings.extend(self.lint_file(file_path))
        return LintReport(all_findings)

    def lint_file(self, file_path: Path) -> List[Finding]:
        """Lint a single file and return a report"""
        try:
            return [
                finding.set_file(str(file_path))
                for finding in self.lint_string(Path(file_path).read_text())
            ]
        except Exception as e:
            return [
                Finding(
                    message=f"Error linting file: {e}",
                    severity=Severity.ERROR,
                    file=str(file_path),
                )
            ]

    def lint_string(self, content: str) -> List[Finding]:
        """Lint a string and return a report"""
        document = self.parser.parse(content)
        findings = []

        for rule in self.rules:
            rule_findings = rule.check(document)
            findings.extend(rule_findings)

        return findings
