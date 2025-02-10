# base_rules.py - Import module for base functionality
"""
This module re-exports the base functionality from base.py for backward compatibility.
"""

from .base import Severity, Position, Finding, Rule, RuleRegistry

__all__ = ["Severity", "Position", "Finding", "Rule", "RuleRegistry"]
