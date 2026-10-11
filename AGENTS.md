# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests belong in each package's `tests/`, never under `src/`.
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
- Write all documentation, architecture specifications, and guide materials in English.
- Do not commit `.env`, log secrets/PII, or commit/push without explicit instructions.

## Packages

Keep package descriptions in this guide to a high-level summary of their purpose. Do not add package-specific configurations or detailed architectural explanations here; refer to the respective package's `README.md` when deeper details are needed:

- `agent-rule-engine`: Agent-managed rule and repository governance engine. See [packages/agent-rule-engine/README.md](packages/agent-rule-engine/README.md).
- `devkit-distribution`: CLI tool (`devkit`) and runtime for packaging and synchronizing agent asset bundles across workspaces. See [packages/devkit-distribution/README.md](packages/devkit-distribution/README.md).
- `devkit-starter`: Example resource package demonstrating bundle packaging and distribution. See [packages/devkit-starter/README.md](packages/devkit-starter/README.md).

## Verification

Run lint, type checks, and relevant tests before completing code changes:

| Target | Command |
| --- | --- |
| Lint & format | `just lint [module]` |
| Type check (Pyright) | `just check [module]` |
| Tests | `just test [module]` |
| Test Coverage | `just test-cov [module]` |
| Governance Rules | `just rules-check` or `just rules-fix` |
