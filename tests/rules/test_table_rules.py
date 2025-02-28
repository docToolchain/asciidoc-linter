# test_table_rules.py - Tests for table rules

import pytest
from asciidoc_linter.rules.table_rules import TableFormatRule
from asciidoc_linter.rules.base import Finding, Severity

def test_table_format_rule():
    """Test that table format rule catches basic formatting issues"""
    rule = TableFormatRule()
    
    # Test unterminated table
    document = [
        "|===",
        "| Column 1 | Column 2",
        "| Data 1 | Data 2",
    ]
    findings = rule.check(document)
    assert any(f.message == "Unterminated table" for f in findings)
    
    # Test inconsistent column count
    document = [
        "|===",
        "| Column 1 | Column 2",
        "| Data 1 | Data 2 | Extra",
        "|===",
    ]
    findings = rule.check(document)
    assert any("Inconsistent column count" in f.message for f in findings)
    
    # Test valid table
    document = [
        "|===",
        "| Column 1 | Column 2",
        "| Data 1 | Data 2",
        "|===",
    ]
    findings = rule.check(document)
    assert len(findings) == 0

def test_table_format_rule_disabled():
    """Test that disabled table format rule produces no findings"""
    rule = TableFormatRule()
    rule.enabled = False
    
    document = [
        "|===",
        "| Column 1 | Column 2",
        "| Data 1 | Data 2 | Extra",  # Would normally trigger finding
    ]
    findings = rule.check(document)
    assert len(findings) == 0

def test_table_format_rule_severity():
    """Test that table format rule respects severity setting"""
    rule = TableFormatRule()
    rule.severity = Severity.ERROR
    
    document = [
        "|===",
        "| Column 1 | Column 2",
        "| Data 1 | Data 2 | Extra",  # Inconsistent columns
        "|===",
    ]
    findings = rule.check(document)
    assert all(f.severity == Severity.ERROR for f in findings)