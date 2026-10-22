---
name: testing
description: Read before authoring, moving or organizing workspace tests across unit, integration and e2e tiers.
---

# Testing Tiers and Boundaries

Put a package's tests in its `tests/{unit,integration,e2e}/` tiers, creating only the tiers it needs. Classify each
test by its execution boundary, not by whether the package is an application.

## Unit (`tests/unit/`)

- Scope: pure domain logic, model validation, parsing, scoring algorithms, formatters and in-memory transformations.
- Use no disk I/O, Git, subprocess or network; substitute in-memory doubles, so hundreds of tests finish in 1-2
  seconds without parallel workers.
- Example: `packages/devkit-core/tests/unit/core/test_frontmatter.py` parses Markdown frontmatter.

## Integration (`tests/integration/`)

- Scope: in-process collaboration of use cases, services, repositories and transport adapters, within or across
  features.
- Read and write real files under `tmp_path` (configuration, receipts, envelopes) and invoke CLI commands through
  `click.testing.CliRunner().invoke()`.
- Spawn no `devkit` or Python process and run no Git hook. Keep Git to the few commands a fixture repository needs,
  not a full repository lifecycle.
- Example: a use case orchestrates its services and returns structured output and notices, asserted through
  `CliRunner`.

## End-to-end (`tests/e2e/`)

- Scope: out-of-process execution (`subprocess.run(["devkit", ...])`, `python -m ...`), OS Git hooks, multi-branch
  worktree lifecycles, full spec workflows from `devkit spec new` to rule audit, and MCP protocol confirmation.
- Example: `packages/devkit/tests/e2e/features/gate/test_hooks.py` runs a real `git commit` that triggers the
  commit-msg hook in a separate interpreter.

## Layout

- Under each tier, mirror source ownership (`tests/unit/features/<feature>/`, `tests/integration/package/`,
  `tests/unit/core/`); create no empty directories.
- Put package-specific fixtures and helpers in that package's `tests/support/` (for example
  `packages/devkit-spec/tests/support/spec_support/`). If a helper is needed by several packages, put it in
  `devkit_dev.testing`.
- Keep a governance rule's tests beside the rule in `rules/<rule>/tests/test_rule.py`.
- Keep installed-wheel cross-package checks under `scripts/`.

## Running tests

- During development, run `just test-affected`: it selects the affected unit and integration tests from the diff
  against the base, and adds e2e tests when an e2e test changed or `--e2e` is passed.
- Before integration approval, or when a change touches an end-to-end flow, run `just test-e2e [module]` or
  `just test-affected --e2e`.
- `just test [module]` runs every tier with parallel workers; it is the nightly, release and fallback suite.

## Completion

Each new or moved test sits in the tier its execution boundary names, and `just test-affected` passes.
