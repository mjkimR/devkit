---
id: PADR-consolidated-record-budgets
title: Rule-local budgets for alias-bearing records
summary: "For long consolidated ADRs and feedback, we opt into a rule-local line budget selected by record ID and aliases, to keep settings resolution pure, accepting a documented alias-based heuristic for ADRs."
proposal: PROP-consolidated-record-length
status: draft
created_at: 2026-11-04
---

# [PADR-consolidated-record-budgets] Rule-local budgets for alias-bearing records

- **Status**: Draft
- **Date**: 2026-11-04

## 1. Context & Problem Statement

`ADR-decision-ledger` keeps a topic's decisions together. Ordinary line-length remediation splits that record,
while exact-path exceptions accumulate. `ADR-feedback-lifecycle-ledger` appends closed outcomes to area records.
The pure typed settings resolver knows path patterns but no document content; its optional integer vocabulary
already supports a rule-owned budget. Alias metadata does not establish consolidation provenance for ADRs.

## 2. Decision Drivers

- Preserve existing consumer defaults and higher path-specific budgets.
- Keep file reading and record-specific judgment outside the reusable settings model.
- Bound the larger budget while preserving consolidation fidelity.
- Reuse existing fields without requiring document-model changes.

## 3. Considered Options

- **Rule-local optional budget (selected):** one typed setting and a cached header lookup only for over-budget
  Markdown. Small implementation, with explicit record-kind knowledge in this builtin and ADR heuristic matches.
- **Generic frontmatter override matching:** reusable predicates for all rules, requiring a new policy grammar,
  injected content loader, validation and caching semantics. No second consumer in this scope justifies that cost.
- **Exact-path overrides (current state):** no implementation but recurring edits per consolidated record.
- **New consolidation marker:** exact provenance, requiring document-kind and authoring changes outside scope.

## 4. Decision Outcome

- `RULE-file-length` exposes optional `consolidated_max_lines`, omitted by default and positive when set.
  → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- Eligible Markdown has `ADR-` identity and at least two distinct nonempty string aliases, or
  `FB-consolidated-<area>-<status>` identity and at least one; absent or malformed headers keep the ordinary limit.
  ADR alias history is a heuristic that can match repeated renames, not evidence of a consolidation operation.
  → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- The effective budget is the larger of the resolved ordinary and consolidated limits; consumers omitting the
  option retain existing behavior. → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- This repository selects 600 lines for both kinds; a warning prompts topic review without dropping retained
  decisions or outcomes. Existing records and feedback grouping policy are not changed by this work.
- Generic settings resolution remains path-only and performs no frontmatter reads.

## 5. Consequences

- Six existing consolidated ADR warnings disappear while the 619-line document-system ADR remains visible.
- The builtin recognizes two record ID conventions without depending on `devkit-docs` or its document model.
- Repeated ADR renames can receive the larger warning budget. Exact provenance would require a separate
  document-model decision if that ambiguity causes a concrete harmful outcome.
- Feedback records still grow; exceeding the budget signals the already deferred grouping decision.

## 6. Confirmation

The rule's `file_length/tests/` and integration tests verify eligibility, defaults, malformed input, precedence,
limits and remediation. Content tests verify playbook fidelity wording. A same-head disabled/enabled comparison
verifies the six affected ADR identities. `CAP-GOV-evaluation-lifecycle` section 5 restates the lasting contract.
