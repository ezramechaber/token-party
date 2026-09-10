import concurrent.futures
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Store, Runner, jpeg_dimensions

FIXTURES=Path(__file__).parent/'fixtures'

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        media=self.root/'seed'
        media.mkdir()
        for name in ['original','v1','v2']:
            shutil.copy2(FIXTURES/'gray.jpg',media/(name+'.jpg'))
        self.store=Store(self.root/'state')
        self.store.seed(media,'test.ORF')
    def tearDown(self): self.tmp.cleanup()
    def job(self,feedback='Brighten the face',request='request-0001'):
        return self.store.create_job('portrait','v2',feedback,request)[0]
    def result(self,job):
        directory=self.store.state/'jobs'/job['id']
        (directory/'exports').mkdir(parents=True)
        path=directory/'exports'/'export.jpg'
        shutil.copy(FIXTURES/'white.jpg',path)
        self.store.set_status(job['id'],'verifying')
        return directory,{'status':'completed','source_filename':'test.ORF','base_version':'Roundtrip 02 - Subject first','lightroom_version':'Roundtrip job '+job['id'],'export_path':str(path),'summary':'Face brightened','changes':['Subject exposure +0.2'],'identity_verified':True,'export_reviewed':True}
    def test_catalog_identity_and_global_job_lock(self):
        catalog=self.root/'catalog.json'
        catalog.write_text(json.dumps([{'id':'another-photo','title':'Another photo','source_filename':'other.ORF','jpeg':str(FIXTURES/'gray.jpg')}]))
        self.store.import_catalog(catalog)
        self.store.import_catalog(catalog)
        self.assertEqual(len(self.store.snapshot()),2)
        job,_=self.store.create_job('another-photo','another-photo-original','Crop to his hands only','request-another')
        self.assertEqual(job['photo_id'],'another-photo')
        with self.assertRaisesRegex(ValueError,'already working'):
            self.job()
        catalog.write_text(json.dumps([{'id':'another-photo','title':'Another photo','source_filename':'wrong.ORF','jpeg':str(FIXTURES/'gray.jpg')}]))
        with self.assertRaisesRegex(ValueError,'cannot be reassigned'):
            self.store.import_catalog(catalog)

    def test_seed_preserves_lineage(self):
        photo=self.store.snapshot()[0]
        self.assertEqual(photo['current_revision'],'v2')
        self.assertEqual([r['parent_id'] for r in photo['revisions']],[None,'original','v1'])
        self.assertNotIn('path',photo['revisions'][0])
    def test_repeated_submission_is_idempotent(self):
        one=self.job()
        two,created=self.store.create_job('portrait','v2','Brighten the face','request-0001')
        self.assertEqual(one['id'],two['id'])
        self.assertFalse(created)
    def test_idempotency_key_cannot_change_feedback(self):
        self.job()
        with self.assertRaisesRegex(ValueError,'different feedback'):
            self.job('Darken the background')
    def test_stale_revision_rejected(self):
        with self.assertRaisesRegex(ValueError,'newer revision'):
            self.store.create_job('portrait','v1','Make it warmer','request-stale')
    def test_only_one_job_can_claim_lightroom(self):
        def create(i):
            try: return self.job(request='request-'+str(i)+'abc')
            except ValueError: return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(create,range(6)))
        self.assertEqual(sum(r is not None for r in results),1)
    def test_export_creates_revision_without_overwriting_base(self):
        job=self.job();directory,result=self.result(job)
        previous=self.store.revision('v2')['sha256']
        new_id=self.store.commit_result(job['id'],result,directory,native_actions=2)
        self.assertEqual(self.store.get_job(job['id'])['status'],'completed')
        self.assertEqual(self.store.revision(new_id)['parent_id'],'v2')
        self.assertEqual(self.store.revision('v2')['sha256'],previous)
        self.assertEqual(self.store.snapshot()[0]['current_revision'],new_id)
    def test_wrong_source_never_publishes(self):
        job=self.job();directory,result=self.result(job);result['source_filename']='wrong.ORF'
        with self.assertRaisesRegex(ValueError,'identity'):
            self.store.commit_result(job['id'],result,directory,2)
        self.assertEqual(self.store.snapshot()[0]['current_revision'],'v2')
    def test_old_base_version_never_publishes(self):
        job=self.job();directory,result=self.result(job);result['base_version']='Original'
        with self.assertRaisesRegex(ValueError,'base version'):
            self.store.commit_result(job['id'],result,directory,2)
    def test_identical_export_rejected(self):
        job=self.job();directory,result=self.result(job)
        shutil.copy(FIXTURES/'gray.jpg',result['export_path'])
        with self.assertRaisesRegex(ValueError,'identical'):
            self.store.commit_result(job['id'],result,directory,2)
    def test_no_native_action_cannot_claim_success(self):
        job=self.job();directory,result=self.result(job)
        with self.assertRaisesRegex(ValueError,'native Lightroom'):
            self.store.commit_result(job['id'],result,directory,0)
    def test_unreviewed_export_rejected(self):
        job=self.job();directory,result=self.result(job);result['export_reviewed']=False
        with self.assertRaisesRegex(ValueError,'inspect the export'):
            self.store.commit_result(job['id'],result,directory,2)
    def test_export_outside_job_rejected(self):
        job=self.job();directory,result=self.result(job);result['export_path']=str(FIXTURES/'white.jpg')
        with self.assertRaisesRegex(ValueError,'inside this job'):
            self.store.commit_result(job['id'],result,directory,2)
    def test_symlink_export_rejected(self):
        job=self.job();directory,result=self.result(job)
        path=Path(result['export_path']);path.unlink();path.symlink_to(FIXTURES/'white.jpg')
        with self.assertRaisesRegex(ValueError,'inside this job'):
            self.store.commit_result(job['id'],result,directory,2)
    def test_cancelled_job_cannot_publish(self):
        job=self.job();directory,result=self.result(job)
        Runner(self.store).cancel(job['id'])
        with self.assertRaisesRegex(ValueError,'no longer accepting'):
            self.store.commit_result(job['id'],result,directory,2)
        self.assertEqual(self.store.snapshot()[0]['current_revision'],'v2')
    def test_restart_marks_interrupted_job_without_retry(self):
        job=self.job();self.store.set_status(job['id'],'running')
        reopened=Store(self.store.state)
        self.assertEqual(reopened.get_job(job['id'])['status'],'failed')
        self.assertEqual(reopened.snapshot()[0]['current_revision'],'v2')
    def test_truncated_jpeg_rejected(self):
        path=self.root/'bad.jpg';path.write_bytes((FIXTURES/'white.jpg').read_bytes()[:-10])
        with self.assertRaisesRegex(ValueError,'complete JPEG'):
            jpeg_dimensions(path)
    def test_dimensions(self): self.assertEqual(jpeg_dimensions(FIXTURES/'white.jpg'),(1536,2048))

