"""Strict portable preset contract v1. Python standard library only."""
import copy
import json
import math
import os
from pathlib import Path
import re
import tempfile

MAX_BYTES = 65536

class ProfileError(ValueError):
    """Invalid or unsupported preset content."""

def _object(value, keys, path):
    if type(value) is not dict:
        raise ProfileError(f'{path}: expected an object')
    if set(value) != set(keys.split()):
        raise ProfileError(f'{path}: missing or unknown fields')

def _number(value, low, high, path):
    # Compare integers before any float conversion: arbitrary-size ints are legal
    # Python inputs but must not overflow math.isfinite or error formatting.
    if type(value) not in (int, float):
        raise ProfileError(f'{path}: expected a number')
    if not low <= value <= high or (type(value) is float and not math.isfinite(value)):
        raise ProfileError(f'{path}: expected a finite number in {low}..{high}')

def validate_profile(value: object) -> dict:
    _object(value, 'schema_version id name description game style', '$')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ProfileError('schema_version: only integer version 1 is supported')
    if type(value['id']) is not str or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',value['id']):
        raise ProfileError('id: use 1..64 lowercase ASCII letters, digits or hyphens')
    for key, low, high in [('name',1,80),('game',1,80),('description',0,500)]:
        text=value[key]
        if type(text) is not str or not low <= len(text) <= high or text != text.strip():
            raise ProfileError(f'{key}: expected trimmed text, {low}..{high} characters')
        if any(ord(c)<32 or ord(c)==127 or 0xD800<=ord(c)<=0xDFFF for c in text):
            raise ProfileError(f'{key}: unsupported control or surrogate character')
    s=value['style']
    _object(s,'color opacity outline_color outline_width rotation scale lines dot circle','style')
    for key in ('color','outline_color'):
        if type(s[key]) is not str or not re.fullmatch(r'#[0-9a-fA-F]{6}',s[key]):
            raise ProfileError(f'style.{key}: use #RRGGBB')
    for key,lo,hi in [('opacity',0,1),('outline_width',0,8),('rotation',-180,180),('scale',.25,8)]:
        _number(s[key],lo,hi,'style.'+key)
    for key,fields,bounds in [
        ('lines','enabled length thickness gap top',[('length',1,100),('thickness',.5,20),('gap',0,100)]),
        ('dot','enabled radius',[('radius',.5,20)]),
        ('circle','enabled radius thickness',[('radius',1,100),('thickness',.5,20)])]:
        part=s[key]; _object(part,fields,'style.'+key)
        for flag in ('enabled','top') if key=='lines' else ('enabled',):
            if type(part[flag]) is not bool: raise ProfileError(f'style.{key}.{flag}: expected boolean')
        for field,lo,hi in bounds: _number(part[field],lo,hi,f'style.{key}.{field}')
    if not any(s[k]['enabled'] for k in ('lines','dot','circle')):
        raise ProfileError('style: enable at least one component')
    return copy.deepcopy(value)

def _pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ProfileError('JSON contains duplicate object keys')
        result[key]=value
    return result

def _constant(_):
    raise ProfileError('NaN and Infinity are not JSON numbers')

def _encoded(text):
    try: data=text.encode('utf-8')
    except UnicodeEncodeError as exc: raise ProfileError('Invalid Unicode text') from exc
    if len(data)>MAX_BYTES: raise ProfileError('Preset exceeds 65,536 bytes')
    return data

def loads_profile(text: str) -> dict:
    if type(text) is not str: raise ProfileError('Expected JSON text')
    if text.startswith('\ufeff'): raise ProfileError('UTF-8 BOM is not supported')
    _encoded(text)
    try: value=json.loads(text,object_pairs_hook=_pairs,parse_constant=_constant)
    except ProfileError: raise
    except (ValueError,RecursionError) as exc: raise ProfileError('Malformed or excessively nested JSON') from exc
    return validate_profile(value)

def dumps_profile(value: object) -> str:
    text=json.dumps(validate_profile(value),indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n'
    _encoded(text)
    return text

def load_profile(path: str | Path) -> dict:
    with open(path,'rb') as handle: data=handle.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES: raise ProfileError('Preset exceeds 65,536 bytes')
    try: text=data.decode('utf-8')
    except UnicodeDecodeError as exc: raise ProfileError('Preset must be valid UTF-8') from exc
    return loads_profile(text)

def save_profile(path: str | Path, value: object) -> None:
    """Atomic replacement, not guaranteed power-loss durability of directory metadata.

    Validation occurs before disk writes; a same-directory temporary file is
    flushed and fsynced before replacement. Parent directories must exist.
    """
    data=dumps_profile(value).encode('utf-8')
    path=Path(path)
    fd,temp=tempfile.mkstemp(prefix='.projectscope-',dir=path.absolute().parent)
    try:
        try: handle=os.fdopen(fd,'wb')
        except Exception:
            os.close(fd)
            raise
        with handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp,path)
    finally:
        try: os.unlink(temp)
        except FileNotFoundError: pass
