---
id: PROP-handoff-rewrite-overlap-scheduling
title: Handoff rewrites as integration evidence in scope scheduling
summary: Tells the Host in the spec-orchestrate skill to discount overlap that only the units' completed handoff commits wrote, so handoff reference rewrites alone no longer serialize otherwise separate Development workers.
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: collaboration/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/proposals/PROP-handoff-rewrite-overlap-scheduling/
  excludes:
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-docs/
    - packages/devkit/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-handoff-rewrite-overlap-scheduling] Handoff rewrites as integration evidence in scope scheduling

## 1. Background & Hypothesis

`FB-handoff-reference-overlap-serializes-workers`: the spec-orchestrate skill runs units whose `horizon=current`
evidence overlaps sequentially (`skills/spec-orchestrate/SKILL.md.jinja`). Scope collection classifies paths by
horizon only (`features/scope/services/collection.py`), so the reference rewrites a completed handoff commit makes
count as current overlap, and two otherwise separate Development units serialized on eight such paths.

Hypothesis: paths a completed, Host-owned handoff transaction already rewrote are integration-conflict evidence,
not prospective writes, so treating them apart restores parallel Development without weakening the guarantee for
real worker writes.

## 2. Technical Spike Questions

- **Q1**: Is exempting handoff-rewritten paths from scheduling overlap safe, or can a worker still need to edit them
  (link repair after a move)?
- **Q2**: Should collection tell those paths apart by provenance (the handoff commit) or by path class, or is a
  wording note in the skill enough?

## 3. Proposed Design & Impact

Planning ran at `low` effort (user override of the `medium` hint): questions only, no `scout` or `challenger`.
Evidence: `materials/overlap-evidence.md`.

### Answers

- **Q1**: Safe when it is limited to paths only the handoff commit changed. A worker that must edit such a path
  either declares it (reconcile, target-docs or `_Boundary:`), which keeps a `current` overlap on declared evidence,
  or edits it as an extension, which shows up in its commits after the handoff commit. What remains is a reference
  rewrite the Host's handoff transaction completed; two of them on one file conflict only at integration, which
  already runs one unit at a time in overlap order.
- **Q2**: A wording note in the spec-orchestrate skill, keyed to provenance. Path class is unsafe: the rewritten files
  (capability, ADR, milestone, sibling proposal files) are the classes workers also edit. Provenance in collection
  would change the `scope collect` output contract for a non-recurring friction, while the Host already has each
  unit's handoff `commit` from the handoff return and each evidence entry's `source`.

### Change

1. `skills/spec-orchestrate/SKILL.md.jinja`, the scheduling bullet: a `current` overlap does not serialize
   Development when, for both units, the path's evidence is `observed` only and the path changed in the unit's
   handoff commit but in none of its later commits (`git diff --name-only <handoff commit>..<unit head>`). Such a
   path stays integration-conflict evidence: integration runs in overlap order and resolves the rewrites; neither
   payload names it as a write target. Any declared or candidate evidence on the path, or a later commit touching
   it, serializes as before. The rule covers every reference rewrite the handoff commit makes, including the alias
   rewrites the in-progress sibling-alias handoff bugfix adds (branch `dev-handoff-sibling-alias-rewrite`).
2. CAP-HARN-agent-guidance, "Host scope observation": the same rule in the mirrored scheduling sentence.

No code, test or `scope collect` output change. Verification: `devkit rules check` on the changed files, the bundle's
projection check and `git diff --check`.

### Design, domain and operations impact

- Design: unaffected; the scheduling statement owner is CAP-HARN-agent-guidance (Host scope observation), its
  source the skill text. CAP-COLL-work-scope-registry owns collection output, which is unchanged.
- Domain: unaffected; no entity or term changes (`horizon`, `source` and `observed` keep their meaning).
- Operations: unaffected; no command, configuration or runbook changes.

### Planning decisions

- Wording-only: provenance by the Host from the handoff `commit`, not in collection and not by path class; no PADR
  (a refinement of the existing horizon reading under ADR-host-owned-scope-observation).
- Resized: boundaries drop `features/scope/` and tests and add CAP-HARN-agent-guidance; `dev_effort` lowered to
  `low`.
- Follow-up trigger, not scheduled: if the manual check recurs or is misapplied, move provenance into collection as
  a new evidence source.

## 4. Lifecycle & Retirement Criteria

Retired when the accepted design is handed off, or rejected with the skill wording unchanged.
