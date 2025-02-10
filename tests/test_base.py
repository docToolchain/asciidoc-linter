# test_base.py - Tests for base functionality
"""Tests for the base functionality of the rule system"""

import unittest
from typing import Dict, Any, List
from asciidoc_linter.rules.base import Severity, Position, Finding, Rule, RuleRegistry


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

    def test_severity_string(self):
        """Test string representation of Severity"""
        self.assertEqual(str(Severity.ERROR), "error")
        self.assertEqual(str(Severity.WARNING), "warning")
        self.assertEqual(str(Severity.INFO), "info")


class TestPosition(unittest.TestCase):
    """Test the Position dataclass"""

    def test_position_with_line_only(self):
        """Test Position with line number only"""
        pos = Position(line=10)
        self.assertEqual(pos.line, 10)
        self.assertIsNone(pos.column)
        self.assertEqual(str(pos), "line 10")

    def test_position_with_line_and_column(self):
        """Test Position with line and column"""
        pos = Position(line=10, column=5)
        self.assertEqual(pos.line, 10)
        self.assertEqual(pos.column, 5)
        self.assertEqual(str(pos), "line 10, column 5")

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
        self.assertEqual(finding.line_number, 10)

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
        self.assertEqual(finding.line_number, 10)

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

        id = "TEST001"
        name = "Test Rule"
        description = "Rule for testing"
        severity = Severity.WARNING

        def check(self, content: str) -> List[Finding]:
            """Test implementation that finds 'ERROR' in content"""
            findings = []
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "ERROR" in line:
                    findings.append(
                        self.create_finding(
                            line_number=i + 1, message=f"Found ERROR in line {i+1}"
                        )
                    )
            return findings

        def check_line_content(self, line: str, line_number: int) -> List[Finding]:
            """Test implementation for line content checking"""
            if "WARNING" in line:
                return [self.create_finding(line_number, "Found WARNING")]
            return []

        def check_line_context(
            self, line: str, line_number: int, prev_line: str, next_line: str
        ) -> List[Finding]:
            """Test implementation for line context checking"""
            if prev_line and line == prev_line:
                return [self.create_finding(line_number, "Repeated line")]
            return []

    def setUp(self):
        """Set up test data"""
        self.rule = self.ConcreteRule()

    def test_rule_attributes(self):
        """Test rule attributes"""
        self.assertEqual(self.rule.id, "TEST001")
        self.assertEqual(self.rule.name, "Test Rule")
        self.assertEqual(self.rule.description, "Rule for testing")
        self.assertEqual(self.rule.severity, Severity.WARNING)

    def test_check_method(self):
        """Test check method"""
        content = "This line has an ERROR\nThis line is fine\nAnother ERROR here"
        findings = self.rule.check(content)

        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0].message, "Found ERROR in line 1")
        self.assertEqual(findings[0].severity, Severity.WARNING)
        self.assertEqual(findings[0].position.line, 1)
        self.assertEqual(findings[1].message, "Found ERROR in line 3")

    def test_check_line(self):
        """Test check_line method"""
        content = [
            "First line",
            "Line with WARNING",
            "Line with WARNING",  # Repeated line
            "Last line",
        ]

        # Test line with warning
        findings = self.rule.check_line(content[1], 1, content)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].message, "Found WARNING")

        # Test repeated line
        findings = self.rule.check_line(content[2], 2, content)
        self.assertEqual(len(findings), 2)  # WARNING + repeated line
        self.assertTrue(any(f.message == "Repeated line" for f in findings))

    def test_base_rule_methods(self):
        """Test that base Rule class methods raise NotImplementedError"""
        base_rule = Rule()
        with self.assertRaises(NotImplementedError):
            base_rule.check("some content")


class TestRuleRegistry(unittest.TestCase):
    """Test the RuleRegistry"""

    class TestRule1(Rule):
        """First test rule"""

        id = "TEST001"

    class TestRule2(Rule):
        """Second test rule"""

        id = "TEST002"

    def setUp(self):
        """Set up test data"""
        # Clear registry before each test
        RuleRegistry._rules = {}

    def test_register_rule(self):
        """Test rule registration"""
        RuleRegistry.register_rule(self.TestRule1)
        self.assertIn(self.TestRule1.__name__, RuleRegistry._rules)
        self.assertEqual(RuleRegistry._rules[self.TestRule1.__name__], self.TestRule1)

    def test_get_rule(self):
        """Test getting a rule by name"""
        RuleRegistry.register_rule(self.TestRule1)
        rule_class = RuleRegistry.get_rule(self.TestRule1.__name__)
        self.assertEqual(rule_class, self.TestRule1)

    def test_get_all_rules(self):
        """Test getting all registered rules"""
        RuleRegistry.register_rule(self.TestRule1)
        RuleRegistry.register_rule(self.TestRule2)
        rules = RuleRegistry.get_all_rules()
        self.assertEqual(len(rules), 2)
        self.assertIn(self.TestRule1, rules)
        self.assertIn(self.TestRule2, rules)

    def test_create_all_rules(self):
        """Test creating instances of all rules"""
        RuleRegistry.register_rule(self.TestRule1)
        RuleRegistry.register_rule(self.TestRule2)
        instances = RuleRegistry.create_all_rules()
        self.assertEqual(len(instances), 2)
        self.assertTrue(any(isinstance(rule, self.TestRule1) for rule in instances))
        self.assertTrue(any(isinstance(rule, self.TestRule2) for rule in instances))

    def test_get_nonexistent_rule(self):
        """Test getting a rule that doesn't exist"""
        with self.assertRaises(KeyError):
            RuleRegistry.get_rule("NonexistentRule")


if __name__ == "__main__":
    unittest.main()
