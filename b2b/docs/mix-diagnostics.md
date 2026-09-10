# Listening and measuring a real handoff

2026-09-10. Captured the browser's master bus, including the selected fades, EQ, trim and master volume. Four 23.28-second recordings remain private in `.b2b/diagnostics/` and are replayable in **Recorded mix comparisons**. These are actual browser recordings, not a separately approximated Python render. Spectrograms and RMS measurements support human listening; they do not measure musical quality.

The initial mix used Dedication (Sound Factory Mix) into Push The Feeling On at 124 BPM, eight bars. Outgoing original-file cue337.9295s; incoming8.9666s (bar5). The proposed musical arrival24.7037s is bar13, but bars13–16 contain no detected kicks. Full kick support resumes32.5722s, bar17. Ending the mix at bar13 therefore drops the outgoing drums exactly when the incoming drums disappear.

## Actual recorded comparison

All measurements below are dBFS RMS, not LUFS. Midpoint is the central30% of the overlap; before/after sample short neighboring sections with different arrangements. They are not interchangeable equal-content loudness samples.

| Take | B entry | Full-band before / middle / after | Bass35–180Hz middle / after |
|---|---:|---:|---:|
| Original linear, original gain | bar5 | −19.42 / −24.22 / −24.52 | −28.71 / −41.96 |
| Equal-power, original gain | bar5 | −19.44 / −16.72 / −24.52 | −18.21 / −41.96 |
| Equal-power, matched loudness | bar5 | −28.15 / −23.76 / −29.26 | −25.27 / −46.71 |
| Equal-power, matched loudness, supported landing | bar17 | −28.10 / −23.50 / −21.09 | −25.08 / −22.67 |

Whole-track FFmpeg loudnorm measurements: Dedication−7.28LUFS; Nightcrawlers−11.26LUFS. Applied trims toward−16LUFS are−8.72dB and−4.74dB, with peak headroom constraint. The preferred final recording peaks at−7.89dBFS. Whole-track matching does not equalize every individual phrase.

The first two takes isolate the curve change. The next isolates loudness matching. The final take changes the incoming phrase: it should not be used to attribute all improvement to the curve. The user listened live, reported more continuity, then strongly approved the final combination. It is now the default, with the old curve retained for comparison. Capture `af10ab0fd5764ae38eb3cf36c6d7d513` is the preferred reference.

## Why the original curve could sag

Gain-node ramps operate in amplitude, while a low-shelf filter's gain parameter is in decibels. Halfway from0to−24dB is−12dB, roughly25% amplitude, not50%. Combining that with a50% channel fade leaves roughly12.6% low-frequency amplitude per deck. Equal-power channel curves remove the conventional uncorrelated-signal midpoint power dip; bass EQ still changes the total response. The experimental low-EQ curve is derived from those amplitude curves, limited to−24dB. It is not a constant perceived-bass guarantee, particularly with correlated kicks or changing arrangements.

References: [Web Audio specification](https://www.w3.org/TR/webaudio/) and [Web Audio equal-power crossfade explanation](https://webaudioapi.com/book/Web_Audio_API_Boris_Smus_html/ch03.html).

## Changes supported by this test

- Outgoing8/16bar windows must align to a separate phrase anchor. Nightcrawlers'16bar exit moves from355.182s/bar181 to347.3134s/bar177. The origin remains estimated until a human confirms it.
- Inspect two incoming bars after A stops. The simple mixer skips a landing that immediately loses drum support. This moves Nightcrawlers' incoming window to32.5722s/bar17 for this pair.
- Future strategy: carry outgoing texture/drums through an intentional incoming breakdown and hand over on its return. That needs explicit overlap/landing instructions in the mix map, rather than relaxing all kick-support constraints.
