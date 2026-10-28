---
id: PROP-milestone-archive
title: Archive done and dropped milestones within the roadmap
summary: "Separate done and dropped milestone files into docs/roadmap/_archive while preserving milestone identity, historical lookup and dependency resolution. Define close, drop, reopen and existing-history relocation without coupling the change to CLI restructuring."
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

`CAP-DOCS-document-model` and `ADR-roadmap-and-milestones` classify `done` and `dropped` milestones as history.
Default document browsing and search hide them, but the files remain beside current milestones in `docs/roadmap/`.
Separating `done` and `dropped` files would make filesystem browsing reflect the working roadmap without discarding
history.

The hypothesis is that one reserved directory, `docs/roadmap/_archive/`, is enough. Milestone status remains the
lifecycle fact; the directory is its storage convention. Archiving adds no status, document kind or membership
registry. This proposal concerns one storage and lifecycle contract, including the readers required to preserve it.

This is a queued Backlog draft. Implementation is deferred while CLI refactoring is in progress. Formal Planning,
direction acceptance and Development have not started. Planning should inspect the then-current package ownership
and CLI contracts rather than freezing implementation details from this draft.

## 2. Technical Spike Questions

- **Q1 — terminal scope (resolved)**: The archive contains both `done` and `dropped`, following the user's scope
  decision. Their statuses remain distinct; archiving a dropped milestone does not certify completion.
- **Q2 — enforcement**: Which existing document-rule boundary should validate status and location, including
  explicitly targeted historical files, without introducing automatic lifecycle writes?
- **Q3 — reader coverage**: After the CLI refactoring, which index, proposal-authoring, governance and viewer readers
  still assume a direct child of `docs/roadmap/`? Verify the complete reader set before selecting implementation tasks.
- **Q4 — existing history**: Confirm a reviewed, one-time relocation of existing `done` and `dropped` files after
  reader support lands. Retain their content and lifecycle evidence rather than re-running completion review.

## 3. Proposed Design & Impact

### 3.1 Recommended storage convention

```text
docs/roadmap/
  MS-current-theme.md          # planned or active
  _archive/
    MS-delivered-theme.md      # done
    MS-abandoned-theme.md      # dropped
```

- Use `_archive`, with no year/status subdirectories. Add partitioning only after a concrete browsing need appears.
- Store `planned` and `active` milestones at the roadmap root, and `done` and `dropped` milestones in `_archive/`.
- Preserve the filename, `MS-<slug>` ID, aliases, creation date, dependencies, summary and completion review body.
  A directory move does not rename the milestone or need a new alias.
- Keep exactly one file per milestone identity across the roadmap and archive. A destination collision requires
  explicit resolution; never overwrite or silently select one copy.
- Derive historical visibility from status as before. Directory placement alone must not make an active milestone
  historical or satisfy a prerequisite. Invalid status/location pairs should be reported rather than silently hidden.
- Add no `archived` status, `archived_at`, copied archive index or separate member list.

### 3.2 Close, drop, reopen and existing files

- Close uses the existing user-owned completion decision in `CAP-HARN-agent-guidance`: recheck the candidate and
  confirm both assertions. Write `status: done`, both confirmed assertions and the move into `_archive/` in the same
  Backlog commit. Archiving is part of that authorized close, with no additional approval round.
- Drop uses the existing user-owned decision after reviewing unsettled members and dependent milestones and
  preparing member reassignment, clearing or rejection. Record `status: dropped`, the agreed disposition and the
  archive move in the same Backlog commit. Do not mark completion assertions confirmed merely because of a drop.
- Reopen requires the existing user decision. Move the file to the roadmap root, set `status: active` and reset both
  assertions to pending in the same Backlog commit. The move alone grants no authority to reopen or extend scope.
- Existing `done` and `dropped` files move only after all required readers support the archive. Prepare an exact file
  set for the user's relocation decision. Preserve their contents, including absent historical completion assertions;
  relocation does not certify delivery or retrofit closure evidence. Leave completed spec bundles in place.
- Retrying an unchanged archived close or drop writes nothing. Preserve the existing milestone merge procedure in
  `ADR-milestone-merging`, including archived sources and aliases.
