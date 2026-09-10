# Roundtrip — from RAW to client-approved photos

2026-09-10. Leading direction for focused exploration, not a completed selection or implementation. The founder explicitly likes a pipeline that operates Lightroom through computer use, exports photos to a private cloud destination, receives client comments, watches for new feedback, and revises the photos accordingly. Loadmaster and Showrunner remain interesting alternatives.

## Product thesis

A post-production operator for independent commercial photographers and small studios: give it a selected shoot, reference look, and delivery brief; it carries the work through editing, client review, revision, and final delivery in the photographer's existing tools.

The valuable unit of work is a completed revision round. The central interaction is a client comment becoming an actual, reversible Lightroom edit, with the resulting photo available at the same review destination. Success is approval of deliverables, not merely applying a preset or collecting comments.

Working name: Roundtrip. No naming or trademark research performed.

## Proposed experience

1. Photographer supplies selected photos, an approved reference look, protected details, export requirements, and the permitted scope for client-directed changes.
2. Astra operates Lightroom to edit the selection. It observes rendered results, compares them against the brief, and revises settings where needed.
3. The operator exports previews and creates or updates a private review destination. The photographer receives its link; sending invitations or messages is a separate explicit action.
4. A reviewer leaves feedback tied to a photo and revision, such as “less yellow in the background; keep the product's blue.”
5. A local worker detects new feedback while running, associates it with the correct asset and version, and asks Astra to translate it into scoped editing actions.
6. Astra returns to the correct Lightroom photo, saves a recoverable prior state, changes the appropriate controls or mask, checks the result, and produces revision 2.
7. The review destination presents the updated image and revision status. The client's approval remains a human action; the system does not approve its own work.
8. Approved photos are exported with the requested dimensions, profile, and filenames and uploaded to the private delivery destination.

Supporting only exposure, temperature/tint, and crop is a reasonable first scope. Selective subject/background masking is the stretch capability that makes the protected-product-color demo stronger. Do not promise semantic color preservation without testing the masks and rendered result.

## Verified product facts and current unknowns

Adobe's [Lightroom desktop documentation](https://helpx.adobe.com/lightroom/desktop/save-share-and-export/save-share-photos.html) describes invite-only shared album links, viewer comments, JPEG download controls, shared images that retain the latest edits, and file export options. Native review could remove the need to build a full gallery. It does not establish that the proposed agent can reliably detect comments, that a comment webhook is available, or that native sharing provides our desired immutable revision history.

