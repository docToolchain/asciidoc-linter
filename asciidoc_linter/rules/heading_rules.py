# heading_rules.py - Rules for checking headings in AsciiDoc files

from typing import List, Union, Dict
from .base import Rule, Finding, Severity, Position

class HeadingFormatRule(Rule):
    """Rule to check heading format"""
    id = "HEAD001"
    name = "Heading Format"
    description = "Checks for proper heading format"
    severity = Severity.ERROR

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        for line_number, line in enumerate(document):
            line_content = str(line).strip()
            if line_content.startswith('='):
                # Check for proper spacing after = characters
                level = 0
                for char in line_content:
                    if char != '=':
                        break
                    level += 1
                
                # Missing space after = characters
                if len(line_content) > level and line_content[level] != ' ':
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Missing space after {'=' * level}",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                    continue  # Skip further checks for this line
                
                # Check for proper capitalization if we have content
                if len(line_content) > level + 1:
                    title = line_content[level + 1:].strip()
                    if title and title[0].islower():
                        findings.append(
                            Finding(
                                rule_id=self.id,
                                position=Position(line=line_number + 1),
                                message="Heading should start with uppercase letter",
                                severity=self.severity,
                                context=line_content,
                            )
                        )
        
        return findings

class HeadingHierarchyRule(Rule):
    """Rule to check heading hierarchy"""
    id = "HEAD002"
    name = "Heading Hierarchy"
    description = "Checks for proper heading hierarchy"
    severity = Severity.ERROR

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        current_level = 0
        
        for line_number, line in enumerate(document):
            line_content = str(line).strip()
            if line_content.startswith('='):
                level = 0
                for char in line_content:
                    if char != '=':
                        break
                    level += 1
                
                # First heading must be level 1
                if current_level == 0 and level != 1:
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message="First heading must be level 1",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                
                # Can't skip levels
                elif level > current_level + 1:
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Heading level skipped: found h{level} after h{current_level}",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                
                current_level = level
        
        return findings

class MultipleTopLevelHeadingsRule(Rule):
    """Rule to check for multiple top-level headings"""
    id = "HEAD003"
    name = "Multiple Top-Level Headings"
    description = "Checks for multiple top-level headings"
    severity = Severity.ERROR

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        first_h1_line = None
        
        for line_number, line in enumerate(document):
            line_content = str(line).strip()
            if line_content.startswith('= '):  # Level 1 heading
                if first_h1_line is not None:
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Multiple top-level headings found (first at line {first_h1_line + 1})",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                else:
                    first_h1_line = line_number
        
        return findings