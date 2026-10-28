---
id: SPEC-milestone-archive
title: Archive done and dropped milestones within the roadmap
summary: "Archives done and dropped global milestones in one flat roadmap directory while preserving identity, history visibility, dependencies and lifecycle authority across document tools and the viewer."
status: in-progress
created: 2026-10-28
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-milestone-archive] Archive done and dropped milestones within the roadmap

## 1. Problem Statement & Motivation

Handed off from proposal PROP-milestone-archive on 2026-10-28.
- **Preserved Materials**: `docs/materials/2026-10/20261028-milestone-archive`
- Target Docs Blueprint: `PROP-milestone-archive-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

`CAP-DOCS-document-model` and `ADR-roadmap-and-milestones` retain terminal milestone history. The root roadmap
contains four `done` files and two `planned` files at base `b17db06f`; there are no `dropped` files. History filters
already hide done/dropped documents, but filesystem browsing still mixes them with current themes.

One reserved flat archive can separate storage without another status or index. The document index already reads
nested Markdown and derives history from status; path validators, proposal membership and viewer discovery still
assume root-only milestone files. `docs/materials/2026-10/20261028-milestone-archive/reader-inventory.md` records the source evidence and a bounded probe.

Planning uses the current docs/spec/viewer ownership. No structural prerequisite or active CLI-refactor dependency
was found in these seams. Development rechecks its base and repairs renamed reader locations within this scope;
a later change that breaks this agreement returns to the Host rather than inventing a dependency or duplicate API.

## 2. User Stories

- **US-1**: As a developer/agent, I want terminal milestones outside the live roadmap directory while retaining lookup, membership and prerequisite history.
- **US-2**: As a viewer user, I want archived history and details available through the existing dashboard and roadmap controls.

## 3. Non-Goals

**Scope Excluded**: new commands/statuses/registries, automatic moves or lifecycle decisions, partitioned archives,
CLI restructuring, viewer redesign, compatibility shims, archiving other document kinds and retroactive completion evidence.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Layout

- **Given** root live and archived terminal milestones.
- **When** convention and format checks run.
- **Then** supported status/location pairs pass; archived live, root terminal, other nesting and namespaced milestones report invalid placement when targeted. Safe metadata fixes neither move files nor change status.

### [AC-02] History and identity

- **Given** archived done/dropped documents with aliases and incoming references.
- **When** resolve, refs, list and search run.
- **Then** IDs and aliases resolve, default/explicit-status/history visibility follows status, and invalid archived active documents remain indexed and reportable.

### [AC-03] Proposal membership

- **Given** an archived done/dropped milestone or its alias.
- **When** proposal creation selects it.
- **Then** membership stores the canonical ID and emits SPEC_PROPOSAL_MILESTONE_INACTIVE. Invalid location or identity fails before writes.

### [AC-04] Prerequisites

- **Given** a live milestone depending on archived done and dropped milestones and an unknown edge.
- **When** readiness is evaluated with history off and on.
- **Then** both terminal prerequisites are known satisfied edges; the unknown edge remains unknown. Resolve all milestones before display filtering.

### [AC-05] Viewer readers

- **Given** optimized dashboardList and generic tree/blob sources containing archived milestones.
- **When** dashboard and roadmap load and an archived item opens.
- **Then** headers, counts, ordering, pagination, cache, history and detail/deep links retain their existing contracts. Archived done/dropped increase totalCount and never openCount; discovery reads only the reserved archive in addition to current directories.

### [AC-06] Lifecycle transitions

- **Given** a concrete user-authorized close, drop, reopen or historical merge.
- **When** the agent follows installed guidance.
- **Then** status, applicable assertions/disposition and movement are one commit. Drop creates no completion assertion; unchanged archived close/drop are no-ops; reopen returns active to the root and resets both assertions; merged identities stay aliases.

### [AC-07] Approved relocation batch

- **Given** the four exact files in the retained manifest and passing reader checks.
- **When** the approved batch moves to the flat archive.
- **Then** only paths change and bytes match the reviewed inputs. Changed candidates or destination collisions stop the move. No historical assertion is invented and completed specs remain in place.

### [AC-08] Delivered verification

- **Given** the complete implementation.
- **When** package lint/types, affected Python tests, consumer smoke, viewer lint/check/test/build, sync and cumulative governance run.
- **Then** all checks pass, including done/dropped/collision/reopen and both viewer loading paths, and the committed viewer page is rebuilt.

## 5. Approved Design and Assumptions

The Host records user approval of the reviewed four-file batch and Development handoff.
The current base retains the Planning reader owners; no structural prerequisite was found.
No screen arrangement changes: existing dashboard, roadmap, history and detail interfaces remain.
Codex delegation is emulated: absolute worktree paths, scoped commits and before/after review snapshots substitute for native isolation.

### 3. Proposed Design & Impact

#### Storage and validation

1. Global `planned`/`active` milestones live at `docs/roadmap/MS-<slug>.md`; global `done`/`dropped` milestones live
   at `docs/roadmap/_archive/MS-<slug>.md`. Keep the word-led kebab-case slug and matching ID/H1. No other nesting,
   year/status partition or namespace roadmap is supported.
2. Preserve the filename, ID, aliases, frontmatter and body on an existing-history move. Moving location alone
   creates no alias, status, `archived_at`, copied index or member registry. There is exactly one file per identity.
3. Extend the existing location check to validate status/location pairs. Invalid pairs, duplicate identities and
   destination collisions remain visible errors; do not silently overwrite, choose a duplicate or move a file.
   Keep invalid archived active/planned documents indexed so their location error can be reported.
4. Preserve existing safe metadata-format fixes. Placement enforcement neither changes an existing lifecycle status
   nor moves files automatically. Default historical targeting remains unchanged; explicit archived-file checks run.
5. Prefer a small pure accepted-path helper in the existing document layout owner if needed by both Python
   validators. Do not make indexing reject invalid documents or add a general path abstraction/resolver.

#### Lookup and prerequisites

6. Retain status-derived default/history visibility, `resolve`, alias resolution and incoming/outgoing `refs`.
   The document scanner and history model do not need a second archive registry. Index both supported locations.
7. `proposal new --milestone` validates the supported canonical global path and status/location pair, writes the canonical ID and retains
   `SPEC_PROPOSAL_MILESTONE_INACTIVE` for both done and dropped. It neither reactivates the milestone nor blocks
   otherwise valid membership simply because the file is archived.
8. Existing milestone readiness treats both `done` and `dropped` prerequisites as satisfied. Resolve the complete
   milestone set before applying history display filters. Hiding a terminal document must not turn a known edge into
   an unknown one. Preserve MS-only edges and direct PROP-only membership; SPECs acquire no milestone field.

#### Viewer and lifecycle guidance

9. Include archive headers in the existing backend dashboard list, frontend dashboard discovery, post-load
   `extractDashboardData` classification/count aggregation and roadmap loader. Cover both optimized `dashboardList` sources and generic tree/blob source fallback. Do not read the whole repository
   when the milestone section opens; add only the reserved archive directory. Keep current paging, caching, sorting,
   history toggle, detail and deep-link behavior. A reopened active file returns to live browsing.
10. Generic viewer nested tree/blob reads already support `_archive`; verify archived detail navigation and both
    loader paths. No archive screen or redesigned roadmap is introduced. Rebuild the committed viewer page after
    frontend changes using the repository's viewer checks.
11. Backlog close writes done, both confirmed assertions and the archive move in one authorized commit. Drop writes
    the agreed member/dependency disposition, dropped and the move together, without inventing completion assertions.
    Reopen moves to the root, sets active and resets both assertions in one authorized commit. Keep the existing
    user-owned decision boundaries; no extra archive-only approval round for those exact transition effects.
12. Repeating an unchanged archived close/drop writes nothing. Milestone merging still works for either location:
    retain merged IDs as aliases, preserve explicit scope disposition and never infer delivery from removal.

#### Existing-history relocation and authority

The captured candidate set is:

| ID | Source | Destination |
| --- | --- | --- |
| MS-backlog-subagent-roles | `docs/roadmap/MS-backlog-subagent-roles.md` | `docs/roadmap/_archive/MS-backlog-subagent-roles.md` |
| MS-idea-incubation | `docs/roadmap/MS-idea-incubation.md` | `docs/roadmap/_archive/MS-idea-incubation.md` |
| MS-maintenance-operations | `docs/roadmap/MS-maintenance-operations.md` | `docs/roadmap/_archive/MS-maintenance-operations.md` |
| MS-ux-documentation | `docs/roadmap/MS-ux-documentation.md` | `docs/roadmap/_archive/MS-ux-documentation.md` |

All four are done. The manifest records their current bytes and SHA256; synthetic fixtures exercise dropped history.
No source/destination collision exists in this snapshot. There are no live Markdown file links to these exact paths;
one older feedback fence records an observed source path and stays historical evidence rather than a link repair.
References by ID need no rewrite and filenames/IDs stay unchanged.

After reader support is verified, the Host obtains or reuses explicit authority for that exact batch and performs
content-preserving moves in Development. Compare bytes before/after. Preserve absent old assertions rather than
retrofitting evidence, even though the current four all have confirmed assertions. Re-read the candidate set before
applying it. New terminal files, changed source contents or destination conflicts require a refreshed concrete
candidate and authority for changed effects; do not silently broaden this batch. Plain file checks suffice; no new
runtime manifest protocol, hash lock or migration reader is introduced.

## 6. Verification Baseline

The retained reader inventory records a bounded Planning probe: archived done/dropped are indexed and readable
by generic detail reads but rejected as proposal membership; path rules and viewer discovery are root-only.
Development verifies the changed reader outcomes against those inputs without checking out the base.
