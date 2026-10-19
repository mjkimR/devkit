---
id: FB-effort-procedure-restated
title: The activity-effort procedure is restated in many bundle files
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/effort.md
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-effort-procedure-restated] The activity-effort procedure is restated in many bundle files

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the per-effort review procedure (`low` / `medium` / `high`) is written out in `effort.md`
  and again in prose in the `sdd-session-feature`, `sdd-session-bugfix`, `sdd-spec-*` and `sdd-proposal` workflow
  bodies, the `spec-review` and `spec-delegate` skills, both worker contracts and `CAP-DLV-delivery-workflows`.
  Changing one effort level means editing every copy, and a missed copy leaves a worker following old rules.
- **Proposed Procedure**: keep the procedure in `effort.md` (and its contract in the capability); the other bundle
  files cite it by level name and state only what is specific to them.
- **Expected Benefit**: one edit per procedure change; no drift between a worker contract and the reference.
- **Cost & Risk**: readers of a workflow body follow one more link; a test that asserts restated text needs updating.
- **Attempted**: hypothesis; the impact list of `SPEC-high-effort-review-loop` §3.7 needed eleven bundle files for one
  effort level, and the Planning review found two worker contracts missing from the first draft of that list.

## Evidence

- `sdd-session-feature.md`, `sdd-session-bugfix.md`: "`high` a `code-reviewer` subagent review and a re-review after
  the fixes".
- `spec-review/SKILL.md`: "High retains re-review after fixes."
- `development-worker.md`, `planning-worker.md`: each restates the per-effort review steps.
- `envelopes/challenger-01.yaml` of this proposal: finding on the impact list missing the worker contracts.

- **Disposition**: PROP-direct-planning-procedure: moving the Planning steps, with their per-effort review, into one spec reference; SPEC-high-effort-review-loop already moved the high loop into review-loop.md. The remaining development-worker step 4 and workflow-body sentences state what each role runs at each level, which effort.md does not own, so they stay
