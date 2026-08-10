import html
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "presentation"


class PresentationContractTests(unittest.TestCase):
    """Keep the generated slide deck aligned with its maintainable source."""

    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((PRESENTATION / "slides.json").read_text(encoding="utf-8"))
        cls.chinese_source = json.loads(
            (PRESENTATION / "slides.zh.json").read_text(encoding="utf-8")
        )
        cls.document = (PRESENTATION / "index.html").read_text(encoding="utf-8")

    def test_slide_count_ids_and_required_order(self):
        slides = self.source["slides"]
        self.assertGreaterEqual(len(slides), 11)
        self.assertLessEqual(len(slides), 13)
        self.assertEqual(len({slide["id"] for slide in slides}), len(slides))
        required = [
            "Problem area and why",
            "Background research and surprising fact",
            "Ideation process",
            "What failed",
            "What might still work",
            "Testing and case evidence",
            "Recommendation",
            "What could go wrong",
        ]
        cursor = -1
        sections = [slide["section"] for slide in slides]
        for section in required:
            cursor = sections.index(section, cursor + 1)

    def test_generated_html_matches_source_titles_and_pages(self):
        slides = self.source["slides"]
        self.assertEqual(len(re.findall(r'<section class="slide"', self.document)), len(slides))
        self.assertEqual(
            len(re.findall(r'<div class="slide-copy" data-copy="en"', self.document)),
            len(slides),
        )
        self.assertEqual(
            len(re.findall(r'<div class="slide-copy" data-copy="zh"', self.document)),
            len(slides),
        )
        for index, (slide, chinese_slide) in enumerate(
            zip(slides, self.chinese_source["slides"]), start=1
        ):
            self.assertIn(f'id="slide-{index}"', self.document)
            self.assertIn(html.escape(slide["title"]), self.document)
            self.assertIn(html.escape(chinese_slide["title"]), self.document)
        self.assertIn(f"1 / {len(slides)}", self.document)

    def test_chinese_translation_matches_slide_structure(self):
        english = self.source["slides"]
        chinese = self.chinese_source["slides"]
        self.assertEqual(len(english), len(chinese))
        for original, translated in zip(english, chinese):
            self.assertEqual(
                (original["id"], original["section"], original["layout"]),
                (translated["id"], translated["section"], translated["layout"]),
            )
            self.assertTrue(translated["sectionLabel"])
            self.assertNotEqual(original["title"], translated["title"])

    def test_core_evidence_and_recommendation_are_present(self):
        required_evidence = [
            "installed_ports",
            "active_ports",
            "null + HUMAN_REVIEW",
            "97.5%",
            "limited, fully human-reviewed pilot",
            "does not support production deployment",
        ]
        for text in required_evidence:
            self.assertIn(text, self.document)

    def test_navigation_hash_and_fullscreen_contract_is_embedded(self):
        for key in [
            "ArrowRight",
            "ArrowDown",
            "PageDown",
            "ArrowLeft",
            "ArrowUp",
            "PageUp",
            "Home",
            "End",
        ]:
            self.assertIn(key, self.document)
        self.assertIn("#slide-", self.document)
        self.assertIn("requestFullscreen", self.document)
        self.assertIn("exitFullscreen", self.document)
        self.assertIn("pointerdown", self.document)
        self.assertIn("wheel", self.document)

    def test_motion_and_print_accessibility_contract_is_embedded(self):
        self.assertIn("prefers-reduced-motion: reduce", self.document)
        self.assertIn("@media print", self.document)
        self.assertIn("page-break-after: always", self.document)
        self.assertIn("aria-live=\"polite\"", self.document)

    def test_language_and_theme_controls_are_embedded(self):
        for text in [
            'id="language"',
            'id="theme"',
            'data-language="en"',
            'data-theme="dark"',
            'data-theme="light"',
            "voltstream-language",
            "voltstream-theme",
        ]:
            self.assertIn(text, self.document)

    def test_html_is_self_contained(self):
        self.assertNotRegex(self.document, r'<script[^>]+src=')
        self.assertNotRegex(self.document, r'<link[^>]+href=')
        self.assertNotIn("http://", self.document)
        self.assertNotIn("https://", self.document)

    def test_build_receipt_matches_final_deck(self):
        receipt = json.loads((PRESENTATION / "BUILD_RECEIPT.json").read_text(encoding="utf-8"))
        self.assertTrue(receipt["ok"])
        self.assertEqual(receipt["slides"], len(self.source["slides"]))
        self.assertTrue(receipt["self_contained"])
        self.assertEqual(receipt["browser"]["content_clipping"], "none detected")
        self.assertEqual(receipt["print"]["pages"], len(self.source["slides"]))
        self.assertEqual(set(receipt["languages"]), {"en", "zh-CN"})
        self.assertEqual(set(receipt["themes"]), {"dark", "light"})


if __name__ == "__main__":
    unittest.main()
