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
2. Load A/B to listen. Use **GRID / CUES** to correct BPM, beat one, intro entry, intro/outro lengths and outro end. These are proposals until confirmed; four identical kicks cannot determine bar one.
3. Choose **Suggest order**. Incompatible tracks remain in the crate and are excluded from the automatic plan.
4. **Audition A → B** uses exactly the tracks loaded in A and B. It starts A two bars before the overlap, blends its ending with B’s intro for the selected 8 or 16 bars (falling back to 8 if required), then leaves B playing. Repeat the button to compare again. **Start Auto** builds a crate plan and plays from the opening cue.
5. **Take over** (or move a mixer control) cancels future automation and holds current EQ/fader values. **Stop all** stops both decks. Space plays/pauses a deck; Escape takes over.

**Beat & phrase inspector:** choose deck A or B, jump to **Intro**, **Outro**, or **Playhead**, and view 4, 8, or 16 bars. The slider and arrow buttons navigate the entire file. Tall numbered lines mark bars, short lines mark beats, orange dots mark detected kick candidates, and highlighted regions mark the proposed intro/outro. Click the detailed waveform to seek, or **Listen here · Solo** to hear the displayed section alone. The close-up uses the actual decoded stereo waveform; timestamps refer to the original file. Use **Grid / cues** to correct estimates.

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

Spotify links identify recordings already available to the DJ; they do not download Spotify audio. YouTube requests use the same bounded importer as the crate. Requests are assessed for tempo, cue support, energy and tonal fit, then revalidated against the live set tail before being appended. They never interrupt an armed handoff. Uncertain matches remain for review; no audio match is labeled **Needs audio**. The listener service exposes only audience state, artwork, requests and live audio, not the workstation's control API. This demo stays local; no public tunnel is running.


## Café scene and artwork

**Watch the set** opens the Blender-built human DJ in a warm walnut booth. The editable model and reproducible generator live in `scene/`; ordinary playback only needs its checked-in GLB. Loading a track animates its album sleeve from the crate to a deck. Covers appear in the crate too; click a cover for its local source/match record.

Artwork extraction is offline by default. Twelve current tracks supplied their own embedded covers. Two missing covers were matched to related releases and privately cached: [Nightcrawlers single](https://musicbrainz.org/release/91b66d95-58e5-4fbd-85d0-b7d4fe63a2b7) and [DJ Disciple Ian Carey remixes](https://music.apple.com/us/album/yes-ian-carey-dj-disciple-remixes-feat-s-u-z-y-single/1524504781). These are release-family matches, not a claim that the precise edition is known. No Discogs credentials were needed. `python -m b2b.artwork --help` documents explicit, serial batch fetching of reviewed cover matches; playback routes do not search the internet. Covers and provenance remain under ignored `.b2b/cache/`.
