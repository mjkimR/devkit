# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests belong in each package's `tests/`, never under `src/`.
- `agent-rule-engine` is the agent-managed rule & governance engine:
  - Self-contained package providing both core evaluation library and `agent-rules` CLI entry point.
  - Uses unified in-memory `WorkspaceCache` for file reads, YAML frontmatter, markdown AST links, and catalog index.
  - Sequentially evaluates rules with convergence recheck after autofix.
  - Minimal dependencies (`click`, `pyyaml`).
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
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
