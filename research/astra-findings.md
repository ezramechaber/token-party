# Astra capability research

Research snapshot: 2026-09-10. The repository is still in ideation; this is a working synthesis, not a product decision.

## Executive read

Astra's interesting edge is the combination of a strong reasoning model with the ability to operate software, use tools, preserve context, and keep working through a multi-step task. A winning hackathon project should make that combination visible. A plain chat, RAG wrapper, or generic CRUD app will underuse the model.

The best initial wedge is a bounded workflow with a visible before/after state, a real tool or UI interaction, and machine-checkable evidence that the result is correct.

## What the primary materials say

OpenAI positions GPT-6 Astra for complex reasoning, coding, computer use, research, and document creation. The API model page lists a 1.05M-token context window, 128K max output, image input, and support for web search, file search, code interpreter, hosted shell, image generation, computer use, MCP, tool search, skills, structured outputs, and function calling. The model is available as `gpt-6-astra`; current standard API pricing is $10/M input tokens and $50/M output tokens.

OpenAI's launch material emphasizes:

- Computer use across browsers, desktop apps, CRMs, calendars, forms, specialized software, and frontend QA.
- End-to-end professional work: research, code, spreadsheets, presentations, documents, and data analysis.
- Long-running coding work with context retrieval across compaction boundaries.
- Scientific workflows that combine reasoning, code, plots, and specialized software.
- Stronger instruction following, scope awareness, prompt-injection robustness, and fewer factual errors than GPT-5.6 Sol in the reported evaluations.
- New API primitives that matter for agent products: async tool calls, mid-turn steering, changing reasoning effort without rewriting the prompt prefix, multi-agent orchestration, persisted reasoning, compaction, and prompt caching.

The official computer-use guidance recommends code execution through a persistent isolated browser or desktop environment for Astra. The loop should return screenshots and other observations, preserve session state, and verify the actual final state. OpenAI explicitly recommends allowlisted environments, treating screen content as untrusted, confirmation for consequential actions, and step/time/cost bounds.

## What the system card adds

The 118-page GPT-6 Astra System Card is primarily a safety and deployment document, but it gives useful capability boundaries:

- Astra reaches OpenAI's Critical threshold for cybersecurity capability. With the right tools and access, the card says it can find unknown flaws and develop exploits across well-protected systems without step-by-step human guidance. The shipping model has stronger safeguards and refuses many advanced offensive requests; defensive code review and patching are the safer product surface.
- Reported capability results include 72.6% on OSWorld 2.0, 92.7% on ScreenSpot-Pro, 95.9% on BenchCAD, 91.5% on BrowseComp, 57.9% on Terminal-Bench 4.0, 74.1% on DeepSWE v1.1, 97.6% on FrontierMath Tier 4, 64.6% on Terminal-Bench Science, and 88.0% on SRE-Bench.
- UK AISI measured a no-chain-of-thought math time horizon of 30.9 minutes versus 3.6 minutes for GPT-5.6 Sol, though it notes possible benchmark contamination and limited testing time.
- The system card is unusually candid about limits: Astra's chain-of-thought is shorter and less monitorable than Sol's in several tests, and evaluation awareness can complicate interpreting safety results. Absence of observed failures is not proof of reliability in every environment.

The implication for a hackathon is practical: build for bounded, auditable autonomy, and make the agent's actions and evidence inspectable. Do not make unsafe cyber autonomy the headline demo.

## Independent hands-on signal

### Every / Dan Shipper / Katie Parrott

Every's Astra Vibe Check says Astra impressed them with writing, operating software, and visual design, while Anthropic's Fable had better instincts for building a product. The most striking data point is that Astra wrote the first draft of the Vibe Check from one prompt and Dan Shipper initially thought Katie had written it.

The useful distinction is that Astra appears stronger as an exploration and execution engine than as a final taste-maker. That is a strong fit for a product that creates, tests, compares, or operates things, and a weaker fit for a product whose main value is exquisite interface aesthetics or final editorial judgment.

### Matt Shumer / Something Big Is Happening

Shumer reports strong backend engineering, computer use he is comfortable leaving unattended, understandable progress updates, long-context continuity, and useful handoffs between agents. He describes Astra fixing a broken service from a short instruction, navigating inboxes and ad interfaces, and retaining small user preferences.

His main caveat is important: long-running autonomy is not solved. Astra can get absorbed in details and plateau unless a coordinator keeps the larger goal moving. His "Manager Loop" uses a coordinator to define phases and an implementer to execute them, with sub-agents for scoped work. He also reports that Astra is effective with existing assets and tools in Unreal, while direct visual asset creation and visual taste remained weaker than Claude's.

