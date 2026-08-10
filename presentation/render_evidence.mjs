import { createHash } from "node:crypto";
import { extname } from "node:path";

/** Render reviewed evidence as a readable, self-contained page.
 *
 * The unchanged source file remains beside this viewer and is always available
 * through the secondary "Open raw file" action. All rich rendering starts from
 * escaped text or parsed structured data; source HTML is never trusted.
 */
export function renderEvidenceViewer(source, content) {
  const text = content.toString("utf8");
  const sha256 = createHash("sha256").update(content).digest("hex");
  const rawName = source.split("/").at(-1);
  const returnPath = `${"../".repeat(source.split("/").length)}index.html`;
  const kind = viewerKind(source);
  const rendered = renderByKind(kind, text);
  const kindLabel = { markdown: "Rendered Markdown", json: "Pretty JSON", jsonl: "JSON Lines", csv: "Data table", code: "Source code", text: "Text file" }[kind];

  return `<!doctype html>
<html lang="en" data-viewer-kind="${kind}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><title>${escapeHtml(rawName)} — VoltStream evidence</title>
<style>${viewerCss()}</style></head>
<body><header class="topbar"><div class="topbar-inner"><div class="identity"><span class="product">VoltStream evidence</span><span class="kind">${kindLabel}</span><h1>${escapeHtml(source)}</h1><div class="checksum">SHA-256 <code>${sha256}</code></div></div><nav class="actions"><a class="button primary" href="${escapeHtml(rawName)}">Open raw file</a><a class="button" href="${returnPath}">Return to presentation</a><button class="button" type="button" onclick="window.print()">Print</button></nav></div></header>
<main class="viewer-shell">${rendered}</main>${viewerScript(kind)}</body></html>`;
}

export function renderEvidenceDirectory(directoryPath, files) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark light"><title>${escapeHtml(directoryPath)} — VoltStream evidence</title><style>${viewerCss()}</style></head><body><header class="topbar"><div class="topbar-inner"><div class="identity"><span class="product">VoltStream evidence</span><span class="kind">Evidence set</span><h1>${escapeHtml(directoryPath)}</h1></div></div></header><main class="viewer-shell"><article class="document markdown-body"><h2>Published review files</h2><p>This directory contains the frozen run files referenced by the final recommendation.</p><ul>${files.map(file => `<li><a href="${escapeHtml(file)}.html">View ${escapeHtml(file)}</a> <span class="secondary">·</span> <a href="${escapeHtml(file)}">raw file</a></li>`).join("")}</ul></article></main></body></html>`;
}

function viewerKind(source) {
  if (source.endsWith(".jsonl")) return "jsonl";
  const extension = extname(source).toLowerCase();
  if (extension === ".md") return "markdown";
  if (extension === ".json") return "json";
  if (extension === ".csv") return "csv";
  if ([".py", ".js", ".mjs", ".ts", ".sh"].includes(extension)) return "code";
  return "text";
}

