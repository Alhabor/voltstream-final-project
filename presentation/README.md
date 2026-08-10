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

## Source-file links / 原始文件链接

Every slide has one to three small `Files:` links in its lower-left footer.
Each link opens a formatted, read-only web view of the exact project file that
supports that slide, in a new tab, so the live presentation remains on the
current slide. Markdown is rendered as a readable document; JSON is pretty
printed; JSON Lines can be expanded record by record; CSV becomes a scrollable
table; and source code gains line numbers. Every view still shows the repository
path and SHA-256 checksum and offers the unchanged raw file as a secondary
action. The Chinese review mode displays translated link labels but opens the
same evidence.

每页左下角均提供一至三个低干扰的“原始文件”链接。链接会在新标签页打开支撑该页内容
的格式化只读视图，因此演示页会保留在当前页。Markdown 会渲染成文档，JSON 会美化缩进，
JSON Lines 可逐条展开，CSV 会显示为可横向滚动的表格，代码文件则带行号。证据页面仍显示
仓库路径与 SHA-256 校验值，并将未经改写的原始文件保留为二次入口；中文审阅模式仅翻译
链接名称，打开的证据与英文版一致。

`evidence.json` is the maintained slide-to-file map; `render_evidence.mjs`
contains the type-specific safe renderers. Regeneration validates
every path, requires evidence for all slides, copies only the listed files into
`presentation/evidence/`, and builds a self-contained viewer beside each copy.
Do not edit the generated evidence copies or viewer pages by hand.

`evidence.json` 是可维护的“页面—原始文件”映射，`render_evidence.mjs` 保存按文件类型
区分的安全渲染逻辑。重新生成时会验证所有路径，要求每页都
存在证据，只将清单内文件复制到 `presentation/evidence/`，并为每份副本生成自包含查看页。
请勿手工修改生成的证据副本或查看页。

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

## Presentation motion / 演示动效

All slides share one restrained, one-time entrance rhythm: the major content
blocks fade upward in reading order and then remain still. Tables move as whole
blocks rather than cell by cell. Slides 6 and 8 use a more detailed version of
the same motion language because they teach a sequence. Slide 6 reveals the
current manual path and prototype path for the same incoming file. Slide 8
reveals the installed-versus-active conflict, the safe blank-plus-human-review
answer, and the observed strategy outcomes. Returning to a slide restarts its
sequence. Nothing loops. Reduced-motion mode and printing show every complete
final state immediately.

所有页面现在共享同一套克制的单次进入节奏：主要内容块按照阅读顺序轻微上移淡入，之后
保持静止；表格作为完整内容块出现，不会逐个单元格跳动。第 6 页和第 8 页承担流程教学，
因此使用同一动效语言的详细版本：第 6 页依次展示同一份新文件的人工路线与原型路线；
第 8 页依次展示“已安装数量与当前启用数量”的冲突、安全答案和实测结果。返回某页时会
重新播放；动画不会循环。减少动态效果模式和打印状态会立即显示全部完整内容。

## Print or save as PDF / 打印或另存 PDF

Select the desired language and theme first, then use the browser's Print
command. Only the current language is printed. The stylesheet places each of
the 17 slides on its own 16:9 landscape page. Enable background graphics if the
browser offers that option.

先选择需要的语言和主题，再使用浏览器的“打印”功能；打印稿只包含当前语言。打印
样式会将 17 张幻灯片分别放在独立的 16:9 横向页面上。如浏览器提供选项，请启用
“背景图形”。

## Verification / 验证

`BUILD_RECEIPT.json` records the generated artifact and the current browser QA.
The animated build passed 153 real-Chrome checks at 1920×1080 and 1280×800
across English/dark, English/light, Chinese/dark, and Chinese/light. The 136
full-deck checks verified every slide and found no text outside the 16:9 stage.
Additional checks covered keyboard and button navigation, rapid switching, hash
recovery, fullscreen, pointer and wheel gestures, one-time animation playback,
strict step 3 → step 4 → example ordering, return-to-slide replay, reduced
motion, and printing. Slides 6 and 8 were also
visually inspected in both presentation and review modes. The print output was
confirmed as 17 independent 960×540-point pages.

`BUILD_RECEIPT.json` 记录生成产物与当前浏览器 QA。动画版本在 1920×1080 和
1280×800 视口下，对英文深色、英文浅色、中文深色、中文浅色四种组合完成 153 项真实
Chrome 检查。其中 136 项逐页检查覆盖全部 17 页，没有发现文字超出 16:9 舞台。其余
检查覆盖键盘和按钮导航、快速切页、hash 恢复、全屏、指针与滚轮手势、单次动画播放、
严格的“第 3 步 → 第 4 步 → 底部示例”顺序、返回页面后重播、减少动态效果和打印；
第 6 页与第 8 页还完成了演示模式和审阅模式下的
人工视觉检查。打印稿验证为 17 个独立的 960×540 点页面。
