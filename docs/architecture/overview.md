# Architecture Overview

The `devkit` modules, their boundaries and interaction, the conventions every module shares, and the index of the documentation under `docs/`.

## 1. System Mission & Core Modules

`devkit` is a developer tooling suite for engineering teams collaborating with AI coding agents (such as Codex, Claude Code, and Antigravity). It ships as one Python package, `devkit`, with one CLI (`devkit`):

1. **Asset Distribution & Guidance Delivery (`devkit.distribution`)**: packaging, versioning, selecting and synchronizing agent guidance, instructions, playbooks, native skills, subagent roles and other bundle assets across repositories (`devkit sync`, `add`, `remove`, `list`, `status`, ...).
2. **Repository Governance & Deterministic Verification (`devkit.rules`)**: static invariants, Markdown link integrity and code hygiene with automated repairs and convergence rechecks, including the rules bundles distribute; the engine carries no document model (`devkit rules`).
3. **Delivery Workflow Orchestration (`devkit.workflow`)**: multi-stage delivery procedures declared as data; the current stage of a work unit is computed from its files, approval gates follow project policy, human decisions are recorded and procedure drift is detected, so every agent host follows the same procedure from the same state (`devkit workflow`).
4. **Commit Gates (`devkit.gate`)**: pluggable policy at Git's commit hooks through static wrappers, layered project and per-clone configuration, and gates distributed as bundle assets (`devkit gate`).
5. **Agent Advisories (`devkit.advisory`)**: the Agent Advisory Protocol, through which every command reports errors, warnings and notices with an `[ACTION]` directive; the built-in `advisory` bundle teaches it to agents in consumer repositories.
6. **Compact Command Output (`devkit.compact`)**: verification commands run with their complete output in a log file and a bounded view for the agent (`devkit run`).
7. **Document Search (`devkit.search`)**: lexical (BM25), dense (static embeddings) and hybrid ranking over a caller's documents, a library without a CLI; dense search comes with the `devkit[search]` extra.
8. **Task Worktrees (`devkit.worktree`)**: one Git worktree per task, created from the base checkout and integrated, removed and reported by deterministic commands that refuse instead of forcing (`devkit worktree`).

All of them build on `devkit.core`, the SDD-agnostic shared foundation (frontmatter grammar, installation receipt, safe paths, Git runner, plugin loading, project discovery, CLI plumbing).

Every command is agent-first: its primary consumer is an AI coding agent, and its output is a contract specified in [Agent-First Output](agent-output.md).

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         devkit package (one CLI)                         │
├──────────────────────┬─────────────────────┬────────────────┬────────────┤
│ devkit.distribution  │ devkit.rules        │ devkit.workflow│ devkit.gate│
│ - bundle.toml schema │ - Markdown & file   │ - definitions  │ - hook     │
│ - transactional sync │   scanners          │   as data      │   wrappers │
│ - agent projections  │ - autofix + recheck │ - stage, gates,│ - layered  │
│ - guidance block     │ - phases & policy   │   decisions    │   config   │
│ - playbook search    │ - Git snapshots     │ - handoff      │ - rules-   │
│                      │                     │                │   staged   │
├──────────────────────┴─────────────────────┴────────────────┴────────────┤
│       devkit.compact (devkit run: bounded command output for agents)     │
├──────────────────────────────────────────────────────────────────────────┤
│       devkit.advisory (advisory protocol)  ·  devkit.core (foundation)   │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │ devkit sync writes; rules, workflow
                                   │ and gate read the receipt
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       Consumer Project Workspace                         │
│  - .devkit/config.toml (selection and policy), .devkit/installation.json │
│  - .devkit/managed/<bundle>/ (pristine copies), .devkit/overrides/       │
│  - Root AGENTS.md managed guidance block, seeded project files           │
│  - Native agent projections (.agents/, .codex/, .claude/)                │
│  - Git hooks installed by devkit gate; CI runs devkit rules check --ci   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Layering.** `advisory` imports no other module; `core` may import `advisory`; `rules` may import `core` and `advisory`; `workflow` may import `core`, `advisory` and `rules`; `gate` may import those and `compact` (the `verify-commands` gate runs commands through it); `search`, `compact` and `worktree` may import only `core` and `advisory`; `distribution` may import `core`, `advisory` and `search`. `devkit.cli` assembles the command line. A test enforces this. The root group maps each command name to a `module:attribute` reference and imports the module only when that command runs, so a command imports only its own area and the layers below it; a test enforces this too. Installed packages mount further top-level commands through the `devkit.commands` entry-point group ([Command Plugins](command-plugins.md)).

