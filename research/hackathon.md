# GPT-6 Astra Hackathon NYC

Research snapshot: 2026-09-10. The participant guide supplied to the team is now the authoritative source for event operations and judging. Sensitive access details from that guide—including network credentials and the private community invitation—are intentionally excluded from this open-source repository.

## Executive read

This is a seven-hour build sprint, not an all-day coding window: hacking starts at 10:30 a.m. and submissions close at 5:30 p.m. The submission is a public repository plus a publicly accessible one-minute demo video. A group of OpenAI judges uses those submissions to select five finalists. Finalists receive three minutes for a live demo and two minutes of judge Q&A.

The official rubric is evenly divided:

| Criterion | Weight |
| --- | ---: |
| GPT-6 Astra used during development | 25% |
| GPT-6 Astra used inside the finished project | 25% |
| Live demo | 25% |
| Technicality | 25% |

This corrects two earlier assumptions. The model must matter both **to how the team builds** and **to what the product does at runtime**. And the pitch cannot be a conventional presentation: the guide explicitly demands a demo rather than slides, a Figma file, or another nonfunctional presentation artifact.

The winning shape is therefore an AI-native product, built in a visibly Astra-native way, with sound engineering and a compelling three-minute live transformation.

## Working project assumption: ignore token economics

For ideation and the prototype, token cost is treated as unconstrained at build time and runtime. Use as much reasoning, context, iteration, and agent coordination as materially improves the result. This is a prototype assumption, not a claim about production economics.

The team receives $100 in OpenAI API credits and one month of complimentary ChatGPT Pro Lite access at check-in. The guide says organizers can provide additional Codex credits if needed. Therefore, dollar efficiency is not an optimization target, but actual credit availability, rate limits, latency, reliability, safety, and the finite demo window remain real constraints. See [Project Decisions](./decisions.md).

## Event logistics

| Item | Confirmed information |
| --- | --- |
| Event | OpenAI GPT-6 Astra Hackathon NYC |
| Hosts | OpenAI and Cerebral Valley |
| Date | Thursday, September 10, 2026 |
| Venue | OpenAI's New York office; the street address is retained in the private participant guide rather than this public repository |
| Check-in | A completed Visitly preregistration, unique QR code, and government-issued photo ID are required |
| Preregistration | Visitly email includes an NDA and media release |
| Intended participants | Developers, technical founders, and startup teams |
| Team size | One to four people |
| Hacking window | 10:30 a.m.–5:30 p.m. EDT: seven hours |
| Submission | CV platform entry, public repository, all team members listed, and publicly accessible one-minute demo video |
| Finalists | Five |
| Stage format | Three-minute live demo plus two-minute judge Q&A |
| First prize | $50,000 in credits plus DevDay 2026 tickets |
| Second prize | $25,000 in credits |
| Third prize | $15,000 in credits |
| Finalist prize | One year of ChatGPT Pro for every finalist |

The public event listing originally showed an end time of 10:00 p.m.; the participant guide says doors close at 9:00 p.m. Use the participant guide's schedule.

## Schedule

| Time | Event |
| --- | --- |
| 9:00 a.m. | Doors open and check-in |
| 10:00 a.m. | Welcome and kickoff |
| 10:30 a.m. | Hacking starts |
| 12:00 p.m. | Lunch |
| 5:30 p.m. | Submissions due and dinner |
| 7:00 p.m. | Five finalist demos |
| 7:45 p.m. | Final deliberation and awards |
| 8:00 p.m. | Reception |
| 9:00 p.m. | Doors close |

## Official goal

Build something novel and useful in the real world that makes strong use of GPT-6 Astra's new capabilities. The entry may be either:

- A new product; or
- A new feature for an existing startup, isolated in a repository that can be shared publicly.

All submitted functionality must be built during the hackathon. Existing product code does not qualify.

## Official rules

### Required

