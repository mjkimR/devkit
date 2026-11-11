# devkit: Agent Guide

Personal developer tools monorepo: Python packages managed with `uv` workspaces and `just`.

## Guardrails

Checks here prevent accidental mistakes; deliberate bypass by the owner is outside the threat model. Add a check only
at the relevant boundary for a concrete failure with a meaningful consequence; protect secrets, destructive
operations and published compatibility contracts.

## Architecture

Read `ARCH-05-2-components` before adding a package, feature, layer or test tier; the `devkit-dev` rules enforce it.

- Sources live in `packages/<package>/src/` or `tools/<tool>/src/`; tests in each package's
  `tests/{unit,integration,e2e}/` mirroring source ownership, helpers in `tests/support/`, a rule's tests in
  `<rule>/tests/`.
- Each wheel owns its regular package (`devkit-agt` → `devkit_agt`, others by distribution name); `devkit-advisory`
  keeps the PEP 420 `devkit.advisory` namespace. No installed path belongs to two wheels.
- Behavior lives under `features/<feature>/` with only the layers it needs (`cli`, `mcp`, `usecases`, `services`,
  `repositories`, `models`); no package-level `core`, no logic in `__init__.py`. Feature edges are declared in
  `.devkit/architecture.toml` `feature_dependencies`; a payload delegating a cross-feature choice names them in its
  write scope or rules a new edge out.
- Exposed operations implement `devkit_core.base.usecase.BaseUseCase`; adapters call use cases, and services and
  repositories never import use cases or adapters.
- Never import `devkit_core.core` from `devkit_core.base`, an application package from `devkit-core`, `devkit_agt` or
  the MCP SDK from `devkit-dist` (`just test-dist` passes without `devkit-agt`), or `devkit_spec` from
  `devkit-adaptive`.
- Keep `justfile` recipes thin; shared shell logic goes in `scripts/`.

## Documentation

- `docs/capabilities/<area>/` is canonical for behavior, `docs/architecture/` for structure; keep
  `docs/development/reference/`, package READMEs, bundle guides and `guides/` in step with them.
- Write in English, except a non-`en` release handbook under `handbook/<lang>/`.
- Before editing a bundle's skill, playbook, instruction, guidance fragment or guide, run
  `uv run devkit get-context authoring` and apply `agent-asset-writing`.
- Never commit `.env` or log secrets or PII.

## Agent-First Design

The primary consumer is an AI coding agent. Before changing a command, library API or guide, follow
`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol` and `CAP-CLI-agent-cli-toolkit`; in short:

- stdout is the result: one-line `[KIND: ...]` sentinels or one JSON object. stderr carries advisory blocks, and
  `[INFO]` only under `-v`.
- Give everything an agent acts on a stable `UPPER_SNAKE` code and a deterministic `[ACTION]`; branch and test on
  codes, never on message text.
- Raise failures as `AdvisoryError`; return warnings under `notices`. Exit `0` success, `1` negative result, `2`
  could not run; warnings change it only under `--strict`.
- Default output carries only what changes the agent's next step; diagnostics go to `logging`. Libraries never
  print; commands write through `devkit_dist.adapters.cli`.

## Packages

`devkit-core` shared foundation · `devkit-dist` asset distribution and the `devkit` executable · `devkit-agt`
(`packages/devkit`) harness: rules, workflows, commit gates, worktrees, integration · `devkit-mcp` MCP transport ·
`devkit-cli` CLI boundary · `devkit-advisory` advisory library · `devkit-docs` document system · `devkit-spec`
spec-driven delivery · `devkit-adaptive` adaptive development · `devkit-catalog` opt-in bundles · `devkit-viewer`
Living Spec viewer · `devkit-starter` example content package. Each package's README describes its modules.

## Verification

Before completing code changes, run lint, type checks and `just test-affected` (keep its `mode=full` fallback); no
local full-suite run is required. A viewer frontend change also runs the command its `[FRONTEND_CHECK: ...]` line
names. Commands: [setup](docs/development/setup.md#3-common-verification-commands); integration, post-landing checks,
E2E and CI: [CI/CD](docs/development/ci-cd.md).

<!-- DEVKIT:START -->
## devkit

- Before using a bundle's assets, run `uv run devkit get-context <bundle>` once per agent context. Installed: `advisory`, `authoring`, `deep-research`, `devkit`, `devkit-dev`, `docs`, `harness`, `response-style`, `spec`.
- Never edit `.devkit/managed/` or projected agent files; change the source bundle or use `devkit override`.
- Before document work, run `uv run devkit get-context docs`.
- Before replying, read and apply the `response-style` skill: conclusion first, `→ **Core sentence.** Explanation` for ordinary points, required facts and formats kept, unfinished work and user decisions stated.
- Read `uv run devkit config show`: under sdd, run `uv run devkit get-context spec` and start work with `/spec <intent>`; each new task intake runs its intake step first. For adaptive-dev, use its guidance and independent checks without SDD records.

Managed by `devkit sync`; edit outside the markers only.
<!-- DEVKIT:END -->
