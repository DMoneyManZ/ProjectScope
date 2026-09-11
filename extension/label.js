export function presetLabel(text) {
    const p=JSON.parse(text);
    const name=String(p.name??'Preset').replace(/[\x00-\x1f\x7f]/g,'').slice(0,48);
    const color=p.style.color;
    const [r,g,b]=[1,3,5].map(i=>parseInt(color.slice(i,i+2),16));
    return name+' · [R'+r+' G'+g+' B'+b+']';
}
