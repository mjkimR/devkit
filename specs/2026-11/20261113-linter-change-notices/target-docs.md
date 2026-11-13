---
id: PROP-linter-change-notices-target
title: Target Living Spec Structure for PROP-linter-change-notices
status: draft
proposal: SPEC-linter-change-notices
created_at: 2026-11-13
targets:
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
  - file: docs/capabilities/gate/CAP-GATE-commit-gates.md
  - file: docs/development/reference/rules.md
  - file: docs/decisions/2026-11/20261113-change-scoped-rule-notices.md
  - file: packages/devkit/README.md
---

# [Blueprint] PROP-linter-change-notices: Target Living Spec Structure

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-GOV-rules-engine`: additive NOTICE finding severity, distinct advisory `notices`, considered status,
  nonblocking remaining-count semantics and explicit read-context use case.
- `CAP-GOV-evaluation-lifecycle`: change_scope selection independent from severity; hygiene exclusion; exact
  working/staged/CI source pairs, old/new ranges, unavailable-evidence omissions and unchanged snapshot failures.
- `CAP-GOV-rule-authoring`: optional declaration, immutable source evidence, deletion/semantic-span rules,
  legacy INFO compatibility and notice metadata validation, with the representative fixture.
- `CAP-GATE-commit-gates`: NOTICE findings passed as `GATE_RULES_NOTICES`, never a refusal or a warning.

## 2. Use Cases Plan (docs/usecases/)

No new use case document or screen. Rule-check and explicit read companion contracts belong in the governance
capabilities and command reference. Workflow lint-clean still uses blocking findings only; its implementation and
approval boundaries do not change.

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

`ADR-change-scoped-rule-notices` records the accepted additive decision. No accepted ADR is superseded:
the choice extends the rule contract without changing existing INFO/warning/snapshot meanings. Current host and
advisory contracts are read authorities, not modified targets. Existing `rules -> project` and `gate -> rules`
edges suffice; no change to `.devkit/architecture.toml`, dist or MCP.

Candidate code paths (future evidence; Development chooses exact files inside these declared owners):

- `packages/devkit/src/devkit_agt/features/rules/`: contracts/snapshot models, `services/builtins/base.py`,
  policy/phase/evaluation services, workspace capture and memo repositories, project/context use cases and CLI.
- `packages/devkit/src/devkit_agt/features/gate/usecases/gates/rules.py` and
  `packages/devkit/src/devkit_agt/features/gate/models/errors.py`: returning notice considerations.
- `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/`,
  `packages/devkit/tests/integration/features/gate/`, `packages/devkit/tests/integration/features/workflow/` and
  `packages/devkit/tests/e2e/features/gate/`: AC-N1 to AC-N10 and existing-contract regression evidence.

New files stay under these existing feature/layer owners. Exposed operations implement `BaseUseCase`; models never
start Git or write memo state. No separate package, feature, test tier or native host handler is introduced.

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

`docs/development/reference/rules.md` documents the additive summary/severity contract, `rules context` synopsis,
source table, omission/session codes, excerpt bounds, failure/strict behavior and opt-in session suppression.
`packages/devkit/README.md` restates the command/API pointers. No bundle instruction or generated projection change.

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Rule severity | error, warning, info | Adds notice; info stays distinct |
| Change facts | Snapshot file metadata | Exact source identities and old/new text ranges |
| Relevant construct | Rule-specific file targeting | Validated change overlap, including deletion evidence |
| Read companion | No rule-owned surface | Explicit file context with hunks even without a matching rule |
| Session reminders | No rule notice suppression | Bounded opt-in transient suppression; explicit checks remain complete |
| Hygiene | Includes every linter rule | Excludes change_scope rules |
