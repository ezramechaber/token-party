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
    monkeypatch.setattr(server,'session_state',{'tempo':125,'bars':8,'tailId':'tail','crateIds':['a','tail']})
    assert server.listener_submit(server.ListenerSubmission(url='https://example.com',name='Test'))==server.session_state
