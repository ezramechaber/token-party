# Back 2 Back — prototype plan

2026-09-10, 11:35 EDT. User-selected next project; planning only. Earlier Lightroom work remains a separate experiment. Implementation choices below are recommendations, not tested capabilities.

## Product and first scope

A two-deck DJ program that prepares a small crate, suggests a playable order, and performs phrase-aligned transitions. The human can take over the same controls Auto uses.

Confirmed: user-supplied MP3s; roughly ten tracks; four-on-the-floor house in 4/4; club arrangements with clean intros; tempo, meter, sound-pattern and key analysis; intro/outro lengths; matching 8- or 16-bar overlaps; linear volume transitions and linear low-EQ swaps; manual controls and Auto.

Recommended first boundary: constant-tempo tracks, one selected set tempo, two active decks, one transition style, desktop browser with local analysis service. Start with two tracks, then three, then ten. Defer streaming integrations, stems, scratching, effects, arbitrary meters, variable-tempo music, automatic looping, and hardware controllers.

## 1. Prepare the crate

Decode each MP3 once into canonical stereo PCM. Analyze a downsampled mono copy; play from the canonical audio or a prepared tempo-adjusted derivative. Keep original-sample coordinates and an explicit mapping for every rendered derivative, avoiding disagreement between independent MP3 decoders about leading delay. Hash content and cache by analysis version, tempo and render settings.

For each track, store:

- Duration, waveform peaks and source sample rate.
- BPM, beat timestamps, grid anchor, grid residuals and confidence.
- Meter status: `4/4 assumed`, `4/4 supported`, or `needs review`.
- Bar/downbeat candidates and confidence, separately from beat confidence.
- Per-beat low/mid/high energy and transient activity; probable kick events.
- Global key candidates and local intro/outro key evidence, including `unknown`.
- Structural boundaries and usable intro/outro regions in beats and seconds.
- Candidate 8/16-bar entry and exit windows, evidence and confidence.
- Playback trim/headroom and manual corrections with provenance.

Progress should appear track by track; one problematic file should not block the crate. Keep personal audio and generated PCM outside version control. Include rights-cleared or synthetic fixtures for reproducibility and the public demo.

## 2. Tempo, beats, bars and sounds

Use numerical audio features, with waveforms and spectrograms as inspection tools. A waveform peak alone does not establish that a kick occurred.

1. Compute spectral-flux onset envelopes in several frequency bands. Low-frequency transient candidates provide a kick proxy; higher bands help distinguish percussion changes. These are probable events, not instrument separation.
2. Estimate BPM with a house-biased search range, initially 115–135 BPM. Also compare half/double-time candidates; do not silently force every track into that range.
3. Fit a constant-tempo grid and check timing error in multiple sections, especially both proposed mixing windows. Small BPM errors accumulate over a long track.
4. Evaluate all four possible bar phases using recurring accents, bass/harmonic changes, fills and section boundaries. Equal-strength quarter-note kicks cannot determine beat one by themselves.
5. Treat 4/4 as the supported scope. Mark ambiguous meter or downbeat phase for review rather than claiming a general time-signature detector.
6. Provide tap BPM, half/double BPM, grid nudge, “this is beat one,” and draggable cue markers. Manual correction invalidates dependent windows and queued plans.

