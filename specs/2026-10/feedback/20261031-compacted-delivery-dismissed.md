---
id: FB-compacted-delivery-dismissed
title: Delivery feedback, dismissed
summary: Delivery workflow stages, envelopes, and proposal handoff.
target: docs/capabilities/delivery/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-automatic-review-managed-sync
  - FB-handbook-journey-misses-handoff-commit
  - FB-handoff-premise-drift-unreported
  - FB-intent-stage-lists-a-proposal-artifact
  - FB-nested-project-paths-in-integration-and-worker
  - FB-parallel-planning-feedback-id-collision
  - FB-permission-review-deadline-retry
  - FB-planning-decisions-without-worker-questions
  - FB-received-feedback-status-during-planning
  - FB-review-refactor-cited-sections-embed-the-route
  - FB-specify-boundary-commit-refused-by-task-coverage
  - FB-spike-complete-without-evidence
  - FB-split-feedback-disposition-outside-scope
---

# [FB-compacted-delivery-dismissed] Delivery feedback, dismissed

## FB-automatic-review-managed-sync

- **Symptom**: Automatic review treats sanctioned sync as forbidden direct edits
- **Response**: Dismissed outcome
- **Reason**: dismissed. The observation concerns host-level automatic permission review prompt/policy in OpenAI Codex, which mistakenly interpreted the direct-edit prohibition as forbidding the sanctioned recovery generator (`devkit sync`). devkit repository code does not own or configure the host's automatic review model behavior.

## FB-handbook-journey-misses-handoff-commit

- **Symptom**: Handbook proposal journey misses the composed handoff commit
- **Response**: Dismissed by the user
- **Reason**: the release handbook is refreshed only when a release requests it, and that refresh finds stale pages itself (`just handbook status`, `HANDBOOK_STALE`). Development does not track handbook drift.

## FB-handoff-premise-drift-unreported

- **Symptom**: Proposal premises changed between plan-accept and Development are found only by reading history
- **Response**: Dismissed outcome
- **Reason**: Dismissed after reassessment. Checking accepted premises against the current base remains the responsibility of the Host and Development worker. In the reported case the worker found the change and incorporated it into the work. Handoff change notifications would be a convenience feature; this observation establishes no missed premise change. No additional notification or checking procedure is introduced.

## FB-intent-stage-lists-a-proposal-artifact

- **Symptom**: The direct-delivery intent stage lists a proposal artifact
- **Response**: not a defect
- **Reason**: the proposal path applies to units handed off from a proposal, which Routes 3 and 4 bind to direct-delivery or bugfix

## FB-nested-project-paths-in-integration-and-worker

- **Symptom**: Integration readiness and worker runners assume the project is the Git top level
- **Response**: dismissed by the user's decision
- **Reason**: devkit's root contract (`find_project_root` / `require_devkit_root`) makes the Git top level the devkit root and refuses a `.devkit/` below it with `DEVKIT_ROOT_NESTED`, so nested projects are unsupported and the partial project-prefix handling in `native_handoff`, composed plan-accept, scope, policy, `generated` and `worker inspect` was removed instead.

## FB-parallel-planning-feedback-id-collision

- **Symptom**: Parallel Planning branches record the same feedback ID unnoticed
- **Response**: Dismissed
- **Reason**: separate branches can independently record the same observation, but the existing integration procedure incorporates the current base and runs cumulative rules before landing. `RULE-document-reference` detects duplicate IDs in the combined tree, as the recorded incident demonstrates. Keep the existing recovery: retain one observation, remove the duplicate and rerun verification. No additional cross-branch reservation or prevention mechanism is needed.

## FB-permission-review-deadline-retry

- **Symptom**: Automatic permission review deadlines interrupted local verification
- **Response**: Dismissed outcome
- **Reason**: dismissed. The observation concerns intermittent deadline timeouts in the external OpenAI Codex automatic permission approval review service during exec calls. devkit repository packages do not operate the external approval review backend.

## FB-planning-decisions-without-worker-questions

- **Symptom**: Record Planning decisions without a preceding worker question
- **Response**: Dismissed
- **Reason**: proposal/PADR documents retain Planning direction and rationale, the spec records the agreed contract, and gates record approvals; a separate decision record without a worker question would duplicate these existing artifacts.

## FB-received-feedback-status-during-planning

- **Symptom**: Status of feedback a proposal fixes directly is ambiguous
- **Response**: Dismissed by the user
- **Reason**: `source-feedback.md` already answers it. A direct-fix source stays `open` through Planning and handoff, because they do not verify a fix, and completion sets it to `resolved`. This item's own source was handled that way.

## FB-review-refactor-cited-sections-embed-the-route

- **Symptom**: review-refactor application sections embed the overall-refactor route
- **Response**: Dismissed by the user's decision
- **Reason**: `CAP-DLV-performance-pass` already selects its feature route through an explicit override of the cited text. Current routing is defined; removing that documentation duplication alone does not justify separate work. Keep the existing override and behavior.

## FB-specify-boundary-commit-refused-by-task-coverage

- **Symptom**: Commit gate refuses the specify stage boundary until tasks cover every AC
- **Response**: Dismissed outcome
- **Reason**: Dismissed as a skill-versus-stage boundary misunderstanding. The existing sdd-spec-feature specify stage lists spec-specify, spec-plan and spec-tasks together, requires all three nonskeleton documents and lint-clean, and declares all three as its artifacts. A spec.md-only commit is not that stage boundary. Verified with `devkit workflow show sdd-spec-feature`; task coverage continues to guard the real boundary. No rule relaxation or implementation change is needed.

## FB-spike-complete-without-evidence

- **Symptom**: Proposal spike reports done before substantive Planning evidence exists
- **Response**: Dismissed outcome
- **Reason**: Dismissed after reassessment. Spike is an optional investigation stage; necessary investigation and review remain responsibilities of the existing Planning and Challenger procedures. The observed evidence concerns the CLI's `done` display, not a proposal incorrectly accepted because required investigation was omitted. A separate completion mechanism is not justified by this case. No workflow or runtime change is made.

## FB-split-feedback-disposition-outside-scope

- **Symptom**: A Planning split leaves promoted source feedback pointing at the narrowed proposal
- **Response**: Dismissed under `ADR-feedback-lifecycle`
- **Reason**: promotion closes the originating feedback. Subsequent splitting or completion is tracked in the receiving work, without reopening the source or requiring a new source disposition. No additional Planning-worker permission to maintain terminal feedback is needed. The original observation is retained as history.
