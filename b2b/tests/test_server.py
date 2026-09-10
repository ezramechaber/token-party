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
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.setattr(server,'tracks',{'a':track('a'),'b':track('b')})
    with pytest.raises(HTTPException) as error:server.plan(server.PlanRequest(ids=['a','b'],astra=True))
    assert 'OPENAI_API_KEY' in error.value.detail


def test_fixed_order_rejects_overlapping_middle_track_windows(monkeypatch):
    monkeypatch.setattr(server,'tracks',{id:track(id) for id in ['a','b','c']})
    def overlap(a,b,tempo,bars):
        return {'from':a['id'],'to':b['id'],'entry':190,'exit':200,'duration':31}
    monkeypatch.setattr(server,'edge',overlap)
    with pytest.raises(HTTPException) as error:
        server.plan(server.PlanRequest(ids=['a','b','c'],tempo=124,fixed=True))
    assert error.value.status_code==400
    assert 'prepare the next deck' in error.value.detail
