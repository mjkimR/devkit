---
id: PLAN-delivery-document-hygiene
spec: SPEC-delivery-document-hygiene
---

# Technical Plan: `SPEC-delivery-document-hygiene`

## 1. Constitution & Invariant Review

No contract or architectural invariant changes. Existing decision outcomes retain their meaning; only current
restatement locations may change. Historical IDs, aliases and completed evidence are preserved.

## 2. Architecture Overview & Impact

Keep workflow stages, gates and review policy in `CAP-DLV-delivery-workflows`; move role contracts, lifecycle
executor dispatch, activity-worker boundaries and worker inspection to CAP-DLV-delivery-roles (planned).
Keep proposal Planning, layout and policy in `CAP-DLV-proposal-planning`; move detailed handoff, CLI, library,
output, code and recovery interfaces to CAP-DLV-proposal-lifecycle (planned). These are existing responsibilities,
not new runtime features. Portal headings retain discoverability from existing entry points.

Move source sections intact where possible. A section map and mechanical normalized-text comparison will account
for every moved paragraph; section labels and owner references are adjusted explicitly. This avoids both
retaining a monolith behind a new index and duplicating normative contracts. Current ADR traces and CAP/UC links
are repaired only where their destination moved. The Host's exact link-repair admission list bounds those edits.

The distribution reference keeps its unique notice/error tables: the canonical sync capability points readers
there for that index. Shorten the duplicated configuration sample while keeping a practical selection example.
Renumber the duplicate use-case heading only; retain all scenarios. No source, assets or generated artifacts change.

## 6. Verification & Test Plan

- AC-01: baseline/head line counts and section map with normalized moved-text comparison; independent review.
- AC-02: current reference inspection, `uv run devkit rules check --ci --base cf1c4fd4767131c2194bfccea618dc722f49108d`,
  exact CAP/UC backlink checks and independent reconciliation review.
- AC-03: compare reference examples/diagnostic tables and line count; affected documented-code tests.
- AC-04: scenario-heading/body comparison, `git diff --check`, `uv run devkit sync --check`,
  `just test-affected --base cf1c4fd4767131c2194bfccea618dc722f49108d --tier all`, and explicit E2E selection.
- Run hygiene phase and retain its justified warnings. No full lint/types/frontend repeat for an entirely
  documentary diff: the Host verified unchanged production at the baseline with those checks and 6501 native,
  355 E2E and 167 frontend tests. No test is authored merely to mirror prose.
