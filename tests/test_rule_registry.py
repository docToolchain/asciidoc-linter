# test_rule_registry.py - Tests for the rule registry
"""Tests for the rule registry functionality"""

import pytest
from asciidoc_linter.rules.base import Rule, RuleRegistry, Severity


class MockRuleOne(Rule):
    """First test rule"""

    id = "MockRuleOne"
    name = "Mock Rule One"
    description = "First mock rule"
    severity = Severity.WARNING


class MockRuleTwo(Rule):
    """Second test rule"""

    id = "MockRuleTwo"
    name = "Mock Rule Two"
    description = "Second mock rule"
    severity = Severity.ERROR


def test_rule_registry():
    """Test the rule registry functionality"""
    # Clear registry
    RuleRegistry._rules.clear()

    # Test registration
    RuleRegistry.register_rule(MockRuleOne)
    RuleRegistry.register_rule(MockRuleTwo)

    # Test getting a specific rule
    rule_class = RuleRegistry.get_rule("MockRuleOne")
    assert rule_class == MockRuleOne

    # Test getting all rules
    all_rules = RuleRegistry.get_all_rules()
    assert len(all_rules) == 2
    assert MockRuleOne in all_rules
    assert MockRuleTwo in all_rules

    # Test creating all rules
    rule_instances = RuleRegistry.create_all_rules()
    assert len(rule_instances) == 2
    assert isinstance(rule_instances[0], Rule)
    assert isinstance(rule_instances[1], Rule)

    # Test getting non-existent rule
    with pytest.raises(KeyError):
        RuleRegistry.get_rule("NonExistentRule")
