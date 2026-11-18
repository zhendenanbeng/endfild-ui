"""Offline checks for a distributable Agent Skill, its assets and native PPT data."""
from pathlib import Path
from decimal import Decimal
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import argparse, importlib.util, io, json, os, posixpath, re, zipfile
import xml.etree.ElementTree as ET
from common import ROOT, IGNORED, config, runtime_files, skill_root

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
    'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
PRIVATE_PATH = re.compile(r'(?i)(?:[a-z]:[\\/]Users[\\/]|/Users/|/home/)[a-z0-9_.-]+')
SECRET = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
TEXT = {'.md', '.py', '.json', '.yaml', '.yml', '.html', '.css', '.js', '.svg'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def public_files(root):
    for directory, folders, names in os.walk(root, followlinks=False):
        folders[:] = [name for name in folders if name not in IGNORED]
        require(all(not (Path(directory) / name).is_symlink() for name in folders), 'Public source directory is a symlink')
        for name in names:
            path = Path(directory) / name
            if path.suffix in TEXT or name in ('LICENSE', '.gitattributes', '.gitignore'):
                require(not path.is_symlink(), 'Public source file is a symlink')
                yield path

def check_public_text(text, name):
    require(not PRIVATE_PATH.search(text), 'Author-machine path in ' + name)
    require(not SECRET.search(text), 'Possible credential in ' + name)

def local_reference(root, owner, target):
    target = target.strip().strip('<>')
    if not target or target.startswith(('#', 'data:', 'mailto:')) or urlsplit(target).scheme:
        return
    path = (owner.parent / unquote(urlsplit(target).path)).resolve()
    require(path.is_relative_to(root.resolve()), 'Relative resource escapes repository: ' + target)
    require(path.is_file(), 'Missing resource from ' + owner.relative_to(root).as_posix() + ': ' + target)

class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ('href', 'src') and value)

def part(owner, target):
    target = unquote(target)
    result = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(posixpath.dirname(owner), target))
    require(not result.startswith('../'), 'OPC relationship escapes package')
    return result

def relationship(package, owner, identifier):
    rel_name = posixpath.join(posixpath.dirname(owner), '_rels', posixpath.basename(owner) + '.rels')
    relations = ET.fromstring(package.read(rel_name))
    reference = next((item for item in relations if item.get('Id') == identifier), None)
    require(reference is not None and reference.get('TargetMode') != 'External', 'Missing internal package relationship')
    return part(owner, reference.get('Target'))

def workbook_values(blob, formula):
    sheet_name, address = formula.rsplit('!', 1)
    sheet_name = sheet_name.strip("'").replace("''", "'")
    match = re.fullmatch(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', address.replace('$', ''))
    require(match is not None and match[1] == match[3], 'Expected one native chart value column')
    with zipfile.ZipFile(io.BytesIO(blob)) as workbook:
        book = ET.fromstring(workbook.read('xl/workbook.xml'))
        sheet = next((s for s in book.findall('x:sheets/x:sheet', NS) if s.get('name') == sheet_name), None)
        require(sheet is not None, 'Chart worksheet missing')
        path = relationship(workbook, 'xl/workbook.xml', sheet.get('{' + NS['r'] + '}id'))
        document = ET.fromstring(workbook.read(path))
        cells = {cell.get('r'): cell.find('x:v', NS) for cell in document.findall('.//x:sheetData/x:row/x:c', NS)}
        values = []
        for row in range(int(match[2]), int(match[4]) + 1):
            value = cells.get(match[1] + str(row))
            require(value is not None and value.text is not None, 'Chart workbook cell missing')
            values.append(Decimal(value.text))
        return values

def check_pptx(path):
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        require(all(not name.startswith('/') and '..' not in name.split('/') for name in names), 'Unsafe presentation package entry')
        slides = [name for name in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)]
        require(len(slides) == 6, 'Expected all six template layouts')
        for name in names:
            if name.endswith(('.xml', '.rels')):
                check_public_text(package.read(name).decode('utf-8'), 'PPTX/' + name)
        require(all(ET.fromstring(package.read(name)).findall('.//a:t', NS) for name in slides), 'A slide lost its native text')
        table = ET.fromstring(package.read('ppt/slides/slide5.xml')).find('.//a:tbl', NS)
        require(table is not None, 'Comparison layout must retain a native table')
        owner = 'ppt/slides/slide4.xml'
        reference = ET.fromstring(package.read(owner)).find('.//c:chart', NS)
        require(reference is not None, 'Data layout must retain a native chart')
        chart_path = relationship(package, owner, reference.get('{' + NS['r'] + '}id'))
        chart = ET.fromstring(package.read(chart_path))
        external = chart.find('.//c:externalData', NS)
        require(external is not None, 'Native chart needs its editable workbook')
        workbook_path = relationship(package, chart_path, external.get('{' + NS['r'] + '}id'))
        require(workbook_path.endswith('.xlsx'), 'Native chart workbook type missing')
        series = chart.findall('.//c:ser', NS)
        require(bool(series), 'Chart data series missing')
        for item in series:
            formula = item.find('c:val/c:numRef/c:f', NS)
            cached = item.findall('c:val/c:numRef/c:numCache/c:pt/c:v', NS)
            require(formula is not None and cached, 'Chart value formula/cache missing')
            actual = workbook_values(package.read(workbook_path), formula.text)
            expected = [Decimal(value.text) for value in cached]
            require(actual == expected and all(value.is_finite() for value in actual), 'Chart cache differs from its editable workbook')

