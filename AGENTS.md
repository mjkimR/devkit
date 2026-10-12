# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests belong in each package's `tests/`, never under `src/`.
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
- Inside `packages/devkit`, lower modules never import higher ones (`core` < `advisory` < `rules` < `workflow`/`gate`; `distribution` uses only `core` and `advisory`); a test enforces the layering.
- `docs/<area>/` is canonical for each module's semantics; `docs/<area>/reference.md` and package READMEs stay quick references that link there, and the bundled guide instructions are consumer-facing mirrors kept in step.
- Write all documentation, architecture specifications, and guide materials in English.
- Do not commit `.env`, log secrets/PII, or commit/push without explicit instructions.

## Compatibility

- No external consumers exist yet. Breaking changes to schemas (`bundle.toml`, `.devkit/config.toml`, `.devkit/installation.json`), CLI commands, and APIs may be made in place: do not bump schema versions or add migration paths, deprecation shims, or legacy readers.
- Once a real consumer exists, delete this section and treat these formats as versioned contracts that require migrations.

## Packages

Keep package descriptions in this guide to a high-level summary of their purpose. Do not add package-specific configurations or detailed architectural explanations here; refer to the package README and `docs/<area>/` when deeper details are needed:

- `devkit`: The single devkit package with one CLI (`devkit`): agent asset distribution, repository rules, delivery workflows, commit gates and structured agent errors, built on an SDD-agnostic shared core. See [packages/devkit/README.md](packages/devkit/README.md) for its modules and layering.
- `devkit-starter`: Example external content package demonstrating bundle packaging and distribution. See [packages/devkit-starter/README.md](packages/devkit-starter/README.md).

## Verification

Run lint, type checks, and relevant tests before completing code changes:

| Target | Command |
| --- | --- |
| Lint & format | `just lint [module]` |
| Lint & format check (CI) | `just lint-check [module]` |
| Type check (Pyright) | `just check [module]` |
| Tests | `just test [module]` |
| Test Coverage | `just test-cov [module]` |
| Governance Rules | `just rules-check` or `just rules-fix` |
| Consumer smoke (packaging, CLI wiring, hooks) | `just smoke` |
