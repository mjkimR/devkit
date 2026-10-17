---
id: CAP-GEN-tracked-artifacts
title: "Tracked Generated Artifacts"
summary: "Deterministic regeneration and conflict resolution for machine-generated files."
area: generated
status: active
created_at: 2026-10-17
---

# [CAP-GEN-tracked-artifacts] Generated Files: Overview

`devkit.generated` manages files that a command generates but Git tracks: lockfiles, devkit's installation receipt, generated clients, rendered snapshots. Git merges them as text, so two branches that each regenerated one conflict even when their inputs merge cleanly, and a textual merge of such a file is rarely what the generator would write. A project registers each artifact with its paths and the command that regenerates it. `resolve` settles a conflict in those paths by regenerating instead of merging, `check` reports files committed out of date, and `regen` rewrites them. Quick reference: [reference.md](../../generated/reference.md).

The module is trigger-agnostic. Nothing runs automatically: an agent or a person runs `resolve` when a merge, rebase or cherry-pick stops, and a CI job runs `check`. Section 6 covers the integration points (merge drivers, hooks, bots) that a project can build on top.

## 1. Artifacts

An artifact is a set of paths owned by one command. A project declares its artifacts in `.devkit/generated.toml`, a Git-tracked file of its own beside `.devkit/config.toml`, so the registry can grow without crowding the project configuration. The file is optional, and its only top-level table is `[artifacts]`:

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]
command = "uv lock"
```

| Key | Default | Meaning |
| --- | --- | --- |
| `paths` | required | Patterns of the files the command owns. Conflicts in them are settled by regenerating, and `check` compares them. |
| `command` | required | Shell command run with `sh -c` from the project root. `{devkit}` stands for the running devkit (`<python> -P -m devkit`). |
| `inputs` | `[]` | Patterns of the files the command reads. `[]` means any file, so every conflict the artifact does not own blocks `resolve` (section 3). |
| `updates` | `[]` | Patterns of files the command also rewrites without owning them, such as a managed block inside a project-owned file. They are never seeded, but changed ones are staged. |
| `after` | `[]` | Artifacts regenerated before this one. When one of them is regenerated, this one is regenerated after it. |
| `seed` | `"ours"` | The side a conflicted path keeps before the command runs: `"ours"` (index stage 2) or `"theirs"` (stage 3). |
| `optional` | `false` | Skip the artifact while none of its paths is tracked. A conflict in one of its paths is always settled. |
| `enabled` | `true` | `false` drops the artifact, a built-in one included. |

- **Patterns** are relative to the project root (the directory holding `.devkit/`) and `/`-separated. `*`, `?` and `[...]` match within one path segment, and a `**` segment matches any number of segments (`gen/**`, `**/schema.json`). Absolute patterns, `.` and `..` segments, empty segments and backslashes are `GENERATED_CONFIG_INVALID`.
- **One owner per path**: a path two artifacts' `paths` match is `GENERATED_CONFIG_INVALID` when it is met.
- **Ordering**: artifacts run in `after` order, ties in id order. An `after` naming an unknown or disabled artifact, or a cycle, is `GENERATED_CONFIG_INVALID`.
- **Ids** are lowercase letters, digits, `-` and `_`, starting with a letter or digit.
- **Errors**: an unreadable or invalid TOML file is `CONFIG_INVALID`. Any other problem in it is `GENERATED_CONFIG_INVALID`, targeting `.devkit/generated.toml`. `.devkit/config.toml` accepts no `[generated]` table.
- **Commands** must be deterministic: the same inputs give the same bytes, with no timestamps, absolute paths or machine-specific ordering. A command that is not deterministic makes `check` report the artifact as always stale and makes `resolve` produce churn.

### Built-in Artifacts

devkit registers its own tracked output in `builtin.toml` beside the module, in the same format as `.devkit/generated.toml`. A project changes a built-in artifact with an `[artifacts.<id>]` table of the same id, which changes only the keys it sets, and drops it with `enabled = false`.

| Id | Paths | Command | Notes |
| --- | --- | --- | --- |
| `devkit-receipt` | `.devkit/installation.json` | `{devkit} sync` | `inputs`: `.devkit/config.toml`, `.devkit/overrides/**`, `AGENTS.md`. `updates`: `AGENTS.md` (the DEVKIT block), `.devkit/.gitignore` (seeded when missing). `optional`: projects without a receipt skip it. |

The receipt also records the installed packages, so a merge that changes the environment (`uv.lock`) must update the environment before the receipt is regenerated. A uv project registers its lockfile and orders the receipt after it:

```toml
# .devkit/generated.toml
[artifacts.uv-lock]
paths = ["uv.lock"]
inputs = ["pyproject.toml", "packages/*/pyproject.toml"]
command = "uv lock && uv sync"

