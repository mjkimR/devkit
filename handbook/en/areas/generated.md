---
sources:
  CAP-DIST-sync-and-transactions: 3d649f4fe73a83d740680e7b07a40966a90dabf8
  CAP-GATE-commit-gates: 83c1bd822d3330dab5eed84e7b8f13a552e5f638
  CAP-GEN-tracked-artifacts: f62da86cdec8fffc20ce2f2d33a6dc78aa340b83
title: Generated Files
---

# Generated Files

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `3da97383dc87`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Some files are produced by a command but tracked by Git: `uv.lock`, devkit's own receipt
`.devkit/installation.json`, generated clients, rendered snapshots. Git merges them as text, so two branches that
each regenerated one conflict even when their inputs merge cleanly, and a textual merge is rarely what the generator
would write. `devkit generated` (from `devkit-agt`) settles such conflicts by regenerating instead of merging, and
checks that committed copies are up to date. The contract is
[CAP-GEN-tracked-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/generated/CAP-GEN-tracked-artifacts.md).

Nothing runs automatically. You, or your agent, run `resolve` when a merge, rebase or cherry-pick stops, and CI runs
`check`. Where this fits in the life of a branch is described in [Concepts](../concepts.md).

## Register an artifact

An artifact is a set of paths owned by one command. Declare it in `.devkit/generated.toml`, a tracked file beside
`.devkit/config.toml`:

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]
command = "uv lock && uv sync"

[artifacts.devkit-receipt]
after = ["uv-lock"]
```

- `paths` are the files the command owns; `command` runs with `sh -c` from the project root, and `{devkit}` stands
  for the running devkit.
- `inputs` are the files the command reads. Leave it empty only if any conflict should block `resolve`.
- `updates` lists files the command rewrites without owning them, such as the managed block of `AGENTS.md`.
- `after` orders artifacts; `seed` picks which side of a conflict the command starts from (`ours` by default);
  `optional` skips an artifact with no tracked paths; `enabled = false` drops one.

devkit registers one built-in artifact, `devkit-receipt`, whose command is `{devkit} sync`. Because the receipt
records installed packages, a uv project orders it after its lockfile as above, so the environment is updated before
the receipt is regenerated. A project that tracks native projections adds them to the receipt's `updates`, not its
`paths`. `uv run devkit generated list` shows the registered artifacts, built-in ones included.

Commands must be deterministic: the same inputs give the same bytes. A command that writes timestamps or absolute
paths makes `check` report it as always stale.

## Settle a merge conflict

When Git stops with conflicts:

```bash
uv run devkit generated resolve --dry-run   # show the plan, change nothing
uv run devkit generated resolve             # seed, regenerate, stage
```

`resolve` classifies each unmerged path as owned by an artifact or not, seeds every owned conflict to its `seed`
side, runs the commands in order and stages the result. It never commits. Then:

- with no conflicts left it prints `[NEXT_CMD: git <operation> --continue]`;
- with conflicts it does not own left, it lists them in a `GENERATED_CONFLICTS_REMAIN` warning for you to resolve
  by hand;
- during a rebase each replayed commit may stop again, so run `resolve` at each stop.

It refuses before changing anything when a conflict it does not own is an *input* of an artifact in the plan
(`GENERATED_INPUTS_CONFLICTED`): resolve and stage those inputs first, then rerun, so no command reads conflict
markers. A failed command is `GENERATED_COMMAND_FAILED`; a command that changed files it did not declare is
`GENERATED_OUTPUT_UNDECLARED`, and its changes stay in the work tree for review. Either way nothing is staged and a
rerun starts over cleanly.

## Check and regenerate outside a merge

A clean textual merge is not a conflict, so `resolve` does not touch it, yet the file may still be inconsistent with
the merged inputs. Two commands cover that:

- `uv run devkit generated check` regenerates every artifact in a temporary detached worktree of `HEAD` (or
  `--rev REV`) and reports each stale one as `GENERATED_STALE`, exiting `1`. Your checkout is not touched, and the
  commands run as in a fresh clone, so they must work without ignored files. Run it in CI.
- `uv run devkit generated regen [ID...]` reruns the commands in place and stages nothing. It refuses with
  `GENERATED_UNMERGED` while the index has conflicts; use `resolve` then.

## Limits and trust

- An artifact owns whole files. A file that is partly yours, like the root `AGENTS.md`, is never an artifact; its
  conflicts are resolved by hand and the owning command rewrites its part through `updates`.
- There is no merge driver: Git runs one per file before the tree is merged, so it cannot regenerate. A CI bot that
  merges the base into pull requests and runs `resolve` is left to each repository, and a hosting service's merge
  button runs no custom resolution.
- Commands come from the tracked `.devkit/generated.toml` and run with your privileges, like gate commands
  (`CAP-GATE-commit-gates`). A CI job that runs `resolve` or `check` on untrusted contributions takes the
  configuration from a trusted commit.

How the receipt itself is written and kept in step across clones is described in [Distribution](distribution.md)
and `CAP-DIST-sync-and-transactions`.
