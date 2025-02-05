# cli.py - Command line interface
"""
Command line interface for the AsciiDoc linter
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path
from .linter import AsciiDocLinter
from .reporter import ConsoleReporter, JsonReporter, HtmlReporter

def create_parser() -> argparse.ArgumentParser:
    """Create the command line parser"""
    parser = argparse.ArgumentParser(
        description='Lint AsciiDoc files for common issues and style violations'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='One or more AsciiDoc files to check'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--format',
        choices=['console', 'json', 'html'],
        default='console',
        help='Output format (default: console)'
    )
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the linter"""
    if args is None:
        args = sys.argv[1:]
    
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    report = AsciiDocLinter().lint(parsed_args.files)

    # Set reporter based on format argument
    reporter = ConsoleReporter()
    if parsed_args.format == 'json':
        reporter = JsonReporter()
    elif parsed_args.format == 'html':
        reporter = HtmlReporter()
    print(reporter.format_report(report))

    return report.exit_code

if __name__ == '__main__':
    sys.exit(main())