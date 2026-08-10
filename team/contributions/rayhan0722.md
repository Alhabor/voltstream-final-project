# 独立项目审阅记录 · RayHan0722

- **贡献者显示名称**：RayHan0722（GitHub 账号未设置显示名称，按流程使用用户名）
- **GitHub 用户名**：rayhan0722
- **UTC 审阅时间**：2026-08-10T19:13:45Z
- **被审阅的 `origin/main` commit SHA**：`6b66c454ff9d59a2a9f73b6fbf4efe02189a7750`

## 审阅重点

最终建议是否得到实验结果的支持。

## 阅读过的文件

- `README.md`
- `docs/QA_REPORT.md`
- `presentation/README.md`
- `evaluation/RESULTS.md`
- `docs/FINAL_RECOMMENDATION.md`（与审阅重点直接相关，一并阅读）

## 实际执行的验证命令与结果

| 命令 | 环境 | 结果 |
|---|---|---|
| `make check` | Python 3.9.5（仓库文档记载的 QA 环境） | **通过**（81 项测试全部 OK；fixture 校验通过：10 用例 / 10 答案 / 7 映射键；`verify_run.py` 通过：11 个冻结文件、60 个逐用例输出、6 个策略分数独立重算一致；compileall 通过；秘密扫描通过） |
| `make check` | Python 3.13.3（本机默认） | **失败**（仅 `verify-run` 一步：6 个策略的已保存分数与独立重算结果在浮点精确比较下不一致） |
| `git diff --check` | — | **通过**（无空白错误） |
| `python3 scripts/scan_secrets.py` | — | **通过**（未发现高信号密钥模式） |

关于 `make check` 在 Python 3.13.3 下的失败：该失败在未修改的 `origin/main` 上即存在，并非本次贡献引起。已核实原因：分数独立重算在较新 Python 版本下产生浮点 ULP 级差异，而校验采用精确浮点比较；在仓库文档记载的 Python 3.9.x 环境下同一命令完整通过（见上表第一行）。本审阅未修改任何项目文件来规避该差异。

## 独立观察（有证据支持）

最终建议与实验结果一致，且边界表述恰当：`evaluation/RESULTS.md` 的预注册阈值审计显示，**guarded Codex 是唯一无硬安全否决、且全部指标达到 ≥90% 的策略**（字段值 97.5%、问题召回 100%、路由 90%），而四个 DeepSeek 系策略全部在 EVG-009 上触发硬否决（选择了安装端口数 `8`、遗漏 `AMBIGUOUS_FIELD_VALUE`、以 `ACCEPT` 替代 `HUMAN_REVIEW`）。`docs/FINAL_RECOMMENDATION.md` 因而只建议"受人工复核的有限试点"，并明确该结果"支持进一步受控测试，而非证明生产就绪"——这一限定与 Codex 路由准确率恰好压在 90% 门槛线上的事实相符。同时，由于 Codex 货币成本不可得（`evaluation/RESULTS.md` 效率表中为 `unavailable`），建议书明确不做成本优势声明；"必须人工复核"的边界在 `docs/FINAL_RECOMMENDATION.md` 第 7 节试点设计与 `docs/QA_REPORT.md` H3 披露中前后一致。以上各点均可由仓库内实际内容直接支持。

## 本次审阅的局限

- 仅基于仓库文档与只读验证；未重跑模型推理（需提供商密钥，且按流程不允许）。
- 演示文稿仅依据 `presentation/README.md` 及其 `BUILD_RECEIPT.json` 记录，未在真实浏览器中复测。
- 分数核验仅覆盖本机可用的 Python 3.9.5 与 3.13.3 两个版本。
- 本审阅未修改、未运行任何会改写仓库内容的命令。

本次贡献仅为独立审阅记录，不修改源代码、评测数据、实验结果、演示内容或项目配置。
