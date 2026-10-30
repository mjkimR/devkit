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
   Before integration, `just test-affected --base <base-ref>` verifies the task branch; a conflict-free moved base
   needs no merge or rerun, because integration checks the CI rules on the merged result. Keep its full-suite
   fallback and frontend checks. After a local-orchestrated run, `devkit generated check` runs on `main` (stale
   artifacts are regenerated with `devkit generated regen <ids>` and committed), then `just test-affected --base
   <batch start>` runs once on `main`; otherwise a later batch run or nightly CI tests the combined head
   (`ADR-post-batch-test-run`). Complete CI runs overnight for unverified default-branch heads and before release
   (`ADR-test-selection-and-ci`).
4. `just rules-check --staged` reports 0 governance violations.
