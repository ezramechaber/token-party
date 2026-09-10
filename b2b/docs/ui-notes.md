# Working chrome interface

Implemented September 10, 2026 from the approved [ChatGPT Image concept](design/b2b-chrome-art-ui-v2.png).

The live interface uses the concept's neutral charcoal panels, pink/lavender accents, central Audition and Auto controls, and wide chrome artwork. The artwork is a CSS-clipped display of the generated concept's art-only region. No generated control, waveform or track text is displayed as working UI. The existing spectrum-driven canvas overlays the art softly, so the chrome profile remains visible while the playing track changes its reflected colors.

All previous DOM IDs and deck hooks were retained. Buttons, inputs, waveforms, phrase inspector and crate remain real HTML/canvas controls. The layout adapts from three desktop columns to two decks above a compact mixer, then a single column on narrow phones. Reduced-motion support remains in the audio-reactive canvas.

Integration slots: Watch the set (`toggleScene`, `sceneSection`, `boothScene`, `sceneStatus`), listener requests (`requestSection`, `listenerLink`, `requestQueue`), recording (`recordMix`, `recordStatus`), handoff curve (`mixCurve`, values `linear` and `balanced`), and loudness matching (`autoGain`). Their behavior belongs to the application layer; adding these surfaces alone does not implement their features.

Validation: no previous IDs removed, no duplicate IDs, balanced CSS braces, and clean whitespace diff. Parent task performs the live integrated browser check.
