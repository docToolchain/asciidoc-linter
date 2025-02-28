# parser.py - AsciiDoc parser

from typing import List, Optional, Union
from dataclasses import dataclass

@dataclass
class AsciiDocElement:
    """Base class for AsciiDoc elements"""
    line_number: int
    content: str

@dataclass
class Header(AsciiDocElement):
    """Represents an AsciiDoc header"""
    level: int

@dataclass
class CodeBlock(AsciiDocElement):
    """Represents a code block"""
    language: Optional[str]

@dataclass
class Table(AsciiDocElement):
    """Represents a table"""
    columns: int

class AsciiDocParser:
    """Parser for AsciiDoc content"""

    def parse(self, content: str) -> List[str]:
        """
        Parse AsciiDoc content into lines
        
        Args:
            content: The AsciiDoc content to parse
            
        Returns:
            List of lines from the content
        """
        return content.splitlines()