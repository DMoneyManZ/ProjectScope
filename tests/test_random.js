// Catch invisible/oversized geometry, broken portable JSON, and lost opacity.
import {randomProfile} from '../extension/random.js';
import {readStyle,extent} from '../extension/draw.js';
function check(value,message){if(!value)throw Error(message);}
let seed=7143;
function rng(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
const shapes=new Set();
for(let i=0;i<1000;i++){
    const p=randomProfile('{"schema_version":1}',rng);
    const text=JSON.stringify(p), s=readStyle(text);
    check(extent(s)<20,'Generated crosshair is too large');
    check(s.opacity>=.5,'Fallback opacity is unreadable');
    check(s.outline_width>=1,'Missing contrast outline');
    shapes.add([s.lines.enabled,s.dot.enabled,s.circle.enabled].join());
    print(text); // Python validates the complete portable contract too.
}
check(shapes.size>=4,'Generator did not vary shape families');
const first=randomProfile('{}',()=>0);
first.style.opacity=.37;
const second=randomProfile(JSON.stringify(first),()=>.999999);
check(second.style.opacity===.37,'Randomization lost user opacity');
check(first.id!==second.id,'Distinct draws should have distinct save names');
readStyle(JSON.stringify(second));
