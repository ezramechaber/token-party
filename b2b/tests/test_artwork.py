import json
import pytest
from b2b import artwork


def test_cached_art_never_fetches(tmp_path,monkeypatch):
    track={'id':'abc','path':'missing.mp3'}
    (tmp_path/'abc-art.jpg').write_bytes(b'cached')
    monkeypatch.setattr(artwork.urllib.request,'build_opener',lambda *a:pytest.fail('No network on hot path'))
    assert artwork.locate_artwork(track,tmp_path)==tmp_path/'abc-art.jpg'


def test_embedded_provenance(tmp_path,monkeypatch):
    track={'id':'abc','path':'audio.mp3','title':'Song'}
    def jpeg(source,target):target.write_bytes(b'jpeg');return True
    monkeypatch.setattr(artwork,'_jpeg',jpeg)
    assert artwork.locate_artwork(track,tmp_path)
    assert json.loads((tmp_path/'abc-art.json').read_text())['method']=='embedded'


def test_missing_marker_prevents_repeated_decode(tmp_path,monkeypatch):
    (tmp_path/'abc-no-art').touch()
    monkeypatch.setattr(artwork,'_jpeg',lambda *a:pytest.fail('Repeated decode'))
    assert artwork.locate_artwork({'id':'abc','path':'audio.mp3'},tmp_path) is None


@pytest.mark.parametrize('url',['file:///etc/passwd','https://127.0.0.1/art.jpg','https://evil.archive.org.evil.test/a','https://user@coverartarchive.org/a','http://coverartarchive.org/a'])
def test_remote_source_allowlist(url):
    with pytest.raises(ValueError):artwork._image_url(url)


def test_reviewed_source_requires_evidence(tmp_path):
    with pytest.raises(ValueError):artwork.cache_reviewed_artwork({'id':'abc'},tmp_path,{'imageUrl':'https://coverartarchive.org/a'})
    with pytest.raises(ValueError):artwork.paths({'id':'../secret'},tmp_path)
