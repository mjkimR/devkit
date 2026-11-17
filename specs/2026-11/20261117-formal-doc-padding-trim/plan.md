---
id: PLAN-formal-doc-padding-trim
spec: SPEC-formal-doc-padding-trim
---

# Technical Plan: `SPEC-formal-doc-padding-trim` Trim padding from formal document guidance and documents

## 1. Constitution & Invariant Review

- `ADR-formal-document-closings` (accepted at handoff) supersedes in part `ADR-problem-first-formal-document-openings`
  and `ADR-linked-domain-relationship-views`; this plan implements its Decision Outcome and Confirmation. No further
  ADR is needed.
- `CAP-DOCS-documentation-ownership` §3.3 rule 2 is the SHOULD the ADR restates; it changes with the ADR's trace.
  §3.1 rules 5 and 7 merge into one SHOULD with an unchanged owner set (Q3), so no contract weakens.
- `CAP-DLV-proposal-lifecycle` §4.1 step 5 and §4.3 keep every guarantee `ADR-proposal-handoff` §4 and §6 confirm;
  only mechanism clauses move (Q8), which `CAP-DOCS-documentation-ownership` §3.1 rule 3 (Transfer) governs: the
  capability text goes in the same change that the design states it.
- Bundle self-containment (`agent-asset-writing`): templates and instructions cite no repository document ID.

## 2. Architecture Overview & Impact

Text-only change across one bundle, three capabilities, the formal documents and two tests; no code path changes.

- **Docs bundle** (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`): templates `design`, `domain`,
  `operations`, `capability`, `usecase`, `ux`, `milestone`; instructions `design-writing`, `domain-writing`,
  `operations-writing`, `living-spec-writing`, `document-writing`, `usecase-writing`, `ux-writing`. `devkit sync`
  rewrites `.devkit/installation.json` digests and the managed copies (ignored).
- **Living Spec**: `CAP-DOCS-documentation-ownership` (§3.1, §3.2, §3.3, §4), `CAP-DLV-proposal-lifecycle` (§4.1
  step 5, the rollback paragraph, §4.3), `CAP-DIST-sync-and-transactions` (one reference repair).
- **Formal documents**: the 13 documents per `docs/materials/2026-11/20261117-formal-doc-padding-trim/document-audit.md`;
  DESIGN-distribution-transactions is folded into `DESIGN-distribution-file-directory-replacement` (old ID in
  `aliases`, bundle deleted).
- **Tests**: `test_formal_doc_checkpoints_guidance.py` pins 15 rows and the new first row; viewer
  `FormalReading.test.ts` reads five chapters and follows capability → detail.

Formal design/domain/operations assessment: the change edits these documents themselves (no new document). Owner of
each statement stays as today except the Q8 move (capability → `DESIGN-proposal-handoff` for order and passes) and
the Q6 fold (two sentences into the successor design). Maintenance action: each document's new `## Update triggers`.
No new persisted format, identity derivation, ordering or code is introduced.

Choices made inside the agreed scope:

- `## Authority boundary` in the domain and operations templates carries a comment saying to omit it when empty,
  rather than a separate optional template, so one template serves both cases.
- Private helpers are written as words describing the step ("the target check", "the extras planner"); public names
  (`apply_changes`, `require_writable`, `recover_locked`, `handoff_proposal`, `HandoffUseCase`, `HandoffProposalUseCase`,
  `evaluate_definition`, `carry_proposal_body`, `rewrite_*`, `prepare`, `auto_register`, `move_path`, `roll_back`,
  `atomic_write`, `replace_file`, `missing_directories`, `blocked_parent`, `current_envelopes`, `record_instant`,
  `Decisions.*`) stay, since a reader searches for them.
- `DOMAIN-bundle-selection-and-installation` gets `related_designs: [DESIGN-distribution-file-directory-replacement]`,
  the design its removed line 55 reached through the capability.

## 5. Error Handling & Edge Cases

- `devkit rules fix` would rewrite the backticked old ID in the resolved feedback line to the successor twice; that
  line is edited by hand (Q6). Completed specs, reconcile records and materials keep the old ID and resolve it
  through the alias.
- `DESIGN-proposal-handoff` line 156 (ADR promotion worked-example row) is left for the sibling unit.

## 6. Verification & Test Plan

- `uv run pytest packages/devkit-spec/tests/integration/bundles/spec packages/devkit-docs/tests/integration/bundles/docs`
  (guidance pins, AC-01 to AC-04).
- The `rg` commands of AC-01, AC-02, AC-04, AC-06 and AC-08; `uv run devkit docs resolve DESIGN-distribution-transactions` (AC-07).
- `uv run devkit rules check --ci --base main`, `uv run devkit rules check --phase hygiene <bundle instructions>`.
- `uv run devkit sync`, `uv run devkit generated check`, `uv run devkit sync --check`.
- `just lint-check`, `just test-affected --base main`.
- Viewer: `just viewer install`, then the `[FRONTEND_CHECK: ...]` commands (lint, check, test, build) for
  `FormalReading.test.ts` (AC-07).
