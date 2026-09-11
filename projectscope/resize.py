"""Change the current design's overall scale without altering its other settings."""
from .profiles import loads_profile, dumps_profile


def resize(cfg, direction, maximum=8):
    if direction not in (-1, 1):
        raise ValueError('Direction must be -1 or 1')
    if cfg.get_boolean('og-controls'):
        return
    profile = loads_profile(cfg.get_string('profile'))
    scale = profile['style']['scale']
    updated = round(max(.25, min(maximum, scale + direction * .25)), 6)
    if updated != scale:
        profile['style']['scale'] = updated
        cfg.set_string('profile', dumps_profile(profile))


def thicken(cfg, direction):
    if direction not in (-1, 1):
        raise ValueError('Direction must be -1 or 1')
    if cfg.get_boolean('og-controls'):
        return
    profile = loads_profile(cfg.get_string('profile'))
    style = profile['style']
    for group in ['lines', 'circle', 'dot']:
        if style[group]['enabled']:
            field = 'radius' if group == 'dot' else 'thickness'
            style[group][field] = round(max(.5, min(20, style[group][field] + direction * .25)), 6)
    cfg.set_string('profile', dumps_profile(profile))
