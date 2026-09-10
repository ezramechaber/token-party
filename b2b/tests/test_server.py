import pytest
from fastapi import HTTPException
from b2b import server

def track(id,ready=True):
    return {'id':id,'bpm':124,'ready':ready,'introBars':16,'outroBars':16,'introEnd':31,
            'exitEnd':250,'energy':.6,'key':{'root':0,'confidence':'estimated'}}

def test_manual_order_preserves_selection_and_reports_exclusions(monkeypatch):
    monkeypatch.setattr(server,'tracks',{t['id']:t for t in [track('a'),track('b'),track('bad',False)]})
    p=server.plan(server.PlanRequest(ids=['b','bad','a'],tempo=124,fixed=True))
    assert p['order']==['b','a']
    assert p['excluded']==['bad']
    assert p['transitions'][0]['from']=='b'

def test_reject_duplicate_crate_ids(monkeypatch):
    monkeypatch.setattr(server,'tracks',{'a':track('a')})
    with pytest.raises(HTTPException) as error:server.plan(server.PlanRequest(ids=['a','a']))
    assert error.value.status_code==400

def test_missing_key_does_not_claim_astra(monkeypatch):
    monkeypatch.setattr(server.astra,'api_key',lambda:'')
    monkeypatch.setattr(server,'tracks',{'a':track('a'),'b':track('b')})
    with pytest.raises(HTTPException) as error:server.plan(server.PlanRequest(ids=['a','b'],astra=True))
    assert 'Connect Astra' in error.value.detail


def test_fixed_order_rejects_overlapping_middle_track_windows(monkeypatch):
    monkeypatch.setattr(server,'tracks',{id:track(id) for id in ['a','b','c']})
    def overlap(a,b,tempo,bars):
        return {'from':a['id'],'to':b['id'],'entry':190,'exit':200,'duration':31}
    monkeypatch.setattr(server,'edge',overlap)
    with pytest.raises(HTTPException) as error:
        server.plan(server.PlanRequest(ids=['a','b','c'],tempo=124,fixed=True))
    assert error.value.status_code==400
    assert 'prepare the next deck' in error.value.detail


def test_failed_marker_reanalysis_preserves_previous_grid(monkeypatch):
    original={**track('a'),'duration':300,'path':'unused-test-audio','gridOffset':0.01}
    monkeypatch.setattr(server,'tracks',{'a':original.copy()})
    monkeypatch.setattr(server,'decode',lambda _:None)
    def fail(*args):raise RuntimeError('decode failed')
    monkeypatch.setattr(server,'analyze_mix_map',fail)
    with pytest.raises(HTTPException) as error:
        server.correct('a',server.Correction(bpm=125,gridOffset=.05,entry=.05,introBars=16,exitEnd=250,outroBars=16))
    assert error.value.status_code==422
    assert server.tracks['a']==original


def test_marker_save_rebuilds_then_publishes_updated_grid(monkeypatch):
    original={**track('a'),'duration':300,'path':'unused-test-audio','gridOffset':0.01}
    monkeypatch.setattr(server,'tracks',{'a':original.copy()})
    monkeypatch.setattr(server,'decode',lambda _:None)
    observed=[]
    def rebuild(audio,sr,bpm,offset,candidate):
        assert server.tracks['a']==original
        assert bpm==125 and offset==.05
        return {'entryCandidates':[{}],'exitCandidates':[{}]}
    monkeypatch.setattr(server,'analyze_mix_map',rebuild)
    monkeypatch.setattr(server,'save',lambda:observed.append(server.tracks['a'].copy()))
    monkeypatch.setattr(server,'public',lambda t:t)
    result=server.correct('a',server.Correction(bpm=125,gridOffset=.05,entry=.05,introBars=16,exitEnd=250,outroBars=16))
    assert observed==[result] and result['reviewed'] and result['ready']
    assert result['introEnd']==.05+16*240/125

def test_extension_preserves_astra_short_handoff(monkeypatch):
    from b2b.planner import edge
    rows=[track('a'),track('b'),track('c')]
    monkeypatch.setattr(server,'tracks',{t['id']:t for t in rows})
    previous={**edge(rows[0],rows[1],128,8),'astraReason':'Quick handoff preserves momentum.'}
    result=server.plan(server.PlanRequest(ids=['a','b','c'],tempo=128,bars=16,fixed=True,previous=[previous]))
    assert result['transitions'][0]==previous
    previous['entry']+=.1
    with pytest.raises(HTTPException):
        server.plan(server.PlanRequest(ids=['a','b','c'],tempo=128,bars=16,fixed=True,previous=[previous]))
