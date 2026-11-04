---
reconcile_id: REC-namespace-steering-registers
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-namespace-steering-directories.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-namespace-steering-registers.md
    resolution: modified
---

# Reconciliation: `SPEC-namespace-steering-registers`

## Reflection

Namespace/model/rule contracts name optional canonical steering registers and explicit legacy migration. Search
specifies the existing namespace selection, deterministic union and actual-file diagnostics. Agent and delivery
contracts read global with selected local vocabulary, create only needed registers and retain agent-only object
semantics. The accepted ADR partially supersedes only the earlier glossary/register decisions; the old ADR stays
accepted with its partial-supersession annotation. No milestone or globally unique identity changed.

## Source feedback

- `FB-namespace-ux-objects-copy` resolved: all actual agent consumers support root plus selected local registers;
  the original claim about automatic object parsing is corrected in the disposition. Independent review P2 found
  unconditional root creation in the seeded UX README; the fix and new regression passed 13 guidance tests.
- `FB-package-glossary-asymmetry` resolved: canonical location, root+selected synonym reads, actual-file errors,
  legacy move/merge findings, registered Owner validation and fixes verified. No automatic data move.

## Verification

Focused baseline: six failures and one pass before source changes; GREEN steering/reference/search 88 passed,
then 19 focused tests with extra invalid selected YAML cases. Affected selection: 2291 passed, 136 paths, partial
mode with full fallback preserved. Post-review seed/guidance: 13 passed. Deployed steering/reference rule tests,
both package Ruff/Pyright, offline wheel builds and cumulative CI rules passed. No required scope was deferred.

## Entrypoints

Existing search, namespace, governance and guidance entrypoints already cover these modifications; review the
mechanically derived candidates and retain authored source owners only. No new public operation was added.
