---
id: CAP-DLV-test-management
title: Test-management assessment
summary: "An explicitly invoked maintenance playbook assesses bounded test suites, resource prerequisites and runner configuration while preserving consumer verification gates and routing only user-decided changes."
area: delivery
status: active
usecases:
  - UC-assess-test-management
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/SKILL.md
created_at: 2026-11-05
---

# [CAP-DLV-test-management] Test-management assessment

## 1. Summary

The maintenance catalog bundle provides a test-specific assessment router and conditional coverage/resource and
pytest references. The procedure uses the consumer's commands and ownership instead of standardizing test tiers,
worker settings or branch policies. `SPEC-test-management` retains the author-led procedural walkthrough.

## 2. Scope & Boundary

- **In-Scope**: bounded suite assessment, prerequisite inspection, coverage/isolation findings, optional local
  runner comparison, one decision round and routing approved changes through the native development workflow.
- **Out-of-Scope**: application bug repair and consumer policy redesign (separate consumer work), performance-only
  passes (`CAP-DLV-performance-pass`), integration authority (`CAP-DLV-delivery-workflows`), mandatory history
  (`CAP-DLV-maintenance-history`), source snapshots and publication (separate authority).

## 3. Business Rules & Policies

1. **Selection**: WHEN testing or all is selected, the bundle MUST deploy the complete directory-form playbook;
   existing individual presets MUST keep their asset sets. Tests: `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`.
2. **Entry**: the agent MUST run the procedure only on explicit invocation or confirmation; selection/retrieval
   MUST NOT invoke assessment. Structural deployment tests and the walkthrough in `SPEC-test-management`.
3. **Prerequisites**: before execution including collection, the agent MUST inspect executable hooks and resource
   requirements; unresolved resource safety MUST leave the affected command unexecuted. `SPEC-test-management` walkthrough.
4. **Coverage**: the agent MUST treat tier labels and resource isolation as separate facts and preserve native
   ownership and required completion checks. `SPEC-test-management` three-repository walkthrough.
5. **Incomplete checks**: IF a required prerequisite is missing, THEN the report MUST label its check `not_run`
   with an unmet gate; documented optional skips MUST name their missing coverage. `SPEC-test-management` walkthrough.
6. **Conditional tuning**: WHERE pytest runner configuration is in scope, the agent MUST load its conditional
   reference and require comparable identities, outcomes/skips, cleanup and elapsed time before default promotion;
   inconclusive evidence MUST retain existing settings. `SPEC-test-management` tuning walkthrough.
7. **Decision**: an unattended assessment MUST stop at the one decision round with no edits; approved candidates
   MUST name exact scope and route through native development/review/integration approvals. `SPEC-test-management` walkthrough.
8. **Evidence**: the report MUST distinguish actual commands/results from examples, walkthroughs and unexecuted
   checks; raw logs stay outside versioned reports. `SPEC-test-management` walkthrough.

## 4. Interfaces & Data Contracts

Select with `devkit add maintenance:testing` or existing default `devkit add maintenance` (all).
Load through `devkit playbook get maintenance/test-management`, `devkit-playbook` or a confirmed intake offer
(`CAP-DIST-context-and-playbooks`). The asset contains `SKILL.md`, `references/assessment.md` and
`references/pytest.md`; reference loading conditions are checked by catalog integration tests.

The ordinary local report contains inspected state, selected roots/goal, native commands/gates, resource/coverage
findings, actual outcomes and gaps, decisions, exact candidate paths and routed destinations. Outcome is
`stopped at decision round`, `routed`, `partially routed` or `kept`. An unattended run ends with its report and
no edits; a decided run routes approved candidates and keeps required missing checks visible. Publication and
optional history capture are never inferred from invocation.
