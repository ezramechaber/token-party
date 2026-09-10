# Working chrome interface

Implemented September 10, 2026 from the approved [ChatGPT Image concept](design/b2b-chrome-art-ui-v2.png).

The live interface uses the concept's neutral charcoal panels, pink/lavender accents, central Audition and Auto controls, and wide chrome artwork. The artwork is a CSS-clipped display of the generated concept's art-only region. No generated control, waveform or track text is displayed as working UI. The existing spectrum-driven canvas overlays the art softly, so the chrome profile remains visible while the playing track changes its reflected colors.

All previous DOM IDs and deck hooks were retained. Buttons, inputs, waveforms, phrase inspector and crate remain real HTML/canvas controls. The layout adapts from three desktop columns to two decks above a compact mixer, then a single column on narrow phones. Reduced-motion support remains in the audio-reactive canvas.

Integration slots: Watch the set (`toggleScene`, `sceneSection`, `boothScene`, `sceneStatus`), listener requests (`requestSection`, `listenerLink`, `requestQueue`), recording (`recordMix`, `recordStatus`), handoff curve (`mixCurve`, values `linear` and `balanced`), and loudness matching (`autoGain`). Their behavior belongs to the application layer; adding these surfaces alone does not implement their features.

Validation: no previous IDs removed, no duplicate IDs, balanced CSS braces, and clean whitespace diff. Parent task performs the live integrated browser check.

## Full revision 2 composition

The next pass follows the approved concept's proportions instead of merely applying its palette. The artwork is followed by short, wide deck panels with compact waveforms, large circular play controls, and vertical Low/Mid/High sliders. Audition, Auto and the crossfader stay between the decks. The crate sits immediately below, with a compact YouTube import field in its header.

Secondary tools remain accessible through functional disclosures: set settings in the header; cue details per deck; order/import tools inside the crate; and the beat inspector (`inspectorPanel`) and recording comparisons below the crate. Existing IDs are retained. Mid and high ranges use −24 to +6 dB; low retains −24 to 0 dB; each input is immediately followed by its output for the audio engine's updates. The parent implementation owns those new audio hooks and automatic inspector opening.

The desktop layout stays in three columns from 900 px. Smaller screens stack decks around a compact mixer. The typography uses DM Sans, with graphite surfaces and pink/lavender accents. The generated chrome remains the single expressive image; functional controls are native HTML and canvas.

Applied the requested [frontend-design principles](https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md): plan against the concrete brief, concentrate the visual identity in one element, remove nonfunctional labels, and preserve accessible controls. Static checks found no removed or duplicate IDs and a clean whitespace diff. A separate browser visual check was attempted, but the subagent has no in-app browser surface available; the parent task performs integrated rendered QA.


## Rendered polish and working EQ

The final pass used [Impeccable polish](https://raw.githubusercontent.com/pbakaus/impeccable/main/.agents/skills/impeccable/reference/polish.md) through the local design router: preserve the approved chrome composition, expose transport state, make the import path keyboard accessible, and verify rendered layouts. Artist names and up to two title lines stay visible. Loading disables transport/EQ controls; failures provide a reload instruction. Both decks sit above the mixer at 640–899 px, while narrow phones stack them. Secondary controls wrap without leaving the panel.

Low, mid, and high sliders now operate real Web Audio filters. Equal-power manual crossfade follows the selected handoff law. Waveform overviews show stereo peak and RMS rather than a solid amplitude wall. Inspect opens the beat/phrase view at the selected deck's playhead, with keyboard seeking on the overview.

Validation: inspected the live desktop with Dedication and Nightcrawlers, plus a 390 px responsive preview. Keyboard mid-EQ adjustment and Inspect succeeded. The browser's OfflineAudioContext verification at `/audio-check.html` measured −11.94/−12.00/−11.92 dB for nominal −12 dB low/mid/high cuts, and unit total power at crossfade midpoint. Four existing handoff regression tests passed. The temporary responsive harness is removed from the shipped files.
