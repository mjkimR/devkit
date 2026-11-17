# Planning evidence for PROP-formal-doc-authoring-checkpoints

Rechecked at worktree HEAD of `plan-formal-doc-authoring-checkpoints` (base `22cacbe52`).

## Counts and inventories

- `specs/*/*/reconcile.md`: 260 records. Every spec bundle has `status: completed`; no bundle is in flight.
- Records that mention a DESIGN, DOMAIN or OPS ID or a `designs/`, `domain/` or `operations/` path: 10, all in
  `specs/2026-11/20261116-*` bundles of the formal-document work (domain-model-documents, design-document-foundation,
  design-bundle-layout, reverify-summary-required, remaining-feedback-fixes, proposal-precedence-edges,
  formal-document-coverage, formal-document-kinds, formal-docs-feedback-handoff, formal-document-templates). The
  draft's "6 of 258" predates the last integrations.
- `docs/development/reference/`: 18 pages besides the README. Code tables use at least eight column sets, e.g.
  `Code | Level | Class | Condition` (compact, search, worktree, generated), `Code | Caller action` (exec),
  `Code | Class | Mode | Exit | Meaning` (gate), `Code | Level | When` (rules), `Code | Exit | When` (viewer).

## Owners of the touched contracts

- The reconcile record form is checked by `RULE-reconcile-contract`
  (`packages/devkit-spec/src/devkit_spec/features/governance/usecases/reconcile_contract.py`), not by
  `RULE-spec-progress`, which is a warning-level progress hint on `spec.md` versus `tasks.md`.
- `RULE-reconcile-contract` already separates form (every run) from diff evidence (snapshot runs only, and only for a
  `resolved` record whose frontmatter differs from the base). A completed bundle's record is checked only when named
  as an explicit target. The staged commit gate names staged files as targets.
- The record schema is stated in the `spec-sync` skill step 2 and the rule guide; `CAP-GOV-spec-rules` lists the
  rule; `CAP-DLV-delivery-workflows` rule 9 requires the design/domain/operations assessment "in existing
  plan/reconcile bodies" and rule 15 requires review to compare it with the diff.
- `reconcile-reviewer` findings today: missing target, reflection contradicting implementation or contract, waiver of
  a required mismatch, a stated no-impact the diff contradicts. Nothing names formal-document content.
- Review severity (`review-loop.md` §3): reconcile P1 is a missing target or contradiction, P2 an incomplete or
  imprecise reflection, P3 an improvement. Severity changes no check; P2 and P3 may be waived with a reason.
- `CAP-DOCS-documentation-ownership` §3.1 rule 5 routes by responsibility; `living-spec-writing` "Responsibility and
  design navigation" projects it as one sentence. No text says what stays out of a capability.
- `design-writing` item 6 and the design template mention datasheets as optional; nothing names when one is due.
- The docs template set is pinned in three places: the docs and spec bundle constitutions
  (`templates/{capability,usecase,ux,decision,milestone,design,domain,operations}.md`),
  `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` and
  `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`; `CAP-DOCS-document-model` counts "eight
  formal templates".
- No ADR fixes the reconcile record to its current keys; `ADR-review-loop` keeps round numbers out of new envelope
  fields, which does not cover reconcile frontmatter.

## Concurrent proposals

- `SPEC-handoff-rewrite-overlap-scheduling` (draft) owns `packages/devkit-spec/tests/` and the `spec-orchestrate`
  skill. This proposal's owned paths are narrowed to the files it changes so the only shared prefix is the test tree.
