# devkit: Agent Guide

Personal developer tools monorepo: Python packages managed with `uv` workspaces and `just`.

## Architecture and Boundaries

`ARCH-05-2-components` is the contract for package layout, layering and test layout; the repository-owned
`devkit-dev` rules (`RULE-usecase-boundaries` and the structure rules) enforce it. Read it before adding a
package, feature, layer or test tier. The rules agents most often need:

- Sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests in each package's
  `tests/{unit,integration,e2e}/`, mirroring source ownership, with helpers in `tests/support/`. A rule's tests
  live in `<rule>/tests/` (`CAP-GOV-rule-authoring`).
- Each wheel owns its own regular package (`devkit-dist` → `devkit_dist`, `devkit-agt` → `devkit_agt`, others by
  distribution name); `devkit-advisory` keeps the PEP 420 `devkit.advisory` namespace (no
  `src/devkit/__init__.py`). No installed path belongs to two wheels.
- Behavior lives under `features/<feature>/` with only the layers it needs (`cli`, `mcp`, `usecases`, `services`,
  `repositories`, `models`); no package-level `core`. Business logic stays out of `__init__.py`.
- CLI/MCP/HTTP-exposed operations implement `devkit_core.base.usecase.BaseUseCase` with a typed `execute`.
  Adapters call use cases; services and repositories never import use cases or adapters.
- `devkit_core.base` never imports `devkit_core.core`; `devkit-core` imports no application package.
  `devkit-dist` never imports `devkit_agt` or the MCP SDK, and its tests pass without `devkit-agt` (`just test-dist`).
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.

## Documentation

- `docs/capabilities/<area>/` is canonical for behavior and `docs/architecture/` for structure;
  `docs/development/reference/`, package READMEs and bundled guide instructions are quick references kept in
  step with them. `guides/` holds the consumer agents' installation guides: keep their commands, codes and bundle
  recommendations in step with `docs/` and the packages.
- Write documentation in English. The one exception is the release handbook's `handbook/<lang>/` for a language
  other than `en` (`ADR-localized-handbook-language-exception`).
- Do not commit `.env` or log secrets/PII.

## Agent-First Design

`devkit`'s primary consumer is an AI coding agent. Every command, library API and guide follows
`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol` and `CAP-CLI-agent-cli-toolkit`; in short:

- stdout is the result: one-line `[KIND: ...]` sentinels, or exactly one JSON object under `--format json` or from
  a JSON-only command (`ARCH-08-1`). Nothing terminal-dependent.
- stderr carries Agent Advisory Protocol blocks, plus `[INFO]` lines only under `-v`.
- Everything an agent must act on has a stable `UPPER_SNAKE` code and a deterministic `[ACTION]`; branch and test
  on codes, never on message text.
- Failures are raised as `AdvisoryError`; a successful operation returns warnings and notices under `notices`.
  Exit codes: `0` success, `1` negative result, `2` could not run; warnings change them only under `--strict`.
- Default output carries only what changes the agent's next step; diagnostics are `logging` calls.
- Libraries never print: commands write through `devkit_dist.adapters.cli`.

## Compatibility

- No external consumers exist yet: schemas (`bundle.toml`, `.devkit/config.toml`, `.devkit/installation.json`),
  CLI commands and APIs change in place, without version bumps, migrations, shims or legacy readers. Delete this
  rule once a real consumer exists.
- Exception: `devkit-advisory` (`devkit.advisory`) and `devkit-cli` (`devkit_cli`) have runtime consumers in other
  repositories and are semver contracts: within `0.x` a breaking change needs a minor bump, released in lockstep
  with `devkit-dist` and `devkit-agt` (`ARCH-07-deployment`).

## Packages

Each package's README describes its modules; `docs/capabilities/<area>/` holds the contracts.

| Package | Purpose |
| --- | --- |
| `devkit-core` | Shared foundation without CLI or application dependencies |
| `devkit-dist` | Agent asset distribution and the `devkit` executable |
| `devkit-agt` (`packages/devkit`) | Developer harness: rules, workflows, commit gates, worktrees, integration |
| `devkit-mcp` | Optional MCP transport and registration provider |
| `devkit-cli` | Agent-first command-line boundary (`devkit_cli`) |
| `devkit-advisory` | Agent Advisory Protocol library (`devkit.advisory`) |
| `devkit-docs` | Document system: document model, `devkit docs` commands, document rules |
| `devkit-spec` | Spec-driven delivery commands and agent assets |
| `devkit-starter` | Example external content package |
| `devkit-catalog` | Opt-in content bundles |
| `devkit-viewer` | Local read-only Living Spec viewer and its Svelte library |

## Verification

Run lint, type checks and relevant tests before completing code changes. Use `just test-affected` for
development, review and the final integration content (keep its `mode=full` fallback); no separate local
full-suite run is required. Incorporate a moved base before testing; merging unchanged verified content needs no
new run. Full CI runs nightly (04:17 Asia/Seoul, when the default branch changed), at release and on demand. A
viewer frontend change selects no pytest test: run the command its `[FRONTEND_CHECK: ...]` line names.

| Target | Command |
| --- | --- |
| Lint & format / check (CI) | `just lint [module]` / `just lint-check [module]` |
| Type check (Pyright) | `just check [module]` |
| Tests | `just test-affected`, `just test <module> [area\|path...]`, full: `just test` |
| devkit-dist without devkit-agt | `just test-dist` |
| Coverage | `just test-cov [module] [area\|path...]` |
| Governance rules | `just rules-check` / `just rules-fix` |
| Consumer smoke (packaging, CLI wiring, hooks) | `just smoke` |
| Viewer frontend (needs Node; rebuild the committed page after a change) | `just viewer lint\|check\|test\|build` |

<!-- DEVKIT:START -->
## devkit

This repository installs agent assets with `devkit`. `.devkit/config.toml` selects
bundles; `.devkit/installation.json` records what is deployed.

- Before work that touches a bundle's assets, run `uv run devkit get-context <bundle>` once per bundle in the current agent context. Installed bundles: `advisory`, `authoring`, `devkit`, `devkit-dev`, `harness`, `response-style`, `spec`.
- Entry skill `devkit-playbook`: find and run an operational playbook the user invokes or confirms.
- Entry skill `devkit-workflow`: diagnose and follow the delivery workflow stage of a work unit.
- Never edit `.devkit/managed/` or projected agent files; change the source bundle or use `devkit override`.
- Before replying, read and apply the `response-style` skill. Put the conclusion in the first sentence. Use `→ **Core sentence.** Explanation` for ordinary points; preserve required facts and formats, and make unfinished work and necessary user decisions clear.
- Before any development work, run `uv run devkit get-context spec` once per agent context and follow it. Start work with `/spec <intent>`; each new task intake runs its intake step first; `/spec-next` orients. `docs/` is the current-state Living Spec, `specs/` holds feature specs.

This block is managed by `devkit sync`; edit outside the markers only.
<!-- DEVKIT:END -->
