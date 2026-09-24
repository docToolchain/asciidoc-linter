# test_image_rules.py - Tests for image rules in BDD style
"""
Tests for all image-related rules including:
- ImageAttributesRule: Validates image attributes and file existence
  - Checks for alt text presence and quality
  - Validates image file existence
  - Checks for required attributes in block images
  - Handles external URLs differently
"""

import tempfile
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


class TestImagePathResolution(unittest.TestCase):
    """Image targets resolve against the document's directory and :imagesdir:
    like AsciiDoc does, not against the working directory (issue #60)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.doc_dir = Path(self.tmp.name) / "d"
        (self.doc_dir / "img").mkdir(parents=True)
        (self.doc_dir / "img" / "b.png").touch()
        (self.doc_dir / "top.png").touch()

    def _not_found(self, content, base_dir=None):
        rule = ImageAttributesRule(
            base_dir=str(self.doc_dir) if base_dir is None else base_dir
        )
        return [f for f in rule.check(content) if "not found" in f.message]

    def test_imagesdir_relative_to_document_directory(self):
        content = ["= T", ":imagesdir: img", "", "image:b.png[Bild b]"]
        self.assertEqual(self._not_found(content), [])

    def test_without_imagesdir_resolves_against_document_directory(self):
        self.assertEqual(self._not_found(["image::top.png[Top image]"]), [])

    def test_missing_file_is_still_reported(self):
        content = [":imagesdir: img", "image::missing.png[Missing image]"]
        findings = self._not_found(content)
        self.assertEqual(len(findings), 1)
        self.assertIn("missing.png", findings[0].message)

    def test_imagesdir_applies_only_after_its_definition(self):
        content = ["image::b.png[Before]", ":imagesdir: img", "image::b.png[After]"]
        findings = self._not_found(content)
        self.assertEqual([f.position.line for f in findings], [1])

    def test_imagesdir_can_be_unset(self):
        content = [":imagesdir: img", ":imagesdir!:", "image::b.png[Unset dir]"]
        self.assertEqual(len(self._not_found(content)), 1)

    def test_absolute_target_ignores_imagesdir(self):
        target = str(self.doc_dir / "top.png")
        content = [":imagesdir: img", f"image::{target}[Absolute path]"]
        self.assertEqual(self._not_found(content), [])

    def test_url_imagesdir_skips_existence_check(self):
        content = [":imagesdir: https://example.org/img", "image::x.png[Remote]"]
        self.assertEqual(self._not_found(content), [])

    def test_attribute_reference_in_target_skips_existence_check(self):
        self.assertEqual(self._not_found(["image::{logo}[Logo image]"]), [])

    def test_unknown_base_dir_skips_existence_check(self):
        rule = ImageAttributesRule(base_dir=None)
        findings = rule.check(["image::missing.png[]"])
        self.assertEqual([f for f in findings if "not found" in f.message], [])
        self.assertTrue(any("Missing alt text" in f.message for f in findings))

    def test_imagesdir_is_reset_between_documents(self):
        rule = ImageAttributesRule(base_dir=str(self.doc_dir))
        rule.check([":imagesdir: img"])
        findings = rule.check(["image::top.png[Top image]"])
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
