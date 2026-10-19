# devkit.generated

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
[GENERATED_CURRENT: devkit-receipt changed=0]
[SUMMARY: commit=1a2b3c4d5e6f checked=2 stale=1 skipped=0]
```

- `list`: one `[GENERATED: ...]` line per artifact, in run order. `source` is `builtin` for an artifact of `builtin.toml`, also when the project changes it.
- `resolve`: `GENERATED_PLANNED` replaces `GENERATED_RESOLVED` under `--dry-run`. `conflicts` counts the owned conflicts settled and `changed` the files the command changed. `GENERATED_SKIPPED` marks an optional artifact with nothing tracked. `operation` is `merge`, `rebase`, `cherry-pick`, `revert`, `am` or `-`. `[NEXT_CMD: ...]` appears only when no conflict remains and the operation is known.
- `regen` and `check`: `changed` counts the files the command changed. For `check`, these are the files that differ from the commit.

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
| `GENERATED_INPUTS_CONFLICTED` | `ERROR` (`BLOCKED`) | `InputsConflictedError` | `resolve`: a conflict no artifact owns may be read by an artifact to regenerate. Nothing changed; the details list each path and its readers. |
| `GENERATED_UNMERGED` | `ERROR` (`BLOCKED`) | `UnmergedError` | `regen` with unmerged paths in the index; nothing ran. |
| `GENERATED_COMMAND_FAILED` | `ERROR` (`MAINTENANCE`) | `CommandFailedError` | An artifact's command failed. The details carry its exit code, log path and last output lines; nothing was staged. |
| `GENERATED_OUTPUT_UNDECLARED` | `ERROR` (`MAINTENANCE`) | `OutputUndeclaredError` | A command changed files outside its `paths` and `updates`. The changes stay in the work tree; nothing was staged. |
| `GENERATED_STALE` | `ERROR` (`MAINTENANCE`, exit `1`) | `StaleError` | `check`: artifacts differ from what their command produces at the commit; `[FIX]` is `devkit generated regen <ids>`, then commit. |
| `GENERATED_CONFLICTS_REMAIN` | `WARNING` | `ConflictsRemainWarning` | `resolve` settled the generated conflicts; conflicts no artifact owns remain (listed). |
| `CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit.core.ConfigError` | `.devkit/generated.toml` cannot be read or is not valid TOML. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit.core.ArgumentError` | An unknown or disabled artifact id (`check` names one registered only in the working tree as not committed at `--rev`), or a `--rev` that is not a commit. |
| `GIT_FAILED` | `ERROR` | `devkit.core.GitError` | Not in a Git work tree, or another Git command failed. |

## Library

```python
from devkit.generated import check, load_registry, regenerate, resolve

registry = load_registry(project_root)       # Registry(artifacts); .get(id), .owner(path), .closure(ids)
result = resolve(project_root)               # ResolveResult(operation, artifacts, remaining, next_command, notices)
plan = resolve(project_root, dry_run=True)   # the same, with nothing changed
done = regenerate(project_root, ["uv-lock"]) # RunResult(artifacts)
report = check(project_root, rev="HEAD")     # RunResult(artifacts, commit); report.stale
```
