# test_rules.py - Tests for rules.py

import unittest
from asciidoc_linter.rules import Severity, Position, Finding, Rule, RuleRegistry


class TestImports(unittest.TestCase):

    def test_import_Severity(self):
        self.assertIsNotNone(Severity)

    def test_import_Position(self):
        self.assertIsNotNone(Position)

    def test_import_Finding(self):
        self.assertIsNotNone(Finding)

    def test_import_Rule(self):
        self.assertIsNotNone(Rule)

    def test_import_RuleRegistry(self):
        self.assertIsNotNone(RuleRegistry)


if __name__ == "__main__":
    unittest.main()
