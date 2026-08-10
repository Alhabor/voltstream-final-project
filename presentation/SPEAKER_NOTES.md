# Ten-Minute Bilingual Speaker Notes / 十分钟双语讲稿

These notes follow the 13-slide HTML deck. The time boxes total 10:00 and leave
the most time for the EVG-009 case, comparative evidence, and recommendation.

The second section provides a concise Chinese cue for every slide, for review
or a Chinese-language delivery. The evidence boundaries and 10:00 timing are
identical in both languages.

每页附有简洁中文提示，可用于中文审阅或中文现场讲述；中英文版本采用相同的证据边界，
总时长均控制在 10:00。

## Slide 1 · 0:00–0:35 — Decision first

VoltStream is an intake gate, not a complete data platform. Lead with the
decision: one guarded Codex configuration earned another limited,
human-reviewed test. No configuration earned production or autonomous-write
approval.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`docs/FINAL_RECOMMENDATION.md`.

## Slide 2 · 0:35–1:15 — Problem area and why

Contractor submissions can arrive as CSV, JSON, or prose. Intake is the
defensible slice because uncertainty is cheapest to stop before it reaches a
system of record. Do not claim Con Edison internal error rates, measured labor
savings, or regulatory compliance.

[Sources] `research/BACKGROUND_RESEARCH.md`; `docs/PROJECT_SCOPE.md`.

## Slide 3 · 1:15–1:55 — Research surprise

The surprising fact is that DOE AFDC itself combines daily network APIs,
spreadsheet/CSV imports, and manual records. Heterogeneity is not an edge case;
provenance and explicit unknowns matter as much as completeness.

[Sources] `research/SOURCES.md` entries for DOE AFDC, NREL, Con Edison
PowerReady, and NYSDPS Case 18-E-0138.

## Slide 4 · 1:55–2:35 — Ideation and scope choice

We considered a free-form cleaner and the full five-layer platform vision. The
first was hard to audit; the second was too broad for a real course prototype.
The selected slice proposes canonical values, preserves provenance, validates,
and routes uncertainty.

[Sources] `docs/PROJECT_SCOPE.md`; `build-log/2026-08-09-freeform-cleaning-hypothesis.md`.

## Slide 5 · 2:35–3:15 — How the gate works

Walk left to right: input, eight-field proposal plus source mappings,
deterministic validation, then routing. Emphasize that the language model never
chooses the final route. Briefly name the excluded production capabilities.

[Sources] `docs/ARCHITECTURE.md`; `src/voltstream/model_pipeline.py`.

## Slide 6 · 3:15–3:55 — What failed in development

The unrestricted cleaner was stopped as the default. Also show that failures
were preserved: nested JSON handling, Codex schema compatibility, and the v3
status check that raced final artifact writes. Clarify that v3 was not a model
or provider failure.

[Sources] `build-log/README.md`; preserved runs under `evaluation/runs/`.

## Slide 7 · 3:55–5:05 — EVG-009 core case

Slow down here. The payload contains `installed_ports=8` and `active_ports=6`,
while the schema has one `port_count`. The safe answer is null plus
HUMAN_REVIEW. Baseline was safely conservative; guarded Codex was correct; all
four DeepSeek-based paths chose 8 and ACCEPT. One unsupported critical choice
and unsafe route vetoed automation despite 95%+ field accuracy.

[Sources] `data/cases.jsonl`; `data/answer_key.jsonl`;
`evaluation/runs/2026-08-09-final-v4/*/predictions.jsonl`.

## Slide 8 · 5:05–5:45 — What might still work

DeepSeek Pro reached 96.4% mapping accuracy but retained the same safety veto;
its conditional validator feedback was not triggered. Codex's route miss was a
conservative text-lineage miss, suggesting two narrow repairs: deterministic
text-lineage extraction and raw-payload ambiguity checks.

[Sources] `evaluation/RESULTS.md`; `docs/FINAL_RECOMMENDATION.md`.

## Slide 9 · 5:45–6:25 — Testing design

Ten synthetic cases and the answer key were fixed first. Six strategies faced
the same cases and output/scoring contract with frozen strategy-specific
prompts. Metrics remain separate, and any unsafe under-route, critical
invention, or EVG-010 injection failure triggers a hard veto.

[Sources] `docs/EXPERIMENT_PLAN.md`; `data/README.md`;
`evaluation/EVALUATION_SPEC.md`.

## Slide 10 · 6:25–7:35 — Quality and safety evidence

Read the Codex row: 78/80 values, 56/56 structured mappings, 8/8 issue recall,
9/10 routes, zero unsafe under-routes, and zero unsupported values. The baseline
was safe but incomplete. Every DeepSeek-based strategy has one unsafe
under-route, so none is eligible. Do not collapse the table into one score.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/RESULTS.md`.

## Slide 11 · 7:35–8:10 — Cost and latency

The cascade saved one call and about 10%, below the preregistered 40% target,
while retaining the safety failure. Pro cost about 3.15 times guarded Flash
without clearing the veto. Codex was slower, its comparable price was
unavailable, and host token accounting is not directly comparable.

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/pricing_2026-08-09.json`.

