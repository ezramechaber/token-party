import pytest
from b2b.planner import edge


def track(id):
    bpm=122.005;grid=1.0981;bar=240/bpm
    def window(start_bar,n):
        start=grid+(start_bar-1)*bar
        return {'start':round(start,4),'end':round(start+n*bar,4),'bars':n,
                'startBar':start_bar,'kickCoverage':1.}
    return dict(id=id,ready=True,bpm=bpm,gridOffset=grid,introBars=16,outroBars=8,
                entry=grid,introEnd=grid+16*bar,exitEnd=398.4581,outroStart=382.721,
                energy=.7,key={'root':0,'confidence':'estimated'},
                mixMap={'entryCandidates':[window(1,16),window(9,8)],
                        'exitCandidates':[window(181,16),window(189,8),window(177,16),window(185,8)]})


def test_legacy_nightcrawlers_map_chooses_bar177_not_bar181():
    result=edge(track('a'),track('b'),124,16)
    assert result['bars']==16
    assert result['mixEvidence']['exitBar']==177
    assert result['exit']==pytest.approx(347.3134,abs=.001)
    assert result['phraseAnchorSource']=='estimated'


def test_eight_bar_exit_follows_eight_bar_phase():
    result=edge(track('a'),track('b'),124,8)
    assert result['mixEvidence']['exitBar']==185


def test_explicit_phrase_anchor_and_reviewed_outro_bounds_are_preserved():
    a=track('a');bar=240/a['bpm']
    a['phraseAnchor']=a['gridOffset']+4*bar
    result=edge(a,track('b'),124,16)
    assert result['mixEvidence']['exitBar']==181
    assert result['phraseAnchorSource']=='human'
    a['reviewed']=True;a['outroStart']=390
    assert edge(a,track('b'),124,16) is None


def test_landing_does_not_finish_at_start_of_drum_break():
    from b2b.planner import edge
    base={'ready':True,'bpm':120,'gridOffset':0,'introEnd':32,'exitEnd':256,'outroStart':192,'introBars':16,'outroBars':32,'energy':.5,'key':{'root':0,'confidence':'certain'}}
    outgoing={'bars':8,'start':224,'end':240,'startBar':113,'kickCoverage':1}
    early={'bars':8,'start':0,'end':16,'startBar':1,'kickCoverage':1}
    late={'bars':8,'start':32,'end':48,'startBar':17,'kickCoverage':1}
    a={**base,'id':'a','mixMap':{'exitCandidates':[outgoing],'entryCandidates':[]}}
    b={**base,'id':'b','mixMap':{'exitCandidates':[],'entryCandidates':[early,late], 'bars':[{'start':i*2,'kickFraction':0 if 8<=i<12 else 1} for i in range(40)]}}
    assert edge(a,b,120,8)['entry']==32
