"""Outbound-only bridge from the hosted review inbox to the local Lightroom queue."""
import json
from pathlib import Path
import threading
import time
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlparse

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

# Never forward the private worker credential to a sign-in or other redirected host.
urlopen = build_opener(NoRedirect()).open

class RemoteInbox:
    def __init__(self, store, runner, config_path):
        config=json.loads(Path(config_path).read_text())
        self.url=config['url'].rstrip('/')
        parsed=urlparse(self.url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
            raise ValueError('Remote inbox must use an HTTPS origin.')
        self.key=config['worker_key']
        self.review_link=self.url+'/#'+config['review_key']
        self.photo_id=config['photo_id']
        self.store,self.runner=store,runner
        self.stop=threading.Event()
        self.last_sync=None
        self.error=None
        self.update=None
    def snapshot(self):
        return {'configured':True,'connected':self.last_sync is not None and time.time()-self.last_sync<20,
                'last_sync':self.last_sync,'error':self.error,'review_url':self.review_link}
    def sync(self):
        with self.store.connect() as db:
            photo=db.execute('SELECT * FROM photos WHERE id=?',(self.photo_id,)).fetchone()
            if not photo: raise ValueError('The paired photo is no longer in this gallery.')
            revision=self.store.revision(photo['current_revision'])
        accepting=self.runner.available() and self.runner.started<self.runner.max_jobs
        payload={'photo':{'id':photo['id'],'title':photo['title'],'revision':revision['id'],'label':revision['label']},'accepting':accepting,'update':self.update}
        req=Request(self.url+'/api/worker/sync',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=12) as response:
            data=json.loads(response.read(16000))
        self.last_sync=time.time()
        self.error=None
        self.update=None
        remote=data.get('request')
        if not remote:return
        request_id='remote_'+remote['id']
        with self.store.connect() as db:
            existing=db.execute('SELECT id FROM jobs WHERE request_id=?',(request_id,)).fetchone()
            active=db.execute("SELECT id FROM jobs WHERE status IN ('queued','running','verifying')").fetchone()
        if existing:
            job=self.store.get_job(existing['id'])
            label=self.store.revision(job['revision_id'])['label'] if job['revision_id'] else None
            messages={'queued':'Received on the photographer’s Mac.','running':'Astra is making recoverable edits in Lightroom.','verifying':'The Mac is checking the new JPEG export.','completed':'The new JPEG was verified and added to the local gallery.','failed':'The edit needs the photographer’s attention. Earlier exports are preserved.','cancelled':'The photographer stopped this revision. Earlier exports are preserved.'}
            self.update={'id':remote['id'],'status':'running' if job['status']=='queued' else job['status'],'message':messages[job['status']],'result_label':label}
        elif remote['base_revision']!=revision['id']:
            self.update={'id':remote['id'],'status':'stale','message':'The photo has a newer version. Review the latest export before requesting another edit.'}
        elif remote['status']!='requested':
            # The relay knows another local state accepted this request. Never replay blindly.
            self.update={'id':remote['id'],'status':'failed','message':'This request was accepted by a different local session. Ask the photographer to inspect Lightroom before retrying.'}
        elif accepting and not active:
            try:
                job,created=self.store.create_job(self.photo_id,remote['base_revision'],remote['feedback'],request_id)
                if created:
                    self.store.event(job['id'],'remote','Feedback received from the hosted review link.')
                    self.runner.start(job)
            except ValueError:
                # Local admission could change between polling and saving. Recheck next poll.
                return
    def run(self):
        while not self.stop.is_set():
            try:self.sync()
            except HTTPError as error:
                self.error=('The inbox’s access settings currently block this Mac. External access approval is pending.' if error.code in (301,302,303,307,308,401,403) else 'The inbox could not process the connection. Retrying automatically.')
            except Exception:
                self.error='The remote inbox is unreachable. Local editing is still available; reconnecting automatically.'
            self.stop.wait(3)
    def start(self):
        threading.Thread(target=self.run,daemon=True,name='remote-inbox').start()
