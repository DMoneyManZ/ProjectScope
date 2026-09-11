import GLib from 'gi://GLib';
import Cairo from 'cairo';
import {readStyle,extent,draw} from '../extension/draw.js';
const [,bytes]=GLib.file_get_contents('presets/cs2-precision.json');
const text=new TextDecoder().decode(bytes), s=readStyle(text);
if(extent(s)<13 || extent(s)>15) throw Error('Extent incorrect');
for(const bad of ['{}',text.replace('"opacity": 1.0','"opacity": true'),text.replace('"length": 6.0','"length": 1000')]) {
    let failed=false; try {readStyle(bad);} catch {failed=true;}
    if(!failed) throw Error('Invalid style accepted');
}
const surface=new Cairo.ImageSurface(Cairo.Format.ARGB32,80,80);
draw(new Cairo.Context(surface),s,40,40);
surface.writeToPNG('/tmp/projectscope-gjs-test.png');
print('GJS validation, extent, Cairo rendering passed');

const thick=readStyle(text); thick.lines.length=1; thick.lines.gap=0; thick.lines.thickness=20;
thick.outline_width=8; thick.scale=4; thick.rotation=45;
if(extent(thick)<82) throw Error("Outlined corners would be clipped");

const large=JSON.parse(text); large.style.scale=8; readStyle(JSON.stringify(large));
