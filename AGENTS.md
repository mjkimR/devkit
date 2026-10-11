# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests belong in each package's `tests/`, never under `src/`.
- `agent-rule-engine` is the agent-managed rule & governance engine:
  - Self-contained package providing both core evaluation library and `agent-rules` CLI entry point.
  - Uses unified in-memory `WorkspaceCache` for file reads, YAML frontmatter, lightweight markdown link extraction, and catalog index.
  - Sequentially evaluates rules with convergence recheck after autofix.
  - Feature folders: `engine/`, `workspace/`, `cli/`, and `rules/{specification,markdown,hygiene}/`; tests mirror these groups outside `src/`.
  - Minimal dependencies (`click`, `pyyaml`).
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
- `devkit-distribution` provides the `devkit` CLI. Consumer projects install it
  and content wheels as uv dev dependencies, then run `uv run devkit sync`.
  Discover content through `devkit_distribution.bundles` module entry points;
  resources live under the module's `bundle/` with `bundle.toml`. Keep native
  bytes intact, protect unowned/edited files, and use `.devkit/` receipts.
  `devkit-starter` is the example resource package.
- Do not commit `.env`, log secrets/PII, or commit/push without explicit instructions.

## Verification

Run lint, type checks, and relevant tests before completing code changes:

| Target | Command |
| --- | --- |
| Lint & format | `just lint [module]` |
| Type check (Pyright) | `just check [module]` |
| Tests | `just test [module]` |
| Test Coverage | `just test-cov [module]` |
| Governance Rules | `just rules-check` or `just rules-fix` |
