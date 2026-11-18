"""Shared offline product metadata, bounded runtime files and reproducible archives."""
from pathlib import Path, PurePosixPath
import hashlib, json, re, stat, zipfile

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.build', 'dist', 'node_modules', '__pycache__', '.venv'}

def config(root=ROOT):
    value = json.loads((root / 'project.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value['name']) or len(value['name']) > 64:
        raise ValueError('Invalid skill name')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-z0-9][a-z0-9.-]*)?', value['version']):
        raise ValueError('Invalid release version')
    if value['skill'] != 'skills/' + value['name']:
        raise ValueError('Skill directory must match the declared name')
    return value

def skill_root(root=ROOT):
    path = (root / config(root)['skill']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Skill directory escapes repository')
    return path

def runtime_files(root=ROOT):
    skill = skill_root(root)
    result = {}
    for relative in config(root)['runtimeFiles']:
        item = skill / relative
        if item.is_symlink() or not item.resolve().is_relative_to(skill):
            raise ValueError('Runtime source escapes skill: ' + relative)
        if not item.exists():
            raise ValueError('Missing runtime source: ' + relative)
        candidates = item.rglob('*') if item.is_dir() else [item]
        for path in candidates:
            if path.is_symlink():
                raise ValueError('Runtime symlinks are not distributed: ' + str(path))
            if any(part in IGNORED for part in path.relative_to(skill).parts) or path.suffix in ('.pyc', '.pyo'):
                continue
            if path.is_file():
                if not path.resolve().is_relative_to(skill):
                    raise ValueError('Runtime source escapes skill')
                result[path.relative_to(skill).as_posix()] = path
    return dict(sorted(result.items()))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def archive(path, files, root_prefix='', date='2026-11-18'):
    """Write sorted regular files with a fixed timestamp; reject ZIP traversal."""
    year, month, day = map(int, date.split('-'))
    # Stored entries avoid zlib-version differences across supported runners.
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_STORED) as output:
        for relative, value in sorted(files.items()):
            name = PurePosixPath(root_prefix) / relative if root_prefix else PurePosixPath(relative)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError('Unsafe ZIP entry: ' + str(name))
            info = zipfile.ZipInfo(name.as_posix(), (year, month, day, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            data = value.read_bytes() if isinstance(value, Path) else value
            output.writestr(info, data)

def checksums(directory):
    files = sorted(directory.glob('*.zip'))
    (directory / 'SHA256SUMS.txt').write_text(''.join(sha256(path) + '  ' + path.name + '\n' for path in files), encoding='utf-8')
