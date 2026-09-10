# Song maps and musical handoffs

A song map separates measured timing from mixing choices. Each private track has a readable `.b2b/maps/<track-id>.json`, also available through **Mix map** in the inspector. It contains tempo/grid confidence, editable phrase cues, per-bar kick evidence and sustained low energy, usable overlap candidates, and a proposed musical-arrival boundary. Maps remain local and are excluded from Git.

## What changed after listening

The Dedication → Nightcrawlers feedback exposed two independent problems. The prepared audio had roughly 42 milliseconds of attack separation despite close tempo estimates. Beat detection now anchors to broadband attacks across several sections, and the actual tempo-prepared overlap receives a local timing correction before playback is armed. This is attack alignment, not proof of the correct musical downbeat.

The user clarified that Nightcrawlers' opening does contain thumpy kicks: the problem was handing over while it still sounded like just drums. Kick continuity alone therefore cannot define a good intro. Harmonic midrange changes suggest an arrival around 24.7 seconds, followed by fuller drum support around 32.6 seconds. These are spectral proposals, not claims that a model recognized the hook by listening.

The planner favors an overlap ending at the musical-arrival candidate while checking the entire window for drum support. For this pair, the proposed eight-bar incoming window begins around 9 seconds and ends around 24.7 seconds. The existing channel and low-EQ ramps remain linear. When no safe mapped overlap exists, the planner requires review rather than reverting to an unsafe generic intro window.

## What the model can do well

A model can compare candidate handoffs, decide which phrase should take over, suggest whether to preserve a hook or build tension through a break, and explain the tradeoff. The map supplies compact evidence and uncertainty; the audio engine supplies executable timing. Runtime Astra currently sees the valid edges and their mix evidence when enabled. The API key is still pending; current decisions use explicit rules.

Hook identity, vocal clashes, and whether a handoff feels musically satisfying need listening. Harmonic energy is not semantic understanding, and bass stabs can resemble kicks. In **Grid / cues**, **Musical arrival** and **First real kick** accept human corrections. The latter suppresses early kick estimates; the former replaces the spectral arrival proposal. Keep the intro window consistent with the desired handoff when confirming cues.

A future strategy can hold outgoing texture or drums through an incoming break, then crossfade into the full groove. That requires coordinating channel volume and low-band gain together; holding only low EQ while fading the whole channel would still remove its drums. This version chooses supported overlaps instead.
