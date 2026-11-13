---
id: MAT-impeccable-routing-planning
title: Impeccable routing Planning evidence
summary: "Separates official host capability documentation, the observed Codex continuation probe and unmet native Impeccable checks for the question-relay proposal."
created_at: 2026-11-13
---

# [MAT-impeccable-routing-planning] Impeccable routing Planning evidence

## Evidence baseline

Planning started from `aa6c51dc3148efba121bc54c8e582a59aacd11d1`. The initial reviewing commit is
`dc2d31a9371647043d9075498fa0b028d7c7b0b1`. Scope is `PROP-uiux-improve-impeccable-routing`; the run-model and
bundle-hygiene proposals are parallel Planning work, not accepted dependencies at this baseline.

## Local evidence

- `CAP-DLV-uiux-improvement` rule 16 (`docs/capabilities/delivery/CAP-DLV-uiux-improvement.md:98`): native skill
  loading, refinement-only child, interactive user session, write pause and brief boundaries.
- `ADR-impeccable-session-authority` Decision Outcome (`docs/decisions/2026-11/20261110-impeccable-session-authority.md:94`):
  answer ownership and interactive routing; its context-file clause at line 77 requires explicit user direction.
- `MAT-uiux-improve-pilot` A1/A2 (`docs/proposals/PROP-uiux-improve-bundle-hygiene/materials/20261113-uiux-improve-pilot.md:48`):
  same-child init phases were observed on Claude Code; only gaps were user-answered, and cache loading bypassed the
  native mechanism. The correction at line 71 attributes likely failure to project enablement but calls it untested.
- The bundle's orchestration reference at
  `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/orchestration.md:106`
  records nested isolated roles for critique. The loaded upstream command, not this static reference, determines
  what nested capabilities a run needs.

## Official-source scout

The read-only scout retrieved the following primary documentation on 2026-11-13:

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), “Resume subagents”: resuming a completed child
  retains its conversation history. “Preload skills into subagents”: available project, user and plugin skills can
  be discovered and invoked through the Skill tool. “Let subagents spawn their own subagents” documents nested
  delegation. These are documented mechanisms, not observations of this consumer's Impeccable setup.
- [Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents), “Custom agents”: skills inherit
  from the parent; the scout found no explicit confirmation of plugin-installed skill reach in a child.

## Bounded live observations

- The current tool and skill catalogs exposed no Impeccable invocation and no Claude Code runtime. No plugin was
  installed, enabled, loaded from its cache or invoked for this check.
- The read-only scout returned marker `relay-probe-c71f`. The caller resumed that exact child identity through
  `collaboration.followup_task`; it returned the retained marker without tools. This confirms only same-child
  continuation in this Codex session. It proves no native Impeccable load, permission handoff, question pause,
  product write or nested Impeccable-role behavior.
- Native Impeccable load in a fresh child on Claude Code with the consumer project enabled: **unmet**.
- Native Impeccable load in a fresh Codex child: **unmet**.
- End-to-end interactive relay (`init`, new work, `shape`, `critique`), including all user answers and required nested
  roles: **unmet**.

The user sets empirical validation to best-effort for this personal project (`by: user`). These unverified live
checks do not hold Planning; observed problems during use can become concrete feedback. Until the relevant
per-run capability checks pass, the command stays in the user session.

## Inbound references supplied to the Challenger

`devkit docs refs CAP-DLV-uiux-improvement --direction in -n 0` returned 16 IDs:
`ADR-impeccable-session-authority`, `ADR-role-worker-subagent`, `ADR-uiux-improvement-workflow-boundary`,
`ARCH-05-2-components`, `CAP-DLV-design-exploration`, `FB-impeccable-autonomy-probe-in-subagent`,
`FB-projection-guard-after-mid-session-install`, `PLAN-uiux-improve-ooux-impeccable`,
`PROP-uiux-improve-bundle-hygiene`, `PROP-uiux-improve-impeccable-routing`, `PROP-uiux-improve-run-model`,
`REC-lightweight-general-subagent`, `REC-uiux-improve-ooux-impeccable`, `SPEC-lightweight-general-subagent`,
`SPEC-uiux-improve-ooux-impeccable`, `UC-improve-an-interface-and-user-flow`.

`devkit docs refs ADR-impeccable-session-authority --direction in -n 0` returned 9 IDs:
`ADR-uiux-improvement-workflow-boundary`, `CAP-DLV-uiux-improvement`, `MAT-uiux-improve-pilot`,
`PLAN-uiux-improve-ooux-impeccable`, `PROP-uiux-improve-impeccable-routing`, `PROP-uiux-improve-run-model`,
`PROP-uiux-improve-ooux-impeccable-target`, `REC-uiux-improve-ooux-impeccable`, `SPEC-uiux-improve-ooux-impeccable`.

Historical specs retain their records. Current targets are the capability/use case, the exact old-ADR pointer and
bundle guidance/tests. Other live proposals retain their own scopes and dependency order.

## Emulated role boundary

Codex role/path enforcement is emulated. Absolute worktree paths, separate per-operation permission requests and
before/after complete-tree snapshots substitute for native enforcement. Scout snapshot and HEAD stayed
`90f9695d37a1d424183e1022763be3dc94856cd7` and `dc2d31a9371647043d9075498fa0b028d7c7b0b1` respectively.
