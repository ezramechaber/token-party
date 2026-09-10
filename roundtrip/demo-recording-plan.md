# Roundtrip — 59-second recording plan

September 10, 2026, 15:34 EDT. Working recording plan, not a completed video. User clarified “Follow The Rules” means the hackathon requirements. This is the current recommended cut; earlier presentation drafts remain as history.

## Narrative

**Problem:** For independent photographers, the shoot ends; the revisions do not. Turning feedback into manual adjustments takes attention away from other work, while the photographer still needs to control the look.

**Human stake:** A headshot or portrait has value as an encounter between a person, a photographer and a camera. Preserve the actual photograph and its author’s direction. This is the user's product premise, not surveyed customer evidence.

**Product promise:** Turn feedback into a reviewable Lightroom revision, with the photographer making the final judgment.

**Why Astra:** At runtime, interpret visual intent and operate existing professional software. During development, build and refine the gallery, job workflow, native-edit integration and result verification.

**Proof:** One photo → one real request → a product-triggered Astra run → native Lightroom changes → a verified export → before/after and retained versions. The hero is the photograph returning to the photographer.

Other possible hooks: “Taking the portrait is personal. Getting through the revisions takes time.” Or “A client asks for a small change. The photographer still has to turn those words into an edit.” Recommend the shorter shoot/revisions hook. Do not imply a request came from an actual client unless it did.

## Choose the recorded case

Preferred: **Seated portrait**, beginning with **Unedited RAW**, and its existing request:

> This photo is not color corrected at all. Correct the white balance. Crop the photo to 4:5. Make the background a little darker. Keep the skin tones natural.

The request was read directly from the current local gallery. The 15:24 build log records a window-access blocker. During this planning session the gallery showed a later “Revision needs attention” result because the full native base-version label could not be verified. It explicitly reported no edits or export. New editing was paused at the session usage limit. Therefore this case is ready to plan, but its successful recording is not yet available. Resolve execution in the implementation task before recording; do not hide this state to imply success.

Fallback: **Portrait study**, verified **V2 → V3** revision. Its actual request is:

> Please make her face a little brighter while keeping the background dark. Keep the natural skin texture, the same crop, and the existing film-like color.

V3, “New version ready,” the request, comparison controls, and Download JPEG were inspected in the local gallery during this session. The build log records +0.35 EV on a feathered face mask and a 257.6-second successful run. This is a subtler visible change; use a closer face crop for the comparison, with identical display treatment for both images.

The existing 47.07-second accelerated `session-16x.mp4` documents an earlier assisted editing session. It is NOT established as footage of the V2 → V3 product-triggered run. Use it only as accurately labeled development footage. Do not pair that movie with the later form submission as though they were one runtime execution. If no matching runtime recording exists, capture a real successful run or explicitly present the existing completed run as a retrospective using its actual activity and native version evidence.

## Edit timeline and narration

59 seconds total, leaving one second below the minute. About 129 words; record at a conversational pace and trim phrasing rather than accelerating the voice. These are planned timings, not a measured rehearsal.

| Time | Shot and exact action | Narration | Evidence / overlay |
| --- | --- | --- | --- |
| 0:00–0:06 | Open on the chosen original portrait inside the real gallery. Photo fills most of the frame; avoid a title-screen delay. | “For independent photographers, the shoot ends. The revisions don't.” | Product and photograph visible immediately. |
| 0:06–0:12 | Widen to the photo, feedback panel and Roundtrip navigation. | “Roundtrip turns feedback into Lightroom edits, with the photographer still directing the look.” | Small editorial overlay: “Roundtrip · built today with GPT-6 Astra.” |
| 0:12–0:20 | Show the exact request in Photo feedback; click **Revise in Lightroom** during the real recorded run. Hold on the actual admitted/running state. | “Here, I'm asking for corrected white balance, a four-by-five crop, and a darker background.” | Keep request text legible. Narration summarizes rather than replaces the on-screen wording. |
| 0:20–0:32 | Cut to the same run in Lightroom: source photo, visible native white-balance/crop/background-mask actions. Select meaningful moments from continuous source capture. | “Astra reads the photograph and operates Lightroom's native controls. No image generation: it edits the photograph we actually took.” | “Astra at runtime · condensed recording.” Use actual speed/elapsed-time labels; no invented values. |
| 0:32–0:39 | Show named-version/export action, then the actual **New version ready** result in the gallery. | “It saves a new version, exports it, and returns the verified image to the gallery.” | Keep the same photo and request identity through the cuts. Display “Actual run: [measured duration]” when finalized. |
| 0:39–0:49 | Select **Compare versions**, choose the same base, sweep the divider slowly once. Hold the final image. Show retained version thumbnails; click **Download JPEG** if time permits. | “I compare the result and decide what feels right. The original and previous versions stay available.” | The audience must be able to see the crop/color change. “Original RAW preserved in Lightroom” is real UI text. |
| 0:49–0:56 | Briefly show a legible Roundtrip-specific development exchange, then a tight view of the current request's **View activity** or result checks. Return to the photo. | “I built the gallery, editing workflow, and verification with Astra during today's hackathon.” | “Built today: gallery → native edit → verified revision.” Show actual development evidence; keep Lightroom identified as existing third-party software. |
| 0:56–0:59 | Hold the finished portrait with Roundtrip name and short, verified public repository link. | “Roundtrip. The photographer keeps the final say.” | Small “Token Party” credit. No lengthy end animation. |

