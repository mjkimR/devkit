---
id: SPEC-adr-admission-and-trace-format
title: ADR admission criteria and restatement trace format
summary: decision-writing gains admission criteria that ADRs and PADRs share, and Decision Outcome clauses record their restatement as a trailing trace with the target ID, location and keyword instead of inline RFC 2119 keywords.
status: planned
created: 2026-11-02
related_capabilities: [CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adr-admission-and-trace-format] ADR admission criteria and restatement trace format

## 1. Problem Statement & Motivation

`SPEC-adr-normative-outcomes` made each normative Decision Outcome clause carry an inline RFC 2119 keyword and its
restating ID. That format has two problems:

- The keyword sits inside the sentence, so the ADR reads like a policy. "Blueprint or Policy in Disguise" is a known
  ADR anti-pattern. The keyword was only meant to record how the clause was restated.
- The trace names the target document but not the rule inside it.

Separately, `decision-writing` says how to write an ADR or PADR but not when one is warranted. Planning creates a PADR
for any decision, and handoff promotes every PADR to an ADR. As a result, small and local choices accumulate as ADRs:
97 accepted ADRs in October 2026.

## 2. User Stories

- **US-1**: As a reviewer, I want each Decision Outcome clause to say where and how strongly it was restated, so that I
  can go from the decision to its final contract in one step.
- **US-2**: As an author in Planning or Development, I want a clear threshold for writing an ADR or PADR, so that
  choices that are small and local stay in the proposal or spec records.

## 3. Non-Goals

1. **Scope Excluded**: Changing handoff. PADR promotion stays as it is, and the threshold applies when a PADR is
   created.
2. **Scope Excluded**: Compacting or retiring existing ADRs that fall below the threshold.
   - **When to Reconsider**: in an `adr-compaction` run.
3. **Scope Excluded**: An importance or priority field on decisions.
4. **Scope Excluded**: A governance rule that checks the trace format.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Admission criteria shared by ADRs and PADRs
- **Given** the docs bundle's `decision-writing` instruction
- **When** an author decides whether to record an ADR or a PADR
- **Then** the instruction lists the criteria. At least one must hold:
  - the decision is costly to reverse;
  - it affects more than one package, feature area or document kind;
  - more than one viable option was weighed;
  - it changes an existing contract or a lasting rule.
- **And** it directs a choice that meets none of them to the proposal's Planning decisions or the spec's `plan.md`
  instead
- **And** it states that the criteria apply to ADRs and PADRs alike

### [AC-02] Planning applies the criteria before creating a PADR
- **Given** the spec bundle's Planning reference
- **When** a Planning run is about to create a PADR
- **Then** the reference directs it to apply the `decision-writing` admission criteria first
- **And** it directs it to keep a choice that fails them in the proposal's Planning decisions

### [AC-03] Declarative clauses with a trailing restatement trace
- **Given** `decision-writing` and the `decision` template
- **When** an author writes a Decision Outcome clause that a capability or architecture document restates
- **Then** the clause is a declarative sentence without an RFC 2119 keyword
- **And** it ends with `→ <ID> <location> (<KEYWORD>)`. The location is a section or rule of the restating document,
  and the keyword is the one that document uses.
- **And** a clause with no restating document carries no trace
- **And** the bundle text names placeholder IDs only

### [AC-04] Marked ADRs follow the new format
- **Given** the 13 ADRs whose Decision Outcome carries a restatement marker
- **When** the change lands
- **Then** no Decision Outcome clause in them carries an inline RFC 2119 keyword that this spec added
- **And** each marker is rewritten to `→ <ID> <location> (<KEYWORD>)`
- **And** the keyword matches the restating document
- **And** the edits are format-only and change no decision

### [AC-05] Checks pass
- **Given** the finished change
- **When** `uv run devkit rules check`, `--phase hygiene` on the edited bundle assets and `just test-affected` run
- **Then** each exits `0`
