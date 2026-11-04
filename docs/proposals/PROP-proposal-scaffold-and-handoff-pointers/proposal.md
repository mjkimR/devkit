---
id: PROP-proposal-scaffold-and-handoff-pointers
title: Lean proposal scaffold and handoff supersession pointers
summary: Make devkit spec proposal new create no empty directories and devkit spec proposal handoff write the Superseded in part by pointer for each partially superseded ADR, so a Planning worktree holds what it needs and the handoff commit passes its gate.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: delivery/
priority: high                        # critical | high | medium | low
size: S                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - docs/capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-proposal-scaffold-and-handoff-pointers] Lean proposal scaffold and handoff supersession pointers

## 1. Background & Hypothesis

Two frictions of the proposal lifecycle in `devkit-spec` surfaced in one Planning and handoff
(`SPEC-ux-coverage-explicit-exceptions`):

- `devkit spec proposal new` creates empty `decisions/` and `materials/` directories. Git tracks no empty directory,
  so the Planning worktree created by `devkit worktree start plan-<slug>` has neither, and the first write to
  `materials/` fails. `padr` already creates `decisions/` on demand.
- `devkit spec proposal handoff` promotes a PADR whose `supersedes` names an ADR it replaces only in part, but writes
  no "Superseded in part by `ADR-<slug>`: <clauses>" line into that ADR. `RULE-decision-supersession` exempts PADRs,
  so the gap is first seen by the handoff's own commit gate, which refuses the transaction
  (`SPEC_HANDOFF_COMMIT_REFUSED`) and leaves the writes staged for a manual repair. The pointer cannot be written in
  Planning because `ADR-<slug>` does not resolve before the handoff.

Hypothesis: the scaffold creates no empty directory and names where each is created on demand, and the handoff
writes the pointer line for every `supersedes` target that stays `accepted`, using the PADR's `summary` as the
clause description for Development to refine; the handoff commit then passes its gate without manual repair.

## Source feedback

- `FB-proposal-scaffold-dirs-vanish-in-worktree`: the empty `materials/` and `decisions/` directories; this proposal
  receives the scaffold change and the planning reference note.
- `FB-handoff-writes-no-partial-supersession-pointer`: the missing pointer at handoff; this proposal receives the
  handoff change.

## 2. Technical Spike Questions

- **Q1**: Does any reader rely on the empty directories existing after `new` (the `decomposer` payload, `report`,
  `prune`, the materials move at handoff)? Expected: none, since each reads or moves only existing files.
- **Q2**: Which pointer text does the handoff write when the PADR's Decision Outcome names the replaced clauses, and
  which when it does not? Expected: the PADR `summary` in both cases, with the planning reference asking Development
  to replace it with the clauses at `living-spec-draft`.
- **Q3**: What happens when the target ADR already carries a pointer naming the new ID (a rerun after a partial
  handoff)? Expected: the line is written once.

## 3. Proposed Design & Impact

- `scaffold.py`: `new` writes `proposal.md` only (and `target-docs.md` with `--with-target-docs`); `padr` keeps
  creating `decisions/` on demand; the spec skill's `references/planning.md` says `materials/` is created with its
  first file.
- `handoff.py`: for each promoted PADR with `supersedes`, each target whose status is not `superseded` receives one
  "Superseded in part by `ADR-<new>`: <PADR summary>" line below its heading, once; the target is staged with the
  transaction and the `[REWRITTEN ...]` notice lists it. A target that does not resolve stays
  `RULE-document-reference`'s report.
- `CAP-DLV-proposal-planning` restates both; the handoff tests gain the partial-supersession fixture and the scaffold
  tests the directory assertion.

Non-goals: writing `superseded` status or `superseded_by` (a whole supersession stays the author's edit); parsing
Decision Outcome clauses; changing `RULE-decision-supersession`.

## 4. Lifecycle & Retirement Criteria

Direction settled; eligible for direct acceptance. Completion: the handoff of a proposal with a partially superseding
PADR commits without manual repair, and a fresh Planning worktree needs no `mkdir`.
