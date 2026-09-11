import GLib from 'gi://GLib';
import {nextColor} from '../extension/colors.js';
const [,bytes]=GLib.file_get_contents('presets/cs2-precision.json');
let p=JSON.parse(new TextDecoder().decode(bytes));
const initial=JSON.stringify(p);
p=nextColor(p);
if(p.style.color!=='#003D3D'||p.style.outline_color!=='#FFFFFF')throw Error('Cyan must advance to contrasting dark color');
if(JSON.parse(initial).style.opacity!==p.style.opacity)throw Error('Opacity changed');
const shape=JSON.stringify(p.style.lines), seen=new Set();
for(let i=0;i<24;i++){
 p=nextColor(p);seen.add(p.style.color);
 const rgb=[1,3,5].map(j=>parseInt(p.style.color.slice(j,j+2),16)/255);
 const light=rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722>.5;
 if(light!==(i%2===0))throw Error('Colors did not alternate light/dark');
 if(JSON.stringify(p.style.lines)!==shape)throw Error('Color cycle changed geometry');
}
if(seen.size!==12)throw Error('Color cycle did not wrap through 12 colors');
print('Light/dark palette, wrap, outline contrast and shape preservation passed');
