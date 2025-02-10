# table_rules.py - Implementation of table rules
"""
This module contains rules for checking AsciiDoc table structure and format.
"""

from typing import List, Dict, Any, Union, Optional, Tuple
from .base import Rule, Finding, Severity, Position
import re


class TableFormatRule(Rule):
    """
    TABLE001: Check table formatting.
    Ensures that tables are consistently formatted:
    - Column separators are properly aligned
    - Header row is properly marked
    - Cells are properly aligned
    """

    def __init__(self):
        super().__init__()
        self.id = "TABLE001"
        self.cell_pattern = re.compile(r"\|([^|]*)")

    @property
    def description(self) -> str:
        return "Ensures consistent table formatting (alignment and structure)"

    def extract_table_lines(
        self, content: Union[List[str], List[Tuple[int, str]]]
    ) -> List[List[Tuple[int, str]]]:
        """Extract tables from document lines.
        Returns a list of tables, where each table is a list of (line_number, line) tuples.
        """
        tables = []
        current_table = []
        in_table = False

        # Convert content to list of tuples if it's not already
        if content and isinstance(content[0], str):
            content = [(i, line) for i, line in enumerate(content)]

        for line_num, line in content:
            if not isinstance(line, str):
                continue

            stripped = line.strip()
            if stripped == "|===":
                if in_table:
                    current_table.append((line_num, line))
                    tables.append(current_table)
                    current_table = []
                    in_table = False
                else:
                    in_table = True
                    current_table = [(line_num, line)]
            elif in_table:
                current_table.append((line_num, line))

        # Handle unclosed table
        if in_table and current_table:
            tables.append(current_table)

        return tables

    def check_column_alignment(
        self, table_lines: List[Tuple[int, str]]
    ) -> List[Finding]:
        """Check if columns are consistently aligned within a table."""
        findings = []
        cell_positions = []  # List of lists of cell positions for each row

        for line_num, line in table_lines[1:-1]:  # Skip table markers
            if not line.strip():  # Skip empty lines
                continue

            matches = list(self.cell_pattern.finditer(line))
            if matches:
                positions = [m.start() for m in matches]
                if cell_positions and positions != cell_positions[0]:
                    findings.append(
                        Finding(
                            message="Column alignment is inconsistent with previous rows",
                            severity=Severity.WARNING,
                            position=Position(line=line_num + 1),
                            rule_id=self.id,
                            context={"line": line},
                        )
                    )
                    break
                cell_positions.append(positions)

        return findings

    def check_header_separator(
        self, table_lines: List[Tuple[int, str]]
    ) -> List[Finding]:
        """Check if header is properly separated from content."""
        findings = []

        # Find header row
        header_line = None
        for i, (line_num, line) in enumerate(
            table_lines[1:-1], 1
        ):  # Skip table markers
            if "|" in line:
                header_line = i
                break

        if header_line is not None:
            # Check for empty line after header
            next_line = header_line + 1
            if next_line < len(table_lines) - 1:  # Ensure we're not at the end
                if table_lines[next_line][
                    1
                ].strip():  # Line after header should be empty
                    findings.append(
                        Finding(
                            message="Header row should be followed by an empty line",
                            severity=Severity.WARNING,
                            position=Position(line=table_lines[next_line][0] + 1),
                            rule_id=self.id,
                            context={"line": table_lines[next_line][1]},
                        )
                    )

        return findings

    def check(self, document: Union[Dict[str, Any], List[Any], str]) -> List[Finding]:
        findings = []

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        # Extract tables
        tables = self.extract_table_lines(lines)

        # Check each table
        for table in tables:
            findings.extend(self.check_column_alignment(table))
            findings.extend(self.check_header_separator(table))

        return findings


