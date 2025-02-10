# test_base_rules.py - Tests for base rule classes
"""Tests for the base rule classes"""

import unittest
from typing import Dict, Any
from asciidoc_linter.rules.base_rules import Severity, Position, Finding, Rule


class TestSeverity(unittest.TestCase):
    """Test the Severity enum"""

    def test_severity_values(self):
        """Test that Severity enum has correct values"""
        self.assertEqual(Severity.ERROR.value, "error")
        self.assertEqual(Severity.WARNING.value, "warning")
        self.assertEqual(Severity.INFO.value, "info")

    def test_severity_comparison(self):
        """Test that Severity values can be compared"""
        self.assertNotEqual(Severity.INFO, Severity.ERROR)
        self.assertEqual(Severity.WARNING, Severity.WARNING)
        self.assertTrue(isinstance(Severity.ERROR, Severity))


class TestPosition(unittest.TestCase):
    """Test the Position dataclass"""

    def test_position_with_line_only(self):
        """Test Position with line number only"""
        pos = Position(line=10)
        self.assertEqual(pos.line, 10)
        self.assertIsNone(pos.column)

    def test_position_with_line_and_column(self):
        """Test Position with line and column"""
        pos = Position(line=10, column=5)
        self.assertEqual(pos.line, 10)
        self.assertEqual(pos.column, 5)

    def test_position_equality(self):
        """Test Position equality comparison"""
        pos1 = Position(line=10, column=5)
        pos2 = Position(line=10, column=5)
        pos3 = Position(line=10, column=6)

        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)


class TestFinding(unittest.TestCase):
    """Test the Finding dataclass"""

    def setUp(self):
        """Set up test data"""
        self.position = Position(line=10, column=5)
        self.context: Dict[str, Any] = {"key": "value"}

    def test_finding_minimal(self):
        """Test Finding creation with minimal attributes"""
        finding = Finding(
            message="Test message", severity=Severity.WARNING, position=self.position
        )

        self.assertEqual(finding.message, "Test message")
        self.assertEqual(finding.severity, Severity.WARNING)
        self.assertEqual(finding.position, self.position)
        self.assertIsNone(finding.rule_id)
        self.assertIsNone(finding.context)

    def test_finding_complete(self):
        """Test Finding creation with all attributes"""
        finding = Finding(
            message="Test message",
            severity=Severity.ERROR,
            position=self.position,
            rule_id="TEST001",
            context=self.context,
        )

        self.assertEqual(finding.message, "Test message")
        self.assertEqual(finding.severity, Severity.ERROR)
        self.assertEqual(finding.position, self.position)
        self.assertEqual(finding.rule_id, "TEST001")
        self.assertEqual(finding.context, self.context)

    def test_finding_equality(self):
        """Test Finding equality comparison"""
        finding1 = Finding(
            message="Test message",
            severity=Severity.WARNING,
            position=self.position,
            rule_id="TEST001",
        )
        finding2 = Finding(
            message="Test message",
            severity=Severity.WARNING,
            position=self.position,
            rule_id="TEST001",
        )
        finding3 = Finding(
            message="Different message",
            severity=Severity.WARNING,
            position=self.position,
            rule_id="TEST001",
        )

        self.assertEqual(finding1, finding2)
        self.assertNotEqual(finding1, finding3)


class TestRule(unittest.TestCase):
    """Test the Rule base class"""

    class ConcreteRule(Rule):
        """Concrete implementation of Rule for testing"""

        rule_id = "TEST001"

        def check(self, content: str):
            """Test implementation that finds 'ERROR' in content"""
            findings = []
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "ERROR" in line:
                    findings.append(
                        Finding(
                            message=f"Found ERROR in line {i+1}",
                            severity=Severity.ERROR,
                            position=Position(line=i + 1),
                            rule_id=self.rule_id,
                        )
                    )
            return findings

    def setUp(self):
        """Set up test data"""
        self.rule = self.ConcreteRule()

    def test_rule_id(self):
        """Test rule_id attribute"""
        self.assertEqual(self.rule.rule_id, "TEST001")

        # Test default rule_id
        base_rule = Rule()
        self.assertEqual(base_rule.rule_id, "BASE")

    def test_check_method_concrete(self):
        """Test check method in concrete implementation"""
        content = "This line has an ERROR\nThis line is fine\nAnother ERROR here"
        findings = self.rule.check(content)

        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0].message, "Found ERROR in line 1")
        self.assertEqual(findings[0].severity, Severity.ERROR)
        self.assertEqual(findings[0].position.line, 1)
        self.assertEqual(findings[1].message, "Found ERROR in line 3")

    def test_check_method_base(self):
        """Test check method in base class raises NotImplementedError"""
        base_rule = Rule()
        with self.assertRaises(NotImplementedError):
            base_rule.check("some content")


if __name__ == "__main__":
    unittest.main()
