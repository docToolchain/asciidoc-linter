# reporter.py - Output formatters for lint results
"""
Different output formatters for lint results
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict
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


class Reporter(ABC):
    """Base class for lint report formatters."""

    @abstractmethod
    def format_report(self, report: LintReport) -> str:
        pass


class ConsoleReporter(Reporter):
    """Base class for formatting lint reports"""

    def __init__(self, enable_color):
        self.enable_color = enable_color

    def _green(self, text):
        if not self.enable_color:
            return text
        return f"\033[32m{text}\033[0m"

    def _red(self, text):
        if not self.enable_color:
            return text
        return f"\033[31m{text}\033[0m"

    def format_report(self, report: LintReport) -> str:
        """Format the report as string"""
        if not report:
            return self._green("✓ No issues found")

        output = []
        for file, findings in report.grouped_findings().items():
            if file:
                output.append(f"Results for {file}:")
            else:
                output.append("Results without file:")

            for finding in findings:
                location = finding.location
                if location:
                    output.append(
                        f"{self._red('✗')} {finding.location}: {finding.message}"
                    )
                else:
                    output.append(f"{self._red('✗')} {finding.message}")
            output.append("\n")

        return "\n".join(output)


class JsonReporter(Reporter):
    """Reports findings in JSON format"""

    def format_report(self, report: LintReport) -> str:
        return json.dumps(
            {
                "findings": [finding.to_json_object() for finding in report.findings],
            },
            indent=2,
        )


class HtmlReporter(Reporter):
    """Reports findings in HTML format"""

    def format_report(self, report: LintReport) -> str:
        rows = []
        for finding in report.findings:
            rows.extend(
                [
                    "<tr>",
                    f"<td>{finding.severity}</td>",
                    f'<td>{finding.rule_id or ""}</td>',
                    f"<td>{finding.location}</td>",
                    f"<td>{finding.message}</td>",
                    "</tr>",
                ]
            )

        rows = "\n".join(rows)

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
        {rows}
    </table>
</body>
</html>"""
