---
reconcile_id: REC-targeted-tests
feature: SPEC-targeted-tests
status: pending
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/development/setup.md
    resolution: modified
  - file: docs/development/workflow.md
    resolution: modified
---

# Reconciliation

The development documents describe the new test commands as the current contract. `ci-cd.md` §2 states the
selectors of `just test`/`just test-cov` for a single module, the selection rules, output, error and limits of
`just test-affected`, and that an agent runs targeted tests during development and the full suite once on the
reviewed head before integration. `setup.md` lists the two new command forms, and `workflow.md` §3 replaces "`just
test` before every commit" with the targeted run plus the single full run.

No capability, story, architecture document or ADR changes. The commands are repository tooling (`justfile`,
`scripts/`), not a `devkit` package module, so no `docs/capabilities/` area owns them and no entrypoints apply. The
devkit-spec bundle skills `spec-review` and `spec-plan` now say when the full suite runs; no capability document
describes how those skills run tests (`CAP-DLV-delivery-workflows` names the stages and roles only), so the bundled
skill text is the whole contract. `AGENTS.md` and `README.md` are agent and contributor quick references outside the
Living Spec and were updated in step. No deferred work remains.
