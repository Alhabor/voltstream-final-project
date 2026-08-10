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

    def test_audience_can_follow_without_repository_context(self):
        """The visible deck must define its situation, process, and test language."""
        english_explanations = [
            "Con Edison receives charger information through outside contractors",
            "One clear decision before anyone relies on a new record",
            "The 8 boxes are station ID",
            "no company records were used",
            "Codex and DeepSeek are two families of generative AI models",
            "leave it blank: null + HUMAN_REVIEW",
            "Veto” means one unsafe result disqualified the approach",
        ]
        chinese_explanations = [
            "Con Edison 通过外部承包商和数据公司收集充电桩信息",
            "在任何人依赖新记录之前，先作出一次清晰判断",
            "8 项信息分别是",
            "没有使用公司记录",
            "Codex 和 DeepSeek 是两类生成式 AI 模型",
            "先留空：null + HUMAN_REVIEW（交给人检查）",
            "只要有一次不安全结果就不合格",
        ]
        for text in english_explanations + chinese_explanations:
            self.assertIn(html.escape(text), self.document)

    def test_visible_decision_rules_match_preregistered_thresholds(self):
        judgement = next(
            slide for slide in self.source["slides"] if slide["layout"] == "judgement"
        )
        self.assertEqual(
            [rule["threshold"] for rule in judgement["qualityRules"]],
            ["10 of 10 cases", "at least 90%", "at least 90%", "at least 90%"],
        )
        self.assertEqual(len(judgement["vetoRules"]), 3)
        for phrase in [
            "unsafe approval",
            "critical value not supported",
            "malicious instruction",
            "There is no single average score",
        ]:
            self.assertIn(phrase, self.document)

    def test_experiment_components_are_explained_before_results(self):
        """A first-time audience must see what was compared and what was measured."""
        slides = {slide["id"]: slide for slide in self.source["slides"]}
        self.assertEqual(
            [strategy["code"] for strategy in slides["strategies"]["strategies"]],
            ["S0", "S1", "S2", "S3", "S4", "S5"],
        )
        self.assertEqual(
            [metric["value"] for metric in slides["metrics"]["metricsDetail"]],
            ["80", "56", "8", "10", "9", "3"],
        )
        slide_ids = [slide["id"] for slide in self.source["slides"]]
        self.assertLess(slide_ids.index("strategies"), slide_ids.index("metrics"))
        self.assertLess(slide_ids.index("metrics"), slide_ids.index("system"))
        self.assertLess(slide_ids.index("system"), slide_ids.index("quality"))

    def test_frozen_experiment_values_survive_plain_language_rewrite(self):
        """Changing the narrative must not change the final-v4 evidence."""
        slides = {slide["id"]: slide for slide in self.source["slides"]}
        self.assertEqual(
            [row[1:] for row in slides["quality"]["rows"]],
            [
                ["41.3%", "35.7%", "62.5%", "40%", "0", "Fail"],
                ["97.5%", "100%", "100%", "90%", "0", "Pass"],
                ["95.0%", "66.1%", "87.5%", "80%", "1", "Veto"],
                ["96.3%", "55.4%", "87.5%", "90%", "1", "Veto"],
                ["96.3%", "96.4%", "87.5%", "80%", "1", "Veto"],
                ["95.0%", "66.1%", "87.5%", "80%", "1", "Veto"],
            ],
        )
        self.assertEqual(
            [(row["calls"], row["latency"], row["cost"]) for row in slides["efficiency"]["rows"]],
            [
                ("10", "86.5 s", "Unavailable"),
                ("10", "19.2 s", "$0.000705"),
                ("10", "18.8 s", "$0.000713"),
                ("10", "31.9 s", "$0.002221"),
                ("9", "17.2 s", "$0.000635"),
            ],
        )
        self.assertEqual([value["value"] for value in slides["evg009"]["sourceValues"]], ["8", "6"])
        self.assertIn("null + HUMAN_REVIEW", slides["evg009"]["safeAnswer"])

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
