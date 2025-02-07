# test_cli.py - Tests for command line interface
"""Tests for the command line interface"""

import unittest
from unittest.mock import patch
from asciidoc_linter.cli import main, create_parser, get_reporter
from asciidoc_linter.rules.base import Finding, Severity
from asciidoc_linter.reporter import (
    ConsoleReporter,
    JsonReporter,
    HtmlReporter,
    LintReport,
)


class TestCliArgumentParsing(unittest.TestCase):
    """Test argument parsing functionality"""

    def test_create_parser(self):
        """Test parser creation and default values"""
        parser = create_parser()
        args = parser.parse_args(["test.adoc"])

        self.assertEqual(args.files, ["test.adoc"])
        self.assertEqual(args.format, "console")
        self.assertIsNone(args.config)

    def test_multiple_files(self):
        """Test parsing multiple file arguments"""
        parser = create_parser()
        args = parser.parse_args(["file1.adoc", "file2.adoc"])

        self.assertEqual(args.files, ["file1.adoc", "file2.adoc"])

    def test_format_option(self):
        """Test different format options"""
        parser = create_parser()

        # Test console format
        args = parser.parse_args(["test.adoc", "--format", "console"])
        self.assertEqual(args.format, "console")

        # Test JSON format
        args = parser.parse_args(["test.adoc", "--format", "json"])
        self.assertEqual(args.format, "json")

        # Test HTML format
        args = parser.parse_args(["test.adoc", "--format", "html"])
        self.assertEqual(args.format, "html")

    def test_config_option(self):
        """Test config file option"""
        parser = create_parser()
        args = parser.parse_args(["test.adoc", "--config", "config.yml"])

        self.assertEqual(args.config, "config.yml")

    def test_invalid_format(self):
        """Test invalid format option"""
        parser = create_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["test.adoc", "--format", "invalid"])


class TestCliFileProcessing(unittest.TestCase):
    """Test file processing functionality"""

    @patch("asciidoc_linter.linter.AsciiDocLinter.lint")
    def test_successful_lint(self, mock_lint):
        """Test successful file linting"""
        mock_lint.return_value = LintReport([])  # No lint errors

        exit_code = main(["valid.adoc"])

        self.assertEqual(exit_code, 0)
        mock_lint.assert_called_once()

    @patch("asciidoc_linter.linter.AsciiDocLinter.lint")
    def test_lint_with_errors(self, mock_lint):
        """Test file linting with errors"""
        mock_lint.return_value = LintReport(
            [Finding(message="Foo", severity=Severity.ERROR)]
        )  # Simulate lint error

        exit_code = main(["invalid.adoc"])

        self.assertEqual(exit_code, 1)
        mock_lint.assert_called_once()


class TestCliReporters(unittest.TestCase):
    """Test reporter selection and usage"""

    def test_json_reporter(self):
        """Test JSON reporter selection"""
        args = create_parser().parse_args(["test.adoc", "--format", "json"])
        self.assertIsInstance(get_reporter(args.format), JsonReporter)

    def test_html_reporter(self):
        """Test HTML reporter selection"""
        args = create_parser().parse_args(["test.adoc", "--format", "html"])
        self.assertIsInstance(get_reporter(args.format), HtmlReporter)

    def test_console_reporter(self):
        """Test explicit console reporter"""
        args = create_parser().parse_args(["test.adoc", "--format", "console"])
        self.assertIsInstance(get_reporter(args.format), ConsoleReporter)

    def test_default_console_reporter(self):
        """Test default console reporter"""
        args = create_parser().parse_args(["test.adoc"])
        self.assertIsInstance(get_reporter(args.format), ConsoleReporter)


if __name__ == "__main__":
    unittest.main()
