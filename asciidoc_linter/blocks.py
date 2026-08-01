# blocks.py - Shared helpers for detecting AsciiDoc verbatim blocks
"""
Shared helper for locating the content of AsciiDoc verbatim blocks.

Content inside listing (``----``), literal (``....``) and passthrough
(``++++``) blocks is verbatim: it represents example or source text rather
than real AsciiDoc structure, so lint rules must not be applied to it.
Centralising the detection here keeps every rule (and the parser) consistent
and avoids the drift that caused issues #52 and #54, where some rules skipped
code blocks and others did not.
"""

from typing import List, Set, Union

# Delimiters whose enclosed content is verbatim and must not be linted.
VERBATIM_BLOCK_DELIMITERS = {"----", "....", "++++"}


def _line_text(line: Union[str, object]) -> str:
    """Return the raw text of a line, whether it is a str or an element."""
    if hasattr(line, "content"):
        return line.content
    return str(line)


def find_code_block_content_lines(lines: List[Union[str, object]]) -> Set[int]:
    """Return the 0-based indices of lines that fall *inside* a verbatim block.

    Only the lines between an opening delimiter and its matching closing
    delimiter are returned; the delimiter lines themselves are document
    structure and are excluded. An unterminated block extends to the end of
    the document.
    """
    content_lines: Set[int] = set()
    delimiter = None  # delimiter that opened the current block, or None
    for index, line in enumerate(lines):
        stripped = _line_text(line).strip()
        if delimiter is None:
            if stripped in VERBATIM_BLOCK_DELIMITERS:
                delimiter = stripped
            continue
        # Inside a block: a matching delimiter closes it; anything else is
        # verbatim content that must be exempt from linting.
        if stripped == delimiter:
            delimiter = None
        else:
            content_lines.add(index)
    return content_lines
