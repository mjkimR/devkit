---
id: SPEC-generated-conflicts-in-prepared-merge
title: Settle generated-file conflicts in prepared merges
summary: Let integration preparation and integration complete a moved-target merge whose only conflicts are in registered generated files, by taking each artifact's seed side and disclosing the artifacts to regenerate on the target, instead of refusing with WORKTREE_MERGE_CONFLICT.
status: completed
created: 2026-10-30
related_capabilities: [CAP-WT-task-worktrees, CAP-INT-mcp-services, CAP-GEN-tracked-artifacts, CAP-HARN-agent-guidance]
related_usecases: [UC-drive-development-to-integration]
workflow: sdd-spec-feature
---

# [SPEC-generated-conflicts-in-prepared-merge] Settle generated-file conflicts in prepared merges

## 1. Problem Statement & Motivation

Local integration of a moved target builds the merge in the object store with `git merge-tree --write-tree`
(`ADR-moved-target-merge`; `build_result` in `packages/devkit/src/devkit_agt/features/worktree/services/merging.py`,
called by `IntegrationService` at prepare with `prospective=True` and at integrate with `advance=True`). Any conflict
refuses with `WORKTREE_MERGE_CONFLICT` (`INTERACTION`) and nothing changed.

Two integrations in this repository's local-orchestrated pilot of 2026-10-30 stopped on a conflict only in
`.devkit/installation.json`, the built-in generated artifact `devkit-receipt` (`CAP-GEN-tracked-artifacts`). The Host
merged the base into the task branch by hand, although the generated registry already says how such a file is
settled: keep the artifact's `seed` side and regenerate it. Commit c9d91146 already points the
`WORKTREE_MERGE_CONFLICT` fix and `spec-integrate` step 1 at `devkit generated resolve` for that manual path; this
change keeps it and removes the manual merge when every conflict is in a generated file.

### Settled direction (user)

- When every conflict of the in-memory merge is in a path owned by an enabled generated artifact (the registry
  `devkit generated list` reads: built-in plus `.devkit/generated.toml`), the merge keeps each such path from the
  artifact's `seed` side (`ours` = the target, `theirs` = the source; removed when that side deleted it) and
  continues instead of refusing.
- Nothing is regenerated during the in-memory build.
- Staleness stays visible: the checks on the merged result still run (`receipts.check_merge` with
  `INTEGRATION_RECEIPT_CONFLICT`, the policy digest, the CI rules), and the prepare and integrate results disclose
  the seeded artifacts (ids and paths) with the exact command that regenerates them on the target after landing,
  alongside the readiness disclosure.
- A conflict no artifact owns, or an owned conflict whose artifact's `inputs` or `updates` are also conflicted (the
  `GENERATED_INPUTS_CONFLICTED` condition of `devkit generated resolve`), still refuses with
  `WORKTREE_MERGE_CONFLICT` and nothing changed.
- The prospective (prepare) and the real (integrate) builds of one source and target produce the same tree.
- The post-batch step of a local-orchestrated run regenerates stale generated artifacts on the base branch and
  commits them before its single test run.
- This changes the "a conflict refuses at prepare" decision of `ADR-moved-target-merge`, so a new ADR records it with
  `supersedes`.

### Assumptions

