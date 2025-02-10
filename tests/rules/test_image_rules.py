# test_image_rules.py - Tests for image rules in BDD style
"""
Tests for all image-related rules including:
- ImageAttributesRule: Validates image attributes and file existence
  - Checks for alt text presence and quality
  - Validates image file existence
  - Checks for required attributes in block images
  - Handles external URLs differently
"""

import unittest
from pathlib import Path
from asciidoc_linter.rules.image_rules import ImageAttributesRule


class TestImageAttributesRule(unittest.TestCase):
    """Tests for ImageAttributesRule.
    This rule ensures that images have proper attributes and exist in the filesystem.
    """

    def setUp(self):
        """
        Given an ImageAttributesRule instance
        """
        self.rule = ImageAttributesRule()

    def test_inline_image_without_alt(self):
        """
        Given a document with an inline image without alt text
        When the image attributes rule is checked
        Then two findings should be reported
        And one finding should be about missing alt text
        And one finding should be about the missing file
        """
        # Given: A document with an inline image without alt text
        content = ["Here is an image:test.png[] without alt text."]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Two findings should be reported
        self.assertEqual(
            len(findings), 2, "Should report both missing alt text and file not found"
        )

        # And: One finding should be about missing alt text
        self.assertTrue(
            any("Missing alt text" in f.message for f in findings),
            "Should report missing alt text",
        )

    def test_inline_image_with_alt(self):
        """
        Given a document with an inline image with alt text
        When the image attributes rule is checked
        Then only one finding should be reported
        And the finding should be about the missing file
        """
        # Given: A document with an inline image with alt text
        content = [
            "Here is an image:test.png[A good description of the image] with alt text."
        ]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Only one finding should be reported
        self.assertEqual(len(findings), 1, "Should only report file not found")

    def test_block_image_complete(self):
        """
        Given a document with a complete block image
        When the image attributes rule is checked
        Then only one finding should be reported
        And the finding should be about the missing file
        """
        # Given: A document with a complete block image
        content = ["image::test.png[Alt text for image, title=Image Title, width=500]"]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Only one finding should be reported
        self.assertEqual(
            len(findings),
            1,
            "Should only report file not found for complete block image",
        )

    def test_block_image_missing_attributes(self):
        """
        Given a document with a block image missing attributes
        When the image attributes rule is checked
        Then three findings should be reported
        And findings should include missing alt text, title, size, and file
        """
        # Given: A document with a block image missing attributes
        content = ["image::test.png[]"]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Three findings should be reported
        self.assertEqual(
            len(findings),
            3,
            "Should report missing alt, title, size and file not found",
        )

    def test_short_alt_text(self):
        """
        Given a document with an image having too short alt text
        When the image attributes rule is checked
        Then a finding about short alt text should be reported
        """
        # Given: A document with an image having short alt text
        content = ["image:test.png[img]"]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: A finding about short alt text should be reported
        self.assertTrue(
            any("Alt text too short" in f.message for f in findings),
            "Should report alt text being too short",
        )

    def test_external_url(self):
        """
        Given a document with an external image URL
        When the image attributes rule is checked
        Then no findings should be reported
        Because external URLs are not checked for existence
        """
        # Given: A document with an external image URL
        content = ["image:https://example.com/test.png[External image]"]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: No findings should be reported
        self.assertEqual(
            len(findings), 0, "External URLs should not be checked for existence"
        )

    def test_multiple_images_per_line(self):
        """
        Given a document with multiple images in one line
        When the image attributes rule is checked
        Then appropriate findings should be reported for each image
        """
        # Given: A document with multiple images in one line
        content = [
            "Here are two images: image:test1.png[] and image:test2.png[Good alt text]"
        ]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Three findings should be reported
        self.assertEqual(
            len(findings),
            3,
            "Should report missing alt + not found for first image and not found for second",
        )

    def test_attribute_parsing(self):
        """
        Given a document with complex image attributes
        When the image attributes rule is checked
        Then only the missing file should be reported
        And complex attributes should be parsed correctly
        """
        # Given: A document with complex image attributes
        content = [
            'image::test.png[Alt text, title="Complex, title with, commas", width=500]'
        ]

        # When: We check the line for image issues
        findings = []
        for i, line in enumerate(content):
            findings.extend(self.rule.check_line(line, i, content))

        # Then: Only one finding should be reported
        self.assertEqual(
            len(findings),
            1,
            "Should only report file not found for image with complex attributes",
        )

    def test_valid_local_image(self):
        """
        Given a document with a reference to an existing local image
        And the image file exists
        When the image attributes rule is checked
        Then no findings should be reported
        """
        # Given: A temporary test image file
        test_image = Path("test_image.png")
        test_image.touch()

        try:
            # And: A document referencing the existing image
            content = [
                'image::test_image.png[Valid test image, title="Test Image", width=500]'
            ]

            # When: We check the line for image issues
            findings = []
            for i, line in enumerate(content):
                findings.extend(self.rule.check_line(line, i, content))

            # Then: No findings should be reported
            self.assertEqual(
                len(findings),
                0,
                "Valid local image with proper attributes should not produce findings",
            )
        finally:
            # Clean up: Remove the temporary test image
            test_image.unlink()


if __name__ == "__main__":
    unittest.main()
