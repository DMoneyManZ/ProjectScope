"""Original controls as a reversible settings mode, not a software rollback."""
import json

KEYS=('toggle-key','previous-key','next-key','random-key','save-key','color-key')
FLAGS=('show-label','invert-label','invert-crosshair')
CONTROL_KEYS=KEYS+FLAGS

def set_og(cfg, enabled):
    if cfg.get_boolean('og-controls')==enabled:
        return
    if enabled:
        current={key:cfg.get_value(key).unpack() for key in CONTROL_KEYS}
        cfg.set_string('updated-controls',json.dumps(current))
        cfg.set_boolean('og-controls',True)
        for key in KEYS: cfg.set_strv(key,['Home'] if key=='toggle-key' else [])
        for key in FLAGS: cfg.set_boolean(key,False)
    else:
        try:
            saved=json.loads(cfg.get_string('updated-controls'))
            valid=(type(saved) is dict and set(saved)==set(CONTROL_KEYS)
                and all(type(saved[k]) is list and all(type(v) is str for v in saved[k]) for k in KEYS)
                and all(type(saved[k]) is bool for k in FLAGS))
        except (ValueError,RecursionError):
            valid=False
        if not valid:
            saved={key:cfg.get_default_value(key).unpack() for key in CONTROL_KEYS}
        for key in KEYS: cfg.set_strv(key,saved[key])
        for key in FLAGS: cfg.set_boolean(key,saved[key])
        cfg.set_boolean('og-controls',False)
