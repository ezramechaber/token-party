"""Local gallery integration test using a generated solid-color JPEG, never personal photos."""
import json,uuid,urllib.request,urllib.error
from pathlib import Path
BASE='http://localhost:8770'
REVIEW='local-review-test-key-000000000000000000000'
WORKER='local-worker-test-key-000000000000000000000'
def call(path,key=None,data=None,ctype='application/json'):
 h={'Content-Type':ctype}
 if key:h['Authorization']='Bearer '+key
 if isinstance(data,dict):data=json.dumps(data).encode()
 try:
  with urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,headers=h)) as r:return r.status,r.read()
 except urllib.error.HTTPError as e:return e.code,e.read()
assert call('/api/media/testexport')[0]==401
assert call('/api/comments',data={})[0]==401
assert call('/api/gallery/upload',REVIEW,b'')[0]==401
fixture=(Path(__file__).resolve().parents[2]/'tests/fixtures/gray.jpg').read_bytes()
def upload(photo_id,revision_id):
 boundary='RoundtripTestBoundary'
 parts=[]
 for k,v in {'photo_id':photo_id,'id':revision_id,'label':'Test fixture','summary':'Generated solid-color integration-test fixture','created':'1'}.items():
  parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
 parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode()+fixture+b'\r\n')
 parts.append(f'--{boundary}--\r\n'.encode())
 return call('/api/gallery/upload',WORKER,b''.join(parts),'multipart/form-data; boundary='+boundary)[0]
assert upload('portrait','testexport') in (200,201)
for photo_id in ('gallery-one','gallery-two','gallery-three'):
 assert upload(photo_id,photo_id+'-original') in (200,201)
assert upload('unknown','testunknown')==400
assert upload('gallery-one','testexport')==400
assert call('/api/media/testexport',REVIEW)==(200,fixture)
s=json.loads(call('/api/review',REVIEW)[1]);assert len(s['photos'])==4
assert all(r['photo_id']==p['id'] for p in s['photos'] for r in p['revisions'])
assert all(r['url'].startswith('/api/media/') for p in s['photos'] for r in p['revisions'])
payload={'id':uuid.uuid4().hex,'photo_id':'gallery-one','revision_id':'gallery-one-original','text':'Local test comment'}
assert call('/api/comments',REVIEW,payload)[0]==201
assert call('/api/comments',REVIEW,payload)[0]==200
assert call('/api/comments',REVIEW,{**payload,'text':'Different'})[0]==400
assert call('/api/comments',REVIEW,{**payload,'id':uuid.uuid4().hex,'revision_id':'testexport'})[0]==400
assert any(c['id']==payload['id'] for c in json.loads(call('/api/review',REVIEW)[1])['comments'])
print('PASS: photo authentication, protected upload/read, gallery catalog, persistent comments, idempotency, and cross-photo revision rejection.')
