"""Named user presets with collision-safe filenames."""
import re
from .profiles import validate_profile, load_profile, save_profile, ProfileError

def save_named_profile(profile, directory):
    candidate=validate_profile(profile)
    base=re.sub('[^a-z0-9]+','-',candidate['name'].lower()).strip('-')[:64].rstrip('-')
    if not base: raise ProfileError('Use at least one ASCII letter or digit in the preset name')
    slug=base; number=1
    while (directory/(slug+'.json')).exists():
        existing=load_profile(directory/(slug+'.json'))
        if existing['name']==candidate['name']: break
        number+=1; suffix=f'-{number}'; slug=base[:64-len(suffix)].rstrip('-')+suffix
    candidate['id']=slug
    save_profile(directory/(slug+'.json'),candidate)
    return candidate

def preset_catalog(stock_directory, user_directory):
    """Valid profiles ordered by ID, with personal copies taking precedence."""
    profiles={}
    for directory in (stock_directory,user_directory):
        for path in sorted(directory.glob('*.json')):
            try: profile=load_profile(path)
            except (OSError,ProfileError): continue
            profiles[profile['id']]=(path,profile)
    return [profiles[key] for key in sorted(profiles)]
