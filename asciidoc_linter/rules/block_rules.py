# block_rules.py - Rules for checking blocks in AsciiDoc files

from typing import List, Union, Dict
from .base import Rule, Finding, Severity, Position

class UnterminatedBlockRule(Rule):
    """Rule to check for unterminated blocks"""
    id = "BLOCK001"
    name = "Unterminated Block"
    description = "Checks for unterminated blocks"
    severity = Severity.ERROR

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        block_stack = []
        
        for line_number, line in enumerate(document):
            line_content = str(line).strip()
            
            # Check for block delimiters
            if line_content in ['----', '====', '****', '....', '|===']:
                if not block_stack or block_stack[-1] != line_content:
                    block_stack.append(line_content)
                else:
                    block_stack.pop()
            
            # Check for listing blocks
            elif line_content.startswith('[source'):
                next_line = document[line_number + 1] if line_number + 1 < len(document) else ''
                if str(next_line).strip() != '----':
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message="Source block not followed by delimiter",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
        
        # Report unterminated blocks
        for block in block_stack:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=len(document)),
                    message=f"Unterminated block: {block}",
                    severity=self.severity,
                    context="End of file",
                )
            )
        
        return findings

class BlockSpacingRule(Rule):
    """Rule to check block spacing"""
    id = "BLOCK002"
    name = "Block Spacing"
    description = "Checks for proper spacing around blocks"
    severity = Severity.WARNING

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        block_delimiters = ['----', '====', '****', '....', '|===']
        
        for line_number, line in enumerate(document):
            line_content = str(line).strip()
            
            if line_content in block_delimiters:
                # Check spacing before block
                if line_number > 0:
                    prev_line = str(document[line_number - 1]).strip()
                    if prev_line and not prev_line.startswith('['):
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_number + 1),
                                message="Block should be preceded by a blank line",
                                severity=self.severity,
                                context=line_content,
                            )
                        )
                
                # Check spacing after block
                if line_number < len(document) - 1:
                    next_line = str(document[line_number + 1]).strip()
                    if next_line and not any(next_line.startswith(d) for d in block_delimiters):
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_number + 1),
                                message="Block should be followed by a blank line",
                                severity=self.severity,
                                context=line_content,
                            )
                        )
        
        return findings