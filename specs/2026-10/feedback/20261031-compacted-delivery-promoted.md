---
id: FB-compacted-delivery-promoted
title: Delivery feedback, promoted
summary: Delivery workflow stages, envelopes, and proposal handoff.
target: docs/capabilities/delivery/
status: promoted
created_at: 2026-10-31
aliases:
  - FB-envelope-answer-help-item-keys
  - FB-envelope-findings-reject-severity
  - FB-envelope-head-accepts-unknown-commit
  - FB-handoff-carried-padr-path
  - FB-handoff-moves-gate-decisions-to-materials
  - FB-lint-clean-detail-lists-every-violation
  - FB-proposal-new-target-area-placeholder
  - FB-return-keeps-later-disk-stages-done
  - FB-review-head-before-any-commit
  - FB-worker-manual-check-writes-outside-worktree
  - FB-worker-scope-excludes-code-documentation
  - FB-worker-stage-choice-ambiguous
  - FB-workflow-hash-excludes-body
  - FB-workflow-skill-records-every-gate
---

# [FB-compacted-delivery-promoted] Delivery feedback, promoted

## FB-envelope-answer-help-item-keys

- **Symptom**: envelope answer help does not name the keys of an --answers-file item
- **Response**: packages/devkit/src/devkit/workflow/cli/envelope.py
- **Reason**: --answers-file and --questions-file help name their item keys

## FB-envelope-findings-reject-severity

- **Symptom**: Envelope findings refuse a severity key that role outputs naturally carry
- **Response**: `SPEC-hygiene-reliability`
- **Reason**: Finding severity is optional non-empty string metadata retained through review and reverify.

## FB-envelope-head-accepts-unknown-commit

- **Symptom**: devkit workflow envelope new accepts a --head that names no commit
- **Response**: `SPEC-hygiene-reliability`
- **Reason**: CLI authoring resolves supplied base and head revisions to existing full commit IDs in Git workspaces.

## FB-handoff-carried-padr-path

- **Symptom**: Handoff leaves the proposal's PADR file path in the carried spec notes
- **Response**: packages/devkit-spec/src/devkit_spec/proposals/rewrite.py
- **Reason**: handoff rewrites code-span paths in the carried spec and promoted ADRs to the new ID or path (kind=path)

## FB-handoff-moves-gate-decisions-to-materials

- **Symptom**: Proposal handoff moves the proposal's gate decision records into docs/materials
- **Response**: `SPEC-handoff-unit-records`
- **Reason**: the handoff drops the proposal unit's gate records and envelopes, and records the spec's gates from the user's direction answer. The two records this observation left under `docs/materials/` were removed there.

## FB-lint-clean-detail-lists-every-violation

- **Symptom**: The lint-clean check detail lists every violation on one line
- **Response**: devkit packages/devkit/src/devkit/workflow/evaluation/evaluate.py
- **Reason**: the `lint-clean` detail quotes the first three violations and counts the rest, naming `devkit rules check <unit>`

## FB-proposal-new-target-area-placeholder

- **Symptom**: devkit spec proposal new leaves target_area and boundaries as placeholders
- **Response**: PROP-envelope-record-gaps
- **Reason**: a rule for the literal target_area placeholder (Q3); proposal new already takes --target-area for both fields

## FB-return-keeps-later-disk-stages-done

- **Symptom**: workflow return does not reopen stages whose disk checks still pass
- **Response**: devkit packages/devkit/src/devkit/workflow/evaluation/evaluate.py
- **Reason**: a return voids the envelopes recorded before it for its target stage and later ones; `CAP-DLV-delivery-workflows` and the spec skill state it

## FB-review-head-before-any-commit

- **Symptom**: Review envelope head points at the base when the reviewed change is not committed yet
- **Response**: S-Lane
- **Reason**: `spec-review` prerequisites ask for an intermediate commit before review, and an uncommitted-change assumption in the envelope when a review runs on uncommitted changes.

## FB-worker-manual-check-writes-outside-worktree

- **Symptom**: A worker's manual CLI check created a scratch workspace outside its worktree
- **Response**: `SPEC-worker-committed-result`
- **Reason**: the worker contract keeps throwaway fixtures in pytest's `tmp_path` or an ignored path inside the worktree.

## FB-worker-scope-excludes-code-documentation

- **Symptom**: A worker cannot finish a change that adds an advisory code, because the code must be documented under docs/
- **Response**: `SPEC-worker-committed-result`
- **Reason**: a worker writes the `docs/` paths its task's `_Boundary:` names, and `spec-tasks` puts the documentation a check requires there, so the worker's commit passes its checks (`ADR-orchestration-workers`).

## FB-worker-stage-choice-ambiguous

- **Symptom**: Planning worker envelope stage is ambiguous when spike work runs under collect-feedback
- **Response**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md, packages/devkit-spec/src/devkit_spec/bundle/subagents/planning-worker.md, packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md, docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
- **Reason**: --stage is the stage next names when the worker envelope is written, after the run's other records

## FB-workflow-hash-excludes-body

- **Symptom**: It is not documented that a workflow's binding hash ignores its body
- **Response**: `src/devkit_spec/bundle/skills/spec/SKILL.md`
- **Reason**: `WORKFLOW_DRIFT` names the `stages` list and states that a body, title or stage-name edit needs no rebind; devkit already documents the hash inputs (`docs/capabilities/delivery/CAP-DLV-workflow-definitions.md`, Schema Hash), so nothing is forwarded.

## FB-workflow-skill-records-every-gate

- **Symptom**: The generated devkit-workflow skill tells agents to record the G3 answer
- **Response**: devkit `gates.<gate>.answer` (`docs/capabilities/delivery/CAP-DLV-workflow-definitions.md`), with `answer=given` on the gate's `[REQUEST]` and the generated `devkit-workflow` skill following it; `direct-delivery`, `bugfix` and `s-lane` declare `gates
- **Reason**: {integration: {answer: given}}`.
