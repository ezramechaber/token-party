"""Private cover cache, with provenance; network fetching is an explicit batch step.

Run: python -m b2b.artwork --crate .b2b/crate.json --cache .b2b/cache
Optional --mapping JSON maps track IDs to reviewed image URLs and source credits.
No title-only automatic selection, and no artwork is committed with the app.
"""
import argparse
import json
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

MAX_IMAGE_BYTES = 10 * 1024 * 1024


def paths(track, cache):
    ident = track['id']
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', ident):
        raise ValueError('Invalid track ID.')
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    return cache / (ident + '-art.jpg'), cache / (ident + '-art.json'), cache / (ident + '-no-art')


def _save_provenance(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({**data, 'cachedAt': time.time(),
                                    'rights': 'Artwork remains the property of its rights holders; private cache, not licensed for redistribution.'}, indent=2))
    temporary.replace(path)


def _jpeg(source, target):
    temporary = target.with_name(target.stem + '.partial.jpg')
    try:
        result = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', str(source), '-map', '0:v:0',
                                 '-frames:v', '1', '-vf', 'scale=512:512:force_original_aspect_ratio=decrease',
                                 '-q:v', '3', str(temporary)], capture_output=True, timeout=20)
        if result.returncode or not temporary.is_file() or temporary.stat().st_size < 100:
            return False
        temporary.replace(target)
        return True
    finally:
        temporary.unlink(missing_ok=True)


def locate_artwork(track, cache):
    """Use cached or embedded art only. Safe to call from the local artwork route."""
    target, provenance, missing = paths(track, cache)
    if target.is_file():
        return target
    if missing.exists():
        return None
    if _jpeg(track['path'], target):
        _save_provenance(provenance, {'method': 'embedded', 'match': 'Attached image in this audio file',
                                     'trackId': track['id'], 'title': track.get('title', ''),
                                     'artist': track.get('artist', ''), 'source': 'Audio file embedded artwork'})
        return target
    missing.touch()
    return None


def _image_url(url):
    p = urlsplit(url)
    host = p.hostname or ''
    if p.scheme != 'https' or p.username or p.password or p.port or not (
        host == 'coverartarchive.org' or host == 'archive.org' or host.endswith('.archive.org')
        or host == 'mzstatic.com' or host.endswith('.mzstatic.com')):
        raise ValueError('Use a verified Cover Art Archive or Apple artwork image URL.')
    return url


class _ArtworkRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _image_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def cache_reviewed_artwork(track, cache, reviewed):
    """Fetch one manually verified release match; no network calls from playback."""
    target, provenance, missing = paths(track, cache)
    if reviewed.get('method') not in ('release-family', 'exact-release') or not reviewed.get('source') or not reviewed.get('match'):
        raise ValueError('Record the source, matching evidence and release-match confidence.')
    url = _image_url(reviewed['imageUrl'])
    request = urllib.request.Request(url, headers={'User-Agent': 'Back2Back/0.1 (local music artwork cache)'})
    with urllib.request.build_opener(_ArtworkRedirect()).open(request, timeout=25) as response:
        raw = response.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError('Artwork exceeds the 10 MB cache limit.')
    with tempfile.NamedTemporaryFile(suffix='.image', dir=target.parent) as source:
        source.write(raw); source.flush()
        if not _jpeg(source.name, target):
            raise ValueError('Downloaded file is not a readable image.')
    _save_provenance(provenance, {**reviewed, 'trackId': track['id'], 'title': track.get('title', ''), 'artist': track.get('artist', '')})
    missing.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--crate', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--mapping', type=Path)
    args = parser.parse_args()
    tracks = json.loads(args.crate.read_text())
    mapping = json.loads(args.mapping.read_text()) if args.mapping else {}
    for track in tracks.values():
        if track['id'] in mapping:
            image = cache_reviewed_artwork(track, args.cache, mapping[track['id']])
            time.sleep(1.1)  # A small cache fill is deliberately serial and gentle.
        else:
            image = locate_artwork(track, args.cache)
            if image:
                _, provenance, _ = paths(track, args.cache)
                if not provenance.exists():
                    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                            'stream_disposition=attached_pic', '-of', 'json', track['path']],
                                           capture_output=True, text=True, timeout=10)
                    embedded = any(s.get('disposition', {}).get('attached_pic')
                                   for s in json.loads(probe.stdout or '{}').get('streams', []))
                    _save_provenance(provenance, {'method': 'embedded' if embedded else 'existing-cache',
                                                'match': 'Attached image verified with ffprobe in this audio file' if embedded else 'Previously cached image; original source is unknown',
                                                'trackId': track['id'], 'title': track.get('title', ''), 'artist': track.get('artist', ''),
                                                'source': 'Audio file embedded artwork' if embedded else 'Existing local cache'})
        print(track['id'], 'cached' if image else 'missing')


if __name__ == '__main__':
    main()