class TableStructureRule(Rule):
    """
    TABLE002: Check table structure.
    Ensures that tables have consistent structure:
    - All rows have the same number of columns
    - No empty tables
    - No missing cells
    """

    def __init__(self):
        super().__init__()
        self.id = "TABLE002"
        self.cell_pattern = re.compile(r"\|(?!={3,}$)([^|]*)")

    @property
    def description(self) -> str:
        return "Ensures consistent table structure (column counts and completeness)"

    def count_columns(self, line: str) -> int:
        """Count the number of columns in a table row."""
        # Skip table markers
        if line.strip() == "|===":
            return 0
        # Count cells using regex to handle prefixes correctly
        matches = self.cell_pattern.finditer(line)
        return sum(1 for _ in matches)

    def check_table_structure(
        self, table_lines: List[Tuple[int, str]]
    ) -> List[Finding]:
        """Check table structure for consistency."""
        findings = []
        column_count = None
        content_lines = 0

        for line_num, line in table_lines[1:-1]:  # Skip table markers
            stripped = line.strip()
            if not stripped:  # Skip empty lines
                continue

            if "|" in stripped and stripped != "|===":
                content_lines += 1
                current_columns = self.count_columns(stripped)

                if column_count is None:
                    column_count = current_columns
                elif current_columns != column_count:
                    findings.append(
                        Finding(
                            message=f"Inconsistent column count. Expected {column_count}, found {current_columns}",
                            severity=Severity.ERROR,
                            position=Position(line=line_num + 1),
                            rule_id=self.id,
                            context={"line": line},
                        )
                    )

        if content_lines == 0:
            findings.append(
                Finding(
                    message="Empty table",
                    severity=Severity.WARNING,
                    position=Position(line=table_lines[0][0] + 1),
                    rule_id=self.id,
                    context={"line": table_lines[0][1]},
                )
            )

        return findings

    def check(self, document: Union[Dict[str, Any], List[Any], str]) -> List[Finding]:
        findings = []

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        # Extract tables using TableFormatRule's method
        format_rule = TableFormatRule()
        tables = format_rule.extract_table_lines(lines)

        # Check each table
        for table in tables:
            findings.extend(self.check_table_structure(table))

        return findings


class TableContentRule(Rule):
    """
    TABLE003: Check table cell content.
    Ensures that table cells don't contain complex content without proper declarations:
    - Lists in cells
    - Nested tables
    """

    def __init__(self):
        super().__init__()
        self.id = "TABLE003"
        self.list_pattern = re.compile(r"^\s*[\*\-]")
        # Pattern to match cells with optional prefixes
        # This pattern matches:
        # 1. | followed by optional whitespace
        # 2. Optional prefix (a or l) followed by |
        # 3. Cell content up to the next | or end of string
        self.cell_pattern = re.compile(r"\|\s*(?:([al])\|\s*)?([^|]*)")

    @property
    def description(self) -> str:
        return "Checks for proper declaration of complex content in table cells"

    def extract_cells(self, line: str) -> List[Tuple[str, str]]:
        """Extract cells and their prefixes from a line.
        Returns a list of (prefix, content) tuples.
        """
        cells = []
        # Skip table markers
        if line.strip() == "|===":
            return cells

        # Use regex to find all cells with their prefixes
        matches = self.cell_pattern.finditer(line)
        for match in matches:
            prefix = match.group(1) or ""  # Group 1 is the prefix (a or l)
            content = match.group(2).strip()  # Group 2 is the cell content
            cells.append((prefix, content))

        return cells

    def check_cell_content(
        self, prefix: str, content: str, line_num: int, context: str
    ) -> Optional[Finding]:
        """Check a single cell for complex content. Returns a finding or None."""
        # Check for lists - only check if content starts with a list marker
        if content and self.list_pattern.match(content):
            if prefix not in ["a", "l"]:
                return Finding(
                    message="List in table cell requires 'a|' or 'l|' declaration",
                    severity=Severity.WARNING,
                    position=Position(line=line_num + 1),
                    rule_id=self.id,
                    context={"line": context},
                )

        return None

    def check(self, document: Union[Dict[str, Any], List[Any], str]) -> List[Finding]:
        findings = []

        # Convert document to lines if it's not already
        if isinstance(document, dict):
            lines = document.get("content", "").splitlines()
        elif isinstance(document, str):
            lines = document.splitlines()
        else:
            lines = document

        # Extract tables using TableFormatRule's method
        format_rule = TableFormatRule()
        tables = format_rule.extract_table_lines(lines)

        # Check each table
        for table in tables:
            found_list = False  # Track if we've found a list in this table
            for line_num, line in table[1:-1]:  # Skip table markers
                if (
                    not line.strip() or line.strip() == "|==="
                ):  # Skip empty lines and table markers
                    continue

                # Extract and check cells
                cells = self.extract_cells(line)
                for prefix, content in cells:
                    if (
                        not found_list
                    ):  # Only check for lists if we haven't found one yet in this table
                        finding = self.check_cell_content(
                            prefix, content, line_num, line
                        )
                        if finding:
                            findings.append(finding)
                            found_list = True  # Stop checking after first list finding in this table
                            break  # Exit the cell loop

                if found_list:
                    break  # Exit the line loop if we found a list

        return findings
