"""Measured audio evidence, with explicit uncertainty and editable phrase cues."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from .beatgrid import rhythm
from .mixmap import analyze_mix_map

SR = 22050
HOP = 220
VERSION = 3
NOTES = ['C', 'C♯', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B']
MAJOR = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
MINOR = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
CAM_MAJOR = [8,3,10,5,12,7,2,9,4,11,6,1]
CAM_MINOR = [5,12,7,2,9,4,11,6,1,8,3,10]

def run(args):
    return subprocess.run(args, check=True, capture_output=True)

def decode(path, sr=SR):
    raw = run(['ffmpeg','-v','error','-i',str(path),'-t','900','-ac','1','-ar',str(sr),'-f','f32le','pipe:1']).stdout
    y = np.frombuffer(raw, dtype='<f4').copy()
    if len(y) < sr * 20 or not np.isfinite(y).all():
        raise ValueError('Use a valid, unprotected audio track at least 20 seconds long.')
    return y

def metadata(path):
    data = json.loads(run(['ffprobe','-v','error','-show_format','-of','json',str(path)]).stdout)['format']
    tags = {k.lower():v for k,v in data.get('tags',{}).items()}
    return {'title':tags.get('title',Path(path).stem),'artist':tags.get('artist','Unknown artist'),
            'genre':tags.get('genre',''), 'duration':float(data.get('duration',0))}

def tonal(y):
    import librosa
    # Analyze three tonal excerpts rather than letting drums or one breakdown dominate.
    length=min(20*SR,len(y)//4)
    sample=np.concatenate([y[int(len(y)*fraction):int(len(y)*fraction)+length] for fraction in (.2,.45,.7)])
    harmonic=librosa.effects.harmonic(sample)
    chroma=librosa.feature.chroma_cqt(y=harmonic,sr=SR,hop_length=1024)
    strengths=np.sum(chroma,axis=0)
    c=np.mean(chroma[:,strengths>np.percentile(strengths,35)],axis=1) if np.any(strengths) else np.zeros(12)
    scores=[]
    for mode,template in [('major',MAJOR),('minor',MINOR)]:
        for root in range(12):
            correlation=float(np.corrcoef(c,np.roll(template,root))[0,1]) if np.std(c)>1e-8 else 0
            scores.append((correlation,root,mode))
    scores.sort(reverse=True); best,root,mode=scores[0]
    margin=best-scores[1][0]
    reliable=best>.55 and margin>.035
    camelot=str((CAM_MAJOR if mode=='major' else CAM_MINOR)[root])+('B' if mode=='major' else 'A')
    return {'name':NOTES[root]+('m' if mode=='minor' else ''),'root':root,'mode':mode,'camelot':camelot,
            'score':round(best,3),'margin':round(margin,3),'confidence':'estimated' if reliable else 'uncertain',
            'chroma':np.round(c/max(float(np.max(c)),1e-9),3).tolist()}

def features(y, beats):
    filters=[signal.butter(3,[35,180],fs=SR,btype='band',output='sos'),
             signal.butter(3,[180,2500],fs=SR,btype='band',output='sos'),
             signal.butter(3,[2500,9000],fs=SR,btype='band',output='sos')]
    bands=[]
    for filt in filters:
        v=signal.sosfilt(filt,y)
        values=[float(np.sqrt(np.mean(v[int(t*SR):min(len(v),int((t+.15)*SR))]**2))) for t in beats]
        bands.append(np.array(values))
    return np.array(bands)

def analyze(path, track_id):
    info=metadata(path)
    if info['duration']>900: raise ValueError('The prototype supports individual tracks up to 15 minutes.')
    y=decode(path); bpm,phase,beats,confidence,kicks,env=rhythm(y)
    bands=features(y,beats)
    # Infer bar phase from sustained arrangement novelty; equally strong kicks remain ambiguous.
    novelty=np.sum(np.maximum(0,np.diff(bands,axis=1)),axis=0)
    phase_scores=[float(np.sum(novelty[p::4])) for p in range(4)]
    bar_phase=int(np.argmax(phase_scores))
    downbeat=float(beats[min(bar_phase+1,len(beats)-1)])
    # Include earlier inferred downbeats where they are still within the decoded audio.
    bar=240/bpm
    while downbeat>=bar: downbeat-=bar
    count=max(0,int((len(y)/SR-downbeat)/bar))
    bar_rows=[]
    for b in range(count):
        t=downbeat+b*bar; indices=(beats>=t)&(beats<t+bar)
        bar_rows.append(np.mean(bands[:,indices],axis=1) if np.any(indices) else np.zeros(3))
    rows=np.array(bar_rows)
    scaled=rows/np.maximum(np.percentile(rows,90,axis=0),1e-8) if len(rows) else rows
    activity=np.mean(scaled,axis=1)
    # Among common phrase boundaries, choose the largest change from the intro/tail texture.
    options=[n for n in (4,8,16,32) if count>n*2]
    def boundary_score(n, reverse=False):
        r=scaled[::-1] if reverse else scaled
        return float(np.linalg.norm(np.mean(r[n:n+4],axis=0)-np.mean(r[max(0,n-4):n],axis=0)))
    intro=max(options,key=boundary_score) if options else 4
    outro=max(options,key=lambda n:boundary_score(n,True)) if options else 4
    usable_end=downbeat+count*bar
    # These are proposed phrase lengths, not ground-truth arrangement labels.
    first_active=float(np.flatnonzero(np.abs(y)>.01)[0]/SR) if np.any(np.abs(y)>.01) else 0
    fade=bool(np.sqrt(np.mean(y[:SR*4]**2)) < .18*np.sqrt(np.mean(y[SR*8:SR*16]**2)))
    waveform=[]
    for chunk in np.array_split(y,1200): waveform.append(float(np.max(np.abs(chunk))))
    key=tonal(y[::1])
    grid_ok=confidence>.62 and count>=24
    result = {**info,'id':track_id,'version':VERSION,'duration':round(len(y)/SR,3),'bpm':round(bpm,3),
            'gridOffset':round(downbeat,4),'beatConfidence':round(confidence,3),'meter':'4/4 assumed',
            'barConfidence':'needs audition','introBars':intro,'outroBars':outro,
            'entry':round(downbeat,4),'exitEnd':round(usable_end,4),
            'introEnd':round(downbeat+intro*bar,4),'outroStart':round(usable_end-outro*bar,4),
            'fadeIn':fade,'firstActive':round(first_active,3),'key':key,
            'energy':round(float(np.mean(activity)),3),'waveform':np.round(waveform,3).tolist(),
            'bands':np.round(scaled,3).tolist(),'kickTimes':np.round(kicks,3).tolist(),
            'ready':grid_ok and not fade and min(intro,outro)>=8,
            'reviewed':False,'warnings':(["Check beat one and phrase markers"]+(['Faded or quiet intro'] if fade else [])+(['Unstable house grid'] if not grid_ok else []))}

    result['mixMap']=analyze_mix_map(y,SR,bpm,downbeat,result)
    result['warnings']+=result['mixMap']['warnings'][-1:] if result['mixMap']['introMaxKicklessBeats']>=4 else []
    result['ready']=result['ready'] and bool(result['mixMap']['entryCandidates']) and bool(result['mixMap']['exitCandidates'])
    return result

def content_id(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()[:20]

def prepare(source, target, ratio):
    if not .92<=ratio<=1.08: raise ValueError('Tempo change exceeds the prototype’s ±8% limit.')
    run(['ffmpeg','-v','error','-y','-i',str(source),'-af',f'atempo={ratio:.9f}',
         '-ar','44100','-ac','2','-c:a','pcm_s16le',str(target)])
