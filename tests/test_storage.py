import tempfile
from pathlib import Path
import unittest
from projectscope.storage import save_named_profile
from test_profiles import example
from projectscope.profiles import load_profile

class Storage(unittest.TestCase):
    def test_distinct_names_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            p=example(); p['name']='Aim A'; a=save_named_profile(p,Path(directory))
            p['name']='Aim-A'; b=save_named_profile(p,Path(directory))
            self.assertNotEqual(a['id'],b['id'])
            self.assertEqual(load_profile(Path(directory)/(a['id']+'.json'))['name'],'Aim A')
            p['style']['scale']=2; again=save_named_profile(p,Path(directory))
            self.assertEqual(again['id'],b['id'])
            self.assertEqual(len(list(Path(directory).glob('*.json'))),2)
    def test_truncated_names_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            p=example(); p['name']='a'*70; a=save_named_profile(p,Path(directory))
            p['name']='a'*69+'b'; b=save_named_profile(p,Path(directory))
            self.assertNotEqual(a['id'],b['id']); self.assertLessEqual(len(b['id']),64)

    def test_catalog_user_precedence_and_invalid_files(self):
        from projectscope.storage import preset_catalog
        from projectscope.profiles import save_profile
        with tempfile.TemporaryDirectory() as directory:
            stock=Path(directory)/'stock'; user=Path(directory)/'user'
            stock.mkdir(); user.mkdir()
            p=example(); save_profile(stock/'a.json',p)
            p['name']='Custom replacement'; save_profile(user/'z.json',p)
            (user/'broken.json').write_text('{')
            result=preset_catalog(stock,user)
            self.assertEqual(len(result),1)
            self.assertEqual(result[0][1]['name'],'Custom replacement')
