---
id: SPEC-generated-conflicts-follow-ups
title: Follow-ups of the generated conflict settling
summary: Run merge-tree on the shared Git runner through accepted exit statuses, and close four guidance and test-selection gaps the generated conflict and bundle citation work left as feedback.
status: in-progress
created: 2026-10-30
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-generated-conflicts-follow-ups] Follow-ups of the generated conflict settling

## 1. Problem Statement & Motivation

`SPEC-generated-conflicts-in-prepared-merge` and `SPEC-shipped-bundle-citations-and-doc-fixes` left five follow-ups as
open feedback:

- The shared Git runner `devkit_core.core.git.run_git` raises `GitError` on every nonzero exit and drops Git's standard
  output. `git merge-tree --write-tree` answers a conflict with exit `1` and lists the conflicted entries on standard
  output, so `devkit_agt.features.worktree.services.merging` runs that one command through its own `subprocess` call
  with a copy of the runner's environment and timeout handling. Two copies of Git's run rules can drift.
- `docs/development/workflow.md`, `docs/development/ci-cd.md` and the root `AGENTS.md` describe the batch completion
  of a local-orchestrated run as one `just test-affected --base <batch start>` run, while the `spec-orchestrate` skill
  first runs `devkit generated check` and regenerates and commits stale artifacts (`ADR-generated-conflicts-in-prepared-merge`).
- A Development worker asked to decide a cross-feature design choice could not build any of the options, because each
  needed a new feature edge in the architecture declaration and the payload's write scope excluded it.
- `tools/devkit-dev/tests/integration/test_bundle_citations.py` reads the document IDs of `docs/` and `specs/`, but
  `scripts/affected_tests.py` selects it only for shipped bundle changes, so a new document whose ID a bundle already
  cites is caught only by the nightly full CI.
- The root `AGENTS.md` sends an agent to the context of the bundle whose assets it edits, but the writing and
  self-containment rules for every bundle's agent assets are in the `authoring` bundle's `agent-asset-writing`
  instruction, which that context does not list.

### Assumptions

1. The runner keeps `run_git`'s signature and `bytes` result for its existing callers. A command whose nonzero exit is
   an answer needs the exit status as well as the output (`merge-tree` exit `0` is a clean tree, `1` a conflict), so
   the accepted statuses are an explicit parameter of a sibling function on the same runner that returns both;
   `run_git` is that function with only `0` accepted. Attaching standard output to `GitError` is not chosen: it would
   make an answer travel as an error.
2. The spec bundle is shipped to projects without this repository's paths, and the `authoring` bundle's
   `agent-asset-writing` instruction (Self-Containment) forbids citing the authoring repository's paths in bundle text.
   So the payload rule names the architecture declaration a project's dependency check reads generically, with its
   reason, and the root `AGENTS.md` Architecture and Boundaries section names devkit's declaration: the
   `feature_dependencies` entries of `.devkit/architecture.toml`.
3. The capability `CAP-DLV-delivery-workflows` lists only the payload rules with a cross-role contract (sync outputs,
   probe paths, scratch files); this payload rule changes no role contract and stays in the bundle guidance.
4. `specs/` stops being a path no test reads: every `specs/` change selects the citation test (about a second), since
   a new spec, plan, tasks or feedback ID can collide with a bundle example as a new document under `docs/` can. The
   selection keeps the script's prefix convention instead of matching Markdown files only.

## 2. User Stories

- **US-1**: As a devkit maintainer, I want commands whose nonzero exit is an answer to run on the shared Git runner,
  so that Git's environment, standard input and timeout rules live in one place.
- **US-2**: As the Host completing a local-orchestrated run, I want the repository guides to name the generated check
  before the batch test run, so that they describe the same completion as the `spec-orchestrate` skill.
- **US-3**: As the Host delegating a cross-feature design choice, I want the payload guidance to settle whether the
  worker may add a dependency edge, so that the worker can build the option it chooses or knows it cannot.
- **US-4**: As a developer adding a document, I want the affected test run to include the bundle citation test, so
  that a collision with a cited example ID fails during development.
- **US-5**: As an agent editing a bundle's agent assets, I want the repository guide to name the `agent-asset-writing`
  instruction, so that I apply its rules before writing.

