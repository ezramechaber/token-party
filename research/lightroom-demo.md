# Lightroom roundtrip demonstration — 2026-09-10

## Objective and result

Validate one real RAW photo → native Lightroom edit → JPEG export → visual self-critique → native revision → second export → local comparison page. The user explicitly requested this demonstration and screen recording. This is a computer-use workflow demonstration, not a standalone implementation of cloud review or comment monitoring.

The reference was Kevin Mullins's [Fujifilm Kodachrome-style portrait recipe](https://www.kevinmullinsphotography.co.uk/blog/fujifilm-kodachrome-style-recipe). We interpreted warm skin, subdued color, dark tones, and texture using Adobe Color on an ORF source. This does not reproduce an exact Fujifilm simulation.

## Actual native edits

| Control | V1 | V2 |
| --- | --- | --- |
| Exposure / Contrast | +0.15 / +22 | Same |
| Highlights / Shadows | −45 / +18 | Same |
| Whites / Blacks | −18 / −14 | Same |
| Temperature / Tint | 6000 K / +4 | 5700 K / +2 |
| Vibrance / Saturation | −12 / −8 | Same |
| Purple saturation / luminance | −45 / −15 | Same |
| Blue saturation | −20 | Same |
| Texture / Clarity | −5 / −8 | Same |
| Vignette / Grain | −12 / 20 | Same |
| Background mask exposure | None | −0.55 |

Self-critique of V1: the bright wall competes with the face and the skin is too golden. V2 slightly cools the white balance and lowers exposure on a native background mask. Original composition is preserved. No generative photo editing was used.

Named Lightroom versions: `Roundtrip 00 - Original`, `Roundtrip 01 - Fuji first pass`, and `Roundtrip 02 - Subject first`.

Three native JPEG exports: original rendering, V1, V2. Each is 1536 × 2048, sRGB, quality 90. Local HTML includes a V1/V2 slider, original/V2 toggle, three-stage contact sheet, native settings, source attribution, and the screen recording.

## Evidence and boundaries

Personal image exports, HTML, and recording are under `.local-demo/fuji-portrait/`, excluded from Git. Open `index.html` directly or serve that folder locally. No public deployment was requested or performed.

CleanShot recorded 752.87 seconds (12m 33s) of the active desktop workflow as H.264 at 3010 × 1952. Metadata and sampled frames were checked, including the reference and native Lightroom editing. Initial setup preceded recording. The recording is an uncut working session, not the hackathon's required one-minute submission video.

Reliability finding: Lightroom's unedited filter removed the source after editing, advancing selection. Exact filename search plus named-version verification recovered the intended photo before export. This demonstrates the need for stable photo identity and post-export verification in a product. Native numeric controls and window focus also required visual verification.

The native edit/review/revise loop works for this example. Autonomous client-comment intake, private cloud export delivery, an event-built runtime application, throughput, and robust unattended operation remain unimplemented and unvalidated.

## Responsive QA and rubric assessment — 2026-09-10

Tested the local page in the existing in-app browser at viewport widths 320, 390, 768, 851, 1024, and 1440 pixels. Inspected screenshots and DOM dimensions. Fixed the reference image's fixed intrinsic height, reserved image proportions, loaded the small photo set eagerly, and stacked the history images on narrow phones. No horizontal overflow remained at checked widths, including the expanded settings table on the smallest viewport.

Verified pointer dragging, pointer click positioning, Home/End, arrow keys, Shift+Arrow, original/V1 comparison selection, settings disclosure, loaded images, and 47.07-second video playback. No captured browser warnings or errors. These are desktop browser viewport checks; no physical mobile device or second browser engine was tested. Restored the user's normal viewport after testing.

Added a plain-language opening describing the future client-feedback workflow and explicitly identified the present demo as an edit/export/self-critique/revision example.

### Assessment of the current deliverable

Subjective estimate against the four equally weighted official criteria; not an official judge score or a claim of submission readiness.

| Criterion | Score / 10 | Evidence and remaining gap |
| --- | ---: | --- |
| Astra in development | 8 | Real native-app operation, image review, site creation, debugging, QA, recording, and build notes. Development evidence still needs a concise public presentation. |
| Astra in finished project | 2 | Astra executed this session, but the shipped HTML is a comparison viewer. It cannot accept feedback and invoke the editing workflow. |
| Live demo | 6 | Genuine photo changes, recoverable versions, reference, and a short recording. A fresh live request cannot yet run from the product; the accelerated video needs a narrated product story. |
| Technicality | 4 | Native edits, verified exports, a working comparison UI, and responsive checks. No reusable orchestration, stable asset identity, job state, retries, or client-comment integration. |

**Weighted total: 50/100.** The strongest next improvement is one product-triggered review comment → real Lightroom revision → verified export → updated gallery, with visible progress and recoverable state. More presentation polish alone will not close the runtime gap. Public repository, permitted demo assets, public screen-and-audio submission video, and submission packaging still need separate completion.
