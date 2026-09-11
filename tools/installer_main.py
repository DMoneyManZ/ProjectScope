"""Entry point embedded in the runnable release; no third-party dependencies."""
import argparse
import io
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile


def extract_payload(payload, target):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        members = archive.infolist()
        for member in members:
            path = PurePosixPath(member.filename)
            mode = member.external_attr >> 16
            if (path.is_absolute() or '..' in path.parts or '\\' in member.filename
                    or not path.parts or stat.S_ISLNK(mode)):
                raise ValueError('Unsafe archive member')
        target.mkdir(parents=True, exist_ok=False)
        for member in members:
            destination = target.joinpath(*PurePosixPath(member.filename).parts)
            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(member))
                destination.chmod(0o755 if member.external_attr >> 16 & 0o111 else 0o644)


def main():
    parser = argparse.ArgumentParser(description='ProjectScope 1.0.0 — GNOME 50 per-user installer')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='check system dependencies; change no settings')
    group.add_argument('--extract', metavar='DIRECTORY', help='extract source to a NEW directory; do not install')
    group.add_argument('--install-dependencies', action='store_true',
                       help='install Ubuntu system dependencies using apt and sudo; requires network')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10 or newer is required')
    if not args.check and not args.extract and not args.install_dependencies:
        if os.geteuid() == 0:
            parser.error('Do not install the application as root; use your regular desktop account')
        if not sys.stdin.isatty():
            parser.error('Run from a GNOME desktop terminal for interactive installation, or use --extract DIRECTORY')
        print('ProjectScope installs its editor and GNOME extension for your user account.\n'
              'It creates application/Desktop launchers and enables crosshair shortcuts.\n'
              'Updates replace application files; personal presets and settings are retained.\n'
              'Do not run this installer with sudo. Log out/in after installation or updates.')
        if input('Install ProjectScope? [y/N] ').strip().lower() not in ('y', 'yes'):
            print('Installation cancelled.'); return 0
    with zipfile.ZipFile(Path(sys.argv[0]).resolve()) as bundle:
        payload = bundle.read('payload.zip')
    if args.extract:
        destination = Path(args.extract).expanduser().absolute()
        extract_payload(payload, destination)
        print('Source extracted to ' + str(destination)); return 0
    with tempfile.TemporaryDirectory(prefix='projectscope-install-') as tmp:
        root = Path(tmp) / 'source'
        extract_payload(payload, root)
        if args.install_dependencies:
            result = subprocess.run(['bash', str(root / 'tools/install-dependencies.sh')])
            if result.returncode:
                return result.returncode
        result = subprocess.run([sys.executable, str(root / 'tools/check_dependencies.py')])
        if args.check or args.install_dependencies or result.returncode:
            return result.returncode
        return subprocess.run([sys.executable, str(root / 'tools/install.py')], cwd=root).returncode


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile, KeyError) as exc:
        print('Installer failed: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