Fallback substitutions: in 0:12–0:20 say “Here, I'm asking for a brighter face, while keeping the background dark and the skin texture natural.” In the Lightroom shot show the actual face-mask action, not unrelated white-balance/crop footage. In the comparison select **Compare V2 with V3**. For a retrospective, replace the submission action with the actual recorded request and completed activity, and label “Recorded successful run · 4m 18s”; do not stage a fresh submission.

## Recording procedure

1. Lock the case and its exact base revision/request. Prefer the seated portrait only after its actual returned JPEG is inspected and the crop and skin tones look right. If it remains blocked, use the verified portrait-study case with accurately matched evidence.
2. Record one continuous source take from before the real submit action through completed export/gallery return. Budget several minutes for execution. Keep the actual Lightroom window accessible; do not operate another photo while the worker runs. The planning task does not launch another edit or change run allowances.
3. Use a consistent 16:9 canvas, ideally 1920×1080 at 30 fps. Enlarge the meaningful photo, feedback and Lightroom controls through editor crops; do not force tiny full-desktop text into the final video. Keep mouse movement deliberate and pause around the click/result.
4. Record the before/after divider, history and download as separate pickup shots of the same completed result. Record a short real development-evidence pickup from the Roundtrip build. The B2B Blender pep-talk screenshot belongs to B2B and should not stand in for Roundtrip development.
5. Record narration separately after the source take succeeds. One calm take, then one tighter take. Natural voice is sufficient; music is optional and should never obscure the narration. Use only cleared audio/assets in the public cut.
6. Edit to the timeline. Condense waiting openly with jump cuts or a visible speed label; preserve causal order. Keep at least five seconds for the result itself. Store source captures under ignored `.local-demo`; do not add personal media or private raw traces to Git.
7. Export H.264 MP4 with audible narration and legible captions, at most 60.0 seconds including the ending. Watch the actual exported file once with sound and once muted to check that the actions and captions still tell the story. Check duration from media metadata. Verify the final request/result match and source identity.
8. After the demo is complete, update the activity/usage records and commit the relevant public code/docs, excluding personal media, secrets and unrelated work. Publish the video and verify logged-out access to both its link and the repository before final submission. These are recording/submission steps, not actions completed here.

## Follow the hackathon requirements

Based on the participant-guide summary in [hackathon.md](../research/hackathon.md) and the user's form screenshot; external links remain unvisited at the user's request.

| Requirement or rubric item | How this cut addresses it |
| --- | --- |
| One-minute screen-capture video with audio | Target 59 seconds with voiceover and mostly working-product footage. |
| Astra in development — 25% | Explicit development line and a real Roundtrip build/iteration excerpt at 0:49. |
| Astra in the product — 25% | Actual gallery job driving native Lightroom actions and returning its export. |
| Live demo — 25% | One complete, visually clear revision flow, with honest compression of waiting. The guide does not establish a requirement for an uncut or real-time submission video. |
| Technicality — 25% | Native computer use, correct photo/base version, named edit, verified output and preserved history shown through the workflow. |
| Event-built original contribution | Say the gallery/automation/verification were built today; distinguish Adobe Lightroom and the source photo as inputs. The guide forbids showing non-event-built functionality as the team's contribution. |
| Prohibited image analyzers / dashboard-first products | Center the actual edit/export/review action loop. This is our substantive distinction; presentation wording alone does not determine organizer eligibility. |
| Public repository and publicly accessible video by 5:30 p.m. EDT | Verify both links logged out, list all members, and complete the form before the deadline. Public app hosting is not listed as a submission requirement. |
| Rights to used code, data and assets | Choose a portrait cleared for public demonstration and keep private material out of capture/commits. |

Do not spend this minute on Token Party history, comparative claims, or a second project. Two separate entries remain the working submission plan; no prohibition was found in the supplied summary, and no explicit multiple-entry permission has been verified. Do not block recording on that uncertainty.

## Practical schedule from this checkpoint

Aim to choose the usable take by 4:00 p.m., assemble and narrate by 4:30, export and review by 4:45, and publish/check links by 5:00. Reserve the final half hour for the form and upload/access failures. These are suggested internal targets; the recorded official deadline is 5:30 p.m. EDT.


## 2026-09-10 15:45 EDT — Opening revision and recording pause

Replace the generic first line with the user's supplied origin: **“I love photography. These are my photos, and I needed to edit them for Figmates.”** Allow about seven seconds, recovering a second from the following introduction. The premise is a real personal editing need; do not invent the nature of Figmates. Keep the photographed person and native-edit result as the story's visual center.

The implementation task reports the seated-RAW hero completed in239.93seconds and independently checked. Preserve that real result; verify the exact source/result before using it in the cut. No new capture has started. User paused video because Blender is also active; this session only planned B2B and recorded narrative changes.