if __name__=='__main__': unittest.main()

class HttpTests(unittest.TestCase):
    """Exercise HTTP parsing without opening a network listener or running Astra."""
    setUp = StoreTests.setUp
    tearDown = StoreTests.tearDown

    def request(self,method,path,body=None,host='127.0.0.1:8766',origin='http://127.0.0.1:8766',token='test-csrf',content_type='application/json'):
        import io
        from types import SimpleNamespace
        from server import Handler
        class Wire:
            def __init__(self,raw): self.raw=io.BytesIO(raw);self.output=bytearray()
            def makefile(self,*args): return self.raw
            def sendall(self,data): self.output.extend(data)
        self.started=[]
        runner=SimpleNamespace(available=lambda:True,started=0,max_jobs=3,start=lambda job:self.started.append(job),cancel=lambda job:None)
        app=SimpleNamespace(server_port=8766,csrf='test-csrf',store=self.store,runner=runner)
        payload=json.dumps(body or {}).encode()
        headers=[f'{method} {path} HTTP/1.0',f'Host: {host}',f'Origin: {origin}',f'X-Roundtrip-Token: {token}',f'Content-Type: {content_type}',f'Content-Length: {len(payload)}']
        wire=Wire(('\r\n'.join(headers)+'\r\n\r\n').encode()+payload)
        Handler(wire,('127.0.0.1',12345),app)
        head,data=bytes(wire.output).split(b'\r\n\r\n',1)
        return int(head.split()[1]),data
    def valid(self): return {'photo_id':'portrait','base_revision':'v2','feedback':'Brighten the face','request_id':'http-request-001'}
    def test_valid_post_starts_one_job(self):
        code,_=self.request('POST','/api/revisions',self.valid())
        self.assertEqual(code,202);self.assertEqual(len(self.started),1)
    def test_imported_photo_media_is_served(self):
        catalog=self.root/'catalog.json'
        catalog.write_text(json.dumps([{'id':'gallery-three','title':'Studio','source_filename':'studio.ORF','jpeg':str(FIXTURES/'gray.jpg')}]))
        self.store.import_catalog(catalog)
        code,data=self.request('GET','/media/gallery-three-original.jpg')
        self.assertEqual(code,200)
        self.assertEqual(data,(FIXTURES/'gray.jpg').read_bytes())
    def test_cross_origin_post_rejected(self):
        code,_=self.request('POST','/api/revisions',self.valid(),origin='https://evil.example')
        self.assertEqual(code,403);self.assertFalse(self.started)
    def test_dns_rebinding_host_rejected(self):
        code,_=self.request('GET','/api/state',host='evil.example:8766')
        self.assertEqual(code,403)
    def test_missing_session_token_rejected(self):
        code,_=self.request('POST','/api/revisions',self.valid(),token='')
        self.assertEqual(code,403);self.assertFalse(self.started)
    def test_form_post_rejected(self):
        code,_=self.request('POST','/api/revisions',self.valid(),content_type='application/x-www-form-urlencoded')
        self.assertEqual(code,415)
    def test_path_traversal_rejected(self):
        code,_=self.request('GET','/media/../../server.py')
        self.assertEqual(code,404)
    def test_runtime_trace_not_publicly_served(self):
        code,_=self.request('GET','/jobs/anything/events.jsonl')
        self.assertEqual(code,404)
