"""Exercise the shipped installer without touching the user's desktop."""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Release(unittest.TestCase):
    def test_installer_extracts_complete_public_payload_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'artifacts'
            result = subprocess.run([sys.executable, str(ROOT / 'tools/build_release.py'),
                                     '--output', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            installer = out / 'ProjectScope-1.0.0-linux.run'
            target = Path(tmp) / 'source with spaces'
            result = subprocess.run([sys.executable, str(installer), '--extract', str(target)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / 'tools/install.py').is_file())
            self.assertTrue((target / 'tools/install-dependencies.sh').is_file())
            self.assertTrue((target / 'projectscope/app.py').is_file())
            self.assertEqual(len(list((target / 'presets').glob('*.json'))), 30)
            self.assertFalse((target / 'releases').exists())
            self.assertFalse((target / 'local-model-tasks').exists())
            self.assertFalse((target / 'build').exists())
            marker = target / 'keep.txt'
            marker.write_text('existing data')
            result = subprocess.run([sys.executable, str(installer), '--extract', str(target)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), 'existing data')
            result = subprocess.run([sys.executable, str(installer)], input='',
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('terminal', result.stderr.lower())

    def test_traversal_payload_is_rejected_before_writing(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('installer_main', ROOT / 'tools/installer_main.py')
        self.assertTrue(Path(spec.origin).is_file(), 'installer runtime is missing')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('valid.txt', 'should not be written')
                z.writestr('../escape.txt', 'unsafe')
            target = Path(tmp) / 'target'
            with self.assertRaises(ValueError):
                module.extract_payload(archive.read_bytes(), target)
            self.assertFalse(target.exists())
            self.assertFalse((Path(tmp) / 'escape.txt').exists())

    def test_dependency_installer_rejects_unsupported_shell_before_package_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            import os
            commands = Path(tmp)
            shell = commands / 'gnome-shell'
            shell.write_text('#!/bin/sh\necho "GNOME Shell 49.1"\n')
            shell.chmod(0o755)
            manager = commands / 'apt-get'
            marker = commands / 'package-manager-ran'
            manager.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n')
            manager.chmod(0o755)
            result = subprocess.run(['/bin/bash', str(ROOT / 'tools/install-dependencies.sh')],
                                    env={**os.environ, 'PATH': str(commands) + ':/usr/bin:/bin'},
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('GNOME Shell 50', result.stderr)
            self.assertFalse(marker.exists())
