# Architecture Overview

This document provides a high-level overview of the `devkit` monorepo architecture, design principles, and module boundaries. It is also the index of the documentation under `docs/`.

---

## 1. System Mission & Core Modules

`devkit` is a developer tooling suite for engineering teams collaborating with AI coding agents (such as Codex, Claude Code, and Antigravity). It ships as one Python package, `devkit`, with one CLI (`devkit`), and addresses these concerns in multi-agent workflows:

1. **Asset Distribution & Guidance Delivery (`devkit.distribution`)**:
   Packaging, versioning, selecting, and synchronizing agent guidance, instructions, operational playbooks, native skills, subagent roles, and other bundle assets across developer repositories (`devkit sync`, `add`, `remove`, `list`, `status`, ...).
2. **Repository Governance & Deterministic Verification (`devkit.rules`)**:
   Evaluating static invariants, Markdown link integrity, and code hygiene with automated repairs and convergence rechecks, and executing the rules that bundles distribute; the engine itself carries no document model (`devkit rules`).
3. **Delivery Workflow Orchestration (`devkit.workflow`)**:
   Declaring multi-stage delivery procedures as data, computing the current stage of a work unit from its files, enforcing approval gates by project policy, recording human decisions, and detecting procedure drift, so every agent host follows the same procedure from the same state (`devkit workflow`).
4. **Commit Gates (`devkit.gate`)**:
   Running pluggable policy at Git's commit hooks through static wrappers, layered project and per-clone configuration, and gates distributed as bundle assets (`devkit gate`).
5. **Agent Advisories (`devkit.advisory`)**:
   The Agent Advisory Protocol: every CLI reports errors, warnings and notices as advisories whose `[ACTION]` directive tells an agent whether to fix, wait, stop, or continue. The built-in `advisory` bundle teaches the protocol to agents in consumer repositories.
6. **Compact Command Output (`devkit.compact`)**:
   Running tests, linters and other verification commands with their complete output in a log file and a bounded view for the agent: outcome, recognized summaries and warnings, relayed advisories and, on failure, a head-and-tail excerpt (`devkit run`).

All of them build on `devkit.core`, the SDD-agnostic shared foundation (frontmatter grammar, installation receipt, safe paths, Git runner, plugin loading, project discovery, CLI plumbing).

**Agent-first.** The primary consumer of every `devkit` command is an AI coding agent; people read the same output, but nothing is shaped for them at the agent's expense. Results are matchable sentinel lines or one JSON object on stdout, everything an agent must act on is a coded advisory with a deterministic directive on stderr, and diagnostics stay out of the default output to protect the agent's context window. See [Agent-First Output](agent-output.md).

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

Layering inside the package: `advisory` imports no other module; `core` may import `advisory`; `rules` may import `core` and `advisory`; `workflow` and `gate` may import `core`, `advisory` and `rules`; `distribution` and `compact` may import only `core` and `advisory`. `devkit.cli` assembles the command line. A test enforces this.

---

## 2. Monorepo Structure

```text
devkit/
├── packages/
│   ├── devkit/                # The devkit package: one `devkit` CLI over the modules below
│   │   └── src/devkit/
│   │       ├── core/          # Shared foundation (frontmatter, receipt, paths, Git, plugins, project root)
│   │       ├── advisory/      # Agent Advisory Protocol (errors, warnings, notices) and the `advisory` guide bundle
│   │       ├── rules/         # Governance rule engine (`devkit rules`)
│   │       ├── workflow/      # Delivery workflow engine (`devkit workflow`)
│   │       ├── gate/          # Commit gate system (`devkit gate`)
│   │       ├── distribution/  # Bundle packaging and sync (`devkit sync`, ...) and the `devkit` guide bundle
│   │       ├── compact/       # Compact command output (`devkit run`)
│   │       └── cli.py         # The root `devkit` group: assembles every area's commands
│   └── devkit-starter/        # Example external content package
├── examples/bundles/          # Example bundle delivery-workflow (the starter bundle lives in devkit-starter)
├── scripts/                   # Shared shell logic behind the justfile recipes
└── docs/                      # Documentation per module (see the index below)
```

Inside each area, modules are grouped by concern; every area exposes its library surface from its `__init__` (`from devkit.workflow import Workspace`, `from devkit.gate import run_hook`), and modules import each other by absolute path (`devkit.<area>....`), never relatively:

