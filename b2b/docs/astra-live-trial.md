# Two-sided Astra: live local trial, September 10, 2026

Both roles use `gpt-6-astra` through the Responses API with structured outputs. The request curator judges musical fit; the DJ selects order and available 8/16-bar transition options. The deterministic engine validates tempo limits, phrase cues and preparation time. Audio stays local; the model receives metadata and measured song-map summaries, with confidence labels.

## Five new recordings

| Recording | Acquisition | Actual request result |
| --- | --- | --- |
| Roctakon — Summertime | Existing Bandcamp purchase | Review: plausible tempo/energy, but needs listening confirmation of style and sparse opening. |
| Freddy Musri — Don Juan | Label's free Tundra EP download | Accepted: minimal-house context and an executable handoff; queued. |
| Freddy Musri — Sunset at Paula’s | Label's free Tundra EP download | Musical fit accepted by Astra; held for beat-grid review by the engine. |
| Kevin MacLeod — Monkeys Spinning Monkeys | Artist's YouTube video, downloaded and analyzed via yt-dlp | Rejected: comedy/orchestral style. |
| Scott Buckley — Hiraeth | Artist's YouTube video, downloaded and analyzed via yt-dlp | Rejected: ambient/classical style and loss of dancefloor continuity. |

These were live API decisions, not fixture outcomes. The first YouTube assessments requested review because metadata had lost the artist and descriptions. Preserving source metadata and including drum-map summaries allowed informed rejection. The trial demonstrates a limit too: a detector assuming 4/4 can mistake pizzicato or bass attacks for kicks. Its tempo is not evidence of house genre.

## DJ result

Astra selected Dedication (Sound Factory Mix) → Just A Little (Sunday Service) → Deluxe Bar → Push The Feeling On → Private Suite at 124 BPM. It chose 8-bar overlaps throughout, citing a measured energy build and shorter exposure to uncertain tonal pairings. All cues and the complete sequence passed validation. The existing, listener-approved equal-power/loudness-matched handoff remains the renderer.

## Sources and local-use scope

- [Summertime — Roctakon](https://roctakon.bandcamp.com/track/summertime): downloaded through an existing purchase receipt; receipt tokens and audio remain private.
- [Tundra EP — Pueblo Nuevo](https://pueblonuevo.cl/catalogo/tundra/): free label download; CC BY-NC-ND 3.0. Used for personal local testing; do not distribute a derivative mix or include this music in the public demo without permission.
- [Monkeys Spinning Monkeys — Kevin MacLeod](https://incompetech.com/wordpress/2014/02/monkeys-spinning-monkeys/), [artist video](https://www.youtube.com/watch?v=2eZVbrO6Z1M): credit Kevin MacLeod/incompetech under the artist's attribution license.
- [Hiraeth — Scott Buckley](https://www.scottbuckley.com.au/library/hiraeth/), [artist video](https://www.youtube.com/watch?v=XPZL2yFOeA8): “Hiraeth” by Scott Buckley, released under CC-BY 4.0, www.scottbuckley.com.au. The artist requires video-description credits for YouTube use.

## Reproducing

Run b2b locally and visit `/astra-setup.html`, or set `OPENAI_API_KEY`. The local setup stores the key in ignored `.b2b/openai-key`, mode 0600. A key is never returned by the API or included in a prompt. `Astra DJ` enables set planning; listener requests use Astra automatically. Request-network failures hold the request for review instead of silently claiming a model decision.

Local DJ requests can use `POST /api/requests/local` with an existing `trackId`; this shares listener curation and labels the request “DJ test.” YouTube requests use the ordinary listener link form. Source matches reuse existing analyzed audio on retry. Review/rejected requests are held outside automatic set planning until resolved.

Runtime telemetry is recorded in ignored `.b2b/astra-usage.jsonl`: time, role, model, latency, response status and reported tokens, without prompts, keys or audio. After the browser playback check, 10 calls reported 33,593 input tokens and 1,917 output tokens (35,510 total). These are runtime API totals, not development/account-wide usage.

Browser execution check: the Astra-generated plan started playing Dedication on deck A, prepared Just A Little on deck B, and armed the 8-bar handoff. The accepted Don Juan request was incorporated as track six; both rejected and both review requests stayed outside automatic playback.
