import json
import pytest
from fastapi import HTTPException
from b2b.listener import create_app, listener_config, SongRequest

def setup(tmp_path):
    calls=[]
    def proxy(path,body=None):
        calls.append((path,body))
        if path=='/api/session/state':result={'decks':[{'id':'abc','title':'Track','playing':True,'path':'/secret.mp3','mixMap':{'secret':'data'}}],'crate':[],'broadcasting':True,'tempo':124,'tailId':'secret'}
        elif path=='/api/requests':result={'id':'r','title':'Song','status':'pending','context':'private','url':'private'} if body else {'requests':[{'id':'r','status':'accepted','context':'private','url':'private'}]}
        elif path=='/api/art/abc':return b'PNG','image/png'
        else:raise AssertionError(path)
        return json.dumps(result).encode(),'application/json'
    app=create_app(tmp_path,proxy)
    def route(path,method='GET'):return next(r.endpoint for r in app.routes if r.path==path and method in r.methods)
    return route,listener_config(tmp_path)['token'],calls

def test_surface_whitelist(tmp_path):
    route,key,calls=setup(tmp_path)
    asset=route('/{asset:path}')
    for u in ['api/crate','api/upload','app.js','.b2b/crate.json','docs']:
        with pytest.raises(HTTPException):asset(u)
    with pytest.raises(HTTPException):route('/s/{key}/api/state')('wrong')
    assert route('/s/{key}/')(key).status_code==200
    assert asset('booth-scene.js').status_code==200 and not calls

def test_sanitized_proxies(tmp_path):
    route,key,calls=setup(tmp_path);state=route('/s/{key}/api/state')(key)
    assert state['decks'][0]['title']=='Track' and 'secret' not in str(state)
    assert state['decks'][0]['artworkUrl']==f'/s/{key}/api/art/abc'
    assert 'private' not in str(route('/s/{key}/api/requests')(key))
    result=route('/s/{key}/api/requests','POST')(key,SongRequest(url='https://youtu.be/abcdefghijk',name='Tester'))
    assert 'private' not in str(result)
    assert calls[-1][1]=={'url':'https://youtu.be/abcdefghijk','name':'Tester'}

def test_token_media(tmp_path):
    route,key,_=setup(tmp_path);live=tmp_path/'live';live.mkdir();(live/'index.m3u8').write_text('#EXTM3U\nseg001.ts\n');(live/'seg001.ts').write_bytes(b'audio')
    handler=route('/s/{key}/live/{filename}')
    assert handler(key,'index.m3u8').media_type=='application/vnd.apple.mpegurl'
    with pytest.raises(HTTPException):handler('wrong','seg001.ts')
    with pytest.raises(HTTPException):handler(key,'listener.json')
    with pytest.raises(HTTPException):handler(key,'../listener.json')
    assert route('/s/{key}/api/art/{ident}')(key,'abc').media_type=='image/png'


def test_scene_module_dependencies_are_served(tmp_path):
    import posixpath
    import re
    from b2b.listener import WEB
    route,_,_=setup(tmp_path)
    asset=route('/{asset:path}')
    pending=['booth-scene.js'];seen=set()
    while pending:
        name=pending.pop()
        if name in seen:continue
        seen.add(name)
        assert asset(name).status_code==200
        source=(WEB/name).read_text()
        for dependency in re.findall(r"from\s+['\"]([^'\"]+)['\"]",source):
            if dependency.startswith('.'):
                pending.append(posixpath.normpath(posixpath.join(posixpath.dirname(name),dependency.split('?')[0])))
    assert 'human-rig.js' in seen
