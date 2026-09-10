"""Constrained ordering: executable edges first, optional Astra selection second."""
from .astra import decide, song_evidence
import math
from .mixmap import on_phrase_grid


def validate_sequence(transitions, tracks, tempo, min_prepare_seconds=8):
    """Check connected transitions and time to reuse the freed deck.

    The preparation allowance is a scheduling policy, not a latency guarantee.
    Source cue seconds become prepared seconds at tempo / source BPM. Runtime
    preparation and scheduling still need their own readiness checks.
    """
    if not math.isfinite(tempo) or tempo <= 0 or not math.isfinite(min_prepare_seconds) or min_prepare_seconds < 0:
        raise ValueError('Sequence tempo and preparation allowance must be finite and valid.')
    by_id=tracks if isinstance(tracks,dict) else {track['id']:track for track in tracks}
    for transition in transitions:
        if any(key not in transition for key in ('from','to','entry','exit','duration')):
            raise ValueError('A transition is missing its tracks or timing.')
        if transition['from'] not in by_id or transition['to'] not in by_id or transition['from']==transition['to']:
            raise ValueError('A transition references an unknown or repeated track.')
        if any(not isinstance(transition[key],(int,float)) or not math.isfinite(transition[key]) or transition[key]<0
               for key in ('entry','exit','duration')) or transition['duration']==0:
            raise ValueError('Transition cues and duration must be finite and valid.')
    for incoming,outgoing in zip(transitions,transitions[1:]):
        if incoming['to']!=outgoing['from']:
            raise ValueError('Adjacent transitions must share the same middle track.')
        middle=by_id[incoming['to']]
        bpm=middle.get('bpm')
        if not isinstance(bpm,(int,float)) or not math.isfinite(bpm) or bpm<=0:
            raise ValueError('The middle track needs a valid tempo.')
        ratio=tempo/bpm
        handoff=incoming['entry']/ratio+incoming['duration']
        remaining=outgoing['exit']/ratio-handoff
        if remaining+.001<min_prepare_seconds:
            name=middle.get('title',middle['id'])
            raise ValueError(f'{name} leaves {remaining:.1f} seconds after its handoff; '
                             f'at least {min_prepare_seconds:g} seconds are required to prepare the next deck.')


def edge(a,b,tempo,bars):
    if not (a['ready'] and b['ready']): return None
    if max(abs(tempo/a['bpm']-1),abs(tempo/b['bpm']-1))>.04: return None
    phrase_anchor=a.get('phraseAnchor')
    if phrase_anchor is None:phrase_anchor=a.get('gridOffset',0.)
    mapped=a.get('mixMap') is not None and b.get('mixMap') is not None
    if mapped:
        pair=None
        for n in ([16,8] if bars==16 else [8]):
            exits=[w for w in a['mixMap']['exitCandidates'] if w['bars']==n and w['start']>=a['introEnd']
                   and w['end']>=a['exitEnd']-16*240/a['bpm']-.001
                   and on_phrase_grid(w['start'],phrase_anchor,a['bpm'],n)]
            entries=[w for w in b['mixMap']['entryCandidates'] if w['bars']==n and w['end']<b['exitEnd']]
            if a.get('reviewed'):exits=[w for w in exits if w['start']>=a['outroStart']-.001 and w['end']<=a['exitEnd']+.001]
            if b.get('reviewed'):entries=[w for w in entries if w['start']>=b['entry']-.001 and w['end']<=b['introEnd']+.001]
            arrival=b['mixMap'].get('musicalArrival')
            if arrival:entries=[w for w in entries if w['end']>=arrival['time']-.001]
            # Inspect what remains after A stops, not only drums within the overlap.
            def supported_landing(window):
                rows=b['mixMap'].get('bars')
                if not rows:return True  # Older maps lack this evidence.
                landing=[row for row in rows if window['end']-.001<=row['start']<window['end']+2*240/b['bpm']-.001]
                return len(landing)>=2 and all(row['kickFraction']>=.75 for row in landing)
            entries=[w for w in entries if supported_landing(w)]
            if exits and entries:
                outgoing=max(exits,key=lambda w:w['end']);incoming=min(entries,key=lambda w:abs(w['end']-arrival['time']) if arrival else w['start'])
                pair=(n,outgoing,incoming);break
        if pair is None:return None
        n,outgoing,incoming=pair;start=outgoing['start'];entry=incoming['start']
    else:
        n=16 if bars==16 and min(a['outroBars'],b['introBars'])>=16 else 8
        if min(a['outroBars'],b['introBars'])<n:return None
        span=n*240/a['bpm'];latest=a['exitEnd']-span
        start=phrase_anchor+math.floor((latest-phrase_anchor+.001)/span)*span
        entry=b['introEnd']-n*240/b['bpm']
        if start<a['introEnd'] or entry<0 or b['introEnd']>=b['exitEnd']:return None
        if a.get('reviewed') and start<a.get('outroStart',start)-.001:return None
    ka,kb=a['key'],b['key']; distance=(kb['root']-ka['root'])%12
    harmonic=0 if distance==0 else .2 if distance in (5,7) else .6
    if 'uncertain' in (ka['confidence'],kb['confidence']): harmonic=.3
    score=abs(a['bpm']-b['bpm'])/5+abs(a['energy']-b['energy'])+harmonic+(16-n)/32
    return {'from':a['id'],'to':b['id'],'bars':n,'exit':round(start,4),'entry':round(entry,4),
            'duration':n*240/tempo,'score':round(score,3),
            'phraseAnchor':phrase_anchor,'phraseAnchorSource':'human' if a.get('phraseAnchor') is not None else 'estimated',
            'reason':f'{n}-bar '+('kick-supported overlap' if mapped else 'phrase overlap')+' · '+('close tonal match' if harmonic<.3 else 'check tonal overlap'),
            'mixEvidence':({'entryBar':incoming['startBar'],'exitBar':outgoing['startBar'],'incomingKickCoverage':incoming['kickCoverage'],'outgoingKickCoverage':outgoing['kickCoverage'],'confidence':'estimated','musicalArrival':b['mixMap'].get('musicalArrival')} if mapped else None)}

