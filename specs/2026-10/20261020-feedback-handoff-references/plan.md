---
id: PLAN-feedback-handoff-references
spec: SPEC-feedback-handoff-references
---

# Technical Plan: `SPEC-feedback-handoff-references`

## 1. Constitution & Invariant Review

No architecture or decision changes. `CAP-DLV-proposal-incubation` retains record deletion and gate carry rules.
The user authorized citation-only repair of the two accepted ADRs; their decisions remain unchanged.

## 2. Architecture Overview & Impact

Proposal rewrite skips directory-only code spans. Handoff supplies the exact dropped record set to a historical
reference rewrite before ordinary relocation. That rewrite reads HEAD and verifies record bytes before pinning.
No dependencies or Git mutations are added.

## 3. Component & Interface Design

- Existing code-span rewrites require a concrete relocated file, preserving unknown and directory paths.
- A dedicated proposal helper resolves unit-relative spans and ordinary relative links using relocation origins.
  It replaces verified dropped-record references with explicit historical Git citations and records rewrites.
- A missing or changed record cannot be represented by HEAD: preserve its citation and report `unmapped`.
- Existing ADR citations use the verified pre-handoff commit containing their answer record.

## 4. Verification

Regression tests reproduce both defects before production changes. Test committed, untracked and dirty records,
no Git history, preserved concrete links and generic directories. Run proposal tests, `just test-affected --base
main`, `just lint-check spec`, `just check spec`, independent code and reconcile review, and cumulative rules.
