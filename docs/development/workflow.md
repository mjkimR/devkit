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
3. `just test-affected` (or `just test <module> <area...>`) passes the tests the change can affect; the full
   `just test` passes once on the reviewed head before integration.
4. `just rules-check --staged` reports 0 governance violations.
