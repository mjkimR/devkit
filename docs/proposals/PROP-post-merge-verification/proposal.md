---
id: PROP-post-merge-verification
title: Verify integration after merging with the resulting runtime
summary: Verify the landed result with its declared devkit runtime after branch checks, and simplify integration preparation, recovery and CLI usage.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: integration/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/src/devkit_agt/features/worktree/
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-spec/tests/
    - docs/capabilities/integration/
    - docs/capabilities/delivery/
    - docs/capabilities/governance/
    - docs/capabilities/worktree/
    - docs/usecases/
    - docs/architecture/
    - docs/decisions/
    - docs/development/
    - AGENTS.md
  excludes:
    - packages/devkit-dist/src/
    - packages/devkit-mcp/src/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-post-merge-verification] Verify integration after merging with the resulting runtime

## 1. Background & Hypothesis

Integration evaluates source rules with the target checkout's installed devkit. A branch can pass its own
checks but fail integration because the target runtime lacks its CLI or rule implementation. This affects devkit
self-development and client upgrades. A separate source-built runtime adds setup and recovery work.

Verify branches before integration, then verify the landed result with its declared dependencies and devkit.
A failed final check leaves integration unfinished and is repaired or reverted on the target. A temporary
failing target is an accepted operational trade-off; failure frequency has not been measured.

## 2. Technical Spike Questions

- **Q1**: Which pre-merge checks protect Git effects, and which should move to final verification?
- **Q2**: How should the Host refresh the runtime, run project checks and recover after a landed failure?
- **Q3**: Which integration commands, options and repeated checks can be removed without losing actionable recovery?

## 3. Proposed Design & Impact

Planning settles one integration lifecycle change, including its CLI and guidance. Compare a Host-led final
verification procedure against an automatic verification runner and the current target-runtime checks.
Retain branch tests and existing approval scope. Remove the requirement for target-runtime content readiness.
Use the final runtime to validate the landed result before reporting completion.

New feature dependencies are out of scope. Planning writes only this proposal bundle and its PADRs.
Development boundaries will be narrowed after the implementation inventory.

## 4. Lifecycle & Retirement Criteria

Planning produces a reviewed design, a PADR that identifies the replaced ADR clauses, a Living Spec blueprint,
and measurable acceptance criteria. Direction acceptance precedes Development. One spec implements and verifies
the resulting integration lifecycle; unrelated CLI cleanup and release automation are outside this proposal.