## Slide 12 · 8:10–9:05 — Recommendation

Recommend an offline, fully human-reviewed pilot using approved data only.
Retain original payloads and provenance; forbid authoritative writes; apply
zero tolerance to unsupported critical values and unsafe under-routing. Before
expansion, implement both narrow controls and test a larger blind set.

[Sources] `docs/FINAL_RECOMMENDATION.md`.

## Slide 13 · 9:05–10:00 — Risks and close

Ten synthetic cases and one run cannot establish production reliability. Name
model drift, automation bias, contractor-format drift, privacy, reviewer load,
price/latency uncertainty, and schema limits. Close with: **the evidence
supports learning safely—not automating yet.**

[Sources] `docs/FINAL_RECOMMENDATION.md`; `docs/QA_REPORT.md`.

---

# 中文现场提示（同一 10:00 时间轴）

## 第 1 页 · 0:00–0:35 — 结论先行

VoltStream 是数据进入系统前的质量闸门，不是完整数据平台。先讲结论：只有受约束的
Codex 配置值得进入下一轮有限、全人工复核测试；没有任何配置获准生产部署或自动写入。

## 第 2 页 · 0:35–1:15 — 问题领域与选择理由

承包商数据可能是 CSV、JSON 或自然语言。入口是最可辩护的切片，因为不确定性在进入
权威系统前最容易被拦截。不要声称掌握 Con Edison 内部错误率、人工节省量或合规成效。

## 第 3 页 · 1:15–1:55 — 研究中的意外发现

DOE AFDC 自身也同时使用每日网络 API、表格/CSV 导入和人工记录。异构不是边缘情况；
来源追踪和明确保留未知值，与完整性同样重要。

## 第 4 页 · 1:55–2:35 — 构思与范围选择

我们比较了自由清洗器和完整五层平台。前者难以审计，后者超出课程原型范围。最终切片
只提出规范值、保留来源、执行验证，并对不确定性进行路由。

## 第 5 页 · 2:35–3:15 — 闸门如何运行

从左到右讲输入、八字段与来源映射、确定性验证、最终路由。强调语言模型不能决定最终
路由，并简要说明未纳入原型的生产能力。

## 第 6 页 · 3:15–3:55 — 开发中失败的方案

自由清洗器被停止作为默认方案。展示保留下来的失败：嵌套 JSON、Codex 结构兼容，以及
v3 的进程状态检查与最终文件写入发生竞态；v3 不是模型或供应商失败。

## 第 7 页 · 3:55–5:05 — EVG-009 核心案例

此处放慢。原始数据同时有 `installed_ports=8` 和 `active_ports=6`，而规范结构只有一个
`port_count`。安全答案是空值加人工复核。基线虽保守但安全，Codex 回答正确，四条
DeepSeek 路径都选择 8 并 ACCEPT；一次关键字段的不受支持选择和不安全路由足以否决
自动化，哪怕字段准确率超过 95%。

## 第 8 页 · 5:05–5:45 — 仍可能有效的方向

DeepSeek Pro 的映射准确率达到 96.4%，但仍触发相同安全否决，条件式验证反馈也未触发。
Codex 的路由错误是保守的文本来源遗漏，提示两个窄修复方向：确定性文本来源提取，以及
原始数据歧义检查。

## 第 9 页 · 5:45–6:25 — 测试设计

先冻结十个合成案例和答案，再让六种策略使用相同案例与输出/评分合同，并冻结各自提示
词。指标分开报告；任何不安全降级、关键字段编造或 EVG-010 注入失败，都触发硬性否决。

## 第 10 页 · 6:25–7:35 — 质量与安全证据

读 Codex 这一行：78/80 个值、56/56 个结构化映射、8/8 问题召回、9/10 路由，且没有
不安全降级或不受支持值。基线安全但不完整；每条 DeepSeek 路径都有一次不安全降级，
因此均不合格。不要把这些指标压缩成一个总分。

## 第 11 页 · 7:35–8:10 — 成本与延迟

级联只少调用一次、节省约 10%，低于预注册的 40% 目标，同时保留安全失败。Pro 成本
约为受约束 Flash 的 3.15 倍，仍未解除否决。Codex 更慢、缺少可比价格，宿主 token
统计也不能直接比较。

## 第 12 页 · 8:10–9:05 — 建议

建议只用批准数据进行离线、全人工复核试点。保留原始载荷和来源，禁止写入权威系统；
对关键字段的不受支持值和不安全降级零容忍。扩展前先实现两个窄控制，并测试更大的盲测集。

## 第 13 页 · 9:05–10:00 — 风险与收束

十个合成案例和一次运行不能证明生产可靠性。点出模型漂移、自动化偏见、承包商格式漂移、
隐私、复核负担、成本/延迟不确定性和结构限制。最后收束：**证据支持安全地继续学习，
而不是现在就自动化。**