def contrast(a, b):
    def luminance(color):
        channels = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
        channels = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
        return sum(x * y for x, y in zip(channels, (.2126, .7152, .0722)))
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)

def validate(root=ROOT, tag=None):
    root = Path(root).resolve()
    cfg = config(root)
    skill = skill_root(root)
    entries = runtime_files(root)
    front = (skill / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)
    require(len(front) == 3 and not front[0].strip(), 'SKILL.md YAML frontmatter missing')
    name = re.search(r'^name:\s*(.+)$', front[1], re.M)
    description = re.search(r'^description:\s*(.+)$', front[1], re.M)
    require(name is not None and name[1].strip(' \"\'') == cfg['name'], 'Skill metadata/directory name mismatch')
    require(description is not None and 1 <= len(description[1]) <= 1024, 'Skill description missing or too long')
    tokens = json.loads((skill / 'assets/tokens.json').read_text(encoding='utf-8'))
    require(tokens['version'] == cfg['version'] and tokens['name'] == cfg['name'], 'Token metadata/version drift')
    if tag is not None:
        require(tag == 'v' + cfg['version'], 'Git tag does not match project version')
    for mode in ('light', 'dark'):
        color = tokens['color'][mode]
        require(contrast(color['paper'], color['ink']) >= 4.5 and contrast(color['paper'], color['muted']) >= 4.5, 'Insufficient text contrast: ' + mode)
    for tone in ('bright', 'soft'):
        require(contrast(tokens['color']['accent']['on'], tokens['color']['accent'][tone]) >= 4.5, 'Insufficient accent text contrast')
    require((skill / 'assets/web/fonts/saira-ui.woff2').read_bytes().startswith(b'wOF2'), 'Bundled WOFF2 font missing')
    require('SIL OPEN FONT LICENSE' in (skill / 'assets/web/fonts/Saira-OFL.txt').read_text(encoding='utf-8'), 'Font license missing')
    require('NOTICE.md' in entries and 'LICENSE' in entries, 'Runtime notices missing')
    spec = importlib.util.spec_from_file_location('endfield_materializer_check', skill / 'scripts/materialize.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require((skill / 'assets/web/tokens.css').read_text(encoding='utf-8') == module.css_variables(tokens), 'Generated token CSS is stale; run scripts/sync_tokens.py')
    checked = 0
    for path in public_files(root):
        text = path.read_text(encoding='utf-8')
        check_public_text(text, path.relative_to(root).as_posix())
        if path.suffix == '.md':
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
                local_reference(root, path, target)
        elif path.suffix in ('.html', '.svg'):
            links = HTMLLinks()
            links.feed(text)
            for target in links.links:
                local_reference(root, path, target)
        elif path.suffix == '.css':
            for target in re.findall(r'url\(\s*[\"\']?([^\"\')\s]+)', text):
                local_reference(root, path, target)
        checked += 1
    check_pptx(skill / 'assets/slides/yellow-paper-template.pptx')
    return {'ok': True, 'version': cfg['version'], 'runtime_files': len(entries), 'text_files_checked': checked, 'native_slides': 6}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag')
    args = parser.parse_args()
    try:
        result = validate(tag=args.tag)
    except (ValueError, OSError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
