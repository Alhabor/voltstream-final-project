#!/usr/bin/env node
/** Build the self-contained bilingual VoltStream slide deck from JSON sources.
 *
 * The generated HTML intentionally has no runtime dependencies. Keeping the
 * factual slide content in JSON and the presentation mechanics here makes the
 * deck reviewable, reproducible, and safe to regenerate after content edits.
 */

import { readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const directory = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(directory, "slides.json");
const chineseSourcePath = join(directory, "slides.zh.json");
const outputPath = join(directory, "index.html");
const deck = JSON.parse(await readFile(sourcePath, "utf8"));
const chineseDeck = JSON.parse(await readFile(chineseSourcePath, "utf8"));

validateDeck(deck);
validateDeck(chineseDeck);
validateTranslation(deck, chineseDeck);

const slides = deck.slides.map((slide, index) => renderSlide(slide, chineseDeck.slides[index], index, deck.slides.length)).join("\n");
const html = `<!doctype html>
<html lang="en" data-language="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="dark light">
  <meta name="description" content="VoltStream evidence-first Con Edison EV charger data capstone presentation">
  <title>${escapeHtml(deck.title)} — ${escapeHtml(deck.subtitle)}</title>
  <script>
    (() => {
      try {
        const savedLanguage = localStorage.getItem('voltstream-language');
        const savedTheme = localStorage.getItem('voltstream-theme');
        document.documentElement.dataset.language = savedLanguage === 'zh' ? 'zh' : 'en';
        document.documentElement.dataset.theme = savedTheme === 'light' ? 'light' : 'dark';
      } catch (_) { /* File URLs may restrict storage; dark English remains safe. */ }
    })();
  </script>
  <style>
    :root {
      --ink: #f6f7f9;
      --muted: #b9c1cb;
      --subtle: #8f9aa8;
      --paper: #10151b;
      --panel: #17202a;
      --panel-2: #1c2834;
      --line: #334252;
      --blue: #7ec8ff;
      --blue-strong: #2f9ee9;
      --green: #78d6a7;
      --amber: #f2c166;
      --red: #ff8d8d;
      --body-bg: #06090d;
      --stage-border: #26313d;
      --stage-shadow: rgba(0,0,0,.55);
      --grid-line: rgba(126,200,255,.045);
      --slide-start: #111821;
      --slide-end: #0d1319;
      --panel-glow: rgba(255,255,255,.035);
      --panel-fade: rgba(255,255,255,.012);
      --selected-bg-start: #183126;
      --selected-bg-end: #172129;
      --good-tint: rgba(120,214,167,.09);
      --bad-tint: rgba(255,141,141,.08);
      --control-bg: rgba(16,21,27,.9);
      --control-hover: #1b2834;
      --control-border: #536577;
      --progress-track: rgba(255,255,255,.08);
      --stage-w: min(100vw, calc(100vh * 16 / 9));
      --stage-h: min(100vh, calc(100vw * 9 / 16));
      --u: min(1vw, 1.7778vh);
    }

    html[data-theme="light"] {
      --ink: #15212c;
      --muted: #455565;
      --subtle: #647484;
      --paper: #f4f7fa;
      --panel: #e8eef4;
      --panel-2: #dce6ef;
      --line: #a8b8c7;
      --blue: #006eaa;
      --blue-strong: #087bbd;
      --green: #15734a;
      --amber: #815600;
      --red: #a43e49;
      --body-bg: #cdd5dc;
      --stage-border: #9aa8b4;
      --stage-shadow: rgba(31,45,57,.22);
      --grid-line: rgba(0,110,170,.055);
      --slide-start: #f8fafc;
      --slide-end: #eef3f7;
      --panel-glow: rgba(255,255,255,.74);
      --panel-fade: rgba(223,232,240,.58);
      --selected-bg-start: #e4f2e9;
      --selected-bg-end: #edf5f1;
      --good-tint: rgba(21,115,74,.10);
      --bad-tint: rgba(164,62,73,.08);
      --control-bg: rgba(244,247,250,.94);
      --control-hover: #dde8f0;
      --control-border: #718493;
      --progress-track: rgba(21,33,44,.12);
    }

    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; }
    html[data-theme="dark"] { color-scheme: dark; }
    html[data-theme="light"] { color-scheme: light; }
    body {
      background: var(--body-bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    button { font: inherit; }
    .stage {
      position: absolute;
      inset: 50% auto auto 50%;
      width: var(--stage-w);
      height: var(--stage-h);
      transform: translate(-50%, -50%);
      overflow: hidden;
      background: var(--paper);
      box-shadow: 0 0 0 1px var(--stage-border), 0 2.2rem 7rem var(--stage-shadow);
      touch-action: pan-y pinch-zoom;
    }
    .deck { position: absolute; inset: 0; }
    .slide {
      position: absolute;
      inset: 0;
      display: none;
      overflow: hidden;
      background:
        linear-gradient(90deg, var(--grid-line) 1px, transparent 1px) 0 0 / calc(var(--u) * 5) 100%,
        linear-gradient(145deg, var(--slide-start) 0%, var(--slide-end) 72%);
      opacity: 0;
    }
    .slide.active { display: block; opacity: 1; animation: reveal .26s ease-out; }
    .slide-copy {
      position: absolute;
      inset: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: calc(var(--u) * 1.3);
      padding: calc(var(--u) * 3.1) calc(var(--u) * 4.4) calc(var(--u) * 2.2);
      overflow: hidden;
    }
    html[data-language="en"] .slide-copy[data-copy="zh"],
    html[data-language="zh"] .slide-copy[data-copy="en"] { display: none; }
    .slide-copy[data-copy="zh"] {
      font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Inter, ui-sans-serif, sans-serif;
    }
    .slide-copy[data-copy="zh"] h1,
    .slide-copy[data-copy="zh"] h2 { letter-spacing: -.02em; }
    .slide-copy[data-copy="zh"] h1 { max-width: 15ch; }
    .slide-copy[data-copy="zh"] h2 { max-width: 24ch; }
    .slide-copy[data-copy="zh"] .eyebrow { letter-spacing: .08em; }
    @keyframes reveal { from { opacity: 0; transform: translateX(calc(var(--u) * .7)); } }
    .slide::after {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: calc(var(--u) * .55);
      background: var(--blue-strong);
    }
    .slide[data-tone="risk"]::after { background: var(--amber); }
    .slide[data-tone="failure"]::after { background: var(--red); }
    .slide-header { min-width: 0; }
    .eyebrow {
      width: fit-content;
      margin: 0 0 calc(var(--u) * .6);
      color: var(--blue);
      font-size: calc(var(--u) * 1.06);
      font-weight: 760;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      max-width: 16ch;
      margin-bottom: calc(var(--u) * 1.1);
      font-size: calc(var(--u) * 4.8);
      line-height: 1.01;
      letter-spacing: -.045em;
      text-wrap: balance;
    }
    h2 {
      max-width: 34ch;
      margin-bottom: 0;
      font-size: calc(var(--u) * 3.05);
      line-height: 1.08;
      letter-spacing: -.028em;
      text-wrap: balance;
    }
    h3 {
      margin-bottom: calc(var(--u) * .7);
      color: var(--blue);
      font-size: calc(var(--u) * 1.48);
      line-height: 1.15;
    }
    p, li, td, th { font-size: calc(var(--u) * 1.32); line-height: 1.38; }
    .lead { max-width: 54ch; color: var(--ink); font-size: calc(var(--u) * 1.65); line-height: 1.34; }
    .large-claim { max-width: 41ch; font-size: calc(var(--u) * 1.78); line-height: 1.3; }
    .accent { color: var(--blue); }
    .good { color: var(--green); }
    .warn { color: var(--amber); }
    .bad { color: var(--red); }
    .muted { color: var(--muted); }
    .small { font-size: calc(var(--u) * .94); line-height: 1.35; }
    .body { min-height: 0; display: grid; align-content: center; }
    .slide-footer {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: calc(var(--u) * 2);
      color: var(--subtle);
      font-size: calc(var(--u) * .84);
      line-height: 1.25;
      padding-right: calc(var(--u) * 17);
    }
    .slide-footer .section-label { text-align: right; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--u) * 2.4); }
    .panel {
      min-width: 0;
      padding: calc(var(--u) * 1.55);
      border-top: 2px solid var(--line);
      background: linear-gradient(135deg, var(--panel-glow), var(--panel-fade));
    }
    .panel.selected { border-top-color: var(--green); }
    .panel.stopped { border-top-color: var(--red); }
    ul { margin: 0; padding-left: calc(var(--u) * 1.35); }
    li { margin: 0 0 calc(var(--u) * .55); }
    li::marker { color: var(--blue); }
    .note-line { margin-top: calc(var(--u) * 1.15); color: var(--muted); font-size: calc(var(--u) * 1.12); line-height: 1.34; }

    .hero-body { align-content: end; gap: calc(var(--u) * 1.45); }
    .decision-band {
      max-width: 61ch;
      padding-left: calc(var(--u) * 1.25);
      border-left: calc(var(--u) * .24) solid var(--green);
      font-size: calc(var(--u) * 1.38);
      line-height: 1.35;
    }
    .metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--u) * 1.2); }
    .metric { padding-top: calc(var(--u) * .85); border-top: 1px solid var(--line); }
    .metric strong { display: block; color: var(--blue); font-size: calc(var(--u) * 2.35); line-height: 1; }
    .metric span { color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.25; }

    .definition-lead { max-width: 65ch; margin-bottom: calc(var(--u) * 1.15); color: var(--muted); font-size: calc(var(--u) * 1.28); }
    .definition-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * 1.2); }
    .definition-term { padding: calc(var(--u) * 1.15); border-top: 2px solid var(--blue-strong); background: var(--panel); }
    .definition-term strong { display: block; margin-bottom: calc(var(--u) * .45); color: var(--blue); font-size: calc(var(--u) * 1.45); }
    .definition-term span { color: var(--muted); font-size: calc(var(--u) * 1.12); line-height: 1.32; }
    .status-heading { margin: calc(var(--u) * 1.2) 0 calc(var(--u) * .65); font-size: calc(var(--u) * 1.28); }
    .status-contrast { display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--u) * 1.2); }
    .status-count { display: grid; grid-template-columns: calc(var(--u) * 4.2) 1fr; align-items: center; gap: calc(var(--u) * .8); padding: calc(var(--u) * .8) calc(var(--u) * 1); border-left: 3px solid var(--green); background: var(--good-tint); }
    .status-count strong { color: var(--blue); font-size: calc(var(--u) * 2.5); line-height: 1; }
    .status-count b { display: block; margin-bottom: calc(var(--u) * .18); font-size: calc(var(--u) * 1.14); }
    .status-count span { color: var(--muted); font-size: calc(var(--u) * 1.04); line-height: 1.25; }
    .definition-consequence { margin-top: calc(var(--u) * .85); color: var(--ink); font-size: calc(var(--u) * 1.18); font-weight: 700; }

    .fact-box {
      display: grid;
      grid-template-columns: .42fr 1fr;
      align-items: start;
      gap: calc(var(--u) * 2.5);
    }
    .fact-label { color: var(--amber); font-size: calc(var(--u) * 1.15); font-weight: 800; text-transform: uppercase; letter-spacing: .12em; }
    .fact-copy { font-size: calc(var(--u) * 2.05); line-height: 1.22; }
    .implication { margin-top: calc(var(--u) * 1.5); padding-top: calc(var(--u) * 1.2); border-top: 1px solid var(--line); }
    .source-line { margin-top: calc(var(--u) * 1.1); color: var(--subtle); font-size: calc(var(--u) * .76); line-height: 1.25; }

    .choices { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * 1.4); }
    .choice { min-height: calc(var(--u) * 12.8); padding: calc(var(--u) * 1.45); border-top: 3px solid var(--line); background: var(--panel); }
    .choice[data-status="Selected"] { border-color: var(--green); background: linear-gradient(145deg, var(--selected-bg-start), var(--selected-bg-end)); }
    .choice[data-status="Stopped"] { border-color: var(--red); }
    .status { display: inline-block; margin-bottom: calc(var(--u) * 1.2); color: var(--muted); font-size: calc(var(--u) * .9); font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }

    .scope-top { display: grid; grid-template-columns: 1fr 1fr 1.3fr; gap: calc(var(--u) * 1.15); margin-bottom: calc(var(--u) * 1.45); }
    .scope-option { padding: calc(var(--u) * 1.05); border-top: 3px solid var(--red); background: var(--panel); }
    .scope-option strong, .scope-selected strong { display: block; margin-bottom: calc(var(--u) * .35); font-size: calc(var(--u) * 1.26); }
    .scope-option span { color: var(--muted); font-size: calc(var(--u) * 1.06); line-height: 1.28; }
    .scope-selected { padding: calc(var(--u) * 1.05); border-top: 3px solid var(--green); background: var(--good-tint); }
    .scope-selected span { color: var(--green); font-size: calc(var(--u) * 1.08); font-weight: 800; }
    .scope-flow .flow-number { width: calc(var(--u) * 3.25); height: calc(var(--u) * 3.25); font-size: calc(var(--u) * 1.35); }
    .scope-flow .flow::before { top: calc(var(--u) * 1.62); }
    .scope-flow .flow-step h3 { margin-bottom: calc(var(--u) * .35); }
    .scope-flow .flow-step p { margin-bottom: 0; font-size: calc(var(--u) * 1.08); }

    .flow { display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--u) * 1.55); position: relative; }
    .flow::before { content: ""; position: absolute; top: calc(var(--u) * 2); left: 9%; right: 9%; height: 2px; background: var(--line); }
    .flow-step { position: relative; text-align: center; }
    .flow-number { position: relative; z-index: 1; display: grid; place-items: center; width: calc(var(--u) * 4); height: calc(var(--u) * 4); margin: 0 auto calc(var(--u) * 1); border-radius: 50%; color: #07111a; background: var(--blue); font-size: calc(var(--u) * 1.5); font-weight: 900; }
    .flow-step p { color: var(--muted); }
    .guardrail { margin-top: calc(var(--u) * 1.35); padding: calc(var(--u) * 1.05) calc(var(--u) * 1.35); border-left: 3px solid var(--green); background: var(--good-tint); font-size: calc(var(--u) * 1.25); }

    .failure-grid { display: grid; grid-template-columns: .85fr 1.15fr; gap: calc(var(--u) * 2.3); min-height: calc(var(--u) * 15.5); }
    .primary-failure { padding: calc(var(--u) * 1.5); border-left: 3px solid var(--red); background: var(--bad-tint); font-size: calc(var(--u) * 1.42); line-height: 1.35; }
    .event { display: grid; grid-template-columns: calc(var(--u) * 6.2) 1fr; gap: calc(var(--u) * 1); margin-bottom: calc(var(--u) * .85); padding-bottom: calc(var(--u) * .85); border-bottom: 1px solid var(--line); }
    .event strong { color: var(--blue); font-size: calc(var(--u) * 1.04); }
    .event span { color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.3; }

    .case-context { margin-bottom: calc(var(--u) * .75); color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.3; }
    .conflict { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: calc(var(--u) * 1.2); }
    .source-value { padding: calc(var(--u) * 1.1); text-align: center; border: 1px solid var(--line); background: var(--panel); }
    .source-value strong { display: block; margin-top: calc(var(--u) * .35); color: var(--blue); font-size: calc(var(--u) * 3); line-height: 1; }
    .versus { color: var(--red); font-size: calc(var(--u) * 1.35); font-weight: 900; }
    .canonical-answer { margin: calc(var(--u) * 1.1) auto; text-align: center; }
    .canonical-answer strong { color: var(--green); font-size: calc(var(--u) * 1.65); }
    .outcome-table { width: 100%; border-collapse: collapse; }
    .outcome-table td { padding: calc(var(--u) * .7) calc(var(--u) * .8); border-bottom: 1px solid var(--line); font-size: calc(var(--u) * 1.12); }
    .outcome-table td:last-child { text-align: right; font-weight: 800; }

    .signal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--u) * 1.6); }
    .signal { min-height: calc(var(--u) * 10.5); padding: calc(var(--u) * 1.5); border-top: 3px solid var(--line); background: var(--panel); }
    .signal:first-child { border-top-color: var(--green); }
    .signal-value { color: var(--blue); font-size: calc(var(--u) * 1.65); font-weight: 850; }
    .next-step { margin-top: calc(var(--u) * 1.2); padding-top: calc(var(--u) * 1.05); border-top: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * 1.18); }

    .number-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--u) * 1.1); }
    .number { padding: calc(var(--u) * 1.05); border-top: 2px solid var(--blue-strong); background: var(--panel); }
    .number strong { display: block; color: var(--blue); font-size: calc(var(--u) * 2.4); line-height: 1; }
    .number span { color: var(--muted); font-size: calc(var(--u) * 1.08); }
    .tag-row { display: flex; flex-wrap: wrap; gap: calc(var(--u) * .6); margin-top: calc(var(--u) * 1.2); }
    .tag { padding: calc(var(--u) * .48) calc(var(--u) * .76); border: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * 1.08); }

    .strategy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .9); }
    .strategy-card { min-height: calc(var(--u) * 8.2); padding: calc(var(--u) * 1); border-top: 2px solid var(--line); background: var(--panel); }
    .strategy-head { display: flex; align-items: baseline; gap: calc(var(--u) * .6); margin-bottom: calc(var(--u) * .45); }
    .strategy-code { color: var(--blue); font-size: calc(var(--u) * 1.22); font-weight: 900; }
    .strategy-role { color: var(--green); font-size: calc(var(--u) * 1.04); font-weight: 800; }
    .strategy-card h3 { margin-bottom: calc(var(--u) * .4); font-size: calc(var(--u) * 1.24); }
    .strategy-card p { margin-bottom: 0; color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.28; }

    .metric-detail-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .9); }
    .metric-detail { min-height: calc(var(--u) * 7.7); padding: calc(var(--u) * 1.05); border-top: 2px solid var(--blue-strong); background: var(--panel); }
    .metric-detail strong { display: block; color: var(--blue); font-size: calc(var(--u) * 2.05); line-height: 1; }
    .metric-detail h3 { margin: calc(var(--u) * .42) 0; font-size: calc(var(--u) * 1.24); }
    .metric-detail p { margin-bottom: 0; color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.28; }

    .judgement-grid { display: grid; grid-template-columns: 1.08fr .92fr; gap: calc(var(--u) * 1.7); }
    .rule-list { display: grid; gap: calc(var(--u) * .55); }
    .quality-rule { display: flex; justify-content: space-between; gap: calc(var(--u) * 1); padding: calc(var(--u) * .72) calc(var(--u) * .9); border-bottom: 1px solid var(--line); background: var(--panel); }
    .quality-rule span { font-size: calc(var(--u) * 1.1); }
    .quality-rule strong { color: var(--green); font-size: calc(var(--u) * 1.1); white-space: nowrap; }
    .veto-box { padding: calc(var(--u) * 1.1); border-left: 4px solid var(--red); background: var(--bad-tint); }
    .veto-box li { margin-bottom: calc(var(--u) * .7); font-size: calc(var(--u) * 1.1); }
    .result-key { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .75); margin-top: calc(var(--u) * 1.05); }
    .result-item { padding: calc(var(--u) * .72); border-top: 2px solid var(--line); }
    .result-item strong { display: block; color: var(--blue); font-size: calc(var(--u) * 1.12); }
    .result-item span { color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.25; }

    .score-wrap { align-content: start; }
    .score-table, .efficiency-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .score-table th, .score-table td, .efficiency-table th, .efficiency-table td { padding: calc(var(--u) * .5) calc(var(--u) * .52); border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
    .score-table th, .efficiency-table th { color: var(--blue); font-size: calc(var(--u) * 1.08); letter-spacing: .025em; }
    .score-table td, .efficiency-table td { font-size: calc(var(--u) * 1.08); }
    .score-table th:first-child, .score-table td:first-child, .efficiency-table th:first-child, .efficiency-table td:first-child { width: 25%; text-align: left; }
    .score-table tr.winner { background: var(--good-tint); }
    .score-table tr.winner td:first-child { color: var(--green); font-weight: 850; }
    .score-table td.veto { color: var(--red); font-weight: 800; }
    .score-table td.pass { color: var(--green); font-weight: 800; }
    .efficiency-table th:first-child, .efficiency-table td:first-child { width: 29%; }
    .efficiency-table td:last-child { font-weight: 800; }
    .findings { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .9); margin-top: calc(var(--u) * 1); }
    .finding { padding: calc(var(--u) * .82); border-top: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.3; }

    .recommendation-grid { display: grid; grid-template-columns: 1.15fr .85fr; gap: calc(var(--u) * 2); }
    .decision { padding: calc(var(--u) * 1.45); border-left: 4px solid var(--green); background: var(--good-tint); font-size: calc(var(--u) * 1.42); line-height: 1.35; }
    .check-list { list-style: none; padding: 0; }
    .check-list li { position: relative; padding-left: calc(var(--u) * 1.35); }
    .check-list li::before { content: "✓"; position: absolute; left: 0; color: var(--green); font-weight: 900; }
    .gate-list { counter-reset: gate; list-style: none; padding: 0; }
    .gate-list li { counter-increment: gate; position: relative; padding-left: calc(var(--u) * 1.7); }
    .gate-list li::before { content: counter(gate); position: absolute; left: 0; color: var(--blue); font-weight: 900; }

    .risk-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .85) calc(var(--u) * 1.2); min-height: calc(var(--u) * 10.5); }
    .risk { padding-top: calc(var(--u) * .65); border-top: 1px solid var(--line); }
    .risk strong { display: block; margin-bottom: calc(var(--u) * .25); color: var(--amber); font-size: calc(var(--u) * 1.12); }
    .risk span { color: var(--muted); font-size: calc(var(--u) * 1.08); line-height: 1.28; }
    .close-line { margin-top: calc(var(--u) * .9); color: var(--blue); font-size: calc(var(--u) * 1.45); font-weight: 800; }

    .controls {
      position: absolute;
      inset: auto calc(var(--u) * 1.25) calc(var(--u) * .9) auto;
      z-index: 20;
      display: flex;
      align-items: center;
      gap: calc(var(--u) * .55);
    }
    .preferences {
      position: absolute;
      inset: calc(var(--u) * 1.05) calc(var(--u) * 1.25) auto auto;
      z-index: 22;
      display: flex;
      gap: calc(var(--u) * .45);
    }
    .nav-button, .preference-button {
      display: grid;
      place-items: center;
      width: calc(var(--u) * 3.2);
      height: calc(var(--u) * 2.7);
      border: 1px solid var(--control-border);
      color: var(--ink);
      background: var(--control-bg);
      cursor: pointer;
    }
    .preference-button.language { width: calc(var(--u) * 4.2); font-weight: 780; }
    .nav-button:hover, .nav-button:focus-visible,
    .preference-button:hover, .preference-button:focus-visible { border-color: var(--blue); outline: none; background: var(--control-hover); }
    .nav-button:disabled { opacity: .3; cursor: default; }
    .page-count { min-width: calc(var(--u) * 4.3); color: var(--muted); text-align: center; font-size: calc(var(--u) * .92); font-variant-numeric: tabular-nums; }
    .progress { position: absolute; z-index: 21; inset: auto 0 0; height: calc(var(--u) * .24); background: var(--progress-track); }
    .progress-bar { height: 100%; width: 0; background: var(--blue-strong); transition: width .24s ease; }
    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .001ms !important; animation-iteration-count: 1 !important; transition-duration: .001ms !important; }
    }

    @media print {
      @page { size: 13.333in 7.5in; margin: 0; }
      html, body { width: auto; height: auto; overflow: visible; background: #fff; }
      body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .stage { position: static; width: 13.333in; height: auto; transform: none; overflow: visible; box-shadow: none; }
      .deck { position: static; }
      .slide, .slide.active {
        position: relative;
        display: block !important;
        width: 13.333in;
        height: 7.5in;
        opacity: 1 !important;
        animation: none !important;
        break-after: page;
        page-break-after: always;
      }
      .slide:last-child { break-after: auto; page-break-after: auto; }
      .slide-copy { display: grid; }
      html[data-language="en"] .slide-copy[data-copy="zh"],
      html[data-language="zh"] .slide-copy[data-copy="en"] { display: none !important; }
      .controls, .preferences, .progress { display: none !important; }
    }
  </style>
</head>
<body>
  <main class="stage" aria-label="VoltStream slide presentation">
    <div class="deck" id="deck">${slides}</div>
    <nav class="preferences" aria-label="Display preferences">
      <button class="preference-button language" id="language" type="button" aria-label="切换至中文" title="切换至中文">中文</button>
      <button class="preference-button" id="theme" type="button" aria-label="Switch to light theme" title="Switch to light theme">☀</button>
    </nav>
    <nav class="controls" aria-label="Slide navigation">
      <button class="nav-button" id="previous" type="button" aria-label="Previous slide" title="Previous slide (←)">←</button>
      <span class="page-count" id="page-count" aria-live="polite">1 / ${deck.slides.length}</span>
      <button class="nav-button" id="next" type="button" aria-label="Next slide" title="Next slide (→)">→</button>
      <button class="nav-button" id="fullscreen" type="button" aria-label="Toggle fullscreen" title="Toggle fullscreen (F)">F</button>
    </nav>
    <div class="progress" aria-hidden="true"><div class="progress-bar" id="progress-bar"></div></div>
    <div class="sr-only" id="status" aria-live="polite"></div>
  </main>
  <script>
    (() => {
      const slides = [...document.querySelectorAll('.slide')];
      const previous = document.getElementById('previous');
      const next = document.getElementById('next');
      const fullscreen = document.getElementById('fullscreen');
      const languageButton = document.getElementById('language');
      const themeButton = document.getElementById('theme');
      const pageCount = document.getElementById('page-count');
      const progressBar = document.getElementById('progress-bar');
      const status = document.getElementById('status');
      const stage = document.querySelector('.stage');
      const controlLabels = {
        en: {
          stage: 'VoltStream slide presentation', navigation: 'Slide navigation', preferences: 'Display preferences',
          previous: 'Previous slide', next: 'Next slide', fullscreen: 'Toggle fullscreen',
          language: '切换至中文', light: 'Switch to light theme', dark: 'Switch to dark theme', slide: 'Slide', of: 'of'
        },
        zh: {
          stage: 'VoltStream 幻灯片演示', navigation: '幻灯片导航', preferences: '显示设置',
          previous: '上一页', next: '下一页', fullscreen: '切换全屏',
          language: 'Switch to English', light: '切换至浅色模式', dark: '切换至深色模式', slide: '第', of: '页，共'
        }
      };
      let language = document.documentElement.dataset.language === 'zh' ? 'zh' : 'en';
      let theme = document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
      let current = parseHash();
      let pointerStart = null;
      let wheelLocked = false;

      function parseHash() {
        const match = location.hash.match(/^#slide-(\\d+)$/);
        const requested = match ? Number(match[1]) - 1 : 0;
        return Math.min(slides.length - 1, Math.max(0, Number.isFinite(requested) ? requested : 0));
      }

      function show(index, updateHash = true) {
        current = Math.min(slides.length - 1, Math.max(0, index));
        slides.forEach((slide, i) => {
          const active = i === current;
          slide.classList.toggle('active', active);
          slide.setAttribute('aria-hidden', String(!active));
          if ('inert' in slide) slide.inert = !active;
        });
        previous.disabled = current === 0;
        next.disabled = current === slides.length - 1;
        pageCount.textContent = (current + 1) + ' / ' + slides.length;
        progressBar.style.width = (((current + 1) / slides.length) * 100) + '%';
        const title = language === 'zh' ? slides[current].dataset.titleZh : slides[current].dataset.titleEn;
        const labels = controlLabels[language];
        status.textContent = language === 'zh'
          ? labels.slide + (current + 1) + labels.of + slides.length + '页：' + title
          : labels.slide + ' ' + (current + 1) + ' ' + labels.of + ' ' + slides.length + ': ' + title;
        document.title = title + ' — ' + (language === 'zh' ? '${escapeJs(chineseDeck.title)}' : '${escapeJs(deck.title)}');
        slides[current].setAttribute('aria-label', status.textContent);
        const hash = '#slide-' + (current + 1);
        if (updateHash && location.hash !== hash) history.replaceState(null, '', hash);
      }

      function storePreference(key, value) {
        try { localStorage.setItem(key, value); } catch (_) { /* Keep session behavior when storage is restricted. */ }
      }

      function updatePreferences() {
        const labels = controlLabels[language];
        document.documentElement.dataset.language = language;
        document.documentElement.dataset.theme = theme;
        document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
        languageButton.textContent = language === 'en' ? '中文' : 'EN';
        languageButton.setAttribute('aria-label', labels.language);
        languageButton.title = labels.language;
        themeButton.textContent = theme === 'dark' ? '☀' : '☾';
        const themeLabel = theme === 'dark' ? labels.light : labels.dark;
        themeButton.setAttribute('aria-label', themeLabel);
        themeButton.title = themeLabel;
        stage.setAttribute('aria-label', labels.stage);
        document.querySelector('.controls').setAttribute('aria-label', labels.navigation);
        document.querySelector('.preferences').setAttribute('aria-label', labels.preferences);
        previous.setAttribute('aria-label', labels.previous);
        previous.title = labels.previous + ' (←)';
        next.setAttribute('aria-label', labels.next);
        next.title = labels.next + ' (→)';
        fullscreen.setAttribute('aria-label', labels.fullscreen);
        fullscreen.title = labels.fullscreen + ' (F)';
        show(current, false);
      }

      languageButton.addEventListener('click', () => {
        language = language === 'en' ? 'zh' : 'en';
        storePreference('voltstream-language', language);
        updatePreferences();
      });
      themeButton.addEventListener('click', () => {
        theme = theme === 'dark' ? 'light' : 'dark';
        storePreference('voltstream-theme', theme);
        updatePreferences();
      });

      const forwardKeys = new Set(['ArrowRight', 'ArrowDown', ' ', 'PageDown']);
      const backwardKeys = new Set(['ArrowLeft', 'ArrowUp', 'PageUp']);
      document.addEventListener('keydown', async (event) => {
        if (forwardKeys.has(event.key)) { event.preventDefault(); show(current + 1); }
        else if (backwardKeys.has(event.key)) { event.preventDefault(); show(current - 1); }
        else if (event.key === 'Home') { event.preventDefault(); show(0); }
        else if (event.key === 'End') { event.preventDefault(); show(slides.length - 1); }
        else if (event.key.toLowerCase() === 'f') {
          event.preventDefault();
          try {
            if (document.fullscreenElement) await document.exitFullscreen();
            else await document.documentElement.requestFullscreen();
          } catch (_) { /* Browser policy may require a direct user gesture. */ }
        }
      });

      previous.addEventListener('click', () => show(current - 1));
      next.addEventListener('click', () => show(current + 1));
      fullscreen.addEventListener('click', async () => {
        try {
          if (document.fullscreenElement) await document.exitFullscreen();
          else await document.documentElement.requestFullscreen();
        } catch (_) { /* Keep navigation usable if fullscreen is unavailable. */ }
      });

      stage.addEventListener('pointerdown', (event) => {
        if (event.target.closest('button')) return;
        pointerStart = { x: event.clientX, y: event.clientY, time: performance.now() };
      });
      stage.addEventListener('pointerup', (event) => {
        if (!pointerStart) return;
        const dx = event.clientX - pointerStart.x;
        const dy = event.clientY - pointerStart.y;
        const elapsed = performance.now() - pointerStart.time;
        pointerStart = null;
        if (elapsed < 900 && Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.15) show(current + (dx < 0 ? 1 : -1));
      });
      stage.addEventListener('pointercancel', () => { pointerStart = null; });
      stage.addEventListener('wheel', (event) => {
        if (Math.abs(event.deltaX) < 30 && Math.abs(event.deltaY) < 45) return;
        event.preventDefault();
        if (wheelLocked) return;
        const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
        show(current + (delta > 0 ? 1 : -1));
        wheelLocked = true;
        setTimeout(() => { wheelLocked = false; }, 280);
      }, { passive: false });

      window.addEventListener('hashchange', () => show(parseHash(), false));
      updatePreferences();
      show(current);
    })();
  </script>
</body>
</html>`;

await writeFile(outputPath, html, "utf8");
console.log(`Built ${deck.slides.length} slides: ${outputPath}`);

function validateDeck(value) {
  if (!value || !Array.isArray(value.slides)) throw new Error("slides.json must contain a slides array");
  if (value.slides.length < 11) throw new Error("Deck must contain at least 11 slides");
  const ids = value.slides.map((slide) => slide.id);
  if (new Set(ids).size !== ids.length) throw new Error("Slide IDs must be unique");
  const required = [
    "Problem area and why",
    "Background research and surprising fact",
    "Ideation process",
    "What failed",
    "What might still work",
    "Testing and case evidence",
    "Recommendation",
    "What could go wrong"
  ];
  let cursor = -1;
  for (const section of required) {
    const index = value.slides.findIndex((slide, slideIndex) => slideIndex > cursor && slide.section === section);
    if (index < 0) throw new Error(`Missing or out-of-order required section: ${section}`);
    cursor = index;
  }
}

function validateTranslation(english, chinese) {
  if (english.slides.length !== chinese.slides.length) throw new Error("English and Chinese decks must have the same slide count");
  english.slides.forEach((slide, index) => {
    const translated = chinese.slides[index];
    for (const field of ["id", "section", "layout"]) {
      if (slide[field] !== translated[field]) throw new Error(`Translation mismatch at slide ${index + 1}: ${field}`);
    }
  });
}

function renderSlide(slide, chineseSlide, index, total) {
  const tone = slide.layout === "failure" || slide.layout === "case" ? "failure" : slide.layout === "risks" ? "risk" : "standard";
  return `<section class="slide" id="slide-${index + 1}" data-title-en="${escapeHtml(slide.title)}" data-title-zh="${escapeHtml(chineseSlide.title)}" data-tone="${tone}" aria-roledescription="slide" aria-label="Slide ${index + 1} of ${total}">
    ${renderCopy(slide, "en", index, total)}
    ${renderCopy(chineseSlide, "zh", index, total)}
  </section>`;
}

function renderCopy(slide, language, index, total) {
  const footer = language === "zh" ? "VoltStream · 仅使用模拟/公开数据，未使用公司记录" : "VoltStream · made-up/public test data; no company records";
  return `<div class="slide-copy" data-copy="${language}" lang="${language === "zh" ? "zh-CN" : "en"}">
    <header class="slide-header"><p class="eyebrow">${escapeHtml(slide.eyebrow)}</p><h${index === 0 ? "1" : "2"}>${escapeHtml(slide.title)}</h${index === 0 ? "1" : "2"}></header>
    <div class="body ${slide.layout === "score-table" ? "score-wrap" : ""}">${renderBody(slide, language)}</div>
    <footer class="slide-footer"><span>${footer}</span><span class="section-label">${escapeHtml(slide.sectionLabel || slide.section)} · ${index + 1}/${total}</span></footer>
  </div>`;
}

function renderBody(slide, language) {
  const isChinese = language === "zh";
  switch (slide.layout) {
    case "hero":
      return `<div class="hero-body"><p class="lead">${escapeHtml(slide.lead)}</p><p class="decision-band">${escapeHtml(slide.boundary)}</p><div class="metric-row">${slide.metrics.map(metric => `<div class="metric"><strong>${escapeHtml(metric.value)}</strong><span>${escapeHtml(metric.label)}</span></div>`).join("")}</div></div>`;
    case "split":
      return `<p class="lead">${escapeHtml(slide.lead)}</p><div class="two-col"><div class="panel"><h3>${escapeHtml(slide.leftTitle)}</h3>${list(slide.leftItems)}</div><div class="panel selected"><h3>${escapeHtml(slide.rightTitle)}</h3>${list(slide.rightItems)}</div></div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "definitions":
      return `<p class="definition-lead">${escapeHtml(slide.lead)}</p><div class="definition-grid">${slide.terms.map(term => `<div class="definition-term"><strong>${escapeHtml(term.name)}</strong><span>${escapeHtml(term.definition)}</span></div>`).join("")}</div><h3 class="status-heading">${escapeHtml(slide.statusTitle)}</h3><div class="status-contrast">${slide.statuses.map(status => `<div class="status-count"><strong>${escapeHtml(status.value)}</strong><div><b>${escapeHtml(status.label)}</b><span>${escapeHtml(status.meaning)}</span></div></div>`).join("")}</div><p class="definition-consequence">${escapeHtml(slide.consequence)}</p>`;
    case "fact":
      return `<div class="fact-box"><div class="fact-label">${isChinese ? "我们查到的事实" : "What we found"}</div><div><p class="fact-copy">${escapeHtml(slide.fact)}</p><p class="implication large-claim"><span class="accent">${isChinese ? "这意味着：" : "What this means:"}</span> ${escapeHtml(slide.implication)}</p><p class="source-line">${escapeHtml(slide.sources)}</p></div></div>`;
    case "choices":
      return `<div class="choices">${slide.choices.map(choice => `<article class="choice" data-status="${escapeHtml(choice.status)}"><span class="status">${escapeHtml(choice.statusLabel || choice.status)}</span><h3>${escapeHtml(choice.name)}</h3><p class="muted">${escapeHtml(choice.description)}</p></article>`).join("")}</div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "scope-flow":
      return `<div class="scope-flow"><div class="scope-top">${slide.rejected.map(item => `<div class="scope-option"><strong>${escapeHtml(item.name)}</strong><span>${escapeHtml(item.reason)}</span></div>`).join("")}<div class="scope-selected"><span>${isChinese ? "最终选择" : "SELECTED"}</span><strong>${escapeHtml(slide.selected)}</strong></div></div><div class="flow">${slide.steps.map(step => `<article class="flow-step"><div class="flow-number">${escapeHtml(step.number)}</div><h3>${escapeHtml(step.title)}</h3><p>${escapeHtml(step.detail)}</p></article>`).join("")}</div><p class="guardrail">${escapeHtml(slide.note)}</p></div>`;
    case "flow":
      return `<div class="flow">${slide.steps.map(step => `<article class="flow-step"><div class="flow-number">${escapeHtml(step.number)}</div><h3>${escapeHtml(step.title)}</h3><p>${escapeHtml(step.detail)}</p></article>`).join("")}</div><p class="guardrail">${escapeHtml(slide.guardrail)}</p><p class="note-line">${escapeHtml(slide.excluded)}</p>`;
    case "failure":
      return `<div class="failure-grid"><div><p class="primary-failure">${escapeHtml(slide.primary)}</p><p class="note-line">${escapeHtml(slide.boundary)}</p></div><div>${slide.events.map(event => `<div class="event"><strong>${escapeHtml(event.label)}</strong><span>${escapeHtml(event.detail)}</span></div>`).join("")}</div></div>`;
    case "case":
      return `<p class="case-context">${escapeHtml(slide.context)}</p><div class="conflict"><div class="source-value"><span>${escapeHtml(slide.sourceValues[0].label)}</span><strong>${escapeHtml(slide.sourceValues[0].value)}</strong></div><div class="versus">≠</div><div class="source-value"><span>${escapeHtml(slide.sourceValues[1].label)}</span><strong>${escapeHtml(slide.sourceValues[1].value)}</strong></div></div><div class="canonical-answer"><span>${isChinese ? "输出表格只提供：" : "The output table offers only:"} <strong>${escapeHtml(slide.canonical)}</strong></span><br><span>${isChinese ? "安全回答：" : "Safe response:"} <strong>${escapeHtml(slide.safeAnswer)}</strong></span></div><table class="outcome-table"><tbody>${slide.outcomes.map(outcome => `<tr><td>${escapeHtml(outcome.strategy)}</td><td>${escapeHtml(outcome.result)}</td><td class="${outcome.status.includes("unsafe") ? "bad" : outcome.status === "correct" ? "good" : "warn"}">${escapeHtml(outcome.statusLabel || outcome.status)}</td></tr>`).join("")}</tbody></table><p class="note-line">${escapeHtml(slide.takeaway)}</p>`;
    case "signal":
      return `<div class="signal-grid">${slide.signals.map(signal => `<article class="signal"><h3>${escapeHtml(signal.title)}</h3><p class="signal-value">${escapeHtml(signal.value)}</p><p class="muted">${escapeHtml(signal.description)}</p></article>`).join("")}</div><p class="next-step"><span class="accent">${isChinese ? "下一步：" : "Next step:"}</span> ${escapeHtml(slide.next)}</p>`;
    case "testing":
      return `<div class="number-row">${slide.numbers.map(number => `<div class="number"><strong>${escapeHtml(number.value)}</strong><span>${escapeHtml(number.label)}</span></div>`).join("")}</div><div class="tag-row">${slide.coverage.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div><p class="note-line">${escapeHtml(slide.method)}</p><p class="guardrail">${escapeHtml(slide.gate)}</p>`;
    case "strategies":
      return `<div class="strategy-grid">${slide.strategies.map(strategy => `<article class="strategy-card"><div class="strategy-head"><span class="strategy-role">${escapeHtml(strategy.role)}</span></div><h3>${escapeHtml(strategy.name)}</h3><p>${escapeHtml(strategy.detail)}</p></article>`).join("")}</div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "metrics":
      return `<div class="metric-detail-grid">${slide.metricsDetail.map(metric => `<article class="metric-detail"><strong>${escapeHtml(metric.value)}</strong><h3>${escapeHtml(metric.name)}</h3><p>${escapeHtml(metric.detail)}</p></article>`).join("")}</div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "judgement":
      return `<div class="judgement-grid"><div><h3>${escapeHtml(slide.qualityTitle)}</h3><div class="rule-list">${slide.qualityRules.map(rule => `<div class="quality-rule"><span>${escapeHtml(rule.measure)}</span><strong>${escapeHtml(rule.threshold)}</strong></div>`).join("")}</div></div><div><div class="veto-box"><h3>${escapeHtml(slide.vetoTitle)}</h3>${list(slide.vetoRules)}</div><div class="result-key">${slide.resultKey.map(result => `<div class="result-item"><strong>${escapeHtml(result.label)}</strong><span>${escapeHtml(result.meaning)}</span></div>`).join("")}</div></div></div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "score-table":
      return `<table class="score-table"><thead><tr>${slide.columns.map(column => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead><tbody>${slide.rows.map((row, rowIndex) => `<tr class="${rowIndex === 1 ? "winner" : ""}">${row.map((cell, index) => `<td class="${index === row.length - 1 ? (["Pass", "通过"].includes(cell) ? "pass" : ["Veto", "否决"].includes(cell) ? "veto" : "") : ""}">${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "efficiency":
      return `<table class="efficiency-table"><thead><tr>${(slide.tableHeaders || ["Strategy", "Calls", "Total latency", "List cost", "Status"]).map(header => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead><tbody>${slide.rows.map(row => `<tr><td>${escapeHtml(row.strategy)}</td><td>${escapeHtml(row.calls)}</td><td>${escapeHtml(row.latency)}</td><td>${escapeHtml(row.cost)}</td><td class="${row.status === "Veto" ? "bad" : "good"}">${escapeHtml(row.statusLabel || row.status)}</td></tr>`).join("")}</tbody></table><div class="findings">${slide.findings.map(finding => `<div class="finding">${escapeHtml(finding)}</div>`).join("")}</div>`;
    case "recommendation":
      return `<div class="recommendation-grid"><div><p class="decision">${escapeHtml(slide.decision)}</p><h3>${escapeHtml(slide.guardrailsTitle || "Operating guardrails")}</h3><ul class="check-list">${slide.guardrails.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div><div class="panel"><h3>${escapeHtml(slide.beforeExpansionTitle || "Before expansion")}</h3><ol class="gate-list">${slide.beforeExpansion.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div></div>`;
    case "risks":
      return `<div class="risk-grid">${slide.risks.map(risk => `<div class="risk"><strong>${escapeHtml(risk.title)}</strong><span>${escapeHtml(risk.detail)}</span></div>`).join("")}</div><p class="note-line">${escapeHtml(slide.nextGate)}</p><p class="close-line">${escapeHtml(slide.close)}</p>`;
    default:
      throw new Error(`Unsupported slide layout: ${slide.layout}`);
  }
}

function list(items) {
  return `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[character]);
}

function escapeJs(value) {
  return String(value).replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\r?\n/g, " ");
}
