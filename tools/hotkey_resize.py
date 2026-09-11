#!/usr/bin/env python3
"""One-shot size shortcut; uses the running overlay's existing settings signal."""
import argparse
import fcntl
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('direction', choices=['up', 'down', 'thickness-up', 'thickness-down'])
    args = parser.parse_args()
    from gi.repository import Gio, GLib
    from projectscope.settings import settings, shell_call
    from projectscope.resize import resize, thicken
    # Serialize rapid key presses before reading settings to avoid lost updates.
    lock_path = Path(GLib.get_user_runtime_dir()) / 'projectscope-resize.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        info = shell_call('GetExtensionInfo')
        if info.get('state') != 1:
            return
        direction = 1 if args.direction.endswith('up') else -1
        if args.direction.startswith('thickness-'):
            thicken(settings(), direction)
        else:
            resize(settings(), direction, maximum=8 if info.get('version', 0) >= 5 else 4)
        Gio.Settings.sync()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ProjectScope resize: {exc}', file=sys.stderr)
        sys.exit(1)
