# reporter.py - Output formatters for lint results
"""
Different output formatters for lint results
"""

from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class LintError:
    """Represents a single lint error"""
    file: Optional[str]
    line: int
    message: str

@dataclass
class LintReport:
    """Contains all lint errors for a document"""
    errors: List[LintError]

    def __bool__(self):
        return bool(self.errors)

    def __len__(self):
        return len(self.errors)

class Reporter:
    """Base class for formatting lint reports"""
    
    def format_report(self, report: LintReport) -> str:
        """Format the report as string"""
        output = []
        for error in report.errors:
            location = f"line {error.line}"
            if error.file:
                location = f"{error.file}:{location}"
            
            output.append(f"{location}: {error.message}")
        
        return "\n".join(output)

class ConsoleReporter(Reporter):
    """Reports findings in console format with colors"""
    
    def format_report(self, report: LintReport) -> str:
        """Format the report with ANSI colors"""
        if not report.errors:
            return "\033[32m✓ No issues found\033[0m"
            
        output = []
        for error in report.errors:
            location = f"\033[36mline {error.position.line}\033[0m"
            if error.file:
                location = f"\033[36m{error.file}:{location}\033[0m"
            
            output.append(f"\033[31m✗\033[0m {location}: {error.message}")
        
        return "\n".join(output)

class JsonReporter(Reporter):
    """Reports findings in JSON format"""
    
    def format_report(self, report: LintReport) -> str:
        return json.dumps([
            {
                'file': error.file,
                'line': error.line,
                'message': error.message
            }
            for error in report.errors
        ], indent=2)

class HtmlReporter(Reporter):
    """Reports findings in HTML format"""
    
    def format_report(self, report: LintReport) -> str:
        rows = []
        for error in report.errors:
            location = f"Line {error.line}"
            if error.file:
                location = f"{error.file}:{location}"
            
            rows.append(
                f'<tr>'
                f'<td>{location}</td>'
                f'<td>{error.message}</td>'
                f'</tr>'
            )
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AsciiDoc Lint Results</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>AsciiDoc Lint Results</h1>
    <table>
        <tr>
            <th>Location</th>
            <th>Message</th>
        </tr>
        {"".join(rows)}
    </table>
</body>
</html>"""
