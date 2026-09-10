"""Run against the local inbox preview only; no model calls or personal media."""
import concurrent.futures
import json
import urllib.request
import urllib.error
import uuid
BASE='http://localhost:8770'
REVIEW='local-review-test-key-000000000000000000000'
WORKER='local-worker-test-key-000000000000000000000'
def request(path,key=None,payload=None,origin=None):
 headers={'Content-Type':'application/json'}
 if key:headers['Authorization']='Bearer '+key
 if origin:headers['Origin']=origin
 req=urllib.request.Request(BASE+path,headers=headers,data=json.dumps(payload).encode() if payload is not None else None)
 try:
  with urllib.request.urlopen(req) as res:return res.status,json.load(res)
 except urllib.error.HTTPError as error:
  raw=error.read()
  try:data=json.loads(raw)
  except ValueError:data={}
  return error.code,data
def sync(revision,update=None):
 return request('/api/worker/sync',WORKER,{'photo':{'id':'portrait','revision':revision,'label':'Test version','title':'Test portrait'},'accepting':True,'update':update})
assert request('/api/review')[0]==401
assert request('/api/review',WORKER)[0]==401
assert request('/api/worker/sync',REVIEW,{})[0]==401
version=uuid.uuid4().hex
assert sync(version)[0]==200
# Finish a previous test request, if this test is rerun.
for item in request('/api/review',REVIEW)[1]['requests']:
 if item['status'] in ('requested','running','verifying'):sync(version,{'id':item['id'],'status':'cancelled','message':'Test cleanup'})
payload={'id':uuid.uuid4().hex,'base_revision':version,'feedback':'Reduce grain a little'}
assert request('/api/review',REVIEW,payload,origin='https://elsewhere.example')[0] in (400,403)
assert request('/api/review',REVIEW,{**payload,'base_revision':'old'})[0]==409
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 results=list(pool.map(lambda i:request('/api/review',REVIEW,{**payload,'id':payload['id']+str(i)}),range(2)))
assert sorted(r[0] for r in results)==[202,409],results
accepted=next(r[1] for r in results if r[0]==202)
payload['id']=accepted['id']
assert request('/api/review',REVIEW,payload)[0]==200
assert request('/api/review',REVIEW,{**payload,'feedback':'Different'})[0]==400
assert sync(version)[1]['request']['id']==accepted['id']
new_version=uuid.uuid4().hex
assert sync(new_version,{'id':accepted['id'],'status':'completed','message':'Test export verified','result_label':'Test V2'})[0]==200
# A late progress report cannot roll a completed job back to running.
sync(new_version,{'id':accepted['id'],'status':'running','message':'Late progress'})
assert next(r for r in request('/api/review',REVIEW)[1]['requests'] if r['id']==accepted['id'])['status']=='completed'
assert request('/api/review',REVIEW,payload)[0]==200 # idempotent even after base moves
assert request('/api/review',REVIEW,{**payload,'id':uuid.uuid4().hex})[0]==409
print('PASS: authentication separation, origin rejection, stale revisions, concurrent admission, idempotency, and terminal-state monotonicity.')
