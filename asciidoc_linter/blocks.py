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

from typing import List, Optional, Set, Union

# Characters whose repeated run delimits a verbatim block: listing (-),
# literal (.) and passthrough (+). Example (=), sidebar (*) and quote (_)
# blocks hold parseable content and are intentionally excluded.
VERBATIM_DELIMITER_CHARS = "-.+"

# Minimum run length AsciiDoc requires for a block delimiter.
MIN_DELIMITER_LENGTH = 4


def _line_text(line: Union[str, object]) -> str:
    """Return the raw text of a line, whether it is a str or an element."""
    if hasattr(line, "content"):
        return line.content
    return str(line)


def _verbatim_delimiter(stripped: str) -> Optional[str]:
    """Return the delimiter string if ``stripped`` is a verbatim block delimiter.

    A delimiter is a run of at least four identical characters from
    ``VERBATIM_DELIMITER_CHARS`` and nothing else (e.g. ``----``, ``--------``,
    ``....``). Returns ``None`` otherwise.
    """
    if len(stripped) < MIN_DELIMITER_LENGTH:
        return None
    first = stripped[0]
    if first in VERBATIM_DELIMITER_CHARS and stripped == first * len(stripped):
        return stripped
    return None


def find_code_block_content_lines(lines: List[Union[str, object]]) -> Set[int]:
    """Return the 0-based indices of lines that fall *inside* a verbatim block.

    Only the lines between an opening delimiter and its matching closing
    delimiter are returned; the delimiter lines themselves are document
    structure and are excluded. AsciiDoc requires the closing delimiter to be
    identical to the opening one (same character and length), so a shorter or
    longer run inside the block is treated as content. An unterminated block
    extends to the end of the document.
    """
    content_lines: Set[int] = set()
    delimiter = None  # exact delimiter string that opened the block, or None
    for index, line in enumerate(lines):
        stripped = _line_text(line).strip()
        if delimiter is None:
            if _verbatim_delimiter(stripped):
                delimiter = stripped
            continue
        # Inside a block: only an identical delimiter closes it; anything else
        # is verbatim content that must be exempt from linting.
        if stripped == delimiter:
            delimiter = None
        else:
            content_lines.add(index)
    return content_lines
