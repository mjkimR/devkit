---
id: SPEC-handoff-rewrite-overlap-scheduling
title: Handoff rewrites as integration evidence in scope scheduling
summary: Tells the Host in the spec-orchestrate skill to discount overlap that only the units' completed handoff commits wrote, so handoff reference rewrites alone no longer serialize otherwise separate Development workers.
status: in-progress
created: 2026-11-17
related_capabilities: [CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-handoff-rewrite-overlap-scheduling] Handoff rewrites as integration evidence in scope scheduling

## 1. Problem Statement & Motivation

Handed off from proposal PROP-handoff-rewrite-overlap-scheduling.
Evidence: `docs/materials/2026-11/20261117-handoff-rewrite-overlap-scheduling/overlap-evidence.md`.

The spec-orchestrate skill runs units whose `horizon=current` evidence overlaps sequentially. A Development unit's
observed paths include every path its handoff commit changed, so the reference rewrites a completed, Host-owned
handoff transaction makes count as current overlap. Two otherwise separate Development units serialized on eight
such paths (`FB-handoff-reference-overlap-serializes-workers`).

Those rewrites are already complete; two of them on one file conflict only at integration, which runs one unit at a
time in overlap order. Treating them as integration-conflict evidence restores parallel Development without
weakening the guarantee for declared or worker-made writes.

## 2. User Stories

- **US-1**: As the Host scheduling parallel Development, I want overlap that only completed handoff commits wrote to
  stay integration-conflict evidence, so that handoff reference rewrites alone do not serialize separate workers.

## 3. Non-Goals

1. **Scope Excluded**: no change to `devkit spec scope collect` code, its output contract
   (`CAP-COLL-work-scope-registry`), tests or any command; no path-class exemption; no change to the integration
   order or to Planning-horizon (`future`) scheduling.
   - **When to Reconsider**: if the manual provenance check recurs or is misapplied, move provenance into collection
     as a new evidence source.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Handoff-only paths do not serialize Development
- **Given** two Development units whose only `current` overlap is on paths whose evidence is `observed` only, and
  each such path changed in that unit's handoff commit and in none of its later commits
  (`git diff --name-only <handoff commit>..<unit head>` does not list it)
- **When** the Host schedules them by the spec-orchestrate skill
- **Then** the skill directs that the pair may run Development in parallel, that such a path stays
  integration-conflict evidence resolved during integration in overlap order, and that neither worker payload names
  it as a write target

### [AC-02] Declared, candidate or later-commit evidence still serializes
- **Given** an overlapping path that, for either unit, has declared or candidate evidence or appears in a commit after
  that unit's handoff commit
- **When** the Host schedules the pair
- **Then** the skill still directs that the units run sequentially, as before

### [AC-03] The Living Spec mirrors the rule
- **Given** the amended skill scheduling bullet
- **When** `CAP-HARN-agent-guidance` "Host scope observation" is read
- **Then** it states the same rule, and `uv run devkit rules check --ci --base main` and `uv run devkit generated check`
  report no violation

### [AC-04] The refs-rewritten notice docstring covers alias rewrites
- **Given** the `ProposalReferencesRewrittenNotice` class in `packages/devkit-spec/src/devkit_spec/base/errors.py`
- **When** its docstring is read
- **Then** it names spec, ADR and stale-alias rewrites, and its code `SPEC_PROPOSAL_REFS_REWRITTEN`, level and fix
  are unchanged (Host-authorized scope extension)

## 5. Assumptions

- The Host has each unit's handoff `commit` from the handoff return and each evidence entry's `source` from
  `scope collect`, so the check needs no new data (Planning answer Q2).
- The rule covers every reference rewrite a handoff commit makes, including the sibling-alias rewrites of
  `SPEC-handoff-sibling-alias-rewrite`, because it is keyed to provenance, not path class.

## 6. Source feedback

- `FB-handoff-reference-overlap-serializes-workers` (full scope).
- `FB-refs-rewritten-notice-docstring` (full scope, Host-authorized extension).
