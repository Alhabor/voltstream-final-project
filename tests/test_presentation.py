import html
import hashlib
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
        cls.evidence = json.loads(
            (PRESENTATION / "evidence.json").read_text(encoding="utf-8")
        )

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
            "small trial—a pilot",
            "not ready for live company use",
        ]
        for text in required_evidence:
            self.assertIn(text, self.document)

    def test_audience_can_follow_without_repository_context(self):
        """The visible deck must define its situation, process, and test language."""
        english_explanations = [
            "Con Edison is a company that delivers electricity",
            "One connection that can charge one vehicle at a time",
            "8 is not automatically the number working now",
            "The 8 facts are a site ID (unique label)",
            "no company records were used",
            "Codex and DeepSeek are two kinds of AI systems",
            "leave it blank and send it to a person (saved as null + HUMAN_REVIEW)",
            "One such event caused a veto",
        ]
        chinese_explanations = [
            "Con Edison 是一家向用户输送电力的公司",
            "一次能够连接并为一辆车充电的接口",
            "8 不一定是现在可用的数量",
            "8 项信息是：站点 ID（唯一标签）",
            "没有使用公司记录",
            "Codex 和 DeepSeek 是本项目比较的两种 AI 系统",
            "留空并交给人（保存结果写作 null + HUMAN_REVIEW）",
            "出现一次就会导致否决",
        ]
        for text in english_explanations + chinese_explanations:
            self.assertIn(html.escape(text), self.document)

    def test_first_use_of_audience_terms_is_explained_or_removed(self):
        """Protect the zero-background English narrative from unexplained jargon."""
        slides = {slide["id"]: slide for slide in self.source["slides"]}
        slide_ids = [slide["id"] for slide in self.source["slides"]]
        self.assertLess(slide_ids.index("charger-basics"), slide_ids.index("evg009"))
        self.assertEqual(
            [term["name"] for term in slides["charger-basics"]["terms"]],
            ["Charging site", "Charger", "Charging port"],
        )
        prototype_text = json.dumps(slides["prototype"], ensure_ascii=False)
        for term in ["ACCEPT", "HUMAN_REVIEW", "REJECT"]:
            self.assertIn(term, prototype_text)
        case_text = json.dumps(slides["evg009"], ensure_ascii=False)
        for explanation in [
            "installed_ports means all physical ports installed",
            "active_ports means ports active now",
            "Codex and DeepSeek are two kinds of AI systems",
            "saved as null + HUMAN_REVIEW",
        ]:
            self.assertIn(explanation, case_text)
        audience_source = json.dumps(self.source["slides"], ensure_ascii=False)
        for unexplained_term in [
            "CSV",
            "JSON",
            "API record",
            "Simple baseline",
            "Open-weight path",
            "Closed-model path",
            "prompt guardrails",
            "deterministic post-processing",
            "production deployment",
        ]:
            self.assertNotIn(unexplained_term, audience_source)

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
            "should have gone to a person or stopped",
            "important number that did not appear",
            "hidden in the submitted data",
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

    def test_pipeline_comparison_and_core_case_have_bounded_animation(self):
        """The explanatory animation must preserve the final static evidence."""
        english = {slide["id"]: slide for slide in self.source["slides"]}
        chinese = {slide["id"]: slide for slide in self.chinese_source["slides"]}
        for slides in [english, chinese]:
            pipeline = slides["prototype"]
            self.assertEqual(pipeline["layout"], "pipeline-compare")
            self.assertEqual(len(pipeline["manualLane"]["steps"]), 4)
            self.assertEqual(len(pipeline["prototypeLane"]["steps"]), 4)
            self.assertEqual(len(pipeline["manualLane"]["tasks"]), 3)
            self.assertTrue(pipeline["manualLane"]["burden"])
            self.assertEqual(
                pipeline["prototypeLane"]["decisions"],
                ["ACCEPT", "HUMAN_REVIEW", "REJECT"],
            )
            self.assertIn("8", pipeline["prototypeLane"]["conflict"])
            self.assertIn("6", pipeline["prototypeLane"]["conflict"])
        for marker in [
            'class="pipeline-lane manual"',
            'class="pipeline-lane prototype"',
            "@keyframes pipeline-rise",
            "@keyframes conflict-arrives",
            ".slide.active .pipeline-intake",
            ".slide.active .case-context",
            "animation-delay: 0ms !important",
            "animation: none !important",
        ]:
            self.assertIn(marker, self.document)
        self.assertNotIn("animation-iteration-count: infinite", self.document)
        # Preserve the visible top-to-bottom teaching order on the prototype
        # lane: step 3, step 4, then the conflict example and route chips.
        ordered_timing = [
            (".prototype .pipeline-step:nth-child(3)", 4.7),
            (".prototype .pipeline-step:nth-child(4)", 5.15),
            (".pipeline-conflict", 5.7),
            (".pipeline-decisions", 6.35),
        ]
        for selector, delay in ordered_timing:
            self.assertIn(
                f".slide.active {selector}",
                self.document,
            )
            self.assertRegex(
                self.document,
                re.escape(f".slide.active {selector}")
                + rf"[^;]+both {delay:g}s;",
            )

    def test_all_other_slides_share_restrained_content_motion(self):
        """Every slide should feel related without turning tables into effects."""
        for slide in self.source["slides"]:
            self.assertIn(
                f'data-layout="{slide["layout"]}"',
                self.document,
            )
        for marker in [
            ':not([data-layout="pipeline-compare"]):not([data-layout="case"]) .body > *',
            "@keyframes content-arrives",
            '.slide.active[data-layout="hero"] .hero-body > *',
            ".slide .body > *, .slide .hero-body > *",
        ]:
            self.assertIn(marker, self.document)
        # The common transition acts on major blocks, not every table cell.
        self.assertNotIn("td { animation:", self.document)
        self.assertNotIn("th { animation:", self.document)

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

    def test_review_controls_are_visually_quiet_but_accessible(self):
        for text in [
            "opacity: .24",
            ".preferences:hover, .preferences:focus-within { opacity: 1; }",
            "border: 1px solid transparent",
            "@media (hover: none)",
            "@media (pointer: coarse)",
            "outline: 2px solid var(--blue)",
            '>中</button>',
        ]:
            self.assertIn(text, self.document)

    def test_html_is_self_contained(self):
        self.assertNotRegex(self.document, r'<script[^>]+src=')
        self.assertNotRegex(self.document, r'<link[^>]+href=')
        self.assertNotIn("http://", self.document)
        self.assertNotIn("https://", self.document)

    def test_every_slide_links_to_bilingual_original_file_evidence(self):
        slide_ids = {slide["id"] for slide in self.source["slides"]}
        self.assertEqual(set(self.evidence["slides"]), slide_ids)
        for slide_id, links in self.evidence["slides"].items():
            self.assertGreaterEqual(len(links), 1, slide_id)
            self.assertLessEqual(len(links), 3, slide_id)
            for link in links:
                source = self.evidence["files"][link["file"]]
                self.assertTrue(link["en"])
                self.assertTrue(link["zh"])
                href = f'evidence/{source}.html'
                self.assertIn(f'href="{href}"', self.document)
                self.assertIn('target="_blank" rel="noopener noreferrer"', self.document)

    def test_published_evidence_copies_are_exact_and_viewable(self):
        repository_root = PRESENTATION.parent
        referenced = {
            link["file"]
            for links in self.evidence["slides"].values()
            for link in links
        }
        for file_id in referenced:
            source = Path(self.evidence["files"][file_id])
            original = repository_root / source
            copied = PRESENTATION / "evidence" / source
            viewer = Path(f"{copied}.html")
            self.assertEqual(copied.read_bytes(), original.read_bytes(), source)
            viewer_html = viewer.read_text(encoding="utf-8")
            digest = hashlib.sha256(original.read_bytes()).hexdigest()
            self.assertIn(html.escape(source.as_posix()), viewer_html)
            self.assertIn(digest, viewer_html)
            self.assertIn("Open raw file", viewer_html)

        for directory, files in self.evidence.get("directories", {}).items():
            index = PRESENTATION / "evidence" / directory / "index.html"
            index_html = index.read_text(encoding="utf-8")
            for file in files:
                self.assertIn(f'href="{file}.html"', index_html)
                self.assertIn(f'href="{file}"', index_html)

    def test_evidence_viewers_use_format_specific_readable_layouts(self):
        samples = {
            "docs/PROJECT_SCOPE.md.html": [
                'data-viewer-kind="markdown"',
                '<article class="document markdown-body">',
                "<h2>Decision statement</h2>",
            ],
            "evaluation/runs/2026-08-09-final-v4/manifest.json.html": [
                'data-viewer-kind="json"',
                "Pretty JSON",
                'class="json-key"',
            ],
            "data/cases.jsonl.html": [
                'data-viewer-kind="jsonl"',
                "10 records",
                '<details class="record"',
                'data-action="expand"',
            ],
            "evaluation/runs/2026-08-09-final-v4/summary.csv.html": [
                'data-viewer-kind="csv"',
                '<table class="data-table csv-table">',
                "6 rows · 17 columns",
            ],
            "src/voltstream/gatekeeper.py.html": [
                'data-viewer-kind="code"',
                '<ol class="code-lines">',
                "51 lines",
            ],
        }
        for relative_path, markers in samples.items():
            viewer = (PRESENTATION / "evidence" / relative_path).read_text(
                encoding="utf-8"
            )
            for marker in markers:
                self.assertIn(marker, viewer, relative_path)
            self.assertIn("Open raw file", viewer, relative_path)
            self.assertIn("Return to presentation", viewer, relative_path)
            self.assertIn("SHA-256", viewer, relative_path)

    def test_build_receipt_matches_final_deck(self):
        receipt = json.loads((PRESENTATION / "BUILD_RECEIPT.json").read_text(encoding="utf-8"))
        self.assertTrue(receipt["ok"])
        self.assertEqual(receipt["slides"], len(self.source["slides"]))
        self.assertTrue(receipt["self_contained"])
        self.assertEqual(receipt["browser"]["content_clipping"], "none detected")
        self.assertEqual(receipt["print"]["pages"], len(self.source["slides"]))
        self.assertEqual(set(receipt["languages"]), {"en", "zh-CN"})
        self.assertEqual(set(receipt["themes"]), {"dark", "light"})
        artifact = (PRESENTATION / "index.html").read_bytes()
        self.assertEqual(receipt["artifact"]["bytes"], len(artifact))
        self.assertEqual(receipt["artifact"]["sha256"], hashlib.sha256(artifact).hexdigest())


if __name__ == "__main__":
    unittest.main()
