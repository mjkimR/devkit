---
id: ADR-scope-snapshot-runs-to-diff-paths-including-deletions
title: Scope snapshot runs to diff paths including deletions
summary: For evaluating rules on Git snapshots, we match declared rule inputs against diff paths including deletions in scope_rules, to cut commit gate latency without missing deletion-induced violations, accepting that snapshot runs no longer catch latent violations outside touched paths.
proposal: SPEC-snapshot-scoped-rules
supersedes:
  - ADR-scope-only-explicit-working-tree-targets-in-the-evaluator
status: accepted
created_at: 2026-10-22
---

# [ADR-scope-snapshot-runs-to-diff-paths-including-deletions] Scope snapshot runs to diff paths including deletions

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

`ADR-scope-only-explicit-working-tree-targets-in-the-evaluator` introduced rule target scoping for working-tree targeted runs
(`lint-clean`, `devkit rules check <files>`), but kept snapshot runs whole-workspace because deleted files were not targets.
The follow-up explicitly named scoping snapshot runs when the commit gate cost became a measured problem.

Empirical measurements on this repository show an in-place staged snapshot run (`devkit rules check --staged`) takes 4.49 s on a
documentation edit, spending ~2.93 s on whole-workspace Python AST evaluation for files the commit cannot affect.

## 2. Decision Drivers

- The `rules-check` pre-commit gate and branch snapshot runs must not spend time evaluating whole-workspace rules whose declared inputs are unaffected by the commit.
- Deletion-only changes and file renames must never skip rules whose inputs match the removed path (e.g. deleting a Python file must trigger `RULE-architecture` to check for broken imports).
- Scoping candidate paths must be decoupled from `RuleContext.targets`: non-existent deleted files cannot be treated as evaluation targets.
- Project configuration (`.devkit/config.toml`) and installation receipt (`.devkit/installation.json`) changes must evaluate every rule.
- Full workspace CI runs (`just rules-check` in `.github/workflows/ci.yml`, nightly, and release) continue to act as an unscoped safety net.

## 3. Considered Options

1. **Keep snapshot runs unscoped (status quo)**: Keeps every gate complete before Git history, but every commit pays ~4.5 s regardless of touched files.
2. **Scope snapshot runs matching only `snapshot.changed`**: Avoids evaluating rules when `changed` does not match, but a deletion-only change to Python would skip `RULE-architecture`, hiding broken imports.
3. **Decouple scoping paths from evaluation targets and match diff paths including deletions**:
   - `RuleContext.targets` retains only existing regular files in the snapshot tree (`snapshot.changed` plus inbound Markdown linkers).
   - `scope_rules` constructs candidate names from `ctx.targets` plus `snapshot.deleted` and any non-regular diff paths (e.g. typechanges).
   - `RunProjectRulesUseCase._run` computes `has_work = bool(targets or (snapshot and snapshot.deleted))` so deletion-only commits do not short-circuit before rule loading.
   - Touching `.devkit/config.toml` (`CONFIG_PATH`) or `.devkit/installation.json` (`RECEIPT_PATH`) disables rule skipping.

## 4. Decision Outcome

Chosen: **Option 3: Decouple scoping paths from evaluation targets and match diff paths including deletions**.

- **Scoping matching**: In `scope_rules(ctx, rules, modified)`, when `ctx.snapshot is not None`, `names` includes `ctx.targets` plus `ctx.snapshot.deleted`. Rules declaring `inputs` that match none of `names` are skipped and recorded on `EvaluationResult.skipped`.
- **Decoupled evaluation targets**: `RuleContext.targets` continues to hold only existing files in the snapshot workspace. Target-only rules (e.g. `RULE-secret-leak`) inspect only present files.
- **Engine lifecycle fix**: `has_work` in `RunProjectRulesUseCase._run` considers `snapshot.deleted`, ensuring deletion-only commits initialize `RuleContext` and invoke `evaluate_rules`.
- **Receipt and config protection**: If `CONFIG_PATH` or `RECEIPT_PATH` is in `names`, no rules are skipped.
- **Reporting**: Follows the existing agent-first convention: skipped rules are returned on `EvaluationResult.skipped` and logged at `INFO` under `-v`; stdout and JSON summaries remain clean and unchanged.

## 5. Consequences

- Positive: `rules-check` pre-commit gate latency on documentation/asset commits drops from ~4.49 s to ~1.56 s (~65 % reduction, saving ~2.93 s per commit).
- Positive: deletion-only and rename commits accurately trigger rules matching the removed paths.
- Negative: like working-tree targeted runs, snapshot runs no longer detect latent violations in untouched files; whole-workspace CI and nightly checks remain the safety net.
- Supersedes: the follow-up section of `ADR-scope-only-explicit-working-tree-targets-in-the-evaluator`.

## 6. Confirmation

- Unit tests in `packages/devkit/tests/unit/features/rules/engine/test_scoping.py`:
  - Snapshot with only `.md` changes skips `RULE-architecture` and `RULE-usecase-boundaries`.
  - Snapshot with added or modified `.py` evaluates Python rules.
  - Snapshot with deleted `.py` evaluates Python rules.
  - Snapshot with `.devkit/config.toml` or `.devkit/installation.json` evaluates all rules.
  - Non-existent deleted paths are absent from `ctx.targets`.
- Integration tests in `packages/devkit/tests/integration/features/rules/engine/test_project.py`:
  - Deletion-only commit evaluates matching rules without short-circuiting in `_run`.
- Measured pre-commit gate speedup verified before and after on this repository.
