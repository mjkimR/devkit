# devkit_agt.features.generated

Tracked generated files: register them, check them, regenerate them, and settle their merge conflicts by regenerating. Semantics: `CAP-GEN-tracked-artifacts`.

## Usage

```bash
uv run devkit generated list                 # the registered artifacts: built-in and .devkit/generated.toml
uv run devkit generated resolve              # a merge, rebase or cherry-pick stopped: settle the generated conflicts
uv run devkit generated resolve --dry-run    # what resolve would settle; changes nothing
uv run devkit generated regen uv-lock        # rewrite uv-lock and the artifacts after it, in place
uv run devkit generated check                # CI: exit 1 when a committed generated file is out of date
uv run devkit generated check --rev origin/main
```

Every command takes `-w/--workspace-root` (default: the devkit project containing the current directory), `--format text|json` and the shared output options. Paths in results are relative to the top level of the work tree.

## Output

```text
[GENERATED: devkit-receipt source=builtin seed=ours paths=.devkit/installation.json command="{devkit} sync"]
[GENERATED: uv-lock source=project seed=ours paths=uv.lock command="uv lock && uv sync"]
[GENERATED_RESOLVED: uv-lock conflicts=1 changed=1]
[GENERATED_RESOLVED: devkit-receipt conflicts=0 changed=1]
[SUMMARY: operation=merge artifacts=2 remaining=0 dry_run=no]
[NEXT_CMD: git merge --continue]
[GENERATED_REGENERATED: uv-lock changed=1]
[SUMMARY: regenerated=2 changed=1 skipped=0]
[GENERATED_STALE: uv-lock changed=1]
[SUMMARY: commit=1a2b3c4d5e6f checked=2 stale=1 skipped=0]
```

- `list`: one `[GENERATED: ...]` line per artifact, in run order. `source` is `builtin` for an artifact of `builtin.toml`, also when the project changes it.
- `resolve`: `GENERATED_PLANNED` replaces `GENERATED_RESOLVED` under `--dry-run`. `conflicts` counts the owned conflicts settled and `changed` the files the command changed. An optional artifact with nothing tracked is skipped and logged (`-v`), not printed. `operation` is `merge`, `rebase`, `cherry-pick`, `revert`, `am` or `-`. `[NEXT_CMD: ...]` appears only when no conflict remains and the operation is known.
- `regen` and `check`: one line per artifact that changed (`regen`) or is stale (`check`); unchanged, current and skipped artifacts are `-v` log lines that the `[SUMMARY]` counts. `changed` counts the files the command changed. For `check`, these are the files that differ from the commit.

JSON:
- `list`: `artifacts` (`id`, `paths`, `command`, `inputs`, `updates`, `after`, `seed`, `optional`, `builtin`).
- `resolve`: `operation`, `dry_run`, `artifacts` (`id`, `command`, `conflicts`, `changed`, `skipped`), `remaining`, `next_command`, `notices`.
- `regen`: `artifacts`.
- `check`: `artifacts`, `commit`, `stale` (ids), plus `errors` when stale.

## Configuration

`.devkit/generated.toml` (optional, Git-tracked) holds one `[artifacts.<id>]` table per artifact, with `paths`, `command`, `inputs`, `updates`, `after`, `seed`, `optional` and `enabled`. A table with a built-in id (`devkit-receipt`) changes only the keys it sets. See `CAP-GEN-tracked-artifacts`.

## Error codes

Exit codes: `0` success; `1` from `check` when an artifact is stale; `2` a refusal or an error. Warnings exit `0` (`1` under `--strict`).

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `GENERATED_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `GeneratedConfigError` | A malformed `.devkit/generated.toml`: an unknown key, a bad pattern, seed or id, a missing `paths` or `command`, an `after` naming an unknown artifact or forming a cycle, or a path two artifacts own. |
| `GENERATED_INPUTS_CONFLICTED` | `ERROR` (`INPUT_ERROR`) | `InputsConflictedError` | `resolve`: a conflict no artifact owns may be read by an artifact to regenerate. Nothing changed; `[TARGET]` lists the conflicted paths, the details their readers, `[FIX]` the exact `git add -- ...` and `uv run devkit generated resolve`. |
| `GENERATED_UNMERGED` | `ERROR` (`AUTO`) | `UnmergedError` | `regen` with unmerged paths in the index (`[TARGET]`); nothing ran. `[FIX]` is `uv run devkit generated resolve`. |
| `GENERATED_COMMAND_FAILED` | `ERROR` (`INPUT_ERROR`) | `CommandFailedError` | An artifact's command failed. `[TARGET]` is `.devkit/generated.toml`; the details carry its exit code, log path and last output lines; nothing was staged. |
| `GENERATED_OUTPUT_UNDECLARED` | `ERROR` (`INPUT_ERROR`) | `OutputUndeclaredError` | A command changed files outside its `paths` and `updates`. `[TARGET]` is `.devkit/generated.toml` and the undeclared files. The changes stay in the work tree; nothing was staged. |
| `GENERATED_STALE` | `ERROR` (`INPUT_ERROR`, exit `1`) | `StaleError` | `check`: artifacts differ from what their command produces at the commit. `[TARGET]` lists the stale files; `[FIX]` is the exact `uv run devkit generated regen` command for the stale ids, then commit. |
| `GENERATED_CONFLICTS_REMAIN` | `WARNING` | `ConflictsRemainWarning` | `resolve` settled the generated conflicts; conflicts no artifact owns remain (listed). |
| `CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_dist.base.errors.ConfigError` | `.devkit/generated.toml` cannot be read or is not valid TOML. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_core.base.errors.ArgumentError` | An unknown or disabled artifact id (`check` names one registered only in the working tree as not committed at `--rev`), or a `--rev` that is not a commit. |
| `GIT_FAILED` | `ERROR` | `devkit_core.base.errors.GitError` | Not in a Git work tree, or another Git command failed. |

## Library

```python
from devkit_agt.features.generated import check, load_registry, regenerate, resolve

registry = load_registry(project_root)       # Registry(artifacts); .get(id), .owner(path), .closure(ids)
result = resolve(project_root)               # ResolveResult(operation, artifacts, remaining, next_command, notices)
plan = resolve(project_root, dry_run=True)   # the same, with nothing changed
done = regenerate(project_root, ["uv-lock"]) # RunResult(artifacts)
report = check(project_root, rev="HEAD")     # RunResult(artifacts, commit); report.stale
```
