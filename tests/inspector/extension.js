import Clutter from 'gi://Clutter';
// Test-only screenshot/actor inspection in a separate virtual desktop.
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Shell from 'gi://Shell';
import St from 'gi://St';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
const xml='<node><interface name="io.projectscope.TestInspector"><method name="Snapshot"><arg type="s" direction="in"/><arg type="s" direction="out"/></method><method name="Backdrop"><arg type="s" direction="in"/></method></interface></node>';
export default class Inspector extends Extension {
    enable() {
        this.dbus=Gio.DBusExportedObject.wrapJSObject(xml,this);
        this.dbus.export(Gio.DBus.session,'/io/projectscope/TestInspector');
    }
    Backdrop(color) {
        if(!this.backdrop) {
            this.backdrop=new St.Widget({reactive:false,width:1280,height:900});
            Main.layoutManager.addTopChrome(this.backdrop,{trackFullscreen:false});
            const actor=Main.layoutManager.uiGroup.get_children().find(a=>a.name==='projectscope-crosshair');
            Main.layoutManager.uiGroup.set_child_below_sibling(this.backdrop,actor);
        }
        this.backdrop.set_style('background-color: '+color+';');
    }
    SnapshotAsync([name],invocation) {
        const actor=Main.layoutManager.uiGroup.get_children().find(a=>a.name==='projectscope-preset-label');
        const picked=global.stage.get_actor_at_pos(Clutter.PickMode.REACTIVE,640,450);
        const state=actor ? {visible:actor.visible,opacity:actor.opacity,text:actor.text,
            modal:Main.modalCount,grab:global.stage.get_grab_actor()?.toString(),pointer:global.get_pointer(),position:actor.get_position(),size:actor.get_size(),picked:picked?.toString()} : null;
        const path=GLib.build_filenamev([GLib.get_user_runtime_dir(),name.replace(/[^a-z0-9-]/g,'')+'.png']);
        const stream=Gio.File.new_for_path(path).replace(null,false,Gio.FileCreateFlags.REPLACE_DESTINATION,null);
        const shot=new Shell.Screenshot();
        shot.screenshot(false,stream,(obj,result)=>{
            try {obj.screenshot_finish(result);stream.close(null);
                invocation.return_value(new GLib.Variant('(s)',[JSON.stringify({state,path})]));
            } catch(e){invocation.return_dbus_error('io.projectscope.Error',e.message);}
        });
    }
    disable() {
        this.dbus?.unexport();
        if(this.backdrop){Main.layoutManager.removeChrome(this.backdrop);this.backdrop.destroy();}
    }
}
