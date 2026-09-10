"""Read-only audience projection plus bounded listener requests.

Run on a separate port. Never tunnel the workstation server itself.
"""
import json
import re
import secrets
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / '.b2b'
WEB = ROOT / 'web'
ASSETS = {'watch.js', 'watch.css', 'booth-scene.js', 'vendor/hls.min.js',
          'vendor/three.module.min.js', 'vendor/three.core.min.js', 'vendor/GLTFLoader.js',
          'vendor/BufferGeometryUtils.js', 'vendor/RoomEnvironment.js', 'scene/b2b-booth.glb'}
RECORD_FIELDS = ('id', 'name', 'title', 'artist', 'status', 'reason', 'queued', 'createdAt', 'updatedAt')
TRACK_FIELDS = ('id', 'title', 'artist', 'playing', 'position', 'duration', 'level', 'low', 'fade', 'bpm')


def listener_config(data=DATA):
    data.mkdir(parents=True, exist_ok=True)
    path = data / 'listener.json'
    if path.exists():
        config = json.loads(path.read_text())
        if re.fullmatch(r'[A-Za-z0-9_-]{32,100}', config.get('token', '')):
            return config
    config = {'token': secrets.token_urlsafe(32)}
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    return config


def workstation(path, body=None):
    request = urllib.request.Request('http://127.0.0.1:8779' + path,
                                      data=json.dumps(body).encode() if body is not None else None,
                                      headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.read(), response.headers.get('Content-Type', 'application/json')
    except urllib.error.HTTPError as error:
        # Preserve the bounded form-validation message, never an upstream traceback.
        raise HTTPException(error.code if error.code in (400, 404, 409, 422, 429) else 503,
                            'The request could not be accepted. Check the link or try again shortly.') from error
    except (OSError, TimeoutError) as error:
        raise HTTPException(503, 'The DJ workstation is temporarily offline.') from error


class SongRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    name: str = Field(default='Listener', max_length=80)


def create_app(data=DATA, proxy=workstation):
    app = FastAPI(title='b2b live', docs_url=None, redoc_url=None, openapi_url=None)
    token = listener_config(data)['token']

    @app.middleware('http')
    async def response_headers(request: Request, call_next):
        if request.method == 'POST':
            length = request.headers.get('content-length', '0')
            if not length.isdigit() or int(length) > 8192:
                return JSONResponse({'detail': 'Request too large.'}, status_code=413)
            origin = request.headers.get('origin')
            if origin:
                # Cloudflare terminates TLS; forwarded scheme may differ from request.url.
                from urllib.parse import urlsplit
                if urlsplit(origin).netloc != request.headers.get('host'):
                    return JSONResponse({'detail': 'Use the request form on this page.'}, status_code=403)
        response = await call_next(request)
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        response.headers['Cache-Control'] = 'no-store'
        return response

    def authorize(candidate):
        if not secrets.compare_digest(candidate, token):
            raise HTTPException(404, 'Session not found.')

    def safe_track(track):
        result = {k: track[k] for k in TRACK_FIELDS if k in track}
        if re.fullmatch(r'[A-Za-z0-9_-]{1,100}', str(result.get('id', ''))):
            result['artworkUrl'] = f'/s/{token}/api/art/{result["id"]}'
        return result

    @app.get('/s/{key}/')
    def watch(key: str):
        authorize(key)
        return HTMLResponse((WEB / 'watch.html').read_text())

    @app.get('/s/{key}/api/state')
    def state(key: str):
        authorize(key)
        raw, _ = proxy('/api/session/state')
        source = json.loads(raw)
        result = {k: source[k] for k in ('tempo', 'broadcasting', 'updatedAt') if k in source}
        result['decks'] = [safe_track(t) for t in source.get('decks', [])[:2]]
        result['crate'] = [safe_track(t) for t in source.get('crate', [])[:30]]
        transition = source.get('transition')
        result['transition'] = ({k: transition[k] for k in ('progress', 'bars', 'from', 'to') if k in transition}
                                if isinstance(transition, dict) else None)
        return result

    @app.get('/s/{key}/api/requests')
    def requests(key: str):
        authorize(key)
        raw, _ = proxy('/api/requests')
        source = json.loads(raw)
        rows = source.get('requests', []) if isinstance(source, dict) else source
        return {'requests': [{k: r[k] for k in RECORD_FIELDS if k in r} for r in rows[-50:]]}

    @app.post('/s/{key}/api/requests')
    def submit(key: str, body: SongRequest):
        authorize(key)
        raw, _ = proxy('/api/requests', body.model_dump())
        result = json.loads(raw)
        return {k: result[k] for k in RECORD_FIELDS if k in result}

    @app.get('/s/{key}/api/art/{ident}')
    def art(key: str, ident: str):
        authorize(key)
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', ident):
            raise HTTPException(404)
        raw, content_type = proxy('/api/art/' + ident)
        if content_type.split(';')[0] not in ('image/jpeg', 'image/png', 'image/webp'):
            raise HTTPException(404)
        return Response(raw, media_type=content_type)

    @app.get('/s/{key}/live/{filename}')
    def live(key: str, filename: str):
        authorize(key)
        if filename != 'index.m3u8' and not re.fullmatch(r'[A-Za-z0-9_-]+\.(?:ts|m4s|mp4)', filename):
            raise HTTPException(404)
        path = data / 'live' / filename
        if not path.is_file():
            raise HTTPException(404, 'The live audio has not started yet.')
        media_type = 'application/vnd.apple.mpegurl' if filename.endswith('.m3u8') else 'video/mp2t' if filename.endswith('.ts') else 'video/mp4'
        return FileResponse(path, media_type=media_type)

    @app.get('/{asset:path}')
    def asset(asset: str):
        if asset not in ASSETS or not (WEB / asset).is_file():
            raise HTTPException(404)
        return FileResponse(WEB / asset)

    return app


app = create_app()
