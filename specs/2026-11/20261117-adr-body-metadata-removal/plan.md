---
id: PLAN-adr-body-metadata-removal
spec: SPEC-adr-body-metadata-removal
---

# Technical Plan: `SPEC-adr-body-metadata-removal` Remove the ADR body metadata block and trim the ADR template

## 1. Constitution & Invariant Review

- `ADR-frontmatter-only-decision-status` (accepted at handoff) is the lasting decision; this plan implements its
  Decision Outcome and Confirmation. No further ADR is needed.
- `CAP-DLV-proposal-planning` §4.4 and `CAP-DLV-proposal-lifecycle` §4.1 step 4 change their PADR body statements in
  the same change as the code, as the ADR's planned traces name.
- The existing-ADR pass is a wording and metadata repair: it changes no decision, so no ADR is superseded.
- Bundle self-containment (`agent-asset-writing`): the template and instruction cite no repository document ID.

## 2. Architecture Overview & Impact

- **Docs bundle** (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`): `templates/decision.md` loses the
  metadata block, the per-option Overview/Pros/Cons and every body `---`; Considered Options takes the Q4 lines.
  `instructions/decision-writing.md` states the frontmatter-only status and asks to mark the selected option.
  `devkit sync` rewrites `.devkit/installation.json` digests.
- **devkit-spec proposals feature**: `usecases/scaffold.py` `_padr` writes no body metadata; `usecases/handoff.py`
  drops `_DRAFT_BODY_STATUS` and the body rewrite and gains a deletion-only pass for the legacy scaffold block.
- **Living Spec**: `CAP-DLV-proposal-planning` §4.4, `CAP-DLV-proposal-lifecycle` §4.1 step 4 and the ADR-promotion
  observed-run row of `DESIGN-proposal-handoff`.
- **Existing ADRs**: one mechanical pass over `docs/decisions/` at the Development head.

### Choices made inside the agreed scope

- The legacy-block deletion runs on `visible_lines` like the old rewrite, so fenced, indented and commented lines are
  never candidates. "The first list after the H1" is the first run of consecutive non-blank source lines after the
  H1 whose first line is a visible list item; scanning stops at the first heading. A status line with a trailing HTML
  comment is still the scaffold line and is deleted.
- The template's Considered Options comment points to `decision-writing` by name (a bundle-local instruction), so the
  bundle stays self-contained.
- The existing-ADR pass is a scratch script run once; its result is reviewed as a diff, not kept as code, since no
  later run needs it.

## 3. Error Handling & Edge Cases

- A PADR whose first list item is not the status line (for example a hand-written list) keeps its list; only the
  status line and a directly following date line are deleted, and the `---` stays when the list keeps items.
- A PADR without the block is promoted with its body unchanged apart from the ID rename and pointers.
- A hand-edited legacy block that does not match (for example a Deciders line) stays; the ADR names this risk.

## 4. Verification & Test Plan

- `uv run pytest packages/devkit-docs/tests/integration/bundles/docs packages/devkit-spec/tests/integration/bundles/spec`
  (AC-01, AC-02).
- `uv run pytest packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py
  packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py` (AC-03, AC-04).
- The `rg` commands of AC-05 and AC-06; `uv run devkit rules check docs/decisions`;
  `uv run devkit docs refs CAP-DLV-project-policy --direction in` still lists `ADR-document-system` and
  `ADR-worktrees-and-scope` (AC-05).
- `uv run devkit sync`, `uv run devkit generated check`, `uv run devkit sync --check`,
  `uv run devkit rules check --ci --base main`, `just lint-check`, `just test-affected --base main` (AC-07).
