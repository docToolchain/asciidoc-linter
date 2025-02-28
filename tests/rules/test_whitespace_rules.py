# test_whitespace_rules.py - Tests for the whitespace rules

import pytest
from asciidoc_linter.rules.whitespace_rules import WhitespaceRule
from asciidoc_linter.rules.base import Finding, Severity

def test_section_title_detection():
    """Test the detection of valid and invalid section titles"""
    rule = WhitespaceRule()
    
    # Valid section titles
    assert rule.is_section_title("= Document Title")
    assert rule.is_section_title("== Section Title")
    assert rule.is_section_title("=== Subsection Title")
    
    # Invalid section titles
    assert not rule.is_section_title("")  # Empty line
    assert not rule.is_section_title("=")  # Just equals
    assert not rule.is_section_title("==")  # Just equals
    assert not rule.is_section_title("=No Space")  # No space after equals
    assert not rule.is_section_title("= ")  # No content after space

def test_document_title():
    """Test handling of document title (level 1 heading)"""
    rule = WhitespaceRule()
    document = [
        "= Document Title",
        "== First Section",
        "",
        "Content here."
    ]
    
    findings = rule.check(document)
    
    # Should not require blank line before document title
    assert not any(f.message == "Section title should be preceded by a blank line" 
                  and f.position.line == 1 for f in findings)
    
    # Should require blank line after document title
    assert any(f.message == "Section title should be followed by a blank line" 
              and f.position.line == 1 for f in findings)

def test_consecutive_sections():
    """Test handling of consecutive section titles"""
    rule = WhitespaceRule()
    document = [
        "= Document Title",
        "",
        "== First Section",
        "== Second Section",
        "",
        "Content here."
    ]
    
    findings = rule.check(document)
    
    # Should not require blank line between consecutive sections
    assert not any(f.message == "Section title should be preceded by a blank line" 
                  and f.position.line == 4 for f in findings)

def test_section_with_content():
    """Test sections with content before and after"""
    rule = WhitespaceRule()
    document = [
        "= Document Title",
        "",
        "Some content.",
        "== Section Title",
        "More content."
    ]
    
    findings = rule.check(document)
    
    # Should require blank line before section when preceded by content
    assert any(f.message == "Section title should be preceded by a blank line" 
              and f.position.line == 4 for f in findings)
    
    # Should require blank line after section when followed by content
    assert any(f.message == "Section title should be followed by a blank line" 
              and f.position.line == 4 for f in findings)

def test_disabled_rule():
    """Test that rule can be disabled"""
    rule = WhitespaceRule()
    rule.enabled = False
    
    document = [
        "= Document Title",
        "== Section Title",  # No blank lines, should normally trigger findings
        "Content here."
    ]
    
    findings = rule.check(document)
    assert len(findings) == 0

def test_severity_configuration():
    """Test that severity can be configured"""
    rule = WhitespaceRule()
    rule.severity = Severity.ERROR
    
    document = [
        "= Document Title",
        "Content here."  # No blank line, should trigger ERROR
    ]
    
    findings = rule.check(document)
    assert any(f.severity == Severity.ERROR for f in findings)

def test_trailing_whitespace():
    """Test detection of trailing whitespace"""
    rule = WhitespaceRule()
    document = [
        "= Document Title",
        "",
        "Line with trailing space  ",
        "Line with trailing tab\t",
        "Normal line"
    ]
    
    findings = rule.check(document)
    
    # Should detect both types of trailing whitespace
    assert any(f.message == "Line contains trailing whitespace" 
              and f.position.line == 3 for f in findings)
    assert any(f.message == "Line contains trailing whitespace" 
              and f.position.line == 4 for f in findings)

def test_list_marker_spacing():
    """Test spacing after list markers"""
    rule = WhitespaceRule()
    document = [
        "* Correct list item",
        "*Wrong list item",
        "- Correct list item",
        "-Wrong list item"
    ]
    
    findings = rule.check(document)
    
    # Should detect missing spaces after markers
    assert any(f.message == "Missing space after the marker '*'" 
              and f.position.line == 2 for f in findings)
    assert any(f.message == "Missing space after the marker '-'" 
              and f.position.line == 4 for f in findings)

def test_multiple_consecutive_empty_lines():
    """Test detection of too many consecutive empty lines"""
    rule = WhitespaceRule()
    document = [
        "= Document Title",
        "",
        "",
        "",
        "Content here."
    ]
    
    findings = rule.check(document)
    
    # Should detect too many consecutive empty lines
    assert any(f.message == "Too many consecutive empty lines" 
              and f.position.line == 4 for f in findings)