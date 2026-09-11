"""Start an isolated GNOME Shell; never replace the user's desktop."""
import os,sys,subprocess,time,json
from pathlib import Path
import gi
from gi.repository import Gio,GLib
root=Path(sys.argv[1]); log=(root/'shell.log').open('w')
settings=Gio.Settings.new('org.gnome.shell')
settings.set_strv('enabled-extensions',['projectscope-test-inspector@local','projectscope@local']); Gio.Settings.sync()
shell=subprocess.Popen(['gnome-shell','--headless','--wayland','--no-x11','--wayland-display=projectscope-test','--virtual-monitor=1280x900'],stdout=log,stderr=subprocess.STDOUT)
try:
    bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    info=None
    for _ in range(40):
        if shell.poll() is not None: raise RuntimeError('Nested shell exited')
        try:
            result=bus.call_sync('org.gnome.Shell','/org/gnome/Shell','org.gnome.Shell.Extensions',
                'GetExtensionInfo',GLib.Variant('(s)',('projectscope@local',)),None,Gio.DBusCallFlags.NONE,500,None)
            info=result.unpack()[0]
            if info.get('state')==1: break
        except GLib.Error: pass
        time.sleep(.25)
    print('Nested extension info:',info,flush=True)
    if not info or info.get('state')!=1: raise RuntimeError('Extension not active in test shell')
    intro=bus.call_sync('org.gnome.Mutter.RemoteDesktop','/org/gnome/Mutter/RemoteDesktop',
        'org.freedesktop.DBus.Introspectable','Introspect',None,None,Gio.DBusCallFlags.NONE,1000,None).unpack()[0]
    Path('build/remote.xml').write_text(intro)
    remote_path=bus.call_sync('org.gnome.Mutter.RemoteDesktop','/org/gnome/Mutter/RemoteDesktop',
        'org.gnome.Mutter.RemoteDesktop','CreateSession',None,None,Gio.DBusCallFlags.NONE,1000,None).unpack()[0]
    intro=bus.call_sync('org.gnome.Mutter.RemoteDesktop',remote_path,
        'org.freedesktop.DBus.Introspectable','Introspect',None,None,Gio.DBusCallFlags.NONE,1000,None).unpack()[0]
    Path('build/remote-session.xml').write_text(intro)
    os.environ['GDK_BACKEND']='wayland'; os.environ['WAYLAND_DISPLAY']='projectscope-test'; os.environ.pop('DISPLAY',None)
    result=subprocess.run([sys.executable,'tests/gui_smoke.py'],timeout=30)
    if result.returncode: raise RuntimeError('GUI smoke failed')
    # Inject input only into this isolated virtual desktop, never the live session.
    def remote(method,args=None):
        return bus.call_sync('org.gnome.Mutter.RemoteDesktop',remote_path,
            'org.gnome.Mutter.RemoteDesktop.Session',method,args,None,Gio.DBusCallFlags.NONE,1000,None)
    remote('Start')
    source=Gio.SettingsSchemaSource.new_from_directory(str(Path('extension/schemas').resolve()),Gio.SettingsSchemaSource.get_default(),False)
    cfg=Gio.Settings.new_full(source.lookup('org.gnome.shell.extensions.projectscope',False),None,None)
    probe=subprocess.Popen([sys.executable,'tests/fullscreen_probe.py',str(root)])
    try:
        for _ in range(30):
            if (root/'probe-ready').exists(): break
            time.sleep(.1)
        if not (root/'probe-ready').exists(): raise RuntimeError('Fullscreen probe unavailable')
        # Escape closes the overview if the fresh shell starts there.
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff1b,True)))
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff1b,False)))
        time.sleep(.3)
        cfg.set_boolean('visible',True); Gio.Settings.sync(); time.sleep(.2)
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,True)))
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,False)))
        time.sleep(.2)
        while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        assert not cfg.get_boolean('visible'), 'Home did not hide the crosshair'
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,True)))
        time.sleep(.7)  # Held key must not repeatedly toggle.
        while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        assert cfg.get_boolean('visible'), 'Held Home unexpectedly repeated'
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,False)))
        remote('NotifyPointerMotionRelative',GLib.Variant('(dd)',(-10000.,-10000.)))
        time.sleep(.1)  # Separate motions so they are not coalesced into no movement.
        remote('NotifyPointerMotionRelative',GLib.Variant('(dd)',(640.,450.)))
        time.sleep(.25)  # Let Wayland deliver pointer-enter before the click.
        remote('NotifyPointerButton',GLib.Variant('(ib)',(272,True)))
        time.sleep(.05)
        remote('NotifyPointerButton',GLib.Variant('(ib)',(272,False)))
        time.sleep(.2)
        click_ok=(root/'clicked').exists()
        assert click_ok, 'Fullscreen click was not delivered with the overlay enabled'
        print('Home hide/show, repeat suppression and fullscreen click-through passed',flush=True)
        def inspect(method,value):
            return bus.call_sync('org.gnome.Shell','/io/projectscope/TestInspector','io.projectscope.TestInspector',
                method,GLib.Variant('(s)',(value,)),None,Gio.DBusCallFlags.NONE,3000,None)
        test_profile=json.loads(cfg.get_string('profile'))
        test_profile['id']='inversion-test'; test_profile['name']='Sniper01'
        test_profile['style']['opacity']=1
        test_profile['style']['dot']['enabled']=True
        test_profile['style']['dot']['radius']=2
        test_profile['style']['lines']['enabled']=False
        test_profile['style']['circle']['enabled']=False
        cfg.set_boolean('invert-crosshair',True)
        cfg.set_string('profile',json.dumps(test_profile)); Gio.Settings.sync(); time.sleep(.3)
        from PIL import Image
        for color,name,bright in [('#000000','invert-dark',True),('#FFFFFF','invert-light',False)]:
            inspect('Backdrop',color); time.sleep(.2)
            result=json.loads(inspect('Snapshot',name).unpack()[0])
            pixel=Image.open(result['path']).convert('RGB').getpixel((640,450))
            assert all(c>200 if bright else c<55 for c in pixel), f'Inversion failed on {color}: {pixel}'
            assert result['state'] and 'Sniper01' in result['state']['text'], 'Preset label missing'
            assert result['state']['visible'] and result['state']['opacity']>0
            tx,ty=result['state']['position'];tw,th=result['state']['size']
            crop=Image.open(result['path']).convert('RGB').crop((int(tx),int(ty),int(tx+tw),int(ty+th)))
            pixels=list(crop.get_flattened_data())
            assert any(all(c>200 if bright else c<55 for c in pixel) for pixel in pixels), 'Label lacks inversion contrast'
        time.sleep(3.3)
        result=json.loads(inspect('Snapshot','label-faded').unpack()[0])
        assert not result['state']['visible'] or result['state']['opacity']==0, 'Preset label did not fade'
        cfg.set_boolean('invert-crosshair',False); Gio.Settings.sync()
        print('Actual compositor inversion pixels on black/white and fading preset label passed',flush=True)

        def settle():
            time.sleep(.2)
            while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        def key(symbol,hold=.02):
            remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(symbol,True)))
            time.sleep(hold)
            remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(symbol,False)))
            settle()
        library=cfg.get_strv('preset-library')
        assert len(library)>=7, 'Saved custom preset missing from cycling library'
        cfg.set_string('profile',library[0]); cfg.set_boolean('visible',False)
        Gio.Settings.sync(); settle()
        key(0xff55)
        assert cfg.get_string('profile')==library[-1], 'Page Up failed to wrap'
        assert not cfg.get_boolean('visible'), 'Cycling revealed a hidden crosshair'
        key(0xff56)
        assert cfg.get_string('profile')==library[0], 'Page Down failed to wrap'
        key(0xff56,.7)
        assert cfg.get_string('profile')==library[1], 'Held Page Down repeated or failed'
        for expected in library[2:]+library[:1]:
            key(0xff56)
            assert cfg.get_string('profile')==expected, 'Cycling order differs from sidebar'
        cfg.set_strv('next-key',[]); Gio.Settings.sync(); settle()
        before=cfg.get_string('profile'); key(0xff56)
        assert cfg.get_string('profile')==before, 'Disabled shortcut still cycles'
        cfg.set_strv('next-key',['Page_Down']); cfg.set_boolean('visible',True)
        Gio.Settings.sync(); settle()
        print('Editor-closed cycling, custom presets, wrapping, repeat suppression, hidden state and disabled shortcut passed',flush=True)
        cfg.set_boolean('visible',False); Gio.Settings.sync(); settle()
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff13,True)))
        settle()
        generated=cfg.get_string('profile')
        assert json.loads(generated)['id'].startswith('random-'), 'Pause did not generate a profile'
        time.sleep(.7); settle()
        assert cfg.get_string('profile')==generated, 'Held Pause generated repeatedly'
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff13,False)))
        assert not cfg.get_boolean('visible'), 'Randomize revealed a hidden crosshair'
        assert json.loads(generated)['style']['opacity']==json.loads(library[0])['style']['opacity']
        for binding,symbol in [('F9',0xffc6)]:
            cfg.set_strv('random-key',[binding]); Gio.Settings.sync(); settle()
            before=cfg.get_string('profile'); key(symbol)
            assert cfg.get_string('profile')!=before, binding+' failed to randomize'
        cfg.set_strv('random-key',[]); Gio.Settings.sync(); settle()
        before=cfg.get_string('profile'); key(0xffc6); key(0xff13)
        assert cfg.get_string('profile')==before, 'Disabled random shortcut still acts'
        cfg.set_strv('random-key',['Pause']); cfg.set_string('profile',library[0])
        cfg.set_boolean('visible',True); Gio.Settings.sync(); settle()
        print('Pause/F9 randomization, repeat suppression, opacity preservation and disabled shortcut passed',flush=True)
        custom=json.loads(cfg.get_string('profile'))
        custom['name']='Saved by Insert'; custom['style']['color']='#00FFFF'
        cfg.set_string('profile',json.dumps(custom));cfg.set_boolean('invert-crosshair',True)
        Gio.Settings.sync();settle()
        key(0xff57)
        colored=json.loads(cfg.get_string('profile'))
        assert colored['style']['color']=='#003D3D' and colored['style']['outline_color']=='#FFFFFF'
        assert colored['style']['lines']==custom['style']['lines']
        assert not cfg.get_boolean('invert-crosshair'), 'End did not show selected color'
        key(0xff63)
        saved_path=Path(os.environ['XDG_DATA_HOME'])/'projectscope/presets/saved-by-insert.json'
        for _ in range(20):
            settle()
            if saved_path.exists(): break
        assert saved_path.exists(), 'Insert did not save with editor closed'
        assert json.loads(saved_path.read_text())['style']['color']=='#003D3D'
        assert any(json.loads(p)['id']=='saved-by-insert' for p in cfg.get_strv('preset-library'))
        inspect('Snapshot','saved-label')
        cfg.set_string('profile',library[0]);Gio.Settings.sync();settle()
        print('End alternates color without changing shape; Insert saves and updates cycling with editor closed',flush=True)
        def extension_call(method):
            return bus.call_sync('org.gnome.Shell','/org/gnome/Shell','org.gnome.Shell.Extensions',
                method,GLib.Variant('(s)',('projectscope@local',)),None,Gio.DBusCallFlags.NONE,1000,None)
        extension_call('DisableExtension'); time.sleep(.2)
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,True)))
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,False)))
        time.sleep(.2)
        while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        assert cfg.get_boolean('visible'), 'Disabled extension retained the Home binding'
        before=cfg.get_string('profile'); key(0xff55); key(0xff56); key(0xff13)
        key(0xff57); key(0xff63)
        assert cfg.get_string('profile')==before, 'Disabled extension retained profile shortcuts'
        extension_call('EnableExtension'); time.sleep(.2)
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,True)))
        remote('NotifyKeyboardKeysym',GLib.Variant('(ub)',(0xff50,False)))
        time.sleep(.2)
        while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
        assert not cfg.get_boolean('visible'), 'Re-enabled extension failed or duplicated its binding'
        key(0xff56)
        assert cfg.get_string('profile')==library[1], 'Re-enabled cycling failed'
        key(0xff13)
        assert json.loads(cfg.get_string('profile'))['id'].startswith('random-')
        print('Disable releases random binding; re-enable restores randomization',flush=True)
        print('Disable releases cycling bindings; re-enable restores cycling',flush=True)
        print('Disable releases Home; re-enable restores exactly one toggle handler',flush=True)

    finally:
        probe.terminate(); probe.wait(timeout=3); remote('Stop')
    errors=bus.call_sync('org.gnome.Shell','/org/gnome/Shell','org.gnome.Shell.Extensions',
        'GetExtensionErrors',GLib.Variant('(s)',('projectscope@local',)),None,Gio.DBusCallFlags.NONE,1000,None).unpack()
    print('Extension errors:',errors,flush=True)
    if errors[0]: raise RuntimeError('Extension reported errors')
    assert click_ok, 'Fullscreen click was not delivered'
finally:
    shell.terminate()
    try: shell.wait(timeout=5)
    except subprocess.TimeoutExpired: shell.kill(); shell.wait()
    log.close()
    print('Shell log:',root/'shell.log',flush=True)
