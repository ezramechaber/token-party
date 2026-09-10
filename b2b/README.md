# b2b (back 2 back)

A local two-deck DJ workstation for a small crate of 4/4 house tracks. Import MP3s, inspect beat/phrase estimates, suggest an order, audition an 8- or 16-bar overlap, and let Auto perform equal-power channel fades with a low-EQ handoff and measured loudness matching. Take over the same live controls at any time.

Built during the September 10, 2026 Astra hackathon. [Plan](docs/plan.md) · [Build and usage log](docs/build-log.md) · [Activity log](../research/activity-log.md).

## Run locally

Requires Python 3.11+ and FFmpeg (`ffmpeg` and `ffprobe` on PATH). On macOS, FFmpeg can be installed with `brew install ffmpeg`.

```sh
cd b2b
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn b2b.server:app --host 127.0.0.1 --port 8779
```

Open <http://127.0.0.1:8779>. Add files with **Add tracks** or drag/drop. Alternatively place files in `.b2b/imports/` and choose **Scan local imports**. Files, analysis and prepared audio stay under ignored `.b2b/`. The local service deliberately rejects other host names and cross-origin browser requests.

## YouTube audio import

Paste a single YouTube video URL into **Import from YouTube** in the crate, then choose **Import audio**. The local server uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download its audio, converts it with FFmpeg, and runs the same analysis as a file upload. Download and analysis status appear under the crate. Imports are private files under ignored `.b2b/`.

This feature requires FFmpeg and **Node.js 22+** (or Deno 2.3+), in addition to the Python dependencies. Current yt-dlp uses a JavaScript runtime for YouTube extraction. Single videos must fit the app's 20-second–15-minute and 150-MB bounds. Playlists are not imported. Restricted, unavailable, or login-only videos surface an error; the importer does not use browser cookies or attempt access bypasses. Use videos you are allowed to download.

## Mixing

1. Set a common tempo near your tracks' BPM. Manual decks permit at most ±8% adjustment; Auto uses a tighter ±4% limit. FFmpeg `atempo` prepares pitch-preserving stereo audio before playback.
2. Load tracks into A and B. Each deck shows its cover, title and playback state; “Not in mix” means the deck is playing but its level or crossfader is closed.
3. **Preview transition** jumps A near its planned outro and blends into B now. B continues after the preview. **Mix A into B** keeps A playing until the planned outro; the label reverses when B is the outgoing deck. The incoming deck always resets to its planned entry.
4. Whole-set controls live in the crate: **Let Astra DJ** chooses an order and handoffs, then starts from the first track. **Preview Astra’s plan** proposes the sequence without starting audio. Drag set-list handles (or use their arrow keys) to choose your own order; **Play my order** validates and plays it. During playback, upcoming tracks can move after validation, while played tracks and the prepared handoff stay locked. **Library** shows all imported files; rejected and held requests remain labeled there and are excluded from automatic set selection.
5. **Cancel automation** holds the current EQ/fader levels and cancels future handoffs. **Stop audio** stops both decks and clears effect tails. Space plays/pauses; it does not override focused buttons or form controls.

**Review grid / deck cue settings:** opens that track in the beat & phrase inspector with its marker form beside the waveform. An idle deck is used when needed; tracks outside the set's tempo range can be reviewed at their original tempo. Click the waveform or use arrow keys to position the cursor. **Play this view**, **Play from cursor**, and **Pause preview** let you hear and retain the point you're editing. Marker buttons copy the cursor into the intro, outro, beat-one or phrase marker; phrase starts snap to the nearest bar. Numeric edits appear as a draft on the waveform. **Save markers** rebuilds the map and reloads the deck; closing the form discards the draft. Pause playback before saving. Reanalysis failure leaves the previous grid intact.

**Effects:** each deck has an optional Effects drawer. Delay repeats every quarter, half or full beat. Flanger sweeps every two bars. Amount is deliberately bounded; Off preserves dry audio. Effects sit before the deck level and crossfader, so faded-out decks cannot leak echo into the master. Stop/seek clears stored tails; loading a new track resets effects to Off. They remain manual during automatic mixing. `/effects-check.html` renders deterministic offline checks for repeat timing, bypass, muted tails, clearing and modulation.

An 8-bar blend at 128 BPM lasts 15 seconds; 16 bars lasts 30. The default uses equal-power channel curves, low-shelf gain derived from those amplitude curves, and whole-track loudness matching toward −16 LUFS with peak headroom. This is an experimental DJ curve, not a guarantee of constant perceived bass. The original linear-amplitude/linear-dB combination remains available for comparison. Audio starts and ramps use the audio clock; waveform animation never determines beat timing.

## Mix maps and reactive art

Every track has a private JSON mix map with beat/phrase evidence, drum support, and a proposed musical arrival. The planner chooses a supported overlap that hands over near that arrival, then checks the actual tempo-prepared audio for local attack alignment. Download the map from the inspector; correct **Musical arrival** or **First real kick** through **Grid / cues**. These are editable estimates. [How the maps guide mixing](docs/mix-maps.md).

A separate generative-art strip responds to the playing audio spectrum. Song identity seeds its palette and form; bass, mids, and highs shape its movement and reflected light. It pauses with playback and respects reduced motion. The controls remain ordinary HTML. The earlier space-deck mockup is an archived exploration.

## Optional Astra planning