| Area | Layout |
| --- | --- |
| `core` | `cli.py` (shared CLI plumbing), `errors.py`, `frontmatter.py`, `git.py`, `paths.py`, `plugins.py`, `project.py`, `receipt.py` |
| `advisory` | `error.py`, `types.py` (`ExitCode`, `Level`, `ActionMode`, ...), `advisory.py`, `bundle/` (the `advisory` guide bundle) |
| `rules` | `engine/` (registry, evaluator, configuration, policy, phases, settings, discovery, errors), `workspace/` (cache, Markdown catalog, Git snapshots), `rules/` (built-in rules), `cli/` |
| `workflow` | `definition/` (document model, validation, discovery, check registry, identifiers), `project/` (configuration, layout, roles, plugin checks), `unit/` (units, binding, frontmatter, decision records, envelopes), `evaluation/` (evaluator, primitives, results, requests, Git, lint), top-level `workspace.py`, `answers.py`, `handoff.py`, `render.py`, `errors.py`, and `cli/` |
| `gate` | `engine/` (models, base class, configuration, registry, runner), `hooks/` (hook wrappers and Git queries), `gates/` (built-in gates), `errors.py`, `cli/`, `__main__.py` (`python -m devkit.gate`, which the hook wrappers exec) |
| `distribution` | `content.py` (file content helpers shared by both sides), `bundles/` (authoring: manifest, kinds, packaging; no workspace knowledge), `installation/` (consumer workspace: sync, receipt, overrides, status, context), `cli/`, `guide/` (the `devkit` guide bundle), `errors.py` |
| `compact` | `scan.py` (bounded view of an output), `execute.py` (`run_command`: log, process group, signals), `errors.py`, `cli.py` |

The module maps with one line per file are in each module's documentation.

---

## 3. Module Interaction Model

1. **Content packaging**:
   Assets (instructions, skills, playbooks, rules, workflows, workflow checks, subagent roles, gates, documents, guidance fragments) are declared in a `bundle.toml` inside a Python package and registered under the `devkit.bundles` entry-point group. The `devkit` package registers its own `devkit`, `advisory`, `authoring` and `git-commits` bundles; external packages such as `devkit-starter` register theirs. A repository's own assets ship as an in-repository bundle.
