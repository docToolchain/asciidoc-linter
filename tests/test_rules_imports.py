# test_rules_imports.py - Tests for rules module imports
"""Tests to verify that the rules module correctly exports all required classes"""

from asciidoc_linter import rules
from asciidoc_linter.rules.base import (
    Severity as BaseSeverity,
    Position as BasePosition,
    Finding as BaseFinding,
    Rule as BaseRule,
    RuleRegistry as BaseRuleRegistry,
)


def test_severity_import():
    """Test that Severity is correctly imported"""
    assert rules.Severity is BaseSeverity
    assert hasattr(rules.Severity, "ERROR")
    assert hasattr(rules.Severity, "WARNING")
    assert hasattr(rules.Severity, "INFO")


def test_position_import():
    """Test that Position is correctly imported"""
    assert rules.Position is BasePosition
    # Create a Position object to ensure it works
    pos = rules.Position(1, 2)
    assert pos.line == 1
    assert pos.column == 2


def test_finding_import():
    """Test that Finding is correctly imported"""
    assert rules.Finding is BaseFinding
    # Create a Finding object to ensure it works
    finding = rules.Finding(
        rule_id="test",
        message="test message",
        position=rules.Position(1),
        severity=rules.Severity.WARNING,
    )
    assert finding.rule_id == "test"
    assert finding.message == "test message"


def test_rule_import():
    """Test that Rule is correctly imported"""
    assert rules.Rule is BaseRule
    # Verify it's the abstract base class
    assert hasattr(rules.Rule, "check")


def test_rule_registry_import():
    """Test that RuleRegistry is correctly imported"""
    assert rules.RuleRegistry is BaseRuleRegistry
    # Verify basic functionality
    assert hasattr(rules.RuleRegistry, "register_rule")
    assert hasattr(rules.RuleRegistry, "get_rule")


def test_all_variable():
    """Test that __all__ contains all expected names"""
    expected = {"Severity", "Position", "Finding", "Rule", "RuleRegistry"}
    assert set(rules.__all__) == expected
