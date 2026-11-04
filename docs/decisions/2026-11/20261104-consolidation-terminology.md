---
id: ADR-consolidation-terminology
title: Record merging is called consolidation
summary: "For the playbooks and records that merge related ADRs or feedback into one, we name the operation consolidation and keep the former compaction identifiers as aliases, to stop the term colliding with shortening and compact output, accepting alias-only resolution of the old names."
status: accepted
created_at: 2026-11-04
---

# [ADR-consolidation-terminology] Record merging is called consolidation

- **Status**: Accepted
- **Date**: 2026-11-04

---

## 1. Context & Problem Statement

devkit named the operation that merges related closed records into one replacement with aliases "compaction": the
`adr-compaction` and `feedback-compaction` playbooks, the `FB-compacted-<area>-<status>` records and the wording of
`ADR-decision-ledger` and `ADR-feedback-lifecycle-ledger`. The word has an everyday meaning, shortening, and two other
devkit meanings, `Compact output` (`devkit run`) and the `compact` subagent level. Merging records makes a longer
document, so the technical sense opposes the everyday one. An agent reading a user's everyday "compaction" of long
documents mapped it to the merge playbooks and answered the opposite question. The term appears in hundreds of
places in the bundle, the Living Spec and feedback records, so the collision recurs for every agent that loads them.

---

## 2. Decision Drivers

- The name says what the operation does: merging related records into one.
- No collision with shortening, `Compact output` or the `compact` level.
- Installed guidance, memories and references that use the old identifiers keep resolving.
- No decision of the existing ADRs changes.

---

## 3. Considered Options

- **Rename to consolidation with aliases** (selected): matches the playbooks' own descriptions ("consolidate related
  approved ADRs"); old playbook IDs and record IDs become aliases; a glossary row defines it.
- **Keep the term and define it in the glossary**: cheapest; the collision stays in every loaded asset and in the
  user's language.
- **Rename to merge or compile**: "merge" collides with Git merges throughout the delivery workflow; "compile" with
  builds.

---

## 4. Decision Outcome

Rename to consolidation with aliases, because it meets every driver at the cost of one mechanical rename.

- The playbooks are `adr-consolidation` and `feedback-consolidation`; each lists its former ID in `aliases`, so
  `devkit playbook get spec/adr-compaction` and `spec/feedback-compaction` resolve. → `CAP-HARN-agent-guidance`
  section 4.1 asset table and section 4.5 playbook table (no keyword)
- Consolidated feedback records are `FB-consolidated-<area>-<status>` at
  `specs/<YYYY-MM>/feedback/<YYYYMMDD>-consolidated-<area>-<status>.md`; each existing record keeps its former ID
  as an alias, and references in current documents name the new ID. The naming contract lives in
  `ADR-feedback-lifecycle-ledger` and the `feedback-consolidation` playbook; no capability restates it.
- The ADR consolidation groups and pointer rules of `CAP-DOCS-document-model` keep their clauses with the term
  replaced; the ledger ADRs are edited for wording only. → `CAP-DOCS-document-model` Decision supersession,
  Consolidation groups (MUST) and section 3.5 rule 5
- Retired alias IDs that carry the old word (ADR-adr-compaction, ADR-group-compaction-by-topic,
  ADR-closed-feedback-compacts-into-per-area-records-with-aliases and feedback aliases) stay as written: aliases are
  history.
- "Compaction" keeps its everyday meaning in conversation and documents; `Compact output` and the `compact` level are
  unchanged.

---

## 5. Consequences

- **Positive**: the term names the operation; the everyday word is free; old identifiers keep resolving.
- **Negative / Risks**: completed spec bundles, envelopes and materials keep the old wording as history; readers
  of history meet both terms. External notes that spell the old record IDs resolve only through aliases.
- **Follow-ups**: none.

---

## 6. Confirmation

- `devkit playbook get spec/adr-compaction` resolves to `adr-consolidation`; `devkit docs resolve` of a former
  record ID prints its alias; the `spec` bundle tests assert the playbook IDs and the record naming contract;
  `RULE-document-reference` rewrites alias references in current documents.