2. **Selection and synchronization**:
   Built-in bundles that declare `auto_select` (`devkit`, `advisory`) are selected with their default preset unless `.devkit/config.toml` opts out (`[presets] <bundle> = false`); every other bundle, including the opt-in built-ins `authoring` and `git-commits`, is selected with `devkit add`. `devkit sync` verifies the bundles, writes managed copies under `.devkit/managed/<bundle>/`, projects native skills and subagents into `.agents/`, `.codex/` and `.claude/`, maintains the managed block in the root `AGENTS.md` (with the selected bundles' guidance fragments), seeds project files once, and records every file in `.devkit/installation.json` in one transaction.
3. **Consumption by the other modules**:
   - Agents load bundle guidance on demand with `devkit get-context <bundle>`, and occasional procedures with `devkit playbook search` after an explicit `devkit-playbook` invocation.
   - `devkit rules check` loads the rule assets recorded in the receipt in addition to the built-in rules; `devkit rules check --staged` and `--ci` evaluate exact Git trees.
   - `devkit workflow` discovers workflow definitions, workflow checks and subagent roles from the receipt; the generated `devkit-workflow` entry skill routes agents to `devkit workflow next`.
   - `devkit gate install` writes hook wrappers that run `devkit.gate`; gates come from the package (`message-nonempty`, `rules-staged`) and from `kind = "gate"` assets in the receipt.

---

## 4. Errors, Exit Codes and Platforms

**Library errors.** Every expected failure a `devkit` library function raises is an `AdvisoryError` subclass from `devkit.advisory` with a stable `UPPER_SNAKE` code (`RECEIPT_INVALID`, `BUNDLE_INVALID`, `RULES_CONFIG_INVALID`, `UNIT_NOT_FOUND`, `GATE_CONFIG_INVALID`, ...) and the advisory fields that direct the caller's next step. An embedding caller branches on `error.code` or `error.mode` instead of matching messages; problems a function collects rather than raises (rule loading, policy and execution problems; workflow validation, file loading and shared-stage problems; envelope and decision record errors) are typed entries with a code too. Each module's reference lists its codes. Built-in exceptions remain only for programming errors, such as calling an API with arguments its contract forbids.

**Warnings and notices.** Something a successful operation must tell its caller is an `AdvisoryError` at level `WARNING` (the user must learn or decide something: `ORPHAN_LEFT`, `OVERRIDE_DRIFT` after a sync) or `NOTICE` (worth knowing: `BUNDLE_UNSELECTED`, `TOOL_VERSION_CHANGED`). It is never raised: the function returns it with its result, under `notices`, and the CLI renders it after the result as a `[WARN]` or `[NOTICE]` block. Libraries never print and never use logging to communicate; see the [Agent Advisory Protocol](../advisory/protocol.md#8-warnings-and-notices-in-practice).

**CLI boundary.** Every command group is built on `devkit.core.cli`: the same `-w/--workspace-root` option (an explicit root must be an existing directory; the default is the devkit project containing the current directory, while `devkit gate` always works on the Git top level, found with `devkit.core.require_git_toplevel`), the same `--format text|json` option (case-insensitive), the same output options (`-q/--quiet`, `-v/--verbose`, `--strict`, or `DEVKIT_QUIET`, `DEVKIT_VERBOSE`, `DEVKIT_STRICT`; see [Agent-First Output, section 6](agent-output.md#6-verbosity-and-strictness)) and the same error boundary. The boundary renders an uncaught `AdvisoryError` as an Agent Advisory Protocol block on stderr and exits with the error's `exit_code`; any other exception is reported as `UNEXPECTED_ERROR` (`MAINTENANCE`). `--version` exists only on the root `devkit` group.

**Output channels.** stdout carries the result, stderr carries advisories; the full contract is [Agent-First Output](agent-output.md).

- **JSON output.** When stdout is JSON (`--format json`, and every distribution command), it is exactly one object, never a bare array: a command's payload sits under a named key (`violations`, `rules`, `units`, `checks`, `requests`, `overrides`, ...), problems the command collected sit under `errors` and its warnings and notices under `notices`, as `AdvisoryError.to_dict()` objects, and a command that fails outright prints `{"error": {...}}` (the same envelope) while the advisory goes to stderr.
- **Text output.** Text-mode stdout is made of one-line `[KIND: ...]` sentinels that an agent can match without parsing prose: rules prints `[VIOLATION: ...]`, `[SUMMARY: errors=N warnings=N infos=N fixed=N]` and `[OK: ...]`; workflow prints `[STAGE: ...]`, `[GATE: ...]`, `[REQUEST: ...]` and similar; gate prints `[HOOK: ...]` and `[GATE: ...]`. Advisory sentinel names (`ERROR`, `WARN`, `WARNING`, `NOTICE`, `INFO`, ...) are never used as a kind. No emoji and no colour.
- **stderr.** Advisory blocks only: `[WARN]` and `[NOTICE]` blocks after the result, `[ERROR]` blocks last; `[INFO]` log lines only under `-v`. `-q` hides notices, never warnings or errors.

**Arguments.** click only parses syntax (unknown options, missing arguments, a value outside a fixed choice); those usage errors print click's `Usage:` text and exit `2`. Every semantic check of an argument (conflicting flags, a malformed selector, a workspace root or path that does not exist, an unknown rule ID) raises `ArgumentError` (`ARGUMENT_INVALID`, `INPUT_ERROR`) through the boundary, so a JSON caller still receives one document.

**Configuration errors.** `.devkit/config.toml` (and the gate's clone-local `devkit.config`) is read with `devkit.core.project.read_toml`/`read_project_config`: a file that cannot be read or parsed is the core `ConfigError` (`CONFIG_INVALID`), passed through unchanged by every area. A malformed table an area owns is that area's subclass of it: `RULES_CONFIG_INVALID`, `WORKFLOW_CONFIG_INVALID`, `GATE_CONFIG_INVALID`.

**Exit codes.** Every `devkit` command follows the checker convention of `grep`, `diff` and `ruff` (`devkit.advisory.ExitCode`):

| Code | `ExitCode` | Meaning | Examples |
| --- | --- | --- | --- |
| `0` | `OK` | Success; nothing found | `rules check` without violations; `workflow next` waiting for a human |
| `1` | `FINDINGS` | The command ran and reports a negative result | rule violations remain; `sync --check` needs a sync; a gate refused the commit; `workflow validate` found invalid definitions; `devkit status`, `gate status` or `workflow show` reports a problem |
| `2` | `ERROR` | The command could not do its job | usage and argument errors, unreadable configuration, receipt or definition, a file that cannot be loaded, refused invalid input, unexpected errors |

Warnings and notices never change the exit code; `--strict` turns a run that would exit `0` into `1` when it reported a warning. A command that does work and collects several problems instead of stopping at the first exits with the highest `exit_code` among them: configuration and loading problems give `2`, refusals and findings `1`. A status or show command (`devkit status`, `gate status`, `workflow show`) only reports, so it exits `1` when its report contains a problem, whatever the problem's own code (`devkit.core.cli.report_exit_code`), and `2` only when it cannot run; for `devkit status` that is a missing, modified or mode-mismatched file, a pending journal, or override drift. A workflow state that waits for a person or a delegated role is a result, not a failure, and exits `0`. The per-command details are in each module's reference.

**Platforms.** `devkit` supports macOS and Linux only (POSIX): it relies on `fcntl` locks, POSIX file modes and `/bin/sh` hook wrappers. It writes LF line endings.

---

## 5. Documentation Index

Each module's `reference.md` is the quick reference (CLI, configuration, library); the other documents in its directory are canonical for semantics.

### Cross-Cutting Architecture
- [Agent-First Output](agent-output.md): The output contract of every command: stdout and stderr, text sentinels, JSON envelope, verbosity, logs.
- [Resource Taxonomy](resource-taxonomy.md): Three-tier classification and naming standards for agent assets.
- [Hybrid Binary Distribution Evaluation](evaluations/hybrid-binaries.md): Deferred evaluation record on bundling compiled binaries with `uv` wheels (not adopted).

### Shared Foundation (`devkit.core`, `devkit.advisory`)
- [Core Reference](../core/reference.md): Frontmatter grammar, receipt reader, safe paths, Git runner, plugin loading, project discovery, CLI plumbing.
- [Agent Advisory Protocol](../advisory/protocol.md): Levels, block format, fields, mode derivation and canonical `[ACTION]` directives.
- [Advisory Reference](../advisory/reference.md): The `devkit.advisory` library and the `advisory` guide bundle.

### Asset Distribution (`devkit.distribution`)
- [Distribution Reference](../distribution/reference.md): CLI commands, configuration, and library surface.
- [Distribution Overview](../distribution/overview.md): Distribution architecture, principles, and lifecycle.
- [Bundle Manifest Specification](../distribution/manifest-spec.md): `bundle.toml` syntax, asset kinds, presets, and validation.
- [Workspace Ownership & Overrides](../distribution/workspace-ownership.md): Workspace layout, ownership categories, overrides, and per-file drift review.
- [Synchronization & Transactions](../distribution/sync-and-transactions.md): Selection, receipt, transactional engine, locks, journal, and rollback.
- [Native Agent Projections](../distribution/agent-projections.md): Multi-agent projection matrix for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](../distribution/context-and-playbooks.md): Progressive context disclosure, BM25 playbook search, and CLI tools.
- [Transitive Dependencies](../distribution/transitive-dependencies.md): Python wheel composition and dependency boundaries.
- [In-Repository Bundles](../distribution/in-repo-bundles.md): Repository-owned assets as a self-consumed content package.

### Governance Engine (`devkit.rules`)
- [Rules Reference](../rules/reference.md): CLI usage, configuration, built-in rules, and the custom rule API.
- [Rule Engine Overview](../rules/overview.md): Engine architecture, workspace cache, and Markdown file catalog.
- [Evaluation Lifecycle](../rules/evaluation-lifecycle.md): Single-pass repair, convergence check, phases, project policy, and Git snapshot gates.
- [Rule Authoring Guide](../rules/rule-authoring.md): Protocols, finding models, and creating custom rules.

### Workflow Engine (`devkit.workflow`)
- [Workflow Reference](../workflow/reference.md): CLI usage, configuration, roles, plugin checks, and library.
- [Workflow Engine Overview](../workflow/overview.md): Delivery model, work unit layout template, approval gate policies, CLI surface, and the relationship to specrig.
- [Workflow Definitions and Checks](../workflow/definition-and-checks.md): Definition schema, check registry, envelope contract, binding and drift, and output signals.
- [Human Interaction Contract](../workflow/human-interaction.md): Requests, decision records, and how hosts ask and answer.

### Commit Gates (`devkit.gate`)
- [Gate Reference](../gate/reference.md): Install, configuration, and CLI quick reference.
- [Commit Gate Overview](../gate/overview.md): Hook wrappers, built-in gates, gate contract, bundle distribution, configuration layers, and CLI.

### Compact Command Output (`devkit.compact`)
- [Compact Reference](../compact/reference.md): `devkit run` usage, output lines, exit codes, library, and agent guidance.
- [Compact Command Output Overview](../compact/overview.md): Execution, logs, the bounded view and its budgets, output contract, and scope.

### Examples
- [devkit-starter](../../packages/devkit-starter/README.md): An external content package whose `src/devkit_starter/bundle` is the starter example bundle.
- [delivery-workflow example bundle](../../examples/bundles/delivery-workflow/README.md): A workflow asset with a host-neutral reviewer role.
