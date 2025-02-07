# test_linter.py - Tests for the main linter module
"""
Tests for the main linter module (linter.py)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from asciidoc_linter.linter import AsciiDocLinter
from asciidoc_linter.parser import AsciiDocParser
from asciidoc_linter.reporter import LintReport
from asciidoc_linter.rules.base import Finding, Severity

# Fixtures


@pytest.fixture
def mock_parser():
    """Create a mock parser that returns a simple document structure"""
    parser = Mock(spec=AsciiDocParser)
    parser.parse.return_value = {"type": "document", "content": []}
    return parser


@pytest.fixture
def mock_rule():
    """Create a mock rule that can be configured to return specific errors"""
    rule = Mock()
    rule.check.return_value = []  # By default, return no errors
    return rule


@pytest.fixture
def sample_asciidoc():
    """Return a sample AsciiDoc string for testing"""
    return """= Title

== Section 1

Some content.

== Section 2

More content.
"""


# Tests for initialization


def test_linter_initialization():
    """Test that the linter initializes with correct default rules"""
    linter = AsciiDocLinter()
    assert len(linter.rules) == 7  # Verify number of default rules
    assert hasattr(linter, "parser")  # Verify parser is initialized


# Tests for lint_string method


def test_lint_string_no_errors(mock_parser, mock_rule):
    """Test linting a string with no errors"""
    with patch("asciidoc_linter.linter.AsciiDocParser", return_value=mock_parser):
        linter = AsciiDocLinter()
        linter.rules = [mock_rule]

        findings = linter.lint_string("Some content")

        assert len(findings) == 0
        mock_parser.parse.assert_called_once_with("Some content")
        mock_rule.check.assert_called_once()


def test_lint_string_with_errors(mock_parser, mock_rule):
    """Test linting a string that contains errors"""
    mock_rule.check.return_value = [
        Finding(message="Test error", severity=Severity.ERROR)
    ]

    with patch("asciidoc_linter.linter.AsciiDocParser", return_value=mock_parser):
        linter = AsciiDocLinter()
        linter.rules = [mock_rule]

        findings = linter.lint_string("Some content")

        assert len(findings) == 1
        assert findings[0].message == "Test error"
        assert findings[0].severity == Severity.ERROR


def test_lint_string_multiple_rules(mock_parser):
    """Test that all rules are applied when linting a string"""
    rule1 = Mock()
    rule1.check.return_value = [Finding(message="Error 1", severity=Severity.ERROR)]
    rule2 = Mock()
    rule2.check.return_value = [Finding(message="Error 2", severity=Severity.ERROR)]

    with patch("asciidoc_linter.linter.AsciiDocParser", return_value=mock_parser):
        linter = AsciiDocLinter()
        linter.rules = [rule1, rule2]

        findings = linter.lint_string("Some content")

        assert len(findings) == 2
        assert rule1.check.called
        assert rule2.check.called


# Tests for lint_file method


def test_lint_file_success(tmp_path, sample_asciidoc):
    """Test linting a file that exists and is readable"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text(sample_asciidoc)

    linter = AsciiDocLinter()
    findings = linter.lint_file(test_file)

    assert isinstance(findings, list)
    # Note: actual number of errors depends on the rules


def test_lint_file_not_found():
    """Test linting a file that doesn't exist"""
    non_existent_file = Path("non_existent.adoc")

    linter = AsciiDocLinter()
    findings = linter.lint_file(non_existent_file)

    assert len(findings) == 1
    assert "No such file or directory" in findings[0].message


def test_lint_file_with_source_tracking(tmp_path, sample_asciidoc, mock_rule):
    """Test that file source is correctly tracked in errors"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text(sample_asciidoc)

    mock_rule.check.return_value = [
        Finding(message="Test error", severity=Severity.ERROR)
    ]

    linter = AsciiDocLinter()
    linter.rules = [mock_rule]

    findings = linter.lint_file(test_file)

    assert len(findings) == 1
    assert str(test_file) == findings[0].file


# Integration tests


def test_integration_with_real_rules(tmp_path, sample_asciidoc):
    """Test the linter with actual rules and a sample document"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text(sample_asciidoc)

    linter = AsciiDocLinter()
    report = linter.lint([test_file])
    assert isinstance(report, LintReport)
    # Note: actual number of errors depends on the implemented rules
