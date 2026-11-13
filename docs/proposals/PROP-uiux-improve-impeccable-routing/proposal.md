---
id: PROP-uiux-improve-impeccable-routing
title: Impeccable question and load routing for app-uiux-improve
summary: Decides whether app-uiux-improve may relay an Impeccable command's question round through the coordinator with the user confirming every answer, and how a child loads a plugin-installed Impeccable, partially superseding ADR-impeccable-session-authority.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
depends_on: [PROP-uiux-improve-run-model]
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
  excludes:
    - packages/devkit-dist/
    - packages/devkit-spec/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-uiux-improve-pilot-fit
workflow: sdd-proposal
---

# [PROP-uiux-improve-impeccable-routing] Impeccable question and load routing for app-uiux-improve

## 1. Background & Hypothesis

`CAP-DLV-uiux-improvement` rule 16 and `ADR-impeccable-session-authority` route Impeccable's interactive commands
(new work, `init`, `shape`, `critique`) to a session the user operates, because "no actor answers on the user's
behalf", and let a fresh child run only refinement commands loaded through the host's skill mechanism, returning a
load failure as a blocker. Findings A1 and A2 in `MAT-uiux-improve-pilot` test both clauses. Split from
~~`PROP-uiux-improve-pilot-fit`~~ (drafted in `6902170e9`, deleted in this split) with
`PROP-uiux-improve-bundle-hygiene` and `PROP-uiux-improve-run-model`. The user set the delivery order: after
`PROP-uiux-improve-run-model` (`depends_on`) and before `PROP-uiux-improve-bundle-hygiene`, which depends on this one.

- A1, question round. The pilot split `init` in a child. Phase 1 scanned and drafted the question round without
  writes. The coordinator pre-filled answers from the consumer's OOUX documents and asked the user only the gaps.
  Phase 2 resumed the same child to write. As run, the coordinator answered the pre-filled questions for the user,
  which the ADR forbids; it would comply only if the user confirmed every pre-filled answer, not only the gaps.
- A2, load route. A fresh Claude Code child did not list the plugin-installed Impeccable, and the child read
  `SKILL.md` and `reference/*.md` from the plugin cache instead (twice in the first pilot, once more in a second run).
  Correction to the earlier reading: the Claude Code documentation says subagents can discover and invoke plugin
  skills through the Skill tool wherever the plugin is enabled. In the consumer, the plugin was enabled for a
  different project only, and the coordinator session did not list it either. The failure was most likely
  enablement scope, not a host limit on children; this is not yet tested live. The cache read is an undocumented
  workaround: it skips the Skill tool, progressive loading and the enablement policy, and depends on the cache
  layout. Codex documentation says skills inherit from the parent but does not cover plugin skills in subagents.

Hypothesis: a relayed route where the user confirms every answer keeps the user deciding every answer while saving
the separate user-operated session, and a properly enabled plugin removes the need for any file-read fallback.

## 2. Technical Spike Questions

- **Q1 (main)**: May the coordinator relay an interactive command's question round from a child? Conditions to
  settle: the user confirms every pre-filled answer, not only the gaps, and each pre-filled answer cites its source
  document; the route is gated on the host's ability to resume the same child (Claude Code observed; Codex
  unverified, needs a live check), with the user-operated session as the fallback; answers that write `PRODUCT.md`
  or `DESIGN.md` still need the user's explicit direction (rule 19). Does it extend to `shape` and `critique`, which
  run two isolated sub-agents?
- **Q2**: Load route. With the plugin enabled for the consumer project, does a fresh child load Impeccable through the
  Skill tool on Claude Code, and on Codex? Run a live check on both before deciding. Is any file-read route
  acceptable, or does the skill keep "load through the host's skill mechanism, otherwise return a blocker" and add
  an enablement check to the blocker report?
- **Q3**: Supersession scope. Which clauses of `ADR-impeccable-session-authority` does a new ADR partially supersede
  (the routing clause for Q1; the load clause only if Q2 changes it), and what stays (consumer authority as amended by
  `PROP-uiux-improve-run-model`, if accepted)?

## 3. Proposed Design & Impact

Directions, not final wording; Planning settles each.

1. Relayed question route. Two phases in one resumable child: phase 1 scans and drafts the question round without
   writes; the coordinator shows every question with its pre-filled answer and cited source, and the user confirms or
   changes each one; phase 2 resumes the same child to write. Without resume support, the existing user-operated
   session applies.
2. Load route. Keep the host skill mechanism as the only named route. When a child cannot see the skill, the blocker
   report names plugin enablement for the current project as the first thing to check. Record the cache read in the
   ADR's consequences as an observed workaround, not a sanctioned route.
3. A partial supersession of `ADR-impeccable-session-authority` for the routing clause, and rule 16 rewritten to
   match.

Impact: `CAP-DLV-uiux-improvement` rule 16 (and rule 10 if the blocker text changes),
`UC-improve-an-interface-and-user-flow`, one new ADR, the bundle's `SKILL.md`, `references/orchestration.md` and
README, and `test_app_uiux_improve.py`. Upstream Impeccable behaviors seen in the same runs are recorded as upstream
feedback (`FB-impeccable-autonomy-probe-in-subagent`, `FB-impeccable-context-target-no-visual-implementation`,
`FB-impeccable-audit-storage-write-missing`), not here.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to `sdd-spec-feature` on
  `dev-uiux-improve-impeccable-routing`. The proposal is deleted there and its decision becomes the partially
  superseding ADR.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
