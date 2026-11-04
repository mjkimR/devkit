---
id: SPEC-namespace-roadmap
title: Per-namespace milestones under the namespace docs root
summary: Lets a registered namespace keep its own MS milestones under docs/packages/<name>/roadmap/ with the global lifecycle and selection, so packages on their own cadence stop crowding the global roadmap.
status: planned
created: 2026-11-04
namespace: global
related_capabilities: [CAP-DOCS-namespaces, CAP-GOV-spec-rules, CAP-DLV-proposal-planning]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-namespace-roadmap] Per-namespace milestones under the namespace docs root

## 1. Problem Statement & Motivation

`CAP-DOCS-namespaces` mirrors `docs/` under `docs/packages/<name>/` for capabilities, use cases, UX and architecture
documents, but milestones are global only. `ADR-roadmap-and-milestones-ledger` deferred per-namespace roadmaps
"until a repository needs them", and the code enforces the deferral: `milestone_path_valid` accepts only
`docs/roadmap/(_archive/)?MS-<slug>.md`; `RULE-id-convention` walks every namespace `roadmap/` directory and reports
each file there as misplaced; the `MILESTONE` kind row is `FormatScope.GLOBAL`, so `RULE-spec-format` scans the
global root only; `devkit spec proposal new --milestone` refuses a milestone outside the global root; and the
Backlog references state that milestones are global.

A monorepo whose packages are independent products needs them: several games sharing one platform, each with its own
release cadence and its own docs under `docs/packages/<game>/`. Their milestones either crowd one global roadmap with
unrelated themes or stay outside the document system.

The namespace layer already supplies what per-namespace milestones need: membership of a document under
`docs/packages/<name>/` is `<name>` (`CAP-DOCS-namespaces` 3.2), `devkit docs list` already selects namespaces, and
`living_path` already maps `docs/packages/<name>/roadmap/X` to `docs/roadmap/X` for the rules. This spec allows the
placement and makes the lifecycle checks namespace-aware. The decision is `ADR-namespace-milestone-roots`, promoted at
handoff; the Planning spike inventory is retained at `docs/materials/2026-11/20261104-namespace-roadmap/global-roadmap-root-inventory.md`.
This is the first direct member of `MS-monorepo-namespace-support`.

## 2. User Stories

- **US-1**: As the owner of a monorepo package registered as a namespace, I want to keep that package's milestones at
  `docs/packages/<name>/roadmap/` with the same lifecycle placement as the global roadmap, so that the global roadmap
  holds only cross-package themes and the rules accept my files.
- **US-2**: As an AI coding agent creating a proposal for a package, I want `--milestone` to accept a milestone at the
  namespace roadmap root, so that a package proposal declares membership of a package milestone.
- **US-3**: As an AI coding agent working inside a package directory, I want `devkit docs list milestone` to show that
  package's milestones beside the global ones, and `--all-namespaces` to show every milestone, so that selection
  follows `CAP-DOCS-namespaces` 3.3 for milestones as for the other kinds.
- **US-4**: As an AI coding agent following the Backlog and milestone guidance, I want the references, template and
  rule guides to name the milestone's own roadmap root, so that a lifecycle move of a namespace milestone stays inside
  its root.

## 3. Non-Goals

1. **Scope Excluded**: namespaced IDs or per-package ID spaces; IDs, aliases and the `MS-` prefix stay repository-wide.
2. **Scope Excluded**: per-namespace goals as ID-bearing documents, or a rule that checks a milestone's goal citation;
   the citation stays a review-only recommendation.
3. **Scope Excluded**: a namespace directory for proposals; the `PROPOSAL` kind row stays `FormatScope.GLOBAL`.
4. **Scope Excluded**: a namespace copy of `_archive/` semantics beyond the path, or any change to `milestone_path_valid`'s
   global regex; callers map a path through `living_path` before validating it.
5. **Scope Excluded**: the local viewer (`packages/devkit-viewer/`, `CAP-VIEW-repository-viewer`), on the user's
   decision in Planning; the follow-up is `FB-viewer-namespace-roadmap-roots`.
6. **Scope Excluded**: a same-namespace constraint between a proposal and the milestone it names; a proposal of any
   namespace may name a milestone at the global root or at any namespace root.
7. **Scope Excluded**: external tracker synchronization of namespace roadmaps.

## 4. Acceptance Criteria & Behavioral Contracts

The rule behavior is checked by the rule tests under `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/`,
the command behavior by the integration tests of `devkit-docs` and `devkit-spec`, and the guidance wording by the
`spec` bundle's guidance test. "Registered" means listed in `[[tool.docs.namespaces]]` of `.devkit/config.toml`.

### [AC-01] A registered namespace milestone at each lifecycle location passes `RULE-id-convention`
- **Given** a workspace registering namespace `api` and milestone files `docs/packages/api/roadmap/MS-example.md`
  with `status: planned` or `active`, and `docs/packages/api/roadmap/_archive/MS-example.md` with `status: done` or
  `dropped`, each with `id` equal to its file stem
- **When** `RULE-id-convention` checks the file
- **Then** it reports no violation, the file is not moved and its text is unchanged; the global pairs keep their
  current results.

### [AC-02] Misplaced namespace milestones are reported with both roots in the remediation
- **Given** the same workspace
- **When** `RULE-id-convention` checks `docs/packages/api/roadmap/MS-example.md` with `status: done` or `dropped`,
  `docs/packages/api/roadmap/_archive/MS-example.md` with `status: planned` or `active`,
  `docs/packages/api/roadmap/2026/MS-example.md`, or `docs/packages/web/roadmap/MS-example.md` where `web` is not
  registered
