#!/usr/bin/env python3
"""Register only ProjectScope's two owned GNOME keyboard shortcuts."""
import argparse
from pathlib import Path
import sys
from gi.repository import Gio
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from projectscope.shortcuts import ShortcutSettings


def configure(app, uninstall=False):
    ShortcutSettings(None).install(app, uninstall)
    Gio.Settings.sync()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    configure(Path(__file__).resolve().parents[1], args.uninstall)
