---
id: PLAN-formal-document-coverage
spec: SPEC-formal-document-coverage
---

# Technical Plan: `SPEC-formal-document-coverage` Formal document coverage across capability areas

## 1. Constitution & Invariant Review

None. The change adds documents of delivered kinds under their area-scoped paths (`ADR-area-scoped-design-bundles`)
and follows the problem-first template openings (`ADR-problem-first-formal-document-openings`). Ownership follows
`CAP-DOCS-documentation-ownership` §3.1 and §3.3: each document answers one reader question and cites, never moves,
the normative statements of its owners. No ADR is needed.

## 2. Architecture Overview & Impact

Target area: `docs/` only. Each `SPEC-formal-document-coverage` acceptance criterion maps to the six new documents:

| Task group | Document | Kind instruction | Sources to verify (AC-05) |
| --- | --- | --- | --- |
| A | `docs/designs/delivery/DESIGN-workflow-stage-evaluation/design.md` | `design-writing` | `packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py`, `.../workflow/models/decision_records.py`, `CAP-DLV-workflow-orchestration`, `CAP-DLV-workflow-envelopes`, `CAP-DLV-human-interaction` §5 |
| A | `docs/operations/OPS-assignment-attention-routing.md` | `operations-writing` | `packages/devkit-adaptive/src/devkit_adaptive/features/assignment/`, `CAP-DLV-adaptive-assignments` §4 |
| B | `docs/operations/OPS-host-hook-dispatch-routing.md` | `operations-writing` | `packages/devkit-dist/src/devkit_dist/features/host/`, `CAP-HOST-lifecycle-observation` |
| B | `docs/operations/OPS-mcp-runtime-refusals.md` | `operations-writing` | `packages/devkit-mcp/src/devkit_mcp/features/runtime/`, `CAP-MCP-runtime-registration` |
| C | `docs/domain/distribution/DOMAIN-override-lifecycle.md` | `domain-writing` | `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/override_commands.py`, `CAP-DIST-workspace-ownership` §3 |
| C | `docs/operations/OPS-search-mode-and-model-routing.md` | `operations-writing` | `packages/devkit-dist/src/devkit_dist/features/search/`, `CAP-SRCH-document-search`, `CAP-DOCS-document-search` |

Implementation choice: the three groups are drafted by three parallel drafting helpers with disjoint files, then
integrated, re-verified and committed by the single Development worker (user preference for parallel work; disjoint
paths make the merge trivial).

Design, domain and operations impact: one design, one domain and four operations documents are added, as listed; no
existing formal document changes its statements. `DOMAIN-delivery-relationships`,
`DOMAIN-bundle-selection-and-installation`, `OPS-distribution-sync`, `DESIGN-distribution-transactions` and
`DESIGN-distribution-file-directory-replacement` are unaffected: the new documents cite them as owners or related
entries and restate none of their statements.

## 3. Error Handling & Edge Cases

- An inventory writing condition that the current code cannot support drops that document (the search document's
  explicit `--mode hybrid` row) and the drop is reported.
- A claim the current source contradicts is corrected in the new document; a gap in an owner document becomes feedback.

## 4. Verification & Test Plan

- `uv run devkit rules check --ci --base main` (AC-01, AC-06, reference resolution).
- `uv run devkit docs resolve <ID>` for each new ID (AC-01).
- `git diff --check` (AC-06).
- Manual read against the inventory rows and source, recorded in review (AC-02 to AC-05).
- `just test-affected --base 88732885f` (docs-only; the fallback to full mode is kept).
- `uv run devkit workflow envelope check --unit specs/2026-11/20261116-formal-document-coverage`.
