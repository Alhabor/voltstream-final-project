#!/usr/bin/env node
/** Build the self-contained VoltStream slide deck from slides.json.
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
const outputPath = join(directory, "index.html");
const deck = JSON.parse(await readFile(sourcePath, "utf8"));

validateDeck(deck);

const slides = deck.slides.map((slide, index) => renderSlide(slide, index, deck.slides.length)).join("\n");
const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="dark">
  <meta name="description" content="VoltStream evidence-first Con Edison EV charger data capstone presentation">
  <title>${escapeHtml(deck.title)} — ${escapeHtml(deck.subtitle)}</title>
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
      --stage-w: min(100vw, calc(100vh * 16 / 9));
      --stage-h: min(100vh, calc(100vw * 9 / 16));
      --u: min(1vw, 1.7778vh);
    }

    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; }
    body {
      background: #06090d;
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
      box-shadow: 0 0 0 1px #26313d, 0 2.2rem 7rem rgba(0,0,0,.55);
      touch-action: pan-y pinch-zoom;
    }
    .deck { position: absolute; inset: 0; }
    .slide {
      position: absolute;
      inset: 0;
      display: none;
      grid-template-rows: auto 1fr auto;
      gap: calc(var(--u) * 1.3);
      padding: calc(var(--u) * 3.1) calc(var(--u) * 4.4) calc(var(--u) * 2.2);
      overflow: hidden;
      background:
        linear-gradient(90deg, rgba(126,200,255,.045) 1px, transparent 1px) 0 0 / calc(var(--u) * 5) 100%,
        linear-gradient(145deg, #111821 0%, #0d1319 72%);
      opacity: 0;
    }
    .slide.active { display: grid; opacity: 1; animation: reveal .26s ease-out; }
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
      margin: 0 0 calc(var(--u) * .6);
      color: var(--blue);
      font-size: calc(var(--u) * 1.06);
      font-weight: 760;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      max-width: 13ch;
      margin-bottom: calc(var(--u) * 1.1);
      font-size: calc(var(--u) * 5.15);
      line-height: .98;
      letter-spacing: -.045em;
    }
    h2 {
      max-width: 29ch;
      margin-bottom: 0;
      font-size: calc(var(--u) * 2.75);
      line-height: 1.08;
      letter-spacing: -.028em;
    }
    h3 {
      margin-bottom: calc(var(--u) * .7);
      color: var(--blue);
      font-size: calc(var(--u) * 1.35);
      line-height: 1.15;
    }
    p, li, td, th { font-size: calc(var(--u) * 1.2); line-height: 1.4; }
    .lead { max-width: 50ch; color: #dbe2e9; font-size: calc(var(--u) * 1.55); line-height: 1.35; }
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
      background: linear-gradient(135deg, rgba(255,255,255,.035), rgba(255,255,255,.012));
    }
    .panel.selected { border-top-color: var(--green); }
    .panel.stopped { border-top-color: var(--red); }
    ul { margin: 0; padding-left: calc(var(--u) * 1.35); }
    li { margin: 0 0 calc(var(--u) * .55); }
    li::marker { color: var(--blue); }
    .note-line { margin-top: calc(var(--u) * 1.15); color: var(--muted); font-size: calc(var(--u) * 1.02); }

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
    .metric span { color: var(--muted); font-size: calc(var(--u) * .9); }

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
    .choice[data-status="Selected"] { border-color: var(--green); background: linear-gradient(145deg, #183126, #172129); }
    .choice[data-status="Stopped"] { border-color: var(--red); }
    .status { display: inline-block; margin-bottom: calc(var(--u) * 1.2); color: var(--muted); font-size: calc(var(--u) * .9); font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }

    .flow { display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--u) * 1.55); position: relative; }
    .flow::before { content: ""; position: absolute; top: calc(var(--u) * 2); left: 9%; right: 9%; height: 2px; background: var(--line); }
    .flow-step { position: relative; text-align: center; }
    .flow-number { position: relative; z-index: 1; display: grid; place-items: center; width: calc(var(--u) * 4); height: calc(var(--u) * 4); margin: 0 auto calc(var(--u) * 1); border-radius: 50%; color: #07111a; background: var(--blue); font-size: calc(var(--u) * 1.5); font-weight: 900; }
    .flow-step p { color: var(--muted); }
    .guardrail { margin-top: calc(var(--u) * 1.35); padding: calc(var(--u) * 1.05) calc(var(--u) * 1.35); border-left: 3px solid var(--green); background: rgba(120,214,167,.09); font-size: calc(var(--u) * 1.25); }

    .failure-grid { display: grid; grid-template-columns: .85fr 1.15fr; gap: calc(var(--u) * 2.3); }
    .primary-failure { padding: calc(var(--u) * 1.5); border-left: 3px solid var(--red); background: rgba(255,141,141,.08); font-size: calc(var(--u) * 1.42); line-height: 1.35; }
    .event { display: grid; grid-template-columns: calc(var(--u) * 6.2) 1fr; gap: calc(var(--u) * 1); margin-bottom: calc(var(--u) * .85); padding-bottom: calc(var(--u) * .85); border-bottom: 1px solid var(--line); }
    .event strong { color: var(--blue); font-size: calc(var(--u) * 1.04); }
    .event span { color: var(--muted); font-size: calc(var(--u) * 1.02); line-height: 1.3; }

    .conflict { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: calc(var(--u) * 1.2); }
    .source-value { padding: calc(var(--u) * 1.1); text-align: center; border: 1px solid var(--line); background: var(--panel); }
    .source-value strong { display: block; margin-top: calc(var(--u) * .35); color: var(--blue); font-size: calc(var(--u) * 3); line-height: 1; }
    .versus { color: var(--red); font-size: calc(var(--u) * 1.35); font-weight: 900; }
    .canonical-answer { margin: calc(var(--u) * 1.1) auto; text-align: center; }
    .canonical-answer strong { color: var(--green); font-size: calc(var(--u) * 1.65); }
    .outcome-table { width: 100%; border-collapse: collapse; }
    .outcome-table td { padding: calc(var(--u) * .62) calc(var(--u) * .8); border-bottom: 1px solid var(--line); font-size: calc(var(--u) * 1.02); }
    .outcome-table td:last-child { text-align: right; font-weight: 800; }

    .signal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: calc(var(--u) * 1.6); }
    .signal { padding: calc(var(--u) * 1.5); border-top: 3px solid var(--line); background: var(--panel); }
    .signal:first-child { border-top-color: var(--green); }
    .signal-value { color: var(--blue); font-size: calc(var(--u) * 1.65); font-weight: 850; }
    .next-step { margin-top: calc(var(--u) * 1.2); padding-top: calc(var(--u) * 1.05); border-top: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * 1.18); }

    .number-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: calc(var(--u) * 1.1); }
    .number { padding: calc(var(--u) * 1.05); border-top: 2px solid var(--blue-strong); background: var(--panel); }
    .number strong { display: block; color: var(--blue); font-size: calc(var(--u) * 2.4); line-height: 1; }
    .number span { color: var(--muted); font-size: calc(var(--u) * .92); }
    .tag-row { display: flex; flex-wrap: wrap; gap: calc(var(--u) * .6); margin-top: calc(var(--u) * 1.2); }
    .tag { padding: calc(var(--u) * .42) calc(var(--u) * .7); border: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * .9); }

    .score-wrap { align-content: start; }
    .score-table, .efficiency-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .score-table th, .score-table td, .efficiency-table th, .efficiency-table td { padding: calc(var(--u) * .5) calc(var(--u) * .52); border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
    .score-table th, .efficiency-table th { color: var(--blue); font-size: calc(var(--u) * .86); letter-spacing: .04em; }
    .score-table td, .efficiency-table td { font-size: calc(var(--u) * .88); }
    .score-table th:first-child, .score-table td:first-child, .efficiency-table th:first-child, .efficiency-table td:first-child { width: 25%; text-align: left; }
    .score-table tr.winner { background: rgba(120,214,167,.09); }
    .score-table tr.winner td:first-child { color: var(--green); font-weight: 850; }
    .score-table td.veto { color: var(--red); font-weight: 800; }
    .score-table td.pass { color: var(--green); font-weight: 800; }
    .efficiency-table th:first-child, .efficiency-table td:first-child { width: 29%; }
    .efficiency-table td:last-child { font-weight: 800; }
    .findings { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .9); margin-top: calc(var(--u) * 1); }
    .finding { padding: calc(var(--u) * .8); border-top: 1px solid var(--line); color: var(--muted); font-size: calc(var(--u) * .86); line-height: 1.3; }

    .recommendation-grid { display: grid; grid-template-columns: 1.15fr .85fr; gap: calc(var(--u) * 2); }
    .decision { padding: calc(var(--u) * 1.45); border-left: 4px solid var(--green); background: rgba(120,214,167,.09); font-size: calc(var(--u) * 1.42); line-height: 1.35; }
    .check-list { list-style: none; padding: 0; }
    .check-list li { position: relative; padding-left: calc(var(--u) * 1.35); }
    .check-list li::before { content: "✓"; position: absolute; left: 0; color: var(--green); font-weight: 900; }
    .gate-list { counter-reset: gate; list-style: none; padding: 0; }
    .gate-list li { counter-increment: gate; position: relative; padding-left: calc(var(--u) * 1.7); }
    .gate-list li::before { content: counter(gate); position: absolute; left: 0; color: var(--blue); font-weight: 900; }

    .risk-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: calc(var(--u) * .85) calc(var(--u) * 1.2); }
    .risk { padding-top: calc(var(--u) * .65); border-top: 1px solid var(--line); }
    .risk strong { display: block; margin-bottom: calc(var(--u) * .2); color: var(--amber); font-size: calc(var(--u) * 1.02); }
    .risk span { color: var(--muted); font-size: calc(var(--u) * .88); line-height: 1.25; }
    .close-line { margin-top: calc(var(--u) * .9); color: var(--blue); font-size: calc(var(--u) * 1.45); font-weight: 800; }

    .controls {
      position: absolute;
      inset: auto calc(var(--u) * 1.25) calc(var(--u) * .9) auto;
      z-index: 20;
      display: flex;
      align-items: center;
      gap: calc(var(--u) * .55);
    }
    .nav-button {
      display: grid;
      place-items: center;
      width: calc(var(--u) * 3.2);
      height: calc(var(--u) * 2.7);
      border: 1px solid #536577;
      color: var(--ink);
      background: rgba(16,21,27,.88);
      cursor: pointer;
    }
    .nav-button:hover, .nav-button:focus-visible { border-color: var(--blue); outline: none; background: #1b2834; }
    .nav-button:disabled { opacity: .3; cursor: default; }
    .page-count { min-width: calc(var(--u) * 4.3); color: var(--muted); text-align: center; font-size: calc(var(--u) * .92); font-variant-numeric: tabular-nums; }
    .progress { position: absolute; z-index: 21; inset: auto 0 0; height: calc(var(--u) * .24); background: rgba(255,255,255,.08); }
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
        display: grid !important;
        width: 13.333in;
        height: 7.5in;
        opacity: 1 !important;
        animation: none !important;
        break-after: page;
        page-break-after: always;
      }
      .slide:last-child { break-after: auto; page-break-after: auto; }
      .controls, .progress { display: none !important; }
    }
  </style>
</head>
<body>
  <main class="stage" aria-label="VoltStream slide presentation">
    <div class="deck" id="deck">${slides}</div>
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
      const pageCount = document.getElementById('page-count');
      const progressBar = document.getElementById('progress-bar');
      const status = document.getElementById('status');
      const stage = document.querySelector('.stage');
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
        status.textContent = 'Slide ' + (current + 1) + ' of ' + slides.length + ': ' + slides[current].dataset.title;
        document.title = slides[current].dataset.title + ' — ${escapeJs(deck.title)}';
        const hash = '#slide-' + (current + 1);
        if (updateHash && location.hash !== hash) history.replaceState(null, '', hash);
      }

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
      show(current);
    })();
  </script>
</body>
</html>`;

await writeFile(outputPath, html, "utf8");
console.log(`Built ${deck.slides.length} slides: ${outputPath}`);

function validateDeck(value) {
  if (!value || !Array.isArray(value.slides)) throw new Error("slides.json must contain a slides array");
  if (value.slides.length < 11 || value.slides.length > 13) throw new Error("Deck must contain 11–13 slides");
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

function renderSlide(slide, index, total) {
  const tone = slide.layout === "failure" || slide.layout === "case" ? "failure" : slide.layout === "risks" ? "risk" : "standard";
  return `<section class="slide" id="slide-${index + 1}" data-title="${escapeHtml(slide.title)}" data-tone="${tone}" aria-roledescription="slide" aria-label="Slide ${index + 1} of ${total}">
    <header class="slide-header"><p class="eyebrow">${escapeHtml(slide.eyebrow)}</p><h${index === 0 ? "1" : "2"}>${escapeHtml(slide.title)}</h${index === 0 ? "1" : "2"}></header>
    <div class="body ${slide.layout === "score-table" ? "score-wrap" : ""}">${renderBody(slide)}</div>
    <footer class="slide-footer"><span>VoltStream · synthetic/public data only</span><span class="section-label">${escapeHtml(slide.section)} · ${index + 1}/${total}</span></footer>
  </section>`;
}

function renderBody(slide) {
  switch (slide.layout) {
    case "hero":
      return `<div class="hero-body"><p class="lead">${escapeHtml(slide.lead)}</p><p class="decision-band">${escapeHtml(slide.boundary)}</p><div class="metric-row">${slide.metrics.map(metric => `<div class="metric"><strong>${escapeHtml(metric.value)}</strong><span>${escapeHtml(metric.label)}</span></div>`).join("")}</div></div>`;
    case "split":
      return `<p class="lead">${escapeHtml(slide.lead)}</p><div class="two-col"><div class="panel"><h3>${escapeHtml(slide.leftTitle)}</h3>${list(slide.leftItems)}</div><div class="panel selected"><h3>${escapeHtml(slide.rightTitle)}</h3>${list(slide.rightItems)}</div></div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "fact":
      return `<div class="fact-box"><div class="fact-label">Surprising fact</div><div><p class="fact-copy">${escapeHtml(slide.fact)}</p><p class="implication large-claim"><span class="accent">Design implication:</span> ${escapeHtml(slide.implication)}</p><p class="source-line">${escapeHtml(slide.sources)}</p></div></div>`;
    case "choices":
      return `<div class="choices">${slide.choices.map(choice => `<article class="choice" data-status="${escapeHtml(choice.status)}"><span class="status">${escapeHtml(choice.status)}</span><h3>${escapeHtml(choice.name)}</h3><p class="muted">${escapeHtml(choice.description)}</p></article>`).join("")}</div><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "flow":
      return `<div class="flow">${slide.steps.map(step => `<article class="flow-step"><div class="flow-number">${escapeHtml(step.number)}</div><h3>${escapeHtml(step.title)}</h3><p>${escapeHtml(step.detail)}</p></article>`).join("")}</div><p class="guardrail">${escapeHtml(slide.guardrail)}</p><p class="note-line">${escapeHtml(slide.excluded)}</p>`;
    case "failure":
      return `<div class="failure-grid"><div><p class="primary-failure">${escapeHtml(slide.primary)}</p><p class="note-line">${escapeHtml(slide.boundary)}</p></div><div>${slide.events.map(event => `<div class="event"><strong>${escapeHtml(event.label)}</strong><span>${escapeHtml(event.detail)}</span></div>`).join("")}</div></div>`;
    case "case":
      return `<div class="conflict"><div class="source-value"><span>${escapeHtml(slide.sourceValues[0].label)}</span><strong>${escapeHtml(slide.sourceValues[0].value)}</strong></div><div class="versus">≠</div><div class="source-value"><span>${escapeHtml(slide.sourceValues[1].label)}</span><strong>${escapeHtml(slide.sourceValues[1].value)}</strong></div></div><div class="canonical-answer"><span>Canonical field: <strong>${escapeHtml(slide.canonical)}</strong></span><br><span>Safe answer: <strong>${escapeHtml(slide.safeAnswer)}</strong></span></div><table class="outcome-table"><tbody>${slide.outcomes.map(outcome => `<tr><td>${escapeHtml(outcome.strategy)}</td><td>${escapeHtml(outcome.result)}</td><td class="${outcome.status.includes("unsafe") ? "bad" : outcome.status === "correct" ? "good" : "warn"}">${escapeHtml(outcome.status)}</td></tr>`).join("")}</tbody></table><p class="note-line">${escapeHtml(slide.takeaway)}</p>`;
    case "signal":
      return `<div class="signal-grid">${slide.signals.map(signal => `<article class="signal"><h3>${escapeHtml(signal.title)}</h3><p class="signal-value">${escapeHtml(signal.value)}</p><p class="muted">${escapeHtml(signal.description)}</p></article>`).join("")}</div><p class="next-step"><span class="accent">Next test:</span> ${escapeHtml(slide.next)}</p>`;
    case "testing":
      return `<div class="number-row">${slide.numbers.map(number => `<div class="number"><strong>${escapeHtml(number.value)}</strong><span>${escapeHtml(number.label)}</span></div>`).join("")}</div><div class="tag-row">${slide.coverage.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div><p class="note-line">${escapeHtml(slide.method)}</p><p class="guardrail">${escapeHtml(slide.gate)}</p>`;
    case "score-table":
      return `<table class="score-table"><thead><tr>${slide.columns.map(column => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead><tbody>${slide.rows.map(row => `<tr class="${row[0].startsWith("Codex") ? "winner" : ""}">${row.map((cell, index) => `<td class="${index === row.length - 1 ? (cell === "Pass" ? "pass" : cell === "Veto" ? "veto" : "") : ""}">${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table><p class="note-line">${escapeHtml(slide.note)}</p>`;
    case "efficiency":
      return `<table class="efficiency-table"><thead><tr><th>Strategy</th><th>Calls</th><th>Total latency</th><th>List cost</th><th>Status</th></tr></thead><tbody>${slide.rows.map(row => `<tr><td>${escapeHtml(row.strategy)}</td><td>${escapeHtml(row.calls)}</td><td>${escapeHtml(row.latency)}</td><td>${escapeHtml(row.cost)}</td><td class="${row.status === "Veto" ? "bad" : "good"}">${escapeHtml(row.status)}</td></tr>`).join("")}</tbody></table><div class="findings">${slide.findings.map(finding => `<div class="finding">${escapeHtml(finding)}</div>`).join("")}</div>`;
    case "recommendation":
      return `<div class="recommendation-grid"><div><p class="decision">${escapeHtml(slide.decision)}</p><h3>Operating guardrails</h3><ul class="check-list">${slide.guardrails.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div><div class="panel"><h3>Before expansion</h3><ol class="gate-list">${slide.beforeExpansion.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div></div>`;
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
