---
id: ADR-immutable-decisions-editable-records
title: Immutable Decisions, Editable Decision Records
summary: "For a decision ledger whose append-only rule froze wording and stale references, we keep decisions immutable but let ADR documents be edited and consolidated without changing meaning, to keep records current and compact, accepting that review must judge whether an edit changes a decision."
status: accepted
created_at: 2026-10-22
supersedes:
  - ADR-adr-compaction
---

# [ADR-immutable-decisions-editable-records] Immutable Decisions, Editable Decision Records

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `docs/decisions/`, `capabilities/documents/`, `capabilities/governance/`,
  `capabilities/harness/`

---

## 1. Context & Problem Statement

`docs/decisions/` was an append-only ledger: an approved ADR was never edited or deleted, and any change was a new ADR
linked by `supersedes`. No rule enforced this; it was stated in the decisions README, the `spec-sync` skill, the
`living-spec-writing` instruction and `CAP-DOCS-document-model`, and `RULE-document-reference` exempted ADRs and PADRs
from alias rewrites. `ADR-adr-compaction` then allowed consolidation as a single exception. The rule protected the
wrong thing: what must not change silently is a decision, not its wording. Frozen documents kept stale paths, command
names and retired IDs, and the ledger fragmented.

---

## 2. Decision Drivers

- A decision is never reversed, invalidated or narrowed without a recorded new decision.
- Decision records stay current and readable: wording, format and references can be corrected.
- Related records can be consolidated without breaking references.
- Every current document, ADRs included, converges on canonical IDs through one `devkit rules fix`.

---

## 3. Considered Options

### Option 1: Immutable decisions, editable records (Selected)
- **Overview**: a change of decision needs a new ADR; an edit that keeps every decision's meaning is allowed in place.
- **Pros**: records stay current; compaction is an ordinary edit; references in ADRs are fixed like any other.
- **Cons**: whether an edit changes meaning is a judgment, not a mechanical check.

### Option 2: Append-only with compaction as the only exception (`ADR-adr-compaction`)
- **Overview**: the previous rule.
- **Cons**: stale wording and references stay in every ADR; each other kind of cleanup needs its own exception.

### Option 3: Freely editable ADRs
- **Cons**: a decision could change without a record.

---

## 4. Decision Outcome

We adopt **Option 1**.

- **Decision changes**: reversing, invalidating, narrowing or widening a decision, or changing its scope, drivers'
  weight or consequences, is a new ADR. When it replaces a whole ADR, it names it in `supersedes`, and the replaced
  ADR gets `status: superseded` and `superseded_by`. When it replaces only part of an ADR, it names that ADR and the
  part in its outcome, and the earlier ADR's affected statement gets a one-line pointer to the new ADR.
- **Editorial edits** are allowed in place on accepted ADRs and need no new ADR: wording and format, the template's
  current sections, stale paths, command, code and file names, references rewritten to canonical IDs, and metadata
  (`status`, `superseded_by`, `aliases`). An edit that would change what a statement decides is a decision change.
- **Compaction**: related ADRs may be consolidated into one replacement ADR whose `aliases` lists the retired IDs and
  every alias they declared; the retired files are deleted in the same commit. The replacement's outcome holds exactly
  the statements in effect, each citing its source ID; superseded parts are left out, rejected alternatives stay in
  the considered options. A contradiction or a statement that no longer matches the code or the Living Spec is not
  resolved by compaction; it goes to feedback or a proposal. A group is closed under supersession. A compaction runs
  when the user explicitly invokes the `adr-compaction` playbook, which authorizes its deletions, at `session` depth.
  Superseded in part by `ADR-spec-intake-playbook-discovery`: confirming a discovered candidate is that invocation.
- **References in decision records**: `RULE-document-reference` reports an alias reference in an ADR or PADR like one
  in any current document, and `devkit rules fix` rewrites it to the canonical ID. This replaces the decision-record
  exemption of `ADR-document-id-aliases` (its "References" outcome). Historical files (completed spec bundles, done or
  dropped milestones) stay as written.
- **Checks**: no rule detects a decision change; review of the diff does. A compaction run is complete when
  `devkit rules fix` then `devkit rules check` pass, every deleted ADR ID resolves through `devkit spec resolve`, and a
  fidelity review finds no changed decision.

---

## 5. Consequences

- **Positive**: ADRs carry current names and canonical IDs; consolidation is routine.
- **Negative / Risks**: an editorial edit could change meaning unnoticed; the edit's diff review is the guard.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/document_reference/tests/test_rule.py`
  (`test_alias_references_in_decision_records_are_fixed`, `test_alias_references_in_history_stay`).
- Diff review for decision changes; the `adr-compaction` playbook's completion checks.
