"""Local-only DJ workstation. Personal audio is never served outside its crate."""
import asyncio
import json
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .audio import analyze, content_id, prepare, decode, SR
from .beatgrid import local_attack_offset
from .mixmap import analyze_mix_map
from .planner import make_plan, edge, validate_sequence
from .youtube import download_audio, video_url

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'.b2b'; IMPORTS=DATA/'imports'; CACHE=DATA/'cache'; MAPS=DATA/'maps'
for p in (IMPORTS,CACHE,MAPS):p.mkdir(parents=True,exist_ok=True)
MANIFEST=DATA/'crate.json'
lock=threading.RLock(); workers=ThreadPoolExecutor(max_workers=1)
tracks=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
jobs={}
app=FastAPI(title='Back 2 Back')

@app.middleware('http')
async def local_only(request:Request,call_next):
    host=request.headers.get('host','').split(':')[0]
    origin=request.headers.get('origin')
    if host not in ('localhost','127.0.0.1','testserver') or (origin and origin != str(request.base_url).rstrip('/')):
        return JSONResponse({'detail':'This workstation accepts local requests only.'},status_code=403)
    return await call_next(request)

def save():
    with lock:
        tmp=MANIFEST.with_suffix('.tmp');tmp.write_text(json.dumps(tracks));tmp.replace(MANIFEST)
        for tid,t in tracks.items():
            target=MAPS/(tid+'.json');temp=target.with_suffix('.tmp')
            temp.write_text(json.dumps(song_map(t),indent=2));temp.replace(target)

def song_map(t):
    return {k:t[k] for k in ('id','title','artist','version','bpm','gridOffset','beatConfidence','meter','barConfidence','entry','introEnd','introBars','outroStart','exitEnd','outroBars','drumsIn','musicIn','phraseAnchor','reviewed','mixMap','warnings') if k in t}

@app.get('/api/map/{tid}')
def get_map(tid:str):
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    return JSONResponse(song_map(t),headers={'Content-Disposition':f'attachment; filename="{tid}-mix-map.json"'})

def public(t):return {**{k:v for k,v in t.items() if k!='path'},'artworkUrl':'/api/art/'+t['id']}

def import_track(path,job):
    try:
        tid=content_id(path)
        if tid not in tracks:
            result=analyze(path,tid)
            with lock:tracks[tid]={**result,'path':str(path.resolve())};save()
        jobs[job]={'status':'done','title':tracks[tid]['title'],'track':tid}
    except Exception as e:
        jobs[job]={'status':'error','title':path.stem,'error':str(e)[:240]}

def queue(path):
    job=uuid.uuid4().hex;jobs[job]={'status':'analyzing','title':path.stem};workers.submit(import_track,path,job);return job

def import_youtube(url,job):
    path=None
    def update(**state):
        with lock:jobs[job]=state
    try:
        path=download_audio(url,IMPORTS,update)
        update(status='analyzing',title=path.stem)
        import_track(path,job)
        if jobs[job]['status']=='error':path.unlink(missing_ok=True)
    except Exception as error:
        if path:path.unlink(missing_ok=True)
        update(status='error',title='YouTube import',error=str(error)[:240])

class YoutubeRequest(BaseModel):
    url:str=Field(min_length=1,max_length=2048)

@app.post('/api/youtube')
def youtube(req:YoutubeRequest):
    try:url=video_url(req.url)
    except ValueError as error:raise HTTPException(400,str(error)) from error
    with lock:
        if sum(j['status'] in ('queued','downloading','analyzing') for j in jobs.values())>=30:
            raise HTTPException(429,'Wait for current imports to finish before adding more.')
        job=uuid.uuid4().hex;jobs[job]={'status':'queued','title':'YouTube audio'}
    workers.submit(import_youtube,url,job)
    return {'job':job}

@app.get('/api/crate')
def crate():
    with lock:return {'tracks':[public(t) for t in tracks.values()],'jobs':dict(jobs),'astra':bool(os.getenv('OPENAI_API_KEY'))}

