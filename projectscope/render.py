"""Cairo preview drawing; dimensions are logical pixels, opacity applied once."""
import math

def extent(s):
    l=s['lines']; radii=[0]; pad=s['outline_width']
    if l['enabled']: radii.append(math.hypot(l['gap']+l['length']+pad,l['thickness']/2+pad))
    if s['dot']['enabled']: radii.append(s['dot']['radius']+pad)
    if s['circle']['enabled']: radii.append(s['circle']['radius']+s['circle']['thickness']/2+pad)
    return max(radii)*s['scale']+2

def draw(cr,s,cx,cy):
    cr.save(); cr.translate(cx,cy); cr.rotate(math.radians(s['rotation']))
    cr.scale(s['scale'],s['scale']); cr.push_group()
    def color(hex): cr.set_source_rgb(*(int(hex[i:i+2],16)/255 for i in (1,3,5)))
    def shapes(pad):
        l=s['lines']; t=l['thickness']; g=l['gap']; n=l['length']
        if l['enabled']:
            rects=[(g,-t/2,n,t),(-g-n,-t/2,n,t),(-t/2,g,t,n)]
            if l['top']: rects.append((-t/2,-g-n,t,n))
            for x,y,w,h in rects: cr.rectangle(x-pad,y-pad,w+2*pad,h+2*pad)
            cr.fill()
        d=s['dot']
        if d['enabled']:
            cr.arc(0,0,d['radius']+pad,0,2*math.pi); cr.fill()
        c=s['circle']
        if c['enabled']:
            cr.arc(0,0,c['radius'],0,2*math.pi)
            cr.set_line_width(c['thickness']+2*pad); cr.stroke()
    if s['outline_width']>0:
        color(s['outline_color']); shapes(s['outline_width'])
    color(s['color']); shapes(0)
    cr.pop_group_to_source(); cr.paint_with_alpha(s['opacity']); cr.restore()
