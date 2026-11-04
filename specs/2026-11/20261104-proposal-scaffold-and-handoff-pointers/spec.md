---
id: SPEC-proposal-scaffold-and-handoff-pointers
title: Lean proposal scaffold and handoff supersession pointers
summary: Make devkit spec proposal new create no empty directories and devkit spec proposal handoff write the Superseded in part by pointer for each partially superseded ADR, so a Planning worktree holds what it needs and the handoff commit passes its gate.
status: completed
created: 2026-11-04
related_capabilities: [CAP-DLV-proposal-planning]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-proposal-scaffold-and-handoff-pointers] Lean proposal scaffold and handoff supersession pointers

## 1. Problem Statement & Motivation

Handed off from proposal PROP-proposal-scaffold-and-handoff-pointers on 2026-11-04.

Two frictions of the proposal lifecycle in `devkit-spec` surfaced in one Planning and handoff
(`SPEC-ux-coverage-explicit-exceptions`):

- `devkit spec proposal new` creates empty `decisions/` and `materials/` directories. Git tracks no empty directory,
  so the Planning worktree created by `devkit worktree start plan-<slug>` has neither, and the first write to
  `materials/` fails with "no such file or directory". `devkit spec proposal padr` already creates `decisions/` on
  demand, and devkit's record writers create `decisions/` and `envelopes/` for gate records and envelopes.
- `devkit spec proposal handoff` promotes a PADR whose `supersedes` names an ADR it replaces only in part, but writes
  no "Superseded in part by `ADR-<slug>`: <clauses>" line into that ADR. `RULE-decision-supersession` exempts PADRs,
  so the gap is first seen by the handoff's own commit gate, which refuses the transaction
  (`SPEC_HANDOFF_COMMIT_REFUSED`) and leaves the writes staged for a manual repair. The pointer cannot be written in
  Planning because `ADR-<slug>` does not resolve before the handoff.

The scaffold creates no empty directory, and each directory is created by the command that first writes into it. The
handoff writes the pointer line for every `supersedes` target that is not `superseded`, using the PADR's `summary` as
the clause description for Development to refine at `living-spec-draft`; the handoff commit then passes its gate
without manual repair.

## 2. User Stories

- **US-1**: As a Planning agent in a fresh `plan-<slug>` worktree, I want the proposal bundle to hold only tracked
  files, so that my first write to `materials/` needs no `mkdir` surprise and the bundle shows what it holds.
- **US-2**: As the Host running `devkit spec proposal handoff`, I want a partially superseding PADR to land with its
  pointer in the earlier ADR, so that the handoff commit passes `RULE-decision-supersession` without a manual repair.
- **US-3**: As a Development agent, I want the handoff output to name each pointer it wrote, so that I know which
  ADR line to refine with the replaced clauses at `living-spec-draft`.

## 3. Non-Goals

1. **Scope Excluded**: writing `status: superseded` or `superseded_by` into a target ADR. **Rationale**: a whole
   supersession hides the earlier ADR from browsing and search, a judgment the author makes
   (`CAP-DOCS-document-model`, Decision supersession).
2. **Scope Excluded**: parsing the PADR's Decision Outcome for the replaced clauses. The pointer carries the PADR's
   `summary`; Development replaces it with the clauses.
3. **Scope Excluded**: changing `RULE-decision-supersession` or checking PADRs against their `supersedes` targets in
   Planning.
4. **Scope Excluded**: a pointer for a `supersedes` target that is a PADR promoted in the same handoff. **Rationale**:
   both ADRs are new; the author edits the sibling PADR before the handoff. **When to Reconsider**: a report of a
   refused handoff commit for that case.
5. **Scope Excluded**: seeding `decisions/` or `materials/` with a tracked placeholder file.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The scaffold writes only files

- **Given** a workspace without a proposal of the slug
- **When** `devkit spec proposal new <slug>` runs, with or without `--with-target-docs`
- **Then** the bundle directory holds `proposal.md` (and `target-docs.md` under `--with-target-docs`) and no
  `decisions/` or `materials/` directory, the `[PROPOSAL: ...]` line is unchanged, and the exit code is `0`

### [AC-02] Commands that write into a directory create it

- **Given** a bundle created by `new` with no `decisions/` directory
- **When** `devkit spec proposal padr <slug> "<title>"` runs
- **Then** `decisions/PADR-<padr slug>.md` exists and the command exits `0`
- **And When** the bundle has no `decisions/` or `materials/` directory and the proposal is accepted
- **Then** `devkit spec proposal handoff <slug>` promotes no ADR, reports no `[MATERIALS: ...]` line and exits `0`

### [AC-03] The handoff writes one pointer per partial superseder

- **Given** an accepted ADR ADR-old at `docs/decisions/<dir>/<file>.md` whose body has no "Superseded in part by"
  line, and an accepted proposal whose PADR PADR-pick-a has `supersedes: [ADR-old]` and
  `summary: "<Y-statement>"`
- **When** `devkit spec proposal handoff <slug>` runs
- **Then** the ADR file gains exactly one line "Superseded in part by ADR-pick-a: <Y-statement>" directly below
  its H1 heading, separated by one blank line on each side, its frontmatter and `status: accepted` are unchanged, and
  the ADR text is otherwise byte-identical
