# table_rules.py - Rules for checking tables in AsciiDoc files

from typing import List, Union, Optional
from .base import Rule, Finding, Severity, Position

class TableFormatRule(Rule):
    """Rule to check table formatting"""
    id = "TABLE001"
    name = "Table Format"
    description = "Checks for proper table formatting"
    severity = Severity.WARNING

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        in_table = False
        table_start_line = 0
        column_count = None
        
        for line_number, line in enumerate(document):
            line_content = str(line)
            
            # Check for table start/end
            if line_content.strip() == '|===':
                if not in_table:
                    in_table = True
                    table_start_line = line_number
                else:
                    in_table = False
                    column_count = None
                continue
            
            if in_table:
                # Skip empty lines and attribute lines
                if not line_content.strip() or line_content.strip().startswith('['):
                    continue
                
                # Count columns in this row
                if line_content.strip().startswith('|'):
                    current_columns = line_content.count('|')
                    
                    # First content line sets the expected column count
                    if column_count is None:
                        column_count = current_columns
                    # Check if subsequent lines match the column count
                    elif current_columns != column_count:
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_number + 1),
                                message=f"Inconsistent column count: expected {column_count}, found {current_columns}",
                                severity=self.severity,
                                context=line_content,
                            )
                        )
        
        # Check for unterminated table
        if in_table:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=table_start_line + 1),
                    message="Unterminated table",
                    severity=self.severity,
                    context="Table starting at line " + str(table_start_line + 1),
                )
            )
        
        return findings