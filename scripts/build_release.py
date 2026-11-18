"""Build the installable skill ZIP without repository history or private state."""
from pathlib import Path
import argparse, json
from common import ROOT, archive, checksums, config, runtime_files, sha256
from validate import validate

def build(out_dir, root=ROOT):
    validate(root)
    cfg = config(root)
    out_dir = Path(out_dir).resolve()
    if out_dir.is_relative_to((root / cfg['skill']).resolve()):
        raise ValueError('Release output must be outside the skill')
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = runtime_files(root)
    manifest = {'name': cfg['name'], 'version': cfg['version'], 'files': {name: sha256(path) for name, path in entries.items()}}
    payload = dict(entries)
    payload['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    target = out_dir / (cfg['name'] + '-' + cfg['version'] + '.zip')
    archive(target, payload, cfg['name'], cfg['releaseDate'])
    (out_dir / 'RELEASE_NOTES.md').write_text(
        '# Endfield Design Kit ' + cfg['version'] + '\n\n'
        '非官方《明日方舟：终末地》风格设计技能，用于网页、可编辑 PPT 和报告。\n\n'
        '- Skill ZIP：解压后安装完整的 endfield-design-kit 文件夹。\n'
        '- Site ZIP：可离线浏览或放到静态托管的产品展示站。\n'
        '- SHA256SUMS.txt：发行文件摘要。\n\n'
        '代码和说明为 MIT；随包 Saira 字体按 SIL OFL 1.1 单独许可。无游戏官方素材。\n', encoding='utf-8')
    checksums(out_dir)
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    target = build(args.out)
    print(json.dumps({'archive': str(target), 'bytes': target.stat().st_size, 'sha256': sha256(target)}, ensure_ascii=True))

if __name__ == '__main__':
    main()