function renderByKind(kind, text) {
  if (kind === "markdown") return `<article class="document markdown-body">${renderMarkdown(text)}</article>`;
  if (kind === "json") return `<article class="document data-document"><pre class="json-view"><code>${highlightJson(JSON.stringify(JSON.parse(text), null, 2))}</code></pre></article>`;
  if (kind === "jsonl") return renderJsonLines(text);
  if (kind === "csv") return renderCsv(text);
  if (kind === "code") return renderCode(text);
  return `<article class="document"><pre class="plain-text">${escapeHtml(text)}</pre></article>`;
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n?/g, "\n").split("\n");
  const output = [];
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) { index += 1; continue; }

    const fence = line.match(/^```([^\s`]*)\s*$/);
    if (fence) {
      const code = [];
      index += 1;
      while (index < lines.length && !/^```\s*$/.test(lines[index])) code.push(lines[index++]);
      if (index < lines.length) index += 1;
      output.push(`<pre class="code-block"><code data-language="${escapeHtml(fence[1] || "text")}">${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      output.push(`<h${level}>${renderInline(heading[2], sourceLink)}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      output.push("<hr>");
      index += 1;
      continue;
    }

    if (line.includes("|") && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1])) {
      const headers = splitTableRow(line);
      index += 2;
      const rows = [];
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) rows.push(splitTableRow(lines[index++]));
      output.push(`<div class="table-scroll"><table class="data-table"><thead><tr>${headers.map(cell => `<th>${renderInline(cell, sourceLink)}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${headers.map((_, cellIndex) => `<td>${renderInline(row[cellIndex] || "", sourceLink)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }

    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      const tag = unordered ? "ul" : "ol";
      const items = [];
      while (index < lines.length) {
        const match = tag === "ul" ? lines[index].match(/^\s*[-*+]\s+(.+)$/) : lines[index].match(/^\s*\d+[.)]\s+(.+)$/);
        if (!match) break;
        items.push(`<li>${renderInline(match[1], sourceLink)}</li>`);
        index += 1;
      }
      output.push(`<${tag}>${items.join("")}</${tag}>`);
      continue;
    }

    if (/^>\s?/.test(line)) {
      const quote = [];
      while (index < lines.length && /^>\s?/.test(lines[index])) quote.push(lines[index++].replace(/^>\s?/, ""));
      output.push(`<blockquote>${renderInline(quote.join(" "), sourceLink)}</blockquote>`);
      continue;
    }

    const paragraph = [line.trim()];
    index += 1;
    while (index < lines.length && lines[index].trim() && !startsBlock(lines, index)) paragraph.push(lines[index++].trim());
    output.push(`<p>${renderInline(paragraph.join(" "), sourceLink)}</p>`);
  }
  return output.join("\n");
}

function startsBlock(lines, index) {
  const line = lines[index];
  return /^(?:#{1,6}\s+|```|\s*[-*+]\s+|\s*\d+[.)]\s+|>\s?|\s*(?:-{3,}|\*{3,}|_{3,})\s*$)/.test(line)
    || (line.includes("|") && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1]));
}

function renderInline(value, linkResolver) {
  const code = [];
  let text = String(value).replace(/`([^`]+)`/g, (_, content) => {
    const token = `\u0000CODE${code.length}\u0000`;
    code.push(`<code>${escapeHtml(content)}</code>`);
    return token;
  });
  text = escapeHtml(text);
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const resolved = linkResolver(decodeHtml(href));
    const external = /^https?:\/\//.test(resolved);
    return `<a href="${escapeHtml(resolved)}"${external ? ' target="_blank" rel="noopener noreferrer"' : ""}>${label}</a>`;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  text = text.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  text = text.replace(/\u0000CODE(\d+)\u0000/g, (_, number) => code[Number(number)]);
  return text;
}

function sourceLink(href) {
  const trimmed = href.trim();
  if (/^(?:https?:|mailto:|#)/.test(trimmed)) return trimmed;
  // Reject unapproved schemes such as javascript: even though the current
  // manifest contains only reviewed files. This keeps future Markdown safe.
  if (/^[a-z][a-z0-9+.-]*:/i.test(trimmed)) return "#";
  const [path, fragment = ""] = trimmed.split("#", 2);
  const renderedPath = path.endsWith(".md") ? `${path}.html` : path;
  return fragment ? `${renderedPath}#${fragment}` : renderedPath;
}

function splitTableRow(line) {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(cell => cell.trim());
}

function renderJsonLines(text) {
  const records = text.split(/\r?\n/).filter(line => line.trim()).map((line, index) => ({ index, value: JSON.parse(line) }));
  return `<article class="document data-document"><div class="data-toolbar"><strong>${records.length} records</strong><span><button type="button" data-action="expand">Expand all</button><button type="button" data-action="collapse">Collapse all</button></span></div><div class="records">${records.map(({ index, value }) => {
    const identity = value.case_id || value.id || value.strategy || `Record ${index + 1}`;
    const description = value.description || value.format || value.expected_decision || "JSON object";
    return `<details class="record"${index === 0 ? " open" : ""}><summary><span>${escapeHtml(identity)}</span><small>${escapeHtml(String(description))}</small></summary><pre class="json-view"><code>${highlightJson(JSON.stringify(value, null, 2))}</code></pre></details>`;
  }).join("")}</div></article>`;
}

