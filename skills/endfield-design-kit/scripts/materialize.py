"""Copy standalone visual starters; Python standard library only, no network calls."""
from pathlib import Path
import argparse,json,re,shutil

ROOT=Path(__file__).resolve().parents[1]

def css_variables(tokens):
    def declarations(values):
        return ';'.join('--yp-'+re.sub(r'([A-Z])',lambda m:'-'+m[1].lower(),key)+':'+str(value) for key,value in values.items())+';'
    light=declarations(tokens['color']['light']);dark=declarations(tokens['color']['dark'])
    web=tokens['web'];accent=tokens['color']['accent']
    common={'accent':accent['bright'],'onAccent':accent['on'],'font':tokens['font']['web'],'rail':str(web['rail'])+'px','railMobile':str(web['railMobile'])+'px','aside':str(web['aside'])+'px','cut':str(web['cut'])+'px','motion':str(web['motionMs'])+'ms','ease':web['ease']}
    return '\n'.join([
        '/* Generated from assets/tokens.json by scripts/materialize.py. */',
        ':root{'+declarations(common)+light+'}',
        'html[data-theme="light"]{'+light+'}',
        'html[data-theme="dark"]{'+dark+'}',
        '@media(prefers-color-scheme:dark){html[data-theme="system"]{'+dark+'color-scheme:dark}}',
        'html[data-tone="soft"]{--yp-accent:'+accent['soft']+';--yp-accent-soft:'+accent['softSurfaceLight']+'}',
        'html[data-tone="soft"][data-theme="dark"]{--yp-accent-soft:'+accent['softSurfaceDark']+'}',
        '@media(prefers-color-scheme:dark){html[data-tone="soft"][data-theme="system"]{--yp-accent-soft:'+accent['softSurfaceDark']+'}}',''])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',required=True,choices=('web','slides','tokens'))
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();destination=args.out.expanduser().resolve()
    if destination.is_relative_to(ROOT):parser.error('Choose an output directory outside this skill.')
    tokens=json.loads((ROOT/'assets/tokens.json').read_text(encoding='utf-8'))
    files={}
    if args.kind in ('web','slides'):
        source=ROOT/'assets'/args.kind
        if not source.is_dir():parser.error('Template assets are missing: '+str(source))
        files={path.relative_to(source):path for path in source.rglob('*') if path.is_file()}
    files[Path('tokens.json')]=ROOT/'assets/tokens.json'
    files[Path('LICENSE')]=ROOT/'LICENSE'
    if (ROOT/'NOTICE.md').is_file():files[Path('NOTICE.md')]=ROOT/'NOTICE.md'
    if args.kind in ('web','tokens'):files[Path('tokens.css')]=css_variables(tokens).encode('utf-8')
    for relative in files:
        target=(destination/relative).resolve()
        if not target.is_relative_to(destination):parser.error('Output path escapes the destination: '+str(relative))
        if target.exists():parser.error('Refusing to overwrite existing output: '+str(target))
    for relative,source in files.items():
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if isinstance(source,bytes):target.write_bytes(source)
        else:shutil.copy2(source,target)
    print(json.dumps({'kind':args.kind,'output':str(destination),'files':len(files)},ensure_ascii=True))

if __name__=='__main__':main()
