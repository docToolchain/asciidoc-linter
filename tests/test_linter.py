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
    assert (
        len(linter.rules) == 11
    )  # Verify number of default rules (FMT001, FMT002, FMT003, FMT004)
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


def test_lint_with_config_file(tmp_path, sample_asciidoc):
    """Test linting with a configuration file that disables a rule"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text(sample_asciidoc)

    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text(
        """
rules:
  WS001:
    enabled: false
"""
    )

    linter = AsciiDocLinter(config_path=config_file)
    report = linter.lint([test_file])

    # Ensure that the WS001 rule is disabled and no findings are reported
    assert len(report.findings) == 0


# Tests for UTF-8 encoding support (Issue #24)


def test_lint_file_utf8_characters(tmp_path):
    """Test linting a file with UTF-8 characters (German umlauts, emojis, etc.)"""
    test_file = tmp_path / "utf8_test.adoc"
    utf8_content = """= Überschrift mit Umlauten

== Abschnitt mit Sonderzeichen

Größe, Höhe, Länge – diese Wörter enthalten Umlaute.

=== Emojis und Symbole

Ein Beispiel mit Emoji: 🚀 und Symbole: © ® ™

=== Internationaler Text

日本語テスト – Chinesisch: 中文测试 – Russisch: Русский текст
"""
    # Write with explicit UTF-8 encoding
    test_file.write_text(utf8_content, encoding="utf-8")

    linter = AsciiDocLinter()
    findings = linter.lint_file(test_file)

    # Should not have any encoding-related errors
    encoding_errors = [f for f in findings if "codec" in f.message.lower()]
    assert len(encoding_errors) == 0, f"Unexpected encoding errors: {encoding_errors}"


def test_lint_file_utf8_config(tmp_path):
    """Test that config files with UTF-8 content are read correctly"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("= Title\n\nContent\n", encoding="utf-8")

    config_file = tmp_path / ".asciidoc-lint.yml"
    # Config with UTF-8 comment
    config_content = """# Konfigurationsdatei für AsciiDoc-Linter
# Größe: klein
rules:
  WS001:
    enabled: false
"""
    config_file.write_text(config_content, encoding="utf-8")

    linter = AsciiDocLinter(config_path=str(config_file))
    report = linter.lint([str(test_file)])

    # Should successfully load config without encoding errors
    assert isinstance(report, LintReport)


def test_lint_file_invalid_utf8_gives_error(tmp_path):
    """Test that files with invalid UTF-8 give a clear error message"""
    test_file = tmp_path / "invalid_utf8.adoc"
    # Write invalid UTF-8 bytes directly
    test_file.write_bytes(b"= Title\n\nInvalid byte: \x80\x81\x82\n")

    linter = AsciiDocLinter()
    findings = linter.lint_file(test_file)

    # Should have exactly one error about encoding
    assert len(findings) == 1
    assert "Error linting file" in findings[0].message
    # Error message should mention encoding or decode issue
    assert (
        "decode" in findings[0].message.lower()
        or "codec" in findings[0].message.lower()
        or "encoding" in findings[0].message.lower()
    )


def test_lint_file_uses_explicit_utf8_encoding(tmp_path):
    """Test that lint_file uses explicit UTF-8 encoding (not system default)"""
    test_file = tmp_path / "test.adoc"
    test_file.write_text("= Title\n\nContent\n", encoding="utf-8")

    linter = AsciiDocLinter()

    # Mock Path.read_text to verify encoding parameter is passed
    with patch.object(Path, "read_text") as mock_read_text:
        mock_read_text.return_value = "= Title\n\nContent\n"
        linter.lint_file(test_file)

        # Verify read_text was called with encoding='utf-8'
        mock_read_text.assert_called_once_with(encoding="utf-8")


def test_load_config_uses_explicit_utf8_encoding(tmp_path):
    """Test that load_config uses explicit UTF-8 encoding"""
    config_file = tmp_path / ".asciidoc-lint.yml"
    config_file.write_text("rules:\n  WS001:\n    enabled: false\n", encoding="utf-8")

    linter = AsciiDocLinter()

    # Use mock to verify encoding parameter
    import builtins

    original_open = builtins.open
    open_calls = []

    def mock_open(*args, **kwargs):
        open_calls.append((args, kwargs))
        return original_open(*args, **kwargs)

    with patch.object(builtins, "open", mock_open):
        linter.load_config(str(config_file))

    # Find the call to our config file
    config_call = [c for c in open_calls if str(config_file) in str(c[0])]
    assert len(config_call) == 1
    # Verify encoding='utf-8' was passed
    assert config_call[0][1].get("encoding") == "utf-8"