function renderCsv(text) {
  const rows = parseCsv(text);
  const [headers = [], ...body] = rows;
  return `<article class="document data-document"><div class="data-toolbar"><strong>${body.length} rows · ${headers.length} columns</strong></div><div class="table-scroll"><table class="data-table csv-table"><thead><tr>${headers.map(header => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead><tbody>${body.map(row => `<tr>${headers.map((_, index) => `<td>${escapeHtml(row[index] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div></article>`;
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quoted && character === '"' && text[index + 1] === '"') { cell += '"'; index += 1; }
    else if (character === '"') quoted = !quoted;
    else if (!quoted && character === ",") { row.push(cell); cell = ""; }
    else if (!quoted && (character === "\n" || character === "\r")) {
      if (character === "\r" && text[index + 1] === "\n") index += 1;
      row.push(cell); rows.push(row); row = []; cell = "";
    } else cell += character;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}

function renderCode(text) {
  const lines = text.replace(/\r\n?/g, "\n").split("\n");
  return `<article class="document code-document"><div class="data-toolbar"><strong>${lines.length} lines</strong></div><ol class="code-lines">${lines.map(line => `<li><code>${escapeHtml(line) || "&nbsp;"}</code></li>`).join("")}</ol></article>`;
}

function highlightJson(value) {
  return escapeHtml(value).replace(/(&quot;(?:\\.|[^&])*?&quot;)(\s*:)?|\b(true|false|null)\b|-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/gi, (match, string, keyMarker, literal) => {
    if (string) return `<span class="${keyMarker ? "json-key" : "json-string"}">${string}${keyMarker || ""}</span>`;
    if (literal) return `<span class="json-literal">${match}</span>`;
    return `<span class="json-number">${match}</span>`;
  });
}

function viewerScript(kind) {
  if (kind !== "jsonl") return "";
  return `<script>document.querySelector('[data-action="expand"]').addEventListener('click',()=>document.querySelectorAll('details').forEach(item=>item.open=true));document.querySelector('[data-action="collapse"]').addEventListener('click',()=>document.querySelectorAll('details').forEach(item=>item.open=false));</script>`;
}

function viewerCss() {
  return `:root{color-scheme:dark light;--bg:#0d1218;--surface:#141c24;--surface2:#1a2530;--ink:#edf2f7;--muted:#9eabb8;--line:#334454;--accent:#73c4ff;--accent2:#75d2a1;--warn:#e9bd65;--code:#101820;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink)}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink)}.topbar{position:sticky;z-index:10;top:0;border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--bg) 94%,transparent);backdrop-filter:blur(12px)}.topbar-inner{display:flex;max-width:1280px;margin:auto;padding:1.15rem 2rem;align-items:flex-end;justify-content:space-between;gap:2rem}.identity{min-width:0}.product{color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}.kind{margin-left:.65rem;padding:.18rem .45rem;border:1px solid var(--line);border-radius:3px;color:var(--muted);font-size:.72rem}.identity h1{margin:.45rem 0 .25rem;overflow-wrap:anywhere;font-size:1.18rem;line-height:1.25}.checksum{color:var(--muted);font-size:.74rem;overflow-wrap:anywhere}.checksum code{color:var(--muted)}.actions{display:flex;flex:0 0 auto;flex-wrap:wrap;justify-content:flex-end;gap:.55rem}.button,.data-toolbar button{display:inline-flex;align-items:center;padding:.48rem .72rem;border:1px solid var(--line);border-radius:4px;color:var(--ink);background:transparent;font:inherit;font-size:.82rem;text-decoration:none;cursor:pointer}.button:hover,.button:focus-visible,.data-toolbar button:hover,.data-toolbar button:focus-visible{border-color:var(--accent);outline:none;color:var(--accent)}.button.primary{border-color:var(--accent);color:var(--accent)}.viewer-shell{max-width:1280px;margin:0 auto;padding:2.25rem 2rem 5rem}.document{max-width:960px;margin:0 auto}.data-document,.code-document{max-width:1200px}.markdown-body{font-family:Georgia,"Times New Roman",serif;font-size:1.05rem;line-height:1.7}.markdown-body h1,.markdown-body h2,.markdown-body h3,.markdown-body h4{font-family:Inter,ui-sans-serif,system-ui,sans-serif;line-height:1.22}.markdown-body h1{margin:0 0 1.5rem;font-size:2.35rem}.markdown-body h2{margin:2.8rem 0 1rem;padding-bottom:.45rem;border-bottom:1px solid var(--line);font-size:1.7rem}.markdown-body h3{margin:2rem 0 .8rem;color:var(--accent);font-size:1.28rem}.markdown-body h4{margin:1.5rem 0 .7rem;font-size:1.08rem}.markdown-body p{margin:.75rem 0 1.1rem}.markdown-body li{margin:.35rem 0}.markdown-body a{color:var(--accent);text-underline-offset:.16em}.markdown-body code{padding:.12rem .3rem;border-radius:3px;background:var(--surface2);color:#f0ca78;font:90% ui-monospace,SFMono-Regular,Menlo,monospace}.markdown-body blockquote{margin:1.4rem 0;padding:.6rem 1.2rem;border-left:3px solid var(--accent);color:var(--muted);background:var(--surface)}hr{margin:2.5rem 0;border:0;border-top:1px solid var(--line)}.code-block,.json-view,.plain-text{margin:1rem 0;padding:1.15rem 1.25rem;border:1px solid var(--line);border-radius:6px;background:var(--code);overflow:auto;color:#d9e4ee;font: .88rem/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;tab-size:2}.table-scroll{margin:1.25rem 0;overflow:auto;border:1px solid var(--line);border-radius:6px}.data-table{width:100%;border-collapse:collapse;font-size:.86rem}.data-table th{position:sticky;top:0;padding:.72rem .8rem;text-align:left;color:var(--accent);background:var(--surface2);font-weight:750}.data-table td{padding:.66rem .8rem;border-top:1px solid var(--line);vertical-align:top}.data-table tbody tr:nth-child(even){background:color-mix(in srgb,var(--surface) 60%,transparent)}.data-toolbar{display:flex;margin-bottom:1rem;align-items:center;justify-content:space-between;gap:1rem;color:var(--muted)}.data-toolbar span{display:flex;gap:.45rem}.records{display:grid;gap:.7rem}.record{border:1px solid var(--line);border-radius:6px;background:var(--surface)}.record summary{display:flex;padding:.85rem 1rem;align-items:baseline;justify-content:space-between;gap:1rem;cursor:pointer}.record summary span{color:var(--accent);font-weight:800}.record summary small{color:var(--muted)}.record .json-view{margin:0;border:0;border-top:1px solid var(--line);border-radius:0 0 6px 6px}.json-key{color:#84c8ff}.json-string{color:#9bdbb7}.json-number{color:#f0c979}.json-literal{color:#d4a5ff}.code-lines{margin:0;padding:1rem 0 1rem 4.5rem;border:1px solid var(--line);border-radius:6px;background:var(--code);color:#607587;font: .86rem/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}.code-lines li{padding:0 .9rem}.code-lines li::marker{font-size:.72rem}.code-lines code{display:block;white-space:pre;color:#d9e4ee}.secondary{color:var(--muted)}@media(max-width:760px){.topbar-inner{padding:1rem;align-items:stretch;flex-direction:column}.actions{justify-content:flex-start}.viewer-shell{padding:1.5rem 1rem 4rem}.markdown-body h1{font-size:1.8rem}.checksum code{display:block;margin-top:.2rem}.record summary{align-items:flex-start;flex-direction:column}.data-toolbar{align-items:flex-start;flex-direction:column}}@media(prefers-color-scheme:light){:root{--bg:#f4f7fa;--surface:#e9eff4;--surface2:#dfe8ef;--ink:#182532;--muted:#5c6c7b;--line:#aab9c6;--accent:#006fa9;--accent2:#14724a;--warn:#7d5708;--code:#16202a}.code-block,.json-view,.plain-text,.code-lines{color:#edf3f8}.markdown-body code{background:#dfe8ef;color:#704c00}}@media print{.topbar{position:static}.actions{display:none}.viewer-shell{max-width:none;padding:1rem}.document{max-width:none}.record{break-inside:avoid}.topbar-inner{max-width:none;padding:0 0 1rem}.code-block,.json-view,.plain-text,.code-lines{white-space:pre-wrap;overflow-wrap:anywhere}.table-scroll{overflow:visible}}`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[character]);
}

function decodeHtml(value) {
  return value.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
}