- **Then** each is reported as an invalid partition path, is not fixed, and the message and remediation name both
  `docs/roadmap/` and `docs/packages/<name>/roadmap/` with `_archive/` for done/dropped; a milestone document
  found outside every roadmap directory is reported with the same two-root remediation.

### [AC-03] `RULE-spec-format` checks a namespace milestone as it checks a global one
- **Given** a workspace registering namespace `api`
- **When** `RULE-spec-format` runs with no explicit targets, and `docs/packages/api/roadmap/MS-a.md` has
  `status: draft` and no `created_at`
- **Then** the milestone status is reported as `milestone status must be planned | active | done | dropped` (not
  fixable) and the missing `created_at` is reported and fixed with `--fix`; `docs/packages/api/roadmap/_archive/MS-done.md`
  with `status: done` is history, checked only as an explicit target, and keeps its status and placement after a fix.
  An unregistered `docs/packages/web/roadmap/MS-b.md` is not scanned by default.

### [AC-04] `devkit spec proposal new --milestone` accepts a milestone at either root
- **Given** a workspace registering namespace `api` with `docs/packages/api/roadmap/MS-api-launch.md` (`status: active`)
  and `docs/roadmap/MS-foundation.md` (`status: planned`)
- **When** `devkit spec proposal new member --milestone` MS-api-launch runs from the repository root or from the
  package's source directory, or with `--milestone` MS-foundation
- **Then** it exits `0` and writes `milestone: MS-api-launch` (or MS-foundation) into the proposal's frontmatter;
  the milestone file is unchanged. A done or dropped namespace milestone in its `_archive/` still returns
  `SPEC_PROPOSAL_MILESTONE_INACTIVE` without blocking creation.

### [AC-05] An invalid namespace placement is refused before any write
- **Given** the same workspace with `docs/packages/api/roadmap/MS-api-launch.md` whose `status` is `done`, or the
  file under `docs/packages/api/roadmap/_archive/` with `status: active`, or at `docs/packages/web/roadmap/` where
  `web` is not registered
- **When** `devkit spec proposal new member --milestone` MS-api-launch runs
- **Then** it fails with `ARGUMENT_INVALID` (exit `2`), the message names a milestone at the global or a namespace
  roadmap root, the fix names `devkit docs list milestone --all-namespaces`, and `docs/proposals/` is not created.

### [AC-06] `devkit docs list milestone` selects namespace milestones by the current directory
- **Given** a workspace registering namespaces `api` (`services/api`) and `web` (`apps/web`) with milestones
  `docs/packages/api/roadmap/MS-api-launch.md`, `docs/packages/web/roadmap/MS-web-launch.md` and
  `docs/roadmap/MS-foundation.md`
- **When** `devkit docs list milestone --format json` runs from `services/api`
- **Then** the documents are MS-api-launch and MS-foundation, each with its `namespace`; with `--all-namespaces`
  the documents are all three; from the repository root all three are listed.

### [AC-07] A monorepo passes `devkit rules check` with a cross-namespace milestone edge
- **Given** a workspace registering namespace `api` with a valid namespace milestone at each lifecycle location
  (planned at the root, done in `_archive/`, each with `id`, `title`, `status`, `created_at` and an English `summary`),
  and a global milestone whose `depends_on` names the namespace milestone
- **When** `RULE-id-convention`, `RULE-spec-format` and `RULE-document-reference` check the workspace
- **Then** none reports a finding for the milestones.

### [AC-08] The guidance names the milestone's roadmap root
- **Given** the shipped `spec` skill references `backlog.md`, `roadmap-catalog.md` and `milestone-completion.md`, the
  `docs` bundle's milestone template, the `id_convention` and `spec_format` rule guides and the seeded
  `ARCH-01-introduction-and-goals`
- **When** an agent reads them
- **Then** the Milestones section of `backlog.md` states both roots (`docs/roadmap/MS-<slug>.md` and
  `docs/packages/<name>/roadmap/MS-<slug>.md`, `_archive/` for done/dropped) and that a lifecycle move stays inside
  the milestone's roadmap root; `roadmap-catalog.md` no longer calls milestones global documents;
  `milestone-completion.md` step 3 moves the file into the `_archive/` of the milestone's roadmap root; the template's
  placement sentence names the roadmap root the milestone lives under; the rule guides' milestone row and scope
  sentence name the namespace roadmap root; the guidance test asserts the reference wording, and none of the files
  states that milestones are global only.

## 5. Source feedback

None from Planning. The feedback carried in this bundle is deferred work, not input: `FB-viewer-namespace-roadmap-roots`
(the viewer's roadmap roots, Non-Goal 5) and `FB-padr-default-slug-from-long-title` (Planning guidance, unrelated to
this change).

## 6. Assumptions

- The remediation strings of `RULE-id-convention` keep their current shape (one sentence naming the valid locations,
  then the fix command); only the location clause changes.
- `devkit docs list milestone` needs no code change: the index already discovers `docs/packages/<name>/roadmap/` and
  selection is namespace-generic; AC-06 pins that behavior.
- A cross-namespace `depends_on` edge needs no code change: `RULE-document-reference` resolves repository-wide IDs;
  AC-07 pins that behavior.
- The "Superseded in part by" pointer the handoff wrote into `ADR-roadmap-and-milestones-ledger` is completed at
  `living-spec-draft` to name the two replaced clauses, as `ADR-namespace-milestone-roots` lists them.
