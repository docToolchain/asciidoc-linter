# test_reporter.py - Tests for the reporter module
"""
Tests for the reporter module that handles formatting of lint results
"""

import json
import pytest
from asciidoc_linter.rules.base import Finding, Severity, Position
from asciidoc_linter.reporter import (
    LintReport,
    ConsoleReporter,
    JsonReporter,
    HtmlReporter,
)

# Test Data


@pytest.fixture
def sample_finding():
    """Create a sample lint error"""
    return Finding(
        message="Test error message",
        severity=Severity.ERROR,
        file="test.adoc",
        position=Position(
            line=42,
            column=3,
        ),
        rule_id="TEST001",
        context="context",
    )


@pytest.fixture
def empty_report():
    """Create a sample report with no errors"""
    return LintReport([])


@pytest.fixture
def sample_report(sample_finding):
    """Create a report with errors"""
    return LintReport(
        [
            sample_finding,
            Finding(
                message="Minimal finding", severity=Severity.WARNING, file="test.adoc"
            ),
            Finding(message="Minimal finding without file", severity=Severity.WARNING),
        ]
    )


# Test LintReport


def test_lint_report_creation(sample_finding):
    """Test creating a LintReport"""
    report = LintReport([sample_finding])
    assert len(report.findings) == 1
    assert report.findings[0] == sample_finding


def test_lint_report_bool(sample_report, empty_report):
    """Test boolean evaluation of LintReport"""
    assert bool(sample_report) is True
    assert bool(empty_report) is False


def test_lint_report_len(sample_report, empty_report):
    """Test len() on LintReport"""
    assert len(sample_report) == 3
    assert len(empty_report) == 0


def test_lint_report_exit_code(sample_report, empty_report):
    """Test LintReport.exit_code"""
    assert sample_report.exit_code == 1
    assert empty_report.exit_code == 0


def test_lint_report_grouped_findings(sample_report, sample_finding, empty_report):
    """Test LintReport.grouped_findings"""
    grouped = sample_report.grouped_findings()
    assert len(grouped) == 2
    assert len(grouped["test.adoc"]) == 2
    assert grouped["test.adoc"][0] == sample_finding
    assert len(grouped[None]) == 1

    assert len(empty_report.grouped_findings()) == 0


# Test Console Reporter


def test_console_reporter(sample_report):
    """Test formatting multiple errors"""
    reporter = ConsoleReporter(enable_color=False)
    lines = reporter.format_report(sample_report).split("\n")
    assert "Results for test.adoc:" in lines
    assert "✗ test.adoc, line 42, column 3: Test error message" in lines
    assert "✗ test.adoc: Minimal finding" in lines
    assert "Results without file:" in lines
    assert "✗ Minimal finding without file" in lines


def test_console_reporter_empty(empty_report):
    """Test formatting no findings"""
    reporter = ConsoleReporter(enable_color=False)
    output = reporter.format_report(empty_report)
    assert output == "✓ No issues found"


def test_console_reporter_colored(sample_report):
    """Test formatting multiple errors"""
    reporter = ConsoleReporter(enable_color=True)
    lines = reporter.format_report(sample_report).split("\n")
    assert "Results for test.adoc:" in lines
    assert "\033[31m✗\033[0m test.adoc, line 42, column 3: Test error message" in lines
    assert "\033[31m✗\033[0m test.adoc: Minimal finding" in lines
    assert "Results without file:" in lines
    assert "\033[31m✗\033[0m Minimal finding without file" in lines


def test_console_reporter_empty_colored(empty_report):
    """Test formatting no findings"""
    reporter = ConsoleReporter(enable_color=True)
    output = reporter.format_report(empty_report)
    assert output == "\033[32m✓ No issues found\033[0m"


# Test JSON Reporter


def test_json_reporter(sample_report):
    """Test JSON formatting of a report"""
    reporter = JsonReporter()
    output = reporter.format_report(sample_report)
    data = json.loads(output)
    assert len(data["findings"]) == 3
    assert data["findings"][0]["file"] == "test.adoc"
    assert data["findings"][0]["line"] == 42
    assert data["findings"][0]["column"] == 3
    assert data["findings"][0]["message"] == "Test error message"
    assert data["findings"][0]["severity"] == "error"
    assert data["findings"][0]["rule_id"] == "TEST001"
    assert data["findings"][0]["context"] == "context"
    assert data["findings"][2]["file"] is None
    assert data["findings"][2]["line"] is None
    assert data["findings"][2]["column"] is None


# Test HTML Reporter


def test_html_reporter(sample_report):
    """Test HTML formatting of a report"""
    reporter = HtmlReporter()
    lines = reporter.format_report(sample_report).split("\n")
    assert "<td>error</td>" in lines
    assert "<td>TEST001</td>" in lines
    assert "<td>test.adoc, line 42, column 3</td>" in lines
    assert "<td>Test error message</td>" in lines


def test_html_reporter_styling(sample_report):
    """Test that HTML output includes CSS styling"""
    reporter = HtmlReporter()
    output = reporter.format_report(sample_report)
    assert "<style>" in output
    assert "table {" in output
    assert "border-collapse: collapse" in output
