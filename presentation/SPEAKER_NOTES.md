# Ten-Minute Bilingual Speaker Notes / 十分钟双语讲稿

These notes follow the 13-slide audience-first HTML deck. The slides themselves
contain every fact and definition needed to follow the story; the notes add
transitions and emphasis rather than missing background. The time boxes total
10:00.

这份讲稿对应 13 页“零背景观众版”HTML。理解项目所需的事实和定义都已经写在页面上；
讲稿只补充衔接和强调，不承担补齐背景的任务。总时长为 10:00。

## Slide 1 · 0:00–0:40 — The question

Start with the business situation, not the result. Con Edison receives charger
information through outside parties, and the files do not always describe the
same thing in the same way. Our question is deliberately narrow: can AI help
organize those submissions without guessing when the evidence conflicts?

**中文讲法：** 先交代业务场景，不要先讲模型。Con Edison 通过外部机构收集充电桩
信息，文件的格式、名称和数值可能不同。我们的项目只问一个问题：AI 能否帮忙整理，
同时在证据冲突时不擅自猜答案？

[Sources] `docs/PROJECT_SCOPE.md`; user-provided Con Edison use-case brief.

## Slide 2 · 0:40–1:20 — Why the first check matters

Walk through the two columns as one employee's task. A file arrives; the
employee needs to decide which value is trustworthy, where it came from, and
whether another person must investigate. This project stops at that checkpoint
and makes no claim about internal savings or compliance.

**中文讲法：** 把左右两栏当作一名工作人员面对的任务：材料来了，哪个数可信？来自
哪里？是否需要继续调查？本项目只做到这个检查点，不声称已经节省人工或实现合规。

[Sources] `docs/PROJECT_SCOPE.md`; `research/BACKGROUND_RESEARCH.md`.

## Slide 3 · 1:20–2:00 — Research finding

The important research finding is that mixed sources are normal, not a rare
mistake. Even the national DOE directory combines automated feeds, imported
files, and human-maintained records. Therefore, a reliable result must expose
unknowns and sources instead of merely looking complete.

**中文讲法：** 研究中最重要的发现是：混杂来源不是偶发错误。美国能源部的全国目录
本身也结合自动数据、导入文件和人工维护。因此系统必须展示“不知道”和信息来源，
不能只追求表面完整。

[Sources] `research/SOURCES.md` entries for DOE AFDC, NREL, Con Edison
PowerReady, and NYSDPS Case 18-E-0138.

## Slide 4 · 2:00–2:40 — Scope choice

Explain the three options in ordinary language. Free rewriting was difficult to
trust, while a complete enterprise platform was impossible to test honestly in
the course. We selected one useful checkpoint: organize, check, and hand
uncertain cases to a person.

**中文讲法：** 三个方案中，自由改写很难发现 AI 在什么时候猜测；完整平台又大到无法
在课程中诚实验证。最终只做一个真正可测试的检查点：整理、检查、把不确定情况交给人。

[Sources] `docs/PROJECT_SCOPE.md`;
`build-log/2026-08-09-freeform-cleaning-hypothesis.md`.

## Slide 5 · 2:40–3:25 — What the prototype does

Move left to right through the four verbs: read, organize, check, decide. The
eight output boxes are named at the bottom so the audience does not need the
repository. Clarify the division of responsibility: AI suggests; ordinary code
applies explicit safety rules.

**中文讲法：** 按“读取、整理、检查、处理”四步讲。页面底部已经列出 8 项信息，观众
不需要查看代码仓库。必须强调：AI 只提出建议，普通程序按照明确规则作出处理决定。

[Sources] `docs/ARCHITECTURE.md`; `src/voltstream/model_pipeline.py`;
`evaluation/canonical_record.schema.json`.

## Slide 6 · 3:25–4:05 — What failed

Lead with the product failure: the first cleaner chose a number despite a
conflict. Then briefly show that we also kept evidence of mistakes in the test
setup. The discarded run was excluded because the test process changed, not
because a model provider failed.

**中文讲法：** 先讲产品失败：最初的方案面对冲突仍然选了一个数字。再简要说明测试
过程中也出现并修复了问题。作废运行是测试流程变化造成的，不是模型供应商故障。

[Sources] `build-log/README.md`; preserved runs under `evaluation/runs/`.

## Slide 7 · 4:05–5:15 — The 8-versus-6 case

Slow down. Eight ports were installed, but only six were active. The output has
one port-count box, so neither number is automatically correct. Explain the
codes once: `null` means leave the box blank; `HUMAN_REVIEW` means ask a person;
`ACCEPT` means the record would continue. Four DeepSeek approaches chose 8 and
continued. That single unsafe decision blocked automation.