## 3. Non-Goals

1. **Scope Excluded**: Moving any other `run_git` caller (for example `is_ancestor` or `_signs`, which catch exit `1`)
   onto the new parameter, and changing `GitError`'s fields.
2. **Scope Excluded**: Changing `merge-tree`'s result handling, error codes or timeout; only the way the command runs
   changes.
3. **Scope Excluded**: Changing the `spec-orchestrate` batch completion itself, or editing the managed `AGENTS.md`
   block by hand.
4. **Scope Excluded**: Changing the architecture rule or its declaration, or the citation test itself.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] An accepted nonzero exit returns its status and output

- **Given** a repository in which `git merge-base --is-ancestor HEAD <first commit>` exits `1`
- **When** the runner is called with exit statuses `0` and `1` accepted
- **Then** it returns exit status `1` and Git's standard output, and raises no `GitError`

### [AC-02] An exit outside the accepted statuses still raises as before

- **Given** a command that exits `128` (`rev-parse --verify no-such-ref`)
- **When** the runner is called with exit statuses `0` and `1` accepted
- **Then** it raises `GitError` with `returncode == 128` and Git's standard error, as `run_git` does; `run_git`
  without the parameter raises on exit `1` as before, and every existing `run_git` test passes unchanged

### [AC-03] merge-tree runs on the shared runner with unchanged results

- **Given** `devkit_agt.features.worktree.services.merging`
- **When** a moved-target merge is built
- **Then** the module imports no `subprocess` and runs `git merge-tree --write-tree` through the shared runner with
  exit statuses `0` and `1` accepted and its 120-second timeout, and the existing worktree merging and integration
  tests pass unchanged

### [AC-04] The guides name the generated check before the batch test run

- **Given** `docs/development/workflow.md`, `docs/development/ci-cd.md` and the repository-owned Verification
  paragraph of the root `AGENTS.md`
- **When** each describes the step after a local-orchestrated run
- **Then** each names `devkit generated check` and, for stale artifacts, `devkit generated regen <ids>` with a commit,
  before `just test-affected --base <batch start>`

### [AC-05] The payload guidance settles a delegated cross-feature edge

- **Given** the `spec-delegate` payload reference in both rendered environments (`local`, `cloud`)
- **When** a payload delegates a cross-feature design choice
- **Then** one rule states that it either names in the write scope the architecture declaration the project's
  dependency check reads, limited to its feature edge entries, or states that a new feature edge is out of scope, and
  a guidance test pins it; the root `AGENTS.md` names devkit's declaration, the `feature_dependencies` entries of
  `.devkit/architecture.toml`, for the same choice

### [AC-06] Document changes select the bundle citation test

- **Given** `scripts/affected_tests.py`
- **When** the changed paths are only a `docs/` document, or only a `specs/` record
- **Then** the selection is `partial` and includes `tools/devkit-dev/tests/integration/test_bundle_citations.py`; a
  `docs/` change keeps every test it selected before

### [AC-07] The repository guide names the agent-asset-writing instruction

- **Given** the repository-owned part of the root `AGENTS.md` (outside the `DEVKIT` markers)
- **When** an agent is about to edit any bundle's skill, playbook, instruction or guide
- **Then** one line tells it to run `uv run devkit get-context authoring` and apply its `agent-asset-writing`
  instruction

## 5. Source feedback

- `FB-run-git-drops-output-on-nonzero-exit`: the shared runner serves commands whose nonzero exit is an answer, and
  `merge-tree` moves onto it (AC-01 to AC-03).
- `FB-workflow-batch-run-omits-generated-check`: the two development guides and the root `AGENTS.md` name the
  generated check before the batch test run (AC-04).
- `FB-layering-choice-without-architecture-scope`: the payload guidance settles the architecture declaration in a
  delegated cross-feature choice (AC-05).
- `FB-citation-test-not-selected-by-docs-changes`: `docs/` and `specs/` changes select the citation test (AC-06).
- `FB-bundle-asset-edits-miss-authoring-instruction`: the root `AGENTS.md` names the `agent-asset-writing`
  instruction for bundle asset edits (AC-07).
