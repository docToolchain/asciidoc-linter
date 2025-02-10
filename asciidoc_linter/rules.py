# rules.py - Base classes for linting rules
"""
Base classes and interfaces for AsciiDoc linting rules
"""

# Import only the base classes and types
from .rules.base import Severity, Position, Finding, Rule, RuleRegistry

# Only export the base classes and types
__all__ = ["Severity", "Position", "Finding", "Rule", "RuleRegistry"]