- **And** `devkit rules check <ADR-pick-a path> <ADR-old path>` reports no `RULE-decision-supersession` violation
- **And** stdout has one line `[SUPERSEDED_IN_PART: ADR-old path=<ADR-old path> line=<n> by=ADR-pick-a]` after the
  `[PROMOTED_ADR: ...]` lines, and `--format json` lists `{"adr": "ADR-old", "path": ..., "line": <n>, "by":
  "ADR-pick-a"}` under `pointers`

### [AC-04] A pointer already present is not written twice

- **Given** the setup of AC-03 where ADR-old already has a visible line naming "Superseded in part by
  ADR-pick-a" (by its ID or an alias of the promoted ADR)
- **When** the handoff runs
- **Then** the ADR file is byte-identical to before, and no `[SUPERSEDED_IN_PART: ...]` line names it

### [AC-05] Targets the pointer rule does not need are left alone

- **Given** a PADR whose `supersedes` lists an ADR with `status: superseded`, an ID that resolves to no document, and
  an ID that resolves to a non-ADR document
- **When** the handoff runs
- **Then** none of those files changes, the promoted ADR keeps the `supersedes` value as written, the handoff exits
  `0`, and the unresolved ID stays `RULE-document-reference`'s report on the promoted ADR

### [AC-06] A pointer without a summary falls back to the title

- **Given** a PADR with `supersedes: [ADR-old]` and no `summary` key (the scaffold's commented placeholder)
- **When** the handoff runs
- **Then** the pointer reads "Superseded in part by `ADR-<slug>`: <PADR title>."

### [AC-07] A failed handoff restores the target ADR

- **Given** the setup of AC-03 and a failure after the pointer write (a refused write of a later file)
- **When** the handoff rolls back
- **Then** ADR-old is byte-identical to its text before the handoff, the proposal is kept, and the handoff fails
  with the failure's own code or `SPEC_PROPOSAL_HANDOFF_FAILED`

### [AC-08] The handoff on `dev-<slug>` leaves the pointer in the transaction

- **Given** a committed repository on `dev-<slug>` holding the setup of AC-03
- **When** `devkit spec proposal handoff <slug>` runs there
- **Then** `git status --porcelain` lists the changed ADR-old file beside the new spec bundle and ADR, so the
  composed handoff's `git add -A` stages it, and `devkit rules check` on the two ADRs reports no
  `RULE-decision-supersession` violation

### [AC-09] Contracts and guidance restate the behavior

- **Given** `CAP-DLV-proposal-planning`, the `devkit spec proposal` CLI docstring, the proposal template's lifecycle
  comment and the spec skill's `references/planning.md`
- **When** a reader looks up the bundle layout, the handoff steps or where `materials/` comes from
- **Then** the bundle layout says `new` writes `proposal.md` (and `target-docs.md`) only and names the command that
  creates each directory; handoff step 4 says the handoff writes one "Superseded in part by" line per `supersedes`
  target that is not `superseded`, once, with the PADR `summary` (or title) as the clause text for Development to
  refine; the output section lists `[SUPERSEDED_IN_PART: ...]`; and `references/planning.md` says `materials/` is
  created with its first file

## Assumptions

- The pointer is inserted below the H1 heading rather than at the affected statement, because the handoff cannot
  locate the affected statement (`CAP-DOCS-document-model` allows either placement).
- The pointer text ends with a period; a `summary` already ending in `.`, `!` or `?` is left as it is. Whitespace runs
  in the summary collapse to one space.
- A target whose `status` is anything other than `superseded` (`accepted`, `proposed`, `deprecated`, `rejected`)
  receives the pointer, matching the condition `RULE-decision-supersession` checks.
- When the ADR has no H1 heading, the pointer goes directly after the frontmatter block.
- The dedicated `[SUPERSEDED_IN_PART: ...]` line replaces the proposal's `[REWRITTEN ...]` suggestion: `REWRITTEN`
  reports relocated references, and an agent branching on sentinel kinds needs the new effect under its own kind.

## Source feedback

- `FB-proposal-scaffold-dirs-vanish-in-worktree` (promoted): the empty `materials/` and `decisions/` directories;
  this spec delivers the scaffold change and the planning reference note.
- `FB-handoff-writes-no-partial-supersession-pointer` (promoted): the missing pointer at handoff; this spec delivers
  the handoff change.

Both sources are terminal (`promoted`); their references stay for traceability and no disposition is written.

## 5. Carried Proposal Notes

### Technical Spike Questions (answered)

- **Q1**: no reader relies on the empty directories: `handoff` reads `decisions/` and `materials/` only when they
  exist (`_plan_decisions`, `_has_material`, `_plan_extras`), `prune` removes empty trees, `report` reads the
  proposal, PADRs and envelopes, the workflow record writers create `decisions/` and `envelopes/` themselves.
- **Q2**: the PADR `summary` in both cases (AC-03), the title without one (AC-06); Development refines the clauses at
  `living-spec-draft`.
- **Q3**: the line is written once (AC-04).

### Lifecycle & Retirement Criteria

Completion: the handoff of a proposal with a partially superseding PADR commits without manual repair, and a fresh
Planning worktree needs no `mkdir`.
