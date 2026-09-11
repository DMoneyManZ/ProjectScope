"""ProjectScope controls and its two owned GNOME custom shortcuts."""
import shlex
from gi.repository import Gio

DEFAULTS = {
    'toggle-key': 'Home', 'previous-key': 'Page_Up', 'next-key': 'Page_Down',
    'random-key': 'Pause', 'save-key': 'Insert', 'color-key': 'End',
    'size-up': '<Shift>Page_Up', 'size-down': '<Shift>Page_Down',
    'thickness-up': '<Control>Page_Up', 'thickness-down': '<Control>Page_Down',
}
TITLES = {
    'toggle-key': 'Show / hide crosshair', 'previous-key': 'Previous preset',
    'next-key': 'Next preset', 'random-key': 'Random crosshair',
    'save-key': 'Save preset', 'color-key': 'Next color',
    'size-up': 'Increase size', 'size-down': 'Decrease size',
    'thickness-up': 'Increase thickness', 'thickness-down': 'Decrease thickness',
}


class ShortcutSettings:
    def __init__(self, cfg, backend=None):
        self.cfg = cfg
        source = Gio.SettingsSchemaSource.get_default()
        self.media = Gio.Settings.new_full(source.lookup(
            'org.gnome.settings-daemon.plugins.media-keys', True), backend, None)
        schema = source.lookup('org.gnome.settings-daemon.plugins.media-keys.custom-keybinding', True)
        self.size = {key: Gio.Settings.new_full(schema, backend,
            f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/projectscope-{key}/')
            for key in ['size-up', 'size-down', 'thickness-up', 'thickness-down']}

    def get(self, key):
        if key in self.size:
            value = self.size[key].get_user_value('binding')
            return value.unpack() if value is not None else DEFAULTS[key]
        values = self.cfg.get_strv(key)
        return values[0] if values else ''

    def set(self, key, binding):
        if key in self.size:
            self.size[key].set_string('binding', binding)
        else:
            self.cfg.set_strv(key, [binding] if binding else [])

    def reset_defaults(self):
        for key, binding in DEFAULTS.items():
            self.set(key, binding)

    def install(self, app, uninstall=False):
        paths = self.media.get_strv('custom-keybindings')
        for key, cfg in self.size.items():
            path = cfg.get_property('path')
            if uninstall:
                paths = [p for p in paths if p != path]
                for field in ['name', 'command', 'binding']:
                    cfg.reset(field)
            else:
                cfg.set_string('name', 'ProjectScope · ' + TITLES[key])
                cfg.set_string('command', shlex.join(['/usr/bin/python3',
                    str(app / 'tools/hotkey_resize.py'), key.removeprefix('size-')]))
                if cfg.get_user_value('binding') is None:
                    cfg.set_string('binding', DEFAULTS[key])
                if path not in paths:
                    paths.append(path)
        self.media.set_strv('custom-keybindings', paths)
