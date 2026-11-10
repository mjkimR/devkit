---
id: PLAN-file-byte-budgets
spec: SPEC-file-byte-budgets
---

# Technical Plan: `SPEC-file-byte-budgets`

## 1. Constitution & Invariant Review

The builtin keeps its package, rule identity, deterministic offline behavior, cache boundary and hygiene phase.
`ADR-byte-based-file-budgets` partially replaces `ADR-consolidated-record-budgets` for the metric, setting names and
repository thresholds before implementation. No feature dependency or architecture boundary changes.

## 2. Architecture Overview & Impact

The existing file-length builtin owns byte counting and consolidated selection. The generic typed resolver keeps
its current validation and precedence; renamed fields naturally reject obsolete keys. CLI adapters keep their
sentinels, JSON shape and error codes. Source playbooks and the two governance capabilities describe the same units.

## 3. Component & Interface Design

`FileLengthSettings(max_bytes=49152, extensions=[".md"], consolidated_max_bytes=None)` replaces line fields.
`FileLengthRule(max_bytes=49152)` reads `len(ctx.cache.read_bytes(path))`. A violation remains file-level warning
with line 1 and `File exceeds byte budget (<actual> > <limit> bytes)`. Header parsing occurs only for over-budget
Markdown when the optional consolidated budget exists. Qualified records use the larger resolved budget.

The project config replaces its 600-line values with 65536-byte CAP and consolidated limits. Obsolete settings
are rejected, not translated: no faithful universal conversion from lines exists. Keep the existing class/module
names to avoid unrelated API churn. Retain current remediation and no-autofix semantics.

## 4. Error Handling & Edge Cases

The existing settings errors handle obsolete keys, wrong types and invalid positive limits. Raw byte reads preserve
CRLF and invalid UTF-8 sizes. Snapshot evaluation continues through the cache/materialized tree, never `stat` on a
live path. Keep alias qualification, malformed-frontmatter fallback and ordinary higher overrides unchanged.

## 6. Verification & Test Plan

- AC-01/02/04: builtin tests cover exact boundaries, multibyte/long-line/newline/binary input, targeting,
  consolidated selection/laziness and a real staged snapshot whose live bytes disagree.
- AC-03/05: typed resolver, evaluator and CLI check/explain text/JSON tests prove renamed keys, invalid values,
  the default byte count and unchanged phase/severity.
- AC-06: source playbook assertions, document rules, source-pinned before/after hygiene JSON, and capability/ADR
  comparison. The baseline is `materials/hygiene-before.json`, captured before source edits on this branch.
- Required native commands: `just lint-check dev`, `just lint-check spec`, `just check dev`, `just check spec`,
  `uv run devkit rules check --ci --base 7bc401d4f599ff3373a01a11084e7719fe1272f0`,
  `just test-affected --base 7bc401d4f599ff3373a01a11084e7719fe1272f0 --tier all`, source builtin/playbook tests,
  sync and generated checks. Preserve full fallback; run required E2E synchronously here.
- Medium effort uses independent code and reconcile reviews. Host owns integration and landed-head verification.
