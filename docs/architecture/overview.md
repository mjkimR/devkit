# Architecture Overview

This document provides a high-level overview of the `devkit` monorepo architecture, design principles, and subsystem boundaries.

---

## 1. System Mission & Core Subsystems

`devkit` is a developer tooling suite for engineering teams collaborating with AI coding agents (such as Codex, Claude Code, and Antigravity). It addresses these concerns in multi-agent workflows:

1. **Asset Distribution & Guidance Delivery (`devkit-distribution`)**:
   Packaging, versioning, selecting, and synchronizing agent guidance, instructions, operational playbooks, native skills, and configurations across developer repositories.
2. **Repository Governance & Deterministic Verification (`agent-rule-engine`)**:
   Evaluating static invariants, specification document integrity, cross-references, and code hygiene with automated repairs and convergence rechecks.
3. **Delivery Workflow Orchestration (`agent-workflow-engine`)**:
   Declaring multi-stage delivery procedures as data, computing the current stage of a work unit from its files, enforcing approval gates by project policy, and detecting procedure drift, so every agent host follows the same procedure from the same state.
4. **Commit Gates (`agent-commit-gate`)**:
   Running pluggable policy at Git's commit hooks through static wrappers, layered project and per-clone configuration, and gates distributed as bundle assets.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        devkit Monorepo Suite                           │
├───────────────────────────────────┬────────────────────────────────────┤
│       devkit-distribution         │         agent-rule-engine          │
│  - Python content wheels (uv)     │  - Fast AST & Markdown scanner     │
│  - Manifest schema (bundle.toml)  │  - Deterministic invariants        │
│  - ACID transactional sync engine │  - Specification checks & fixes    │
│  - Multi-agent projection         │  - Convergence recheck engine      │
│  - Playbook progressive search    │  - CLI (agent-rules) & library     │
└─────────────────┬─────────────────┴──────────────────┬─────────────────┘
                  │                                    │
                  ▼                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Consumer Project Workspace                       │
│  - Guidance (.devkit/managed/, .devkit/config.toml, installation.json) │
│  - Native agent projections (.agents/, .codex/, .claude/)              │
│  - Local customizations (.devkit/overrides/)                           │
│  - CI & pre-commit verification (just rules-check, just lint, etc.)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Monorepo Structure

```text
devkit/
├── packages/
│   ├── devkit-distribution/   # Distribution CLI (`devkit`) and sync engine
│   ├── agent-rule-engine/     # Governance rule engine and CLI (`agent-rules`)
│   ├── agent-workflow-engine/ # Delivery workflow engine and CLI (`agent-workflow`)
│   ├── agent-commit-gate/     # Commit gate system and CLI (`commit-gate`)
│   ├── agent-advisory/        # Agent Advisory Protocol errors and authoring guide bundle
│   └── devkit-starter/        # Reference content package for bundles
├── examples/bundles/          # Example distribution bundles
├── scripts/                   # Shared shell logic and tooling helpers
└── docs/                      # Central architectural and package specifications
    ├── architecture/          # Cross-cutting system design & taxonomy
    ├── distribution/          # Detailed specifications for devkit-distribution
    ├── rule-engine/           # Detailed specifications for agent-rule-engine
    ├── workflow/              # Detailed specifications for agent-workflow-engine
    └── commit-gate/           # Detailed specifications for agent-commit-gate
```

---

## 3. Subsystem Interaction Model

The subsystems are decoupled yet operate synergistically:

1. **Content Wheel Packaging**:
   Governance rules and operational playbooks are authored within content wheel packages (such as `devkit-starter`).
2. **Deterministic Distribution**:
   When a consumer project runs `devkit sync`, `devkit-distribution` discovers the installed content wheels via standard Python entry points, verifies bundle integrity, and projects managed assets into `.devkit/managed/<bundle>/` and agent-specific directories (`.agents/`, `.codex/`, `.claude/`).
3. **Execution & Verification**:
   - Agent prompts discover playbooks and contextual guidance progressively using `devkit playbook search` or `devkit read`.
   - The repository governance pipeline runs `agent-rules check` (or `just rules-check`) to verify specification links and repo hygiene before committing.

---

## 4. Documentation Index

### Cross-Cutting Architecture
- [Resource Taxonomy](resource-taxonomy.md): Three-tier classification and naming standards for agent assets.
- [Hybrid Binary Distribution Evaluation](evaluations/hybrid-binaries.md): Architectural evaluation of bundling compiled binaries with `uv` wheels.

### Asset Distribution (`devkit-distribution`)
- [Distribution Overview](../distribution/overview.md): Distribution architecture, principles, and lifecycle.
- [Bundle Manifest Specification](../distribution/manifest-spec.md): `bundle.toml` schema v1, asset kinds, presets, and validation.
- [Workspace Ownership & Overrides](../distribution/workspace-ownership.md): Workspace layout, pristine assets, and 3-way drift reconciliation.
- [Synchronization & Transactions](../distribution/sync-and-transactions.md): ACID transactional engine, advisory locks, journals, and rollback.
- [Native Agent Projections](../distribution/agent-projections.md): Multi-agent projection matrix for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](../distribution/context-and-playbooks.md): Progressive context disclosure, BM25 search, and CLI tools.
- [Transitive Dependencies](../distribution/transitive-dependencies.md): Python wheel composition and dependency boundaries.
- [In-Repository Bundles](../distribution/in-repo-bundles.md): Repository-owned assets as a self-consumed content package.

### Governance Engine (`agent-rule-engine`)
- [Rule Engine Overview](../rule-engine/overview.md): Engine architecture, workspace cache, and document catalog.
- [Evaluation Lifecycle](../rule-engine/evaluation-lifecycle.md): Single-pass repair, convergence check, and CLI execution.
- [Rule Authoring Guide](../rule-engine/rule-authoring.md): Protocols, finding models, and creating custom rules.

### Workflow Engine (`agent-workflow-engine`)
- [Workflow Engine Overview](../workflow/overview.md): Delivery model, work unit layout template, approval gate policies, CLI surface, and the relationship to specrig.
- [Workflow Definitions and Checks](../workflow/definition-and-checks.md): Definition schema, check registry, envelope contract, binding and drift, and output signals.

### Commit Gates (`agent-commit-gate`)
- [Commit Gate Overview](../commit-gate/overview.md): Hook wrappers, gate contract, bundle distribution, configuration layers, and CLI.