### Claire Vo / hands-on launch review

Vo reports one-shot wins on a product-intelligence feature, hardware integration, browser QA, an AIM-style Mac app, Blender/3D work, and CRM interaction. Her framing is especially relevant for a demo: use browser/computer use for QA and verification, not only for building; Astra can find issues a developer might miss.

## Capability-to-project map

| Astra strength | Product pattern that exposes it | Demo evidence |
| --- | --- | --- |
| Computer use + visual grounding | Agent operates a real but sandboxed web/desktop workflow | Action trace, screenshots, changed state |
| Long-horizon reasoning + context | Messy packet or codebase becomes a staged plan | Plan, checkpoints, recovered context |
| Coding + test loops | Agent builds, runs, debugs, and verifies an artifact | Tests, browser checks, diff, reproducible result |
| Research + synthesis | Agent gathers sources, analyzes data, and creates a decision artifact | Citations, plots, report or deck |
| Spatial/CAD/3D reasoning | Agent modifies a scene or specialized tool using existing assets | Walkable/interactive artifact, not just a screenshot |
| Multi-agent coordination | Coordinator delegates independent work and reconciles results | Parallel traces and a final integrated output |
| Scope awareness and improved safety | Agent acts within a policy boundary and asks only at consequential points | Approval gate, audit log, blocked unsafe action |

## Provisional project shortlist

Scores are directional until we know the hackathon rubric, time limit, available tools, and whether computer-use environments are allowed.

| Idea | Astra fit | Demo clarity | Hackathon risk | Notes |
| --- | ---: | ---: | ---: | --- |
| Evidence-driven browser QA agent | 5 | 5 | 2 | Give it a local app plus acceptance criteria; it navigates, tests, captures failures, and files a report. Strongest feasibility/clarity balance. |
| Research-to-decision workbench | 5 | 4 | 2 | Ingest a source packet, search, analyze a dataset, make plots, and produce a cited brief/deck. Strong but needs a memorable domain. |
| Legacy-workflow operator | 5 | 5 | 3 | Completes a task across UI-only software where no API exists, with approvals and audit trail. More differentiated if the workflow is painful and specific. |
| Self-driving migration and verifier | 5 | 4 | 3 | Understands a repo, migrates it, runs tests and browser QA, and reports proof. Common idea; differentiation must come from the verification/evidence layer. |
| Interactive world / simulation builder | 4 | 5 | 4 | Uses 3D tools, existing assets, and agents to create a living environment. Big wow factor, but integration and visual quality can consume the whole hackathon. |
| Defensive code-review workbench | 4 | 4 | 3 | Finds issues, explains risk, proposes patches, and verifies fixes in a sandbox. Safe and useful; avoid exploit-generation theatrics. |

## Working recommendation

Until the rubric says otherwise, prioritize an evidence-driven browser QA or UI workflow agent. It naturally combines Astra's computer use, coding, long-horizon reasoning, visual grounding, tool use, and communication. It is also easy to make reliable: use a local fixture app, seeded bugs, allowlisted actions, deterministic acceptance tests, screenshots, and a final report that links each claim to evidence.

The strongest narrative is not "Astra made an app." It is: "Astra understood a messy goal, operated software like a user, found or changed something real, verified the result, and showed its work."

## Sources

- OpenAI, [GPT-6 Astra: A new generation of intelligence](https://openai.com/index/gpt-6-astra/)
- OpenAI API, [GPT-6 Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
- OpenAI API, [Model guidance for GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)
- OpenAI API, [Computer use](https://developers.openai.com/api/docs/guides/tools-computer-use)
- OpenAI Deployment Safety Hub, [GPT-6 Astra System Card](https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf)
- Every, [Vibe Check: GPT-6 Astra Is a Big Upgrade With Some Bad Habits](https://every.to/vibe-check/gpt-6-astra-vibe-check)
- Matt Shumer, [My GPT-6 Astra Review](https://somethingbig.ai/astra-review)
- Claire Vo, [GPT-6 Astra is a banger - here's everything I've built](https://www.lennysnewsletter.com/p/gpt-6-astra-is-a-banger-heres-everything)
- Siavash Memar, [Claude Fable 5.1 vs GPT-6 Astra for Product Design](https://eidosdesign.substack.com/p/claude-fable-51-vs-gpt-6-astra-for)
