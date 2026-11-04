# Development Workflow

Guidelines and conventions for branching, development cycles, and commit quality in devkit.

## 1. Branching & Activity Flow

- Feature and maintenance activities should run on isolated activity branches:
  - `dev-<slug>`: Code changes and feature implementations.
  - `plan-<slug>`: Architectural proposals and their Planning.
- Activities can use task worktrees allocated via `devkit worktree start <branch>`.

## 2. Commit Message Standards

Follow concise, imperative, emoji-free commit messages:

- Format: `<type>(<scope>): <imperative summary>`
- Examples:
  - `feat(rules): add markdown table alignment rule`
  - `fix(sync): handle symlink resolution in workspace root`
  - `docs(arch): update C4 container diagram`

## 3. Pre-Commit Verification

Before committing changes, ensure that:
1. `just lint` applies clean formatting.
2. `just check` passes with 0 Pyright errors.
3. During development, `just test-affected` or `just test <module> <area...>` passes the affected tests.
   Automatic selection uses individual test files, devkit area nodes and module-level devkit_spec dependencies;
   helper/conftest imports and conservative full fallbacks remain part of selection. Other packages retain coarse
   ownership by default. Complete nightly/manual/release checks cover runtime dependencies static analysis misses.
   Before integration, verify the branch and save the target SHA before the first merge. After landing, synchronize
   dependencies with `just init` and use fresh processes for sync, generated-artifact checks and regeneration.
   Commit generated/repair changes, then run `just test-affected --base <saved-target-sha>` against the final target
   HEAD, preserving full fallback and frontend checks. Batch units remain pending until this combined head passes.
   Repair and recheck failures on the target; do not replay merges or automatically roll back. Report the tested
   HEAD, commands and outcomes (`ADR-post-merge-verification`). Nightly/release CI remains the full-suite backstop.

4. `just rules-check --staged` reports 0 governance violations.
