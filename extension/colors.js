// Alternate bright/dark colors; only user-selected profile values are used.
export const COLORS=['#FFFFFF','#202020','#00FFFF','#003D3D','#FFFF00','#403300','#00FF66','#003D18','#FF88CC','#401030','#FFAA33','#402000'];
export function nextColor(profile) {
    const p=JSON.parse(JSON.stringify(profile));
    let index=COLORS.indexOf(p.style.color.toUpperCase());
    if(index<0) {
        const rgb=[1,3,5].map(i=>parseInt(p.style.color.slice(i,i+2),16)/255);
        index=(rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722)>.5 ? 0 : -1;
    }
    const next=(index+1)%COLORS.length;
    p.style.color=COLORS[next];
    p.style.outline_color=next%2===0 ? '#000000' : '#FFFFFF';
    return p;
}
