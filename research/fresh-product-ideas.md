# Fresh product directions — September 10, 2026

Status: ideation only. No product selected and no implementation authorized by this note. These concepts were developed for a request to exclude existing repository ideas. Existing concepts were inspected only to identify overlap; none is being advanced here. Scores are editorial forecasts, not judge scores, measured model performance, or claims of market novelty.

## Capability and judging basis

The [event rubric](hackathon.md) weights Astra in development, Astra in the finished project, live demo, and technicality equally at 25%. Seven hours includes recording and submission. Reserve the last hour; a compelling prototype must have a narrow core.

OpenAI's [Astra guide](https://developers.openai.com/api/docs/guides/latest-model) confirms async tool calling and mid-turn steering. Those enable a useful demo pattern: start real work, introduce a new constraint while it is underway, and show completed work surviving the revision. The application still executes tools and manages pending operations. Steering does not automatically cancel stale writes: the app must version requests and validate results before applying them.

The [model page](https://developers.openai.com/api/docs/models/gpt-6-astra) confirms reasoning, coding, image input, structured outputs, and computer use. It does not support native audio/video input; any film concept below supplies selected frames and transcripts and uses a separate media engine. No proposal depends on undocumented perception, instant responses, or proven superiority over older models. Demonstrating an advantage over an earlier model requires an actual comparison.

## Scorecard

Each official column uses 1–10. Total = 2.5 × the sum of the four columns. These are plausible targets for the scoped, working demo described below; an unbuilt concept earns no actual points. Development is deliberately held at 8 for all candidates: the idea alone cannot earn that quadrant. It depends on preserved evidence of Astra's actual implementation and debugging work.

| Candidate | Development | Runtime | Demo | Technicality | Total / 100 | Usefulness / 5 | Originality / 5 | Seven-hour feasibility / 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Black Box — learn an unfamiliar machine by experimenting | 8 | 10 | 9 | 10 | 92.5 | 3 | 4 | 4 |
| Jury-Rig — design the missing part between two objects | 8 | 9 | 10 | 9 | 90 | 5 | 4 | 3 |
| Recut — change the meaning of an edit with continuity constraints | 8 | 8 | 9 | 8 | 82.5 | 5 | 2 | 4 |
| Fold — turn a packing problem into a cut-and-fold structure | 8 | 7 | 9 | 8 | 80 | 4 | 2 | 3 |

Usefulness and originality are judgments about the proposed use case. Feasibility is a separate estimate, not an extra official weight. No customer interviews or runtime spikes have been performed. Scores within five points are effectively tied at this stage.

## 1. Black Box

**Pitch:** Give Astra a machine it has never seen. It experiments, learns how the controls work, and writes the controller that makes it useful.

**User and product:** Makers and instrument developers bringing up an undocumented or miscalibrated device. The first product is an instrument-onboarding workbench that produces a tested controller and a compact experiment record. Its broader promise is reducing the time between connecting an unfamiliar instrument and making it perform a useful operation.

**Hackathon machine:** A browser-based two-axis drawing rig. The agent receives motor-command tools and position measurements. The actual mapping is held in a separate process and hidden from the runtime agent: axes may be swapped, reversed, scaled, or coupled; optional backlash introduces history dependence. The judge chooses a configuration after the agent starts. The system is explicitly a simulated instrument, not evidence of general hardware reliability.

**Demo:** Ask it to draw a star. An initial diagnostic stroke moves the wrong way. Astra chooses bounded probes, compares explanations, fits a mapping with code, and installs a controller. The star emerges correctly. During a subsequent job, change a supported calibration setting; Astra detects the residual error, investigates, and resumes with a revised controller. The surprise is visible acquired competence.

**Astra's indispensable runtime work:** Select informative experiments, revise its hypothesis from measurements, synthesize controller code, and adapt when the evidence contradicts the current model. A deterministic execution layer applies motion bounds and measures error. The model cannot grade its own success or inspect the hidden configuration.

**Seven-hour slice:** One simulated device, a small documented family of hidden transformations, bounded probes, an event trace, controller export, and one withheld drawing. Start with affine transformations; add backlash only if the first version works. Do not build a device marketplace, real robot integration, or general scientific discovery platform.

**Why the rubric likes it:** Runtime reasoning changes the outcome visibly. Technicality comes from hypothesis selection, code synthesis, isolation, and independent measurements. The development story can show Astra finding flaws in the simulator and verifier, with human-reviewed hidden cases.

**What could kill it:** A polished benchmark can still look like a toy. The team must name the instrument-onboarding workflow honestly. A specialized calibration solver may outperform the agent in this narrow family; compare against one to reveal where Astra adds value. Do not claim universal inference from a few probes.

**First 45-minute gate if selected:** Across five judge-selectable configurations unseen by the runtime agent, reach a proposed mean trajectory-error threshold of 3% of workspace width on a withheld shape in four of five trials, using at most eight probes and a target of 45 seconds per trial. Thresholds are proposed acceptance criteria, not measurements. A reliable three-minute demo needs measured latency; the one-minute video should include at least one complete uncut inference-to-action sequence. Drop the mid-job fault if it makes the initial success unreliable.

**Competitive reality:** Autonomous instrument control is an existing research direction; see [Toward Full Autonomous Laboratory Instrumentation Control with Large Language Models](https://arxiv.org/abs/2604.03286). The differentiation hypothesis is an accessible, inspectable onboarding product with adversarial live configuration, not the invention of autonomous labs.

## 2. Jury-Rig

**Pitch:** Objects should not become useless because the one piece connecting them does not exist.

**User and product:** Makers, repair shops, and owners of small household accessories. Supply two measured interfaces and describe the desired relationship. Astra designs the adapter between them, checks the geometry, and exports a fabrication file.

**Demo:** A small desk accessory cannot attach to a shelf. Provide the shelf thickness, accessory mounting dimensions, and forbidden contact surfaces. Astra creates a clip-and-bracket design and shows an exploded fit view. Interrupt: “No screws, and I need the cable to come out underneath.” It revises the structure, reruns checks, and shows the cable path. End by attaching an event-day fabricated version if equipment is available.

**Astra's indispensable runtime work:** Interpret functional intent, select and compose geometric features, reason about assembly access, and revise after check failures. The output is editable constructive geometry, not a rendered image. Deterministic checks cover dimensions, collision, clearances, and export validity; they do not establish material strength or safe load ratings.

**Seven-hour slice:** One class of lightweight accessory mounts, manually entered measurements, a small constructive-geometry vocabulary, a constrained CAD execution environment, and downloadable STL or SVG. Skip photo-to-CAD, arbitrary broken-part reconstruction, and load-bearing applications. A broad repair marketplace is outside scope.

**Why the rubric likes it:** The audience understands the physical problem instantly. Runtime Astra changes actual geometry. CAD validity, parameter provenance, and assembly checks make the technical work legible.

**What could kill it:** The final physical attachment is its strongest proof, and fabrication access is unknown. A beautiful digital fit does not prove a real fit. If no fast fabrication path exists, lower the demo score from 10 to 7, taking its total to 82.5. A fixed clip template with resized numbers is too thin; at least one requirement should change feature arrangement or assembly strategy.

**First 45-minute gate if selected:** Three varied requests within the supported mount family must produce valid geometry and pass independently specified fit/clearance checks, including one structural revision. Establish fabrication time immediately. Do not spend hours beautifying an unverified model.

**Novelty limit:** Text-to-CAD and parametric adapters are established categories. This concept's differentiation is intent across two interfaces plus assembly-aware revision and checked fit. No comprehensive competitor search has been completed for this exact wedge.

## 3. Recut

**Pitch:** Change what a scene means, then let the editor repair everything the change breaks.

**User and product:** Editors turning one source sequence into different narrative versions. A request such as “Make us suspect the courier until the final shot” becomes an editable timeline with shot choices, cuts, captions, and continuity constraints.

**Demo:** Play a short sequence. Change which character appears suspicious, preserve a particular reaction shot, and cap duration at 20 seconds. Astra revises the edit, checks that the revealing shot now occurs after the protected reaction, and exports the new sequence. The audience sees how ordering changes interpretation.

**Runtime:** Astra reasons over selected frames, shot metadata, and an event-day transcript, then writes a timeline for a separate media engine. It checks timing and explicit continuity constraints with code. Human judgment determines whether the narrative effect works.

**Scope:** Eight to twelve team-owned clips, hard cuts, captions, simple audio continuity, and one export format. No generated movie footage, full NLE integration, or claim that Astra directly watches/listens to the raw video.

**Main risk:** Differentiation. [Descript's Underlord](https://www.descript.com/blog/article/underlord-ai-video-editor-primer) already provides conversational video editing. A compelling prototype would need to make narrative dependency handling and protected creative choices its core interaction. Merely asking for a shorter video does not qualify.

**Gate:** Render two meaningfully different edits from the same clips, obey independently checked duration/order requirements, and have a person identify the intended narrative difference without an explanation.

## 4. Fold

**Pitch:** “These three awkward objects need to travel together.” Get the flat sheet that folds into their custom package.

**User and product:** Small-batch sellers packaging kits and irregular combinations of products. Supply simple measured solids, allowed contact regions, and available sheet size. Astra proposes an insert and enclosure, runs geometry checks, then exports an exact-scale cut/fold pattern.

**Demo:** Add an extra object while the design is underway. The insert changes, its panels unfold into a revised sheet layout, and the user folds an event-day sample around the objects.

**Runtime:** Astra composes compartments, dividers, cutouts, and fold choices in response to packing intent. Code checks net overlap, dimensions, and supported fold relationships. Real protection in shipping is untested.

**Scope:** A rectangular enclosure with configurable insert structures, one material, one sheet size, simple solids, and SVG export. No general origami solver or arbitrary collision-free fold planning.

**Main risk:** [Pacdora already offers customizable dielines](https://www.pacdora.com/tools/dieline-generator) and [AI structural packaging workflows](https://www.pacdora.com/tools/ai-structural-packaging-design). The plausible wedge is composing an insert around a combination of objects and assembly constraints. A box generator with an AI prompt would be insufficient. Physical prototyping also consumes time.

**Gate:** Generate and physically fold a correct insert for two different object combinations. A screen-only unfolding animation is not proof of manufacturability.

## Recommendation and evidence plan

Recommend **Black Box** for the first validation spike. It most directly exposes Astra learning from consequences, offers a judge-controlled surprise, and needs no printer, purchased hardware, OAuth, or third-party service beyond model access. Its weak point is the commercial story; the honest first customer is an instrument developer, and the demo proves only the simulated slice.

Choose **Jury-Rig** instead if rapid fabrication is available and the founder prefers a tangible consumer outcome. Its successful physical reveal could be more memorable, but fabrication uncertainty should change the decision, not disappear from the scorecard.

Keep Recut and Fold as lower-priority alternatives. No direction is selected by this recommendation.

For either leader, earn the development quadrant by recording timestamped evidence of Astra implementing the core engine, encountering a real failure, proposing a fix, and passing an independent check. Preserve human decisions and meaningful code changes; do not expose private reasoning or manufacture a debugging story. Separate prepared fixtures, computed outputs, and live model actions in the demo.

An illustrative seven-hour allocation after selection: 45 minutes for the hardest capability gate; 105 minutes for the minimal runtime and deterministic checks; 90 minutes for the main interaction and surprise; 60 minutes for independent evaluation and recovery; 60 minutes for rehearsal and polish; 60 minutes for video, public repository review, and submission. These are planning estimates; actual remaining event time must govern any build.
