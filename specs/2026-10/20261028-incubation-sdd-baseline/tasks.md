---
id: TASKS-incubation-sdd-baseline
spec: SPEC-incubation-sdd-baseline
plan: PLAN-incubation-sdd-baseline
---

# Task Breakdown: Incubation SDD baseline

- [x] **Task 1**: Deliver the focused baseline playbook, material report template and isolated asset checks.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml, packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py, .devkit/installation.json (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: manifest selection, isolated sync/discovery/reference checks, playbook contract checks, affected tests and sync check.
- [ ] **Task 2**: Exercise adoption with the delivered prerequisites and reflect the retained contract in the Living Spec and installation references.
  - **_Boundary**: packages/devkit-spec/, docs/capabilities/delivery/, docs/capabilities/harness/, docs/usecases/delivery/, docs/usecases/harness/, docs/decisions/, guides/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: sample-app adoption/gap/source-change/partial-failure evidence, existing brownfield regressions, independent code/reconcile review, governance.

Task 2 remains pending during the independent asset turn; the Host refreshes prerequisite code and grants shared-document scope before that work.
