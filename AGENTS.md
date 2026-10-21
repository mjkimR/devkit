# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/` (`models/devkit-embed` is a data package outside the workspace, built by hand); tests belong in each package's `tests/`, never under `src/`, except a rule's own tests, which travel with it in its folder (`<rule>/tests/`, `CAP-GOV-rule-authoring`).
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
- Each application wheel owns an independent regular Python package: `devkit-dist` owns `devkit_dist`, `devkit-agt` owns `devkit_agt`, and the other application packages use their distribution name with underscores. `devkit-advisory` preserves the public `devkit.advisory` API in its PEP 420 namespace; do not add `src/devkit/__init__.py` there. No installed path belongs to two wheels.
- `devkit-core` owns the independent `devkit_core` package: generic filesystem/Git/parsing/plugin primitives, logging and extension dispatch under `core`, shared errors and SDK-free MCP contracts under `base`. `base` never imports `core`. It depends only on `devkit-advisory` and PyYAML; never import application packages from it.
- Application packages organize behavior under `features/<feature>/`, with `cli`, `mcp`, `usecases`, `services`, `repositories` and `models` added when needed as modules or directories. Package-level `base` holds shared contracts and `utils` holds technical helpers; create neither until needed, and do not create package-level `core`. Shared transport adapters require an explicit package declaration; dist owns `adapters/cli.py` for its common CLI boundary. Bundle-only packages may keep only `bundle/`. `devkit_core` is the foundation exception with `base/` and `core/`.
- CLI and MCP adapters expose use cases. Use cases coordinate services and repositories; services and repositories never import use cases or adapters. Models and package base contracts never import higher layers. Feature dependencies must follow their declared direction; optional providers are discovered through the existing entry-point groups. The repository-owned `devkit-dev` bundle checks layout and layer boundaries; package tests cover their feature dependency graph.
- `devkit-dist` never imports `devkit_agt` or the MCP SDK. `devkit-agt` mounts its commands through `devkit.commands` entry points; `devkit-dist` owns the `devkit` executable. The `devkit-dist` tests also run without `devkit-agt` installed (`just test-dist`).
- `guides/` holds the agent-facing installation guides a consumer's agent follows from a GitHub link; keep their commands, codes and bundle recommendations in step with `docs/` and the packages.
- `docs/capabilities/<area>/` is canonical for each module's behavior, and `docs/architecture/` defines system structure; `docs/development/reference/<module>.md` and package READMEs stay quick references that point to those contracts, and the bundled guide instructions are consumer-facing mirrors kept in step.
- Write all documentation, architecture specifications, and guide materials in English.
- Do not commit `.env` or log secrets/PII.

## Agent-First Design

`devkit`'s primary consumer is an AI coding agent that runs it through a shell or tool call and acts on what comes back. People read the same output, but nothing is shaped for them at the agent's expense. Apply this to every command, library API and guide:

- **stdout is the result**: one-line `[KIND: ...]` sentinels, or exactly one JSON object under `--format json`. No colour, emoji, tables, progress output or anything that depends on the terminal.
- **stderr is for advisories**: Agent Advisory Protocol blocks (`[ERROR]`, `[WARN]`, `[NOTICE]`), plus `[INFO]` log lines only under `-v`. Advisory sentinel names are never stdout kinds.
- **Codes and directives**: everything an agent must act on has a stable `UPPER_SNAKE` code and a deterministic `[ACTION]` directive. Branch and test on codes, never on message text; never write hedged directives ("likely", "might").
- **Levels**: a failure or refusal is raised as an `AdvisoryError`; something a successful operation must report is returned with its result under `notices` at `WARNING` or `NOTICE`, never raised and never logged. Warnings and notices do not change exit codes (`0` success, `1` negative result, `2` could not run), except under `--strict`.
- **Context budget**: default output carries only what changes the agent's next step or must reach the user. Diagnostics are `logging` calls, visible under `-v`.
- **Libraries never print**: commands write output only through `devkit_dist.adapters.cli` (`boundary`, `echo_json`, `echo_notices`, `exit_on_warnings`).
- Specifications: `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`.

## Compatibility

- No external consumers exist yet. Breaking changes to schemas (`bundle.toml`, `.devkit/config.toml`, `.devkit/installation.json`), CLI commands, and APIs may be made in place: do not bump schema versions or add migration paths, deprecation shims, or legacy readers.
- Once a real consumer exists, delete this section and treat these formats as versioned contracts that require migrations.
- Exception: `devkit-advisory` (the `devkit.advisory` API) already has runtime consumers in other repositories. Treat it as a semver contract: within `0.x`, a breaking change needs a minor version bump, released in lockstep with `devkit-dist` and `devkit-agt`.

