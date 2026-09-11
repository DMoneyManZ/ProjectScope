"""GNOME settings bridge. Only the editor imports PyGObject."""
from pathlib import Path
import gi
from gi.repository import Gio, GLib
from .profiles import dumps_profile, loads_profile

ROOT=Path(__file__).resolve().parents[1]
UUID='projectscope@local'
SCHEMA='org.gnome.shell.extensions.projectscope'

def settings():
    source=Gio.SettingsSchemaSource.new_from_directory(str(ROOT/'extension/schemas'),
        Gio.SettingsSchemaSource.get_default(),False)
    schema=source.lookup(SCHEMA,False)
    if schema is None: raise RuntimeError('Run python3 tools/install.py to compile settings.')
    return Gio.Settings.new_full(schema,None,None)

def shell_call(method):
    connection=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    result=connection.call_sync('org.gnome.Shell.Extensions','/org/gnome/Shell/Extensions',
        'org.gnome.Shell.Extensions',method,GLib.Variant('(s)',(UUID,)),None,
        Gio.DBusCallFlags.NONE,2000,None)
    return result.unpack()[0] if result.n_children() else None

def status():
    try:
        info=shell_call('GetExtensionInfo')
        state=info.get('state',99)
        if hasattr(state,'unpack'): state=state.unpack()
        if state==1: return 'Overlay ready · Home toggles visibility'
        if state==3: return 'Extension error — see the tutorial troubleshooting section'
        if state==4: return 'This GNOME version is not supported by the installed extension'
        if state in (2,6): return 'Extension is off · select Enable extension'
        if state in (7,8): return 'Extension is changing state · refresh shortly'
        return 'First install: log out and back in, then open ProjectScope'
    except GLib.Error:
        return 'GNOME session unavailable · run from your Ubuntu desktop'
