# image_rules.py - Rules for checking image attributes and references

import os
import re
from typing import List, Dict, Any, Optional, Union
from .base import Rule, Finding, Severity, Position, mask_verbatim_blocks

# URI schemes (https:, ftp:, file:, data:, ...). At least two characters, so
# Windows drive letters (C:/img.png) still count as local paths.
URL_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]+:")
# :imagesdir: value (set) and :imagesdir!: / :!imagesdir: (unset)
IMAGESDIR_SET_PATTERN = re.compile(r"^:imagesdir:\s*(.*?)\s*$")
IMAGESDIR_UNSET_PATTERN = re.compile(r"^:(?:imagesdir!|!imagesdir):\s*$")


class ImageAttributesRule(Rule):
    """Rule to check image attributes and references."""

    id = "IMG001"
    name = "Image Attributes Check"
    description = "Checks for proper image attributes and file references"
    severity = Severity.WARNING

    def __init__(self, base_dir: Optional[str] = "."):
        super().__init__()
        self.current_line = 0
        self.current_context = ""
        # Directory that relative image targets resolve against (the
        # document's directory). None means unknown: skip the existence check.
        self.base_dir = base_dir
        self.imagesdir = ""

    def check(self, document: List[Any]) -> List[Finding]:
        """Check the entire document for image-related issues."""
        findings = []
        self.imagesdir = ""
        document = mask_verbatim_blocks(document)
        for i, line in enumerate(document):
            findings.extend(self.check_line(line, i, document))
        return findings

    def _track_imagesdir(self, line: str) -> None:
        """Follow :imagesdir: attribute entries in document order."""
        stripped = line.strip()
        if IMAGESDIR_UNSET_PATTERN.match(stripped):
            self.imagesdir = ""
            return
        match = IMAGESDIR_SET_PATTERN.match(stripped)
        if match:
            self.imagesdir = match.group(1)

    def _resolve_image_path(self, target: str) -> Optional[str]:
        """Resolve a target like AsciiDoc does, or None if it can't be checked.

        Relative targets resolve against imagesdir, which itself is relative
        to the document's directory.
        """
        if self.base_dir is None or URL_PATTERN.match(target) or "{" in target:
            return None
        if os.path.isabs(target):
            return target
        if URL_PATTERN.match(self.imagesdir) or "{" in self.imagesdir:
            return None
        return os.path.join(self.base_dir, self.imagesdir, target)

    def _check_image_path(self, path: str) -> List[Finding]:
        """Check if the image file exists and is accessible."""
        findings = []

        # Clean up path
        path = path.strip()

        resolved = self._resolve_image_path(path)
        if resolved is None:
            return []

        # Check if file exists
        if not os.path.isfile(resolved):
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=self.current_line + 1),
                    message=f"Image file not found: {path}",
                    severity=self.severity,
                    context=self.current_context,
                )
            )

        return findings

    def _check_attributes(
        self, attributes: Dict[str, str], image_type: str, path: str
    ) -> List[Finding]:
        """Check image attributes for completeness and validity."""
        findings = []

        # Check for alt text
        if "alt" not in attributes or not attributes["alt"]:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=self.current_line + 1),
                    message=f"Missing alt text for {image_type} image: {path}",
                    severity=self.severity,
                    context=self.current_context,
                )
            )
        elif len(attributes["alt"]) < 5:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=self.current_line + 1),
                    message=f"Alt text too short for {image_type} image: {path}",
                    severity=Severity.INFO,
                    context=self.current_context,
                )
            )

        # For block images, check additional attributes
        if image_type == "block" and not attributes:
            findings.append(
                Finding(
                    rule_id=self.id,
                    position=Position(line=self.current_line + 1),
                    message=f"Missing required attributes for block image: {path}",
                    severity=self.severity,
                    context=self.current_context,
                )
            )

        return findings

    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """Parse image attributes from string."""
        attributes = {}

        # Remove brackets if present
        attr_string = attr_string.strip("[]")
        if not attr_string:
            return attributes

        # Split by comma, but respect quotes
        parts = []
        current = []
        in_quotes = False

        for char in attr_string:
            if char == '"':
                in_quotes = not in_quotes
                current.append(char)
            elif char == "," and not in_quotes:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            parts.append("".join(current).strip())

        # Process parts
        for i, part in enumerate(parts):
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                value = value.strip().strip('"')
                attributes[key.strip()] = value
            elif i == 0:  # First part without = is alt text
                attributes["alt"] = part

        return attributes

    def check_line(
        self, line: Union[str, Any], line_number: int, context: List[Any]
    ) -> List[Finding]:
        """Check a line for image-related issues."""
        findings = []
        self.current_line = line_number

        # Handle Header objects and other non-string types
        if hasattr(line, "content"):
            line_content = line.content
        else:
            line_content = str(line)

        self.current_context = line_content
        self._track_imagesdir(line_content)

        # Check for block images
        block_image_match = re.match(
            r"image::([^[]+)(?:\[(.*)\])?", line_content.strip()
        )
        if block_image_match:
            path = block_image_match.group(1)
            attributes = self._parse_attributes(block_image_match.group(2) or "")

            findings.extend(self._check_image_path(path))
            findings.extend(self._check_attributes(attributes, "block", path))
            return findings

        # Check for inline images
        for inline_match in re.finditer(r"image:([^[]+)(?:\[(.*?)\])?", line_content):
            path = inline_match.group(1)
            attributes = self._parse_attributes(inline_match.group(2) or "")

            findings.extend(self._check_image_path(path))
            findings.extend(self._check_attributes(attributes, "inline", path))

        return findings
