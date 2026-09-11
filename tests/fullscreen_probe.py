"""Fullscreen input target for isolated compositor testing; not shipped in app."""
import sys
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GLib
folder=Path(sys.argv[1])
app=Gtk.Application(application_id='io.projectscope.TestProbe')
def activate(app):
    win=Gtk.ApplicationWindow(application=app,title='ProjectScope fullscreen input test')
    button=Gtk.Button(label='Fullscreen click-through test')
    button.connect('clicked',lambda *_:(folder/'clicked').write_text('yes'))
    win.set_child(button); win.fullscreen(); win.present()
    def ready():
        (folder/'probe-ready').write_text('yes'); return False
    GLib.timeout_add(700,ready)
    GLib.timeout_add(40000,lambda:app.quit())
app.connect('activate',activate); app.run([])
