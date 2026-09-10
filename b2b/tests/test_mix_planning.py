from b2b.planner import edge


def record(id):
    return {'id':id,'bpm':120,'ready':True,'introBars':16,'outroBars':8,
            'entry':0,'introEnd':32,'outroStart':336,'exitEnd':352,
            'energy':.5,'key':{'root':0,'confidence':'uncertain'}}


def window(start,bars):
    return {'start':start,'end':start+bars*2,'startBar':int(start/2)+1,
            'bars':bars,'kickCoverage':1}


def test_mix_avoids_kickless_end_of_nominal_intro():
    # Old logic selected seconds16–32, whose last8sec have no kick.
    a,b=record('a'),record('b')
    a['mixMap']={'exitCandidates':[window(336,8)],'entryCandidates':[]}
    b['mixMap']={'entryCandidates':[window(0,8),window(32,16)],'exitCandidates':[]}
    chosen=edge(a,b,120,16)
    assert chosen['bars']==8
    assert chosen['entry']==0
    assert chosen['exit']==336
    assert chosen['mixEvidence']['entryBar']==1


def test_no_fallback_to_unsafe_window_when_maps_reject_it():
    a,b=record('a'),record('b')
    a['mixMap']={'exitCandidates':[window(336,8)],'entryCandidates':[]}
    b['mixMap']={'entryCandidates':[],'exitCandidates':[]}
    assert edge(a,b,120,8) is None


def test_mapped_windows_respect_manual_cue_limits_and_late_outro():
    a,b=record('a'),record('b')
    a['mixMap']={'exitCandidates':[window(200,16),window(336,8)],'entryCandidates':[]}
    b['mixMap']={'entryCandidates':[window(0,8),window(32,16)],'exitCandidates':[]}
    b.update(reviewed=True,entry=16)
    assert edge(a,b,120,16) is None


def test_mix_finishes_at_musical_arrival_not_end_of_drum_only_opening():
    a,b=record('a'),record('b')
    a['mixMap']={'exitCandidates':[window(336,8)],'entryCandidates':[]}
    b['mixMap']={'entryCandidates':[window(0,8),window(8,8),window(32,8)],
                 'exitCandidates':[],'musicalArrival':{'time':24,'confidence':'candidate'}}
    chosen=edge(a,b,120,8)
    assert chosen['entry']==8
    assert chosen['entry']+chosen['duration']==24
    assert chosen['mixEvidence']['musicalArrival']['time']==24