@app.post('/api/scan')
def scan():
    known={t['path'] for t in tracks.values()}
    pending={j['title'] for j in jobs.values() if j['status']=='analyzing'}
    paths=[p for p in IMPORTS.iterdir() if p.suffix.lower() in ('.mp3','.wav','.m4a','.flac') and str(p.resolve()) not in known and p.stem not in pending]
    return {'jobs':[queue(p) for p in paths]}

@app.post('/api/upload')
async def upload(file:UploadFile):
    suffix=Path(file.filename or '').suffix.lower()
    if suffix not in ('.mp3','.wav','.m4a','.flac'):raise HTTPException(400,'Choose MP3, WAV, M4A or FLAC.')
    path=IMPORTS/(uuid.uuid4().hex+suffix);size=0
    try:
        with path.open('wb') as out:
            while chunk:=await file.read(1024*1024):
                size+=len(chunk)
                if size>150*1024*1024:raise HTTPException(413,'Limit: 150 MB per track.')
                out.write(chunk)
    except Exception:
        path.unlink(missing_ok=True);raise
    return {'job':queue(path)}

class Correction(BaseModel):
    bpm:float=Field(ge=108,le=142)
    gridOffset:float=Field(ge=0,le=30)
    entry:float=Field(ge=0)
    introBars:int=Field(ge=4,le=64)
    exitEnd:float=Field(gt=0)
    outroBars:int=Field(ge=4,le=64)
    reviewed:bool=True
    drumsIn:float|None=Field(default=None,ge=0)
    musicIn:float|None=Field(default=None,ge=0)
    phraseAnchor:float|None=Field(default=None,ge=0)

@app.put('/api/track/{tid}')
def correct(tid:str,c:Correction):
    with lock:
        if tid not in tracks:raise HTTPException(404,'Track not found')
        t=tracks[tid];v=c.model_dump();bar=240/c.bpm
        if c.entry+c.introBars*bar>=c.exitEnd-c.outroBars*bar or c.exitEnd>t['duration'] or any(v is not None and v>=t['duration'] for v in (c.drumsIn,c.musicIn)):
            raise HTTPException(400,'Intro and outro must fit inside the track without overlapping.')
        if c.phraseAnchor is not None:
            snapped=c.gridOffset+round((c.phraseAnchor-c.gridOffset)/bar)*bar
            if not 0<=snapped<t['duration'] or abs(snapped-c.phraseAnchor)>.03:
                raise HTTPException(400,'Phrase anchor must be on a bar boundary. Use the beat inspector to find it.')
            v['phraseAnchor']=snapped
        updated={**t,**v,'introEnd':c.entry+c.introBars*bar,'outroStart':c.exitEnd-c.outroBars*bar,
                 'ready':min(c.introBars,c.outroBars)>=8,'barConfidence':'manually confirmed','warnings':[]}
        try:updated['mixMap']=analyze_mix_map(decode(t['path']),SR,updated['bpm'],updated['gridOffset'],updated)
        except Exception as error:raise HTTPException(422,'Could not rebuild the phrase map. Your previous markers are unchanged; try again.') from error
        updated['ready']=updated['ready'] and bool(updated['mixMap']['entryCandidates']) and bool(updated['mixMap']['exitCandidates'])
        tracks[tid]=updated
        try:save()
        except Exception as error:
            tracks[tid]=t
            raise HTTPException(500,'Could not save markers. Please try again.') from error
        return public(updated)

class PlanRequest(BaseModel):
    ids:list[str]=Field(min_length=1,max_length=30)
    tempo:float=Field(default=128,ge=108,le=142)
    bars:int=Field(default=16,ge=8,le=16)
    direction:str=Field(default='',max_length=1000)
    astra:bool=False
    fixed:bool=False

