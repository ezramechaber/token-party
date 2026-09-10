"""Durable listener requests; acceptance reserves a queue slot, never a deck.

Spotify identifies an existing recording. It is not an audio download source.
Network callbacks and crate ownership stay outside this module.
"""
import copy
import json
import math
import re
import threading
import time
import unicodedata
import urllib.parse
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .planner import edge
from .youtube import video_url

PENDING = {'pending', 'identifying', 'downloading', 'analyzing'}


def request_url(value):
    """Canonicalize only individual Spotify tracks or supported YouTube videos."""
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError('Paste a Spotify track or YouTube video link.')
    try:
        parts = urllib.parse.urlsplit(value.strip())
        if parts.scheme not in ('http', 'https') or parts.username or parts.password or parts.port:
            raise ValueError()
        if parts.hostname == 'open.spotify.com':
            match = re.fullmatch(r'/(?:intl-[a-z]{2}/)?track/([A-Za-z0-9]{22})/?', parts.path)
            if not match:
                raise ValueError()
            return 'spotify', 'https://open.spotify.com/track/' + match[1]
        return 'youtube', video_url(value)
    except ValueError as error:
        raise ValueError('Use one Spotify track or YouTube video; albums, playlists and short redirect links are not supported.') from error


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Spotify metadata is temporarily unavailable.')


def spotify_metadata(url):
    provider, canonical = request_url(url)
    if provider != 'spotify':
        raise ValueError('Expected a Spotify track.')
    endpoint = 'https://open.spotify.com/oembed?' + urllib.parse.urlencode({'url': canonical})
    request = urllib.request.Request(endpoint, headers={'Accept': 'application/json', 'User-Agent': 'b2b/0.1'})
    with urllib.request.build_opener(_NoRedirect()).open(request, timeout=12) as response:
        raw = response.read(65537)
    if len(raw) > 65536:
        raise ValueError('Spotify metadata response was too large.')
    data = json.loads(raw)
    title = str(data.get('title') or '').strip()[:300]
    if not title:
        raise ValueError('Spotify did not provide a track title.')
    # oEmbed may omit the artist. Never guess one from a title or provider name.
    artist = str(data.get('author_name') or '').strip()[:200]
    if artist.lower() == 'spotify':
        artist = ''
    return {'title': title, 'artist': artist}


def normalized(value):
    text = unicodedata.normalize('NFKD', str(value)).casefold()
    return ' '.join(re.findall(r'[^\W_]+', ''.join(c for c in text if not unicodedata.combining(c))))


def match_spotify(url, metadata, tracks):
    exact = [t for t in tracks if url in (t.get('spotifyUrl'), t.get('sourceUrl'))]
    if len(exact) == 1:
        return exact[0], []
    candidates = [t for t in tracks if normalized(t.get('title', '')) == normalized(metadata['title'])]
    artist = normalized(metadata.get('artist', ''))
    if artist:
        candidates = [t for t in candidates if normalized(t.get('artist', '')) == artist]
        if len(candidates) == 1:
            return candidates[0], []
    return None, [t['id'] for t in candidates]


def assess_fit(track, tracks, context, tail_id=None):
    """Evidence based fit gate. Uncertain musical matches need the DJ's review."""
    tempo, bars = context['tempo'], context['bars']
    if not track.get('ready') or (not track.get('reviewed') and track.get('beatConfidence', 0) <= .62):
        return {'status': 'review', 'reason': 'The beat grid or phrase markers need a DJ review.', 'reviewKind': 'grid'}
    bpm = track.get('bpm', 0)
    if not isinstance(bpm, (float, int)) or not math.isfinite(bpm) or bpm <= 0:
        return {'status': 'review', 'reason': 'A reliable tempo could not be measured.', 'reviewKind': 'grid'}
    if abs(tempo / bpm - 1) > .04:
        return {'status': 'rejected', 'reason': f'{bpm:g} BPM is outside the set’s ±4% tempo range at {tempo:g} BPM.'}
    tail = next((t for t in tracks if t['id'] == (tail_id or context.get('tailId'))), None)
    if tail is None:
        return {'status': 'review', 'reason': 'Choose the set’s final track so its transition can be checked.', 'reviewKind': 'tail'}
    if tail['id'] == track['id'] or track['id'] in context.get('crateIds', []):
        return {'status': 'rejected', 'reason': 'This recording is already in the planned set.'}
    if not tail.get('ready') or (not tail.get('reviewed') and tail.get('beatConfidence', 0) <= .62):
        return {'status': 'review', 'reason': 'The outgoing track’s grid needs a DJ review.', 'reviewKind': 'grid'}
    transition = edge(tail, track, tempo, bars)
    if not transition:
        return {'status': 'review', 'reason': 'No safe 8- or 16-bar handoff was found from the end of the set.', 'reviewKind': 'edge'}
    energy_delta = abs(float(tail.get('energy', 0)) - float(track.get('energy', 0)))
    if energy_delta > .4:
        return {'status': 'review', 'reason': 'Tempo and phrases fit, but the measured energy jump needs a DJ check.', 'transition': transition, 'reviewKind': 'energy'}
    a, b = tail.get('key', {}), track.get('key', {})
    tonal_uncertain = any(k.get('confidence') == 'uncertain' for k in (a, b))
    reason = f'{transition["bars"]}-bar handoff fits the tempo and phrase map.'
    if tonal_uncertain:
        reason += ' Key is uncertain; audition the overlap.'
    elif (b.get('root', 0) - a.get('root', 0)) % 12 not in (0, 5, 7):
        return {'status': 'review', 'reason': 'Tempo and phrases fit, but the estimated keys need a tonal audition.', 'transition': transition, 'reviewKind': 'key'}
    return {'status': 'accepted', 'reason': reason, 'transition': transition}


