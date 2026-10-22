---
id: PLAN-milestone-guidance-tone
spec: SPEC-milestone-guidance-tone
---

# Technical Plan: `SPEC-milestone-guidance-tone` Recommend coarse milestones and allow merging small ones

## 1. Constitution & Invariant Review

- `ADR-roadmap-and-milestones` (Status outcome) keeps `done` and `dropped` milestones as historical documents. Merging
  deletes such a file, which widens what may happen to them: a decision change, so a new ADR is required
  (`ADR-immutable-decisions-editable-records`, "Decision changes"). It replaces only that clause, so the new ADR names
  the ADR and the clause in its outcome, and the old Status bullet gets a one-line pointer; the old ADR stays
  `accepted`.
- The Reopen outcome of `ADR-roadmap-and-milestones` stays in force; the new ADR restates that a merge is not an
  in-place extension.
- `CAP-DOCS-document-model` §3.5 already allows `aliases` as "previous or alternate IDs" on any ID-bearing document,
  milestones included, and `RULE-document-reference` already rewrites alias references through `devkit rules fix`. No
  rule or code changes.
- Capability SHOULD statements (`CAP-HARN-agent-guidance`) stay: RFC 2119 SHOULD equals "recommended" (spec Non-Goal 4).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| New ADR `docs/decisions/2026-10/20261022-milestone-merging.md` | Decision record for merging and the softened tone; partial supersession of the Status clause. |
| `docs/decisions/2026-10/20261022-roadmap-and-milestones.md` | One-line pointer on the Status outcome bullet. |
| `docs/roadmap/README.md` | Recommendation wording; merge paragraph; reworded done-extension sentence; cites the new ADR. |
| Bundle seed `seed/docs/roadmap/README.md` | Same as above without repository ADR references (bundle self-containment). |
| Bundle template `templates/milestone.md` | Goal and Exit condition guidance as recommendations. |
| Spec skill `references/backlog.md.jinja` | One `## Milestones` item with the merge procedure. |
| Spec skill `references/milestone-completion.md` | "Later changes": merge is not an in-place extension; done records stay unless merged. |
| `CAP-DOCS-document-model` rule 7, `CAP-HARN-agent-guidance` milestone paragraph | Living Spec reconciliation: the historical/done-unchanged statement gains the merge exception. |
| `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_completion_guidance.py` | Pins the recommendation and merge wording; repoints the seed done-extension assertion. |

Projected copies under `.devkit/managed/` and `.claude/` change only through `uv run devkit sync`.

## 3. Component & Interface Design

Merge procedure, as the Backlog reference states it (one list item):

1. The user decides the merge on a concrete candidate through Backlog.
2. The theme milestone (existing or new) lists every merged ID in `aliases` and states the combined goal and exit
   condition; the merged files are deleted in the same commit.
3. `devkit rules fix` moves current references; `depends_on` edges between merged milestones are removed.
4. Remaining scope becomes draft proposals in the theme; the theme is `planned` or `active` while scope remains and
   becomes `done` only through both Completion review confirmations.

## 5. Error Handling & Edge Cases

- Extending one `done` milestone's own scope without merging still needs the user's reopen to `active` with reset
  assertions, or another milestone.
- A merge into a theme whose scope then grows resets the theme's assertions like any actual semantic scope change.

## 6. Verification & Test Plan

- `just test-affected` (selects `test_milestone_completion_guidance.py` and the other bundle guidance tests).
- `uv run devkit rules check` and `uv run devkit sync --check`.
- `uv run devkit spec resolve ADR-milestone-merging`.
- `git diff --check`.
- Reconcile at `low`: self-checked reconcile against the new ADR, recorded as a `reconcile-check` envelope.
