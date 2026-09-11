import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from projectscope.profiles import (ProfileError, validate_profile, loads_profile,
                                  dumps_profile, load_profile, save_profile)

ROOT = Path(__file__).resolve().parents[1]

def example():
    return json.loads((ROOT / 'presets/cs2-precision.json').read_text())

class Profiles(unittest.TestCase):
    def test_roundtrip_and_copy(self):
        p=example(); q=validate_profile(p)
        q['style']['lines']['length']=10
        self.assertEqual(p['style']['lines']['length'],6)
        p['name']='Précision 精确'
        self.assertEqual(loads_profile(dumps_profile(p)),p)
        self.assertIn('精确',dumps_profile(p))
        self.assertTrue(dumps_profile(p).endswith('\n'))
    def test_strict_validation(self):
        for path,value in [('schema_version',True),('schema_version',1.0),('id','BAD'),
                           ('name',' padded'),('description','bad\x00text')]:
            p=example(); p[path]=value
            with self.subTest(path=path,value=value), self.assertRaises(ProfileError): validate_profile(p)
        for value in [True,None,'1',float('nan'),float('inf'),10**10000,-1,2]:
            p=example(); p['style']['opacity']=value
            with self.assertRaises(ProfileError): validate_profile(p)
        for location in [(),('style',),('style','lines'),('style','dot'),('style','circle')]:
            p=example(); target=p
            for part in location: target=target[part]
            target['extra']=1
            with self.assertRaises(ProfileError): validate_profile(p)
    def test_numeric_boundaries(self):
        cases=[('opacity',0,1),('outline_width',0,8),('rotation',-180,180),('scale',.25,8),
               ('lines.length',1,100),('lines.thickness',.5,20),('lines.gap',0,100),
               ('dot.radius',.5,20),('circle.radius',1,100),('circle.thickness',.5,20)]
        for path,lo,hi in cases:
            for value in [lo,hi,lo-.1,hi+.1]:
                p=example(); target=p['style']; parts=path.split('.')
                for key in parts[:-1]: target=target[key]
                target[parts[-1]]=value
                if lo<=value<=hi: validate_profile(p)
                else:
                    with self.assertRaises(ProfileError): validate_profile(p)
    def test_parsing(self):
        text=json.dumps(example())
        for bad in ['\ufeff'+text,text.replace('"opacity": 1.0','"opacity": NaN'),
                    text.replace('"opacity": 1.0','"opacity": 1, "opacity": 0'),
                    text+'x','['*2000+'0'+']'*2000]:
            with self.assertRaises(ProfileError): loads_profile(bad)
        exact=text+' '*(65536-len(text.encode()))
        loads_profile(exact)
        with self.assertRaises(ProfileError): loads_profile(exact+' ')
        with self.assertRaises(ProfileError): loads_profile(exact+'é')
    def test_disabled_geometry_and_invisible(self):
        p=example(); p['style']['dot']['radius']=0
        with self.assertRaises(ProfileError): validate_profile(p)
        p=example(); p['style']['opacity']=0; validate_profile(p)
        p['style']['lines']['enabled']=False
        with self.assertRaises(ProfileError): validate_profile(p)
    def test_save_and_failed_replace(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'profile.json'; save_profile(p,example()); before=p.read_bytes()
            self.assertEqual(load_profile(str(p)),example())
            with patch('os.replace',side_effect=OSError('simulated')):
                with self.assertRaises(OSError): save_profile(p,example())
            self.assertEqual(p.read_bytes(),before)
            self.assertEqual(list(Path(d).iterdir()),[p])
            with patch('os.fdopen',side_effect=OSError('simulated')):
                with self.assertRaises(OSError): save_profile(p,example())
            self.assertEqual(list(Path(d).iterdir()),[p])
            with self.assertRaises(ProfileError): save_profile(p,{})
            self.assertEqual(p.read_bytes(),before)
            p.write_bytes(b'\xff')
            with self.assertRaises(ProfileError): load_profile(p)
            with self.assertRaises(FileNotFoundError): load_profile(Path(d)/'absent')
    def test_pack(self):
        for p in (ROOT/'presets').glob('*.json'):
            self.assertEqual(load_profile(p)['id'],p.stem)

if __name__=='__main__': unittest.main()
