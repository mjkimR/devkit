---
id: SPEC-milestone-guidance-tone
title: Recommend coarse milestones and allow merging small ones
summary: "Softens the milestone granularity guidance from SHOULD rules to recommendations and lets small milestones of any status merge into a broader theme that keeps their IDs as aliases, while a done milestone's scope still extends only by reopening or another milestone."
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-HARN-agent-guidance
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-milestone-guidance-tone] Recommend coarse milestones and allow merging small ones

## 1. Problem Statement & Motivation

Milestones are meant to be loosely managed themes, but the roadmap guidance reads as hard rules: the repository
roadmap README, the shipped seed README and the milestone template state granularity and exit-condition wording as
SHOULD and SHOULD NOT. `ADR-roadmap-and-milestones` also keeps every `done` and `dropped` milestone as a historical
document, so small milestones created before the coarse-theme guidance cannot be folded into the theme they belong
to. The repository merged five such milestones into `MS-maintenance-operations` (base commit `e048c24f`) as a one-off:
the theme declares their IDs in `aliases`, their files are gone and `devkit rules fix` moved current references.
Nothing documents that procedure or permits it.

## 2. User Stories

- **US-1**: As a user reviewing the roadmap with an agent, I want granularity guidance phrased as a recommendation, so
  that a narrow milestone is a judgment call rather than a rule violation.
- **US-2**: As a user, I want to merge small milestones of any status into a broader theme milestone through Backlog,
  so that the roadmap shows themes instead of fragments while every old ID still resolves.
- **US-3**: As an agent closing or extending milestones, I want the in-place extension rule for `done` milestones kept
  and distinguished from merging, so that a confirmed completion is never silently reopened.

## 3. Non-Goals

1. **Scope Excluded**: Code, CLI, rule or hygiene-warning changes; merging is a documented Backlog edit that uses the
   existing `aliases` field and `devkit rules fix`.
2. **Scope Excluded**: Editing any milestone document (`docs/roadmap/MS-*.md`), including `MS-maintenance-operations`,
   which is the worked example only.
3. **Scope Excluded**: Changing the closure assertions, their invalidation, or the reopen rule for a `done`
   milestone's own scope.
4. **Scope Excluded**: Rewording the normative SHOULD statements in capabilities; in RFC 2119 terms SHOULD already
   means "recommended", so only the user-facing guidance documents change tone.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Granularity and exit-condition guidance is a recommendation
- **Given** the repository roadmap README, the shipped seed roadmap README and the shipped milestone template
- **When** an agent reads their granularity and exit-condition guidance
- **Then** each prefers a broader multi-unit theme over a milestone that only sequences one proposal and recommends
  phase-level exit conditions, and none contains `SHOULD NOT` or `SHOULD represent`
- **And** the bundle guidance tests assert the recommendation wording in the seed README and the template

### [AC-02] Merging small milestones is a documented Backlog procedure
- **Given** the shipped Backlog reference (`references/backlog.md`), the seed roadmap README and the repository roadmap
  README
- **When** an agent prepares a milestone merge
- **Then** the guidance permits merging milestones of any status (`planned`, `active`, `done`, `dropped`) into a
  broader theme milestone on the user's Backlog decision, and names each step: the theme lists the merged IDs in
  `aliases`, the merged files are deleted in the same commit, `devkit rules fix` moves current references, remaining
  scope moves to draft proposals, and the theme stays `planned` or `active` while scope remains and becomes `done`
  only through both Completion review confirmations
- **And** a bundle guidance test asserts these clauses in the Backlog reference

### [AC-03] Extending a done milestone in place still needs a reopen
- **Given** the shipped milestone completion reference, the seed roadmap README and the repository roadmap README
- **When** an agent extends the scope of a `done` milestone instead of merging it
- **Then** the guidance still requires the user's reopen to `active` with both assertions reset, or another milestone,
  and states that a merge is not an in-place extension
- **And** the existing guidance tests for the reopen rule pass unchanged or pinned to the new wording

### [AC-04] A new ADR supersedes the historical-document clause
- **Given** `ADR-roadmap-and-milestones`, whose Status outcome keeps `done` and `dropped` milestones as historical
  documents
- **When** `devkit spec resolve ADR-milestone-merging` runs
- **Then** it resolves to an accepted ADR whose outcome names `ADR-roadmap-and-milestones` and the replaced Status
  clause, records the merge procedure, and keeps the reopen rule
- **And** the Status outcome of `ADR-roadmap-and-milestones` carries a one-line pointer to the new ADR, that ADR keeps
  `status: accepted` (a partial supersession under `ADR-immutable-decisions-editable-records`), and
  `devkit rules check` reports no violation

## 5. Assumptions

- `CAP-DOCS-document-model` (historical documents) and `CAP-HARN-agent-guidance` (milestone guidance) state that
  `done` and `dropped` milestones remain history; the Living Spec reconciliation adds the merge exception to that
  statement only.
- The merged milestones' `depends_on` edges on each other become self-references after `devkit rules fix`; the
  Backlog step removes them, because `RULE-document-reference` reports a `depends_on` cycle as an error.
- A merge changes the theme milestone's semantic scope, so its Completion review assertions are pending after a merge,
  as for any other actual scope change.
- `ADR-immutable-decisions-editable-records` keeps done and dropped milestones "as written" only against reference
  rewrites by `devkit rules fix`; deleting a merged file is a separate, user-decided edit and needs no change there.
