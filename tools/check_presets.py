#!/usr/bin/env python3
"""Check every required preset through the shared strict validator."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from projectscope.profiles import load_profile, ProfileError
NAMES=['cs2-precision','dayz-small-dot','bodycam-subtle-dot','fps-balanced','high-contrast','fps-ring']
def main():
    seen=set()
    for name in sorted(set(NAMES)|{p.stem for p in (ROOT/'presets').glob('*.json')}):
        try:
            p=load_profile(ROOT/'presets'/(name+'.json'))
            if p['id']!=name or p['id'] in seen: raise ProfileError('Preset filename/id mismatch or duplicate')
            seen.add(p['id'])
        except (OSError,ProfileError) as exc:
            print(f'{name}: {exc}',file=sys.stderr); return 1
    print(f'All {len(seen)} presets pass the shared validator'); return 0
if __name__=='__main__': sys.exit(main())
