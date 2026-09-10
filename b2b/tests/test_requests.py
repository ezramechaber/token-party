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

def pending_review(m, url=S):
    ident=m.submit(url,'Listener',C)['id'];m.process(ident);return ident

def test_dj_confirms_title_only_candidate_and_delivery(tmp_path):
    m=manager(tmp_path,metadata={'title':'Track b'})
    ident=pending_review(m)
    assert m.resolve(ident,'b',C)['status']=='accepted'
    m.consume('b')
    result=m.list()[0]
    assert result['status']=='added' and not result['queued']
    assert any(h['action']=='confirm-recording' for h in result['history'])
    assert any(h['action']=='added-to-set' for h in result['history'])
    with pytest.raises(ValueError,match='already in the set'):m.dismiss(ident)

def test_attach_audio_to_spotify_needs_audio(tmp_path):
    m=manager(tmp_path,metadata={'title':'Missing'})
    ident=pending_review(m)
    assert m.list()[0]['status']=='needs_audio'
    assert m.resolve(ident,'b',C)['status']=='accepted'

def test_approval_overrides_energy_only_after_safe_handoff(tmp_path):
    m=manager(tmp_path,tracks=[track(),track('b',energy=.99)])
    ident=pending_review(m,Y)
    first=m.resolve(ident,'b',C)
    assert first['status']=='review' and first['reviewKind']=='energy'
    approved=m.resolve(ident,'b',C,approve=True)
    assert approved['status']=='accepted' and approved['approvedByDJ']
    assert approved['transition']['from']=='a' and approved['transition']['to']=='b'

def test_approval_can_override_tonal_taste(tmp_path):
    m=manager(tmp_path,tracks=[track(),track('b',key={'root':2,'confidence':'estimated'})])
    ident=pending_review(m,Y)
    assert m.list()[0]['reviewKind']=='key'
    assert m.resolve(ident,'b',C,approve=True)['status']=='accepted'

@pytest.mark.parametrize('fields',[{'bpm':140},{'ready':False},{'beatConfidence':.2},
                                    {'introBars':4},{'introEnd':400}])
def test_approval_cannot_override_technical_failures(tmp_path,fields):
    m=manager(tmp_path,tracks=[track(),track('b',**fields)])
    ident=pending_review(m,Y)
    result=m.resolve(ident,'b',C,approve=True)
    assert result['status']!='accepted' and not m.queue_ids()

def test_approval_needs_valid_current_tail(tmp_path):
    m=manager(tmp_path,metadata={'title':'Missing'})
    ident=pending_review(m)
    assert m.resolve(ident,'b',{**C,'tailId':'missing'},approve=True)['status']=='review'
    with pytest.raises(ValueError,match='existing analyzed'):m.resolve(ident,'missing',C,True)

def test_retry_reuses_record_and_new_context(tmp_path):
    calls=[]
    def importer(url,update):
        calls.append(url)
        if len(calls)==1:raise ValueError('temporary')
        return track('b')
    m=manager(tmp_path,importer=importer)
    ident=pending_review(m,Y)
    assert m.list()[0]['status']=='error'
    assert m.submit(Y,'Another',C)['duplicate']
    assert m.retry(ident,{**C,'tempo':121})['status']=='pending'
    m.process(ident)
    assert m.list()[0]['status']=='accepted' and len(m.list())==1
    assert len(calls)==2 and m.list()[0]['transition']['duration']==16*240/121
    assert any(h['action']=='retry' for h in m.list()[0]['history'])

def test_dismiss_allows_explicit_retry_only(tmp_path):
    m=manager(tmp_path)
    ident=m.submit(Y,'',C)['id']
    assert m.dismiss(ident)['status']=='dismissed'
    m.process(ident)
    assert m.list()[0]['status']=='dismissed'
    assert m.submit(Y,'',C)['status']=='dismissed'
    m.retry(ident,C);m.process(ident)
    assert m.list()[0]['status']=='accepted'

def test_resolved_old_request_joins_end_not_submission_position(tmp_path):
    tracks=[track(),track('b'),track('c')]
    m=manager(tmp_path,tracks=tracks,metadata={'title':'Unknown'},importer=lambda url,update:tracks[1])
    old=pending_review(m,S)
    pending_review(m,Y)
    result=m.resolve(old,'c',C)
    assert m.queue_ids()==['b','c'] and result['transition']['from']=='b'

