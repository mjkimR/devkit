---
id: SPEC-partial-adr-supersession
title: Keep partially superseded ADRs accepted and searchable
summary: An ADR becomes superseded only when wholly replaced; a partial replacement keeps it accepted with a superseded-in-part line, the PADR scaffold offers supersedes, and misclassified ADRs are corrected.
status: completed
created: 2026-10-30
related_capabilities: [CAP-DOCS-document-model, CAP-DLV-proposal-planning]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-partial-adr-supersession] Keep partially superseded ADRs accepted and searchable

## 1. Problem Statement & Motivation

`status: superseded` is terminal for a decision: browsing and search hide the ADR unless `--history` is passed
(`CAP-DOCS-document-model`, rule 8). Several ADRs carry that status although their superseder replaced only some of
their clauses, so the clauses still in force disappear from search. `ADR-local-and-pull-request-integration` is the
reported case: `ADR-host-cli-lifecycle-authority` replaced only its lifecycle request, native confirmation and resume
clauses, yet `devkit docs search "Local and Pull Request Integration"` does not return it although its merge
construction is the current contract of `CAP-INT-mcp-services`.

`ADR-immutable-decisions-editable-records` already separates whole replacement (`status: superseded`,
`superseded_by`) from partial replacement (a one-line pointer at the earlier ADR), but no document a writer reads
states it: `CAP-DOCS-document-model` names only the terminal status, the docs bundle's `decision-writing` instruction
and decision template say nothing about supersession, and the PADR scaffold offers no `supersedes` key. Writers fell
back to `superseded_by` for partial replacements and to ad-hoc prose pointers.

## 2. User Stories

- **US-1**: As an agent searching decisions, I want an ADR whose decisions are only partly replaced to stay
  `accepted`, so that `devkit docs search` returns the clauses still in force.
- **US-2**: As an agent writing a decision, I want the decision format to state when an ADR becomes `superseded` and
  how a partial replacement is recorded, so that the ledger stays consistent.
- **US-3**: As a Planning agent, I want the PADR scaffold to offer `supersedes`, so that a preliminary decision names
  the ADR it replaces and handoff carries it into the ADR.

## 3. Non-Goals

1. **Scope Excluded**: a structured partial-supersession field (`superseded_in_part_by`, `status: amended`) or a
   parsed decision `supersedes` reference graph. **Rationale**: the agreed scope keeps the status and a body line;
   `supersedes` and `superseded_by` on a decision stay unparsed metadata.
2. **Scope Excluded**: changing any decision. The ledger correction changes only `status`, `superseded_by`,
   `supersedes`, the body status line and "Superseded in part by" lines.
3. **Scope Excluded**: `ADR-moved-target-merge` (a sibling worker supersedes it in part on another branch).
4. **Scope Excluded**: the spec constitution's sentence on changed decisions; it already reads "a new ADR with
   `supersedes`", which holds for whole and partial replacements, so it needs no "in part".

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The decision format states whole and partial supersession

- **Given** `CAP-DOCS-document-model`, the docs bundle's `decision-writing` instruction, its decision template and its
  seeded `docs/decisions/README.md`
- **When** a writer reads how a later decision replaces an earlier ADR
- **Then** each states that an ADR gets `status: superseded` and `superseded_by` only when a later ADR replaces all of
  its in-force decisions, and that a partial replacement keeps it `accepted` without `superseded_by` and adds a body
  line "Superseded in part by `ADR-<new>`: <which clauses>", while the new ADR names it in `supersedes` and states the
  replaced clauses
- **And** a guidance test asserts the rule in `decision-writing` and the template

### [AC-02] A decision's `supersedes` naming an ADR is valid metadata

- **Given** an ADR whose `supersedes` lists an accepted ADR, and a PADR whose `supersedes` names one as a scalar
- **When** `RULE-document-reference` checks them
- **Then** it reports no violation (the `PROP-`-only rule applies to Unit anchors), and no rule or code requires
  the named ADR to be `status: superseded`

### [AC-03] The PADR scaffold offers `supersedes` and handoff carries it

- **Given** a proposal bundle
- **When** `devkit spec proposal padr <slug> "<title>"` runs
- **Then** the PADR frontmatter has the commented line `# supersedes: [ADR-<slug>]` with a note to name the replaced
  clauses in Decision Outcome, and its parsed frontmatter is unchanged (no `supersedes` key)
- **And When** the author uncomments it with an existing ADR ID and the proposal is handed off
- **Then** the promoted ADR keeps that `supersedes` value, and handoff leaves the named ADR unchanged
- **And** `CAP-DLV-proposal-planning` documents the commented key and that handoff edits no superseded ADR

### [AC-04] The ledger matches the rule

- **Given** the nine `status: superseded` ADRs and the ADRs with a partial-replacement pointer under `docs/decisions/`
- **When** a superseder's own text shows it replaces only part of the earlier ADR
- **Then** that ADR is `status: accepted` with no `superseded_by`, its body status line reads Accepted, and it carries
  one "Superseded in part by `ADR-<new>`: <clauses>" line per partial superseder, using the superseder's description
  of the replaced clauses
- **And** an ADR wholly replaced (its superseder restates or replaces every clause) stays `superseded`
- **And** `reconcile.md` lists every ADR changed or reviewed, with the reason
- **And** `uv run devkit docs search "Local and Pull Request Integration"` lists `ADR-local-and-pull-request-integration`
- **And** `uv run devkit rules check` reports no violation

## 5. Assumptions

1. No new ADR is needed: the whole/partial rule is the "Decision changes" outcome of
   `ADR-immutable-decisions-editable-records`. Naming the partly replaced ADR in `supersedes` too, as the agreed scope
   requires, adds metadata that outcome does not forbid and that `ADR-host-cli-lifecycle-authority`,
   `ADR-lean-subagent-level` and `ADR-host-owned-scope-observation` already write.
2. The in-part line goes directly below the ADR's H1 heading unless an existing pointer already sits at the affected
   statement; existing pointers in other wordings ("supersedes only ...", "This decision alone is superseded by") are
   rewritten into the "Superseded in part by" form in the ADRs this Unit touches, without changing what they say.
3. The clauses an in-part line names are taken from the superseder's own statement of what it replaces, so no
   decision is reinterpreted.
4. The commented key is a YAML list (`[ADR-<slug>]`) because a decision can supersede several ADRs; a scalar stays
   valid metadata.

## 6. Source feedback

- `FB-partial-supersession-hides-in-force-clauses`: addressed directly. In scope: the rule in the decision format, the
  PADR scaffold's `supersedes`, and correcting `ADR-local-and-pull-request-integration` and every other misclassified
  ADR. Out of scope: its suggested structured field (`superseded_in_part_by`, `status: amended`), Non-Goal 1.
