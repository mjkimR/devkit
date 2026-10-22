# Spike evidence: snapshot-scoped rules

Measured on `plan-snapshot-scoped-rules` at `56568864` (Linux, Python 3.12, this repository with ~820 tracked Python files).

## 1. Baseline: In-place `--staged` Commit Gate vs Scoped targeted runs

Currently, snapshot runs (`devkit rules check --staged`, `devkit rules check --ci`) bypass `scope_rules` because `ctx.snapshot is not None`. Every active rule evaluates even when a commit only touches documentation.

Timing measured across 3 runs on a staged documentation edit in place (`matches_working_tree` is True, 0 s materialization):

| Run kind | Command | min | median | Notes |
| --- | --- | --- | --- | --- |
| In-place staged (`--staged`) | `uv run devkit rules check --staged` | 4.434 s | 4.492 s | Evaluates all rules (architecture, usecase boundaries, unique code) |
| Scoped working-tree | `uv run devkit rules check docs/proposals/PROP-snapshot-scoped-rules/proposal.md` | 1.547 s | 1.561 s | Skips `RULE-advisory-unique-code`, `RULE-architecture`, `RULE-usecase-boundaries` |
| Materialized snapshot (`--ci`) | `uv run devkit rules check --ci --base HEAD~1` | 4.980 s | 5.026 s | Materializes tree + full unscoped evaluation |

**Net saving**: ~2.93 s rule execution saving (65 % reduction) right at the pre-commit gate (`rules-check` hook) on non-Python commits, proving the cost is rule evaluation rather than Git materialization.

## 2. Spike Q1: Snapshot path coverage and rule dependencies

### Path capture in `git_snapshot`
`git_snapshot` uses `_changes(root, prior, tree)` running `git diff --name-status -z --no-renames prior tree`:
- Added (`A`) and modified (`M`) regular files: captured in `snapshot.changed` (present in tree).
- Mode changes (`chmod +x`): status `M`, captured in `snapshot.changed`.
- Deleted files (`D`): captured in `snapshot.deleted`.
- Renames: due to `--no-renames`, a rename from `old` to `new` decomposes into `D old` (in `snapshot.deleted`) and `A new` (in `snapshot.changed`). Both paths are captured.
- Typechanges (`T`, e.g. file replaced by symlink or submodule): must be retained in snapshot change paths so rule scoping treats them as changed inputs.
- Markdown referrers: `snapshot_targets` inspects all Markdown files in the snapshot workspace and includes any file whose relative links point to a path in `snapshot.deleted` (or a parent directory that lost files).

### Scoping paths vs target paths separation
- **Targets for evaluation** (`RuleContext.targets`): must only contain regular files present in the snapshot workspace (`snapshot.changed` + referring Markdown files). Deleted paths must not be targets, as they do not exist on disk and file-reading rules would fail.
- **Paths for scoping rule matching** (`names` in `scope_rules`): must include `ctx.targets` PLUS `snapshot.deleted` and typechanges. If `old.py` is deleted, its deletion matches `**/*.py` and triggers `RULE-architecture` and `RULE-usecase-boundaries`.
- **Engine short-circuit fix**: `RunProjectRulesUseCase._run` must not short-circuit when only deletions occur (`has_work = bool(targets or (snapshot and snapshot.deleted))`), ensuring whole-workspace rules evaluate when a Python file is deleted without additions.
- **Special configuration paths**:
  - `.devkit/config.toml`: already present in `scope_rules` (`CONFIG_PATH in names` disables skipping).
  - `.devkit/installation.json` (`RECEIPT_PATH`): receipt changes alter loaded rule definitions, so its presence in `names` also disables skipping.

### Rule input completeness
The declared rules (`RULE-architecture`, `RULE-usecase-boundaries`, `RULE-advisory-unique-code`) each carry automated tests using `opened_files` verifying that every workspace file read matches their declared `inputs` (`**/*.py`, `**/pyproject.toml`, `**/bundle.toml`, `.devkit/architecture.toml`). Any change to these files appears in Git's diff (`changed` or `deleted`). No declared rule depends on an uncaptured file.

## 3. Spike Q2: Safety-net CI runs and reporting

### CI safety net
- In `.github/workflows/ci.yml`, the workspace job runs `just rules-check` without arguments. This is a full-workspace evaluation without snapshot or targets, running every active rule across Linux and macOS.
- Nightly and release workflows run full CI.
- Thus, a whole-workspace safety net already exists in CI. `check --staged` (commit gate) and `check --ci --base <ref>` (branch / reverify check) evaluate what the commit/branch changes.

### Reporting convention
- Follows `SPEC-lint-clean-target-scoped-rules`:
  - Skipped rule IDs are returned on `EvaluationResult.skipped` and `ProjectRun.skipped`.
  - Logged at `INFO` (visible under `-v`).
  - Agent-facing stdout (`[SUMMARY: ...]`, `[OK: ...]`) and JSON remain concise and unchanged when rules are skipped.
