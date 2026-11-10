---
id: FB-worker-inspect-refuses-planning-follow-up-draft
title: Worker inspection reports a planning-worker's follow-up draft proposal as outside scope
scope: repo
kind: friction
category: tool-behavior
target: devkit spec worker inspect
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-10
---

# [FB-worker-inspect-refuses-planning-follow-up-draft] Worker inspection reports a planning-worker's follow-up draft proposal as outside scope

## 1. Friction / Question (friction, question)

- **Context**: Validating the committed range of a first Planning turn whose worker moved the viewer work into a new
  follow-up draft proposal.
- **Expectation**: The `planning-worker` contract allows "the proposal directory inside the worktree, and a new draft
  proposal for a follow-up", so a range holding only those paths validates.
- **Actual**: `devkit spec worker inspect --format json` derived its scope from the unit alone, listed the follow-up
  draft's `proposal.md` under `outside_scope` and failed with `SPEC_WORKER_SCOPE_OUTSIDE`, whose advisory says to stop
  and ask the user.
- **Workaround (or Interpretation Chosen)**: Reran the inspection with `--scope` naming both proposal directories;
  the scope check passed. An override replaces the derived scope, so the unit directory had to be repeated.
- **Suggestion**: For a `plan-` unit, admit a proposal directory the range creates under `docs/proposals/` (absent at
  the base, `status: draft`) as declared scope, or state in the `spec-delegate` worker reference that the Host passes
  the follow-up draft through `--scope`.

## Diagnostic Details

- **Reproduction**: On a `plan-<slug>` branch, commit a new `docs/proposals/PROP-<other>/proposal.md` beside the
  unit's changes and a `worker` envelope, then run the inspection without overrides.
- **Expected / Actual**: expected `scope: pass`; got `scope: fail` with the draft under `outside_scope`.
- **Versions**: the repository at `5642d27d` on the Planning branch.
- **Conditions**: every Planning turn that records a follow-up as a draft proposal.
- **Workarounds Attempted**: `--scope <unit dir> --scope <follow-up dir>`; succeeded.
- **Related Assets**: the `planning-worker` contract (Write boundaries); the `spec-delegate` skill's
  `references/worker.md` (Validate).

## Evidence

```text
scope: [{path: docs/proposals/PROP-partial-adr-supersession-statements, source: unit}]
outside_scope: [docs/proposals/PROP-viewer-decision-supersession/proposal.md]
errors: SPEC_WORKER_SCOPE_OUTSIDE "1 changed paths lie outside the authorized scope"
with --scope for both directories: checks.scope = pass, outside_scope = []
```
