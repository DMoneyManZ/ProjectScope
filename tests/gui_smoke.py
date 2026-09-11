"""Exercise real GTK controls in an isolated session/settings backend."""
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gi
gi.require_version('Gtk','4.0'); gi.require_version('Gsk','4.0')
from gi.repository import Gtk, GLib, Gdk
from projectscope.app import App, Editor
from projectscope.profiles import loads_profile
app=App(); app.register(None); win=Editor(app); win.present()
loop=GLib.MainLoop(); failures=[]
sys.excepthook=lambda typ,value,tb:failures.append(value)
def check():
    try:
        assert win.profile['id']=='cs2-precision', 'Initial focus replaced the saved preset'
        win.controls['lines.gap'].set_value(7)
        assert loads_profile(win.cfg.get_string('profile'))['style']['lines']['gap']==7
        win.controls['dot.enabled'].set_active(True)
        assert loads_profile(win.cfg.get_string('profile'))['style']['dot']['enabled']
        win.cfg.set_boolean('visible',False)
        assert not win.visible.get_active()
        win.visible.set_active(True)
        assert win.cfg.get_boolean('visible')
        win.entry.set_text('Smoke preset'); win.save_named()
        assert (win.user_dir/'smoke-preset.json').exists()
        win.profile['style']['dot']['enabled']=False
        win.profile['style']['lines']['enabled']=False
        before=win.cfg.get_string('profile'); win.apply()
        assert win.cfg.get_string('profile')==before
        win.reset()
        library=win.cfg.get_strv('preset-library')
        assert any(loads_profile(p)['id']=='smoke-preset' for p in library)
        target=library[0]; win.cfg.set_string('profile',target)
        expected=loads_profile(target)
        assert win.profile==expected and win.entry.get_text()==expected['name']
        assert win.selected_path is not None
        win.controls['lines.gap'].set_value(9)
        assert loads_profile(win.cfg.get_string('profile'))['id']==expected['id']
        profile_before=win.cfg.get_string('profile')
        win.apply_shortcut('toggle-key','F8')
        assert win.cfg.get_strv('toggle-key')==['F8']
        win.apply_shortcut('size-up','<Control>F10')
        assert win.shortcuts.get('size-up')=='<Control>F10'
        try:
            win.apply_shortcut('size-down','<Control>F10')
            raise AssertionError('Duplicate shortcut was accepted')
        except ValueError: pass
        win.apply_shortcut('random-key','')
        assert win.cfg.get_strv('random-key')==[]
        win.og_controls.set_active(True)
        assert not win.shortcut_buttons['size-up'].get_sensitive()
        win.og_controls.set_active(False)
        assert win.cfg.get_strv('toggle-key')==['F8']
        assert win.shortcut_buttons['size-up'].get_sensitive()
        win.restore_shortcuts()
        assert win.cfg.get_strv('toggle-key')==['Home']
        assert win.shortcuts.get('size-up')=='<Shift>Page_Up'
        assert win.cfg.get_string('profile')==profile_before
        print('Settings shortcut editing, duplicate rejection, defaults and OG mode passed',flush=True)
        win.controls['opacity'].set_value(.37)
        win.randomize()
        win.capture_shortcut('size-down')
        dialog=next(w for w in Gtk.Window.list_toplevels() if w.get_title()=='Decrease size')
        controllers=dialog.observe_controllers()
        controller=next(controllers.get_item(i) for i in range(controllers.get_n_items())
                        if isinstance(controllers.get_item(i),Gtk.EventControllerKey))
        controller.emit('key-pressed',Gdk.KEY_F11,0,Gdk.ModifierType.CONTROL_MASK)
        assert win.shortcuts.get('size-down')=='<Control>F11'
        win.restore_shortcuts()
        win.tabs.set_current_page(2)
        print('External preset synchronization and shortcut settings passed',flush=True)
        print('GTK controls, settings bridge, profile save and invalid-edit preservation passed',flush=True)
    except Exception as e: failures.append(e)
    GLib.timeout_add(300,capture)
    return GLib.SOURCE_REMOVE

def capture():
    try:
        assert win.profile['id'].startswith('random-'), 'Randomize button did not apply a profile'
        assert win.profile['style']['opacity']==.37, 'Randomize button lost opacity'
        assert win.entry.get_text()==win.profile['name'], 'Editor did not follow random result'
        assert win.selected_path is None, 'Random result retained old reset target'
        print('Randomize button and editor synchronization passed',flush=True)
        assert win.preview.texture is not None, 'Preview did not render'
        paintable=Gtk.WidgetPaintable.new(win)
        snapshot=Gtk.Snapshot(); paintable.snapshot(snapshot,win.get_width(),win.get_height())
        node=snapshot.to_node()
        renderer=win.get_native().get_renderer()
        texture=renderer.render_texture(node,None)
        texture.save_to_png(str(Path(__file__).resolve().parents[1]/'build/editor.png'))
        print('Saved editor screenshot',flush=True)
    except Exception as e:
        failures.append(e); print('Capture/randomization check failed:',e,flush=True)
    win.close(); loop.quit(); return GLib.SOURCE_REMOVE
GLib.timeout_add(600,check); loop.run()
if failures: raise failures[0]
