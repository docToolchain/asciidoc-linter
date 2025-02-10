# __init__.py - Rules package initialization
"""
This module exports only the base classes and types for rules.
For concrete rule implementations, import from .concrete_rules
"""

from .base import Rule, Finding, Severity, Position, RuleRegistry

__all__ = ["Rule", "Finding", "Severity", "Position", "RuleRegistry"]
