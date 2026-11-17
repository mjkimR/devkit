---
id: PROP-handoff-rewrite-overlap-scheduling
title: Handoff rewrites as integration evidence in scope scheduling
summary: Lets scope collection tell paths a completed handoff commit rewrote apart from prospective worker writes, so handoff reference rewrites alone no longer serialize otherwise separate Development workers.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: collaboration/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/scope/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/tests/
    - docs/proposals/PROP-handoff-rewrite-overlap-scheduling/
  excludes:
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

To settle in Planning; impact limited to scope collection, the spec-orchestrate skill and their tests.

## 4. Lifecycle & Retirement Criteria

Retired when the accepted design is handed off, or rejected with the skill wording unchanged.
