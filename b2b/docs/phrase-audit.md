# Nightcrawlers phrase audit

Read-only audio audit, September 10, 2026. Track: “Push The Feeling On.”
Current measured tempo: 122.005 BPM; estimated first bar offset: 1.0981 seconds.
The analysis distinguishes three separate questions: individual beat timing,
which beat begins a bar, and which bar begins a 16-bar phrase. A good beat grid
does not establish the latter two.

The current candidate selection prefers the latest kick-supported ending and
allows starts every four bars. Its winning 16-bar exit is **355.1819–386.6561 s**,
starting on displayed bar 181. That is four bars after displayed bar 177 and
does not match a 16-bar phrase counted from the current bar 1.

A supported alternative already exists: **347.3134–378.7875 s**, displayed bars
177–192. Its kick coverage is 1.0 and average heuristic evidence is 0.876,
versus 0.821 for the later candidate. These are detector scores, not calibrated
probabilities or proof of musical phrasing.

Four-band RMS arrangement changes, measured as the difference between four
bars before and four bars after each boundary, weakly favor the current bar 1
as the origin of a 16-bar pattern. Mean novelty for that phase is 0.427;
the adjacent phase scores 0.402 and the phase twelve bars later scores 0.378.
This small separation does not justify automatic confirmation. Breaks, fills,
and the ending can introduce large changes away from the phrase origin.

Recommended ear checks are **315.839 s**, **347.313 s**, and **378.788 s**:
consecutive proposed 16-bar boundaries. Start playback two bars before each
point to hear the lead-in. Compare the existing 355.182-second exit against
347.313 seconds to hear the four-bar difference.

The practical control is “Phrase one here”: save a human-confirmed phrase
anchor separately from the beat/bar offset and label an inferred anchor as
estimated. With a confirmed 16-bar anchor, require a 16-bar transition to start
at `anchor + n × 16 × 240 / bpm`, then apply kick support and endpoint checks.
For eight-bar transitions, make the policy explicit: start at phrase one, or
start at the midpoint and finish on the following phrase one. Do not silently
substitute the nearest four-bar window. A local section anchor can handle
arrangements that add or remove bars without changing the whole track's grid.

The musical phase has not been confirmed by listening in this audit.
