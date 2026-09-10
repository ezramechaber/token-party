# Project usage

Each project lives in its own subfolder. Record starting usage and an agreed budget when a project starts. Preserve original baselines; append timestamped updates. Commit relevant changes after each completed demo.

## Active projects

| Project | Folder | Status | Started | Usage at start | Project budget |
| --- | --- | --- | --- | --- | --- |
| Back 2 Back | `b2b/` | Implementation underway | 2026-09-10; exact start time not recorded | Unknown — no starting snapshot recorded | Not set; prior repository default treats token cost as unconstrained |
| Roundtrip | `roundtrip/` | Lightroom demo built; further workflow work open | 2026-09-10; exact start time not recorded | Unknown — no starting snapshot recorded | Not set; prior repository default treats token cost as unconstrained |

Existing project planning and demo history remain linked from [the activity log](research/activity-log.md). Roundtrip's private demo assets currently live in ignored `.local-demo/fuji-portrait/`; they must remain excluded from commits. This register does not imply either project has a completed autonomous runtime.

## Usage observations

| Observed at | Scope and metric | Measured usage | Notes |
| --- | --- | --- | --- |
| 2026-09-10 11:43 EDT (15:43 UTC) | Account-wide Codex quota, 10,080-minute (7-day) window | 9% used; 91% remaining | Read from Codex usage limits while establishing this register. Both projects already existed, so this is not a starting baseline or project-specific consumption. Token counts unavailable. |

For new projects, capture usage before implementation and record the budget with explicit units (for example tokens, quota percentage points, dollars, or elapsed time). Record an explicitly agreed unlimited budget as such; an unset budget is not an agreed unlimited allocation. Account-wide quota changes can include other work and resets and must not be attributed entirely to one project.

## 2026-09-10 12:16 EDT — Roundtrip runtime session

User authorized up to 15% of weekly credits for Roundtrip development. Interpreted conservatively as 15 percentage points above the measured 9% account-wide weekly usage at the start of this continuation, with a 24% total ceiling. This is a continuation baseline, not the original project-start measurement. Checkpoints during work: 15%, 17%, and 18% used (latest read at approximately 12:13 EDT). The window is 10,080 minutes. Concurrent project work shares the account; these changes cannot be attributed entirely to Roundtrip. No reset consumed.

Roundtrip now has one verified autonomous local Lightroom revision and a privately published remote inbox. External reviewer access and the production remote pickup test await approval. See [build log](roundtrip/build-log.md).

## 2026-09-10 12:17:02 EDT — Back 2 Back baseline reconciliation and demo

The initial register marked Back 2 Back's baseline and budget unknown. The project's contemporaneous [build log](b2b/docs/build-log.md) recorded **9% weekly used before implementation** on September 10 (exact baseline timestamp unavailable), with the user's cap of **20 percentage points** of weekly allowance. Preserve the earlier register observation as historical; this entry supplies the missing project record. Baseline-plus-budget boundary: 29% total used; conservative working stop: 26%.

At **12:15:10 EDT** and **12:17:02 EDT**, Codex reported **19% used, 81% remaining**, in the 10,080-minute weekly account window. Observed change since baseline: +10 percentage points account-wide, including concurrent projects and reporting lag; this is not Back 2 Back's exact consumption. No resets redeemed. Daily chats, turns, tokens and tool-call totals are unavailable.

Status: local two-deck prototype demonstrated with 13 privately held tracks, a completed eight-bar loaded-pair audition, and a waveform inspector. Eleven tests passed in 2.07 seconds. Runtime Astra awaits an API key; human musical-quality review and sustained full-crate Auto remain open. Blender/3D deck is a future presentation direction.
