---
id: TASKS-feedback-dedup-and-compaction
spec: SPEC-feedback-dedup-and-compaction
plan: PLAN-feedback-dedup-and-compaction
---

# Task Breakdown: `SPEC-feedback-dedup-and-compaction` Feedback lookup before recording and compaction of closed feedback

## Phase 1: Lookup before recording

- [x] **Task 1.1**: Lookup step and status table in the recording procedure and the sweep, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-feedback/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-feedback/references/sweep.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_lookup_guidance.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_feedback_lookup_guidance.py`

## Phase 2: Compaction playbook

- [x] **Task 2.1**: `feedback-compaction` playbook registered in the bundle, synchronized, with guidance and record-shape tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-compaction/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_compaction_guidance.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-12_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_feedback_compaction_guidance.py`, `uv run devkit sync --check`, `uv run devkit playbook get spec/feedback-compaction`

- [x] **Task 2.2**: Neighbouring guidance points to the playbook and the compact record form, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/source-feedback.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/playbooks.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_compaction_guidance.py`
  - _Requirements: AC-11_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_feedback_compaction_guidance.py`