**中文讲法：** 此处放慢。已经安装 8 个端口，目前启用 6 个；系统却只有一个“端口数”
位置，所以不能自动认定其中一个正确。`null` 是留空，`HUMAN_REVIEW` 是交给人，
`ACCEPT` 是继续使用。四种 DeepSeek 方案选择 8 并放行，因此被安全规则否决。

[Sources] `data/cases.jsonl`; `data/answer_key.jsonl`;
`evaluation/runs/2026-08-09-final-v4/*/predictions.jsonl`.

## Slide 8 · 5:15–5:55 — What may still work

The useful lesson is not simply that one model beat another. Codex's one wrong
decision was cautious, while DeepSeek Pro still failed the conflict case. The
next improvement is therefore a direct conflict rule plus better source
tracking for text.

**中文讲法：** 结论不是简单的模型排名。Codex 唯一的处理错误是过于谨慎，而
DeepSeek Pro 仍然败在冲突案例。所以下一步应先增加直接的冲突规则，再改善文字来源
定位，而不是盲目换更大的模型。

[Sources] `evaluation/RESULTS.md`; `docs/FINAL_RECOMMENDATION.md`.

## Slide 9 · 5:55–6:35 — A fair test

Explain that all ten submissions were made for this experiment and contained
no company records. We wrote the answer sheet first and kept cases, scoring,
and AI instructions fixed. The test included ordinary files, uncertainty,
missing data, and a malicious instruction hidden inside data.

**中文讲法：** 十份材料都是专为实验编写的模拟数据，不含公司记录。我们先写正确答案，
再固定案例、评分和 AI 指令。测试既有普通材料，也有冲突、缺失、正确回答“不知道”，
以及夹带恶意指令的材料。

[Sources] `docs/EXPERIMENT_PLAN.md`; `data/README.md`;
`evaluation/EVALUATION_SPEC.md`.

## Slide 10 · 6:35–7:40 — Quality and safety result

Define the table before reading it: values are extracted answers; sources are
the original fields supporting them; decisions are whether to continue, ask a
person, or stop. Codex with safety rules was the only AI approach with high
accuracy and zero unsafe approvals. The DeepSeek rows were vetoed by one unsafe
approval each, regardless of their averages.

**中文讲法：** 先解释表格：数值是提取出的答案，来源是原文件中支撑答案的位置，处理
结果是继续、交给人或停止。带安全规则的 Codex 是唯一同时保持高准确率且没有错误
放行的 AI 方案。DeepSeek 各方案即使平均分高，也因一次错误放行被否决。

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/RESULTS.md`.

## Slide 11 · 7:40–8:15 — Time and cost

Every time shown is the total for all ten cases, not one case. The DeepSeek
options were faster and had low listed API cost, but they failed the safety
test. Codex was slower, and we did not have a comparable price, so this project
does not claim a cost winner.

**中文讲法：** 表中时间是 10 个案例的总时间，不是单个案例。DeepSeek 更快、标价更低，
但没有通过安全测试。Codex 更慢，又缺少可比价格，因此本项目不声称存在成本赢家。

[Sources] `evaluation/runs/2026-08-09-final-v4/summary.csv`;
`evaluation/pricing_2026-08-09.json`.

## Slide 12 · 8:15–9:10 — Recommendation

Recommend only a small offline trial. Every result stays under human review,
the original file and source for each value remain visible, and the tool cannot
write to an official system. One invented critical value or unsafe approval
stops the trial.

**中文讲法：** 最终只建议小规模离线试点。每份结果都由人复核，保留原文件和每个数值
的来源，工具不能写入正式系统。一旦出现关键数值编造或错误放行，立即停止试点。

[Sources] `docs/FINAL_RECOMMENDATION.md`.

## Slide 13 · 9:10–10:00 — Limits and close

Ten made-up examples establish a prototype result, not daily reliability. Name
the remaining unknowns in plain language: changing models, overtrust, new file
formats, privacy, human workload, and an oversimplified eight-field design.
Close with the exact boundary: the evidence supports another careful
experiment, not automation.

**中文讲法：** 十份模拟材料只能证明原型结果，不能证明日常可靠。剩余未知包括模型变化、
过度信任、新文件格式、隐私、人工工作量，以及 8 项信息是否过于简单。最后收束：证据
只支持下一次谨慎实验，不支持自动化。

[Sources] `docs/FINAL_RECOMMENDATION.md`; `docs/QA_REPORT.md`.
