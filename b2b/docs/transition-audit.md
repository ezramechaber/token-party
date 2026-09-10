# Five-track transition audit

September 10, 2026. Read-only audit of the current local crate and rules plan at
124 BPM, requesting 16-bar blends. Actual source audio and existing prepared
PCM files were measured; no new master mix was rendered or played in this audit.
The reusable command is `python scripts/audit_transitions.py`; redirect its
output into ignored `.b2b/transition-audit.json` for local evidence.

## Scheduling and arrangement

| Transition | Blend | Outgoing source cue | Incoming source cue | Incoming solo time before its next transition | Unplayed outgoing tail |
|---|---:|---:|---:|---:|---:|
| Private Suite → Push The Feeling On | 16 bars | 220.821 s | 32.572 s | 278.710 s | 30.983 s |
| Push The Feeling On → Deluxe Bar | 16 bars | 347.313 s | 0.490 s | 170.323 s | 19.736 s |
| Deluxe Bar → Dedication (Sound Factory Mix) | 8 bars | 203.416 s | 0.007 s | 325.161 s | 1.462 s |
| Dedication → Just A Little (Sunday Service) | 8 bars | 337.930 s | 61.433 s | Final track | 3.272 s |

All three middle tracks have ample time to preload and arm the following
transition after the previous handoff. The shortest margin is 170 seconds.
This verifies temporal feasibility of these cue choices, not successful
execution of a complete browser Auto session. No outgoing track loses minutes:
the largest discarded tail is about 31 seconds, approximately one 16-bar phrase.
All four outgoing phrase anchors remain estimated rather than ear-confirmed.

The two-bar kick-supported landing rule passes every pair. Inspecting eight
bars after the handoff finds one additional event: Dedication's displayed bar
16, 28.807–30.727 seconds, has no supported kicks. Its low-energy score drops
from 0.943 in bar 15 to 0.032, then returns to 0.873 in bar 17. This is one bar,
seven bars after landing, and is plausibly an intentional fill/break; it should
be surfaced for listening, not automatically rejected as a bad transition.

Nightcrawlers enters at 32.572 seconds, later than its candidate harmonic arrival
at 24.704 seconds. The selected drum-supported section intentionally skips that
opening. Sunday Service enters at 61.433 seconds and reaches its candidate
harmonic arrival at 76.671 seconds when the blend ends. The phrase map can
explain these choices, but harmonic novelty alone does not identify a hook or
guarantee that the listener wants it included.

## Level and timing evidence

The following are source-section integrated LUFS with the app's whole-track
gain trim added. “Before” is the two bars before the outgoing cue; “landing” is
the first two incoming bars after the overlap. They are not measurements of
the mixed master or a perceptual quality score.

| Transition | Before | Landing | Change |
|---|---:|---:|---:|
| Private Suite → Nightcrawlers | −14.70 | −15.73 | −1.03 LU |
| Nightcrawlers → Deluxe Bar | −16.15 | −17.53 | −1.38 LU |
| Deluxe Bar → Dedication | −17.82 | −16.24 | +1.58 LU |
| Dedication → Sunday Service | −17.70 | −15.60 | +2.10 LU |

There is no evidence here that these level changes require correction. A rise
can be musically desirable. The separately retained, human-approved Dedication
→ Nightcrawlers master capture rises about 7 dB in the recorded RMS windows;
that is a different pair, measurement, and window length. Preserve that approved
behavior instead of treating constant section loudness as the objective.

Prepared-file attack offsets relative to nominal cue timing are respectively:

| Transition | Outgoing correction | Incoming correction |
|---|---:|---:|
| Private Suite → Nightcrawlers | +10.88 ms | +11.53 ms |
| Nightcrawlers → Deluxe Bar | +3.64 ms | +2.52 ms |
| Deluxe Bar → Dedication | +8.40 ms | −10.16 ms |
| Dedication → Sunday Service | −11.63 ms | −14.00 ms |

All eight windows meet the existing attack estimator's reliability threshold,
with median absolute spreads of 2.3–5.6 ms. The Deluxe Bar → Dedication pair
would have about 18.6 ms of relative offset without its local corrections.
Retain the per-window preparation mapping rather than using one universal
offset for an entire record. These are attack proxies, not isolated kick stems.

## Bounded follow-up proposals

1. Add a plan-level temporal constraint when extending an order: the next exit
   must follow the previous incoming handoff by enough time to prepare and arm
   the next deck. Pairwise edges alone cannot establish this. The current plan
   already passes with wide margins.
2. Report the actual chosen eight- or sixteen-bar duration and seconds skipped
   at either end in the transition inspector. Keep musical-arrival candidates
   separate from confirmed instructions to include a particular section.
3. Show the next eight bars of arrangement evidence after landing for audition,
   without rejecting short intentional breaks or flattening desired level rises.

No planner, mixer, server, or user-interface behavior was changed by this audit.


## Follow-up implemented

The sequence preparation constraint is now enforced by the rule search, optional Astra plan validation, fixed-order API and request append path. It requires eight seconds after a middle track's incoming handoff before its outgoing transition. The current five-track order and cues remain unchanged. Runtime failure to arm the next edge releases Auto and keeps the current track playing. The arrangement-display proposals above remain future refinements; the measured source audit is not a complete-set listening test.
