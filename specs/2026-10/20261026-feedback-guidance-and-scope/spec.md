---
id: SPEC-feedback-guidance-and-scope
title: Scratch cleanup guidance, merge-conflict interaction and declared feedback scope
summary: 'Resolves three decided feedback items: workers leave ignored scratch files to worktree removal, a handoff materials merge conflict asks the user instead of blocking, and scope registration accepts explicitly declared feedback files of other spec bundles.'
status: in-progress
created: 2026-10-26
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-COLL-work-scope-registry
  - CAP-DLV-delivery-workflows
  - CAP-WT-task-worktrees
  - CAP-DIST-sync-and-transactions
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-guidance-and-scope] Scratch cleanup guidance, merge-conflict interaction and declared feedback scope

## 1. Problem Statement & Motivation

Three open feedback items need a behavior or guidance change the user decided (`materials/decisions.md`, items 1-3),
and five documentation mismatches found by the Living Spec consistency sweep travel with them (items 4-8):

- A Development payload asked a worker to delete a scratch fixture; the host denied the recursive removal, so the
  worker had to leave it and ask the Host. Workers should never be asked to delete ignored scratch files: removing
  the worktree cleans them.
- A materials merge conflict at proposal handoff renders the `BLOCKED` guardrail directive ("do not propose or apply
  a way around it") beside a fix that tells the agent to reconcile the path. The conflict is a data collision the
  user resolves, not a rule.
- A spec that resolves another spec bundle's feedback file declares that exact path in its task `_Boundary`, but
  scope registration reports it as `excluded-tree`, so two units resolving the same feedback never overlap.
- The proposal error table, the devkit-spec README and MCP install guide, the glossary and actor table, the task
  worktree module layout and the config template example describe states the package no longer has.

## 2. User Stories

- **US-1**: As a Development worker, I want guidance that leaves ignored scratch files to worktree removal, so that
  a host permission denial on recursive deletion never stops my turn.
- **US-2**: As a Host agent handing off a proposal, I want a materials merge conflict to tell me to ask the user, so
  that I neither treat a data collision as an unchangeable rule nor rename materials without the user.
- **US-3**: As a Host scheduling parallel units, I want two units that resolve the same feedback file to overlap, so
  that the scope registry warns me before both edit it.
- **US-4**: As an agent reading the Living Spec and guides, I want the documented modes, dependencies, terms, module
  paths and template values to match the shipped package.

## 3. Non-Goals

1. **Scope Excluded**: widening host permissions for recursive removal, and forcing exploratory fixtures into pytest
   tests (rejected in decision 1).
2. **Scope Excluded**: changing the code `SPEC_PROPOSAL_TARGET_EXISTS` or the class `ProposalTargetExistsError`, an
   agent-fixable merge mode, or a mode change of an existing-target refusal (decision 2;
   `ADR-merge-proposal-materials-per-leaf-at-handoff` stays as accepted).
3. **Scope Excluded**: scope exceptions for globs, directories, non-feedback files of another spec bundle or `docs/`
   paths, an informational reason without a scope, and moving feedback closure to the Host (decision 3).
4. **Scope Excluded**: entrypoint derivation pairs: a feedback file is never a code entrypoint.
5. **Scope Excluded**: redesigning the modes of `HandoffNotReadyError`, `HandoffReplyError` and `HandoffStaleError`
   (item 4 records a defect as feedback).
6. **Scope Excluded**: `FB-plain-handoff-skips-proposal-handoff-policy` and
   `FB-config-template-reports-unchanged-after-writing`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Worker scratch guidance leaves cleanup to worktree removal
- **Given** the development-worker role contract of the `spec` bundle
- **When** its rule 8 is read
- **Then** it keeps authored scratch files in an ignored path inside the worktree, tells the worker not to delete them
  and says that removing the worktree cleans them; the `tmp_path` and `--basetemp` sentences are unchanged

### [AC-02] Payload and mirrored guidance never ask for create-then-delete
- **Given** the `spec-delegate` payload reference, the planning-worker role contract and `CAP-DLV-delivery-workflows`
- **When** they describe a worker's scratch files or probes
- **Then** the payload reference states that a payload never asks a worker to delete a scratch file or fixture it
  created, and no worker text requires removing ignored probes before the last commit

### [AC-03] A materials merge conflict asks the user
- **Given** a proposal whose `materials/` holds a file whose bytes differ from the same path in the existing dated
  materials directory
- **When** the proposal handoff runs
- **Then** it writes nothing and raises `SPEC_PROPOSAL_TARGET_EXISTS` with mode `INTERACTION`, `guardrail` false and
  actor `USER`, and the fix still names the first conflict's source, destination, kind and reconciliation

### [AC-04] An existing handoff target stays a guardrail
- **Given** the spec bundle directory or an ADR file that the handoff would create already exists
- **When** the handoff runs
- **Then** it refuses with `SPEC_PROPOSAL_TARGET_EXISTS` and mode `BLOCKED`, as before

### [AC-05] A declared feedback file of another spec bundle enters the scope
- **Given** a spec bundle whose `tasks.md` `_Boundary` names the exact path `specs/<other bundle>/feedback/<name>.md`
- **When** its scope is collected (`devkit spec scope register`, `update` or `compare --spec`)
- **Then** the path is a `declared-code` scope path of granularity `file` and not unresolved, and two units declaring
  the same feedback file report one code overlap on it

### [AC-06] Other spec-tree paths stay excluded
- **Given** `_Boundary` entries naming another bundle's `spec.md`, its `feedback/` directory, a `docs/` path, or a
  `feedback/` file of the declaring unit itself
- **When** the scope is collected, and when `devkit spec entrypoints derive` runs on the same bundle
- **Then** each such entry is unresolved `excluded-tree` (a glob stays `invalid-path`), and entrypoint derivation
  still skips every `specs/` path, the feedback file included, as `excluded-tree`

### [AC-07] Feedback files do not replace entrypoint candidates
- **Given** a spec bundle whose only path-like `_Boundary` entries are other bundles' feedback files
- **When** its scope is collected
- **Then** its targets' `entrypoints` stay `candidate` code paths beside the feedback file

### [AC-08] Living Spec and guides match the shipped package
- **Given** items 4-8 of `materials/decisions.md`
- **When** the touched documents are read
- **Then** the devkit-spec README and `guides/install/mcp.md` claim no native handoff runtime and no `devkit-mcp`
  dependency of devkit-spec; the glossary has no **Integration MCP** term and the `ARCH-04-1-ecosystem-boundaries`
  actor row names the `devkit integration` CLI; `CAP-WT-task-worktrees` §7 lists only modules that exist; the
  `CAP-DIST-sync-and-transactions` template shows `worktree = "auto"`; and each handoff error-mode mismatch is either
  documented by its shipped mode or recorded as a defect in a new feedback file

## 5. Assumptions

- Decision 2 names `_refuse_merge`: only the merge refusal into the existing materials directory changes mode, the
  dated path that is not a real directory included. The clash of a carried bundle file with `materials/` inside the
  proposal and a directory resolving outside the workspace stay `BLOCKED`: neither is a merge into the existing
  directory.
- "Another spec bundle" means a `feedback/` file outside the declaring unit's directory; the unit's own feedback keeps
  `excluded-tree`.
- The exception needs no existing file: a planned feedback path is collected with granularity `unknown`; a path that
  exists as a directory stays `excluded-tree`.
- Item 4: `HandoffNotReadyError` and `HandoffReplyError` refuse on prerequisites and input the caller controls, so
  their shipped `MAINTENANCE` is a defect: their rows keep the documented modes and a new feedback records the defect.
  The `SPEC_HANDOFF_STALE` row already documents its shipped mode.

## 6. Source feedback

- `FB-fixture-removal-denied` (decision 1)
- `FB-merge-conflict-guardrail-action` (decision 2)
- `FB-scope-external-feedback-target` (decision 3)
- `FB-handoff-error-modes-documented-differently` (item 4)
- `FB-spec-readme-and-mcp-guide-native-handoff` (item 5)
- `FB-integration-mcp-glossary-and-actor-row` (item 6)
- `FB-worktree-module-layout-stale` (item 7)
- `FB-sync-config-template-example-stale` (item 8)
