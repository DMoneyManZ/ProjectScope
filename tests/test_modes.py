import unittest
from gi.repository import Gio
from projectscope.settings import ROOT, SCHEMA
from projectscope.modes import set_og, CONTROL_KEYS

class Modes(unittest.TestCase):
    def setUp(self):
        source=Gio.SettingsSchemaSource.new_from_directory(str(ROOT/'extension/schemas'),Gio.SettingsSchemaSource.get_default(),False)
        self.cfg=Gio.Settings.new_full(source.lookup(SCHEMA,False),Gio.memory_settings_backend_new(),None)

    def test_og_roundtrip_preserves_custom_controls_and_design(self):
        cfg=self.cfg
        cfg.set_strv('toggle-key',['F8']);cfg.set_strv('random-key',['F9'])
        cfg.set_boolean('invert-crosshair',True)
        before={key:cfg.get_value(key).unpack() for key in CONTROL_KEYS}
        profile=cfg.get_string('profile')
        set_og(cfg,True)
        self.assertTrue(cfg.get_boolean('og-controls'))
        self.assertEqual(cfg.get_strv('toggle-key'),['Home'])
        for key in ['previous-key','next-key','random-key','save-key','color-key']:
            self.assertEqual(cfg.get_strv(key),[])
        self.assertFalse(cfg.get_boolean('show-label'))
        self.assertFalse(cfg.get_boolean('invert-crosshair'))
        set_og(cfg,True)  # Repeated activation must not overwrite saved modern controls.
        set_og(cfg,False)
        self.assertEqual({key:cfg.get_value(key).unpack() for key in CONTROL_KEYS},before)
        self.assertEqual(cfg.get_string('profile'),profile)

    def test_invalid_backup_restores_defaults(self):
        self.cfg.set_boolean('og-controls',True)
        self.cfg.set_string('updated-controls','{"random-key": 5}')
        set_og(self.cfg,False)
        self.assertEqual(self.cfg.get_strv('random-key'),['Pause'])
        self.assertFalse(self.cfg.get_boolean('og-controls'))
