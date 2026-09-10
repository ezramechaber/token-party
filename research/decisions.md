# Project Decisions

This log records working decisions made during ideation. Decisions are intentionally revisitable as the hackathon rubric and product direction become clearer.

## 2026-09-10 — Treat token cost as unconstrained

**Decision:** During ideation and the hackathon prototype, do not optimize for model-token cost—either while building the product or in its runtime workflow.

### Why

The primary goal is to discover and demonstrate the strongest AI-native product that GPT-6 Astra makes possible. Constraining inference too early would bias the team toward shallow workflows and obscure the model's value. For the prototype, judge impact, capability leverage, correctness, and demo quality matter more than plausible production unit economics.

### What this permits

- High-reasoning-effort calls when they improve the outcome.
- Multiple agents, critics, verifiers, or iterative passes.
- Large context and generous retrieval where useful.
- Runtime workflows whose central value depends on substantial model inference.
- Using Astra for the product's core reasoning and action loop, not only as a development tool.

### Constraints that still apply

- The participant allocation is $100 in OpenAI API credits plus one month of ChatGPT Pro Lite; additional Codex credits may be available from organizers onsite.
- End-to-end latency must fit the user experience and live demo.
- API rate limits, concurrency limits, and event-provided access are real.
- The demo needs deterministic fallbacks and bounded failure behavior.
- Safety, privacy, permissions, and open-source requirements remain in force.
- Architecture should make token usage observable even though it is not optimized.

### Revisit trigger

Revisit production cost only after selecting a compelling product direction and proving the thin vertical demo. At that point, evaluate whether smaller models, caching, routing, batching, or fewer passes can preserve the experience.

## 2026-09-10 — Plan Back 2 Back as the next project

**Decision:** The user selected a DJ program using a small crate of MP3s, starting with 4/4 house and clean club arrangements. Support suggested ordering, on-screen manual control and Auto, using matched 8/16-bar overlaps with linear channel fades and low-EQ swaps.

**Proposed implementation:** Audio tools measure grids, spectral key evidence and phrase candidates; Astra selects and revises valid set plans; an audio engine schedules playback. Validate one two-track transition before scaling. Preserve the earlier Lightroom work. See [Back 2 Back plan](back-2-back-plan.md).

**Rejected for initial scope:** General meter detection, full instrument separation, screenshot-only timing, model-timed audio automation and implicit pitch changes labeled as key lock. Stack, confidence thresholds and stretching quality remain unvalidated proposals.


## 2026-09-10 13:05 EDT — Name the shared event “~~Rent~~ Token Party”

**Decision:** User chose the display name **~~Rent~~ Token Party**, with only “Rent” struck through. Plain-text name: Token Party. The shared presentation is a party where guests listen to music, get photographed, and let Astra curate sounds and edit images. Back 2 Back and Roundtrip retain their project folders and histories.

**User-authored framing:** “In the annals of NYC history exists the rent party: Show up, listen to music, and put a few $ in the hat to cover rent. It started with jazz, through disco and house. immortalized in Party Girl.” Followed by: “we're throwing a token party: show up, listen to music, get your photo taken, let Astra curate the sounds and edit your images.”

The [reference](https://en.wikipedia.org/wiki/Rent_party) supports Harlem origins, musical fundraising and the Party Girl connection. A continuous jazz-to-disco-to-house historical lineage has not been independently established here. This is the chosen event framing; it does not establish successful runtime music curation. Earlier runtime verification requirements still apply.