def make_plan(tracks,tempo=128,bars=16,direction='',use_ai=False):
    if not 108<=tempo<=142 or bars not in (8,16): raise ValueError('Choose 108–142 BPM and 8 or 16 bars.')
    edges=[e for a in tracks for b in tracks if a['id']!=b['id'] for e in [edge(a,b,tempo,bars)] if e]
    lookup={(e['from'],e['to']):e for e in edges}
    tracks_by_id={t['id']:t for t in tracks}
    eligible=[t for t in tracks if t['ready'] and abs(tempo/t['bpm']-1)<=.04]
    if not eligible: raise ValueError('No tracks are ready. Review the grid and phrase markers first.')
    # Small bounded beam search prioritizes covering the crate, then transition quality.
    beam=[([t['id']],0) for t in eligible]
    best=beam[:]
    for _ in range(len(eligible)-1):
        nxt=[]
        for path,cost in beam:
            for t in eligible:
                if t['id'] not in path and (path[-1],t['id']) in lookup:
                    e=lookup[path[-1],t['id']]
                    if len(path)>1:
                        try:validate_sequence([lookup[path[-2],path[-1]],e],tracks_by_id,tempo)
                        except ValueError:continue
                    nxt.append((path+[t['id']],cost+e['score']))
        if not nxt: break
        beam=sorted(nxt,key=lambda x:x[1])[:100]; best=beam
    order=min(best,key=lambda x:x[1])[0]; mode='Rules'; note='Ordered by phrase fit, tempo and tonal evidence.'
    if use_ai:
        # Astra chooses the musical route and an executable overlap for every handoff.
        options = list(edges)
        if bars == 16:
            options += [e for a in tracks for b in tracks if a['id'] != b['id']
                        for e in [edge(a,b,tempo,8)] if e and e not in options]
        prompt={'task': 'Program a coherent 4/4 house DJ set. Choose the order, and choose one supplied 8/16-bar transition option per consecutive pair. Give a concise musical rationale for the set and each handoff. Use as many suitable tracks as possible once each; exclude stylistic outliers. Never invent cues. Each middle track needs 8 seconds after its incoming handoff before its outgoing transition. The audio engine uses the tested continuous-gain bass handoff; do not invent effects or curves.',
                'setTempo':tempo,'direction':direction,
                'tracks':[song_evidence(t) for t in eligible],
                'transitionOptions':[{**e,'option':i} for i,e in enumerate(options)]}
        result=decide('dj_set',prompt,{'type':'object','properties':{
            'order':{'type':'array','items':{'type':'string'}}, 'reason':{'type':'string'},
            'handoffs':{'type':'array','items':{'type':'object','properties':{
                'option':{'type':'integer'},'reason':{'type':'string'}},
                'required':['option','reason'],'additionalProperties':False}}},
            'required':['order','reason','handoffs'],'additionalProperties':False})
        proposed=result['order']
        if len(result['handoffs']) != len(proposed)-1:
            raise ValueError('Astra did not supply a complete set of handoffs.')
        chosen=[]
        for pair,handoff in zip(zip(proposed,proposed[1:]),result['handoffs']):
            index=handoff['option']
            if type(index) is not int or not 0 <= index < len(options):
                raise ValueError('Astra chose an unknown transition.')
            selected=options[index]
            if (selected['from'],selected['to']) != pair:
                raise ValueError('Astra chose a transition for the wrong tracks.')
            chosen.append({**selected,'astraReason':handoff['reason']})
        lookup.update({(e['from'],e['to']):e for e in chosen})
        allowed={t['id'] for t in eligible}
        if not proposed or len(set(proposed))!=len(proposed) or not set(proposed)<=allowed or any((a,b) not in lookup for a,b in zip(proposed,proposed[1:])):
            raise ValueError('Astra returned an invalid order; the previous plan is unchanged.')
        validate_sequence([lookup[a,b] for a,b in zip(proposed,proposed[1:])],tracks_by_id,tempo)
        order=proposed; mode='Astra'; note=result['reason']
    return {'order':order,'transitions':[lookup[a,b] for a,b in zip(order,order[1:])],
            'tempo':tempo,'mode':mode,'reason':note,'excluded':[t['id'] for t in tracks if t['id'] not in order]}
