import unittest
import cairo
from projectscope.render import draw, extent
from test_profiles import example

class Render(unittest.TestCase):
    def test_dot_opacity_and_center(self):
        p=example(); s=p['style']; s['lines']['enabled']=False
        s['dot']={'enabled':True,'radius':3}; s['outline_width']=1; s['opacity']=.5
        surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,40,40)
        draw(cairo.Context(surface),s,20,20)
        surface.flush(); data=surface.get_data(); stride=surface.get_stride()
        self.assertIn(data[20*stride+20*4+3],range(126,130))
        self.assertEqual(data[0+3],0)
    def test_extent_accounts_for_scaling(self):
        p=example(); s=p['style']; s['scale']=2
        self.assertGreaterEqual(extent(s),23)
        self.assertLess(extent(s),40)

if __name__=='__main__': unittest.main()

class OutlineBounds(unittest.TestCase):
    def test_thick_rotated_short_arms_fit(self):
        s=example()['style']; s['lines'].update(length=1,gap=0,thickness=20)
        s.update(outline_width=8,scale=4,rotation=45)
        self.assertGreaterEqual(extent(s),82)
