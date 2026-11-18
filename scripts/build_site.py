"""Package the static showcase and its local assets. No hosting is configured."""
from pathlib import Path
import argparse, json, shutil
from common import ROOT, archive, checksums, config, runtime_files, sha256
from validate import validate

def build(out_dir, root=ROOT):
    validate(root)
    cfg = config(root)
    out_dir = Path(out_dir).resolve()
    if out_dir.is_relative_to((root / cfg['skill']).resolve()):
        raise ValueError('Site output must be outside the skill')
    out_dir.mkdir(parents=True, exist_ok=True)
    # Explicit public files; never copy the repository directory wholesale.
    files = {name: root / name for name in ('index.html', 'docs/site.css', 'docs/site.js', 'LICENSE', 'NOTICE.md')}
    for name, path in runtime_files(root).items():
        if name.startswith('assets/'):
            files[cfg['skill'] + '/' + name] = path
    site = out_dir / 'site'
    site.mkdir(exist_ok=True)
    for name, source in files.items():
        target = site / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    target = out_dir / (cfg['name'] + '-site-' + cfg['version'] + '.zip')
    archive(target, files, date=cfg['releaseDate'])
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
