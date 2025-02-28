# cli.py - Command-line interface for the linter

import sys
import argparse
from pathlib import Path
from typing import List, Optional

from .linter import AsciiDocLinter
from .reporter import ConsoleReporter, PlainReporter, JsonReporter, HtmlReporter

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Lint AsciiDoc files for common issues and style violations"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more AsciiDoc files to check",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--format",
        choices=["console", "plain", "json", "html"],
        default="console",
        help="Output format (default: console)",
    )
    return parser

def get_reporter(format_name: str):
    """Get the appropriate reporter for the specified format"""
    reporters = {
        "console": ConsoleReporter,
        "plain": PlainReporter,
        "json": JsonReporter,
        "html": HtmlReporter,
    }
    return reporters.get(format_name, ConsoleReporter)()

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI
    
    Args:
        args: Optional list of command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(args)

    # Create linter with configuration if provided
    linter = AsciiDocLinter(args.config)
    
    # Get appropriate reporter
    reporter = get_reporter(args.format)
    
    # Lint all files
    report = linter.lint(args.files)
    
    # Output results
    output = reporter.report(report)
    print(output)
    
    # Return non-zero if there were any errors
    return 1 if any(finding.severity == "error" for finding in report.findings) else 0

if __name__ == "__main__":
    sys.exit(main())