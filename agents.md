# Agents Guide

## Project

This repository contains multiple open-source hackathon projects exploring what can be built with ChatGPT 6 and Astra. Back 2 Back, a DJ program, and Roundtrip, a Lightroom workflow experiment, are separate projects; preserve each project's work and decision history.

## Repository organization, usage, and commits

- Each project must live in its own subfolder (currently `b2b/` and `roundtrip/`). Keep project-specific code, dependencies, documentation, and demo assets together. Shared repository guidance and cross-project research may remain at the top level or in `research/`.
- Maintain the top-level `usage.md` as the register of active projects. At each project's start, record its name, folder, status, start timestamp, measured starting usage (including the metric and measurement window), and agreed project budget with units.
- Usage limits are account-wide; do not present them as per-project token counts. If historical starting usage or a budget was not recorded, mark it unknown or not set rather than inventing it. Preserve baseline entries and append later measurements or budget changes with timestamps.
- Commit after each completed demo. Verify the demo, update its activity and usage records, and commit the relevant project changes with a descriptive message. Exclude secrets, private media, and unrelated unfinished work.

## Current phase: Back 2 Back implementation

- The user selected Back 2 Back as the next project: a small-crate DJ program for 4/4 house, with manual controls and automatic phrase-aligned transitions.
- See `b2b/docs/plan.md` for scope and `b2b/docs/build-log.md` for actual implementation, verification and weekly-usage checkpoints.
- Current implementation: local Python/FastAPI service, NumPy/SciPy feature analysis, FFmpeg tempo preparation and a browser Web Audio mixer. Personal tracks and caches belong in ignored `b2b/.b2b/`.
- User budget: no more than 20 percentage points of weekly Codex allowance from the measured 9% baseline. Conservative stopping point: 26% total weekly usage. Inspect usage before further substantial work and log checkpoints; do not redeem resets.
- Runtime API key will be configured later. Rule-based operation must remain explicit; do not label it as runtime Astra.
- Future direction: Blender-built 3D deck driven by the same real audio controls, after playback is verified.
- Preserve earlier Lightroom experiments as separate work. Prioritize a two-track audible transition before expanding the crate.
- Initial mix rules: clean club intros/outros, matched 8- or 16-bar overlaps, linear channel fades and low-EQ swaps. Separate measured audio timing from Astra's runtime planning.

## Ideation conventions for future changes

- Do not assume a product, audience, or technical architecture before it is agreed.
- Generate multiple concrete ideas before converging on one.
- Evaluate ideas for usefulness, originality, feasibility during a hackathon, and how clearly they demonstrate ChatGPT 6 and Astra.
- Keep experiments small and reversible until a direction is selected.
- Record important decisions and rejected alternatives in the repository as the project takes shape.

## Confirmed hackathon constraints

- The build window is seven hours: 10:30 a.m.–5:30 p.m. EDT on September 10, 2026.
- Submit a public open-source repository and a publicly accessible one-minute demo video by 5:30 p.m.
- Only features, code, and functionality built during the event may be demonstrated; make the original contribution explicit.
- Five finalists receive three minutes for a live demo and two minutes of judge Q&A.
- The official rubric is evenly weighted: GPT-6 Astra in development (25%), GPT-6 Astra in the finished project (25%), live demo (25%), and technicality (25%).
- The project must be both built with Astra and AI-native at runtime. Preserve a timestamped build log and evidence of Astra's role during development.
- Do not build one of the prohibited anti-projects listed in `research/hackathon.md`; generic RAG/chatbot/analyzer/dashboard concepts are especially risky.
- Treat token economics as unconstrained by default, while respecting any project budget recorded in `usage.md`, actual credits, rate limits, latency, reliability, safety, and the live-demo window.
- Never commit participant credentials, private community links, employer secrets, or other nonpublic information.

## Open-source expectations

- Prefer clear, approachable code and documentation.
- Avoid committing secrets, private data, or machine-specific configuration.
- Make setup and usage reproducible for someone discovering the repository.
- Use licenses and third-party dependencies that are compatible with an open-source release.

## Collaboration conventions

- Inspect the existing repository before changing it.
- Explain assumptions when the project direction is ambiguous.
- Make focused changes and preserve unrelated user work.
- Verify changes with the lightest appropriate checks, and report what was verified.
- Keep this guide updated when the project’s goals, architecture, or workflow become clearer.

## Project memory and activity log

- Maintain a lightweight, human-readable log or wiki in the repository so someone can understand what the team is doing and how the project is evolving.
- After each substantive work session, record the date, current objective, notable work completed, decisions and rejected alternatives, open questions, and likely next steps.
- When the necessary telemetry is available, include daily activity statistics such as chats, turns, tokens, tool calls, files changed, or time spent. Clearly distinguish measured values from estimates and mark unavailable data rather than inventing it.
- Keep entries concise, append-only where practical, and free of secrets, private chat content, or other sensitive data. Prefer summaries and aggregate statistics over raw transcripts.
- Until the project chooses a dedicated wiki or data store, use a simple Markdown file such as `research/activity-log.md` and link out to longer decision or research notes as needed.

## Suggested next step

Prepare two or three representative MP3s, verify their beat grids and phrase boundaries, and prove one audible transition using the Back 2 Back plan before expanding scope.