@app.post('/api/plan')
def plan(req:PlanRequest):
    try:
        if len(set(req.ids))!=len(req.ids) or req.bars not in (8,16):raise ValueError('Choose unique tracks and an 8- or 16-bar blend.')
        with lock:selection=[dict(tracks[i]) for i in req.ids]
        if req.fixed:
            excluded=[t['id'] for t in selection if not t['ready'] or abs(req.tempo/t['bpm']-1)>.04]
            selection=[t for t in selection if t['id'] not in excluded]
            if not selection:raise ValueError('No tracks in this order are ready at the selected tempo.')
            transitions=[edge(a,b,req.tempo,req.bars) for a,b in zip(selection,selection[1:])]
            if any(e is None for e in transitions):raise ValueError('This order has an incompatible pair. Review cues or use Suggest order.')
            validate_sequence(transitions,selection,req.tempo)
            return {'order':[t['id'] for t in selection],'transitions':transitions,'tempo':req.tempo,'mode':'Manual','reason':'Your order, with validated phrase windows.','excluded':excluded}
        return make_plan(selection,req.tempo,req.bars,req.direction,req.astra)
    except (ValueError,KeyError) as e:raise HTTPException(400,str(e)) from e
    except Exception as e:raise HTTPException(502,'Astra is unavailable. Your current playback is unchanged.') from e

@app.get('/api/audio/{tid}')
def audio(tid:str,tempo:float=128):
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    ratio=tempo/t['bpm']
    if not .92<=ratio<=1.08:raise HTTPException(400,'Choose a set tempo within 8% of this track.')
    filename=f'{tid}-{t["bpm"]:.3f}-{tempo:.3f}.wav';target=CACHE/filename
    # Serialize preparation independently of the lightweight HTTP/control routes.
    with render_lock:
        if not target.exists():
            temp=target.with_name(target.stem+'.partial.wav')
            try:prepare(t['path'],temp,ratio);temp.replace(target)
            except Exception as e:
                temp.unlink(missing_ok=True);raise HTTPException(422,'Audio preparation failed. The file may be protected or damaged.') from e
    return FileResponse(target,media_type='audio/wav')

alignment_cache={}

@app.get('/api/alignment/{tid}')
def alignment(tid:str,tempo:float=128,cue:float=0,bars:int=8):
    import math
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    if not math.isfinite(cue) or not 0<=cue<t['duration'] or bars not in (8,16):
        raise HTTPException(400,'Choose a cue inside the file and an 8- or 16-bar window.')
    if not math.isfinite(tempo) or not .92<=tempo/t['bpm']<=1.08:
        raise HTTPException(400,'Choose a set tempo within 8% of this track.')
    key=(tid,t.get('version'),t['bpm'],t['gridOffset'],tempo,round(cue,4),bars)
    if key not in alignment_cache:
        prepared=audio(tid,tempo);ratio=tempo/t['bpm'];y=decode(prepared.path)
        result=local_attack_offset(y,SR,tempo,t['gridOffset']/ratio,cue/ratio,cue/ratio+bars*240/tempo)
        alignment_cache[key]={**result,'mappedCue':cue/ratio+result['offset'],'sourceCue':cue,'tempo':tempo}
    return alignment_cache[key]

DIAGNOSTICS=DATA/'diagnostics';DIAGNOSTICS.mkdir(exist_ok=True)
level_cache={}

@app.get('/api/level/{tid}')
def track_level(tid:str):
    from .diagnostics import loudness
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    if tid not in level_cache:level_cache[tid]=loudness(t['path'])
    return level_cache[tid]

@app.post('/api/capture')
async def capture(file:UploadFile,metadata:str=Form('{}')):
    from .diagnostics import inspect_capture
    try:details=json.loads(metadata)
    except ValueError:raise HTTPException(400,'Invalid recording metadata.')
    if not isinstance(details,dict):raise HTTPException(400,'Expected recording metadata.')
    suffix=Path(file.filename or '').suffix.lower()
    if suffix not in ('.webm','.mp4','.ogg','.wav'):raise HTTPException(400,'Unsupported recording format.')
    path=DIAGNOSTICS/(uuid.uuid4().hex+suffix);size=0
    try:
        with path.open('wb') as out:
            while chunk:=await file.read(1024*1024):
                size+=len(chunk)
                if size>50*1024*1024:raise HTTPException(413,'Recording limit: 50 MB.')
                out.write(chunk)
        return await asyncio.to_thread(inspect_capture,path,details)
    except Exception:
        path.unlink(missing_ok=True);raise

