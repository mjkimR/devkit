# Development Workflow

Guidelines and conventions for branching, development cycles, and commit quality in devkit.

## 1. Branching & Activity Flow

- Feature and maintenance activities should run on isolated activity branches:
  - `dev-<slug>`: Code changes and feature implementations.
  - `plan-<slug>`: Architectural proposals and design incubation.
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
   Before integration, `just test-affected --base <base-ref>` verifies the final content after incorporating a moved
   base and resolving conflicts. Keep its full-suite fallback and frontend checks. Reuse this result after merging
   unchanged verified content; no separate local full-suite or post-merge test run is required. Complete CI runs
   overnight for unverified default-branch heads and before release (`ADR-nightly-ci-verification`).
4. `just rules-check --staged` reports 0 governance violations.
