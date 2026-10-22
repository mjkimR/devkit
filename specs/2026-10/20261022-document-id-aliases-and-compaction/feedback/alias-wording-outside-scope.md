---
id: FB-alias-wording-outside-scope
title: Alias wording left in contracts and mirrors outside the unit's write scope
scope: repo
kind: friction
category: spec-ambiguity
target: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-alias-wording-outside-scope] Alias wording left in contracts and mirrors outside the unit's write scope

## 1. Friction / Question (friction, question)

- **Context**: The reconcile verification of `SPEC-document-id-aliases-and-compaction` found contracts and consumer
  mirrors that describe exact IDs only, outside the unit's write scope.
- **Expectation**: Every contract naming a changed behavior states the alias case explicitly.
- **Actual**: `CAP-DLV-spec-bundles` (rule 3 and the `SPEC_EXISTS` row: an alias now blocks a spec slug),
  `CAP-TRACE-code-entrypoints` (`--target` accepts an alias), `CAP-DIST-manifest-spec` (playbook kind summary and the
  alias uniqueness check at manifest validation), the bundled devkit `consumption` instruction (playbook get by a
  declared alias) and `docs/glossary.md` (no alias term, Avoid "search keyword") are unchanged.
- **Workaround (or Interpretation Chosen)**: `CAP-DOCS-document-model` section 3.5 rule 6 states the cross-contract
  rule (an alias declaration counts as a declaration; ID arguments resolve aliases), so the unchanged wording stays
  correct; the projected devkit-playbook skill text was updated in scope.
- **Suggestion**: Add the explicit alias wording to the listed files in a follow-up edit.

## Evidence

- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/specs.py` (`index.declares`).
- `packages/devkit-spec/src/devkit_spec/features/entrypoints/usecases/derive.py` (`index.resolve`).
- `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/manifest.py` (`_check_playbook_aliases`).

- **Disposition (resolved)**: `SPEC-contract-alignment` added the alias case to `CAP-DLV-spec-bundles` (rule 3 and
  `SPEC_EXISTS`), `CAP-TRACE-code-entrypoints` (`--target` and its error rows), `CAP-DIST-manifest-spec` (the
  playbook kind and a **Playbook aliases** validation rule), the devkit bundle `consumption` instruction (`playbook get`
  by a declared alias) and `docs/glossary.md` (an `Alias` row, "search keyword" under Avoid), each checked against
  the cited code. Verified by `devkit rules check --ci`, `devkit sync --check`, `just test-affected` and the unit's
  review.
