---
id: PROP-adaptive-assignment-cli-target
title: Target Living Spec Structure for PROP-adaptive-assignment-cli
status: draft
proposal: PROP-adaptive-assignment-cli
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
  - file: docs/architecture/ARCH-05-1-containers.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/architecture/ARCH-07-deployment.md
  - file: docs/development/reference/adaptive.md
  - file: docs/development/reference/README.md
---

# [Blueprint] PROP-adaptive-assignment-cli: Target Living Spec Structure for Assignment ledger and return verification commands for adaptive delegation

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-adaptive-assignment-cli is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

`PROP-adaptive-package-extraction` lands first and rewrites several of the passages below for the move out of the
catalog. Each item states what must hold after this unit; where the landed wording already says it, nothing changes.

---

## 1. System Capabilities Plan (docs/capabilities/)

- New CAP-DLV-adaptive-assignments (`docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md`): the contract of
  `devkit adaptive assignment`.
  - Scope: recording, return, verification, closing and listing of delegated assignments, and validation of their
    governing documents. Scope Excluded: starting agents, running declared checks, creating worktrees, blocking a
    session, pruning, an MCP service, glob scopes.
  - Rules, one EARS sentence each with its test path: the ledger location and append-only writes under the lock;
    the unterminated final fragment; the write-scope prefix rule; overlap refusal and its two exemptions; nesting depth
    and narrowed authority; governing document validation in the assignment's worktree with
    `ADAPTIVE_GOVERNING_UNRESOLVED`; each verification check with its code; the changed-path definition; `close`
    with `--reason` and `ADAPTIVE_CLOSED_UNVERIFIED`; the facts `list` observes; no change to any tracked file or
    `git status` result; approach independence.
  - Interfaces: the command synopsis, sentinels, JSON objects, the assignment fields, the code table with level and
    exit code, and the stated limits of verification (proposal §3.2 to §3.6).
  - Frontmatter `entrypoints`: the feature's CLI module; `usecases`: `UC-advance-an-idea`.
- `CAP-DLV-adaptive-development`:
  - Rule 2 (independent installation): the `devkit-adaptive` distribution MUST require `devkit-docs` and MUST
    install without a devkit-spec distribution; installing it alone provides the document system and the harness,
    with the `docs` and `harness` bundles selected by their own `auto_select`. Test: the installed-consumer test.
  - Rule 13 and 13a: WHEN the coordinator delegates a deliverable, it SHOULD record the assignment and verify its
    return with the assignment commands (CAP-DLV-adaptive-assignments). IF a command cannot record, THEN the existing
    manual obligations apply unchanged and the assignments are reported as unrecorded.
  - Rule 14: current context names outstanding assignments by ledger ID, and the ledger retains their ownership,
    base and scope.
  - Rule 18: the approach value, bundle, entry skill and context file use `adaptive-dev`; the command group is
    `devkit adaptive`.
  - Rule 19: archetypes state no command prerequisite.
  - Rule 26: the condition "WHERE the project maintains documents" is dropped. WHEN the coordinator partitions a
    multi-writer build, it MUST find the documents that govern the goal and name them in each assignment by ID, by
    path where a document has no ID, or as `none`; recording the assignment validates them
    (CAP-DLV-adaptive-assignments).
  - Rule 27: the document checks in combined checks are `devkit rules check` on the changed documents plus any
    check the project defines; a check that could not run is reported as unverified. The last conditional becomes:
    IF the project has no document yet, THEN the coordinator MUST record that fact in current context, MUST NOT
    seed a document tree, and writes the first document only where a retained subject warrants one, in the document
    system's kinds. The sentences on current state, discarded experiments, the document map and "no per-change
    record, SDD Unit, approval or envelope" stay.
  - §2 Scope Excluded: "a document system created for a project that maintains none" becomes "a document tree seeded
    for a project that has no document". The scheduler, agent bus and model routing exclusions stay.
  - §4 "Distribution and entry": install `devkit-adaptive`, then select `uv run devkit add adaptive-dev`; the
    requirement brings the document system and the harness. "No adaptive-development runtime or CLI is added"
    becomes a pointer to CAP-DLV-adaptive-assignments. One sentence states that the distribution is not a
    `devkit bundle snapshot` source (`BUNDLE_SNAPSHOT_UNSUPPORTED`).
  - "Integration and final verification": "No implicit Unit or verification ledger is created" becomes a statement
    that integration creates no Unit and that the assignment ledger is explicit and untracked.
  - "Product notes and resume": the relation between `.devkit/adaptive-dev.md` and the ledger; "A project without a
    document tree says so there" becomes "A project that has no document yet says so there".
  - "Evidence-scoring test support" is unchanged.
- `CAP-HARN-agent-guidance`: the sentence on installing adaptive development names `devkit-adaptive` as the one
  requirement, without devkit-spec.
- `CAP-HARN-command-mount` is unchanged: its exit-code statement names `devkit spec` and `devkit docs` only.

---

## 2. Use Cases Plan (docs/usecases/)

