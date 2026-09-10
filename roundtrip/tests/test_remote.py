import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Store
from remote import RemoteInbox

class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); root=Path(self.temp.name)
        self.store=Store(root/'state')
        fixtures=Path(__file__).parent/'fixtures'
        media=root/'seed';media.mkdir()
        for n in ['original','v1','v2']:(media/(n+'.jpg')).write_bytes((fixtures/'gray.jpg').read_bytes())
        self.store.seed(media,'example.RAW')
        self.runner=Mock(started=0,max_jobs=2);self.runner.available.return_value=True
        config=root/'remote.json';config.write_text(json.dumps({'url':'https://example.com','worker_key':'w'*40,'review_key':'r'*40,'photo_id':'portrait'}))
        self.bridge=RemoteInbox(self.store,self.runner,config)
    def tearDown(self):self.temp.cleanup()
    def request(self,base='v2',status='requested'):
        return {'id':'abcdefgh12345678','feedback':'Reduce grain','base_revision':base,'status':status}
    def sync(self,remote):
        response=Mock();response.read.return_value=json.dumps({'request':remote}).encode()
        with patch('remote.urlopen') as fetch:
            fetch.return_value.__enter__.return_value=response;self.bridge.sync()
            return json.loads(fetch.call_args[0][0].data)
    def test_remote_feedback_launches_once_and_acknowledges(self):
        self.sync(self.request());self.sync(self.request())
        self.runner.start.assert_called_once();self.assertEqual(self.bridge.update['status'],'running')
        with self.store.connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],1)
    def test_stale_feedback_never_runs(self):
        self.sync(self.request('original'));self.runner.start.assert_not_called();self.assertEqual(self.bridge.update['status'],'stale')
    def test_busy_worker_keeps_request_in_cloud(self):
        self.store.create_job('portrait','v2','Keep skin natural','local-request')
        self.sync(self.request());self.runner.start.assert_not_called();self.assertIsNone(self.bridge.update)
    def test_spent_allowance_does_not_consume_request(self):
        self.runner.started=2
        payload=self.sync(self.request());self.assertFalse(payload['accepting']);self.runner.start.assert_not_called()
    def test_unknown_already_accepted_request_never_replays(self):
        self.sync(self.request(status='running'));self.runner.start.assert_not_called();self.assertEqual(self.bridge.update['status'],'failed')
    def test_no_raw_paths_or_feedback_history_sent_in_sync(self):
        payload=self.sync(None);self.assertEqual(set(payload),{'photo','accepting','update'});self.assertNotIn(str(self.store.state),json.dumps(payload))
    def test_failed_job_returns_generic_message_without_private_trace(self):
        self.sync(self.request());job=self.runner.start.call_args[0][0]
        self.store.set_status(job['id'],'failed','secret /Users/path')
        self.sync(self.request());self.assertEqual(self.bridge.update['status'],'failed');self.assertNotIn('secret',self.bridge.update['message'])
    def test_terminal_ack_is_retried_until_remote_accepts(self):
        self.bridge.update={'id':'x','status':'completed','message':'Ready'}
        with patch('remote.urlopen',side_effect=OSError('offline')):
            with self.assertRaises(OSError):self.bridge.sync()
        self.assertEqual(self.bridge.update['status'],'completed')
if __name__=='__main__':unittest.main()
