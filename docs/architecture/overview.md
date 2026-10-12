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
5. **Structured Errors (`devkit.advisory`)**:
   The Agent Advisory Protocol: every CLI reports failures as advisories whose `[ACTION]` directive tells an agent whether to fix, wait, or stop. The built-in `advisory` bundle teaches the protocol to agents in consumer repositories.

All of them build on `devkit.core`, the SDD-agnostic shared foundation (frontmatter grammar, installation receipt, safe paths, Git runner, plugin loading, project discovery).

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
│         devkit.advisory (error protocol)  ·  devkit.core (foundation)    │
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

Layering inside the package: `core` imports no other module; `advisory` may import `core`; `rules` may import `core` and `advisory`; `workflow` and `gate` may import `core`, `advisory` and `rules`; `distribution` may import only `core` and `advisory`. `devkit.cli` assembles the command line. A test enforces this.

---

## 2. Monorepo Structure

```text
devkit/
├── packages/
│   ├── devkit/                # The devkit package: one `devkit` CLI over the modules below
│   │   └── src/devkit/
│   │       ├── core/          # Shared foundation (frontmatter, receipt, paths, Git, plugins, project root)
│   │       ├── advisory/      # Agent Advisory Protocol errors and the `advisory` guide bundle
│   │       ├── rules/         # Governance rule engine (`devkit rules`)
│   │       ├── workflow/      # Delivery workflow engine (`devkit workflow`)
│   │       ├── gate/          # Commit gate system (`devkit gate`)
│   │       └── distribution/  # Bundle packaging and sync (`devkit sync`, ...) and the `devkit` guide bundle
│   └── devkit-starter/        # Example external content package
├── examples/bundles/          # Example bundles (starter mirror, delivery-workflow)
├── scripts/                   # Shared shell logic behind the justfile recipes
└── docs/                      # Documentation per module (see the index below)
```

---

## 3. Module Interaction Model

1. **Content packaging**:
   Assets (instructions, skills, playbooks, rules, workflows, workflow checks, subagent roles, gates, documents) are declared in a `bundle.toml` inside a Python package and registered under the `devkit.bundles` entry-point group. The `devkit` package registers its own `devkit` and `advisory` bundles; external packages such as `devkit-starter` register theirs. A repository's own assets ship as an in-repository bundle.
2. **Selection and synchronization**:
   Built-in bundles are selected with their default preset unless `.devkit/config.toml` opts out (`[presets] <bundle> = false`); external bundles are selected with `devkit add`. `devkit sync` verifies the bundles, writes managed copies under `.devkit/managed/<bundle>/`, projects native skills and subagents into `.agents/`, `.codex/` and `.claude/`, maintains the managed block in the root `AGENTS.md`, seeds project files once, and records every file in `.devkit/installation.json` in one transaction.
3. **Consumption by the other modules**:
   - Agents load bundle guidance on demand with `devkit get-context <bundle>`, and occasional procedures with `devkit playbook search` after an explicit `devkit-playbook` invocation.
   - `devkit rules check` loads the rule assets recorded in the receipt in addition to the built-in rules; `devkit rules check --staged` and `--ci` evaluate exact Git trees.
   - `devkit workflow` discovers workflow definitions, workflow checks and subagent roles from the receipt; the generated `devkit-workflow` entry skill routes agents to `devkit workflow next`.
   - `devkit gate install` writes hook wrappers that run `devkit.gate`; gates come from the package (`message-nonempty`, `rules-staged`) and from `kind = "gate"` assets in the receipt.

---

## 4. Documentation Index

Each module's `reference.md` is the quick reference (CLI, configuration, library); the other documents in its directory are canonical for semantics.

### Cross-Cutting Architecture
- [Resource Taxonomy](resource-taxonomy.md): Three-tier classification and naming standards for agent assets.
- [Hybrid Binary Distribution Evaluation](evaluations/hybrid-binaries.md): Deferred evaluation record on bundling compiled binaries with `uv` wheels (not adopted).

### Shared Foundation (`devkit.core`, `devkit.advisory`)
- [Core Reference](../core/reference.md): Frontmatter grammar, receipt reader, safe paths, Git runner, plugin loading, project discovery.
- [Advisory Reference](../advisory/reference.md): Agent Advisory Protocol errors and the `advisory` guide bundle.

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

### Examples
- [delivery-workflow example bundle](../../examples/bundles/delivery-workflow/README.md): A workflow asset with a host-neutral reviewer role.
