"""Local-only DJ workstation. Personal audio is never served outside its crate."""
import asyncio
import json
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .audio import analyze, content_id, prepare, decode, SR
from .beatgrid import local_attack_offset
from .mixmap import analyze_mix_map
from .planner import make_plan, edge
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
    return {k:t[k] for k in ('id','title','artist','version','bpm','gridOffset','beatConfidence','meter','barConfidence','entry','introEnd','introBars','outroStart','exitEnd','outroBars','drumsIn','musicIn','reviewed','mixMap','warnings') if k in t}

@app.get('/api/map/{tid}')
def get_map(tid:str):
    with lock:t=tracks.get(tid)
    if not t:raise HTTPException(404,'Track not found')
    return JSONResponse(song_map(t),headers={'Content-Disposition':f'attachment; filename="{tid}-mix-map.json"'})

def public(t):return {k:v for k,v in t.items() if k!='path'}

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

@app.put('/api/track/{tid}')
def correct(tid:str,c:Correction):
    with lock:
        if tid not in tracks:raise HTTPException(404,'Track not found')
        t=tracks[tid];v=c.model_dump();bar=240/c.bpm
        if c.entry+c.introBars*bar>=c.exitEnd-c.outroBars*bar or c.exitEnd>t['duration'] or any(v is not None and v>=t['duration'] for v in (c.drumsIn,c.musicIn)):
            raise HTTPException(400,'Intro and outro must fit inside the track without overlapping.')
        t.update(v);t.update(introEnd=c.entry+c.introBars*bar,outroStart=c.exitEnd-c.outroBars*bar,
                            ready=min(c.introBars,c.outroBars)>=8,barConfidence='manually confirmed',warnings=[])
        t['mixMap']=analyze_mix_map(decode(t['path']),SR,t['bpm'],t['gridOffset'],t)
        t['ready']=t['ready'] and bool(t['mixMap']['entryCandidates']) and bool(t['mixMap']['exitCandidates'])
        save();return public(t)

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

render_lock=threading.Lock()
app.mount('/',StaticFiles(directory=ROOT/'web',html=True),name='web')