## Packages

Keep package descriptions in this guide to a high-level summary of their purpose. Do not add package-specific configurations or detailed architectural explanations here; refer to the package README and `docs/capabilities/<area>/` when deeper details are needed:

- `devkit-core`: Shared foundation without CLI or application dependencies. See [packages/devkit-core/README.md](packages/devkit-core/README.md).
- `devkit-dist`: Agent asset distribution with the `devkit` CLI: bundles, agent projections, sync, context loading, playbooks and native hooks, using `devkit-core` and its own project configuration and receipt contracts. See [packages/devkit-dist/README.md](packages/devkit-dist/README.md) for its modules and layering.
- `devkit-agt`: The developer harness mounted under `devkit`: repository rules, delivery workflows, commit gates, task worktrees, generated files, integration and compact command output; depends on `devkit-dist`. See [packages/devkit/README.md](packages/devkit/README.md) for its modules and layering.
- `devkit-mcp`: Optional MCP transport, native forms and retained-runtime registration provider; domain services stay in their packages. See [packages/devkit-mcp/README.md](packages/devkit-mcp/README.md).
- `devkit-advisory`: The Agent Advisory Protocol library (`devkit.advisory`) on its own, for other repositories' runtime; `devkit-dist` and `devkit-agt` depend on the same version (the three are released in lockstep). See [packages/devkit-advisory/README.md](packages/devkit-advisory/README.md).
- `devkit-spec`: Spec-driven delivery commands and agent assets on the shared devkit harness. See [packages/devkit-spec/README.md](packages/devkit-spec/README.md).
- `devkit-starter`: Example external content package demonstrating bundle packaging and distribution. See [packages/devkit-starter/README.md](packages/devkit-starter/README.md).
- `devkit-catalog`: Opt-in content bundles that are available once installed but deployed only when a project selects them. See [packages/devkit-catalog/README.md](packages/devkit-catalog/README.md).
- `devkit-viewer`: A local, read-only page for the Living Spec, proposals, specs and roadmap of several devkit repositories (`devkit viewer serve`), and the Svelte viewer library autohub vendors. See [packages/devkit-viewer/README.md](packages/devkit-viewer/README.md).

## Verification

Run lint, type checks, and relevant tests before completing code changes. Use `just test-affected` for development,
review and the final integration content; no separate local full-suite run is required. Preserve its `mode=full`
fallback. Incorporate a moved base and resolve conflicts before testing; merging unchanged verified content needs
no additional test run. Full CI runs nightly at 04:17 Asia/Seoul when the default branch differs from its last
successful nightly verification, and always at release or manual invocation. A viewer frontend change selects no
pytest test: run the command its `[FRONTEND_CHECK: ...]` line names instead:

| Target | Command |
| --- | --- |
| Lint & format | `just lint [module]` |
| Lint & format check (CI) | `just lint-check [module]` |
| Type check (Pyright) | `just check [module]` |
| Tests during development | `just test-affected` (from the diff) or `just test <module> [area\|path...]` |
| Full test suite (nightly, release, manual, or selector fallback) | `just test` |
| devkit-dist without devkit-agt (dist-only check) | `just test-dist` |
| Test Coverage | `just test-cov [module] [area\|path...]` |
| Governance Rules | `just rules-check` or `just rules-fix` |
| Consumer smoke (packaging, CLI wiring, hooks) | `just smoke` |
| Viewer frontend (needs Node; rebuild the committed page after a change) | `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build` |

<!-- DEVKIT:START -->
## devkit

This repository installs agent assets with `devkit`. `.devkit/config.toml` selects
bundles; `.devkit/installation.json` records what is deployed.

- Before work that touches a bundle's assets, run `uv run devkit get-context <bundle>` once per bundle in the current agent context. Installed bundles: `advisory`, `authoring`, `devkit`, `devkit-dev`, `harness`, `response-style`, `spec`.
- Entry skill `devkit-playbook`: find and run an operational playbook (explicit user invocation only).
- Entry skill `devkit-workflow`: diagnose and follow the delivery workflow stage of a work unit.
- Never edit `.devkit/managed/` or projected agent files; change the source bundle or use `devkit override`.
- Before replying, read and apply the `response-style` skill. Put the conclusion in the first sentence. Use `→ **Core sentence.** Explanation` for ordinary points; preserve required facts and formats, and make unfinished work and necessary user decisions clear.
- Before any development work, run `uv run devkit get-context spec` once per agent context and follow it. Start work with `/spec <intent>`; `/spec-next` orients. `docs/` is the current-state Living Spec, `specs/` holds feature specs.

This block is managed by `devkit sync`; edit outside the markers only.
<!-- DEVKIT:END -->
