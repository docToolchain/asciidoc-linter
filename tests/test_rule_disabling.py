# test_rule_disabling.py - Tests that all rules can be disabled via configuration

import pytest
from pathlib import Path
from asciidoc_linter.linter import AsciiDocLinter
from asciidoc_linter.rules.heading_rules import (
    HeadingFormatRule,
    HeadingHierarchyRule,
    MultipleTopLevelHeadingsRule,
)
from asciidoc_linter.rules.block_rules import UnterminatedBlockRule, BlockSpacingRule
from asciidoc_linter.rules.whitespace_rules import WhitespaceRule
from asciidoc_linter.rules.image_rules import ImageAttributesRule
from asciidoc_linter.rules.table_rules import TableFormatRule

def test_all_rules_can_be_disabled(tmp_path):
    """Test that all rules can be disabled via configuration"""
    # Create a config file that disables all rules
    config_content = """rules:
  WS001:
    enabled: false
  HEAD001:
    enabled: false
  HEAD002:
    enabled: false
  HEAD003:
    enabled: false
  BLOCK001:
    enabled: false
  BLOCK002:
    enabled: false
  IMG001:
    enabled: false
  TABLE001:
    enabled: false
"""
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(config_content)
    
    # Create a document that would normally trigger all rules
    test_content = """= Document Title
== Section without blank line
=== Invalid Section Level
image::missing.png[]
|===
| Invalid | Table
| Format
|===
"""
    
    test_file = tmp_path / "test.adoc"
    test_file.write_text(test_content)
    
    # Initialize linter with config
    linter = AsciiDocLinter(config_file)
    
    # Lint the file
    report = linter.lint([str(test_file)])
    
    # Should have no findings since all rules are disabled
    assert len(report.findings) == 0

def test_individual_rules_can_be_disabled(tmp_path):
    """Test that individual rules can be disabled while others remain active"""
    # Create a config file that disables only some rules
    config_content = """rules:
  WS001:
    enabled: false
  HEAD001:
    enabled: true
  HEAD002:
    enabled: false
"""
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(config_content)
    
    # Create a document that would trigger multiple rules
    test_content = """=Document Title
== section without proper capitalization
"""
    
    test_file = tmp_path / "test.adoc"
    test_file.write_text(test_content)
    
    # Initialize linter with config
    linter = AsciiDocLinter(config_file)
    
    # Lint the file
    report = linter.lint([str(test_file)])
    
    # Check that only enabled rules produced findings
    findings_by_rule = {f.rule_id: f for f in report.findings}
    assert "WS001" not in findings_by_rule  # Should be disabled
    assert "HEAD001" in findings_by_rule    # Should be enabled (format issues)
    assert "HEAD002" not in findings_by_rule  # Should be disabled

def test_rule_classes_respect_enabled_flag():
    """Test that all rule classes respect their enabled flag"""
    test_document = [
        "= Document Title",
        "== Section without blank line",
        "=== Invalid Section Level",
        "image::missing.png[]",
        "|===",
        "| Invalid | Table",
        "| Format",
        "|===",
    ]
    
    # Test each rule class
    rule_classes = [
        HeadingFormatRule,
        HeadingHierarchyRule,
        MultipleTopLevelHeadingsRule,
        UnterminatedBlockRule,
        BlockSpacingRule,
        WhitespaceRule,
        ImageAttributesRule,
        TableFormatRule,
    ]
    
    for rule_class in rule_classes:
        # Create an instance and disable it
        rule = rule_class()
        rule.enabled = False
        
        # Check the document
        findings = rule.check(test_document)
        
        # Should have no findings since rule is disabled
        assert len(findings) == 0, f"Rule {rule.id} produced findings when disabled"