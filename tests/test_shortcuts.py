import unittest
from pathlib import Path
from gi.repository import Gio
from projectscope.settings import ROOT, SCHEMA
from projectscope.shortcuts import ShortcutSettings, DEFAULTS


class Shortcuts(unittest.TestCase):
    def setUp(self):
        self.backend = Gio.memory_settings_backend_new()
        source = Gio.SettingsSchemaSource.new_from_directory(
            str(ROOT / 'extension/schemas'), Gio.SettingsSchemaSource.get_default(), False)
        self.cfg = Gio.Settings.new_full(source.lookup(SCHEMA, False), self.backend, None)
        self.shortcuts = ShortcutSettings(self.cfg, self.backend)

    def test_register_preserves_existing_shortcuts_and_custom_size_binding(self):
        s = self.shortcuts
        unrelated = '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/other/'
        s.media.set_strv('custom-keybindings', [unrelated])
        s.install(Path('/tmp/test app'))
        s.set('size-up', '<Control>F10')
        s.install(Path('/tmp/test app'))
        self.assertEqual(s.get('size-up'), '<Control>F10')
        self.assertIn(unrelated, s.media.get_strv('custom-keybindings'))
        self.assertEqual(len(s.media.get_strv('custom-keybindings')), 5)
        s.install(Path('/tmp/test app'), uninstall=True)
        self.assertEqual(s.media.get_strv('custom-keybindings'), [unrelated])

    def test_changes_controls_and_restores_defaults_without_changing_design(self):
        s = self.shortcuts
        profile = self.cfg.get_string('profile')
        s.set('toggle-key', 'F8')
        s.set('size-down', '')
        self.assertEqual(self.cfg.get_strv('toggle-key'), ['F8'])
        self.assertEqual(s.get('size-down'), '')
        s.reset_defaults()
        for key, default in DEFAULTS.items():
            self.assertEqual(s.get(key), default)
        self.assertEqual(self.cfg.get_string('profile'), profile)
