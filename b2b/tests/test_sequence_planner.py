import json
import pytest
from b2b.planner import edge, make_plan, validate_sequence


def trio(late_entry=True):
    def window(start):
        return {'bars':16,'start':start,'end':start+32,'startBar':int(start/2)+1,'kickCoverage':1}
    def track(id,entry,exit,end):
        return {'id':id,'title':id,'artist':'Test artist','ready':True,'bpm':120,'gridOffset':0,'introEnd':32,'exitEnd':end,
                'introBars':16,'outroBars':16,'energy':.5,'key':{'root':0,'confidence':'estimated'},
                'mixMap':{'entryCandidates':[] if entry is None else [window(entry)],
                          'exitCandidates':[] if exit is None else [window(exit)]}}
    return [track('a',None,224,256),track('b',80 if late_entry else 32,96,128),track('c',0,None,256)]


def test_pairwise_valid_triple_can_overlap_in_middle_track():
    tracks=trio();a,b,c=tracks
    transitions=[edge(a,b,120,16),edge(b,c,120,16)]
    assert all(transitions)
    with pytest.raises(ValueError,match='at least 8 seconds'):
        validate_sequence(transitions,tracks,120)
    # Beam search must not return the only three-track chain when it is infeasible.
    plan=make_plan(tracks,120,16)
    assert len(plan['order'])==2
    validate_sequence(plan['transitions'],tracks,120)


def test_feasible_triple_retains_all_tracks_and_unchanged_edges():
    tracks=trio(late_entry=False)
    plan=make_plan(tracks,120,16)
    assert plan['order']==['a','b','c']
    assert plan['transitions']==[edge(tracks[0],tracks[1],120,16),edge(tracks[1],tracks[2],120,16)]
    assert validate_sequence(plan['transitions'],{t['id']:t for t in tracks},120) is None


def test_preparation_margin_is_measured_in_prepared_seconds():
    tracks=trio(late_entry=False)
    incoming={'from':'a','to':'b','entry':60.,'exit':224.,'duration':16*240/124}
    outgoing={'from':'b','to':'c','entry':0.,'exit':100.,'duration':16*240/124}
    with pytest.raises(ValueError,match='7.7 seconds'):
        validate_sequence([incoming,outgoing],tracks,124)
    validate_sequence([incoming,outgoing],tracks,124,min_prepare_seconds=7)


def test_disconnected_edges_are_rejected():
    tracks=trio(late_entry=False)
    with pytest.raises(ValueError,match='middle track'):
        validate_sequence([edge(tracks[0],tracks[1],120,16),edge(tracks[0],tracks[2],120,16)],tracks,120)


def test_astra_cannot_accept_a_pairwise_valid_but_infeasible_order(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-key-not-a-secret')
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):
            return json.dumps({'output':[{'content':[{'type':'output_text','text':json.dumps({'order':['a','b','c'],'reason':'Test order'})}]}]}).encode()
    monkeypatch.setattr('b2b.planner.urllib.request.urlopen',lambda *args,**kwargs:Response())
    with pytest.raises(ValueError,match='at least 8 seconds'):
        make_plan(trio(),120,16,use_ai=True)