[librosa's beat tracker](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html) provides tempo and beat locations. Bar phase, meter validation and phrase detection require additional logic.

## 3. Key from spectral information

Use harmonic/percussive separation followed by a constant-Q chromagram. Chroma folds spectral energy into the twelve pitch classes; score that against major/minor key templates and compare evidence across tonal sections. [librosa provides the chroma representation](https://librosa.org/doc/0.11.0/generated/librosa.feature.chroma_cqt.html); template scoring and uncertainty handling are our implementation.

Store the best candidates and their score margin, not a fabricated probability. Distinguish global key from what is actually sounding in the proposed overlap. A drum-only intro can have insufficient tonal evidence even if the body has a clear key. Key changes and relative-major/minor ambiguity should remain visible.

Show conventional key plus optional Camelot notation. Prefer same key, neighboring fifths, or relative major/minor as starting heuristics. Harmonic compatibility is a preference, not a guarantee that a transition sounds good.

## 4. Intros, outros and phrases

The useful question is “where are 8 or 16 bars we can mix over?” Separate this from assigning an exact semantic label to every section.

- Aggregate kick activity, energy, harmonic content and spectral change by beat and bar.
- Search inward from both ends for stable beat grids and changes in arrangement.
- Propose boundaries on 4/8/16/32-bar structures, allowing deviations when the evidence disagrees. Report observed lengths without rounding an irregular intro into a fictional 16 bars.
- Prefer sparse, percussion-led entry/exit regions. Penalize silence, fades, sudden breakdowns and competing melodic content. Vocal detection is unproven in this basic feature set; use a manual “vocals here” tag initially.
- Generate 16-bar windows first; use 8 when both sides support eight clean bars. A four-bar intro can be recognized but is not eligible for the initial automatic overlap rule.
- Align both downbeats and musical endpoints. If B's full arrangement begins at bar 17, mix its bars 1–16 over A's selected final 16 usable bars. If B has a 32-bar intro, its last 16 intro bars can be the entry window when that phrase boundary is validated.
- End A before its unsuitable tail, allowing a short gain taper at zero to avoid discontinuities. Do not assume file end is a musical boundary.

Present candidate markers on a waveform with an audition button. Auto requires supported grids and windows, or explicit manual correction. Readiness thresholds must be calibrated on the actual crate.

## 5. Ordering the crate and Astra's role

First construct valid directed transitions A → B. Each edge contains exact windows, allowed bar count, tempo-render readiness, key evidence, energy change and confidence. Hard checks reject invalid durations, unsupported grids, missing audio and excessive tempo adjustment. Begin with a proposed ±3% tempo adjustment cap, tuned after listening.

Rank remaining transitions by timing/phrase quality first, then harmonic compatibility, energy continuity and repetition. Treat energy as a relative feature-based estimate with a human override; loudness alone is not musical energy. Choose a gentle energy rise as the default set shape, with start/end track locks and manual reorder.

Astra receives the feature summaries, candidate transitions, optional annotated plots and user direction. It selects an order and concrete transition IDs, requests closer analysis of ambiguous regions, and revises the unplayed set when the user changes a track or direction. Code validates its output against the candidate graph, enforces each track at most once, and checks the whole path before enabling Auto. If no complete path exists, show the playable subset and the blocked tracks; never invent a transition to fill the order.

Expose a compact reason beside the next transition: “16 clean bars; compatible key; modest energy lift.” This is a proposed explanation format, not an analysis result.

The [official Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra) lists text/image input, function calling and structured outputs, but no audio input. Astra will reason over tool-produced audio evidence; it will not be described as directly listening to MP3s. Keep its API key in the local service.

Plan at least one track ahead. Once a transition is armed, lock it against asynchronous replanning; a versioned plan prevents stale results from taking control. A timeout leaves the last validated plan running. If no plan is ready, finish the current track and stop cleanly. The runtime demo should show an actual Astra-driven change in song choice or mix point, beyond an explanation of a deterministic playlist.

## 6. Playback, tempo and the transition

Recommended initial engine: Web Audio with two prepared buffers, per-deck trim → low shelf EQ → channel gain → master gain/meter. Use the audio context clock to schedule starts and ramps; animation frames update the display only. Load/decode current and next tracks, then release completed buffers instead of keeping ten full stereo tracks in memory.

Use one set tempo initially. Choose it to cover as much of the crate as possible within the tempo cap. Prepare pitch-preserving audio before arming a transition and retain the transformed cue mapping. [librosa time stretching](https://librosa.org/doc/0.11.0/generated/librosa.effects.time_stretch.html) is an available prototype path, but preparation latency and drum-transient quality need an early listening gate. This is not a claim of production DJ stretch quality.

Do not silently use playback-rate changes as key lock: [Web Audio playbackRate resamples audio](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode/playbackRate), changing pitch as well as speed. If pitch-preserving preparation fails its gate, narrow to near-equal-BPM tracks or explicitly use a pitch-changing mode and score actual transposed pitches, including fractional-semitone offsets. Do not retain original key labels as evidence for harmonic compatibility after such a change.

For N bars of 4/4 at set tempo M, transition duration is `T = N × 4 × 60 / M`. At 128 BPM: 8 bars = 15 seconds; 16 bars = 30 seconds. Both tracks cover N bars during the same T seconds after tempo preparation.

Let `p = elapsed / T`, clamped to [0,1]. Default automation:

| Parameter | Start | End | Curve |
| --- | ---: | ---: | --- |
| A channel gain | 1 | 0 | `1 − p` |
| B channel gain | 0 | 1 | `p` |
| A low shelf | 0 dB | −24 dB | `−24p` dB |
| B low shelf | −24 dB | 0 dB | `−24(1 − p)` dB |

Use an initial low shelf around 200 Hz; audition and tune the frequency/cut depth on real tracks. “Linear low EQ” here means linear movement in dB; this is distinct from the channel gains' linear amplitude ramps. A shelf attenuates bass, not a true isolated bass stem or complete kill.

This literal implementation may dip in loudness and bass at the midpoint. Preserve the requested linear curves for v1, audition the result, and only change that behavior deliberately. Apply static track trims and master headroom; check the rendered transition for clipping and audible pumping. [AudioParam ramps](https://developer.mozilla.org/en-US/docs/Web/API/AudioParam/linearRampToValueAtTime) can schedule these changes against audio time.

Illustrative alignment, assuming a validated A outro and B intro:

```text
                 Transition begins                  Transition ends
A                Outro bars 1–16                    Muted/stopped
B                Intro bars 1–16                    Main section starts
Channel gains    A 100% → 0%   /   B 0% → 100%
Low EQ           A normal → cut / B cut → normal
```

## 7. Controls and Auto behavior

- Crate: title, BPM, key, intro/outro bars, readiness, suggested position; reorder and start/end locks.
- Two decks: waveform with beat/bar markers, current position, entry/exit regions, play/pause, cue, sync, gain and low EQ.
- Center: crossfader, master meter, 8/16-bar selector, next-track choice, transition preview, Auto toggle and Take Over.
- Auto: select validated plan → preload → arm → play overlap → complete handoff → prepare the next deck.
- Turning Auto off cancels future scheduled transitions and holds current gains/EQ without a jump. Take Over cancels remaining ramps at their interpolated current values, exposes manual control and invalidates stale plans. Stop uses a short taper. Resume and seek recreate sources against a new shared time anchor.
- “Mix next” means the next valid phrase-aligned window, not an immediate unsynchronized launch. If none remains, show that explicitly.

## 8. Implementation shape and build order

Proposed architecture: TypeScript browser UI + Web Audio, local Python service with librosa/NumPy/SciPy, JSON analysis/plan cache and prepared audio files. The first milestone must verify MP3 decoding with the selected local decoder. Dependencies and exact versions are to be pinned during implementation. [librosa uses an ISC license](https://github.com/librosa/librosa/blob/main/LICENSE.md); preserve notices and check the full selected dependency/decoder chain before release. Essentia is a viable alternative but [uses AGPLv3 or a proprietary license](https://essentia.upf.edu/documentation.html); do not add it casually while the project's licensing choice is unsettled.

Planning budget from approximately 11:35 a.m. EDT; target feature freeze at 4:30 p.m., leaving an hour before the event submission deadline. Estimates, not measured timings:

| Budget | Deliverable and exit gate |
| --- | --- |
| 45 min | Two MP3s decoded; grids, bar-one markers and one 8-bar mix verified by ear. Benchmark pitch-preserving render early. |
| 60 min | Two-deck playback, synchronized start, scheduled volume/EQ ramps, manual takeover. Synthetic click tracks align; real transition has no obvious drift. |
| 60 min | Per-track features, key candidates, intro/outro windows and editable markers. Two real tracks inspected; ambiguous results stay visible. |
| 60 min | Small crate, Astra order/transition selection, validation, preload and three-track Auto sequence. A user change revises future playback. |
| 65 min | Expand toward ten tracks, audition, handle failures, document setup and polish the demo. Reduce crate size if reliability is not there. |
| Final 60 min | Freeze, record the one-minute video, verify public assets/repository and submit by 5:30 p.m. |

First acceptance gate: one phrase-aligned transition that sounds right. Do this before broad crate analysis or elaborate interface work.

## Verification and demo

- Synthetic fixtures with known BPM, downbeat offset, leading silence and 8/16-bar structure. Proposed timing target: ≤10 ms relative beat error across an entire prepared overlap on fixtures; listen to real tracks as a separate quality gate.
- Key checks with known tonal fixtures plus human assessment of actual club tracks; test `unknown` for percussion-only input. Synthetic success does not establish real-world accuracy.
- Verify cue transformation after tempo preparation, 8/16-bar durations, volume/EQ endpoints, finite samples, headroom and no duplicated/skipped handoff.
- Exercise invalid MP3, low-confidence grid, missing next buffer, model timeout, stale plan and manual takeover during a ramp. A suspended audio context requires resumption/re-anchoring, not a wall-clock catch-up jump.
- Run a complete three-track sequence; add ten-track coverage if time allows. Record actual analysis/render/model latency.
- One-minute demo: import a prepared small crate; show grounded cue markers; ask for an order; audition an 8-bar transition; change the next track or desired energy; show Astra revise the future plan and execute the resulting transition. Pre-analysis/cached results must be labeled if used. Preserve timestamped development and runtime evidence without raw personal audio or secrets.

## Decisions and remaining inputs

Selected direction: Back 2 Back. Proposed technical approach: measured audio features + Astra set planning + deterministic audio scheduling. Rejected for first scope: screenshot-only BPM/key estimation, universal meter detection, full instrument transcription, model-timed fader changes, and silent pitch changes presented as key lock.

Needed before the first audible prototype: two or three representative club MP3s and a human listen-through of their first beat and usable intro/outro. Later inputs: complete crate, preferred opener/closer or energy arc, and final deployment/license decisions. No audio analyzed, code implemented, model runtime called, or musical quality measured in this planning session.