def _context(context):
    tempo, bars = context.get('tempo'), context.get('bars')
    if isinstance(tempo, bool) or not isinstance(tempo, (int, float)) or not 108 <= tempo <= 142 or bars not in (8, 16):
        raise ValueError('The set needs a tempo from 108–142 BPM and an 8- or 16-bar blend.')
    ids = context.get('crateIds', [])
    if not isinstance(ids, list) or len(ids) > 30 or any(not isinstance(i, str) or len(i) > 100 for i in ids):
        raise ValueError('The planned set must contain at most 30 track IDs.')
    return {'tempo': tempo, 'bars': bars, 'tailId': str(context.get('tailId') or '')[:100], 'crateIds': ids[:], 'direction': str(context.get('direction') or '')[:1000]}


class RequestManager:
    def __init__(self, data_dir, get_tracks, import_youtube, metadata_resolver=None, auto_process=True, assessor=None):
        self.path = Path(data_dir) / 'requests.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.get_tracks, self.import_youtube = get_tracks, import_youtube
        self.assessor = assessor
        self.resolve_metadata = metadata_resolver or spotify_metadata
        self.lock = threading.RLock()
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='listener-request') if auto_process else None
        self.records = json.loads(self.path.read_text()) if self.path.exists() else []
        for record in self.records:
            if record['status'] in PENDING:
                self._history(record, 'interrupted')
                record.update(status='review', reviewKind='interrupted', queued=False,
                              reason='Processing was interrupted. The DJ can retry this request.')
            elif record['status'] == 'accepted' and not record.get('queued'):
                self._history(record, 'delivery-migrated')
                record.update(status='added', reason='Added to the set.')
        self._save()

    @staticmethod
    def _public(record):
        return {k: copy.deepcopy(v) for k, v in record.items() if k not in ('context', 'attempt')}

    @staticmethod
    def _history(record, action):
        record.setdefault('history', []).append({'action': action, 'at': time.time(),
                                                **{k: copy.deepcopy(record[k]) for k in ('status', 'reason', 'trackId', 'queued') if k in record}})

    def _record(self, ident):
        record = next((r for r in self.records if r['id'] == ident), None)
        if record is None:
            raise ValueError('Request not found.')
        return record

    def _save(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.records, indent=2))
        temporary.replace(self.path)

    def _update(self, ident, attempt=None, **fields):
        with self.lock:
            record = self._record(ident)
            if attempt is not None and record.get('attempt', 0) != attempt:
                return self._public(record)
            if 'status' in fields and fields['status'] != record['status']:
                self._history(record, 'status-change')
            record.update(fields, updatedAt=time.time())
            self._save()
            return self._public(record)

    def list(self):
        with self.lock:
            return [self._public(r) for r in self.records]

    def _queued(self):
        return sorted((r for r in self.records if r['status'] == 'accepted' and r.get('queued')),
                      key=lambda r: (r.get('queuedAt', r['createdAt']), r['createdAt']))

    def queue_ids(self):
        with self.lock:
            return [r['trackId'] for r in self._queued()]

    def consume(self, track_id):
        """Mark delivery only once the mixer incorporated the track into its plan."""
        with self.lock:
            for record in self.records:
                if record.get('trackId') == track_id and record['status'] == 'accepted' and record.get('queued'):
                    self._history(record, 'added-to-set')
                    record.update(status='added', queued=False, reason='Added to the set.', updatedAt=time.time())
            self._save()

    def _pending_capacity(self):
        if sum(r['status'] in PENDING for r in self.records) >= 8:
            raise ValueError('Eight requests are being checked. Please wait before adding another.')
        now = time.time()
        # Count retries as work too, preventing a single record from bypassing the room limit.
        starts = sum(now - r['createdAt'] < 60 for r in self.records)
        starts += sum(h['action'] == 'retry' and now - h['at'] < 60 for r in self.records for h in r.get('history', []))
        if starts >= 10:
            raise ValueError('The room received ten requests this minute. Please wait a moment.')

    def submit(self, url, name, context):
        provider, canonical = request_url(url)
        context = _context(context)
        with self.lock:
            existing = next((r for r in reversed(self.records) if r['url'] == canonical), None)
            if existing:
                return {**self._public(existing), 'duplicate': True}
            self._pending_capacity()
            if len(self.records) >= 200:
                raise ValueError('This session has reached its 200-request limit.')
            record = {'id': uuid.uuid4().hex, 'url': canonical, 'provider': provider,
                      'name': str(name or 'Listener').strip()[:80], 'status': 'pending', 'reason': 'Waiting to check this request.',
                      'createdAt': time.time(), 'updatedAt': time.time(), 'context': context, 'queued': False,
                      'attempt': 0, 'history': []}
            self.records.append(record)
            self._save()
            result = self._public(record)
        if self.worker:
            self.worker.submit(self.process, record['id'])
        return result

    def retry(self, ident, context):
        context = _context(context)
        with self.lock:
            record = self._record(ident)
            if record['status'] in PENDING or record['status'] in ('accepted', 'added'):
                raise ValueError('This request is already processing, queued or added to the set.')
            self._pending_capacity()
            self._history(record, 'retry')
            for field in ('transition', 'reviewKind', 'candidateIds', 'trackId', 'queuedAt', 'approvedByDJ', 'progress'):
                record.pop(field, None)
            # Invalidate any older worker before scheduling the new one.
            record['attempt'] = record.get('attempt', 0) + 1
            result = self._update(ident, status='pending', reason='The DJ requested another check.',
                                  context=context, queued=False)
        if self.worker:
            self.worker.submit(self.process, ident)
        return result

    def dismiss(self, ident):
        with self.lock:
            record = self._record(ident)
            if record['status'] == 'added':
                raise ValueError('This request is already in the set; remove it using the set controls.')
            if record['status'] == 'dismissed':
                return self._public(record)
            queued = self._queued()
            after = queued[queued.index(record) + 1:] if record in queued else []
            self._history(record, 'dismiss')
            record['attempt'] = record.get('attempt', 0) + 1
            result = self._update(ident, status='dismissed', queued=False, reason='The DJ dismissed this request.')
            # Removing a reservation changes the predecessor of later requests.
            for following in after:
                self._update(following['id'], status='review', queued=False, reviewKind='queue-changed',
                             reason='An earlier request was removed. Recheck this handoff against the current set.')
            return result

    def _assessed(self, record, track, tracks, context, approve=False, judgment=None, queue_snapshot=None):
        queued = self.queue_ids()
        if track['id'] in queued:
            fit = {'status': 'rejected', 'reason': 'This recording is already in the request queue.'}
        else:
            fit = assess_fit(track, tracks, context, tail_id=queued[-1] if queued else None)
        if approve and fit['status'] == 'review' and fit.get('reviewKind') in ('energy', 'key') and fit.get('transition'):
            fit.update(status='accepted', reason='The DJ approved the musical fit; tempo, grid and phrase handoff pass.', approvedByDJ=True)
        if judgment is not None:
            fit['decisionMode'] = 'Astra'
            fit['astraReason'] = judgment['reason']
            fit['technicalReason'] = fit['reason']
            if queue_snapshot != queued:
                fit.update(status='review', reviewKind='queue-changed', reason='The queue changed while Astra was checking. Retry against the new handoff.')
            elif judgment['status'] != 'accepted':
                fit.update(status=judgment['status'], reviewKind='astra', reason='Astra: '+judgment['reason'])
            elif fit['status'] == 'accepted' or (fit.get('reviewKind') in ('energy','key') and fit.get('transition')):
                fit.update(status='accepted', reason='Astra: '+judgment['reason'])
            else:
                fit['reason'] += ' Astra likes the musical fit, but this technical check still needs attention.'
        else:
            fit.update(decisionMode='Rules', astraReason=None, technicalReason=fit['reason'])
        accepted = fit['status'] == 'accepted'
        # Clear evidence from an earlier failed attempt before storing fresh findings.
        fields = {'transition': None, 'reviewKind': None, 'approvedByDJ': False, **fit,
                  'context': context, 'trackId': track['id'], 'title': track.get('title', ''),
                  'artist': track.get('artist', ''), 'queued': accepted,
                  'queuedAt': time.time() if accepted else None}
        return self._update(record['id'], attempt=record.get('attempt', 0), **fields)

    def _judge(self, track, tracks, context, queued):
        if self.assessor is None:
            return None
        try:
            return self.assessor(track, tracks, {**context, 'tailId': queued[-1] if queued else context.get('tailId')})
        except Exception:
            return {'status':'review', 'reason':'Astra is unavailable. Retry its assessment before adding this request.'}

    def resolve(self, ident, track_id, context, approve=False):
        """Network judgment runs outside the lock; stale decisions never reserve a slot."""
        context = _context(context)
        tracks = self.get_tracks()
        track = next((t for t in tracks if t['id'] == track_id), None)
        if track is None:
            raise ValueError('Choose an existing analyzed crate track.')
        with self.lock:
            record = self._record(ident)
            if record['status'] in PENDING or record['status'] in ('accepted', 'added'):
                raise ValueError('This request is already processing, queued or added to the set.')
            self._history(record, 'approve' if approve else 'confirm-recording')
            record['attempt'] = attempt = record.get('attempt', 0) + 1
            queued = self.queue_ids()
            self._update(ident, status='analyzing', reason='Checking musical fit and the handoff.')
        judgment = self._judge(track, tracks, context, queued)
        with self.lock:
            record = self._record(ident)
            if record.get('attempt',0) != attempt:
                return self._public(record)
            return self._assessed(record, track, tracks, context, approve=approve, judgment=judgment, queue_snapshot=queued)

    def process(self, ident):
        with self.lock:
            record = copy.deepcopy(self._record(ident))
            if record['status'] != 'pending':
                return
            attempt = record.get('attempt', 0)
            self._update(ident, attempt=attempt, status='identifying', reason='Identifying the recording.')
        try:
            tracks = self.get_tracks()
            if record['provider'] == 'spotify':
                metadata = self.resolve_metadata(record['url'])
                track, candidates = match_spotify(record['url'], metadata, tracks)
                self._update(ident, attempt=attempt, title=str(metadata.get('title', ''))[:300], artist=str(metadata.get('artist', ''))[:200])
                if track is None:
                    return self._update(ident, attempt=attempt, status='review' if candidates else 'needs_audio', candidateIds=candidates,
                                        reviewKind='recording' if candidates else 'audio',
                                        reason='Possible crate match; the DJ must confirm the recording and version.' if candidates else 'Spotify identifies the track. Add an authorized audio file or YouTube source to assess it.')
            else:
                def update(**state):
                    allowed = {k: v for k, v in state.items() if k in ('title', 'progress')}
                    self._update(ident, attempt=attempt, status=state.get('status') if state.get('status') in PENDING else 'analyzing', **allowed)
                track = self.import_youtube(record['url'], update)
                if not isinstance(track, dict) or not track.get('id'):
                    raise ValueError('Import did not return an analyzed track.')
            tracks = self.get_tracks()
            with self.lock:
                if self._record(ident).get('attempt', 0) != attempt:
                    return self._public(self._record(ident))
                queued = self.queue_ids()
                self._update(ident, attempt=attempt, status='analyzing', reason='Astra is checking musical fit.' if self.assessor else 'Checking the handoff.')
            judgment = self._judge(track, tracks, record['context'], queued)
            with self.lock:
                if self._record(ident).get('attempt',0) != attempt:
                    return self._public(self._record(ident))
                return self._assessed(record, track, tracks, record['context'], judgment=judgment, queue_snapshot=queued)
        except Exception:
            return self._update(ident, attempt=attempt, status='error', reason='The source could not be checked. The DJ can retry or select an existing audio file.')

    def close(self):
        if self.worker:
            self.worker.shutdown(wait=False, cancel_futures=True)
