---
reconcile_id: REC-namespace-roadmap
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-roadmap-and-milestones-ledger.md
    resolution: modified
  - file: docs/roadmap/README.md
    resolution: modified
---

# Reconciliation: `SPEC-namespace-roadmap`

## Contract comparison

`ADR-namespace-milestone-roots` (promoted at handoff) decides that a registered namespace keeps its milestones at
`docs/packages/<name>/roadmap/` with the global lifecycle placement, validated by mapping the path through
`living_path` onto the global layout, with repository-wide identity and the namespace-generic selection. The
implementation matches: `RULE-id-convention` validates every docs root's `roadmap/` through
`milestone_path_valid(living_path(path, namespaces=registered), status)` and names both roots in its remediations;
the `MILESTONE` kind row is `FormatScope.EVERY_ROOT`, so `RULE-spec-format` scans a namespace `roadmap/` (with its
flat `_archive/`, history-targeted by status as the global one) and guards its milestone checks by the same mapping;
`devkit spec proposal new --milestone` accepts a milestone at either root and refuses an invalid placement with
`ARGUMENT_INVALID` naming both roots and `devkit docs list milestone --all-namespaces`. `milestone_path_valid` and
its regex are unchanged (Non-Goal 4); the `PROPOSAL` row stays `GLOBAL` (Non-Goal 3); the viewer is untouched
(Non-Goal 5).

The Living Spec restates each clause where it lived:

- `CAP-GOV-spec-rules`: the Milestone validation contract names the two roots, the `living_path` validation and the
  invalid cases (other nesting, an unregistered namespace's roadmap directory, a milestone outside every root); the
  `RULE-spec-format` scope list gains `roadmap/` of each namespace docs root and its intro no longer says "global
  milestone".
- `CAP-DOCS-namespaces` 3.4: `RULE-id-convention` and `RULE-spec-format` check a namespace `roadmap/` (with its flat
  `_archive/`) as they check `docs/roadmap/`; 3.2 and 3.3 are unchanged rules the change relies on.
- `CAP-DOCS-document-model`: the Milestone placement paragraph and the `MS` kind-table row name one roadmap root per
  milestone (global or a registered namespace's) instead of "global only" (review-01 finding 1).
- `CAP-DLV-proposal-planning`: the `milestone` field row and the `--milestone/-m` option row accept a milestone at
  the global or a namespace roadmap root, with the `--all-namespaces` fix; `UC-route-development-intent` says the same
  in its Backlog step and its Then line (review-01 finding 3).
- `CAP-HARN-agent-guidance`: the roadmap paragraph of the `spec` bundle's guidance names both roots, matching the
  edited `backlog.md`, `roadmap-catalog.md` and `milestone-completion.md` (review-01 finding 2).
- `ARCH-01-introduction-and-goals` Repository roadmap: names the namespace root and the goal a namespace milestone
  cites (this document or an architecture document under its namespace docs root), as the ADR's Q2 finding.
- `ADR-roadmap-and-milestones-ledger`: the "Superseded in part by" line names the two replaced clauses
  (ADR-milestone-documents' global-only sentence and ADR-archive-terminal-milestones-in-roadmap's global-root wording)
  as `ADR-namespace-milestone-roots` section 4 lists them; every other clause stands.
- `docs/roadmap/README.md`: the roadmap guide names the two roots, the in-root `_archive/` move and
  `--all-namespaces`.

The `docs` and `spec` bundle text (rule guides, milestone template, seed, the three `spec` references) is the
agent-facing copy of the same clauses; `devkit sync` regenerated this repository's deployed copies and
`.devkit/installation.json` is its receipt. No glossary term is introduced (`milestone`, `namespace` and `roadmap
root` keep their meaning). `CAP-VIEW-repository-viewer` is unchanged on the user's Planning decision; the viewer's
`docs/roadmap/`-only reading is the follow-up below.

## Entrypoints

`packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py` is added to
`CAP-DLV-proposal-planning` (the `--milestone` validation); `CAP-GOV-spec-rules` already lists
`packages/devkit-docs/src/devkit_docs/features/governance/`, and `CAP-DOCS-namespaces` keeps
`services/namespaces.py` and `repositories/config.py`, which did not change.

## Deferred work and source feedback

No source feedback (spec section 5). Deferred work: the local viewer reads `docs/roadmap/` only and will omit
namespace milestones, mis-render a global milestone that depends on one and show a namespace-milestone proposal in no
roadmap card; this is `FB-viewer-namespace-roadmap-roots` (open, carried in this bundle's `feedback/`), triggered when
a repository with namespace milestones uses the viewer. `FB-padr-default-slug-from-long-title` (open, carried here)
concerns the Planning guidance's `--slug` example, unrelated to this change, and stays open for a later task.

## Verification and retained work

`just test-affected` 2218 passed at the build head; the `spec_format` rule tests 21 passed after the review fix;
`just lint-check` and `just check` pass for `devkit-docs` and `devkit-spec`; `uv run devkit rules check --ci --base
dbaf8f38` errors=0 warnings=0 on the build head (reviewer run); `uv run devkit generated check` passes. Code review
round 1 (`review-01`, native `code-reviewer`) found one P2 and three P3, all Living Spec drift or a test gap; the
fixes are applied and closed in `reverify-01`.