@app.get('/api/captures')
def captures():
    return [json.loads(p.read_text()) for p in sorted(DIAGNOSTICS.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:10]]

@app.get('/api/diagnostic/{filename}')
def diagnostic_file(filename:str):
    if Path(filename).name!=filename or Path(filename).suffix not in ('.png','.wav','.json'):raise HTTPException(404)
    path=DIAGNOSTICS/filename
    if not path.is_file():raise HTTPException(404)
    return FileResponse(path)

# Listener projection is served on a separate port; these remain local-only APIs.
from .requests import RequestManager
from pydantic import ConfigDict
import copy
import time

session_state={'decks':[],'crate':[],'transition':None,'tempo':124,'bars':16,
               'tailId':'','crateIds':[],'broadcasting':False,'updatedAt':0}

def listener_tracks():
    with lock:return copy.deepcopy(list(tracks.values()))

def listener_import(url,update):
    path=download_audio(url,IMPORTS,update)
    try:
        update(status='analyzing',title=path.stem)
        ident=content_id(path)
        with lock:existing=tracks.get(ident)
        if existing:
            if str(path.resolve())!=existing['path']:path.unlink(missing_ok=True)
            return copy.deepcopy(existing)
        result=analyze(path,ident)
        with lock:
            tracks[ident]={**result,'path':str(path.resolve()),'sourceUrl':url};save()
            return copy.deepcopy(tracks[ident])
    except Exception:
        path.unlink(missing_ok=True);raise

request_manager=RequestManager(DATA,listener_tracks,listener_import)

class ListenerDeck(BaseModel):
    id:str=Field(default='',max_length=100)
    playing:bool=False
    position:float=Field(default=0,ge=0,le=36000,allow_inf_nan=False)
    level:float=Field(default=1,ge=0,le=2,allow_inf_nan=False)
    low:float=Field(default=0,ge=-24,le=12,allow_inf_nan=False)
    fade:float=Field(default=0,ge=0,le=1,allow_inf_nan=False)

class ListenerTransition(BaseModel):
    model_config=ConfigDict(populate_by_name=True)
    progress:float=Field(default=0,ge=0,le=1,allow_inf_nan=False)
    from_id:str=Field(default='',alias='from',max_length=100)
    to:str=Field(default='',max_length=100)
    bars:int=Field(default=16,ge=8,le=16)

class SessionProjection(BaseModel):
    decks:list[ListenerDeck]=Field(default_factory=list,max_length=2)
    crate:list[dict]=Field(default_factory=list,max_length=30)
    transition:ListenerTransition|None=None
    tempo:float=Field(default=124,ge=108,le=142,allow_inf_nan=False)
    bars:int=Field(default=16,ge=8,le=16)
    tailId:str=Field(default='',max_length=100)
    crateIds:list[str]=Field(default_factory=list,max_length=30)
    broadcasting:bool=False

@app.post('/api/session/state')
def publish_session(body:SessionProjection):
    if body.bars not in (8,16):raise HTTPException(400,'Choose an 8- or 16-bar blend.')
    def safe_track(tid):
        t=tracks.get(tid)
        return ({k:t[k] for k in ('id','title','artist','bpm','duration') if k in t}
                | {'artworkUrl':'/api/art/'+tid}) if t else {}
    with lock:
        decks=[{**safe_track(d.id),**d.model_dump()} for d in body.decks]
        crate=[safe_track(str(t.get('id',''))) for t in body.crate]
        session_state.update(decks=decks,crate=[t for t in crate if t],
                             transition=body.transition.model_dump(by_alias=True) if body.transition else None,
                             tempo=body.tempo,bars=body.bars,tailId=body.tailId if body.tailId in tracks else '',
                             crateIds=[t for t in body.crateIds if t in tracks],broadcasting=body.broadcasting,updatedAt=time.time())
    return {'ok':True}

