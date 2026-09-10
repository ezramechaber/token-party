"""Single-video YouTube imports, kept inside the workstation's private crate."""
import json
import math
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from yt_dlp import YoutubeDL

MAX_BYTES = 150 * 1024 * 1024
MIN_SECONDS = 20
MAX_SECONDS = 15 * 60


class ImportError(ValueError):
    """A concise message suitable for the import job UI."""


def video_url(value: str) -> str:
    """Accept video links only; discard tracking, playlist and timestamp fields."""
    try:
        parts = urlsplit(value.strip())
        if parts.scheme not in ('https', 'http') or parts.username or parts.password or parts.port:
            raise ValueError()
        host = (parts.hostname or '').lower()
        if host in ('youtu.be', 'www.youtu.be'):
            ident = parts.path.removeprefix('/')
        elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'):
            if parts.path == '/watch':
                values = parse_qs(parts.query).get('v', [])
                ident = values[0] if len(values) == 1 else ''
            else:
                match = re.fullmatch(r'/(?:shorts|embed|live)/([\w-]{11})', parts.path)
                ident = match[1] if match else ''
        else:
            raise ValueError()
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', ident):
            raise ValueError()
        return f'https://www.youtube.com/watch?v={ident}'
    except ValueError as error:
        raise ImportError('Paste a YouTube video link, rather than a channel or playlist.') from error


def validate_info(info):
    if not isinstance(info, dict) or info.get('_type', 'video') != 'video' or info.get('entries') is not None:
        raise ImportError('Choose one YouTube video.')
    if info.get('is_live') or info.get('live_status') in ('is_live', 'is_upcoming', 'post_live'):
        raise ImportError('Live streams and upcoming videos cannot be imported.')
    duration = info.get('duration')
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or not MIN_SECONDS <= duration <= MAX_SECONDS:
        raise ImportError('Choose a video between 20 seconds and 15 minutes with a known duration.')
    if info.get('availability') in ('private', 'premium_only', 'subscriber_only', 'needs_auth'):
        raise ImportError('This video requires access or a purchase. Choose a publicly available video.')
    if info.get('has_drm'):
        raise ImportError('Protected videos cannot be imported.')
    if (info.get('filesize') or 0) > MAX_BYTES:
        raise ImportError('Limit: 150 MB per track.')


class QuietLogger:
    # Do not put signed media URLs or personal local paths in the console.
    def debug(self, message): pass
    def info(self, message): pass
    def warning(self, message): pass
    def error(self, message): pass


def download_audio(url: str, imports: Path, update) -> Path:
    """Download and validate audio, cleaning every partial file on failure."""
    url = video_url(url)
    imports.mkdir(parents=True, exist_ok=True)
    runtimes = {name: {} for name in ('deno', 'node') if shutil.which(name)}
    if not runtimes:
        raise ImportError('YouTube importing needs Node 22+ or Deno 2.3+ on PATH.')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ImportError('YouTube importing needs FFmpeg and ffprobe on PATH.')
    with tempfile.TemporaryDirectory(prefix='.youtube-', dir=imports.parent) as folder:
        stage = Path(folder)

        def progress(data):
            downloaded = data.get('downloaded_bytes') or 0
            total = data.get('total_bytes') or data.get('total_bytes_estimate') or 0
            if downloaded > MAX_BYTES or total > MAX_BYTES:
                raise ImportError('Limit: 150 MB per track.')
            # Some fragmented formats cannot report a total before completion.
            actual_size = sum(p.stat().st_size for p in stage.iterdir() if p.is_file())
            if actual_size > MAX_BYTES:
                raise ImportError('Limit: 150 MB per track.')
            title = (data.get('info_dict') or {}).get('title', 'YouTube audio')
            update(status='downloading', title=str(title)[:200],
                   **({'progress': min(99, int(downloaded / total * 100))} if total else {}))

        def match_filter(info, *, incomplete=False):
            if not incomplete:
                validate_info(info)

        options = {
            'format': 'bestaudio/best', 'noplaylist': True,
            'allowed_extractors': ['youtube'], 'outtmpl': str(stage / 'audio.%(ext)s'),
            'max_filesize': MAX_BYTES, 'match_filter': match_filter,
            'socket_timeout': 20, 'retries': 2, 'fragment_retries': 2,
            'concurrent_fragment_downloads': 1, 'continuedl': False,
            'js_runtimes': runtimes, 'remote_components': [],
            'cachedir': False, 'quiet': True, 'no_warnings': True, 'logger': QuietLogger(),
            'progress_hooks': [progress],
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
        }
        try:
            update(status='downloading', title='Reading YouTube video')
            with YoutubeDL(options) as downloader:
                info = downloader.extract_info(url, download=True)
            validate_info(info)
            output = stage / 'audio.mp3'
            if not output.is_file() or not 0 < output.stat().st_size <= MAX_BYTES:
                raise ImportError('No usable audio was downloaded (150 MB maximum).')
            probe = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(output)],
                check=True, capture_output=True, text=True, timeout=20,
            )
            duration = float(json.loads(probe.stdout)['format']['duration'])
            if not math.isfinite(duration) or not MIN_SECONDS <= duration <= MAX_SECONDS + .1:
                raise ImportError('Downloaded audio must be between 20 seconds and 15 minutes.')
            title = re.sub(r'[^\w .()-]', '_', str(info.get('title') or 'YouTube audio'))[:100].strip(' .')
            destination = imports / f'{title or "YouTube audio"} [{uuid.uuid4().hex[:12]}].mp3'
            source = {'sourceUrl': url, 'title': str(info.get('track') or info.get('title') or title)[:300],
                      'artist': str(info.get('artist') or info.get('creator') or info.get('uploader') or 'Unknown artist')[:200],
                      'sourceDescription': str(info.get('description') or '')[:3000],
                      'sourceLicense': str(info.get('license') or '')[:300]}
            destination.with_suffix('.source.json').write_text(json.dumps(source))
            output.replace(destination)
            return destination
        except ImportError:
            raise
        except Exception as error:
            raise ImportError('YouTube could not provide this audio. It may be unavailable, restricted, or temporarily blocked. Try another video or upload a file.') from error
