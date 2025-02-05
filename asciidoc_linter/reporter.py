# reporter.py - Output formatters for lint results
"""
Different output formatters for lint results
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

from .rules.base import Finding

@dataclass
class LintReport:
    """Contains all lint findings for a document"""
    findings: List[Finding]

    def grouped_findings(self) -> Dict[str, List[Finding]]:
        grouped = defaultdict(list)
        for finding in self.findings:
            grouped[finding.file].append(finding)
        return grouped

    @property
    def exit_code(self) -> int:
        return 1 if self.findings else 0

    def __bool__(self):
        return bool(self.findings)

    def __len__(self):
        return len(self.findings)

class Reporter:
    """Base class for formatting lint reports"""
    
    def format_report(self, report: LintReport) -> str:
        """Format the report as string"""
        if not report:
            return "✓ No issues found"

        output = []
        for file, findings in report.grouped_findings().items():
            output.append(f"Results for {file}:")
            for finding in findings:
                output.append(f"{finding.location}: {finding.message}")
            output.append("\n")
        
        return "\n".join(output)

class ConsoleReporter(Reporter):
    """Reports findings in console format with colors"""
    
    def format_report(self, report: LintReport) -> str:
        """Format the report with ANSI colors"""
        if not report:
            return "\033[32m✓ No issues found\033[0m"
            
        output = []
        for file, findings in report.grouped_findings().items():
            output.append(f"Results for {file}:")
            for finding in findings:
                output.append(f"\033[31m✗\033[0m {finding.location}: {finding.message}")
            output.append("\n")
        
        return "\n".join(output)

class JsonReporter(Reporter):
    """Reports findings in JSON format"""
    
    def format_report(self, report: LintReport) -> str:
        return json.dumps([
            finding.to_json_object()
            for finding in report.findings
        ], indent=2)

class HtmlReporter(Reporter):
    """Reports findings in HTML format"""
    
    def format_report(self, report: LintReport) -> str:
        rows = []
        for finding in report.findings:
            rows.append(
                f'<tr>'
                f'<td>{finding.severity}</td>'
                f'<td>{finding.rule_id or ""}</td>'
                f'<td>{finding.location}</td>'
                f'<td>{finding.message}</td>'
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
            <th>Severity</th>
            <th>Rule ID</th>
            <th>Location</th>
            <th>Message</th>
        </tr>
        {"".join(rows)}
    </table>
</body>
</html>"""