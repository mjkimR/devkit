---
id: PLAN-remaining-feedback-fixes
spec: SPEC-remaining-feedback-fixes
---

# Technical Plan: `SPEC-remaining-feedback-fixes`

## 1. Constitution & Invariant Review

Documentation follows source; no `MUST` changes meaning except narrowing `CAP-SRCH-document-search` §2 "every mode"
to the modes that actually load the model, which matches `SearchIndex` and its test. No ADR is needed: no decision,
architecture rule or published contract changes. Design, domain and operations documents are unaffected: the
operations routing entries written by the formal-document-coverage Development already follow source.

## 2. Architecture Overview & Impact

Text-only edits to five documents, one regression assertion added to an existing integration test, and
dispositions on the six source feedback files. No source, dependency or bundle change, so `devkit sync` writes
nothing.

## 3. Component & Interface Design

- Search: rewrite the §4.5 pass-through sentence and the §2 `SEARCH_MODEL_INVALID` sentence; prefix §6 module names
  with their layer and move the contract types to `models/contracts.py`.
- Host reference: fill the Level and mode cell from each error class (advisory mode derivation: `input_error` gives
  `INPUT_ERROR`, `guardrail` gives `BLOCKED`, developer actor gives `MAINTENANCE`, user actor gives `INTERACTION`) and
  add the `MCP_REGISTRATION_PENDING` notice row. No anchors.
- Override: one sentence in the `remove` bullet's neighborhood stating `list`, `diff`, `accept` and `remove` results;
  pin `list`, `diff` and `accept` in `test_remove_drops_the_override_of_a_removed_asset` before `remove_override`.
- Observation: a §5 paragraph stating the observe-only scope; no failure record.
- Capabilities README: add the six areas to the tree in its existing order style.

## 4. Verification

Reproduction is document review against the cited source plus the new test assertions run on unchanged source
(they pass at once, pinning the stated behavior). Run the override tracking test file, `just test-affected --base
ad0d2f17f`, `just lint-check`, `devkit rules check --ci --base ad0d2f17f`, one `code-reviewer` pass and a reconcile
check.
