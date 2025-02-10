# whitespace_rules.py - Rules for checking whitespace in AsciiDoc files

from typing import List, Union
from .base import Rule, Finding, Severity, Position


class WhitespaceRule(Rule):
    """Rule to check for proper whitespace usage."""

    id = "WS001"
    name = "Whitespace Check"
    description = "Checks for proper whitespace usage"
    severity = Severity.WARNING

    def __init__(self):
        super().__init__()
        self.consecutive_empty_lines = 0

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        """Check the entire document for whitespace issues."""
        findings = []
        for line_number, line in enumerate(document):
            findings.extend(self.check_line(line, line_number, document))
        return findings

    def get_line_content(self, line: Union[str, object]) -> str:
        """Extract the content from a line object or return the line if it's a string."""
        if hasattr(line, "content"):
            return line.content
        return str(line)

    def check_line(
        self,
        line: Union[str, object],
        line_number: int,
        context: List[Union[str, object]],
    ) -> List[Finding]:
        findings = []
        line_content = self.get_line_content(line)

        # Check for multiple consecutive empty lines
        if not line_content.strip():
            self.consecutive_empty_lines += 1
            if self.consecutive_empty_lines > 2:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        position=Position(line=line_number + 1),
                        message="Too many consecutive empty lines",
                        severity=self.severity,
                        context=line_content,
                    )
                )
        else:
            self.consecutive_empty_lines = 0

        # Check for proper list marker spacing
        if line_content.lstrip().startswith(("*", "-", ".")):
            marker = line_content.lstrip()[0]
            content = line_content.lstrip()[1:]

            if not content.startswith(" "):
                findings.append(
                    Finding(
                        rule_id=self.id,
                        position=Position(line=line_number + 1),
                        message=f"Missing space after the marker '{marker}'",
                        severity=self.severity,
                        context=line_content,
                    )
                )

        # Check for trailing whitespace
        if line_content.rstrip() != line_content:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=line_number + 1),
                    message="Line contains trailing whitespace",
                    severity=self.severity,
                    context=line_content,
                )
            )

        # Check for tabs
        if "\t" in line_content:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=line_number + 1),
                    message="Line contains tabs (use spaces instead)",
                    severity=self.severity,
                    context=line_content,
                )
            )

        # Check for proper section title spacing
        if line_content.startswith("="):
            # Count leading = characters
            level = 0
            for char in line_content:
                if char != "=":
                    break
                level += 1

            # Check spacing after = characters
            if len(line_content) > level and line_content[level] != " ":
                findings.append(
                    Finding(
                        rule_id=self.id,
                        position=Position(line=line_number + 1),
                        message=f"Missing space after {'=' * level}",
                        severity=self.severity,
                        context=line_content,
                    )
                )

            # Check for blank line before section title (except for first line)
            if line_number > 0:
                prev_content = self.get_line_content(context[line_number - 1])
                if prev_content.strip():
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message="Section title should be preceded by a blank line",
                            severity=self.severity,
                            context=line_content,
                        )
                    )

            # Check for blank line after section title (except for last line)
            if line_number < len(context) - 1:
                next_content = self.get_line_content(context[line_number + 1])
                if next_content.strip():
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message="Section title should be followed by a blank line",
                            severity=self.severity,
                            context=line_content,
                        )
                    )

        # Check for proper admonition block spacing
        admonition_markers = ["NOTE:", "TIP:", "IMPORTANT:", "WARNING:", "CAUTION:"]
        if any(
            line_content.strip().startswith(marker) for marker in admonition_markers
        ):
            if line_number > 0:
                prev_content = self.get_line_content(context[line_number - 1])
                if prev_content.strip():
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message="Admonition block should be preceded by a blank line",
                            severity=self.severity,
                            context=line_content,
                        )
                    )

        return findings
