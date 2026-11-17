---
id: SPEC-viewer-host-wording
title: Reword viewer documents still written for library hosts
summary: Reword UX-view-decision and mark the library-host parts of two viewer ADRs as history, so viewer documents outside the internal-viewer unit match the one-host internal viewer; no decision changes.
status: planned
created: 2026-11-17
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-host-wording] Reword viewer documents still written for library hosts

## 1. Problem Statement & Motivation

`ADR-internal-repository-viewer` made the viewer an internal tool with one host, `devkit viewer serve`, and no
library host. `SPEC-viewer-internal-simplification` updated the documents inside its boundary, but three viewer
documents outside it still read as if an embedding host existed:

- `UX-view-decision` speaks of "host screens", "Existing host navigation" and raw mode "where the host offers it".
- `ADR-viewer-namespace-roadmap-discovery` keeps its "Both dashboard routes" outcome bullet and library-host
  context and drivers without saying which parts are history.
- `ADR-viewer-indexed-decision-supersession` names local and library hosts in its drivers, options and
  consequences.

A reader can infer an embedding host or generic tree/blob discovery the viewer dropped.

## 2. User Stories

- **US-1**: As a reader of the viewer's Living Spec, I want the UX document to describe the viewer page's own
  navigation and the two ADRs to mark their library-host statements as history, so that I do not infer a second
  host.

## 3. Non-Goals

1. **Scope Excluded**: no decision changes. Each ADR keeps its decision outcome; only wording, history notes and
   the reference to `ADR-internal-repository-viewer` change. No new ADR, no `supersedes` change.
2. **Scope Excluded**: no code, test, capability or use case change; the viewer frontend is untouched.
3. **Scope Excluded**: superseded viewer ADRs that already carry a partial-supersession pointer
   (`ADR-repository-viewer`, `ADR-release-handbook`) are not reworded.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] UX-view-decision names the page's own navigation

- **Given** `docs/ux/viewer/UX-view-decision.md` after the change
- **When** `rg -n -i "host" docs/ux/viewer/UX-view-decision.md` runs
- **Then** it prints no line (exit 1), and the Purpose, Content and Interactions sections refer to the viewer page's
  own navigation, Read, Files and proposal detail views and raw mode instead.

### [AC-02] Namespace roadmap ADR marks library-host parts as history

- **Given** `docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md` after the change
- **When** a reader reads its Context, Decision Drivers and the "Both dashboard routes" outcome bullet
- **Then** each library-host statement is marked as history with a reference to `ADR-internal-repository-viewer`,
  and the set of decision outcome clauses and their capability restatements is unchanged.

### [AC-03] Indexed supersession ADR marks library-host parts as history

- **Given** `docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md` after the change
- **When** a reader reads its Decision Drivers, Considered Options and Consequences
- **Then** each library-host statement is marked as history with a reference to `ADR-internal-repository-viewer`,
  and its Decision Outcome section is byte-identical to the base.

### [AC-04] Documents stay valid

- **Given** the changed documents
- **When** `uv run devkit rules check` runs on them and on this unit
- **Then** it reports no violation (exit 0).

## 5. Source feedback

- `FB-viewer-host-wording-outside-unit`: the whole scope above; this unit fixes it directly.
