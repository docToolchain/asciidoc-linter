# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note:** This file is maintained in English.

## Available Tools

- **dacli**: Available in the shell for working with AsciiDoc documents (docToolchain CLI)

## Project Overview

AsciiDoc Linter is a Python-based CLI tool for checking AsciiDoc files for common issues and style violations. Part of the docToolchain project.

**Version:** 0.1.0
**Python:** 3.8+

## Common Commands

```bash
# Setup development environment
./setup_test_environment.sh

# Run all tests
python -m pytest

# Run a single test file
python -m pytest tests/rules/test_heading_rules.py

# Run a specific test
python -m pytest tests/rules/test_heading_rules.py::test_function_name -v

# Run tests with HTML coverage report
python run_tests_html.py

# Check code formatting
python -m black --check .

# Auto-format code
python -m black .

# Run flake8 linter
python -m flake8 .

# Install package locally
pip install -e ".[test]"

# Run the linter
asciidoc-linter document.adoc
asciidoc-linter --format json document.adoc
```

## Architecture

### Core Flow
`CLI (cli.py)` → `AsciiDocLinter (linter.py)` → `Rules` → `Finding` → `Reporter`

### Key Components

- **cli.py**: Entry point, argument parsing, reporter selection
- **linter.py**: `AsciiDocLinter` class orchestrates parsing and rule checking, supports YAML config
- **parser.py**: `AsciiDocParser` creates internal representation (`Header`, `CodeBlock`, `Table` elements)
- **reporter.py**: Output formatters (`ConsoleReporter`, `JsonReporter`, `HtmlReporter`) and `LintReport` container

### Rules System (`asciidoc_linter/rules/`)

- **base.py**: Core classes - `Rule` (base class), `Finding` (violation), `Severity` (enum: ERROR/WARNING/INFO), `Position`, `RuleRegistry`
- **heading_rules.py**: HEAD001 (hierarchy), HEAD002 (format), HEAD003 (multiple top-level)
- **block_rules.py**: BLOCK001 (unterminated), BLOCK002 (spacing)
- **whitespace_rules.py**: WS001 (whitespace issues)
- **image_rules.py**: IMG001 (attributes/references)
- **table_rules.py**: TABLE001 (formatting) - beta status

### Adding New Rules

1. Create rule class extending `Rule` in appropriate `*_rules.py` file
2. Set `id`, `name`, `description`, `severity` class attributes
3. Implement `check(document)` method returning `List[Finding]`
4. Register rule in `AsciiDocLinter.__init__()` in `linter.py`
5. Add tests in `tests/rules/`

### Finding Creation Pattern
```python
self.create_finding(
    line_number=line_num,
    message="Description of issue",
    column=optional_column,
    context={"key": "value"}
)
```

## Code Style

- Formatter: Black (line length 88)
- Linter: flake8 (ignores E203, W503, E501)
- Test coverage target: 90%+

## CI Pipeline

GitHub Actions runs on push/PR:
- `run_tests`: pytest
- `run_black`: formatting check
- `run_flake8`: linting
- `self_test_readme`: lints README.adoc with the tool itself

## Important Implementation Details

### Parser vs Raw Lines
The linter has two data representations:
- **Parsed elements**: `AsciiDocParser.parse()` returns `List[AsciiDocElement]` (Headers only currently)
- **Raw lines**: `content.splitlines()` returns `List[str]`

Most rules work with parsed elements, but **WhitespaceRule requires raw lines**. The linter handles this in `lint_string()`:
```python
if isinstance(rule, WhitespaceRule):
    rule_findings = rule.check(raw_lines)
else:
    rule_findings = rule.check(document)
```

### AsciiDoc Block Delimiters
Block delimiters look similar to other syntax but must be handled differently:
- `====` - Example/Note block delimiter (NOT a section title)
- `----` - Listing/source block delimiter (NOT a list marker)
- `****` - Sidebar block delimiter (NOT a list marker)
- `....` - Literal block delimiter (NOT a list marker)

The parser excludes these by checking for content after `=` characters:
```python
rest = line[level:]
if rest.startswith(" ") and rest.strip():  # Has " Title" after ===
    elements.append(Header(...))
```

### Testing WhitespaceRule
When testing `WhitespaceRule.check()`, always pass a list of strings, not a raw multi-line string:
```python
# Correct
findings = rule.check(content.splitlines())

# Wrong - iterates over characters, not lines
findings = rule.check(content)
```

### Nested List Markers
AsciiDoc supports nested lists with repeated markers (`**`, `***`). The whitespace rule counts consecutive markers before checking for space.
