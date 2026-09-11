// Geometry-only randomization: no image, game, input, or network inspection.
import {readStyle} from './draw.js';

export function randomProfile(current, rng=Math.random) {
    const pick=values=>values[Math.floor(rng()*values.length)];
    const family=pick(['Dot','Cross','Cross dot','Ring dot']);
    const token=Math.floor(rng()*0x100000000).toString(16).padStart(8,'0');
    let opacity=.85;
    try { opacity=readStyle(current).opacity; } catch (_) {}
    return {
        schema_version:1, id:'random-'+token, name:'Random '+family+' '+token,
        description:'Generated from compact FPS-style ranges. Manually editable; no game awareness.',
        game:'General FPS',
        style:{
            color:pick(['#00FFFF','#00FF66','#FFFF00','#FFFFFF','#FF66CC']),
            opacity,outline_color:'#000000',outline_width:pick([1,1.5]),
            rotation:0,scale:1,
            lines:{enabled:family==='Cross'||family==='Cross dot',
                length:pick([3,4,5,6,7,8]),thickness:pick([1,1.5,2]),
                gap:pick([2,3,4,5]),top:pick([true,true,false])},
            dot:{enabled:family!=='Cross',radius:pick([1,1.5,2])},
            circle:{enabled:family==='Ring dot',radius:pick([4,5,6,7]),thickness:pick([1,1.5])}
        }
    };
}
