# 贡献指南

改动应支持终末地风格的网页、可编辑演示或阅读报告。业务算法、私人数据集和游戏官方素材不属于本项目。

## 修改位置

- 配色和尺寸：`skills/endfield-design-kit/assets/tokens.json`。
- 网页组件：同目录下的 `web/theme.css`；示例交互在 `web/demo.js`。
- 技能规则：`SKILL.md` 和对应 `references/`。通用规则只维护一处，避免每种载体复制整套说明。
- PPT：保持原生可编辑的文字、表格和图表；示例数值必须明确标为演示。
- 安装和发布：仓库根目录 `scripts/`，安装包只使用 `project.json` 声明的运行文件。

修改 tokens 后运行：

```sh
python scripts/sync_tokens.py
```

## 提交前

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/build_release.py
```

网页改动实际查看宽屏、窄屏、深浅色、键盘焦点和空状态。PPT 改动逐页渲染，确认数据与文字完整，保留可编辑对象。说明自己实际做过哪些验证。

提交说明应写清具体改动与验证。字体、图像或第三方代码需要保留可分发的许可和来源；已有许可不能被新的顶层许可替代。
