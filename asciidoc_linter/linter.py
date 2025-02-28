# linter.py - Main linter module that processes AsciiDoc files and applies rules

from typing import List, Optional
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
from .rules.table_rules import TableFormatRule
from .parser import AsciiDocParser
from .reporter import LintReport
from .config import LinterConfig

class AsciiDocLinter:
    """Main linter class that coordinates parsing and rule checking"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the linter with optional configuration
        
        Args:
            config_file: Optional path to a configuration file
        """
        self.parser = AsciiDocParser()
        self.config = LinterConfig(config_file)
        self.rules = [
            HeadingFormatRule(),
            HeadingHierarchyRule(),
            MultipleTopLevelHeadingsRule(),
            UnterminatedBlockRule(),
            BlockSpacingRule(),
            WhitespaceRule(),
            ImageAttributesRule(),
            TableFormatRule(),
        ]
        
        # Configure rules based on config
        self._configure_rules()

    def _configure_rules(self):
        """Configure all rules based on current configuration"""
        for rule in self.rules:
            if rule.id:  # Only configure rules with an ID
                rule.enabled = self.config.is_rule_enabled(rule.id)
                rule.severity = self.config.get_severity_enum(rule.id)

    def lint(self, file_paths: List[str]) -> LintReport:
        """
        Lint content and return formatted output using the current reporter
        
        Args:
            file_paths: List of paths to files to lint
            
        Returns:
            LintReport containing all findings
        """
        all_findings = []
        for file_path in file_paths:
            all_findings.extend(self.lint_file(file_path))
        return LintReport(all_findings)

    def lint_file(self, file_path: Path) -> List[Finding]:
        """
        Lint a single file and return a report
        
        Args:
            file_path: Path to the file to lint
            
        Returns:
            List of findings for the file
        """
        try:
            content = Path(file_path).read_text()
            findings = self.lint_string(content)
            return [finding.set_file(str(file_path)) for finding in findings]
        except Exception as e:
            return [
                Finding(
                    message=f"Error linting file: {e}",
                    severity=Severity.ERROR,
                    file=str(file_path),
                )
            ]

    def lint_string(self, content: str) -> List[Finding]:
        """
        Lint a string and return a report
        
        Args:
            content: String content to lint
            
        Returns:
            List of findings for the content
        """
        document = self.parser.parse(content)
        findings = []

        for rule in self.rules:
            if rule.enabled:
                rule_findings = rule.check(document)
                findings.extend(rule_findings)

        return findings