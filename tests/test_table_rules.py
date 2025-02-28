# test_table_rules.py - Integration tests for table rules

import pytest
from asciidoc_linter.rules.table_rules import TableFormatRule
from asciidoc_linter.rules.base import Finding, Severity

def test_table_format_integration():
    """Integration test for table format rule"""
    rule = TableFormatRule()
    
    # Test a complex document with multiple tables
    document = [
        "= Document Title",
        "",
        "== Section with Tables",
        "",
        "|===",
        "| Header 1 | Header 2",
        "| Data 1.1 | Data 1.2",
        "| Data 2.1 | Data 2.2",
        "|===",
        "",
        "Some text between tables",
        "",
        "|===",
        "| Single | Column",
        "| Table | Extra Column",  # Inconsistent
        "|===",
    ]
    
    findings = rule.check(document)
    
    # Should find inconsistent columns in second table
    assert len(findings) == 1
    assert "Inconsistent column count" in findings[0].message
    assert findings[0].position.line == 15  # Line with extra column

def test_table_format_with_attributes():
    """Test table format rule with table attributes"""
    rule = TableFormatRule()
    
    document = [
        "[cols=2*]",  # Table attribute
        "|===",
        "| Header 1 | Header 2",
        "| Data 1.1 | Data 1.2",
        "|===",
        "",
        "[cols=3*]",  # Table attribute
        "|===",
        "| Header 1 | Header 2 | Header 3",
        "| Data 1.1 | Data 1.2",  # Missing column
        "|===",
    ]
    
    findings = rule.check(document)
    
    # Should find inconsistent columns in second table
    assert len(findings) == 1
    assert "Inconsistent column count" in findings[0].message
    assert findings[0].position.line == 10  # Line with missing column

def test_table_format_with_complex_content():
    """Test table format rule with complex cell content"""
    rule = TableFormatRule()
    
    document = [
        "|===",
        "| Cell with *bold* | Cell with _italic_",
        "| Cell with `code` | Cell with [red]#red text#",
        "|===",
        "",
        "|===",
        "| Cell with list | Another cell",
        "* Item 1 | Missing cell",  # Not a valid table row
        "* Item 2",
        "|===",
    ]
    
    findings = rule.check(document)
    
    # Should handle complex content correctly
    assert len(findings) > 0  # Should find issues in second table