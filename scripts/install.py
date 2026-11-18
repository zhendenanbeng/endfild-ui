"""Install the self-contained skill. Never replace an existing destination."""
from pathlib import Path
import argparse, json, os, shutil, tempfile
from common import ROOT, config, runtime_files

def install(skills_dir, root=ROOT):
    skills_dir = Path(skills_dir).expanduser().resolve()
    source = root.resolve()
    if skills_dir.is_relative_to(source):
        raise ValueError('Choose a skills directory outside this repository')
    target = skills_dir / config(root)['name']
    if target.exists() or target.is_symlink():
        raise FileExistsError('Skill already exists; nothing was changed: ' + str(target))
    entries = runtime_files(root)
    skills_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.endfield-install-', dir=skills_dir))
    try:
        for relative, source_file in entries.items():
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)
        # Windows rename refuses to replace an existing target. Explicitly check on all platforms.
        if target.exists() or target.is_symlink():
            raise FileExistsError('Destination appeared during installation; nothing replaced')
        os.rename(staging, target)
        return target
    finally:
        if staging.exists():
            # Only our own generated staging directory may be removed.
            if staging.parent != skills_dir or not staging.name.startswith('.endfield-install-'):
                raise ValueError('Unexpected staging directory')
            shutil.rmtree(staging)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.agents/skills')
    args = parser.parse_args()
    try:
        target = install(args.skills_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps({'installed': str(target), 'invoke': '$' + config()['name']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
