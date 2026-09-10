# Design Tutor

Started: 2026-09-10 11:44:18 EDT (15:44:18 UTC).
Status: idea generation only. No code, prototype, or Figma work authorized or performed.

## The idea

Drop in a demo website. An agent uses computer control to recreate it in Figma, then walks you through how it built the design and the principles behind its choices.

The useful outcome is an editable example you understand well enough to change yourself. The reconstruction gives every explanation a concrete object: this heading, this gap, this group of cards.

Confirmed by the user: website input, computer-use reconstruction in Figma, and a step-by-step explanation of the process and design principles. Audience, exact input format, interaction model, technical architecture, and implementation budget remain open. “Design Tutor” is a working name.

## Three versions to explore

These are concept judgments, not market research or validated feasibility estimates.

| Version | Concrete experience | Usefulness hypothesis | Originality hypothesis | Hackathon feasibility | Astra demonstration |
| --- | --- | --- | --- | --- | --- |
| Watch it build | Submit a URL; watch the agent construct a section; replay a few meaningful steps with explanations tied to selected Figma layers. | Helps someone connect a polished reference to the operations needed to produce it. | Narrated reconstruction alone may have limited differentiation; no competitor check yet. | Narrowest scope, though reliable Figma control remains untested. | Visible perception, planning, action, and correction. |
| Build it with me | Agent creates the structure, pauses, and asks the learner to reproduce one operation before continuing. | Practice could expose misunderstandings that passive viewing misses. | Shared control could be distinctive if the agent responds to the learner's actual edits. | More demanding: detecting edits, checking results, and resuming safely. | Agent observes an unexpected learner action and adapts the lesson. |
| Change one thing | Reconstruct the reference, then compare a deliberate variation: equal heading sizes, reduced spacing, or two equally prominent buttons. Explain the effect and restore or keep it. | Helps a learner understand why a decision matters and apply it elsewhere. | The combination of reconstruction, editable experiments, and situated explanation is the differentiation hypothesis. | A plausible second step after one reliable reconstruction; limit it to one principle. | Agent performs an experiment and connects an observable result to a design principle. |

Proposed direction for discussion: start with **Watch it build**, then add one **Change one thing** experiment. Preserve **Build it with me** as a separate possibility; it adds a harder interaction loop. No direction has been approved for implementation.

## What a good lesson could feel like

Example reference: a simple landing-page hero with navigation, headline, supporting copy, a primary button, and an image.

1. Show the reference and identify the section being recreated.
2. Build the large layout groups in Figma. Explain how grouping separates navigation from the main message.
3. Add editable text and establish type hierarchy. Point to the specific size and weight differences that guide reading order.
4. Set spacing and alignment. Select the relevant objects so the explanation can be checked directly.
5. Add the primary action and image. Explain relative emphasis and how the composition balances text and imagery.
6. Compare the reconstruction with the reference; disclose approximations and correct one visible mismatch.
7. Replay selected construction steps with short explanations, then try a controlled variation: give the supporting copy the same prominence as the headline.
8. Ask the learner what changed about where their eye goes first; restore the original hierarchy and invite one similar edit on a new example.

Keep three kinds of statements separate: what is visible in the source, what the agent actually did in Figma, and its interpretation of why a design choice might work. Do not claim to know the original designer's intent. The teaching record should follow actual operations and outcomes, including corrections, rather than inventing a flawless retrospective process.

## Smallest convincing experiment, if selected

- One user-supplied or team-owned demo page, one desktop viewport, one hero section.
- Native editable frames, text, and shapes in Figma; a flat screenshot does not establish reconstruction.
- A short record of meaningful construction steps connected to the affected objects.
- Three grounded explanations: hierarchy, spacing/grouping, and emphasis.
- One reversible design variation with a visible before/after.
- A learner can select and edit the headline or button after the agent finishes.

Defer full-page fidelity, arbitrary sites, responsive reconstruction, animation, whole design systems, voice avatars, course libraries, and progress dashboards. These are proposed scope exclusions, not permanently rejected ideas.

## One-minute demo concept

| Time | Show |
| --- | --- |
| 0–8 seconds | Reference website: “I like this design, but I don't know how to make it.” |
| 8–30 seconds | Agent builds the hero in Figma. If accelerated, label the recording and report actual elapsed time. |
| 30–43 seconds | Select the headline and replay the step that established its hierarchy, with a brief explanation. |
| 43–55 seconds | Agent changes one hierarchy decision; show the effect, then restore it. |
| 55–60 seconds | Learner edits the real Figma object and applies the principle. |

The demo must show functioning software performing the workflow. The resulting Figma file is an output, not a substitute for the working product.

## Hackathon fit and unresolved risks

The [event guide](../research/hackathon.md) explicitly prohibits “AI for education” chatbots and image analyzers. This concept sits close enough to that boundary that eligibility remains an open question. Its proposed substance is an agent operating a real design tool, producing editable work, and supporting practical experiments. That distinction does not establish organizer acceptance.

| Rubric component | Evidence a future build would need |
| --- | --- |
| Astra in development — 25% | Timestamped build decisions, debugging, and verified milestones. This note records ideation only. |
| Astra at runtime — 25% | Product-triggered inspection, reconstruction, explanation, and response to a changed design. A manually operated development session alone is insufficient. |
| Live demo — 25% | Recognizable reconstruction, visible native edits, and one understandable design experiment. |
| Technicality — 25% | Reliable control, structured editable output, verification, and explanations tied to observed actions. |

The hardest feasibility question is whether computer use can create and revise a small native Figma layout reliably within a useful waiting time. Tool access, UI behavior, runtime integration, font/assets availability, reconstruction quality, and replay support have not been investigated or tested. No current product/API capability is assumed here.

The learning question is equally important: does the user leave able to perform a similar edit independently? An impressive copy operation alone would not establish that outcome. Exact visual fidelity and an understandable construction process may also conflict; the first experiment should expose that tradeoff.

## Decisions still open

- Who is this first for: a Figma beginner, a developer learning visual design, or a designer studying references?
- Does “drop a website” mean a URL, a screenshot, or a supplied local demo?
- Should the learner watch first, participate during construction, or experiment afterward?
- How close must the reconstruction be to feel useful, and how long will the learner wait?
- Is the concept acceptable under the event's education-chatbot restriction?

Possible next step, only after choosing to proceed: select one reference and storyboard its reconstruction and one design experiment. Then validate native Figma control before deciding on architecture. No implementation has started.
