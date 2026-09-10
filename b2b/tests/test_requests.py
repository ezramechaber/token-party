import json
import pytest
from b2b.requests import RequestManager, request_url, assess_fit
S='https://open.spotify.com/track/0123456789ABCDEFGHIJKL'
Y='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
C={'tempo':120,'bars':16,'tailId':'a','crateIds':['a']}
def track(id='a',**kw):
    return {'id':id,'title':'Track '+id,'artist':'Artist','bpm':120,'ready':True,'beatConfidence':.9,
      'introBars':16,'outroBars':16,'entry':0,'introEnd':32,'outroStart':320,'exitEnd':352,
      'energy':.5,'key':{'root':0,'confidence':'estimated'},**kw}
def manager(path,tracks=None,metadata=None,importer=None):
    tracks=tracks or [track(),track('b')]
    return RequestManager(path,lambda:tracks,importer or (lambda url,update:tracks[-1]),
      metadata_resolver=lambda url:metadata or {'title':'Track b','artist':'Artist'},auto_process=False)
@pytest.mark.parametrize('url',['http://127.0.0.1/foo','https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ',
 'https://user@open.spotify.com/track/0123456789ABCDEFGHIJKL','https://open.spotify.com:443/track/0123456789ABCDEFGHIJKL',
 'https://open.spotify.com/album/0123456789ABCDEFGHIJKL','https://youtu.be/dQw4w9WgXcQ/../../x','file:///etc/passwd'])
def test_bad_urls(url):
    with pytest.raises(ValueError):request_url(url)
def test_canonical():
    assert request_url(S+'?si=abc')[1]==S
    assert request_url('https://youtu.be/dQw4w9WgXcQ?t=5')[1]==Y
def test_known_spotify(tmp_path):
    m=manager(tmp_path);m.process(m.submit(S,'Listener',C)['id'])
    assert m.list()[0]['status']=='accepted' and m.queue_ids()==['b']
    assert 'context' not in m.list()[0]
    assert json.loads((tmp_path/'requests.json').read_text())[0]['queued']
    m.consume('b');assert not m.queue_ids()
def test_title_only(tmp_path):
    m=manager(tmp_path,metadata={'title':'Track b'});m.process(m.submit(S,'',C)['id'])
    assert m.list()[0]['status']=='review' and m.list()[0]['candidateIds']==['b']
def test_missing_audio(tmp_path):
    m=manager(tmp_path,metadata={'title':'Unknown'});m.process(m.submit(S,'',C)['id'])
    assert m.list()[0]['status']=='needs_audio'
def test_youtube_and_duplicate(tmp_path):
    m=manager(tmp_path);r=m.submit(Y,'',C);m.process(r['id'])
    assert m.list()[0]['status']=='accepted'
    d=m.submit(Y+'&list=example','',C)
    assert d['duplicate'] and d['id']==r['id'] and len(m.list())==1
def test_tempo_rejected(tmp_path):
    m=manager(tmp_path,tracks=[track(),track('b',bpm=140)]);m.process(m.submit(Y,'',C)['id'])
    assert m.list()[0]['status']=='rejected' and not m.queue_ids()
def test_error_redaction(tmp_path):
    def fail(url,update):raise RuntimeError('/private/path?secret=abc')
    m=manager(tmp_path,importer=fail);m.process(m.submit(Y,'',C)['id'])
    assert m.list()[0]['status']=='error' and 'secret' not in str(m.list())
def test_evidence_gate():
    for kwargs in ({'beatConfidence':.2},{'introBars':4},{'energy':.99}):
        assert assess_fit(track('b',**kwargs),[track()],C)['status']=='review'
    assert assess_fit(track('b'),[],C)['status']=='review'
def test_queue_last_tail(tmp_path):
    tracks=[track(),track('b'),track('c')];calls=iter(tracks[1:])
    m=manager(tmp_path,tracks=tracks,importer=lambda url,update:next(calls))
    m.process(m.submit(Y,'',C)['id']);m.process(m.submit('https://youtu.be/abcdefghijk','',C)['id'])
    assert m.queue_ids()==['b','c'] and m.list()[1]['transition']['from']=='b'
def test_recover_pending(tmp_path):
    m=manager(tmp_path);m.submit(Y,'',C)
    assert manager(tmp_path).list()[0]['status']=='review'
def test_pending_limit(tmp_path):
    m=manager(tmp_path)
    for n in range(8):m.submit('https://youtu.be/'+str(n).zfill(11),'',C)
    with pytest.raises(ValueError,match='Eight'):m.submit('https://youtu.be/zzzzzzzzzzz','',C)
