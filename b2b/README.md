# b2b (back 2 back)

A local two-deck DJ workstation for a small crate of 4/4 house tracks. Import MP3s, inspect beat/phrase estimates, suggest an order, audition an 8- or 16-bar overlap, and let Auto perform linear channel fades with a simultaneous low-EQ swap. Take over the same live controls at any time.

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

An 8-bar blend at 128 BPM lasts 15 seconds; 16 bars lasts 30. Volume ramps are linear amplitude. Low-shelf ramps are linear dB, from 0 to −24 dB and back, around 200 Hz. This deliberately simple combination can produce a midpoint dip. Audio starts and ramps use the audio clock; waveform animation never determines beat timing.

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
- Next presentation experiment: a Blender-built 3D deck whose physical controls mirror the same audio-engine parameters.

## Verify

```sh
.venv/bin/pytest -q
node --check web/app.js
```

Tests synthesize their own audio to check grid recovery, tempo preparation/pitch, transition durations and constrained ordering. They do not establish real-world musical quality. See the build log for measured validation and known issues.
