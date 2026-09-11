// Cache saved profiles when settings change; key presses never read the disk.
import {readStyle} from './draw.js';
export function readLibrary(entries) {
    const seen=new Set(), library=[];
    for (const text of entries) {
        try {
            readStyle(text);
            const {id}=JSON.parse(text);
            if (typeof id!=='string' || !/^[a-z0-9][a-z0-9-]{0,63}$/.test(id) || seen.has(id)) continue;
            seen.add(id); library.push({id,text});
        } catch (_) { /* Ignore malformed entries without breaking the overlay. */ }
    }
    return library;
}
export function cycleProfile(library,current,direction) {
    if (!library.length) return null;
    let id;
    try { id=JSON.parse(current).id; } catch (_) {}
    const index=library.findIndex(p=>p.id===id);
    const next=index<0 ? (direction>0 ? 0 : library.length-1)
        : (index+(direction>0 ? 1 : -1)+library.length)%library.length;
    return library[next].text;
}