The audio workstation and rule-based planner work without a key. To enable the separate **Plan with Astra** option, set `OPENAI_API_KEY` in the server environment and restart. Do not paste a key into the app or commit it. `.env.example` documents the name; the application does not automatically load `.env`.

Astra receives only track metadata, feature summaries, valid transition edges and your set direction. It chooses an order, which is validated before use. Audio files are not uploaded to OpenAI. The integration targets `gpt-6-astra` via Responses with structured output. It has not been live-tested without a key. On failure, the existing playback is unchanged.

## Boundaries

- Constant-tempo 4/4 house; individual files 20 seconds–15 minutes, at most 150 MB each. Protected streaming downloads cannot be decoded.
- Kick events, spectral key estimates and phrase boundaries are heuristics; they need listening and correction. Meter is explicitly assumed. No stems or reliable vocal detector.
- The current waveform shows section markers and band activity, not a full spectrogram editor. Key estimates use harmonic separation and constant-Q chroma from three excerpts.
- Keep the browser awake for continuous Auto preloading. Audio already scheduled continues against the audio clock; subsequent handoffs require the application to remain active. A late preload stops automatic progression rather than scheduling a missed window.
- Tempo controls apply between playback runs; this is not a live time-stretching jog deck.
- Music is not included in the open-source repository. Use recordings you may download and play; separately clear any soundtrack used in a public demo. The tested local crate includes label-offered downloads and user-provided/purchased files, not redistributable fixtures.
- The Blender-built scene mirrors the real audio state. It illustrates gestures; it does not control the audio clock.

## Verify

```sh
.venv/bin/pytest -q
node --check web/app.js
```

Tests synthesize their own audio to check grid recovery, tempo preparation/pitch, transition durations and constrained ordering. They do not establish real-world musical quality. See the build log for measured validation and known issues.


## Record and compare

**Record audition** plays the loaded A/B transition and captures the actual master bus. It saves a WAV, a spectrogram and full-band/35–180 Hz RMS measurements locally. Open **Recorded mix comparisons** to replay the saved takes and inspect plots. Whole-track LUFS matching reduces mastering differences; section-level loudness and musical arrangement still matter. See [the measured comparison](docs/mix-diagnostics.md).

The separate **16-bar phrase anchor** in Grid / cues is an original-file timestamp on a bar boundary. A blank value uses the estimated grid origin. Outgoing overlaps align to its 8/16-bar boundaries. The planner checks two incoming bars after a handoff, preventing a basic transition from ending exactly where the incoming drums disappear.

## Local listener page

Start a second process from this folder:

```sh
.venv/bin/python -m uvicorn b2b.listener:app --host 127.0.0.1 --port 8780
```

Choose **Open listener view** in Requests. The local token is generated in ignored `.b2b/listener.json`; it is not committed. **Start broadcast** sends the actual master bus to a local FFmpeg encoder, producing a rolling HLS stream with a short delay. Listeners press **Listen live**. The scene follows delayed deck state approximately, rather than frame-accurately matching buffered audio. Keep the workstation tab awake.

Spotify links identify recordings already available to the DJ; they do not download Spotify audio. YouTube requests use the same bounded importer as the crate. Requests are assessed for tempo, cue support, energy and tonal fit, then revalidated against the live set tail before being appended. They never interrupt an armed handoff. Uncertain matches remain for review. In Requests, choose the matching crate recording and use **Confirm & check fit**. **Load B to audition** preserves the intended set context while you listen. **Accept musical fit** can approve an energy/key judgment after your audition; it cannot bypass grid, tempo, or phrase safeguards. **Retry link** retries interrupted checks; **Dismiss** removes a reservation and sends affected later requests back for review. A request is marked added only after the mixer incorporates it. The listener service exposes only audience state, artwork, requests and live audio, not the workstation's control API. This demo stays local; no public tunnel is running.


## Café scene and artwork

**Watch the set** opens the Blender-built human DJ in a warm walnut booth. The editable model and reproducible generator live in `scene/`; ordinary playback only needs its checked-in GLB. Loading a track animates its album sleeve from the crate to a deck. Covers appear in the crate too; click a cover for its local source/match record.

Artwork extraction is offline by default. Twelve current tracks supplied their own embedded covers. Two missing covers were matched to related releases and privately cached: [Nightcrawlers single](https://musicbrainz.org/release/91b66d95-58e5-4fbd-85d0-b7d4fe63a2b7) and [DJ Disciple Ian Carey remixes](https://music.apple.com/us/album/yes-ian-carey-dj-disciple-remixes-feat-s-u-z-y-single/1524504781). These are release-family matches, not a claim that the precise edition is known. No Discogs credentials were needed. `python -m b2b.artwork --help` documents explicit, serial batch fetching of reviewed cover matches; playback routes do not search the internet. Covers and provenance remain under ignored `.b2b/cache/`.


## Transition diagnostics

`python scripts/audit_transitions.py` measures the current rules plan against local source and prepared audio. See `docs/transition-audit.md` for the five-track audit and its limits. Every planned sequence, including manual orders and request additions, must leave at least eight seconds between an incoming handoff and that track's outgoing mix so the freed deck can prepare its next track. Runtime preparation can still fail; Auto then releases control while the current track continues.

For a deterministic Web Audio filter check, open `/audio-check.html`: this renders synthetic tones offline and checks all three EQ bands plus crossfade power. It does not play sound or stand in for listening to real transitions.
