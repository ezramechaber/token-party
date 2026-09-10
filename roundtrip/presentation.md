# Roundtrip — one-minute submission draft

2026-09-10 14:57 EDT. Proposed separate submission aimed at independent photographers. Working promise: **Turn feedback into a new edit. Keep the photographer in control.** The shared event identity remains ~~Rent~~ Token Party.

## Story and shot plan

| Time | Picture | Spoken draft / purpose |
| --- | --- | --- |
| 0–7 s | Strong original portrait with a real feedback request | “For an independent photographer, the shoot is only part of the job. Then come the revisions.” |
| 7–15 s | Show the same photo in Roundtrip and select its actual request | “Roundtrip turns that feedback into a new Lightroom edit, while keeping the photographer in control.” |
| 15–31 s | Recorded Astra run: correct source photo, native edits, named version, returned export | “Astra works in Lightroom, makes the requested changes, and brings back a version I can review.” Label elapsed time; compress execution visibly. |
| 31–46 s | Before/after on the same photo; allow a moment to inspect the result | “The original stays intact. I can compare versions and decide what feels right.” |
| 46–54 s | Brief development evidence, then return to the real gallery | “Built with Astra, with real photographs and real feedback guiding each iteration.” |
| 54–60 s | Final image and name; verified repository link | “Roundtrip. Faster revisions. Still your eye.” This is a proposed benefit, not a measured speed claim. |

## Capture selection

Prefer a successful revision whose visible change is clear and whose request matches the result. The verified studio-portrait example is an intentionally extreme washed-out, hands-only crop; it demonstrates following direction, but may be less persuasive as an example of preserving a photographer's style. Inspect the earlier face-adjustment sequence as a potential main story. Do not invent client dialogue or relabel synthetic demonstration feedback as a real client request.

Use original → actual feedback → returned revision → photographer's judgment. If a before/after is unattractive or hard to read, choose a different verified example rather than claiming taste through narration alone.

## Evidence limits

The local loop and native Lightroom revision are verified in the build log. The studio retry took 289.7 seconds after manual photo restoration and named-base preparation; preserve that context wherever this specific run is presented. Hosting and production remote comment replay are not established. No fresh edit jobs, photo exports or recordings were run for this script. Final timings require rehearsal.


## 2026-09-10 15:02 EDT — Camera connection and native editing

This reframes the earlier productivity-only draft. User's hypothesis: for smaller headshots, family portraits and similar work, people value a real photographic encounter and connection to the camera. Image-generation models can be excellent; Roundtrip deliberately uses a different workflow. This is an audience hypothesis, not validated customer research.

**Implementation evidence:** The runtime prompt restricts execution to native Lightroom tonal/color/detail/crop/masking changes, preserving source identity and named versions. Astra uses visual reasoning and computer use; the workflow does not use an image-generation model. Say “no image generation,” not “no AI image understanding.” Do not equate retained source files with a blanket guarantee of authenticity.

**Proposed spoken copy:**

> A family portrait matters because those people were there. A photographer chose the light and caught the moment.
>
> For independent photographers, the work keeps going after the shoot.
>
> We built Roundtrip with Astra to help turn feedback into finished edits while keeping that human connection.
>
> It uses no image-generation model. Astra reads the feedback, works directly in Lightroom, and adjusts the actual photograph.
>
> [Show native actions, then the returned before/after.]
>
> The original stays intact. The photographer compares versions and decides what feels right.
>
> Roundtrip. Faster revisions. Still your eye.

Use the actual demonstrated portrait rather than implying that family-photo trials were conducted. “Faster revisions” remains a value proposition, not a measured speedup. The story needs a flattering, direction-faithful example; the extreme hands-only crop is stronger as technical supporting evidence than as the main emotional image.

**Both Astra roles, visibly:** Development evidence should show the gallery/feedback/version workflow being built and refined with Astra. Runtime footage should show the separate product job interpreting feedback, operating native Lightroom controls, inspecting the export and returning the revision. Allocate roughly 8 seconds to the opening, 7 to the product/development introduction, 18 to compressed runtime action, 20 to the before/after and human review, and 7 to the close. Rehearse speech and preserve an explicit elapsed-time label on compressed execution. Do not add “all processing stays local” or broader privacy promises: native editing on the Mac does not establish where the model's inference runs.


## 2026-09-10 15:34 EDT — Recordable demo plan

The current recommended cut is the [59-second recording plan](demo-recording-plan.md), with a problem statement, eight timed shots, exact narration, current preferred/fallback cases, capture procedure and hackathon rubric mapping. User clarified that “Follow The Rules” means the hackathon requirements. Seated portrait is the preferred case only after a successful run; the current gallery reports a native base-version verification failure and paused edits. Portrait study V2 → V3 remains the verified fallback. Existing accelerated assisted-edit footage must not be represented as that later runtime job. No new edits or recordings were made in this planning session.


## 2026-09-10 15:45 EDT — Personal photography origin

User clarified: photography is their own interest, the demonstrated photographs are theirs, and they needed to edit them for **Figmates**. Lead with that actual need instead of a purely hypothetical independent photographer. Do not infer who Figmates is, a client relationship, or delivery requirements beyond this statement.

Proposed opening: “I love photography. These are my photos, and I needed to edit them for Figmates.” Then: “I wanted help with the edits while keeping the photograph—and my eye—at the center.” Show the user's real image immediately. Connect that personal experiment to the wider independent-photographer use case after the result. Preserve the no-image-generation and native-Lightroom story and the separate development/runtime evidence.

The other Lightroom task has since reported a completed and independently inspected seated-RAW edit: job f8caf7b898474633, revision e4b111541a30456f, 1638×2048 export, 239.93-second runtime. This is a reported handoff from that task, not a new inspection here. It supersedes the earlier hero-blocked status once its evidence is checked for the recording. Video capture remains paused at the user's request because Blender work is concurrent.
