---
id: ADR-generated-conflicts-in-prepared-merge
title: Prepared merges settle conflicts confined to generated files
summary: "For a moved-target merge whose only conflicts are in registered generated files, we keep each artifact's seed side in the in-memory merge and disclose the artifacts to regenerate on the target, to drop the manual base merge, accepting that a stale generated file lands until it is regenerated."
proposal: SPEC-generated-conflicts-in-prepared-merge
status: accepted
created_at: 2026-10-30
supersedes:
  - ADR-moved-target-merge
---

# [ADR-generated-conflicts-in-prepared-merge] Prepared merges settle conflicts confined to generated files

- **Status**: Accepted
- **Date**: 2026-10-30

This decision supersedes only the clause of `ADR-moved-target-merge` that "a conflict refuses at prepare with
`WORKTREE_MERGE_CONFLICT` and nothing changed", for conflicts confined to generated files. The prospective merge, the
checks on the merged result, the deterministic prospective commit, the pull-request route, `ff-only` and
`finish --merge` rules of that decision remain in force.

---

## 1. Context & Problem Statement

Local integration builds the merge of a moved target with `git merge-tree --write-tree` and refuses any conflict
with `WORKTREE_MERGE_CONFLICT`. Two integrations of one local-orchestrated run stopped on a conflict only in
`.devkit/installation.json`, the built-in generated artifact `devkit-receipt`, and the Host merged the base into each
task branch by hand. The generated registry (`CAP-GEN-tracked-artifacts`) already states how such a file is settled:
keep the artifact's `seed` side, then regenerate it. Regenerating needs a checkout and runs the artifact's command,
which an in-memory build has neither of.

## 2. Decision Drivers

- No manual base merge for a conflict the registry already settles.
- A stale generated file may land, but never unnoticed.
- The checks on the merged result (`receipts.check_merge`, the policy digest, the CI rules) stay as they are.
- Prepare and integrate of one source and target build one tree, so the checked result is the landed result.
- `devkit_agt.features.worktree` stays independent of the generated registry (`ARCH-05-2-components`).

## 3. Considered Options

- **Keep refusing** (rejected): every concurrent receipt change costs a base merge, a rerun and a retry.
- **Regenerate during the build** (rejected): needs a temporary checkout and runs project commands inside
  integration, before the user's confirmation, with the merged tree's commands.
- **Seed and disclose** (selected): keep each owned conflict at its artifact's seed side, refuse when any conflict is
  unowned or read by an artifact to regenerate, and disclose the seeded artifacts with the command that regenerates
  them on the target after landing.

## 4. Decision Outcome

Chosen option "Seed and disclose", because it removes the manual base merge while every check on the merged result
still runs and the result names what is stale.

- When every conflict of a local prepare or integrate build is owned by an enabled artifact of the registry committed
  at the build target, the build keeps each owned path from the artifact's `seed` side (`ours` = the target,
  `theirs` = the source) and removes it where that side deleted it. Nothing is regenerated during the build.
- A conflict no artifact owns, or one an artifact to regenerate reads or updates (`inputs`, `updates`, or any path
  when it declares no `inputs`), refuses with `WORKTREE_MERGE_CONFLICT`, nothing changed, one detail per such path.
- The worktree feature takes the settler as an injected callable (`ConflictSettler`); the integration feature
  composes it from the generated registry. Without a settler, a build refuses every conflict as before: the
  pull-request route, `finish --merge` and composed proposal acceptance pass none.
- The prepare and integrate results disclose the seeded artifacts in `generated` (ids, paths, seed, side kept and the
  `devkit generated regen <ids>` command) and with an `INTEGRATION_GENERATED_SEEDED` warning, beside the readiness
  disclosure.
- A local-orchestrated run regenerates stale artifacts on the base branch and commits them before its batch test run
  (`ADR-post-batch-test-run`); a direct-mode integration does so after landing.

## 5. Consequences

- **Positive**:
  - A receipt-only conflict no longer requires a base merge into the task branch.
  - The disclosure and the batch completion step make the stale artifact visible and fixed on the base branch.
- **Negative / Risks**:
  - The landed artifact is the seed side's file until regenerated; a consumer reading it in between sees the seed
    side's content. `receipts.check_merge` still refuses a merged receipt record that matches neither parent.
  - The integration feature depends on the generated feature, a new edge in the declared feature graph.
- **Follow-ups**:
  - `ADR-moved-target-merge` gets a "Superseded in part by" line naming this decision, without a status change.

## 6. Confirmation

- Tests: `packages/devkit/tests/e2e/features/integration/test_base_advance.py` (a receipt-only conflict prepares,
  discloses and lands the prepared tree; mixed and input conflicts refuse with nothing changed; the receipt check
  still refuses) and `packages/devkit/tests/integration/features/worktree/test_merging.py` (seeding sides, removal,
  no settler).
- `RULE-architecture` checks the declared `integration -> generated` feature dependency.