- The registry that settles a build is the one committed at the build target (built-in artifacts of the running
  devkit plus the target's committed `.devkit/generated.toml`), so the prospective and real builds of one source and
  target read the same registry whatever the base checkout's working tree holds.
- Composed proposal acceptance (`devkit spec proposal accept`) and the pull-request route keep refusing every
  conflict: composed acceptance merges only a proposal directory delta and its text output does not carry
  integration notices, and the platform builds the pull request's merge itself.
- The disclosure is a `WARNING` (`INTEGRATION_GENERATED_SEEDED`), because the landed artifact is stale until it is
  regenerated; it changes the exit code only under `--strict`.

## 2. User Stories

- **US-1**: As a Host agent integrating a verified branch on the local route, I want preparation and integration of a
  moved target to complete when the only conflicts are in registered generated files, so that I merge the base into
  the task branch only for a conflict that needs a person. This changes `UC-drive-development-to-integration` 7i.
- **US-2**: As the user, I want every result that kept a generated file from one side to name the artifact, its paths,
  the side kept and the command that regenerates it, so that a stale generated file never lands unnoticed.
- **US-3**: As the Host of a local-orchestrated run, I want the batch completion step to regenerate stale generated
  artifacts on the base branch before the batch test run, so that the tests run on a consistent receipt.

## 3. Non-Goals

1. **Scope Excluded**: running an artifact's command during the in-memory build, or regenerating anything inside
   `prepare` or `integrate`.
2. **Scope Excluded**: settling conflicts on the pull-request route, in composed proposal acceptance or in
   `devkit worktree finish --merge`.
3. **Scope Excluded**: a merge driver, a commit gate for stale generated files, or any change to
   `devkit generated resolve|regen|check` behavior.
4. **Scope Excluded**: weakening `receipts.check_merge`, the policy digest or the readiness checks on the merged
   result.
5. **Scope Excluded**: an automatic commit by `integrate` of regenerated files on the target.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A conflict only in a generated file prepares and discloses the seeded artifact
- **Given** a task branch and a moved target that both changed `.devkit/installation.json` (the built-in
  `devkit-receipt` artifact, `seed = "ours"`) and nothing else in conflict, under `[worktree] merge = "no-ff"`
- **When** the Host runs `devkit integration prepare <branch> ... --route local`
- **Then** it exits `0`; the prospective result keeps `.devkit/installation.json` from the target; the JSON result
  carries `generated.seeded` with `{"id": "devkit-receipt", "paths": [".devkit/installation.json"], "seed": "ours",
  "kept": "target"}` and `generated.regenerate` `uv run devkit generated regen devkit-receipt`; `notices` carry one
  `INTEGRATION_GENERATED_SEEDED` warning whose `[FIX]` names that command and a commit on the target after landing;
  the text `[INTEGRATION_SCOPE: ...]` line carries `seeded=devkit-receipt`.

### [AC-02] Integration lands the same seeded tree and discloses it
- **Given** the request of AC-01 and an unchanged target
- **When** the Host runs `devkit integration integrate ... --expected-digest <digest>`
- **Then** it exits `0` with `status=completed`; the landed merge's tree equals the tree of the prospective result
  prepare checked; the result carries the same `generated` disclosure and `INTEGRATION_GENERATED_SEEDED` notice, and
  the text `[INTEGRATION: ...]` line carries `seeded=devkit-receipt`.

### [AC-03] The seed side decides the kept file, or its removal
- **Given** a project `.devkit/generated.toml` artifact with `seed = "theirs"` owning a conflicted path, or an owned
  path that the seed side deleted while the other side modified it
- **When** the merge is built
- **Then** the result keeps the source's file for `seed = "theirs"` (`kept: "source"`), and leaves the path out of
  the result tree when the seed side deleted it.

### [AC-04] A conflict no artifact owns still refuses with nothing changed
- **Given** a moved target that conflicts with the branch in `.devkit/installation.json` and in `README.md`
- **When** the Host runs `devkit integration prepare`
- **Then** it refuses with `WORKTREE_MERGE_CONFLICT` (exit `2`), one `[DETAIL]` names `README.md` as owned by no
  generated artifact, and the target ref, the source ref, the base checkout and the task worktree are unchanged.

### [AC-05] An owned conflict whose artifact reads a conflicted path refuses
- **Given** a moved target that conflicts with the branch in `.devkit/installation.json` and in `AGENTS.md`, which
  `devkit-receipt` lists under `inputs` and `updates`
- **When** the Host runs `devkit integration prepare`
- **Then** it refuses with `WORKTREE_MERGE_CONFLICT`, one `[DETAIL]` names `AGENTS.md` as read by `devkit-receipt`,
  and nothing changed.

### [AC-06] The checks on the seeded result still run
- **Given** a receipt-only conflict whose seeded receipt leaves a tracked record inconsistent with a merged file
- **When** the Host runs `devkit integration prepare`
- **Then** it refuses with `INTEGRATION_RECEIPT_CONFLICT` and nothing changed; the readiness provider received the
  seeded prospective result as `result_sha`.

### [AC-07] The registry comes from the build target
- **Given** a target whose committed `.devkit/generated.toml` disables `devkit-receipt` (`enabled = false`)
- **When** a receipt-only conflict is prepared
- **Then** it refuses with `WORKTREE_MERGE_CONFLICT`, naming `.devkit/installation.json` as owned by no generated
  artifact; the registry of a build is read from the committed file at the build target, never from the working
  tree.

### [AC-08] Other merge paths keep refusing every conflict
- **Given** a receipt-only conflict
- **When** `build_result` is called without a conflict settler (the pull-request route, `finish --merge`, composed
  proposal acceptance)
- **Then** it refuses with `WORKTREE_MERGE_CONFLICT`, as before this change.

### [AC-09] The batch completion step regenerates stale generated artifacts first
- **Given** the `spec-orchestrate` skill and the `spec-integrate` skill as installed by `devkit sync`
- **When** an agent reads the Completion section and integration steps 5 and 6
- **Then** the batch test run first runs `devkit generated check` on the base branch HEAD and, when it reports stale
  artifacts, `devkit generated regen <ids>` and a commit, before the tests; integration presents the seeded artifacts
  with the scope and, in direct mode, regenerates and commits them on the base after landing.

## 5. Source feedback

None: the Host observed the problem in the pilot of 2026-10-30 and supplied the direction with the task.