- The repository must be public.
- The demo may show only features, code, and functionality built by the team during the event.
- The original contribution must be unmistakable to judges.
- Every team member must be added to the submission.
- The one-minute video must be publicly accessible.
- The team must own or have rights to every code, data, and asset used.
- Projects must comply with applicable laws, ethics, and platform policies.

Failure to distinguish the team's event-day contribution results in immediate disqualification.

### Explicit anti-projects

The participant guide says **strictly no** to:

- AI mental-health advisers.
- Basic RAG applications.
- Basic Streamlit applications.
- Image analyzers.
- “AI for education” chatbots.
- AI job-application screeners.
- AI nutrition coaches.
- Personality analyzers.
- Any AI-generated medical-advice product.
- Any project whose main feature is a dashboard.
- Sports analyzers or coaches.

This is more than a topic blacklist. It signals that generic input → model → text-output experiences, thin wrappers, and passive analytics surfaces are disfavored. A project should perform a distinctive workflow or create a new interactive capability.

## Submission process

Submissions close at **5:30 p.m. EDT** on the [Cerebral Valley submission page](https://cerebralvalley.ai/e/openai-gpt-6-astra-nyc/hackathon/submit).

Required submission components explicitly named in the guide:

1. Project entry on the CV platform.
2. Public repository.
3. Publicly accessible one-minute demo video with screen capture and audio.
4. Every team member attached to the submission.

The video must highlight the specific features, code, and functionality built during the hackathon. The guide suggests QuickTime, Loom, Cap, or an equivalent recorder, and a public host such as YouTube, Loom, or a public Drive link.

### One-minute video structure

Because this video determines whether the project reaches the stage, treat it as the first-round pitch:

1. **0:00–0:08 — Problem and user.** One sentence.
2. **0:08–0:15 — Why Astra.** Name the capability that makes the product possible.
3. **0:15–0:48 — Product working.** Show the complete transformation with minimal narration.
4. **0:48–0:56 — Technical proof.** Show the action trace, evaluation, verified output, or architecture.
5. **0:56–1:00 — Outcome.** Restate the value in concrete terms.

## Judging process

### Round one: submission review

After the 5:30 p.m. deadline, a group of judges from OpenAI reviews the projects and one-minute videos. They select the five projects they consider most interesting, useful, creative, and technically ambitious.

The participant guide does not name these OpenAI screening judges. The public event page separately names Avery Klemmer, Sriram Krishnan, and Adina Tecklu as members of a judge panel; it does not specify exactly which round each person judges.

### Round two: finalist stage demos

At 7:00 p.m., each of five finalists receives:

- Three minutes for a live demo.
- Two minutes for judge Q&A.

After all five demos, the judges deliberate and choose first, second, and third place.

## Official judging rubric

### GPT-6 Astra in Development — 25%

Questions in the guide:

- How did the team use the model to build the project?
- Did the team efficiently leverage new features and capabilities?
- How did the team work with the model during development?

Evidence to preserve:

- A concise build log with timestamps and milestone outcomes.
- Codex task/thread history or selected screenshots.
- Examples of parallel work, skills, tool use, testing, or model-assisted debugging.
- A before/after example showing Astra improving the implementation.
- A clear account of which work the humans directed and which work Astra executed.

Do not leave this story until the end. Capture evidence continuously during the build.

### GPT-6 Astra in Project — 25%

Questions in the guide:

- How does the finished project use Astra?
- Does it use new features to unlock advanced capability?
- Is it a novel use of the model?

The central product outcome should disappear if Astra is removed. Using Astra for a decorative summary or chat sidebar is unlikely to maximize this category.

### Live Demo — 25%

Questions in the guide:

- Is the concept novel?
- Is it presented and demonstrated well?
- Is it cool to watch?
- Is it truly a demo rather than a presentation, Figma file, or another substitute?

The product must visibly do something. Design around a single irreversible or surprising moment: messy intent enters, Astra reasons and acts, real state changes, and the product proves the result.

### Technicality — 25%

Questions in the guide:

- How well is the idea implemented?
- How technical are the usage and implementation?
- Does the project demonstrate sound engineering?

Technical complexity should be legible. Expose the architecture, agent/tool loop, verification, failure handling, or evaluation evidence without consuming the live demo with a code tour.

## Strategy implied by the rubric

### Score all four quadrants

A project can lose despite being a good product if it neglects how Astra was used to build it. Conversely, an impressive Codex development story cannot compensate for a finished product in which Astra is peripheral.

| Weakness | Likely consequence |
| --- | --- |
| Astra absent from development story | Leaves 25% largely uncontested |
| Astra absent from runtime product | Looks like an ordinary product built with AI |
| Slides or static mockup dominate | Violates the explicit demo-first expectation |
| Clever demo with fragile or shallow implementation | Loses technicality points |

The target is not merely “built with AI” or “an AI product.” It must be both.

### Optimize for the first-round video first

The stage demo does not matter unless the one-minute video reaches the top five. By 4:30 p.m., the team should have a reliable golden path and begin recording. Use the last hour for the final recording, repository cleanup, submission checks, and contingency—not for a new feature.

### Prefer action over analysis

Several banned archetypes are passive analyzers, advisers, chatbots, or dashboards. Favor a product that acts, creates, operates, coordinates, tests, negotiates, modifies, or verifies something in a bounded environment.

### Make the build process judgeable

Add a short `BUILD_LOG.md` or equivalent to the repository. Record:

- Start state and initial idea.
- Major prompts or task delegations.
- Where Astra chose an approach, generated code, found a bug, or verified behavior.
- Pivots and failures.
- Final architecture and tests.

This artifact directly supports 25% of the rubric and helps prove the work was completed during event hours.

## Closest historical precedent

The September 2025 GPT-5 Startup Hackathon NYC was also run by OpenAI and Cerebral Valley for startup teams in New York. Its winners were:

1. **Bell Hop** — an AI chief of staff for boutique hoteliers.
2. **Fathom** — a voice-first AI assistant for understanding codebases.
3. **Ego** — a consumer tool for maximizing credit-card rewards.

Sources: [OpenAI for Startups winner announcement](https://www.linkedin.com/posts/openai-for-startups_200-startup-teams-were-able-to-ship-fast-activity-7379230155635892224-yv0_), [Cerebral Valley project gallery](https://cerebralvalley.ai/e/gpt5-nyc/hackathon/gallery), and [event announcement](https://cerebralvalley.beehiiv.com/p/announcing-our-gpt-5-startup-hackathon-in-nyc).

First-place Bell Hop performed concrete hotel operations—analyzing performance, creating landing pages, writing pricing algorithms, and managing tasks—from natural-language input. The team attributed the working actions to GPT-5 and Codex generating code and API calls. Source: Rami Zeidan, [Bell Hop build recap](https://www.linkedin.com/posts/ramiazeidan_this-past-weekend-we-participated-and-won-activity-7379265479733043200-7OXI).

The prior podium supports an AI-native product strategy, while today's official rubric adds the missing nuance: model-native development is independently worth another 25%.

## Three-minute stage-demo architecture

1. **0:00–0:15 — User and pain.** Name one person and one costly or frustrating job.
2. **0:15–0:30 — Why Astra.** Explain why this needs reasoning, tools, context, or computer interaction.
3. **0:30–2:15 — Live transformation.** Run one golden path. Keep state changes obvious and narration sparse.
4. **2:15–2:35 — Proof.** Show verification, tests, citations, or measurable before/after evidence.
5. **2:35–2:50 — How Astra built it.** Show the strongest development-process artifact.
6. **2:50–3:00 — Close.** Restate the user outcome and larger product wedge.

## Likely Q&A

- What can Astra do here that an older or smaller model cannot?
- How exactly did Astra accelerate or change the development process?
- Which functionality was built during today's hacking window?
- Is the runtime workflow genuinely autonomous or hard-coded for the demo?
- How is the result verified?
- What happens on ambiguous input or a failed tool call?
- Who urgently needs this, and what do they use today?
- Is this a feature or a durable product?
- How do permissions, sensitive data, and consequential actions work?
- What are the latency and operational constraints?

Under the current project decision, answer cost questions honestly but briefly: economics were deliberately not optimized for the prototype; the team first maximized capability and will optimize routing, caching, and model choice after proving the workflow.

## Day-of checklist

### Before hacking starts

- [ ] Complete Visitly preregistration, NDA, and media release.
- [ ] Bring the Visitly QR code and government-issued photo ID.
- [ ] Confirm every teammate has access to the participant Discord and required OpenAI resources.
- [ ] Confirm API credit and ChatGPT/Codex access after check-in.
- [ ] If already paying for the $200/month ChatGPT Pro plan, do not redeem the Pro Lite promotion; the guide warns that doing so will void the existing subscription.
- [ ] Ask organizers about additional Codex credits if needed.

### Build for eligibility

- [ ] Create a fresh, isolated public repository after hacking begins.
- [ ] Add an open-source license compatible with every dependency and asset.
- [ ] Maintain a timestamped build log.
- [ ] Keep employer code, data, designs, credentials, and nonpublic information out of the project.
- [ ] Make event-day contributions explicit in the README and video.
- [ ] Ensure the concept is not one of the prohibited anti-projects.

### Build for submission

- [ ] Freeze the golden path by approximately 4:30 p.m.
- [ ] Record a one-minute screen-and-audio demo.
- [ ] Test the video URL in a logged-out/private browser session.
- [ ] Test the repository URL without authentication.
- [ ] Add every teammate to the CV submission.
- [ ] Submit before 5:30 p.m.; do not rely on a last-minute upload.

### Build for stage reliability

- [ ] Rehearse one three-minute live golden path repeatedly.
- [ ] Prepare a two-minute Q&A division among teammates.
- [ ] Keep a known-good starting state and fast reset path.
- [ ] Cache or locally fixture every network-sensitive dependency where permitted.
- [ ] Make progress visible and eliminate unexplained dead air.
- [ ] Keep the successful one-minute recording available as backup evidence.

## Remaining unknowns

The participant guide still does not specify:

- The identities of the OpenAI judges performing first-round screening.
- Whether the three publicly named VC judges all participate in the final round.
- The exact review interface or any repository fields beyond those described above.
- A mandated open-source license.
- Whether prerecorded video may replace a failed live demo; assume it cannot.

Resolve these through the official participant channels if they affect the build.

## Sources

1. OpenAI and Cerebral Valley. “OpenAI GPT-6 Astra Hackathon Participant Guide.” Supplied participant-only page, accessed September 10, 2026. Sensitive access credentials omitted from this repository.
2. Cerebral Valley. [“GPT-6 Astra Hackathon NYC.”](https://cerebralvalley.ai/e/openai-gpt-6-astra-nyc) Accessed September 10, 2026.
3. Cerebral Valley. [GPT-6 Astra Hackathon NYC submission page.](https://cerebralvalley.ai/e/openai-gpt-6-astra-nyc/hackathon/submit) Accessed September 10, 2026.
4. OpenAI. [Codex app.](https://chatgpt.com/codex/)
5. OpenAI API. [Latest-model guidance.](https://developers.openai.com/api/docs/guides/latest-model)
6. OpenAI API. [GPT-6 Astra migration quickstart.](https://developers.openai.com/api/docs/guides/latest-model#gpt-6-astra-migration-quickstart)
7. OpenAI for Startups. [2025 NYC winners announcement.](https://www.linkedin.com/posts/openai-for-startups_200-startup-teams-were-able-to-ship-fast-activity-7379230155635892224-yv0_) 2025.
8. Cerebral Valley. [“GPT-5 Startup Hackathon NYC” project gallery.](https://cerebralvalley.ai/e/gpt5-nyc/hackathon/gallery) September 27, 2025.
9. Rami Zeidan. [Bell Hop first-place build recap.](https://www.linkedin.com/posts/ramiazeidan_this-past-weekend-we-participated-and-won-activity-7379265479733043200-7OXI) 2025.
