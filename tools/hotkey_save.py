#!/usr/bin/env python3
"""One-shot local save helper. Reads a profile from stdin; never opens a terminal."""
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from projectscope.profiles import loads_profile,dumps_profile,ProfileError,MAX_BYTES
from projectscope.storage import save_named_profile,preset_catalog
ROOT=Path(__file__).resolve().parents[1]
try:
    profile=loads_profile(sys.stdin.buffer.read(MAX_BYTES+1).decode('utf-8'))
    data=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))
    directory=data/'projectscope/presets';directory.mkdir(parents=True,exist_ok=True)
    saved=save_named_profile(profile,directory)
    print(json.dumps({'profile':saved,'library':[dumps_profile(p) for _,p in preset_catalog(ROOT/'presets',directory)]}))
except (OSError,ValueError,ProfileError) as exc:
    print(str(exc),file=sys.stderr);sys.exit(1)
