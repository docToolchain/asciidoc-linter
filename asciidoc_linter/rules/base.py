# base.py - Base classes for linter rules

from enum import Enum
from typing import List, Union, Optional, Type, Dict
from dataclasses import dataclass

class Severity(Enum):
    """Severity levels for findings"""
    WARNING = "warning"
    ERROR = "error"

@dataclass
class Position:
    """Position in a file"""
    line: int
    column: Optional[int] = None

@dataclass
class Finding:
    """A finding from a rule check"""
    message: str
    severity: Severity
    rule_id: Optional[str] = None
    position: Optional[Position] = None
    file: Optional[str] = None
    context: Optional[str] = None

    def set_file(self, file: str) -> 'Finding':
        """Set the file for this finding and return self"""
        self.file = file
        return self

class Rule:
    """Base class for all rules"""
    id: str = ""
    name: str = ""
    description: str = ""
    severity: Severity = Severity.WARNING
    enabled: bool = True

    def check(self, document: List[Union[str, object]]) -> List[Finding]:
        """
        Check the document against this rule
        
        Args:
            document: List of lines or line objects to check
            
        Returns:
            List of findings
        """
        raise NotImplementedError("Rules must implement check()")

class RuleRegistry:
    """Registry for all available rules"""
    _rules: Dict[str, Type[Rule]] = {}

    @classmethod
    def register(cls, rule_class: Type[Rule]) -> Type[Rule]:
        """
        Register a rule class
        
        Args:
            rule_class: The rule class to register
            
        Returns:
            The registered rule class
        """
        cls._rules[rule_class.id] = rule_class
        return rule_class

    @classmethod
    def get_rule(cls, rule_id: str) -> Optional[Type[Rule]]:
        """
        Get a rule class by its ID
        
        Args:
            rule_id: ID of the rule to get
            
        Returns:
            The rule class if found, None otherwise
        """
        return cls._rules.get(rule_id)

    @classmethod
    def get_all_rules(cls) -> Dict[str, Type[Rule]]:
        """
        Get all registered rules
        
        Returns:
            Dictionary of rule IDs to rule classes
        """
        return cls._rules.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered rules"""
        cls._rules.clear()