@app.get('/api/session/state')
def get_session():
    with lock:
        result=copy.deepcopy(session_state)
        if time.time()-result['updatedAt']>10:
            result['broadcasting']=False
            for deck in result['decks']:deck['playing']=False
        return result

class ListenerSubmission(BaseModel):
    url:str=Field(min_length=1,max_length=2048)
    name:str=Field(default='Listener',max_length=80)

@app.post('/api/requests')
def listener_submit(body:ListenerSubmission):
    with lock:context={k:copy.deepcopy(session_state[k]) for k in ('tempo','bars','tailId','crateIds')}
    try:return request_manager.submit(body.url,body.name,context)
    except ValueError as error:raise HTTPException(400,str(error)) from error

@app.get('/api/requests')
def listener_requests():
    return {'requests':request_manager.list(),'queue':request_manager.queue_ids()}

class ConsumeRequest(BaseModel):
    trackId:str=Field(min_length=1,max_length=100)

@app.post('/api/requests/consume')
def consume_request(body:ConsumeRequest):
    request_manager.consume(body.trackId)
    return {'ok':True}


class ResolveRequest(BaseModel):
    trackId:str=Field(min_length=1,max_length=100)
    approve:bool=False

def request_context():
    with lock:return {k:copy.deepcopy(session_state[k]) for k in ('tempo','bars','tailId','crateIds')}

@app.post('/api/requests/{ident}/resolve')
def resolve_request(ident:str,body:ResolveRequest):
    try:return request_manager.resolve(ident,body.trackId,request_context(),body.approve)
    except ValueError as error:raise HTTPException(400,str(error)) from error

@app.post('/api/requests/{ident}/retry')
def retry_request(ident:str):
    try:return request_manager.retry(ident,request_context())
    except ValueError as error:raise HTTPException(400,str(error)) from error

@app.post('/api/requests/{ident}/dismiss')
def dismiss_request(ident:str):
    try:return request_manager.dismiss(ident)
    except ValueError as error:raise HTTPException(400,str(error)) from error


from .broadcast import Broadcast
broadcast=Broadcast(DATA/'live')

@app.get('/api/listener-info')
def listener_info():
    from .listener import listener_config
    return {'url':'http://127.0.0.1:8780/s/'+listener_config(DATA)['token']+'/','public':False}

@app.post('/api/broadcast/start')
def broadcast_start():return {'session':broadcast.start()}

@app.post('/api/broadcast/stop')
def broadcast_stop(session:str):return {'stopped':broadcast.stop(session)}

@app.post('/api/broadcast/chunk')
async def broadcast_chunk(request:Request,session:str):
    body=bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body)>2*1024*1024:raise HTTPException(413,'Audio chunk too large.')
    try:await asyncio.to_thread(broadcast.write,session,body)
    except ValueError as error:raise HTTPException(409,str(error)) from error
    return {'ok':True}

@app.get('/api/art-info/{tid}')
def artwork_info(tid:str):
    if tid not in tracks:raise HTTPException(404,'Track not found')
    path=CACHE/(tid+'-art.json')
    return json.loads(path.read_text()) if path.exists() else {'method':'generated placeholder','source':'b2b'}

@app.get('/api/art/{tid}')
def artwork(tid:str):
    import subprocess
    import html
    from fastapi.responses import Response
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    from .artwork import locate_artwork
    with render_lock:target=locate_artwork(t,CACHE)
    if target:return FileResponse(target,media_type='image/jpeg')
    hue=int(tid[:6],16)%360;title=html.escape(t['title'][:32])
    return Response(f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><rect width="512" height="512" fill="hsl({hue},30%,55%)"/><circle cx="256" cy="230" r="165" fill="#202127"/><circle cx="256" cy="230" r="55" fill="#ded5cf"/><text x="24" y="473" font-family="sans-serif" font-size="20" fill="#fff">{title}</text></svg>',media_type='image/svg+xml')

render_lock=threading.Lock()
app.mount('/',StaticFiles(directory=ROOT/'web',html=True),name='web')