[Lightroom Classic documentation](https://helpx.adobe.com/lightroom-classic/desktop/viewing-photos/share-comment-feedback-collaborate.html) also describes shared-collection feedback, but its workflow differs. A read-only application-path search found the cloud-based Lightroom desktop app locally. Its current sign-in state, usable catalog, version, and computer-control reliability have not been inspected. The founder confirmed that either Lightroom edition is acceptable for the prototype. Use the installed cloud-based Lightroom as the first integration target and test its native private albums first.

Native album syncing and exporting files are different operations. Native sharing can handle review; it does not eliminate the explicit final-export-and-cloud-delivery requirement. The destination for final exports remains undecided.

No account was opened, no photo was edited, no review link was created, no invitation was sent, and no comment watcher or recurring automation was started during this exploration. The request describes a capability of the proposed product, not a request to monitor an existing album now.

## Smallest honest architecture

- **Local worker:** Runs alongside Lightroom and maintains an Astra tool loop with screen observation and bounded UI actions. The hackathon product needs a real execution path; the fact that Codex can operate a desktop during development is not itself a runtime integration.
- **Job record:** Stores stable photo identity, source revision, feedback identity, editing status, export identity, and destination. Filenames or current selection alone are insufficient identity checks.
- **Review adapter:** First test native private Lightroom review. If detecting and associating comments is unreliable, a minimal private web gallery provides explicit comment events and immutable revisions. Only build that surface if the native path fails the core requirement.
- **Export/upload adapter:** Confirm export completion and the exact output before uploading through an available cloud API. Use computer interaction where it demonstrates Lightroom work; use ordinary APIs for deterministic file transport when available.
- **Version handling:** Keep a prior editing state or supported copy before applying a revision. Coalesce related comments; do not execute duplicates twice. New comments referring to an older preview must not silently overwrite an approved newer revision.
- **Access and scope:** A private link must enforce restricted access, not just hide an otherwise public URL. Clients may direct edits to the photos made available to them within the photographer's configured scope. Comments cannot broaden computer permissions, expose other photos, or act as arbitrary tool instructions.

“Listening” can be bounded polling in the prototype if native events are unavailable. The local worker must be running with Lightroom accessible. Do not describe this as continuous cloud execution when it depends on a local desktop session.

## One-minute demo to validate

- 0–10 seconds: Three selected RAW photos and a concise campaign brief. Show a prepared first-pass album created during the event.
- 10–20 seconds: In the client review view, enter one scoped correction on one photo.
- 20–45 seconds: Astra detects it, selects the correct photo in Lightroom, changes a small set of controls, and verifies the rendered result. Show actual UI work.
- 45–55 seconds: The revised image appears at the same private review destination with an identifiable new revision. Before/after makes the requested change visible.
- 55–60 seconds: Show a completed export/upload receipt and one compact piece of event-day development evidence.

These timings are targets, not measured latency. If editing and sync exceed the slot, label accelerated footage honestly and use the three-minute stage demo for an uncut roundtrip. Do not pretend a precomputed edit came from a fresh client comment. The shared review view should remain private even though the hackathon video is public; use team-owned sample photos and hide access details.

## First validation gate if selected

Start with one event-owned photo already in Lightroom. A genuine comment should cause the runtime worker to choose that photo, make one reversible exposure adjustment, verify it, and update the review output. Then replay the comment: nothing should be edited twice. Measure latency and verify that a logged-out, unauthorized viewer cannot access the private material.

Do this before gallery polish, RAW ingestion at scale, custom masks, multi-reviewer conflict resolution, or broad integrations. If local runtime control or native comment access fails, record that result and narrow the integration explicitly rather than substituting scripted imagery for the live loop.

## Rubric forecast

| Criterion | Target / 10 | Evidence needed |
| --- | ---: | --- |
| Astra in development | 8 | Timestamped examples of Astra building and debugging the worker, version handling, and verification |
| Astra at runtime | 10 | Client feedback changes actual editing actions and rendered output |
| Live demo | 10 | A review comment visibly travels through Lightroom and returns as a revised photo |
| Technicality | 9 | Reliable asset identity, reversible edits, duplicate prevention, private access, and verified exports |

Conditional target: 92.5/100 using equal 25% weights. No category has been earned by the concept alone. Feasibility is uncertain until the local control and feedback loop work; limiting the first version to three photos and one revision keeps it testable.

## Positioning and boundaries

Adobe already supplies editing and private review, while Imagen and Aftershoot already provide AI photo editing. The proposed contribution is coordination across the entire feedback-to-revision-to-delivery cycle, with the photographer's constraints preserved. This is a differentiation hypothesis, not a claim that no competitor does it.

The user's explicit preference is Lightroom computer use. A separate RAW renderer or generated-image pipeline would not demonstrate that preference. The new event-built contribution should be unmistakable: the operator, feedback state machine, and verification around existing Lightroom functionality.

Remaining choices: native review versus a small custom review page after testing; final cloud destination; sample photos; whether revisions publish automatically within the agreed scope or go through the photographer first. Cloud-based Lightroom is the provisional integration target, not a commitment to broader architecture.

## Pressure test — preserving the photograph and the photographer's control

Added 2026-09-10 after the founder identified the emotional appeal: AI edits the actual photograph through recoverable operations instead of changing its essence. Headshot photographers are the specific customer hypothesis. The following is desk research and product reasoning, not customer validation.

### Three distinct requirements

1. **Recoverability:** The source and earlier revisions remain available. This protects against losing work but does not establish faithfulness; a generated replacement on a separate layer can also be reversible.
2. **Editable working state:** The photographer can inspect and adjust meaningful native controls, masks, and supported layers. Keeping the original plus a flattened edited JPEG is a weaker handoff. Editing one operation independently can require recomputing dependent operations; do not promise arbitrary history surgery without implementation.
3. **Faithfulness to the agreed brief:** Preserve the subject's expression, permanent features, and captured scene according to the photographer's policy. Conventional adjustments can still distort appearance. Neither Lightroom use nor an undo button proves this automatically.

The founder's preference spans all three. A useful promise is: “Client revisions, carried out in your editing workflow, under your rules, with a working edit you can take over.” Avoid claims such as “no pixels changed,” “AI editors are inherently destructive,” or “Lightroom guarantees identity preservation.”

### Evidence supporting the need

[NYC Headshots By Gareth's FAQ](https://headshotsbygareth.nyc/policies/faqs/) discusses natural texture and correcting accidental removal of permanent marks. [San Diego Professional Headshots' service policy](https://www.sandiegoprofessionalheadshots.com/agreement) distinguishes routine retouching from changes to permanent features or facial structure. These are concrete examples of practitioners expressing boundaries around authenticity, not evidence that most photographers reject AI or that they would pay for this product.

### Evidence weakening the novelty claim

- [Imagen markets a headshot workflow](https://imagen-ai.com/solution/ai-headshot-photo-editing-software/) that returns adjustable Lightroom settings and describes it as non-destructive. Its indexed official product text was available; direct page retrieval failed during this research. This is a vendor claim, not a tested integration.
- [Retouch4me Dodge & Burn](https://static.retouch4.me/dodgeburn) offers a Soft Light layer as a non-destructive output.
- [Figma Weave's retouching page](https://www.figma.com/solutions/ai-photo-retouching/) describes layers, masks, color grading, and visible workflow nodes. Treating Weave as a single opaque generative editor would misrepresent it. This does not establish that all underlying generation can be decomposed into Lightroom controls.
- [Aftershoot](https://aftershoot.com/retouching/) already positions itself across editing, retouching, and gallery delivery. “Shoot to delivery” is also an occupied proposition.
- [JarvisArt](https://arxiv.org/abs/2506.17612) researches an agent for Lightroom retouching. Operating a professional editor through an agent is not itself a novel research claim.

These findings challenge a business built only around non-destructive AI photo editing. They do not establish that the complete proposed comment-to-revision loop is already solved. That exact competitive question remains open.

### What would make this product worthwhile

The most promising hypothesis is coordinating revision rounds: interpret a client's request, apply the photographer's rules, make the right native edit, retain an inspectable state, and return the correct revision to the correct review destination. The photographer delegates execution while retaining creative authority.

Computer use is a preferred integration and a strong hackathon demonstration. Buyers may care more about a dependable native working file and time saved than whether sliders were moved through a UI or updated through an API. Preserve the founder's computer-use prototype preference while testing that distinction rather than assuming visible clicking is the business moat.

An initial “develop-only” policy could permit exposure, white balance, tone curves, crop, and local tonal masks while excluding generated replacement content and face reshaping. AI-assisted mask selection can remain within that policy. Retouching of blemishes, flyaways, glasses glare, or clothing is a separate capability question: many real headshot revisions may require tools beyond this initial Lightroom slice. A product promising finished headshot retouching must eventually address those jobs or position its scope more narrowly.

Client comments are scoped requests within a photographer-defined policy. They must not silently expand that policy or become arbitrary computer instructions. This is also a product concern: unrestricted auto-execution could remove the very authorial control the founder values.

### Proposed validation, not yet performed

Recruit five working headshot photographers for a small directional test, including existing AI-editor users and manual retouchers. Do not ask only whether they like reversible editing; ask for the last actual revision round, the tools used, and the work that consumed their attention. No outreach is authorized or performed by this note.

For one consented source image and the same brief, compare their current workflow with a prototype that returns native editable state and handles one client correction. If a generative comparison is included, inspect image quality blind before revealing the workflows, then ask them to perform a follow-up correction using each deliverable. Measure active minutes, correction effort, unintended changes, willingness to delegate publication, and whether they would trial it on a real paid job. Small samples provide direction, not market-size estimates.

Reasons to abandon or narrow the thesis: existing tools already complete their revision rounds; photographers never use the editable handoff; image inspection costs more time than editing; final-JPEG quality and speed dominate workflow control; or most requested changes fall outside the supported toolset.

The strongest hackathon proof of this preference is selective revision: a reviewer asks for less warmth but wants to retain the crop; Astra makes the targeted change in Lightroom and returns a new version, then the photographer takes over the native controls. This demonstrates continuity of authorship more clearly than a dramatic beauty transformation.
