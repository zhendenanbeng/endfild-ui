"""Meaningful product contracts: portable assets, user-file preservation and releases."""
from pathlib import Path
from unittest import TestCase
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import common
import install
import validate
import build_release
import build_site

class ProductTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='endfield-product-')
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def materialize(self, kind, destination, root=None):
        source = (root or common.skill_root()) / 'scripts/materialize.py'
        return subprocess.run([sys.executable, str(source), '--kind', kind, '--out', str(destination)], capture_output=True, text=True, encoding='utf-8')

    def test_whole_product_validates_offline(self):
        result = validate.validate()
        self.assertTrue(result['ok'])
        self.assertEqual(result['native_slides'], 6)

    def test_release_tag_must_match_actual_version(self):
        with self.assertRaisesRegex(ValueError, 'Git tag'):
            validate.validate(tag='v999.0.0')

    def test_install_is_standalone(self):
        target = install.install(self.base / 'skills')
        self.assertEqual(target.name, 'endfield-design-kit')
        result = self.materialize('web', self.base / '独立网页 with spaces', target)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('index.html', 'theme.css', 'tokens.css', 'demo.js', 'fonts/saira-ui.woff2', 'fonts/Saira-OFL.txt'):
            self.assertTrue((self.base / '独立网页 with spaces' / name).is_file(), name)

    def test_existing_install_and_other_skills_are_untouched(self):
        parent = self.base / 'skills'
        other = parent / 'other-skill/keep.txt'
        other.parent.mkdir(parents=True)
        other.write_text('keep', encoding='utf-8')
        target = install.install(parent)
        user_file = target / 'my-notes.txt'
        user_file.write_text('my edits', encoding='utf-8')
        before = {str(p.relative_to(parent)): p.read_bytes() for p in parent.rglob('*') if p.is_file()}
        with self.assertRaises(FileExistsError):
            install.install(parent)
        after = {str(p.relative_to(parent)): p.read_bytes() for p in parent.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_install_cannot_write_inside_its_source(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            install.install(ROOT / 'skills')

    def test_materialize_preserves_all_existing_files(self):
        dest = self.base / 'web'
        self.assertEqual(self.materialize('web', dest).returncode, 0)
        (dest / 'customer.txt').write_text('preserve', encoding='utf-8')
        before = {p.name: p.read_bytes() for p in dest.rglob('*') if p.is_file()}
        self.assertNotEqual(self.materialize('web', dest).returncode, 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in dest.rglob('*') if p.is_file()})

    def test_materializer_supports_unicode_paths_on_ascii_console(self):
        dest = self.base / '中文路径'
        env = dict(os.environ, PYTHONIOENCODING='ascii', PYTHONUTF8='0')
        result = subprocess.run([sys.executable, str(common.skill_root() / 'scripts/materialize.py'), '--kind', 'web', '--out', str(dest)], env=env, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout.decode('ascii'))['output'], str(dest))
        self.assertTrue((dest / 'index.html').is_file())

    def test_slide_materialization_is_the_native_template(self):
        dest = self.base / 'slides'
        result = self.materialize('slides', dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        ppt = dest / 'yellow-paper-template.pptx'
        self.assertEqual(ppt.read_bytes(), (common.skill_root() / 'assets/slides/yellow-paper-template.pptx').read_bytes())
        validate.check_pptx(ppt)

    def test_output_cannot_escape_via_existing_symlink(self):
        dest = self.base / 'web'
        dest.mkdir()
        external = self.base / 'outside'
        external.mkdir()
        try:
            (dest / 'fonts').symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('This account cannot create symlinks')
        result = self.materialize('web', dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((dest / 'index.html').exists())

    def test_private_paths_and_tokens_are_rejected(self):
        for text in ('C:' + '/Users/' + 'private-user/project', 'ghp_' + 'a' * 36):
            with self.assertRaises(ValueError):
                validate.check_public_text(text, 'test')

    def test_workflow_token_reference_is_allowed(self):
        validate.check_public_text('GH_TOKEN: ${{ github.token }}', 'workflow')

    def test_release_is_reproducible_and_manifest_verifies_every_byte(self):
        first = build_release.build(self.base / 'first')
        second = build_release.build(self.base / 'second')
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as package:
            prefix = 'endfield-design-kit/'
            manifest = json.loads(package.read(prefix + 'manifest.json'))
            self.assertEqual(set(package.namelist()), {prefix + p for p in manifest['files']} | {prefix + 'manifest.json'})
            for name, expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256(package.read(prefix + name)).hexdigest(), expected)
            self.assertTrue(all(not any(token in name for token in ('.git/', 'tests/', '__pycache__', 'node_modules')) for name in package.namelist()))

    def test_untracked_environment_and_bytecode_are_not_released(self):
        mirror = self.base / 'source'
        shutil.copytree(ROOT, mirror, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
        assets = common.skill_root(mirror) / 'assets'
        (assets / '.env').write_text('EXAMPLE=' + 'private-test-value', encoding='utf-8')
        (assets / 'local.pyc').write_bytes(b'not distributable')
        archive = build_release.build(self.base / 'release', mirror)
        with zipfile.ZipFile(archive) as package:
            self.assertFalse(any(name.endswith(('.env', '.pyc')) for name in package.namelist()))

    def test_archive_paths_cannot_traverse(self):
        for name in ('../escape.txt', '..\\escape.txt', '/escape.txt', 'C:/escape.txt'):
            with self.assertRaises(ValueError):
                common.archive(self.base / 'invalid.zip', {name: b'x'})

    def test_static_site_is_portable_and_excludes_developer_files(self):
        archive = build_site.build(self.base / 'public')
        with zipfile.ZipFile(archive) as package:
            self.assertIn('index.html', package.namelist())
            self.assertIn('docs/site.js', package.namelist())
            self.assertIn('skills/endfield-design-kit/assets/web/fonts/saira-ui.woff2', package.namelist())
            self.assertFalse(any(name.startswith(('.git/', 'scripts/', 'tests/')) for name in package.namelist()))

    def test_installed_tokens_can_be_exported(self):
        target = install.install(self.base / 'skills')
        destination = self.base / 'tokens'
        result = self.materialize('tokens', destination, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('#FFFA00', (destination / 'tokens.css').read_text(encoding='utf-8'))

    def test_installed_materializer_does_not_need_product_scripts(self):
        target = install.install(self.base / 'skills')
        self.assertEqual([p.name for p in (target / 'scripts').iterdir()], ['materialize.py'])
        result = self.materialize('slides', self.base / 'standalone-slides', target)
        self.assertEqual(result.returncode, 0, result.stderr)
