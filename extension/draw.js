// Pure geometry + Cairo drawing, shared by shell renderer and GJS checks.
export function readStyle(text) {
    if (typeof text !== 'string' || text.length > 65536) throw Error('Invalid profile size');
    const p = JSON.parse(text);
    if (p.schema_version !== 1) throw Error('Unsupported profile');
    const s = p.style;
    for (const key of ['color', 'outline_color'])
        if (!/^#[0-9a-fA-F]{6}$/.test(s[key])) throw Error('Invalid color');
    const ranges = [[s,'opacity',0,1],[s,'outline_width',0,8],[s,'scale',.25,8],
        [s,'rotation',-180,180],[s.lines,'length',1,100],[s.lines,'gap',0,100],
        [s.lines,'thickness',.5,20],[s.dot,'radius',.5,20],
        [s.circle,'radius',1,100],[s.circle,'thickness',.5,20]];
    for (const [obj,key,lo,hi] of ranges)
        if (typeof obj?.[key] !== 'number' || !Number.isFinite(obj[key]) || obj[key]<lo || obj[key]>hi)
            throw Error(`Invalid ${key}`);
    for (const key of ['lines','dot','circle'])
        if (typeof s[key].enabled !== 'boolean') throw Error('Invalid enabled flag');
    if (typeof s.lines.top !== 'boolean') throw Error('Invalid top flag');
    if (![s.lines,s.dot,s.circle].some(x => x.enabled)) throw Error('Empty profile');
    return s;
}
export function extent(s) {
    const l=s.lines, radii=[0], pad=s.outline_width;
    if (l.enabled) radii.push(Math.hypot(l.gap+l.length+pad,l.thickness/2+pad));
    if (s.dot.enabled) radii.push(s.dot.radius+pad);
    if (s.circle.enabled) radii.push(s.circle.radius+s.circle.thickness/2+pad);
    return Math.max(...radii)*s.scale+2;
}
export function draw(cr,s,cx,cy) {
    cr.save(); cr.translate(cx,cy); cr.rotate(s.rotation*Math.PI/180);
    cr.scale(s.scale,s.scale); cr.pushGroup();
    function color(hex) { cr.setSourceRGB(...[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255)); }
    function shapes(pad) {
        const l=s.lines,t=l.thickness,g=l.gap,n=l.length;
        if (l.enabled) {
            const rects=[[g,-t/2,n,t],[-g-n,-t/2,n,t],[-t/2,g,t,n]];
            if (l.top) rects.push([-t/2,-g-n,t,n]);
            for (const [x,y,w,h] of rects) cr.rectangle(x-pad,y-pad,w+2*pad,h+2*pad);
            cr.fill();
        }
        if (s.dot.enabled) { cr.arc(0,0,s.dot.radius+pad,0,2*Math.PI); cr.fill(); }
        if (s.circle.enabled) {
            cr.arc(0,0,s.circle.radius,0,2*Math.PI);
            cr.setLineWidth(s.circle.thickness+2*pad); cr.stroke();
        }
    }
    if(s.outline_width>0) { color(s.outline_color); shapes(s.outline_width); }
    color(s.color); shapes(0);
    cr.popGroupToSource(); cr.paintWithAlpha(s.opacity); cr.restore();
}
