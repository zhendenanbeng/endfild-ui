# 发布

仓库：https://github.com/zhendenanbeng/endfild-ui

## 准备版本

同步修改 `project.json` 和技能内 `assets/tokens.json` 的版本号，更新 CHANGELOG。技能文件夹名、`SKILL.md` 名称与发布包根目录保持 `endfield-design-kit`。

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/build_release.py
python scripts/build_site.py
```

`dist/endfield-design-kit-版本号.zip` 是可安装的技能包，`dist/endfield-design-kit-site-版本号.zip` 是可放到静态托管的展示站。`dist/SHA256SUMS.txt` 列出这两个 ZIP 的摘要。构建不会联网，也不需要用户账号。

打包清单在 `project.json`。构建前会检查入口、相对资源、字体许可、演示图表数据、绝对路径和常见凭据模式，禁止把 Git 历史、缓存或构建目录带入运行包。

## 上传与 Release

确认版本后提交并推送到主分支，再创建同名版本标签。例如 1.0.0：

```sh
git push origin HEAD:main
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions 会先检查并重建文件，再创建 Release 和上传 ZIP/校验文件。只有标签任务拥有发布所需的仓库写入权限；普通检查使用只读权限。不要强制替换已发布标签或覆盖旧的发行包。

首次发布仍须检查 Actions 的实际结果。工作流文件存在不代表任务已经运行成功。

## 展示站

打开仓库根目录 `index.html` 可本地浏览。`python scripts/build_site.py` 生成的站点可放在任意静态托管路径；页面中的 GitHub、安装和 Release 地址都指向本仓库。

如使用 GitHub Pages，可将站点产物部署到 Pages，并在仓库设置中选择对应发布方式。本项目不要求开通额外托管，也不在本地构建时修改仓库设置。