- `UC-advance-an-idea`:
  - 5b: the Host records the assignment before dispatch and verifies the return.
  - 5b1: a lead records its children under its own assignment and closes them before returning.
  - 5b6: "in a project that maintains documents" is dropped; the governing documents are passed when the assignment
    is recorded, and an unresolved one is refused.
  - 5c: a return whose verification fails is rejected with its codes.
  - 6c: "in a project that maintains documents" is dropped; the document checks are `devkit rules check` plus any
    check the project defines.
  - 7b: on interruption the outstanding assignments stay in the ledger; current context names their IDs.
  - 7c: "a project without a document tree records that fact and gains no document system" becomes "a project that
    has no document yet records that fact and gets no seeded tree".
  - 3a: on resume the Host lists outstanding assignments and treats each open one as interrupted.
  - Scenario "Reject an out-of-scope return" (covers 5b, 5c) and scenario "Resume from recorded assignments"
    (covers 3a, 7b); both state the fallback when a command cannot record.
  - `capabilities` gains CAP-DLV-adaptive-assignments.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-1-containers`: the `devkit-adaptive` section lists the CLI `devkit adaptive assignment`, the
  dependencies `devkit-docs`, `devkit-core` and `click` (internal wheels pinned to selected actual versions) and the
  statement that it never imports `devkit_spec`; the container diagram gains the edge from `devkit-adaptive` to
  `devkit-docs`.
- `ARCH-05-2-components`: the `assignment` feature of `devkit-adaptive`, its two feature edges
  (`devkit_dist.features.project`, `devkit_docs.features.documents`) and its public list use case. The sentence
  that the `adaptive-dev` entries "add no runtime module or dependency" no longer covers `devkit-adaptive`:
  the package has a feature and requires `devkit-docs`. `devkit-spec` and `devkit-adaptive` both sit above
  `devkit-docs`, and neither imports the other.
- `ARCH-07-deployment`: a clean adaptive-dev installation is `devkit-adaptive` alone, without devkit-spec; its
  requirement on `devkit-docs` is an exact pin like every internal requirement. The sentence on the docs bundle
  says its core is auto-selected by any installation that carries `devkit-docs`.
- Decisions promoted at handoff: `PADR-adaptive-assignment-commands`, `PADR-adaptive-requires-document-system`
  (each supersedes in part `ADR-adaptive-development-and-research`) and `PADR-adaptive-assignment-ledger-storage`.
- `ADR-adaptive-development-and-research` gains two partial-supersession lines:
  - for the clause "Identifiers and commands use `adaptive-dev`", which no longer covers the command group;
  - for "independent docs/catalog installation" in the clause on catalog ownership, which no longer means two
    requirements declared side by side; the independence from devkit-spec stays.
  Its decision drivers "without another release wheel or runtime service" and "No new runtime, CLI or distribution
  mechanism" are not edited.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- New reference page `docs/development/reference/adaptive.md` with the sections Usage, Output, Error codes and
  Library, modelled on `docs/development/reference/worktree.md`; a row in `docs/development/reference/README.md`.
- `.devkit/architecture.toml`: the package entry of proposal §3.8.
- `uv.lock`: regenerated for the requirement.
- Package README of `devkit-adaptive`: the feature and its modules, the one-requirement installation, and the
  statement that the distribution is not a snapshot source.
- Root `README.md` and root `AGENTS.md`: the package row or line for `devkit-adaptive` names the bundle and the
  `devkit adaptive` commands; `AGENTS.md` states that `devkit-adaptive` never imports `devkit_spec`.
- Installation guides, each with the statement that adaptive development is installed with the one requirement
  `devkit-adaptive`, which brings the document system and the harness, without devkit-spec:
  - `guides/INSTALL_GUIDE.md`: the adaptive path, and the upgrade list (`--upgrade-package devkit-adaptive` beside
    `--upgrade-package devkit-docs` when `devkit-adaptive` is declared);
  - `guides/install/existing-repository.md` and `guides/install/new-repository.md`: the adaptive installation
    sentence;
  - `guides/install/bundle-recommendations.md`: the adaptive row and the "development without SDD lifecycle records"
    passage;
  - `guides/install/adaptive-dev-sdd-adoption.md`: adopting SDD adds `devkit-spec` and keeps `devkit-adaptive`.
- Bundle guidance: `delegation.md`, `orchestration.md`, `current-context.md`, `documents.md`, the current-context
  template, the three archetypes and the bundle constitution (proposal §3.7), with their content tests.
- `tests/e2e/smoke.sh`: the adaptive wheel with its sibling wheels and one `devkit adaptive assignment list` call.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Assignment board | Host context | Ledger under the shared Git directory, written at each event |
| Return check | Host reads the diff | `verify` compares ancestry, HEAD, changed paths and declared checks with the assignment |
| Governing documents | Named in the payload, unchecked | Resolved in the assignee's worktree when the assignment is recorded |
| Resume after interruption | `.devkit/adaptive-dev.md` if it was updated | `list` reports outstanding assignments with worktree facts; the Markdown names their IDs |
| Nesting | Stated in the payload | Depth and narrowed authority refused at `new`; open children fail the parent's verification |
| Installation | `devkit-docs` and the bundle's wheel as two requirements | `devkit-adaptive` alone; it requires `devkit-docs` |
| Document steps in guidance | Conditional on the docs bundle and on a document tree | Unconditional; documents still only where the subject warrants |
| Snapshot of the bundle source | Possible while the wheel is bundle-only | Refused (`BUNDLE_SNAPSHOT_UNSUPPORTED`) |
| A command cannot record | Not applicable | The manual procedure, unchanged |
| Scheduler, runner, hooks | None | None |
