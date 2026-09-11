import GLib from 'gi://GLib';
import {readLibrary,cycleProfile} from '../extension/cycle.js';
const [,bytes]=GLib.file_get_contents('presets/cs2-precision.json');
const p=JSON.parse(new TextDecoder().decode(bytes));
const a=JSON.stringify({...p,id:'a'}), b=JSON.stringify({...p,id:'b'});
const lib=readLibrary(['bad',a,b,a]);
function check(ok){if(!ok)throw Error('Cycle assertion failed');}
check(lib.length===2);
check(cycleProfile(lib,a,1)===b);
check(cycleProfile(lib,b,1)===a);
check(cycleProfile(lib,a,-1)===b);
check(cycleProfile(lib,'{}',1)===a);
check(cycleProfile(lib,'{}',-1)===b);
check(cycleProfile([],a,1)===null);
check(cycleProfile(readLibrary([a]),a,1)===a);
print('Preset cycling validation, order, wrap and empty-library checks passed');
