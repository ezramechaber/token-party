from b2b import server


def test_projection_resolves_metadata_from_crate(monkeypatch):
    monkeypatch.setattr(server,'tracks',{'a':{'id':'a','title':'Original','artist':'Artist','bpm':124,'path':'/private/audio.mp3'}})
    monkeypatch.setattr(server,'session_state',{})
    body=server.SessionProjection(decks=[{'id':'a','title':'Spoof','playing':True}],
                                  crate=[{'id':'a','path':'private'}],tempo=124,tailId='a',crateIds=['a','missing'])
    server.publish_session(body)
    result=server.get_session()
    assert result['decks'][0]['title']=='Original'
    assert result['crateIds']==['a']
    assert 'private' not in str(result)


def test_request_context_comes_from_session(monkeypatch):
    class Manager:
        def submit(self,url,name,context):return context
    monkeypatch.setattr(server,'request_manager',Manager())
    monkeypatch.setattr(server,'session_state',{'tempo':125,'bars':8,'tailId':'tail','crateIds':['a','tail'],'direction':'Warm house'})
    assert server.listener_submit(server.ListenerSubmission(url='https://example.com',name='Test'))==server.session_state


def test_request_review_uses_current_session_and_forwards_decision(monkeypatch):
    class Manager:
        def resolve(self,ident,track_id,context,approve):
            return {'id':ident,'track':track_id,'context':context,'approved':approve}
        def retry(self,ident,context):return context
        def dismiss(self,ident):raise ValueError('Unknown request')
    context={'tempo':126,'bars':8,'tailId':'current-tail','crateIds':['current-tail'],'direction':'Build slowly'}
    monkeypatch.setattr(server,'request_manager',Manager())
    monkeypatch.setattr(server,'session_state',context)
    result=server.resolve_request('request',server.ResolveRequest(trackId='candidate',approve=True))
    assert result=={'id':'request','track':'candidate','context':context,'approved':True}
    result['context']['crateIds'].append('changed-copy')
    assert server.session_state['crateIds']==['current-tail']
    assert server.retry_request('request')==context
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as error:server.dismiss_request('missing')
    assert error.value.status_code==400
