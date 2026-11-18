"""Regenerate the web variables from the skill's single token file."""
import importlib.util, json
from common import skill_root

def main():
    root = skill_root()
    spec = importlib.util.spec_from_file_location('endfield_materialize', root / 'scripts/materialize.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tokens = json.loads((root / 'assets/tokens.json').read_text(encoding='utf-8'))
    target = root / 'assets/web/tokens.css'
    target.write_text(module.css_variables(tokens), encoding='utf-8', newline='\n')
    print('Updated ' + target.relative_to(root).as_posix())

if __name__ == '__main__':
    main()
