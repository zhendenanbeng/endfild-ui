---
name: endfield-design-kit
description: "Create Arknights: Endfield-inspired web interfaces, dashboards, editable PowerPoint slides, reports and posters. Use when the user requests 明日方舟：终末地风格、Endfield style or its paper/ink/acid-yellow industrial visual language. Includes a responsive web starter and an editable PPTX template. Preserve the user's content, functionality and requested format."
license: MIT; bundled Saira fonts use SIL OFL 1.1
---

# Endfield Design Kit / 终末地风格设计

把内容组织成清楚、克制的工业工作界面。这是一套非官方的《明日方舟：终末地》风格设计技能。默认采用 Yellow Paper 黄黑变体，需要深色时使用配套变量。品牌、业务和数据由用户的任务决定；不使用游戏官方标志、截图、角色或字体素材。

## 先选载体

- **网页、WebUI、应用界面**：读 [references/web.md](references/web.md)，以 [assets/web/index.html](assets/web/index.html) 和配套 CSS 为起点。已有项目沿用原技术栈。
- **PPT、演示文稿**：读 [references/slides.md](references/slides.md)，复用 [assets/slides/yellow-paper-template.pptx](assets/slides/yellow-paper-template.pptx) 的六类版式。交付可编辑 PPTX；不要把网页截图当作整套演示文稿。
- **报告、文档、海报**：读 [references/other-media.md](references/other-media.md)，按阅读距离调整密度，不机械搬入侧栏和按钮。

共用规范在 [references/design-system.md](references/design-system.md)，颜色、字号及尺寸的机器可读源在 [assets/tokens.json](assets/tokens.json)。只加载当前任务相关的分支。这个技能负责视觉系统，内容研究、业务功能和格式导出继续使用当前环境适合的工具。

需要视觉锚点时查看 [网页预览](assets/preview-web.jpg) 或 [PPT 版式一览](assets/preview-slides.webp)，再按自己的内容组织布局。

## 保留这几个识别点

1. 浅纸色承载正文，浅灰面板分区，墨黑承担文字和结构。亮黄只强调当前项、关键动作或少量重点。
2. 中文标题粗而清楚；英文标签短、小、大写并适度展开。`//` 和编号可用，但编号须对应真实章节、记录或图表。
3. 默认直角。可操作块允许小切角；阅读面板、图像和数据表保持完整的矩形边界。
4. 用留白、细线和灰度区分层级。等高线仅是可选的低对比背景；不压到文字、坐标轴或图像证据上。
5. 主动作可用黄底黑字，次动作采用灰底或黑底。黄色上用深色文字，避免浅底黄色小字。
6. 表格、数据图、正文是主角。保留数据本来的色标、误差、单位和语义；品牌黄不替换科学色图或全部状态颜色。

## 执行方式

根据用户内容确定页面或每页幻灯片的主任务，再选对应版式。默认一处主要视觉焦点；需要高密度工作台时才使用主视区与侧边参数区。已有界面的操作、输入和数据协议继续工作，样式改动不扩大功能范围。

模板中的样本文字和数值都是演示内容，制作成品时替换或移除，并按真实材料写结论。不要默认附加火星仪器名称、M 标志、原项目数据或开发者路径。

验证交付物本身：网页实际查看宽屏、窄屏、键盘焦点和深浅色；PPT 渲染每页并核对可编辑对象与文字边界；报告查看分页与打印。没有运行某项检查时，明确实际验证范围。

## 快速起稿

`scripts/materialize.py` 使用 Python 3.9+ 标准库，把模板复制成独立起点，默认拒绝覆盖已有文件。在目标项目目录执行下面的命令，把 `<skill-dir>` 换成本技能的实际目录；输出目录放在技能之外：

```sh
python "<skill-dir>/scripts/materialize.py" --kind web --out ./my-web
python "<skill-dir>/scripts/materialize.py" --kind slides --out ./my-slides
```

网页输出可直接打开 `index.html`；PPT 输出包含可编辑模板。更改 `assets/tokens.json` 后，可用 `--kind tokens` 导出配套 CSS 变量；该操作不自动改写现有 PPT 或项目。

## 安装与调用

分发时保留整个 `endfield-design-kit` 文件夹。仓库的完整安装方法见根目录 README；使用安装包时可放进工具的技能目录，Codex 的通用目录为 `~/.agents/skills/`。调用 `$endfield-design-kit`；若当前会话未刷新技能列表，在新会话中调用。

示例：`使用 $endfield-design-kit 做一个终末地风格的数据管理前端，保留筛选、表格和导出。`

示例：`使用 $endfield-design-kit 把这些材料做成 8 页可编辑的终末地风格 PPT，保留原始数字和引用。`

分发与字体来源见 [LICENSE](LICENSE) 和 [references/provenance.md](references/provenance.md)。
