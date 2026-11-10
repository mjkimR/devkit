---
id: PROP-core-git-observation-helpers
title: Public Git observation helpers in devkit-core
summary: "Add public devkit-core functions that read git worktree list and git status porcelain records and resolve a revision to a commit ID, and move the packages' private parsers to them, so each Git output is parsed once and tested once."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: packages/devkit-core/
priority: medium                      # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-core/
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit/tests/
    - packages/devkit-dist/src/devkit_dist/features/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/tests/
    - packages/devkit-adaptive/src/devkit_adaptive/features/
    - packages/devkit-adaptive/tests/
    - packages/devkit-mcp/src/devkit_mcp/features/
    - packages/devkit-mcp/tests/
    - packages/devkit-viewer/src/devkit_viewer/features/
    - packages/devkit-viewer/tests/
    - .devkit/architecture.toml
  excludes:
    - docs/capabilities/
    - docs/decisions/
    - packages/devkit-spec/src/devkit_spec/bundles/
    - packages/devkit-adaptive/src/devkit_adaptive/bundles/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-core-git-observation-helpers] Public Git observation helpers in devkit-core

## 1. Background & Hypothesis

`devkit_core.core` exports only `run_git`, `run_git_text` and `is_ancestor` for Git. Every feature that needs the
worktrees of a repository or the records of `git status --porcelain` parses the output itself:

- `git worktree list --porcelain` is read at 12 call sites in six packages (`devkit_agt` worktree lifecycle,
  execution, isolated execution and integration; `devkit_dist` shared repositories and host registrations;
  `devkit_spec` scope inventory and reconcile contract; `devkit_adaptive` assignment; `devkit_mcp` runtime
  configuration; `devkit_viewer` browse planning). Some use `-z`, some split on blank lines, some read only the first
  line.
- `git status --porcelain=v1 -z` records are parsed by `devkit_agt.features.compact.services.porcelain`
  (a feature without a `public_modules` entry), `devkit_spec.features.worker.usecases.inspect`,
  `devkit_spec.features.delivery.usecases.native_handoff` and `devkit_adaptive.features.assignment.repositories.git`.
- Revision resolution (`git rev-parse`) is written inline wherever a full commit ID is needed.

The details that are easy to get wrong are decided separately in each copy: the record order of a rename in `-z`
output, the trailing slash of an untracked nested repository, and the `bare`, `detached`, `locked` and `prunable`
worktree records. Packages that may not import `devkit_spec` or `devkit_agt` cannot reuse the existing parsers, so
each new feature adds another (the adaptive assignment commands added the latest pair).

Hypothesis: one public, tested reading of each output in `devkit_core.core` removes the duplicated parsers without
changing any command's behavior, and new features stop adding copies.

## Source feedback (when this proposal receives feedback)

- `FB-no-public-git-observation-helpers`: the whole observation (worktree records, status records with both names of a
  rename, revision resolution, moving the existing callers).

## 2. Technical Spike Questions

- **Q1**: Which call sites read Git output with semantics a shared helper must preserve (no `-z`, first line only,
  `--no-optional-locks`, `--no-renames`, `--ignore-submodules=none`, deadlines through `Deadline`, a local `git`
  wrapper instead of `run_git`), and which differences are accidental?
- **Q2**: Does the caller migration land in the same spec as the helpers, or does the spec add the helpers and move
  only the callers whose tests pin the behavior, leaving the rest to later touches?
- **Q3**: Is revision resolution worth a helper, given most `rev-parse` uses are one-line calls, or should it be limited
  to resolving a revision to a verified full commit ID?
- **Q4**: Which record shapes (dataclass fields, rename representation, path decoding with `surrogateescape`) serve
  every current caller without each one re-mapping them?

## 3. Proposed Design & Impact

- Add to `devkit_core.core.git` and export beside `run_git`:
  - a worktree reader returning records with path, HEAD, branch, `bare`, `detached`, `locked` and `prunable`;
  - a status reader returning porcelain v1 records with the status code, the path and, for a rename or copy, the
    original path, with the options callers need passed through;
  - a revision resolver returning a full commit ID or raising `GitError`.
- Unit-test each reader against recorded Git output, including renames, untracked nested repositories, detached,
  bare, locked and prunable worktrees, and non-UTF-8 paths.
- Move the existing parsers to the helpers, feature by feature, keeping each feature's tests green; remove
  `devkit_agt.features.compact.services.porcelain` once its callers moved.
- No CLI, output or capability contract changes; `devkit-core` keeps importing no application package, and
  `devkit-dist` stays independent of `devkit_agt`.

## 4. Lifecycle & Retirement Criteria

- On acceptance (plan-accept): `devkit spec proposal accept core-git-observation-helpers --by user` records
  `gate:plan-accept` and `status: accepted`, then the Planning branch is merged; an eligible draft may instead be
  accepted with `--direct` on the base. Development starts with `devkit spec proposal handoff core-git-observation-helpers`.
- On rejection: change only `status: rejected`, with the user's decision and reason as a decision sentence in the
  commit message; a later hygiene pass writes the rejection ADR and deletes the proposal directory.
