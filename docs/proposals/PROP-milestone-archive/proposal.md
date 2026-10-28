---
id: PROP-milestone-archive
title: Archive done and dropped milestones within the roadmap
summary: "Archives done and dropped global milestones in one flat roadmap directory while preserving identity, history visibility, dependencies and lifecycle authority across document tools and the viewer."
status: reviewing
created_at: 2026-10-28
target_area: capabilities/documents/
priority: low
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-docs/
    - packages/devkit-spec/
    - packages/devkit-viewer/
    - docs/capabilities/documents/
    - docs/capabilities/delivery/
    - docs/capabilities/governance/
    - docs/capabilities/harness/
    - docs/capabilities/viewer/
    - docs/usecases/documents/
    - docs/usecases/delivery/
    - docs/decisions/
    - docs/roadmap/
  excludes:
    - packages/devkit-cli/
    - packages/devkit-dist/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-milestone-archive] Archive done and dropped milestones within the roadmap

## 1. Background & Hypothesis

`CAP-DOCS-document-model` and `ADR-roadmap-and-milestones` retain terminal milestone history. The root roadmap
contains four `done` files and two `planned` files at base `b17db06f`; there are no `dropped` files. History filters
already hide done/dropped documents, but filesystem browsing still mixes them with current themes.

One reserved flat archive can separate storage without another status or index. The document index already reads
nested Markdown and derives history from status; path validators, proposal membership and viewer discovery still
assume root-only milestone files. `materials/reader-inventory.md` records the source evidence and a bounded probe.

Planning uses the current docs/spec/viewer ownership. No structural prerequisite or active CLI-refactor dependency
was found in these seams. Development rechecks its base and repairs renamed reader locations within this scope;
a later change that breaks this agreement returns to the Host rather than inventing a dependency or duplicate API.

## 2. Technical Spike Questions

- **Q1 — terminal scope, settled**: include both `done` and `dropped`. Keep their statuses distinct; archiving does
  not certify completion. This was resolved before this Planning turn.
- **Q2 — boundary**: recommend extending the global milestone path convention and its existing document-rule
  validation. Keep lifecycle authority in Backlog guidance; no new archive command, watcher or move autofix.
- **Q3 — reader coverage**: index/history/aliases already work by identity and status. Extend proposal membership,
  viewer dashboard header discovery, dashboard filtering and roadmap loading to the reserved archive location.
- **Q4 — retained history**: recommend relocating the exact four unchanged files in
  `materials/relocation-candidates.json` after readers and checks pass. That manifest is an approval candidate,
  not relocation authority; the Host presents it with the proposed Development effects.

`PADR-archive-terminal-milestones-in-roadmap` compares keeping the root, one archive and partitioned alternatives.

## 3. Proposed Design & Impact

### Storage and validation

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

### Lookup and prerequisites

6. Retain status-derived default/history visibility, `resolve`, alias resolution and incoming/outgoing `refs`.
   The document scanner and history model do not need a second archive registry. Index both supported locations.
7. `proposal new --milestone` validates either supported canonical global path, writes the canonical ID and retains
   `SPEC_PROPOSAL_MILESTONE_INACTIVE` for both done and dropped. It neither reactivates the milestone nor blocks
   otherwise valid membership simply because the file is archived.
8. Existing milestone readiness treats both `done` and `dropped` prerequisites as satisfied. Resolve the complete
   milestone set before applying history display filters. Hiding a terminal document must not turn a known edge into
   an unknown one. Preserve MS-only edges and direct PROP-only membership; SPECs acquire no milestone field.

### Viewer and lifecycle guidance

9. Include archive headers in the existing backend dashboard list, frontend dashboard discovery and roadmap loader.
   Cover both optimized `dashboardList` sources and generic tree/blob source fallback. Do not read the whole repository
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

### Existing-history relocation and authority

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

### Validation scenarios

- **AC-01 — layout**: Given root live and archived terminal milestones, when convention/format checks run, then
  supported pairs pass with the same ID/H1; archived live, root terminal, arbitrary nested and namespaced locations
  report the invalid placement when targeted. A fix never changes status or moves a file to resolve placement.
- **AC-02 — history and identity**: Given archived done/dropped documents with aliases and incoming refs, when
  resolve/refs/list/search run, then IDs/aliases remain resolvable and default, explicit-status and history visibility
  match the existing status contract. Invalid active archived input remains indexed and is reported by governance.
- **AC-03 — proposal membership**: Given either archived terminal state or alias, when proposal creation runs, then
  canonical membership and the inactive notice are preserved. Invalid location/identity is refused before writes.
- **AC-04 — prerequisites**: Given a live milestone depending independently on archived done and archived dropped,
  when next-work guidance and viewer readiness are evaluated with history off/on, then both are known satisfied
  edges; an unknown edge remains unknown. Resolve before display filtering and keep current member semantics.
- **AC-05 — viewer readers**: Given optimized and generic viewer sources, when dashboard/roadmap history loads and
  an archived item opens, then correct headers, counts, sorting, paging, detail/deep links and existing cache behavior
  include history without scanning unrelated sections. After authorized reopen, the active item is live at the root.
- **AC-06 — transitions**: Given an authorized close/drop/reopen candidate, when the agent follows installed guidance,
  then the status, applicable assertions/disposition and move appear in one commit. Drop never certifies completion;
  repeat unchanged terminal operations are no-ops. Existing milestone merge/alias behavior works across locations.
- **AC-07 — captured batch**: Given approval for the exact recorded relocation set and passing readers, when the four
  files move, then only paths change and bytes match the reviewed source. Duplicate destinations or changed candidates
  stop for resolution; completed specs remain in place. No historical assertion is invented.
- **AC-08 — delivered checks**: Given the complete implementation, when package lint/types, affected Python tests,
  consumer smoke, viewer frontend lint/check/test/build, sync and cumulative governance run, then they pass.
  Include real done/dropped/collision/reopen fixtures and archived detail/loading tests; rebuild the committed page.

### Verification boundary and exclusions

Development selects exact test paths from the inventory. Reuse document lookup/history/namespace tests, milestone
convention and proposal roadmap tests, viewer backend selective-read tests and frontend dashboard/roadmap/deep-link
coverage. Semantic close/drop/reopen exercises record actual file states and clearly labelled simulated decisions;
a token assertion alone does not establish the transition. `just test-affected` retains its full fallback. Run the
command named by its `[FRONTEND_CHECK: ...]` result and the required viewer build, rather than claiming pytest covers TS.

- **Scope Excluded**: CLI restructuring, a new archive command/API, viewer redesign, lifecycle authority or dependency
  meaning changes, automatic transitions/moves, migration shims, a persistent manifest/index/lineage graph, archiving
  other document kinds, partitioned archives and retroactive completion evidence.
- **Scope Excluded**: actual archive moves or milestone status changes during Planning.

## 4. Lifecycle & Retirement Criteria

Keep one feature spec: storage convention and all required readers jointly deliver the archive path. Planning
found no independent structural prerequisite and retains M/medium hints. Host/user acceptance approves the
proposed direction; handoff starts Development only under its existing policy. Any exact relocation authority must
name the reviewed effects; no worker accepts or hands off. Completion requires AC-01 through AC-08 and current
Living Spec/guidance reflection. The milestone theme decisions and historical records remain otherwise unchanged.
