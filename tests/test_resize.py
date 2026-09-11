import json
import unittest
from gi.repository import Gio
from projectscope.settings import ROOT, SCHEMA
from projectscope.resize import resize, thicken


class Resize(unittest.TestCase):
    def setUp(self):
        source = Gio.SettingsSchemaSource.new_from_directory(
            str(ROOT / 'extension/schemas'), Gio.SettingsSchemaSource.get_default(), False)
        self.cfg = Gio.Settings.new_full(source.lookup(SCHEMA, False),
                                         Gio.memory_settings_backend_new(), None)

    def test_changes_only_scale_and_keeps_hidden_crosshair_hidden(self):
        before = json.loads(self.cfg.get_string('profile'))
        self.cfg.set_boolean('visible', False)
        resize(self.cfg, 1)
        after = json.loads(self.cfg.get_string('profile'))
        self.assertEqual(after['style']['scale'], 1.25)
        after['style']['scale'] = before['style']['scale']
        self.assertEqual(after, before)
        self.assertFalse(self.cfg.get_boolean('visible'))
        resize(self.cfg, -1)
        self.assertEqual(json.loads(self.cfg.get_string('profile')), before)

    def test_clamps_to_supported_limits(self):
        for start, direction, expected in [(7.9, 1, 8), (.3, -1, .25), (8, 1, 8), (.25, -1, .25)]:
            with self.subTest(start=start, direction=direction):
                profile = json.loads(self.cfg.get_string('profile'))
                profile['style']['scale'] = start
                self.cfg.set_string('profile', json.dumps(profile))
                resize(self.cfg, direction)
                self.assertEqual(json.loads(self.cfg.get_string('profile'))['style']['scale'], expected)

    def test_og_mode_does_not_resize(self):
        self.cfg.set_boolean('og-controls', True)
        before = self.cfg.get_string('profile')
        resize(self.cfg, 1)
        self.assertEqual(self.cfg.get_string('profile'), before)

    def test_old_renderer_limit_keeps_crosshair_supported_until_next_login(self):
        profile = json.loads(self.cfg.get_string('profile'))
        profile['style']['scale'] = 4
        self.cfg.set_string('profile', json.dumps(profile))
        resize(self.cfg, 1, maximum=4)
        self.assertEqual(json.loads(self.cfg.get_string('profile'))['style']['scale'], 4)

    def test_invalid_profile_is_not_overwritten(self):
        self.cfg.set_string('profile', '{}')
        with self.assertRaises(ValueError):
            resize(self.cfg, 1)
        self.assertEqual(self.cfg.get_string('profile'), '{}')

    def test_thickness_changes_strokes_without_resizing_shape(self):
        before = json.loads(self.cfg.get_string('profile'))
        thicken(self.cfg, 1)
        after = json.loads(self.cfg.get_string('profile'))
        self.assertEqual(after['style']['lines']['thickness'], 2.25)
        after['style']['lines']['thickness'] = before['style']['lines']['thickness']
        self.assertEqual(after, before)
        thicken(self.cfg, -1)
        self.assertEqual(json.loads(self.cfg.get_string('profile')), before)

    def test_thickness_clamps_and_supports_dot_only(self):
        profile = json.loads(self.cfg.get_string('profile'))
        profile['style']['lines']['enabled'] = False
        profile['style']['dot'].update(enabled=True, radius=.5)
        self.cfg.set_string('profile', json.dumps(profile))
        thicken(self.cfg, -1)
        self.assertEqual(json.loads(self.cfg.get_string('profile'))['style']['dot']['radius'], .5)
        thicken(self.cfg, 1)
        self.assertEqual(json.loads(self.cfg.get_string('profile'))['style']['dot']['radius'], .75)
