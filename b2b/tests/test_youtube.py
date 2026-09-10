from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from b2b import server, youtube

VIDEO = 'https://www.youtube.com/watch?v=BaW_jenozKc'


@pytest.mark.parametrize('url', [
    'https://example.com/watch?v=BaW_jenozKc',
    'https://youtube.com.evil.test/watch?v=BaW_jenozKc',
    'https://youtube.com@127.0.0.1/watch?v=BaW_jenozKc',
    'http://127.0.0.1/video', 'file:///tmp/song.mp3',
    'https://youtube.com/playlist?list=test', 'https://youtube.com/@channel',
    'https://youtu.be/bad', 'https://youtube.com:443/watch?v=BaW_jenozKc',
])
def test_rejects_non_video_urls(url):
    with pytest.raises(youtube.ImportError):youtube.video_url(url)


@pytest.mark.parametrize('url', [
    VIDEO + '&list=playlist&t=40', 'https://youtu.be/BaW_jenozKc?si=tracking',
    'https://m.youtube.com/shorts/BaW_jenozKc', 'https://youtube.com/embed/BaW_jenozKc',
])
def test_normalizes_one_video(url):
    assert youtube.video_url(url) == VIDEO


@pytest.mark.parametrize('info', [
    {'duration': 19}, {'duration': 901}, {'duration': None}, {'duration': float('nan')},
    {'duration': 120, 'is_live': True}, {'duration': 120, '_type': 'playlist'},
    {'duration': 120, 'availability': 'premium_only'}, {'duration': 120, 'has_drm': True},
    {'duration': 120, 'filesize': youtube.MAX_BYTES + 1},
])
def test_metadata_bounds(info):
    with pytest.raises(youtube.ImportError):youtube.validate_info(info)


def fake_downloader(monkeypatch, action):
    class Downloader:
        def __init__(self, options):self.options = options
        def __enter__(self):return self
        def __exit__(self, *args):return False
        def extract_info(self, url, download):
            assert url == VIDEO and download
            assert self.options['noplaylist'] and self.options['allowed_extractors'] == ['youtube']
            assert self.options['remote_components'] == []
            return action(self.options)
    monkeypatch.setattr(youtube, 'YoutubeDL', Downloader)
    monkeypatch.setattr(youtube.shutil, 'which', lambda name: '/usr/bin/' + name)


def test_download_success_and_progress(tmp_path, monkeypatch):
    def action(options):
        info = {'duration': 120, 'title': '../../House / track'}
        options['match_filter'](info, incomplete=False)
        Path(options['outtmpl'].replace('%(ext)s', 'mp3')).write_bytes(b'audio')
        options['progress_hooks'][0]({'downloaded_bytes': 5, 'total_bytes': 10, 'info_dict': info})
        return info
    fake_downloader(monkeypatch, action)
    monkeypatch.setattr(youtube.subprocess, 'run', lambda *a, **kw: SimpleNamespace(stdout='{"format":{"duration":"120"}}'))
    states = []
    imports = tmp_path / 'imports'
    path = youtube.download_audio(VIDEO, imports, lambda **state: states.append(state))
    assert path.parent == imports and path.suffix == '.mp3' and path.read_bytes() == b'audio'
    assert states[-1]['progress'] == 50
    assert list(tmp_path.iterdir()) == [imports]


@pytest.mark.parametrize('failure', ['network', 'oversize', 'duration'])
def test_failure_removes_partial_download(tmp_path, monkeypatch, failure):
    def action(options):
        Path(options['outtmpl'].replace('%(ext)s', 'mp3')).write_bytes(b'partial')
        if failure == 'network':raise RuntimeError('secret signed URL')
        if failure == 'oversize':options['progress_hooks'][0]({'downloaded_bytes': youtube.MAX_BYTES + 1})
        return {'duration': 120, 'title': 'track'}
    fake_downloader(monkeypatch, action)
    monkeypatch.setattr(youtube.subprocess, 'run', lambda *a, **kw: SimpleNamespace(stdout='{"format":{"duration":"950"}}'))
    with pytest.raises(youtube.ImportError) as error:
        youtube.download_audio(VIDEO, tmp_path / 'imports', lambda **state: None)
    assert 'secret' not in str(error.value)
    assert list((tmp_path / 'imports').iterdir()) == []
    assert not list(tmp_path.glob('.youtube-*'))


def test_endpoint_queues_analysis(monkeypatch, tmp_path):
    submissions = []
    monkeypatch.setattr(server, 'jobs', {})
    monkeypatch.setattr(server, 'workers', SimpleNamespace(submit=lambda *args: submissions.append(args)))
    monkeypatch.setattr(server, 'IMPORTS', tmp_path)
    result = server.youtube(server.YoutubeRequest(url=VIDEO))
    job = result['job']
    assert server.jobs[job]['status'] == 'queued'
    def download(url, imports, update):
        update(status='downloading', title='track', progress=50)
        path = imports / 'track.mp3';path.write_bytes(b'audio');return path
    def analyze(path, jid):
        assert server.jobs[jid]['status'] == 'analyzing'
        server.jobs[jid] = {'status': 'done', 'title': 'track', 'track': 'new-id'}
    monkeypatch.setattr(server, 'download_audio', download)
    monkeypatch.setattr(server, 'import_track', analyze)
    fn, url, jid = submissions[0];fn(url, jid)
    assert server.jobs[job]['track'] == 'new-id'


def test_analysis_failure_removes_import(monkeypatch, tmp_path):
    path = tmp_path / 'broken.mp3';path.write_bytes(b'bad')
    monkeypatch.setattr(server, 'jobs', {'job': {'status': 'queued'}})
    monkeypatch.setattr(server, 'download_audio', lambda *args: path)
    def fail(path, job):server.jobs[job] = {'status': 'error', 'error': 'bad audio'}
    monkeypatch.setattr(server, 'import_track', fail)
    server.import_youtube(VIDEO, 'job')
    assert server.jobs['job']['status'] == 'error' and not path.exists()


def test_invalid_endpoint_url_is_400():
    with pytest.raises(HTTPException) as error:
        server.youtube(server.YoutubeRequest(url='https://example.com'))
    assert error.value.status_code == 400