## 2. Monorepo Structure

```text
devkit/
├── packages/
│   ├── devkit/                # The devkit package: src/devkit/<module>/ per module above, cli.py the root `devkit` group
│   ├── devkit-embed/          # The default embedding model of devkit.search (data only)
│   └── devkit-starter/        # Example external content package
├── examples/bundles/          # Example bundle delivery-workflow (the starter bundle lives in devkit-starter)
├── scripts/                   # Shared shell logic behind the justfile recipes
└── docs/                      # docs/<module>/ per module (index in section 5)
```

Inside each module, files are grouped by concern; each module's documentation has its file map. Every module exposes its library surface from its `__init__` (`from devkit.workflow import Workspace`, `from devkit.gate import run_hook`), and modules import each other by absolute path (`devkit.<module>....`), never relatively.

## 3. Module Interaction Model

1. **Content packaging**: assets (instructions, skills, playbooks, rules, workflows, workflow checks, subagent roles, gates, documents, guidance fragments) are declared in a `bundle.toml` inside a Python package and registered under the `devkit.bundles` entry-point group. The `devkit` package registers its own `devkit`, `advisory`, `authoring` and `git-commits` bundles; external packages such as `devkit-starter` register theirs. A repository's own assets ship as an in-repository bundle.
2. **Selection and synchronization**: installed bundles that declare `auto_select` (built in: `devkit`, `advisory`) are selected with their default preset unless `.devkit/config.toml` opts out (`[presets] <bundle> = false`); every other bundle, including the opt-in built-ins `authoring` and `git-commits`, is selected with `devkit add`. `devkit sync` verifies the bundles, writes managed copies under `.devkit/managed/<bundle>/`, projects native skills and subagents into `.agents/`, `.codex/` and `.claude/`, maintains the managed block in the root `AGENTS.md` (with the selected bundles' guidance fragments), seeds project files once, and records every file in `.devkit/installation.json` in one transaction.
3. **Consumption by the other modules**:
   - Agents load bundle guidance on demand with `devkit get-context <bundle>`, and occasional procedures with `devkit playbook search` after an explicit `devkit-playbook` invocation.
   - `devkit rules check` loads the rule assets recorded in the receipt in addition to the built-in rules; `devkit rules check --staged` and `--ci` evaluate exact Git trees.
   - `devkit workflow` discovers workflow definitions, workflow checks and subagent roles from the receipt; the generated `devkit-workflow` entry skill routes agents to `devkit workflow next`.
   - `devkit gate install` writes hook wrappers that run `devkit.gate`; gates come from the package (`verify-commands`, `message-nonempty`) and from `kind = "gate"` assets in the receipt.

## 4. Errors, Exit Codes and Platforms

**Library errors.** Every expected failure a `devkit` library function raises is an `AdvisoryError` subclass from `devkit.advisory` with a stable `UPPER_SNAKE` code (`RECEIPT_INVALID`, `BUNDLE_INVALID`, `RULES_CONFIG_INVALID`, `UNIT_NOT_FOUND`, `GATE_CONFIG_INVALID`, ...) and the advisory fields that direct the caller's next step. An embedding caller branches on `error.code` or `error.mode`, never on messages. Problems a function collects rather than raises (rule loading, policy and execution problems; workflow validation, file loading and shared-stage problems; envelope and decision record errors) are typed entries with a code too. Something a successful operation must report is returned with its result under `notices`, as an `AdvisoryError` at level `WARNING` or `NOTICE`, never raised ([protocol, section 8](../advisory/protocol.md#8-warnings-and-notices-in-practice)). Each module's reference lists its codes. Built-in exceptions remain only for programming errors, such as calling an API with arguments its contract forbids.

**CLI boundary.** Every command group is built on `devkit.core.cli`: the same `-w/--workspace-root` option (an explicit root must be an existing directory; the default is the devkit project containing the current directory, while `devkit gate` always works on the Git top level, found with `devkit.core.require_git_toplevel`), the same `--format text|json` option (case-insensitive), the same output options ([Agent-First Output, section 6](agent-output.md#6-verbosity-and-strictness)) and the same error boundary. The boundary renders an uncaught `AdvisoryError` as an advisory block on stderr and exits with the error's `exit_code`; any other exception is reported as `UNEXPECTED_ERROR` (`MAINTENANCE`). `--version` exists only on the root `devkit` group and prints one `[VERSION: devkit <version>]` line. What goes to stdout and stderr is specified in [Agent-First Output](agent-output.md).

**Arguments.** click only parses syntax (unknown options, missing arguments, a value outside a fixed choice); those usage errors print click's `Usage:` text and exit `2`. Every semantic check of an argument (conflicting flags, a malformed selector, a workspace root or path that does not exist, an unknown rule ID) raises `ArgumentError` (`ARGUMENT_INVALID`, `INPUT_ERROR`) through the boundary, so a JSON caller still receives one document.

**Configuration errors.** `.devkit/config.toml` (and the gate's clone-local `devkit.config`) is read with `devkit.core.project.read_toml`/`read_project_config`: a file that cannot be read or parsed is the core `ConfigError` (`CONFIG_INVALID`), passed through unchanged by every module. A malformed table a module owns is that module's subclass of it: `RULES_CONFIG_INVALID`, `WORKFLOW_CONFIG_INVALID`, `GATE_CONFIG_INVALID`.

**Exit codes.** Every `devkit` command follows the checker convention of `grep`, `diff` and `ruff` (`devkit.advisory.ExitCode`):

| Code | `ExitCode` | Meaning | Examples |
| --- | --- | --- | --- |
| `0` | `OK` | Success; nothing found | `rules check` without violations; `workflow next` waiting for a human |
| `1` | `FINDINGS` | The command ran and reports a negative result | rule violations remain; `sync --check` needs a sync; `sync --locked` would change committed files; a gate refused the commit; `workflow validate` found invalid definitions; `devkit status`, `gate status` or `workflow show` reports a problem |
| `2` | `ERROR` | The command could not do its job | usage and argument errors, unreadable configuration, receipt or definition, a file that cannot be loaded, refused invalid input, unexpected errors, a reader that closed stdout before the result was written |

- Warnings and notices never change the exit code; `--strict` turns a run that would exit `0` into `1` when it reported a warning.
- A command that does work and collects several problems instead of stopping at the first exits with the highest `exit_code` among them: configuration and loading problems give `2`, refusals and findings `1`.
- A status or show command (`devkit status`, `gate status`, `workflow show`) only reports, so it exits `1` when its report contains a problem, whatever the problem's own code (`devkit.core.cli.report_exit_code`), and `2` only when it cannot run; for `devkit status` that is a missing, modified, mode-mismatched, symlinked or non-regular managed file, a symlinked or malformed root `AGENTS.md`, a selected bundle whose package fails to load, a pending journal, or override drift.
- A workflow state that waits for a person or a delegated role is a result, not a failure, and exits `0`.

The per-command details are in each module's reference.

**Platforms.** `devkit` supports macOS and Linux only (POSIX): it relies on `fcntl` locks, POSIX file modes and `/bin/sh` hook wrappers. It writes LF line endings.

## 5. Documentation Index

Each module's `reference.md` is the quick reference (CLI, configuration, library); the other documents in its directory are canonical for semantics.

### Cross-Cutting Architecture
- [Agent-First Output](agent-output.md): The output contract of every command: stdout and stderr, text sentinels, JSON envelope, verbosity, exit codes, logs.
- [Resource Taxonomy](resource-taxonomy.md): Three-tier classification and naming standards for agent assets.
- [Command Plugins](command-plugins.md): Top-level commands that installed packages mount through `devkit.commands`, their loading and their output contract.
- [Hybrid Binary Distribution Evaluation](evaluations/hybrid-binaries.md): Evaluation record on bundling compiled binaries with `uv` wheels (not adopted; semantic search landed in pure Python as `devkit.search`).

### Shared Foundation (`devkit.core`, `devkit.advisory`)
- [Core Reference](../core/reference.md): Frontmatter grammar, receipt reader, safe paths, Git runner, plugin loading, project discovery, CLI plumbing.
- [Agent Advisory Protocol](../advisory/protocol.md): Levels, block format, fields, mode derivation and canonical `[ACTION]` directives.
- [Advisory Reference](../advisory/reference.md): The `devkit.advisory` library and the `advisory` guide bundle.

### Task Worktrees (`devkit.worktree`)
- [Worktree Reference](../worktree/reference.md): `devkit worktree start|finish|status`, output, configuration, error codes, library.
- [Worktree Overview](../worktree/overview.md): Paths, the start and finish steps, refusals and resumption, status, the setup command.

### Document Search (`devkit.search`)
- [Search Reference](../search/reference.md): Library surface, the `devkit[search]` extra and error codes.
- [Search Overview](../search/overview.md): Document model, modes, BM25 and tokenizer, the embedding model and its package, measurements.

### Asset Distribution (`devkit.distribution`)
- [Distribution Reference](../distribution/reference.md): CLI commands and sync options, configuration, notices and error codes, library surface.
- [Distribution Overview](../distribution/overview.md): Principles, architecture units, module layout and library surface.
- [Bundle Manifest Specification](../distribution/manifest-spec.md): `bundle.toml` layout, asset kinds, presets, validation and archive builds.
- [Content Packages](../distribution/content-packages.md): Content wheel contract, installation and upgrades, and dependency boundaries.
- [Workspace Ownership & Overrides](../distribution/workspace-ownership.md): Workspace layout, ownership categories, guidance block, seeded files, overrides and drift review.
- [Synchronization & Transactions](../distribution/sync-and-transactions.md): Receipt, selection model, transaction engine, recovery and post-sync hooks.
- [Native Agent Projections](../distribution/agent-projections.md): Projection matrix and role contracts for Codex, Claude Code and Antigravity.
- [Context Loading & Playbooks](../distribution/context-and-playbooks.md): `get-context`, the skill prerequisite and playbook search.
- [In-Repository Bundles](../distribution/in-repo-bundles.md): Repository-owned assets as a self-consumed content package.

### Governance Engine (`devkit.rules`)
- [Rules Reference](../rules/reference.md): CLI synopsis, exit codes and output, configuration, built-in rule catalog, library API and error codes.
- [Rule Engine Overview](../rules/overview.md): Principles, module layout, and integration with sync, project policy and commit gates.
- [Evaluation Lifecycle](../rules/evaluation-lifecycle.md): Single-pass autofix and convergence, targets and exclusions, phases, project policy and Git snapshot gates.
- [Rule Authoring Guide](../rules/rule-authoring.md): Rule protocols, settings and guides, the workspace cache API, rule sources and registration, and a custom rule example.

### Workflow Engine (`devkit.workflow`)
- [Workflow Reference](../workflow/reference.md): Module map, CLI usage, configuration and library API.
- [Workflow Engine Overview](../workflow/overview.md): Delivery model, work unit layout, approval gates, integration, and the relationship to specrig.
- [Workflow Definitions and Checks](../workflow/definition-and-checks.md): Definition schema, shared stages, handoff candidates, check registry and plugin checks, binding and drift.
- [Review Envelopes](../workflow/envelopes.md): Envelope file contract, authoring flags and `envelope check`.
- [Human Interaction Contract](../workflow/human-interaction.md): Requests, decision records, and how hosts ask and answer.
- [Workflow CLI and Output](../workflow/cli-and-output.md): Commands, exit and error codes, text sentinels and JSON output.

### Commit Gates (`devkit.gate`)
- [Gate Reference](../gate/reference.md): Install, commands, exit and error codes, configuration, writing a gate.
- [Commit Gate Overview](../gate/overview.md): Library, built-in gates, hook wrappers, gate contract, bundle distribution and configuration layers.

### Compact Command Output (`devkit.compact`)
- [Compact Reference](../compact/reference.md): `devkit run` usage, output lines, exit and error codes, library, agent guidance and module map.
- [Compact Command Output Overview](../compact/overview.md): Execution, logs, the bounded view and its budgets, output contract, library and scope.

### Examples
- [devkit-starter](../../packages/devkit-starter/README.md): An external content package whose `src/devkit_starter/bundle` is the starter example bundle.
- [delivery-workflow example bundle](../../examples/bundles/delivery-workflow/README.md): A workflow asset with a host-neutral reviewer role.