- Prefer agent guidance and ordinary file moves for close/drop/reopen. No new archive CLI command, background watcher,
  automatic status transition or general rule autofix is proposed.

### 3.3 Lookup, references and viewer

- Index both supported locations. Preserve `resolve`, incoming/outgoing `refs`, alias resolution and the existing
  `--history` list/search behavior under `CAP-DOCS-document-lookup` and `CAP-DOCS-document-search`.
- A live milestone depending on an archived `done` or `dropped` milestone remains ready under the existing dependency
  semantics. Resolve the full milestone set before applying display filters, so hiding history never turns a satisfied
  dependency into an unknown one.
- `proposal new --milestone` accepts an archived milestone ID or alias as an existing global milestone. Preserve
  canonicalization and `SPEC_PROPOSAL_MILESTONE_INACTIVE`; archiving does not reactivate it or forbid membership.
- Preserve viewer roadmap/dashboard history access and milestone detail links. Update both backend candidate
  discovery and frontend path recognition/loading where needed. Keep the existing UI and data-source contracts;
  this work does not add an archive screen or viewer redesign.
- Extend the allowed milestone paths and corresponding rule guidance. Keep historical rule targeting semantics;
  explicitly targeted archived files remain checkable.

### 3.4 Known implementation touchpoints to recheck in Planning

These are inspection evidence, not a prescribed implementation layout:

- `packages/devkit-docs/src/devkit_docs/features/governance/usecases/id_convention.py` requires a direct roadmap child.
- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py` validates that exact location.
- `packages/devkit-viewer/src/devkit_viewer/features/browse/repositories/worktree.py` discovers direct milestone files
  for dashboard headers.
- `packages/devkit-viewer/frontend/src/lib/api/roadmap.ts` matches direct paths and loads only the roadmap root.
- Reconcile `CAP-DOCS-document-model`, lookup/search, proposal incubation, governance, agent guidance and viewer
  contracts. Record the changed storage decision in a PADR during Planning and promote it through the normal handoff.
  Update the owning bundle sources and seed guidance, then regenerate managed assets through synchronization.

### 3.5 Expected acceptance checks

| Check | Given / When / Then |
| --- | --- |
| AC-1 | Given a valid user-confirmed close candidate, when close is recorded, then status, both assertions and archive relocation appear together with the same milestone ID. |
| AC-2 | Given an archived `done` or `dropped` milestone, when lookup/search and reference queries run, then default/history visibility and ID/alias resolution retain their existing semantics. |
| AC-3 | Given a live milestone depending on archived `done` or `dropped` history, when CLI references and viewer readiness are evaluated, then the prerequisite is resolved and satisfied with history display off or on. |
| AC-4 | Given an authorized reopen, when it is recorded, then the file returns to the root as `active` with both assertions pending and its ID unchanged. |
| AC-5 | Given existing `done` and `dropped` files, when their reviewed relocation is applied, then only paths change; repeated relocation does not create duplicate files or overwrite collisions. |
| AC-6 | Given an archived milestone ID or alias, when a proposal is created with it, then the canonical membership and inactive notice are preserved. |
| AC-7 | Given archived history or invalid placement, when governance explicitly targets the files, then supported paths pass and duplicate identities or invalid status/location pairs are reported; no lifecycle state is automatically rewritten. |
| AC-8 | Given a user-authorized drop with member disposition prepared, when it is recorded, then disposition, `status: dropped` and archive relocation appear together with the same ID, without certifying completion. |

### 3.6 Non-goals

Scope excluded: implementing or extending the ongoing CLI refactoring; a new archive command; a viewer redesign;
archiving proposals, specs, ADRs or feedback; changing completion authority or membership; recomputing delivery
lineage; retention/deletion policies; nested archive partitions; and retroactively changing completion assertions.

## 4. Lifecycle & Retirement Criteria

Keep this proposal `draft` until the user picks it up. Resume Planning after the CLI work permits stable reader and
package boundaries, resolving Q2–Q4 against the current repository before acceptance. Review the size and effort
hints at pickup; this draft estimates one feature spec rather than separate CLI and viewer deliverables.

Acceptance decides the storage and lifecycle direction. Development starts only through the normal authorized
handoff. This draft authorizes no milestone status changes or file relocation. On rejection, use the existing
proposal retirement procedure and retain the user's reason.
