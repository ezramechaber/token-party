"""Model decisions must never bypass executable audio or queue ownership checks."""
import threading
import pytest
from b2b import astra
from b2b.requests import RequestManager
from test_requests import track, C, Y


def make(tmp_path, assessor, tracks=None):
    tracks = tracks or [track(), track('b')]
    return RequestManager(tmp_path, lambda: tracks, lambda url, update: tracks[-1],
                          auto_process=False, assessor=assessor)


def test_astra_accept_cannot_override_tempo(tmp_path):
    m=make(tmp_path,lambda *args:{'status':'accepted','reason':'Nice house groove'},[track(),track('b',bpm=140)])
    m.process(m.submit(Y,'DJ test',C)['id'])
    r=m.list()[0]
    assert r['status']=='rejected' and not m.queue_ids()
    assert r['decisionMode']=='Astra' and '140 BPM' in r['technicalReason']


def test_astra_rejects_style_despite_compatible_grid(tmp_path):
    m=make(tmp_path,lambda *args:{'status':'rejected','reason':'Comedy cue does not fit club house.'})
    m.process(m.submit(Y,'DJ test',C)['id'])
    assert m.list()[0]['status']=='rejected' and not m.queue_ids()


def test_astra_can_judge_energy_when_handoff_is_safe(tmp_path):
    m=make(tmp_path,lambda *args:{'status':'accepted','reason':'An intentional lift.'},[track(),track('b',energy=.99)])
    m.process(m.submit(Y,'DJ test',C)['id'])
    assert m.queue_ids()==['b'] and m.list()[0]['transition']


def test_slow_astra_does_not_hold_lock_or_resurrect_dismissal(tmp_path):
    started,release=threading.Event(),threading.Event()
    def assess(*args):
        started.set();assert release.wait(3)
        return {'status':'accepted','reason':'Fits'}
    m=make(tmp_path,assess);ident=m.submit(Y,'DJ test',C)['id']
    worker=threading.Thread(target=m.process,args=(ident,));worker.start()
    assert started.wait(3)
    try:
        assert m.lock.acquire(timeout=.2)
        m.lock.release()
        m.dismiss(ident)
    finally:
        release.set();worker.join(3)
    assert m.list()[0]['status']=='dismissed' and not m.queue_ids()


def test_astra_error_requires_review(tmp_path):
    def fail(*args):raise RuntimeError('private details')
    m=make(tmp_path,fail);m.process(m.submit(Y,'DJ test',C)['id'])
    assert m.list()[0]['status']=='review' and not m.queue_ids()
    assert 'private details' not in str(m.list())


def test_private_key_storage(tmp_path,monkeypatch):
    monkeypatch.setattr(astra,'DATA',tmp_path);monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    astra.configure('sk-test-placeholder')
    assert astra.api_key()=='sk-test-placeholder'
    assert (tmp_path/'openai-key').stat().st_mode & 0o777 == 0o600
    monkeypatch.setenv('OPENAI_API_KEY','sk-env-placeholder')
    assert astra.api_key()=='sk-env-placeholder'

def test_local_dj_request_uses_same_assessor(tmp_path):
    calls=[]
    def assess(t,tracks,context):
        calls.append(t['id']);return {'status':'accepted','reason':'Fits the set.'}
    m=make(tmp_path,assess)
    r=m.submit_track('b',C);m.process(r['id'])
    assert calls==['b'] and m.queue_ids()==['b']
    assert m.list()[0]['provider']=='local' and m.list()[0]['name']=='DJ test'
    assert m.submit_track('b',C)['duplicate']


def test_song_evidence_includes_map_not_audio():
    t=track('b',path='/private/music.mp3',waveform=[1,2,3],mixMap={'bars':[{'kickFraction':1},{'kickFraction':0}]})
    evidence=astra.song_evidence(t)
    assert evidence['songMap']['supportedBarFraction']==.5
    assert 'path' not in evidence and 'waveform' not in evidence
