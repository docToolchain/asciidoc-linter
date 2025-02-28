# image_rules.py - Rules for checking images in AsciiDoc files

import re
from pathlib import Path
from typing import List, Union
from .base import Rule, Finding, Severity, Position

class ImageAttributesRule(Rule):
    """Rule to check image attributes"""
    id = "IMG001"
    name = "Image Attributes"
    description = "Checks for proper image attributes"
    severity = Severity.WARNING

    def __init__(self):
        super().__init__()
        self.image_pattern = re.compile(r'image::([^[]+)(?:\[(.*?)\])?')

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        if not self.enabled:
            return []
            
        findings = []
        
        for line_number, line in enumerate(document):
            line_content = str(line)
            
            # Find image macros
            for match in self.image_pattern.finditer(line_content):
                path = match.group(1)
                attrs = match.group(2) or ""
                
                # Check for alt text
                if not any(attr.startswith('alt=') for attr in attrs.split(',')):
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Missing alt text for image: {path}",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                
                # Check file extension
                if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Invalid image file extension: {path}",
                            severity=self.severity,
                            context=line_content,
                        )
                    )
                
                # Check for width/height attributes
                if not any(attr.startswith(('width=', 'height=')) for attr in attrs.split(',')):
                    findings.append(
                        Finding(
                            rule_id=self.id,
                            position=Position(line=line_number + 1),
                            message=f"Missing width/height attributes for image: {path}",
                            severity=Severity.WARNING,
                            context=line_content,
                        )
                    )
        
        return findings