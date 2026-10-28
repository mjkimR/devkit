---
id: PLAN-milestone-archive
spec: SPEC-milestone-archive
---

# Technical Plan: `SPEC-milestone-archive`

## 1. Constitution & Invariant Review

`ADR-archive-terminal-milestones-in-roadmap` partially supersedes root-only storage in `ADR-roadmap-and-milestones`.
Identity, history statuses, dependency satisfaction, membership and user-owned lifecycle authority stay unchanged.
`ARCH-05-2-components` owns existing feature layers and test tiers; no new package or dependency is needed.

## 2. Architecture Overview & Impact

Document models expose a small pure milestone path/status predicate. Document convention validation and proposal
membership reuse it. The index continues to accept invalid locations so governance can report them.
Viewer backend header discovery and frontend dashboard/roadmap loaders include only the reserved archive directory.
Post-load dashboard classification recognizes both canonical locations and keeps terminal items out of open counts.

## 3. Component & Interface Design

Use `milestone_path_valid(path, status)` in the document model with the existing lifecycle statuses.
The canonical filename/ID check stays at callers. The predicate accepts root planned/active and archive done/dropped
only; no general resolver, file IO or automatic lifecycle mutation.
Viewer path matching accepts root or one `_archive` segment; readiness resolves the full loaded set before filtering.
Existing dashboardList, tree/blob, proposal CLI and notice contracts are unchanged.

## 4. Storage & State Management

Done/dropped use `docs/roadmap/_archive/MS-<slug>.md`; live milestones use the root.
Validate reader fixtures before moving the four manifest files. Compare SHA256 and byte length before and after.
Current guidance makes close/drop/reopen atomic status/assertion/disposition plus move operations under existing
user authority; unchanged terminal operations write nothing. Preserve historical aliases and bytes.

## 5. Error Handling & Edge Cases

Report invalid status/location pairs, other nesting, namespace roadmaps and identity collisions.
Keep safe format fixes, never move or change lifecycle status automatically. Invalid archived live documents stay indexed.
Proposal membership refuses invalid placement before writes. Missing archive directories are ordinary empty sources.

## 6. Verification & Test Plan

AC-01/02: document rule and index/CLI integration fixtures with both terminal states, explicit historical targeting,
aliases, references, invalid live archive and collision. AC-03: proposal authoring tests and unchanged inactive notice.
AC-04/05: backend selective-header tests; frontend extraction, optimized/generic loaders, readiness, history and detail tests.
AC-06: installed guidance scenarios plus actual synthetic Git file transitions with labelled simulated authority.
AC-07: manifest comparison and four byte-preserving moves. AC-08: `just test-affected`, package lint/check, `just smoke`,
`just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`, sync and cumulative rules.
Reuse unchanged verified results; run affected checks after any Host base merge. Independent code and reconcile reviewers
use pinned committed scope and before/after snapshots.
