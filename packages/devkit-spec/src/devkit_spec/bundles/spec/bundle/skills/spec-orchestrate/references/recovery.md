# Context loss and returning to direct

## After context loss

- Rebuild state from `devkit worktree status`, `devkit spec scope collect` and per-unit `devkit workflow next --unit <dir>`.
- Recover the batch start from the first parent of the earliest merge in this run; when unclear, use the selector's full fallback.

## Returning to direct

Stop starting workers, validate running ones' results and continue the remaining units one at a time.
