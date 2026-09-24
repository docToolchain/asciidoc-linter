# test_linter_rule_dispatch.py - Rules must fire through the linter entry point
"""
Regression tests: the CLI calls AsciiDocLinter.lint(), which dispatches to
the rules. These tests go through that path instead of calling rules directly.
"""

import pytest

from asciidoc_linter.linter import AsciiDocLinter


def rule_ids_for(tmp_path, content):
    """Lint content via the same entry point the CLI uses and return rule IDs"""
    doc = tmp_path / "doc.adoc"
    doc.write_text(content, encoding="utf-8")
    report = AsciiDocLinter().lint([str(doc)])
    return [finding.rule_id for finding in report.findings]


@pytest.mark.parametrize(
    "content, rule_id",
    [
        ("= T\n\n== Eins\n\n==== Sprung\n\ntext\n", "HEAD001"),
        ("= T\n\n== eins klein\n\ntext\n", "HEAD002"),
        ("= T\n\n== Eins\n\n----\ncode\n", "BLOCK001"),
        ("= T\n\n## Markdown\n", "FMT004"),
        ("= T\n\nimage::missing.png[]\n", "IMG001"),
    ],
)
def test_rule_fires_through_linter(tmp_path, content, rule_id):
    assert rule_id in rule_ids_for(tmp_path, content)


def test_example_block_delimiter_is_not_a_heading(tmp_path):
    content = "= T\n\n== Eins\n\n====\nExample\n====\n"
    assert rule_ids_for(tmp_path, content) == []


@pytest.mark.parametrize(
    "prefix",
    ["[source,python]\n", ".Listing title\n", ".Listing title\n[source,python]\n"],
)
def test_block_attribute_and_title_lines_belong_to_block(tmp_path, prefix):
    content = "= T\n\n== Eins\n\n" + prefix + "----\nx = 1\n----\n"
    assert "BLOCK002" not in rule_ids_for(tmp_path, content)
