// README.adoc - Project documentation
= AsciiDoc Linter
:toc: left
:icons: font
:source-highlighter: rouge
:experimental:

image:https://img.shields.io/badge/license-MIT-blue.svg[License: MIT, link=https://opensource.org/licenses/MIT]
image:https://img.shields.io/badge/python-3.8+-blue.svg[Python Version]

A Python-based linter for AsciiDoc files that helps maintain consistent documentation quality and style.

== About

AsciiDoc Linter is a command-line tool that checks your AsciiDoc files for common issues and style violations. It helps maintain consistent documentation by enforcing rules for heading structure, formatting, whitespace, and image usage.

[NOTE]
====
This project was developed with the assistance of an AI language model (GPT-4) as part of an experiment in AI-assisted development. The AI helped design the architecture, implement the code, and create the documentation.
====

== Features

=== Implemented Rules

[cols="1,2,1"]
|===
|Rule ID |Description |Severity

|HEAD001
|Check for proper heading hierarchy (no skipping levels)
|ERROR

|HEAD002
|Verify heading format (spacing and capitalization)
|ERROR/WARNING

|HEAD003
|Detect multiple top-level headers
|ERROR

|BLOCK001
|Check for unterminated blocks (listing, example, sidebar, etc.)
|ERROR

|BLOCK002
|Verify proper spacing around blocks
|WARNING

|WS001
|Check whitespace usage (blank lines, list markers, tabs)
|WARNING

|IMG001
|Verify image attributes and file references
|WARNING/ERROR
|===

=== Planned Rules

* TABLE001: Table formatting consistency
* LINK001: Broken internal references
* FMT001: Markdown-compatible styles detection

== Installation

[source,bash]
----
# Clone the repository
git clone https://github.com/yourusername/asciidoc-linter.git

# Navigate to the project directory
cd asciidoc-linter

# Install the package
pip install .
----

== Usage

=== Basic Usage

[source,bash]
----
# Check a single file
asciidoc-linter document.adoc

# Check multiple files
asciidoc-linter doc1.adoc doc2.adoc

# Check with specific output format
asciidoc-linter --format json document.adoc
----

=== Output Formats

The linter supports three output formats:

* `console` (default): Human-readable output
* `json`: Machine-readable JSON format
* `html`: HTML report format

=== Example Output

[source]
----
Checking file: document.adoc

ERROR: Heading level skipped: found h3 after h1 (line 15)
  === Advanced Topics

WARNING: Heading should start with uppercase letter (line 23)
  == introduction to concepts

ERROR: Unterminated listing block starting (line 45)
  ----

WARNING: Block should be preceded by a blank line (line 67)
  ----

ERROR: Multiple top-level headings found (line 30)
  First heading at line 1: 'Document Title'

WARNING: Missing alt text for image: diagram.png (line 80)
  image::diagram.png[]
----

== Development

=== Running Tests

[source,bash]
----
# Run all tests
python run_tests.py

# Run specific test file
python -m unittest tests/rules/test_heading_rules.py
----

=== Project Structure

[source]
----
asciidoc-linter/
├── asciidoc_linter/
│   ├── __init__.py
│   ├── cli.py
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── heading_rules.py
│   │   ├── block_rules.py
│   │   ├── whitespace_rules.py
│   │   └── image_rules.py
│   ├── parser.py
│   └── reporter.py
├── tests/
│   └── rules/
│       ├── test_heading_rules.py
│       ├── test_block_rules.py
│       ├── test_whitespace_rules.py
│       └── test_image_rules.py
├── docs/
│   ├── requirements.adoc
│   └── block_rules.adoc
├── README.adoc
└── run_tests.py
----

== Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

=== Development Guidelines

1. Write tests for new rules
2. Update documentation
3. Follow Python code style guidelines
4. Add appropriate error messages and context

== License

This project is licensed under the MIT License - see the LICENSE file for details.

== Acknowledgments

* This project was developed with the assistance of GPT-4, demonstrating the potential of AI-assisted development
* Inspired by various linting tools and the need for better AsciiDoc quality control
* Thanks to the AsciiDoc community for their excellent documentation and tools

== Roadmap

1. Phase 1 (Current)
* ✅ Basic heading rules
* ✅ Block structure rules
* ✅ Whitespace rules
* ✅ Image validation
* ⏳ Configuration system

2. Phase 2
* 🔲 Table validation
* 🔲 Link checking
* 🔲 Format rules

3. Phase 3
* 🔲 IDE integration
* 🔲 Git pre-commit hooks
* 🔲 Custom rule development

== Contact

* Project Homepage: https://github.com/yourusername/asciidoc-linter
* Issue Tracker: https://github.com/yourusername/asciidoc-linter/issues