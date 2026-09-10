# Back 2 Back — submission form draft

Prepared from the user-supplied form screenshot on September 10, 2026. Proposed separate submission; final text should match the recorded demo.

## Project Description

Back 2 Back is a DJ partner that explores how far Astra can go with musical judgment. Built by a former DJ, it keeps the human in charge of song selection and taste. Each uploaded track is analyzed for estimated beats, key, and promising transition points and lengths. Astra reasons over that evidence to program the set, select eight- or sixteen-bar handoffs, explain its choices, and assess listener requests for musical fit. A real two-deck audio engine performs the mix, with manual takeover available throughout. The experiment is whether model reasoning can become a transition worth listening to.

## Describe your use of OpenAI products to build the submitted project.

I used GPT-6 Astra in Codex to develop the audio-analysis pipeline, browser mixer, request workflow, tests, and interface. Development crossed coding, browser inspection and Blender scene work; ChatGPT Image supplied visual concepts. I supplied references, musical feedback and corrections, using listening and visible results to guide iteration.

Astra also runs inside the product through the Responses API. It receives track metadata, measured song maps and valid transition options, then chooses a set order and specific handoffs with musical explanations. A separate Astra decision evaluates listener requests against the set's style and energy. Numerical signal processing estimates beats, key and cue evidence; Astra reasons over those measurements, and the audio engine handles timing. This separates model judgment from real-time execution while retaining human control.

## Provide feedback from your experience using OpenAI products.

Suggested wording for the user's review:

Astra was most useful when I could turn subjective feedback into a concrete target: this transition feels wrong, this intro has no drums, or this render does not match the reference. The build combined code, browser inspection, audio diagnostics and visual iteration. It still needed a human ear and repeated checks: correct timing alone did not make a good mix, and an attractive concept did not guarantee a matching implementation. Better continuity between reference images, generated scenes and live UI would help, as would clearer separation between measured evidence and a model's interpretation.

## Evidence before final submission

A real Astra API call and the structured planning/request code are documented. The final video must show a verified integrated decision-to-playback sequence. Avoid claims of direct raw-audio listening or exhaustive superiority to established DJ software. Keep any competitor references deferred as requested.

## Team and links

Team name: Token Party. The supplied form screenshot shows Ezra Mechaber as a member. Public GitHub repository URL and one-minute demo URL still need to be inserted and verified. The screenshot does not establish that multiple submissions are permitted. No form fields were filled or submitted by this session.
