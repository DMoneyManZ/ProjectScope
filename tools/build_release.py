#!/usr/bin/env python3
"""Build public-only source and runnable installer artifacts using the standard library."""
import argparse
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import zipapp
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'


def public_files():
    # Explicit publication boundary: never include backups, personal presets or local task logs.
    directories = ('projectscope', 'extension', 'presets', 'assets', 'tools', 'tests', 'docs/images')
    for folder in directories:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlink is not allowed in a release: ' + str(path.relative_to(ROOT)))
            if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.pyc', '.compiled'):
                yield path
    names = ('README.md', 'LICENSE', 'CONTRIBUTING.md', 'VALIDATION.md',
             'docs/INSTALL.md', 'docs/USER-GUIDE.md', 'docs/DEVELOPMENT.md',
             'docs/RELEASE-VALIDATION.md', 'support/PRESET-GUIDE.md',
             'support/example-profile.json', 'support/preset-gallery.png')
    for name in names:
        path = ROOT / name
        if path.is_symlink():
            raise ValueError('Symlink is not allowed in a release: ' + name)
        if path.is_file():
            yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    files = list(public_files())
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
    name = 'ProjectScope-' + VERSION
    source = args.output / (name + '-source.tar.gz')
    with tarfile.open(source, 'w:gz') as archive:
        for path in files:
            info = archive.gettarinfo(str(path), name + '/' + path.relative_to(ROOT).as_posix())
            info.uid = info.gid = 0; info.uname = info.gname = ''
            with path.open('rb') as handle:
                archive.addfile(info, handle)
    installer = args.output / (name + '-linux.run')
    with tempfile.TemporaryDirectory(prefix='projectscope-bundle-') as tmp:
        staging = Path(tmp)
        (staging / '__main__.py').write_bytes((ROOT / 'tools/installer_main.py').read_bytes())
        (staging / 'payload.zip').write_bytes(payload.getvalue())
        zipapp.create_archive(staging, installer, interpreter='/usr/bin/env python3', compressed=True)
    installer.chmod(0o755)
    (args.output / 'SHA256SUMS').write_text(''.join(
        hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
        for path in (source, installer)))
    print(f'Built {len(files)} public files into {args.output}')


if __name__ == '__main__':
    main()
