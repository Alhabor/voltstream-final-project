# Final HTML Presentation / 最终 HTML 演示

`index.html` is a self-contained, 17-slide, 16:9 presentation for the final
10-minute briefing. The same file contains complete English and Chinese
versions plus dark and light themes. It displays one full-viewport slide at a
time and needs no server, network connection, external font, or sibling runtime
asset.

English is the live presentation language and is written for a first-time,
English-speaking audience. Chinese is a structurally matched review mirror for
the project owner. The deck introduces the physical charging-site context and
defines each business object, decision, model family, test measure, and safety
term before or on first use. It does not rely on the repository, speaker notes,
or assignment brief to supply missing context.

`index.html` 是一份自包含的 17 页、16:9、10 分钟汇报演示。同一个文件内置完整的
中英文版本与深浅色主题，每次只显示一张完整幻灯片；直接打开即可，不依赖服务器、
网络、外部字体或同目录运行资源。

英文是现场主版本，面向完全不了解项目的英文观众；中文仅作为结构一致的审阅镜像。
演示先解释真实充电设施，再介绍业务问题和原型；每个业务对象、处理结果、模型类别、
测试指标和安全术语都会在首次出现前或当页解释，不依赖代码仓库、讲稿或作业说明补背景。

## Review modes / 审阅模式

The default is English with the dark theme. The two compact controls in the
upper right switch language (`中` / `EN`) and theme (`☀` / `☾`). They remain
visually quiet during the talk and become fully visible on hover or keyboard
focus; touch devices retain larger tap targets. Both choices are saved locally,
so refresh, hash navigation, and reopening the file preserve the last review
mode. Switching does not change the current slide.

默认显示英文深色版。右上角两个紧凑控件分别切换语言（`中` / `EN`）和主题（`☀` /
`☾`）。演示过程中控件保持低存在感，鼠标悬停或键盘聚焦时才完整显示；触屏设备仍保留
较大的点击区域。浏览器会在本地保存两项选择，因此刷新、使用 hash 导航或重新打开时，
均会恢复上一次的审阅模式；切换语言或主题不会改变当前页码。

## Regenerate / 重新生成

The factual English source is `slides.json`; the structurally matched Chinese
source is `slides.zh.json`. Layout, styling, navigation, localization, and HTML
generation are maintained in `build.mjs`. From the repository root, run:

英文事实源文件为 `slides.json`，结构对应的中文源文件为 `slides.zh.json`；布局、样式、
导航、本地化与 HTML 生成逻辑位于 `build.mjs`。在仓库根目录运行：

```bash
node presentation/build.mjs
```

The builder validates that there are at least 11 slides, slide IDs are unique, the
eight required course sections occur in order, and both languages have
identical slide IDs, layouts, and canonical section order before replacing
`presentation/index.html`.

生成器会在覆盖 `presentation/index.html` 前验证：总页数不少于 11 页、ID 不重复、
课程要求的八个部分顺序正确，以及中英文版本的 ID、布局和规范章节完全对应。

## Open / 打开

Double-click `presentation/index.html`, drag it into a browser, or run:

双击 `presentation/index.html`、将其拖入浏览器，或运行：

```bash
open presentation/index.html
```

The current slide is stored in the URL hash. A URL ending in `#slide-6` opens
slide 6 and returns to it after refresh. / 当前页码保存在 URL hash 中；以
`#slide-6` 结尾的地址会打开第 6 页，刷新后仍恢复到该页。

## Controls / 操作

- Next / 下一页：`→`、`↓`、空格或 `PageDown`
- Previous / 上一页：`←`、`↑` 或 `PageUp`
- First / last / 首尾页：`Home` / `End`
- Fullscreen / 全屏：`F`；再次按 `F` 退出
- On screen / 屏幕按钮：上一页、下一页、全屏、语言与主题
- Trackpad or mouse / 触控板或鼠标：横向或纵向滚轮手势
- Touchscreen / 触屏：横向滑动

The page counter and bottom progress bar update with every navigation method.
The deck honors `prefers-reduced-motion`. / 所有导航方式都会同步更新页码、URL hash
与底部进度条，并支持 `prefers-reduced-motion`。

## Print or save as PDF / 打印或另存 PDF

Select the desired language and theme first, then use the browser's Print
command. Only the current language is printed. The stylesheet places each of
the 17 slides on its own 16:9 landscape page. Enable background graphics if the
browser offers that option.

先选择需要的语言和主题，再使用浏览器的“打印”功能；打印稿只包含当前语言。打印
样式会将 17 张幻灯片分别放在独立的 16:9 横向页面上。如浏览器提供选项，请启用
“背景图形”。

## Verification / 验证

`BUILD_RECEIPT.json` records the generated artifact and browser QA. The deck
passed 417 real-Chrome checks at 1920×1080 and 1280×800 across English/dark,
English/light, Chinese/dark, and Chinese/light. Coverage includes navigation,
rapid switching, hash recovery, language/theme persistence, fullscreen,
reduced motion, contrast, external requests, browser errors, control overlap,
content clipping, and the low-prominence preference controls in default, hover,
focus, and touch states. The checks include a dedicated typography gate for
every slide in both languages. English/dark and Chinese/light print outputs
were each confirmed as 17 independent 960×540-point pages.

`BUILD_RECEIPT.json` 记录生成产物与浏览器 QA。演示在 1920×1080 和 1280×800
视口下，对英文深色、英文浅色、中文深色、中文浅色四种组合完成 417 项真实 Chrome
检查，覆盖导航、快速切页、hash 恢复、语言与主题持久化、全屏、减少动态效果、对比度、
外部请求、浏览器错误、控件遮挡、内容裁切，以及设置控件在默认、悬停、聚焦和触屏状态
下的低存在感与可操作性，并逐页检查中英文标题平衡与最小正文字号。英文深色与中文浅色
打印稿均验证为 17 个独立的 960×540 点页面。
