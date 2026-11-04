---
reconcile_id: REC-namespace-steering-registers
status: resolved
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
  - file: docs/decisions/2026-11/20261102-ux-screens.md
    resolution: modified
---

# Reconciliation: `SPEC-namespace-steering-registers`

## Reflection

Namespace/model/rule contracts name optional canonical steering registers and explicit legacy migration. Search
specifies the existing namespace selection, deterministic union and actual-file diagnostics. Agent and delivery
contracts read global with selected local vocabulary, create only needed registers and retain agent-only object
semantics. The accepted ADR partially supersedes the earlier namespace glossary/register decisions and `ADR-ux-screens`
root-only register location, unconditional creation and root-only drafted-row sync writes. Both old ADRs stay
accepted with precise partial-supersession annotations; their other clauses remain intact. No milestone or globally unique identity changed.

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

The mechanical derivation returned 112 pairs with 98 new candidates. Rejected receipt, test, README and broad
cross-product directory candidates: they are outputs, verification or unrelated owners, not new reading doorways.
Existing search, namespace, governance and guidance entrypoints already cover these modifications. No new public
operation or entrypoint was added.
