---
id: PLAN-steering-alias-autofix
spec: SPEC-steering-alias-autofix
---

# Technical Plan: `SPEC-steering-alias-autofix`

## 1. Constitution & Invariant Review

No architecture or ADR change is required. `CAP-GOV-spec-rules` explicitly describes report-only alias findings
for these inputs; revise that capability for the approved autofix extension. Keep cache-only reads/writes,
existing Markdown masking and document-index boundaries from `ARCH-05-2-components`.

## 2. Architecture Overview & Impact

Extend the governance use case's existing fix pass to steering paths. Share Owner extraction between checks and
repairs, exposing source spans within recognized tables. Apply replacements from right to left so variable ID
lengths cannot corrupt adjacent content. No feature dependencies or public interfaces change.

## 3. Component & Interface Design

`DocumentReferenceRule.check` marks uniquely resolved Owner and steering aliases fixable. Its `fix` method rewrites
code-span citations through `_rewrite_citations`, then glossary Owner alias spans while preserving brackets.
Missing and ambiguous references remain report-only. Rule guide and capability document the same boundary.

## 6. Verification & Test Plan

AC-01/02: deployed rule tests for both Owner delimiters, source columns, whitespace, repeated IDs and idempotency.
AC-03: masked spans, canonical/missing/ambiguous references, exclusions and targeting tests.
AC-04: cache-backed rule fixtures plus unchanged DocumentIndex coverage.
Run `uv run devkit rules test RULE-document-reference`, `just lint-check docs`, `just check docs`,
`just test-affected`, cumulative CI rules and `devkit sync --check`. Independent code review at medium effort;
self reconciliation is sufficient if the single capability and guide match all changed checks exactly.