def test_dismiss_predecessor_invalidates_later_reservations(tmp_path):
    tracks=[track(),track('b'),track('c')];imports=iter(tracks[1:])
    m=manager(tmp_path,tracks=tracks,importer=lambda url,update:next(imports))
    first=pending_review(m,Y)
    second=pending_review(m,'https://youtu.be/abcdefghijk')
    m.dismiss(first)
    assert not m.queue_ids()
    assert m.list()[1]['reviewKind']=='queue-changed'
    assert m.resolve(second,'c',C)['transition']['from']=='a'

def test_dismissed_running_worker_cannot_resurrect_request(tmp_path):
    import threading
    entered,release=threading.Event(),threading.Event()
    def importer(url,update):
        entered.set();assert release.wait(3)
        update(status='analyzing',title='Late old title')
        return track('b')
    m=manager(tmp_path,importer=importer)
    ident=m.submit(Y,'',C)['id']
    worker=threading.Thread(target=m.process,args=(ident,));worker.start()
    assert entered.wait(3)
    m.dismiss(ident);release.set();worker.join(3)
    assert not worker.is_alive() and m.list()[0]['status']=='dismissed'
    assert not m.queue_ids() and m.list()[0].get('title')!='Late old title'

def test_old_attempt_cannot_replace_new_resolution(tmp_path):
    import threading
    entered,release=threading.Event(),threading.Event()
    def importer(url,update):entered.set();assert release.wait(3);return track('b')
    tracks=[track(),track('b'),track('c')]
    m=manager(tmp_path,tracks=tracks,importer=importer)
    ident=m.submit(Y,'',C)['id']
    worker=threading.Thread(target=m.process,args=(ident,));worker.start();assert entered.wait(3)
    m.dismiss(ident);m.resolve(ident,'c',C);release.set();worker.join(3)
    assert m.queue_ids()==['c'] and m.list()[0]['trackId']=='c'

def test_concurrent_resolution_can_only_reserve_once(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    m=manager(tmp_path,metadata={'title':'Unknown'})
    ident=pending_review(m)
    def resolve():
        try:return m.resolve(ident,'b',C)['status']
        except ValueError:return 'already-resolved'
    with ThreadPoolExecutor(max_workers=2) as executor:results=list(executor.map(lambda _:resolve(),range(2)))
    assert sorted(results)==['accepted','already-resolved'] and m.queue_ids()==['b']

def test_actions_validate_identity_and_context(tmp_path):
    m=manager(tmp_path)
    for action in (lambda:m.dismiss('unknown'),lambda:m.retry('unknown',C),lambda:m.resolve('unknown','b',C)):
        with pytest.raises(ValueError,match='Request not found'):action()
    ident=m.submit(Y,'',C)['id']
    with pytest.raises(ValueError):m.retry(ident,C)
    with pytest.raises(ValueError):m.resolve(ident,'b',C)
    with pytest.raises(ValueError):m.submit(Y,'',{**C,'tempo':float('nan')})

def test_recovery_preserves_history_and_can_retry(tmp_path):
    m=manager(tmp_path);ident=m.submit(Y,'',C)['id']
    recovered=manager(tmp_path)
    result=recovered.list()[0]
    assert result['reviewKind']=='interrupted' and result['history'][-1]['action']=='interrupted'
    recovered.retry(ident,C);recovered.process(ident)
    assert recovered.list()[0]['status']=='accepted'

def test_legacy_consumed_records_show_added(tmp_path):
    m=manager(tmp_path);ident=pending_review(m,Y)
    stored=json.loads((tmp_path/'requests.json').read_text());stored[0]['queued']=False
    (tmp_path/'requests.json').write_text(json.dumps(stored))
    restored=manager(tmp_path)
    assert restored.list()[0]['status']=='added' and not restored.queue_ids()

def test_retry_obeys_processing_capacity(tmp_path):
    m=manager(tmp_path);ident=m.submit(Y,'',C)['id'];m.dismiss(ident)
    for n in range(8):m.submit('https://youtu.be/'+str(n).zfill(11),'',C)
    with pytest.raises(ValueError,match='Eight'):m.retry(ident,C)
