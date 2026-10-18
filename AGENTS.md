# devkit: Agent Guide

Personal developer tools monorepo.

## Architecture and Boundaries

- Python monorepo managed with `uv` workspaces and `just`.
- Python sources live in `packages/<package>/src/` or `tools/<tool>/src/` (`models/devkit-embed` is a data package outside the workspace, built by hand); tests belong in each package's `tests/`, never under `src/`, except a rule's own tests, which travel with it in its folder (`<rule>/tests/`, `CAP-GOV-rule-authoring`).
- Keep `justfile` recipes thin; shared shell logic belongs in `scripts/`.
- Inside `packages/devkit`, lower modules never import higher ones (`advisory` < `core` < `rules` < `workflow`/`gate`; `search`, `compact`, `worktree` and `host` use only `core` and `advisory`; `distribution` also uses `search` and `host`; `integration` uses `core`, `advisory`, `host` and `worktree`; `rules`, `gate` and `generated` also use `compact`; the data-only bundle areas `advisory_guide` and `commits_guide` import nothing, and `authoring_guide` only `core`, `advisory` and `rules`); a test enforces the layering (`packages/devkit/tests/test_layering.py`). `devkit.advisory` ships as the separate `devkit-advisory` distribution (standard library only, no entry points), and `devkit` is a namespace package both share: never add `src/devkit/__init__.py`.
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
- **Libraries never print**: commands write output only through `devkit.core.cli` (`boundary`, `echo_json`, `echo_notices`, `exit_on_warnings`).
- Specifications: `ARCH-08-1-agent-output` and `CAP-ADV-agent-advisory-protocol`.

## Compatibility

- No external consumers exist yet. Breaking changes to schemas (`bundle.toml`, `.devkit/config.toml`, `.devkit/installation.json`), CLI commands, and APIs may be made in place: do not bump schema versions or add migration paths, deprecation shims, or legacy readers.
- Once a real consumer exists, delete this section and treat these formats as versioned contracts that require migrations.
- Exception: `devkit-advisory` (the `devkit.advisory` API) already has runtime consumers in other repositories. Treat it as a semver contract: within `0.x`, a breaking change needs a minor version bump, released in lockstep with `devkit`.

## Packages

Keep package descriptions in this guide to a high-level summary of their purpose. Do not add package-specific configurations or detailed architectural explanations here; refer to the package README and `docs/capabilities/<area>/` when deeper details are needed:

- `devkit-agt`: The single devkit distribution with one CLI (`devkit`): agent asset distribution, repository rules, delivery workflows, commit gates and structured agent advisories, built on an SDD-agnostic shared core. See [packages/devkit/README.md](packages/devkit/README.md) for its modules and layering.
- `devkit-advisory`: The Agent Advisory Protocol library (`devkit.advisory`) on its own, for other repositories' runtime; `devkit-agt` depends on the same version. See [packages/devkit-advisory/README.md](packages/devkit-advisory/README.md).
- `devkit-spec`: Spec-driven delivery commands and agent assets on the shared devkit harness. See [packages/devkit-spec/README.md](packages/devkit-spec/README.md).
- `devkit-starter`: Example external content package demonstrating bundle packaging and distribution. See [packages/devkit-starter/README.md](packages/devkit-starter/README.md).
- `devkit-catalog`: Opt-in content bundles that are available once installed but deployed only when a project selects them. See [packages/devkit-catalog/README.md](packages/devkit-catalog/README.md).

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

<!-- DEVKIT:START -->
## devkit

This repository installs agent assets with `devkit`. `.devkit/config.toml` selects
bundles; `.devkit/installation.json` records what is deployed.

- Before work that touches a bundle's assets, run `uv run devkit get-context <bundle>` once per bundle in the current agent context. Installed bundles: `advisory`, `authoring`, `devkit`, `response-style`, `spec`.
- Entry skill `devkit-playbook`: find and run an operational playbook (explicit user invocation only).
- Entry skill `devkit-workflow`: diagnose and follow the delivery workflow stage of a work unit.
- Never edit `.devkit/managed/` or projected agent files; change the source bundle or use `devkit override`.
- Before responding to the user, read .devkit/managed/response-style/instructions/response-style.md and apply its communication guidelines.
- Before any development work, run `uv run devkit get-context spec` once per agent context and follow it. Start work with `/spec <intent>`; `/spec-next` orients. `docs/` is the current-state Living Spec, `specs/` holds feature specs.

This block is managed by `devkit sync`; edit outside the markers only.
<!-- DEVKIT:END -->
