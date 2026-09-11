#!/usr/bin/env python3
"""Read-only checks for the GNOME 50 desktop installer."""
import importlib
import shutil
import subprocess
import sys


def main():
    checks = [('Python 3.10+', sys.version_info >= (3, 10))]
    for command in ('gnome-shell', 'gnome-extensions', 'glib-compile-schemas'):
        checks.append((command, bool(shutil.which(command))))
    version = ''
    if shutil.which('gnome-shell'):
        result = subprocess.run(['gnome-shell', '--version'], capture_output=True, text=True, timeout=10)
        version = result.stdout.strip()
    checks.append(('GNOME Shell 50 (' + (version or 'not found') + ')',
                   version == 'GNOME Shell 50' or version.startswith('GNOME Shell 50.')))
    for label, module in [('PyGObject', 'gi'), ('Pycairo', 'cairo')]:
        try:
            importlib.import_module(module)
            passed = True
        except ImportError:
            passed = False
        checks.append((label, passed))
    try:
        import gi
        gi.require_version('Gtk', '4.0')
        from gi.repository import Gtk  # noqa: F401
        gtk = True
    except (ImportError, ValueError):
        gtk = False
    checks.append(('GTK 4', gtk))
    for label, passed in checks:
        print(('OK      ' if passed else 'MISSING ') + label)
    print('\nRun installation from your GNOME desktop terminal. This check changes no settings.')
    if not all(passed for _, passed in checks):
        print('Ubuntu packages: python3 python3-gi python3-cairo '
              'gir1.2-gtk-4.0 libglib2.0-bin')
        print('The desktop must already run GNOME Shell 50; other Shell versions are unsupported.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