[artifacts.devkit-receipt]
after = ["uv-lock"]
```

A project that tracks native projections (`.claude/skills/...`) adds them to the receipt's `updates`. Do not add them to its `paths`, which would seed project-owned skills in the same directories from one side.

## 2. resolve

`devkit generated resolve` runs while the index has unmerged paths: during a merge, rebase, cherry-pick, revert or `git am`, or after any command that leaves conflicts. It never commits.

1. **Classify.** Each unmerged path is either owned (an enabled artifact's `paths` match it) or not. The plan is the artifacts that own a conflict, plus every artifact that comes after one of them, in order.
2. **Refuse on conflicted inputs.** If a conflict the plan does not own matches the `inputs` of an artifact in the plan, or the artifact declares no `inputs`, `resolve` refuses with `GENERATED_INPUTS_CONFLICTED` before changing anything. The details list each path and the artifacts that read it. The command would otherwise read conflict markers. Resolve those paths by hand, stage them, and rerun.
3. **Seed.** Each owned conflict is set to its artifact's `seed` side: `git checkout --ours|--theirs`, or removal when that side deleted the file. Every owned conflict is seeded before any command runs, so no command reads markers from another artifact's files. The seed matters for incremental generators: `uv lock` keeps the pins of the lockfile it finds, so the merged lock starts from the seed side's resolutions.
4. **Regenerate.** Each artifact in the plan runs its command, except an `optional` one that owns no conflict and has none of its paths tracked. A failed command is `GENERATED_COMMAND_FAILED` with the log path and last output lines. A command that changes any file outside its `paths` and `updates` is `GENERATED_OUTPUT_UNDECLARED`, and its changes stay in the work tree for review. Either error stops the run with nothing staged. Rerunning starts over from the same conflicts, because seeding overwrites what the stopped run left.
5. **Stage.** The owned conflicts and every file a command changed are staged (`git add`, or `git rm --cached` for a removed file). Paths are staged as they are in the work tree.
6. **Report.** Conflicts that remain are not owned by any artifact. They are listed in a `GENERATED_CONFLICTS_REMAIN` warning, and no `[NEXT_CMD]` is printed. With none left, `[NEXT_CMD: git <operation> --continue]` names the command that continues the operation. During a rebase, each replayed commit may stop again, so run `resolve` at each stop.

`--dry-run` stops after step 2. It prints the plan (`GENERATED_PLANNED`), changes nothing and runs no command. With no unmerged paths, `resolve` does nothing and exits `0`, so a rerun after success is harmless.

**Sides during a rebase.** Git's index stages are inverted during a rebase: `ours` (stage 2) is the branch being rebased onto, and `theirs` (stage 3) is the commit being replayed. The regenerated result is the same either way. Only the starting state of an incremental generator differs.

**A clean textual merge is not regenerated.** `resolve` acts on conflicts. When Git merged a generated file without a conflict, the file may still be inconsistent with the merged inputs. `check` in CI catches that, and `regen` fixes it.

## 3. Detecting Undeclared Writes

Before and after each command, devkit records every path `git status` lists (untracked included, ignored excluded) with its status and content digest. A path whose entry differs afterwards was changed by the command. It must match the artifact's `paths` or `updates`, or the run stops with `GENERATED_OUTPUT_UNDECLARED`. Ignored files (`.venv/`, `.devkit/managed/`, build caches) are never compared, so environment and cache writes are allowed. The check catches commands that touch more than they declare, which `resolve` would otherwise stage or leave unnoticed.

## 4. regen

`devkit generated regen [ID...]` runs the commands of the given artifacts and of every artifact after them in place, or of every artifact when no id is given. It stages nothing. An `optional` artifact with nothing tracked is skipped. It refuses with `GENERATED_UNMERGED` while the index has unmerged paths, because a command would read conflict markers. Use `resolve` then.

## 5. check

`devkit generated check [ID...] [--rev REV]` checks out `REV` (default `HEAD`) in a temporary detached worktree, reads the registry (`.devkit/generated.toml`) from that commit, runs the commands there in order, and reports each artifact whose owned files changed as `GENERATED_STALE`. It exits `1` when any artifact is stale, with a `[FIX]` naming the `regen` command. The checkout is not touched, and the temporary worktree is removed afterwards.

- The commands run in a fresh checkout. That checkout has no ignored files (no `.venv`, no `.devkit/managed/`) and gets the caller's environment, so a command must work from a clean clone, as it does in CI.
- Undeclared writes stop `check` too (`GENERATED_OUTPUT_UNDECLARED`), with exit `2`.
- `{devkit} sync` in the temporary worktree writes the shared Git hooks like any writing sync ([Commit Gate Overview, section 3](../../gate/overview.md#3-hook-wrappers)). The hooks it writes are the same ones the checkout already has.

In CI: `uv run devkit generated check`.

## 6. Integration Points

Git offers no hook that runs at the right moment to regenerate inside a merge, so automation is layered on top of `resolve`:

| Level | How | Status |
| --- | --- | --- |
| Detection | `devkit generated check` in CI | Built in |
| Command | `devkit generated resolve` when an operation stops on conflicts | Built in |
| Local merge driver | `.gitattributes` `merge=<driver>` that takes one side so Git does not stop, plus a commit gate that refuses stale generated files with `[FIX] devkit generated regen` | Not built: a merge driver runs per file before the tree is merged, so it cannot regenerate. It does not run for modify/delete or rename conflicts, and lives in Git configuration that is not versioned. |
| CI bot | On a push to the base branch, merge the base into each conflicting pull request, run `resolve`, and push when no conflict remains | Left to each repository: it needs a token that triggers workflows, it cannot push to forks, and it must run the base branch's configuration, never the pull request's |

The server-side merge of a hosting service (a pull request's merge button or merge queue) runs no custom resolution, so it cannot be automated there.

## 7. Scope

- **Whole files only.** An artifact owns whole files. A file that is partly project-owned, such as the root `AGENTS.md` with its DEVKIT block, is not an artifact. Its conflicts are resolved by hand, and the owning command rewrites its part through `updates`.
- **Trust.** Commands come from the tracked `.devkit/generated.toml` and run with the caller's privileges, as `verify-commands` gate commands do. A CI job that runs `resolve` or `check` on untrusted contributions must take the configuration from a trusted commit.
