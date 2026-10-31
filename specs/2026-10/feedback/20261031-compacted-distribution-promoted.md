---
id: FB-compacted-distribution-promoted
title: Distribution feedback, promoted
summary: Bundle asset synchronization, presets, and package distribution.
target: docs/capabilities/distribution/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-bundle-budget-forces-waivers
  - FB-commit-intent-before-planning-worktree
  - FB-effort-procedure-restated
  - FB-feedback-hidden-in-completed-bundles
  - FB-mcp-registration-pending-ignores-runtime
  - FB-reconcile-self-check-cross-component
  - FB-shared-skill-unreachable-from-role
  - FB-skeleton-read-before-rewrite
  - FB-skill-byte-budgets-leave-no-headroom
  - FB-smoke-response-style-skill-path
  - FB-worker-checkbox-leaves-spec-status-to-host
  - FB-wrapped-boundary-drops-paths
---

# [FB-compacted-distribution-promoted] Distribution feedback, promoted

## FB-bundle-budget-forces-waivers

- **Symptom**: Bundle size budgets left no room for a review fix in spec-delegate
- **Response**: `tests/test_bundle_budgets.py`
- **Reason**: the budget follows devkit's raised `RULE-skill-document-size` default (12288 bytes, devkit 94085f4), the headroom is the budget minus 512, and a failure reports the size, the limit and the excess.

## FB-commit-intent-before-planning-worktree

- **Symptom**: Make the proposal intent commit explicit before branching
- **Response**: `src/devkit_spec/bundle/skills/spec/references/classification.md`
- **Reason**: the proposal Backlog bullet commits the draft and its `plan-intent` record to the base, and only them, before `plan-<slug>` starts.

## FB-effort-procedure-restated

- **Symptom**: The activity-effort procedure is restated in many bundle files
- **Response**: PROP-direct-planning-procedure
- **Reason**: moving the Planning steps, with their per-effort review, into one spec reference; SPEC-high-effort-review-loop already moved the high loop into review-loop.md. The remaining development-worker step 4 and workflow-body sentences state what each role runs at each level, which effort.md does not own, so they stay

## FB-feedback-hidden-in-completed-bundles

- **Symptom**: Open feedback in a completed bundle is hidden without --history
- **Response**: `SPEC-open-feedback-and-progress`
- **Reason**: feedback of completed bundles stays current; the assets no longer pass `--history`

## FB-mcp-registration-pending-ignores-runtime

- **Symptom**: MCP_REGISTRATION_PENDING repeats when the MCP runtime is unavailable
- **Response**: `SPEC-mcp-runtime-pending`
- **Reason**: promoted by the user's decision for Planning of the recorded behavior and its contract constraints.

## FB-reconcile-self-check-cross-component

- **Symptom**: The medium reconcile self-check exception leaves "cross-component impact" undefined for bundle wording changes
- **Response**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/effort.md, docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
- **Reason**: the medium reconcile exception defines cross-component impact (packages, capability areas and repository tooling counted separately; the change's own reflection excluded)

## FB-shared-skill-unreachable-from-role

- **Symptom**: Reviewer and reconciler projections name a skill the subagent cannot load
- **Response**: `src/devkit_spec/bundle/subagents/reviewer.md`, `src/devkit_spec/bundle/subagents/reconciler.md` (s-lane)
- **Reason**: each contract names its skill by the host-neutral managed path and the sections to follow; the reconciler reads the constitution file instead of running `get-context`.

## FB-skeleton-read-before-rewrite

- **Symptom**: Skeleton files written by devkit commands are rewritten without a prior read
- **Response**: commit fa6aa90 (docs(spec)
- **Reason**: read command-written skeletons before rewriting them): spec-specify, spec-plan, spec-tasks and the planning-worker PADR step now say to read the skeleton first.

## FB-skill-byte-budgets-leave-no-headroom

- **Symptom**: Spec skill references sit at the byte budget, so policy wording changes need trimming elsewhere
- **Response**: S-Lane
- **Reason**: the Git policy levels moved from `spec/references/completion.md` to `spec/references/git-policy.md`, and the payload field table from `spec/references/envelope.md` to `spec-delegate/references/payload.md` (completion 6.7 KB, envelope 7.7 KB).

## FB-smoke-response-style-skill-path

- **Symptom**: Consumer smoke still checks the response-style instruction path after the bundle moved to a skill
- **Response**: scripts/smoke.sh (commit c05b3c5)
- **Reason**: the smoke now checks the rendered response-style skill and its AGENTS.md pointer instead of the removed instruction path.

## FB-worker-checkbox-leaves-spec-status-to-host

- **Symptom**: A worker's checked task leaves spec.md status behind, and only the host may fix it
- **Response**: `SPEC-worker-committed-result`
- **Reason**: the worker sets the spec's status itself with `devkit rules fix <unit>/spec.md` as part of its committed result (`ADR-orchestration-workers`); no host step.

## FB-wrapped-boundary-drops-paths

- **Symptom**: A wrapped _Boundary line silently drops its continuation paths
- **Response**: `SPEC-boundary-continuation-lines`
- **Reason**: indented continuation lines join a `_Boundary` value; `spec-tasks` states the form
