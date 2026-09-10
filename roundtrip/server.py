#!/usr/bin/env python3
"""Local Lightroom review app. No third-party Python packages required."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import sqlite3
import struct
import subprocess
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from edit_policy import supported_edit, POLICY

ROOT = Path(__file__).resolve().parent
TERMINAL = {'completed', 'failed', 'cancelled'}

def now():
    return time.time()

def uid():
    return uuid.uuid4().hex[:16]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def jpeg_dimensions(path):
    """Read SOF dimensions, reject missing JPEG framing and truncated exports."""
    data = Path(path).read_bytes()
    if len(data) < 1024 or data[:2] != b'\xff\xd8' or data[-2:] != b'\xff\xd9':
        raise ValueError('The returned file is not a complete JPEG export.')
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 255:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 255:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in [0xD8, 0xD9] or 0xD0 <= marker <= 0xD7:
            continue
        if marker == 0xDA:
            break
        length = int.from_bytes(data[offset:offset+2], 'big')
        if length < 2 or offset + length > len(data):
            break
        if marker in {0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF}:
            height, width = struct.unpack('>HH', data[offset+3:offset+7])
            if width < 100 or height < 100:
                raise ValueError('The export is too small to verify.')
            return width, height
        offset += length
    raise ValueError('Could not read JPEG dimensions.')

class Store:
    def __init__(self, state):
        self.state = Path(state).resolve()
        self.state.mkdir(parents=True, exist_ok=True)
        self.db_path = self.state / 'roundtrip.sqlite3'
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS photos(id TEXT PRIMARY KEY,title TEXT,source_filename TEXT,current_revision TEXT);
            CREATE TABLE IF NOT EXISTS revisions(id TEXT PRIMARY KEY,photo_id TEXT,parent_id TEXT,label TEXT,version TEXT,path TEXT,sha256 TEXT,width INTEGER,height INTEGER,summary TEXT,changes TEXT,created REAL,job_id TEXT);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,photo_id TEXT,base_revision TEXT,feedback TEXT,status TEXT,created REAL,updated REAL,error TEXT,revision_id TEXT,request_id TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,job_id TEXT,kind TEXT,message TEXT,created REAL);
            ''')
            # Never silently rerun an interrupted edit: Lightroom may already have changed.
            db.execute("UPDATE jobs SET status='failed',error='The app restarted during this revision. Inspect Lightroom before requesting another edit.',updated=? WHERE status IN ('queued','running','verifying')", (now(),))
    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()
    def event(self, job_id, kind, message):
        with self.lock, self.connect() as db:
            db.execute('INSERT INTO events(job_id,kind,message,created) VALUES(?,?,?,?)',(job_id,kind,message[:1200],now()))
    def seed(self, media, source_filename):
        with self.lock, self.connect() as db:
            if db.execute('SELECT 1 FROM photos').fetchone():
                return
            copies = self.state / 'media'
            copies.mkdir(exist_ok=True)
            seeds = [('original','Original','Roundtrip 00 - Original','Original RAW rendering',[]),('v1','V1','Roundtrip 01 - Fuji first pass','First edit inspired by the reference portrait',['Warmer white balance','Reduced blue and purple saturation','Highlight recovery and grain']),('v2','V2','Roundtrip 02 - Subject first','Cooler skin tones and a darker background',['White balance 5700 K, tint +2','Background mask exposure −0.55'])]
            parent = None
            for stem,label,version,summary,changes in seeds:
                src = Path(media) / (stem+'.jpg')
                width,height = jpeg_dimensions(src)
                dest = copies / (stem+'.jpg')
                if not dest.exists():
                    shutil.copy2(src,dest)
                db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(stem,'portrait',parent,label,version,str(dest),digest(dest),width,height,summary,json.dumps(changes),now(),None))
                parent=stem
            db.execute('INSERT INTO photos VALUES(?,?,?,?)',('portrait','Portrait study',source_filename,'v2'))
    def snapshot(self):
        with self.connect() as db:
            photos=[dict(p) for p in db.execute('SELECT * FROM photos')]
            for p in photos:
                p['revisions']=[self.public_revision(r) for r in db.execute('SELECT * FROM revisions WHERE photo_id=? ORDER BY created,rowid',(p['id'],))]
                p['jobs']=[self.job_from_db(db,j['id']) for j in db.execute('SELECT id FROM jobs WHERE photo_id=? ORDER BY created DESC',(p['id'],))]
            return photos
    @staticmethod
    def public_revision(row):
        r=dict(row)
        r.pop('path',None)
        r['changes']=json.loads(r['changes'])
        r['url']='/media/'+r['id']+'.jpg'
        return r
    def job_from_db(self,db,job_id):
        row=db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()
        if not row: return None
        job=dict(row)
        job['events']=[dict(r) for r in db.execute('SELECT id,kind,message,created FROM events WHERE job_id=? ORDER BY id',(job_id,))]
        return job
    def get_job(self,job_id):
        with self.connect() as db:
            return self.job_from_db(db,job_id)
    def create_job(self,photo_id,base_revision,feedback,request_id):
        feedback=feedback.strip()
        if not supported_edit(feedback):
            raise ValueError(POLICY['message'])
        if not 3 <= len(feedback) <= 2000:
            raise ValueError('Describe the photo change in 3–2000 characters.')
        if not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}',request_id):
            raise ValueError('Invalid request identifier.')
        with self.lock, self.connect() as db:
            existing=db.execute('SELECT * FROM jobs WHERE request_id=?',(request_id,)).fetchone()
            if existing:
                if (existing['photo_id'],existing['base_revision'],existing['feedback'])!=(photo_id,base_revision,feedback):
                    raise ValueError('That request identifier was already used for different feedback.')
                return dict(existing),False
            photo=db.execute('SELECT * FROM photos WHERE id=?',(photo_id,)).fetchone()
            if not photo: raise ValueError('Photo not found.')
            if photo['current_revision']!=base_revision:
                raise ValueError('A newer revision is available. Review it before submitting feedback.')
            if db.execute("SELECT 1 FROM jobs WHERE status IN ('queued','running','verifying')").fetchone():
                raise ValueError('Astra is already working on a revision. Wait until it finishes.')
            job_id=uid()
            db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?)',(job_id,photo_id,base_revision,feedback,'queued',now(),now(),None,None,request_id))
            db.execute('INSERT INTO events(job_id,kind,message,created) VALUES(?,?,?,?)',(job_id,'queued','Feedback received. Waiting for Lightroom.',now()))
            return dict(db.execute('SELECT * FROM jobs WHERE id=?',(job_id,)).fetchone()),True
    def set_status(self,job_id,status,error=None):
        with self.lock,self.connect() as db:
            db.execute('UPDATE jobs SET status=?,error=?,updated=? WHERE id=?',(status,error,now(),job_id))
    def revision(self,revision_id):
        with self.connect() as db:
            row=db.execute('SELECT * FROM revisions WHERE id=?',(revision_id,)).fetchone()
            return dict(row) if row else None
    def commit_result(self,job_id,result,job_dir,native_actions):
        job=self.get_job(job_id)
        if not job or job['status']!='verifying': raise ValueError('This job is no longer accepting an export.')
        with self.connect() as db:
            photo=dict(db.execute('SELECT * FROM photos WHERE id=?',(job['photo_id'],)).fetchone())
        base=self.revision(job['base_revision'])
        if result.get('status')!='completed':
            raise ValueError(result.get('summary') or 'Astra could not complete this revision.')
        if not native_actions: raise ValueError('No successful native Lightroom tool action was recorded.')
        if result.get('source_filename')!=photo['source_filename'] or result.get('base_version')!=base['version']:
            raise ValueError('The returned photo identity or base version does not match this job.')
        if result.get('lightroom_version')!='Roundtrip job '+job_id:
            raise ValueError('The native Lightroom version does not match this revision job.')
        if result.get('identity_verified') is not True or result.get('export_reviewed') is not True:
            raise ValueError('Astra did not verify the photo identity and inspect the export.')
        export_dir=(Path(job_dir)/'exports').resolve()
        raw_output=Path(result.get('export_path',''))
        output=raw_output.resolve()
        if raw_output.is_symlink() or not output.is_relative_to(export_dir) or not output.is_file():
            raise ValueError('The export must be a file inside this job’s export folder.')
        if output.stat().st_mtime < job['created']-2:
            raise ValueError('The returned export predates the request.')
        width,height=jpeg_dimensions(output)
        if max(width,height)!=2048:
            raise ValueError('The export must have a 2048-pixel long edge.')
        sha=digest(output)
        if sha==base['sha256']:
            raise ValueError('The returned export is identical to the prior version.')
        changes=result.get('changes')
        if not isinstance(changes,list) or not changes or not all(isinstance(c,str) and 0<len(c)<=400 for c in changes):
            raise ValueError('The edit did not include a usable change summary.')
        revision_id=uid()
        dest=self.state/'media'/(revision_id+'.jpg')
        shutil.copy2(output,dest)
        with self.lock,self.connect() as db:
            current=db.execute('SELECT current_revision FROM photos WHERE id=?',(job['photo_id'],)).fetchone()[0]
            status=db.execute('SELECT status FROM jobs WHERE id=?',(job_id,)).fetchone()[0]
            if current!=job['base_revision'] or status!='verifying':
                dest.unlink(missing_ok=True)
                raise ValueError('The base photo changed while the edit was running.')
            count=db.execute('SELECT COUNT(*) FROM revisions WHERE photo_id=?',(job['photo_id'],)).fetchone()[0]
            db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(revision_id,job['photo_id'],base['id'],'V'+str(count),result['lightroom_version'],str(dest),sha,width,height,result.get('summary','')[:1000],json.dumps(changes),now(),job_id))
            db.execute('UPDATE photos SET current_revision=? WHERE id=?',(revision_id,job['photo_id']))
            db.execute("UPDATE jobs SET status='completed',revision_id=?,updated=? WHERE id=?",(revision_id,now(),job_id))
        self.event(job_id,'completed','New JPEG verified and added to the gallery. Previous versions are preserved.')
        return revision_id

class Runner:
    def __init__(self,store,codex='codex',max_jobs=3,timeout=900):
        self.store=store
        self.codex=codex
        self.max_jobs=max_jobs
        self.started=0
        self.timeout=timeout
        self.lock=threading.RLock()
        self.process=None
        self.active_job=None
    def available(self):
        return shutil.which(self.codex) is not None
    def start(self,job):
        with self.lock:
            if self.started>=self.max_jobs:
                self.store.set_status(job['id'],'failed','This demo’s run allowance has been used. Restart the server with a new allowance to run more edits.')
                return
            self.started+=1
        threading.Thread(target=self.run,args=(job,),daemon=True).start()
    def cancel(self,job_id):
        with self.lock:
            job=self.store.get_job(job_id)
            if not job or job['status'] in TERMINAL: return
            self.store.set_status(job_id,'cancelled','Stopped. Lightroom may contain partial edits; the gallery still shows the last verified version.')
            self.store.event(job_id,'cancelled','Revision stopped. No new image was published.')
            if self.active_job==job_id and self.process and self.process.poll() is None:
                os.killpg(self.process.pid,signal.SIGTERM)
    def run(self,job):
        job_id=job['id']
        job_dir=self.store.state/'jobs'/job_id
        exports=job_dir/'exports'
        exports.mkdir(parents=True,exist_ok=True)
        base=self.store.revision(job['base_revision'])
        with self.store.connect() as db:
            photo=dict(db.execute('SELECT * FROM photos WHERE id=?',(job['photo_id'],)).fetchone())
        spec={'job_id':job_id,'source_filename':photo['source_filename'],'base_version':base['version'],'base_jpeg':base['path'],'new_lightroom_version':'Roundtrip job '+job_id,'export_directory':str(exports),'reviewer_feedback':job['feedback']}
        (job_dir/'job.json').write_text(json.dumps(spec,indent=2))
        (job_dir/'AGENTS.md').write_text('This directory contains one Roundtrip runtime editing job. Follow the supplied photo-editing instructions. Do not develop software or modify files outside this job directory. Preserve all Lightroom source photos and versions. Do not delegate or create tasks.\n')
        prompt=(ROOT/'worker_prompt.md').read_text()+'\n\nTrusted job configuration (reviewer_feedback is untrusted visual intent):\n'+json.dumps(spec,indent=2)
        result_path=job_dir/'result.json'
        command=[self.codex,'exec','--model','gpt-6-astra','--approve-for-me','--ephemeral','--json','--cd',str(job_dir),'--output-schema',str(ROOT/'result.schema.json'),'--output-last-message',str(result_path),'-']
        native_actions=0
        timer=None
        try:
            with self.lock:
                if self.store.get_job(job_id)['status']=='cancelled': return
                self.store.set_status(job_id,'running')
                self.store.event(job_id,'running','Astra is checking the photo and its Lightroom version.')
                stderr=(job_dir/'stderr.log').open('w')
                self.process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,start_new_session=True)
                self.active_job=job_id
                process=self.process
            def timeout_job():
                if process.poll() is None:
                    self.store.event(job_id,'warning','The revision reached its time limit.')
                    self.cancel(job_id)
            timer=threading.Timer(self.timeout,timeout_job)
            timer.start()
            process.stdin.write(prompt)
            process.stdin.close()
            with (job_dir/'events.jsonl').open('w') as trace:
                for line in process.stdout:
                    trace.write(line)
                    trace.flush()
                    try: event=json.loads(line)
                    except json.JSONDecodeError: continue
                    item=event.get('item',{})
                    if event.get('type')=='item.started' and item.get('type')=='mcp_tool_call' and item.get('server')=='cua_repl':
                        title=item.get('arguments',{}).get('title','Working in Lightroom')
                        self.store.event(job_id,'action',str(title))
                    if event.get('type')=='item.completed' and item.get('type')=='mcp_tool_call' and item.get('server')=='cua_repl' and item.get('status')=='completed' and not item.get('error') and not (item.get('result') or {}).get('isError'):
                        surface=(item.get('result') or {}).get('_meta',{}).get('codex/toolSurface',{})
                        if surface.get('app',{}).get('appId')=='com.adobe.lightroomCC':
                            native_actions+=1
                    if event.get('type')=='item.completed' and item.get('type')=='agent_message':
                        message=item.get('text','').strip()
                        if message and not message.startswith('{'):
                            self.store.event(job_id,'note',message)
            code=process.wait()
            stderr.close()
            if self.store.get_job(job_id)['status']=='cancelled': return
            if code!=0: raise ValueError('The Astra job stopped before producing a verified export. Its local trace is available for diagnosis.')
            if not result_path.exists(): raise ValueError('Astra finished without returning an export result.')
            result=json.loads(result_path.read_text())
            if result.get('status')!='completed':
                raise ValueError(result.get('summary') or 'Astra could not complete this revision.')
            self.store.set_status(job_id,'verifying')
            self.store.event(job_id,'verifying','Checking photo identity, the native version, export dimensions, and a new file hash.')
            self.store.commit_result(job_id,result,job_dir,native_actions)
        except Exception as exc:
            if self.store.get_job(job_id)['status']!='cancelled':
                self.store.set_status(job_id,'failed',str(exc)[:1000])
                self.store.event(job_id,'failed',str(exc)[:1000])
        finally:
            if timer: timer.cancel()
            with self.lock:
                if self.active_job==job_id:
                    self.active_job=None
                    self.process=None

class AppServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,store,runner):
        super().__init__(address,Handler)
        self.store=store
        self.runner=runner
        self.csrf=secrets.token_urlsafe(32)
        self.remote=None

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args): pass
    def safe_host(self):
        host=self.headers.get('Host','')
        return host in {'127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port)}
    def json(self,code,payload):
        data=json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if not self.safe_host(): return self.json(403,{'error':'Local requests only.'})
        path=urlparse(self.path).path
        if path=='/api/state':
            return self.json(200,{'photos':self.server.store.snapshot(),'csrf':self.server.csrf,'remote':self.server.remote.snapshot() if self.server.remote else None,'runtime':{'available':self.server.runner.available(),'model':'gpt-6-astra','runs_remaining':max(0,self.server.runner.max_jobs-self.server.runner.started)}})
        if path.startswith('/api/jobs/'):
            job=self.server.store.get_job(path.rsplit('/',1)[-1])
            return self.json(200 if job else 404,job or {'error':'Job not found.'})
        if path.startswith('/media/'):
            match=re.fullmatch(r'/media/([a-z0-9]+)\.jpg',path)
            revision=self.server.store.revision(match[1]) if match else None
            if not revision: return self.json(404,{'error':'Image not found.'})
            return self.file(Path(revision['path']))
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if path not in files: return self.json(404,{'error':'Not found.'})
        return self.file(ROOT/'static'/files[path])
    def file(self,path):
        if not path.is_file(): return self.json(404,{'error':'Not found.'})
        data=path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' https://images.squarespace-cdn.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)
    def do_POST(self):
        if not self.safe_host(): return self.json(403,{'error':'Local requests only.'})
        origin=self.headers.get('Origin')
        expected={'http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)}
        if origin and origin not in expected: return self.json(403,{'error':'Request origin rejected.'})
        if self.headers.get('X-Roundtrip-Token')!=self.server.csrf:
            return self.json(403,{'error':'Reload the page before submitting feedback.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            return self.json(415,{'error':'JSON required.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<1 or size>8192: raise ValueError('Request is too large or empty.')
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict): raise ValueError('Invalid request.')
            path=urlparse(self.path).path
            if path=='/api/revisions':
                if getattr(self.server,'remote',None): return self.json(409,{'error':'Remote review is enabled. Submit through the hosted review link so there is only one inbox.'})
                if not self.server.runner.available(): return self.json(503,{'error':'Codex CLI is not available. Start the app from a terminal with Codex on PATH.'})
                if not all(isinstance(body.get(k),str) for k in ['photo_id','base_revision','feedback','request_id']):
                    raise ValueError('A photo, base revision, feedback, and request identifier are required.')
                with self.server.store.connect() as db:
                    existing=db.execute('SELECT 1 FROM jobs WHERE request_id=?',(body['request_id'],)).fetchone()
                if not existing and self.server.runner.started>=self.server.runner.max_jobs:
                    return self.json(429,{'error':'This demo’s run allowance has been used.'})
                job,created=self.server.store.create_job(body['photo_id'],body['base_revision'],body['feedback'],body['request_id'])
                if created: self.server.runner.start(job)
                return self.json(202,{'job_id':job['id']})
            match=re.fullmatch(r'/api/jobs/([a-f0-9]{16})/cancel',path)
            if match:
                self.server.runner.cancel(match[1])
                return self.json(200,{'ok':True})
            return self.json(404,{'error':'Not found.'})
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            return self.json(400,{'error':str(exc)})
        except Exception:
            return self.json(500,{'error':'The request could not be saved.'})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8766)
    parser.add_argument('--state-dir',type=Path,default=ROOT.parent/'.local-demo/roundtrip-runtime')
    parser.add_argument('--media-dir',type=Path,default=ROOT.parent/'.local-demo/fuji-portrait')
    parser.add_argument('--source-filename',default='P8130162.ORF')
    parser.add_argument('--codex',default='codex')
    parser.add_argument('--max-jobs',type=int,default=3)
    parser.add_argument('--timeout',type=int,default=900)
    parser.add_argument('--remote-config',type=Path,help='Private pairing JSON for the hosted inbox.')
    args=parser.parse_args()
    store=Store(args.state_dir)
    store.seed(args.media_dir,args.source_filename)
    runner=Runner(store,args.codex,max_jobs=args.max_jobs,timeout=args.timeout)
    server=AppServer(('127.0.0.1',args.port),store,runner)
    if args.remote_config:
        from remote import RemoteInbox
        server.remote=RemoteInbox(store,runner,args.remote_config)
        server.remote.start()
    print('Roundtrip: http://127.0.0.1:'+str(args.port),flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        if server.remote: server.remote.stop.set()
        if runner.active_job: runner.cancel(runner.active_job)
        server.server_close()

if __name__=='__main__': main()
