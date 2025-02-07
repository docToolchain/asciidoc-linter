# cli.py - Command line interface
"""
Command line interface for the AsciiDoc linter
"""

import argparse
import sys
from typing import List, Optional
from .linter import AsciiDocLinter
from .reporter import ConsoleReporter, JsonReporter, HtmlReporter, Reporter


def create_parser() -> argparse.ArgumentParser:
    """Create the command line parser"""
    parser = argparse.ArgumentParser(
        description="Lint AsciiDoc files for common issues and style violations"
    )
    parser.add_argument("files", nargs="+", help="One or more AsciiDoc files to check")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--format",
        choices=["console", "plain", "json", "html"],
        default="console",
        help="Output format (default: console)",
    )
    return parser


def get_reporter(format: str) -> Reporter:
    if format == "json":
        return JsonReporter()
    if format == "html":
        return HtmlReporter()
    if format == "plain":
        return ConsoleReporter(enable_color=False)
    if format == "console":
        return ConsoleReporter(enable_color=True)
    raise ValueError(f"Unrecognised format {format}")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the linter"""
    if args is None:
        args = sys.argv[1:]

    parser = create_parser()
    parsed_args = parser.parse_args(args)

    report = AsciiDocLinter().lint(parsed_args.files)

    # Set reporter based on format argument
    print(get_reporter(parsed_args.format).format_report(report))

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
