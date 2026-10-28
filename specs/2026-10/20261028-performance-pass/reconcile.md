---
reconcile_id: REC-performance-pass
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-performance-pass.md
    resolution: modified
  - file: docs/usecases/governance/UC-speed-up-selected-slow-operations.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-review-refactor.md
    resolution: modified
  - file: docs/decisions/2026-10/20261028-keep-performance-passes-in-a-separate-maintenance-playbook.md
    resolution: modified
---

# Reconcile: performance pass

- `CAP-DLV-performance-pass` (new) states the run, measurement and change contracts and the report interface of the
  playbook as committed, including the review round 1 fixes: the work item's branch and integration follow its
  feature workflow, the single-variant noise floor, the managed-directory fallback, removals as contract changes,
  a change with no measurable change returning to the decision round, and survey completion.
  `UC-speed-up-selected-slow-operations` (new) carries the goal, steps, extensions and scenarios.
- `CAP-DIST-context-and-playbooks` §5: reading a co-deployed playbook's body resources is reference reading, no
  invocation; its `usecases` list gains the new use case (traceability back-link).
- `CAP-DIST-content-packages` §6: the `performance` preset, the co-deployment constraint, four playbooks under `all`
  and the reference reading of `review-refactor`.
- `CAP-DLV-review-refactor` §1: its application and evidence headings are cited by `performance-pass`, which a bundle
  test enforces.
- `ADR-keep-performance-passes-in-a-separate-maintenance-playbook`: the follow-up names the retirement criterion of
  `SPEC-performance-pass` instead of the former proposal (handoff wording only; the decision is unchanged).
- Not changed: `CAP-DLV-delivery-workflows`, `ARCH-04-delivery-strategy` and the `spec` classification reference,
  because the direct-mode overall-refactor grant stays with `review-refactor` (user decision `q1`); the other three
  ADRs (their handoff-rewritten references read correctly).
- Entrypoints: the new capability's entrypoint is the playbook's `SKILL.md`, which exists.
- Deferred: handbook journey entries for the performance pass follow at the next release
  (`ADR-handbook-on-request-release-snapshot`); no source feedback was carried from Planning.
