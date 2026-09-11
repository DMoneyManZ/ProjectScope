import Cairo from 'cairo';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import {nextColor} from './colors.js';
import Clutter from 'gi://Clutter';
import {InvertEffect} from './invert.js';
import {presetLabel} from './label.js';
import {randomProfile} from './random.js';
import {readLibrary, cycleProfile} from './cycle.js';
import St from 'gi://St';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {readStyle, extent, draw} from './draw.js';

export default class ProjectScope extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._signals = [];
        this._actor = new St.DrawingArea({reactive:false, can_focus:false, name:'projectscope-crosshair', accessible_name:'ProjectScope crosshair'});
        this._actor.connect('repaint', area => {
            if (!this._style) return;
            const cr=area.get_context();
            try {
                const [w,h]=area.get_surface_size();
                const style=this._settings.get_boolean('invert-crosshair')
                    ? {...this._style,color:'#FFFFFF',outline_width:0} : this._style;
                draw(cr,style,w/2,h/2);
            } finally { cr.$dispose(); }
        });
        Main.layoutManager.addTopChrome(this._actor, {affectsStruts:false, trackFullscreen:false});
        this._toast=new St.DrawingArea({name:'projectscope-preset-label',reactive:false,can_focus:false,visible:false});
        this._toast.text='';
        this._toast.connect('repaint',area=>{
            const cr=area.get_context();
            try {
                cr.selectFontFace('Sans',0,1); cr.setFontSize(14); cr.moveTo(3,19);
                if(!this._settings.get_boolean('invert-label')) {
                    cr.setSourceRGB(0,0,0);
                    for(const [dx,dy] of [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]]) {
                        cr.moveTo(3+dx,19+dy);cr.showText(area.text);
                    }
                }
                cr.setSourceRGB(1,1,1);cr.moveTo(3,19);cr.showText(area.text);
            } finally {cr.$dispose();}
        });
        Main.layoutManager.addTopChrome(this._toast,{affectsStruts:false,trackFullscreen:false});
        this._configureEffects();
        const watch=(obj,event,fn)=>this._signals.push([obj,obj.connect(event,fn)]);
        watch(this._settings,'changed',(_s,key)=> {
            if (key==='profile') this._load(true);
            else if (key==='random-request') this._randomize();
            else if (key==='preset-library') this._library=readLibrary(this._settings.get_strv(key));
            else {
                if (['invert-crosshair','invert-label'].includes(key)) {
                    this._configureEffects(); this._actor.queue_repaint();
                }
                this._update();
            }
        });
        watch(Main.layoutManager,'monitors-changed',()=>this._update());
        watch(Main.sessionMode,'updated',()=>this._update());
        watch(Main.overview,'showing',()=>this._update());
        watch(Main.overview,'hidden',()=>this._update());
        Main.wm.addKeybinding('toggle-key',this._settings,Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
            Shell.ActionMode.NORMAL,()=>this._settings.set_boolean('visible',!this._settings.get_boolean('visible')));
        this._library=readLibrary(this._settings.get_strv('preset-library'));
        for (const [key,direction] of [['previous-key',-1],['next-key',1]])
            Main.wm.addKeybinding(key,this._settings,Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
                Shell.ActionMode.NORMAL,()=> {
                    const profile=cycleProfile(this._library,this._settings.get_string('profile'),direction);
                    if (profile!==null) this._settings.set_string('profile',profile);
                });
        Main.wm.addKeybinding('random-key',this._settings,Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
            Shell.ActionMode.NORMAL,()=>this._randomize());
        Main.wm.addKeybinding('save-key',this._settings,Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
            Shell.ActionMode.NORMAL,()=>this._save());
        Main.wm.addKeybinding('color-key',this._settings,Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
            Shell.ActionMode.NORMAL,()=> {
                if(!this._style) return;
                this._settings.set_boolean('invert-crosshair',false);
                this._settings.set_string('profile',JSON.stringify(nextColor(JSON.parse(this._settings.get_string('profile')))));
                this._showLabel();
            });
        this._load();
    }
    _save() {
        if(this._saveProcess) return;
        const snapshot=this._settings.get_string('profile');
        const helper=GLib.build_filenamev([GLib.get_user_data_dir(),'projectscope','app','tools','hotkey_save.py']);
        try {
            const proc=Gio.Subprocess.new(['/usr/bin/python3',helper],
                Gio.SubprocessFlags.STDIN_PIPE|Gio.SubprocessFlags.STDOUT_PIPE|Gio.SubprocessFlags.STDERR_PIPE);
            this._saveProcess=proc;
            proc.communicate_utf8_async(snapshot,null,(process,result)=>{
                try {
                    if(this._saveProcess!==process) return;
                    const [,stdout,stderr]=process.communicate_utf8_finish(result);
                    if(!this._settings) return;
                    if(!process.get_successful()) throw Error(stderr.trim()||'Save failed');
                    const saved=JSON.parse(stdout); const text=JSON.stringify(saved.profile);
                    readStyle(text);
                    this._settings.set_strv('preset-library',saved.library);
                    if(this._settings.get_string('profile')===snapshot) this._settings.set_string('profile',text);
                    this._showLabel('Saved · '+presetLabel(text));
                } catch(e) {
                    if(this._settings) this._showLabel('Save failed · open ProjectScope to save');
                    console.error('ProjectScope save: '+e.message);
                } finally {if(this._saveProcess===process)this._saveProcess=null;}
            });
        } catch(e) {this._showLabel('Save failed · open ProjectScope to save');}
    }
    _randomize() {
        this._settings.set_string('profile',JSON.stringify(randomProfile(this._settings.get_string('profile'))));
    }
    _configureEffects() {
        for (const [actor,key] of [[this._actor,'invert-crosshair'],[this._toast,'invert-label']]) {
            actor.remove_effect_by_name('projectscope-inversion');
            if(this._settings.get_boolean(key)) actor.add_effect_with_name('projectscope-inversion',new InvertEffect());
        }
        this._toast.queue_repaint();
    }
    _showLabel(message=null) {
        if(!this._settings.get_boolean('show-label') || Main.sessionMode.isLocked ||
            Main.sessionMode.isGreeter || Main.overview.visible) return;
        this._toast.remove_all_transitions();
        this._toast.text=message??presetLabel(this._settings.get_string('profile'));
        const monitor=Main.layoutManager.monitors[this._settings.get_int('monitor')] ?? Main.layoutManager.primaryMonitor;
        if(!monitor) return;
        const cr=new Cairo.Context(new Cairo.ImageSurface(Cairo.Format.ARGB32,1,1));
        cr.selectFontFace('Sans',0,1);cr.setFontSize(14);
        const width=Math.min(Math.ceil(cr.textExtents(this._toast.text).xAdvance)+8,Math.max(1,monitor.width-48));
        cr.$dispose();
        this._toast.set_size(width,26);this._toast.queue_repaint();
        this._toast.set_position(monitor.x+monitor.width-width-24,monitor.y+48);
        this._toast.opacity=255; this._toast.show();
        this._toast.ease({opacity:0,delay:1800,duration:1200,mode:Clutter.AnimationMode.EASE_OUT_QUAD,
            onComplete:()=>this._toast?.hide()});
    }
    _load(notify=false) {
        let id;
        try {
            const text=this._settings.get_string('profile');
            this._style=readStyle(text); id=JSON.parse(text).id;
        }
        catch (e) { this._style=null; console.error(`ProjectScope: ${e.message}`); }
        this._update();
        this._actor.queue_repaint();
        if(notify && id && id!==this._profileId && this._style) this._showLabel();
        this._profileId=id;
    }
    _update() {
        if(this._toast && (!this._settings.get_boolean('show-label') || Main.sessionMode.isLocked ||
            Main.sessionMode.isGreeter || Main.overview.visible)) {
            this._toast.remove_all_transitions(); this._toast.hide();
        }
        const monitors=Main.layoutManager.monitors;
        const index=this._settings.get_int('monitor');
        const monitor=monitors[index] ?? Main.layoutManager.primaryMonitor;
        if (!monitor || !this._style) { this._actor.hide(); return; }
        const size=Math.ceil(extent(this._style))*2;
        this._actor.set_size(size,size);
        const x=Math.max(-monitor.width/2,Math.min(monitor.width/2,this._settings.get_int('offset-x')));
        const y=Math.max(-monitor.height/2,Math.min(monitor.height/2,this._settings.get_int('offset-y')));
        this._actor.set_position(Math.round(monitor.x+monitor.width/2+x-size/2),
            Math.round(monitor.y+monitor.height/2+y-size/2));
        this._actor.visible=this._settings.get_boolean('visible') && !Main.sessionMode.isLocked &&
            !Main.sessionMode.isGreeter && !Main.overview.visible;
    }
    disable() {
        if(this._saveProcess) {this._saveProcess.force_exit();this._saveProcess=null;}
        for (const key of ['toggle-key','previous-key','next-key','random-key','save-key','color-key']) Main.wm.removeKeybinding(key);
        for (const [obj,id] of this._signals ?? []) obj.disconnect(id);
        this._signals=[];
        if(this._actor) { Main.layoutManager.removeChrome(this._actor); this._actor.destroy(); }
        if(this._toast) {
            this._toast.remove_all_transitions(); Main.layoutManager.removeChrome(this._toast); this._toast.destroy();
        }
        this._toast=null; this._profileId=null;
        this._library=[]; this._actor=null; this._style=null; this._settings=null;
    }
}
