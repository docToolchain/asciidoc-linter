# linter.py - Main linter module
"""
Main linter module that processes AsciiDoc files and applies rules
"""

from typing import List
from pathlib import Path
import yaml

from .rules.base import Finding, Severity
from .rules.heading_rules import (
    HeadingFormatRule,
    HeadingHierarchyRule,
    MultipleTopLevelHeadingsRule,
)
from .rules.block_rules import UnterminatedBlockRule, BlockSpacingRule
from .rules.whitespace_rules import WhitespaceRule
from .rules.image_rules import ImageAttributesRule
from .rules.format_rules import (
    MarkdownSyntaxRule,
    ExplicitNumberedListRule,
    NonSemanticDefinitionListRule,
    CounterInTitleRule,
)
from .rules.markdown_table_rules import MarkdownTableRule
from .parser import AsciiDocParser
from .reporter import LintReport


class ConfigError(Exception):
    """Raised when the configuration file cannot be read, parsed or applied"""


class AsciiDocLinter:
    """Main linter class that coordinates parsing and rule checking"""

    def __init__(self, config_path: str = None):
        self.parser = AsciiDocParser()
        self.rules = [
            HeadingFormatRule(),
            HeadingHierarchyRule(),
            MultipleTopLevelHeadingsRule(),
            UnterminatedBlockRule(),
            BlockSpacingRule(),
            WhitespaceRule(),
            ImageAttributesRule(),
            MarkdownSyntaxRule(),
            ExplicitNumberedListRule(),
            NonSemanticDefinitionListRule(),
            CounterInTitleRule(),
            MarkdownTableRule(),
        ]
        self.config_path = config_path

    def lint(self, file_paths: List[str]) -> LintReport:
        """
        Lint content and return formatted output using the current reporter

        This is the main entry point used by the CLI
        """
        if self.config_path:
            self.load_config(self.config_path)

        all_findings = []
        for file_path in file_paths:
            all_findings.extend(self.lint_file(file_path))
        return LintReport(all_findings)

    def load_config(self, config_path: str) -> None:
        """Load configuration from a YAML file

        Raises ConfigError if the file cannot be read, parsed or applied.
        An empty file or a file without a ``rules`` key is valid.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                config = yaml.safe_load(config_file)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
            raise ConfigError(f"{config_path}: {e}") from e
        try:
            self.apply_config(config)
        except ConfigError as e:
            raise ConfigError(f"{config_path}: {e}") from e

    def apply_config(self, config: dict) -> None:
        """Apply configuration to the linter

        Raises ConfigError if the configuration has an invalid structure.
        """
        if config is None:
            return
        if not isinstance(config, dict):
            raise ConfigError("top level must be a mapping")
        rules_config = config.get("rules")
        if rules_config is None:
            rules_config = {}
        if not isinstance(rules_config, dict):
            raise ConfigError("'rules' must be a mapping of rule IDs")
        for rule in list(self.rules):
            rule_config = rules_config.get(rule.id)
            if rule_config is None:
                rule_config = {}
            if not isinstance(rule_config, dict):
                raise ConfigError(f"configuration of rule {rule.id} must be a mapping")
            # Validate the severity even for disabled rules, so a typo does
            # not go unnoticed until the rule is enabled again
            try:
                severity = Severity(rule_config.get("severity", rule.severity))
            except ValueError as e:
                raise ConfigError(
                    f"invalid severity for rule {rule.id}: "
                    f"{rule_config.get('severity')!r} "
                    "(expected error, warning or info)"
                ) from e
            if not rule_config.get("enabled", True):
                self.rules.remove(rule)
            else:
                rule.severity = severity

    def lint_file(self, file_path: Path) -> List[Finding]:
        """Lint a single file and return a report"""
        try:
            return [
                finding.set_file(str(file_path))
                for finding in self.lint_string(
                    Path(file_path).read_text(encoding="utf-8")
                )
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
        # The parsed elements only carry headers; rules work on raw lines
        self.parser.parse(content)
        raw_lines = content.splitlines()
        findings = []

        for rule in self.rules:
            findings.extend(rule.check(raw_lines))

        return findings
