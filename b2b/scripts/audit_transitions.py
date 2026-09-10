"""Read-only audit of the current local crate; JSON output excludes source paths.

Run from b2b/: ../.venv/bin/python scripts/audit_transitions.py > .b2b/transition-audit.json
Uses real decoded audio and FFmpeg measurements. Does not render or play a mix.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b2b.audio import decode, SR
from b2b.beatgrid import local_attack_offset
from b2b.diagnostics import loudness
from b2b.planner import make_plan


def section_lufs(path,start,duration):
    cmd=['ffmpeg','-hide_banner','-nostats','-ss',str(max(0,start)),'-i',str(path),
         '-t',str(duration),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-']
    result=subprocess.run(cmd,capture_output=True,text=True,check=True)
    values=json.loads(re.search(r'\{\s*"input_i".*?\}',result.stderr,re.S)[0])
    return float(values['input_i'])


def audit():
    tracks=json.loads((ROOT/'.b2b/crate.json').read_text())
    plan=make_plan(list(tracks.values()),124,16)
    levels={tid:loudness(tracks[tid]['path']) for tid in plan['order']}
    rows=[];prepared={}
    for index,e in enumerate(plan['transitions']):
        a,b=tracks[e['from']],tracks[e['to']]
        ar,br=124/a['bpm'],124/b['bpm']
        aend=e['exit']+e['bars']*240/a['bpm']
        bend=e['entry']+e['bars']*240/b['bpm']
        row={'from':a['title'],'to':b['title'],'bars':e['bars'],
             'exitSeconds':e['exit'],'entrySeconds':e['entry'],
             'incomingSourceAtHandoff':round(bend,3),
             'outgoingSkippedTailSeconds':round(a['duration']-aend,3),
             'incomingSkippedOpeningSeconds':round(e['entry'],3),
             'incomingHandoffUntilNextExitSeconds':None,
             'outgoingPhraseConfirmed':e['phraseAnchorSource']=='human'}
        if index+1<len(plan['transitions']):
            row['incomingHandoffUntilNextExitSeconds']=round((plan['transitions'][index+1]['exit']-bend)/br,3)
        sections={}
        for label,t,start,duration in [('outgoingPre',a,e['exit']-2*240/a['bpm'],2*240/a['bpm']),
                  ('outgoingOverlap',a,e['exit'],e['bars']*240/a['bpm']),
                  ('incomingOverlap',b,e['entry'],e['bars']*240/b['bpm']),
                  ('incomingLanding',b,bend,2*240/b['bpm']),
                  ('incomingNextEightBars',b,bend,8*240/b['bpm'])]:
            raw=section_lufs(t['path'],start,duration)
            sections[label]={'lufs':raw,'afterWholeTrackTrimLufs':round(raw+levels[t['id']]['gainDb'],2)}
        row['sections']=sections
        row['normalizedLandingDeltaLufs']=round(sections['incomingLanding']['afterWholeTrackTrimLufs']-sections['outgoingPre']['afterWholeTrackTrimLufs'],2)
        landing=[x for x in b.get('mixMap',{}).get('bars',[]) if bend-.001<=x['start']<bend+8*240/b['bpm']-.001]
        row['incomingNextEightBarsKickCoverage']=[x['kickFraction'] for x in landing]
        row['timing']={}
        for label,t,cue,ratio in [('outgoing',a,e['exit'],ar),('incoming',b,e['entry'],br)]:
            cache=ROOT/'.b2b/cache'/f"{t['id']}-{t['bpm']:.3f}-124.000.wav"
            if cache.exists():
                if t['id'] not in prepared:prepared[t['id']]=decode(cache)
                row['timing'][label]=local_attack_offset(prepared[t['id']],SR,124,t['gridOffset']/ratio,
                                                       cue/ratio,cue/ratio+e['duration'])
            else:row['timing'][label]={'available':False}
        rows.append(row)
    return {'tempo':124,'requestedBars':16,'order':[tracks[i]['title'] for i in plan['order']],
            'trackLevels':{tracks[i]['title']:levels[i] for i in plan['order']},'transitions':rows,
            'limitations':['Source-section LUFS with whole-track trim, not a rendered master mix.',
                           'Kick support and attack timing are heuristics; phrase origins remain estimated.']}


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
