---
id: SPEC-scope-boundary-candidates
title: Drop entrypoint candidates once a spec declares its code boundary
summary: Once tasks.md declares _Boundary code paths, the work scope registry compares a spec unit by its declared and observed code only, so the entrypoints of a broad capability target no longer report overlaps outside the unit's boundary.
status: in-progress
created: 2026-10-22
related_capabilities: [CAP-COLL-work-scope-registry]
related_usecases: [UC-run-parallel-work-safely]
workflow: sdd-spec-feature
---

# [SPEC-scope-boundary-candidates] Drop entrypoint candidates once a spec declares its code boundary

## 1. Problem Statement & Motivation

`devkit spec scope` builds a spec bundle's code side from two declarations: the `tasks.md` `_Boundary` entries
(`declared-code`) and the `entrypoints` of every capability or use case target of `reconcile.md` or `target-docs.md`
(`candidate`, `CAP-COLL-work-scope-registry` §4.1). A unit that lists a broad capability as a reconcile target
therefore claims every code path that capability lists, even after its tasks name a much narrower boundary.

`SPEC-periodic-drift-reconciliation` listed `CAP-DLV-delivery-workflows` as a `modified` reconcile target. At the
feedback's base revision that capability's `entrypoints` included the `spec-delegate` and `spec-orchestrate` skill
directories, so `devkit spec scope update` reported both as `source=candidate` overlaps with another running unit
across two revisions, although the unit's `_Boundary` entries named neither and its handoff denied both. The feedback
attributed this to observation-only imported feedback; the actual mechanism is the target's entrypoints.
`spec-orchestrate` runs units that overlap one after another, so these candidate-only overlaps cost parallelism
without reflecting any planned write.

Candidates estimate the code a task will touch before it says so. Once `tasks.md` declares code paths, the unit has
said so, and Git observes what it actually changes at build. The agreed intent (decision `gate:plan-intent`, option A)
is that a spec unit whose `tasks.md` declares `_Boundary` code paths is compared by its declared and observed code
only; before that, candidates stay as today.

### Source feedback

- `FB-scope-observation-candidates` (scope `repo`, open): scope overlap reported candidate paths the unit's task
  boundaries did not name. Addressed directly by this spec.

## 2. User Stories

- **US-1**: As an orchestrating agent, I want a spec unit whose tasks declare their code boundary to be compared by
  that boundary and by what Git observes, so that a broad Living Spec target does not serialize units whose
  declared and observed code is disjoint (`UC-run-parallel-work-safely`).
- **US-2**: As an orchestrating agent, I want proposals and spec bundles without declared code to keep their
  entrypoint candidates, so that overlaps are still estimated before tasks exist.

## 3. Non-Goals

1. **Scope Excluded**: changing the `no-entrypoints` unresolved reason. A capability or use case target without
   `entrypoints` stays unresolved (`reason=no-entrypoints`, `source=candidate`) at every stage, also when declared
   code replaces the candidates.
   - **Rationale**: the reason reports a gap in the target document's code traceability, which stays true whether or
     not candidates are used; `UC-run-parallel-work-safely` Scenario 4 states it for a spec without qualification,
     and `spec-orchestrate` orders units by overlaps, not by unresolved counts, so keeping it costs no parallelism.
   - **When to Reconsider**: when a consumer starts treating unresolved counts as a reason to serialize units.
2. **Scope Excluded**: rewriting records registered before this change. A stored record keeps the candidate paths it
   was collected with until its next `register` or `update` recollects the scope; comparison reads stored records as
   they are.
3. **Scope Excluded**: treating a `_Boundary` that resolves to no code path (`N/A`, a placeholder, a path under
   `docs/` or `specs/`, an invalid path) as a declared code boundary; such a bundle keeps its candidates.
4. **Scope Excluded**: changing proposal (`prop` stage) scope sets, observed-path collection, document overlap,
   comparison semantics, output lines or codes, or the guidance of the `spec-orchestrate` and `spec-delegate`
   skills.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Declared code replaces target entrypoint candidates
- **Given** a spec bundle whose `tasks.md` declares at least one `_Boundary` entry that resolves to a code path and
  whose `reconcile.md` targets a capability with `entrypoints` outside that boundary
- **When** its scope set is built (`devkit spec scope compare --spec`, `register`, `update` or `query --spec`)
- **Then** its code side holds only `source=declared-code` paths, no `source=candidate` path, and its document side
  still holds the capability target

### [AC-02] A candidate-only path no longer overlaps
- **Given** that spec bundle and a second scope set whose only code path is an entrypoint of the first bundle's
  target that the first bundle's `_Boundary` does not cover
- **When** the two are compared
- **Then** the pair reports `code=0`, while document overlap on a shared target is still reported

### [AC-03] Candidates stay before code is declared
- **Given** a proposal, a spec bundle whose `tasks.md` is missing or still the handoff skeleton, and a spec bundle
  whose `_Boundary` entries resolve to no code path (only `N/A`, placeholders or paths under `docs/` or `specs/`)
- **When** each scope set is built
- **Then** each holds the `entrypoints` of its capability and use case targets as `source=candidate` code paths, as
  before this change

### [AC-04] Observed paths are still compared
- **Given** a registered spec bundle with declared code and a committed change in its worktree outside that boundary
  and outside every target's `entrypoints`
- **When** it runs `devkit spec scope update`
- **Then** the record holds the changed file as `source=observed`, and a scope set whose declared code covers that
  file overlaps it with `kind=code` evidence

### [AC-05] Missing target entrypoints stay unresolved
- **Given** a spec bundle with declared code whose `reconcile.md` targets a capability without `entrypoints`
- **When** its scope set is built
- **Then** the target is unresolved with `reason=no-entrypoints`, as before this change

### [AC-06] The contract states the rule
- **Given** `CAP-COLL-work-scope-registry`
- **When** it is read after this change
- **Then** §4.1 states that target `entrypoints` contribute candidates only while the bundle declares no `_Boundary`
  code path, and §4.2 states that a spec with declared code is compared by its declared and observed code

## 5. Assumptions

1. "Declares `_Boundary` code paths" means that at least one `_Boundary` entry of a non-skeleton `tasks.md` resolves
   to a `declared-code` path under `CAP-TRACE-code-entrypoints`; the rule is per bundle, not per task.
2. The rule applies wherever a spec bundle's scope set is built, so `compare --spec`, `register`, `update` and
   `query --spec` share it; a stored record's scope changes at its next recollection.
3. The diagnosis was verified at the feedback's base revision a7958abb: `CAP-DLV-delivery-workflows` listed the
   `spec-delegate/` and `spec-orchestrate/` skill directories as `entrypoints`, and the unit's `reconcile.md` targeted
   it as `modified`.
