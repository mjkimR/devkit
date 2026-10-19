---
id: PROP-devkit-dist-package-separation
title: Separate asset distribution into independent devkit-dist package
summary: Extracts agent asset distribution, bundle manifests, and sync logic into a standalone devkit-dist package to decouple distribution from developer harness tooling.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-17
target_area: capabilities/distribution/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
    - capabilities/core/
    - capabilities/host/
    - capabilities/search/
    - architecture/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
workflow_hash: sha256:1ef60809329fded5a496efb7757fd2d07c59a9c1ec1aef6858bbef2fb5d65fc0
---

# [PROP-devkit-dist-package-separation] Separate asset distribution into independent devkit-dist package

## 1. Background & Hypothesis

### 1.1 Problem
- **Distribution machinery is coupled with developer harness tools**: Currently, `devkit-agt` (`packages/devkit`) houses the full developer harness (`devkit.rules`, `devkit.workflow`, `devkit.gate`) along with the agent asset distribution system (`devkit.distribution`: bundle loading, asset projections for skills/subagents/instructions/hooks, synchronization, receipt management, and workspace ownership).
- **Over-scoped dependencies for pure distribution consumers**: Consumers (such as service repositories like `app-common` or host agents) that only need asset synchronization or skills/subagents projections are exposed to the entire harness engine and CLI tooling.
- **Unclear boundaries between delivery workflow and asset distribution**: Delivery workflows and commit gates operate on top of distribution receipts, but the core asset packaging and synchronization protocol has zero dependency on workflow state machines or rule AST evaluation.

### 1.2 Hypothesis
Extracting `devkit.distribution` into a dedicated `packages/devkit-dist` package provides clean modularization:
1. `devkit-advisory`: Core runtime exit codes and protocol definitions (zero external dependencies).
2. `devkit-dist`: Bundle manifests, agent projection, sync transactions, receipt tracking, and asset discovery.
3. `devkit-agt`: Developer harness, rule engine, delivery workflows, commit gates, and top-level CLI aggregator.
4. `devkit-spec`: Spec-Driven Development (SDD) Living Spec extension, proposals, and lifecycle rules.

## 2. Technical Spike Questions
The standalone scope and foundation ownership are decided in `PADR-dist-foundation-ownership`:
- Installing `devkit-dist` alone provides the distribution commands, including native hook support, context loading, and playbook functionality, without installing the harness engines.
- `devkit-dist` owns the shared foundation required by those features and the sole `devkit` console entry point. `devkit-agt` depends on it and supplies the harness engines; `devkit-dist` does not depend on `devkit-agt`.

- **Q1 (Packaging & Namespace)**: Should `devkit-dist` use a separate top-level module `devkit_dist` or maintain `devkit.distribution` via PEP 420 native namespace packaging?
- **Q2 (CLI and Entrypoint Aggregation)**: How should the CLI owned by `devkit-dist` mount the harness commands supplied by its downstream dependent `devkit-agt`? Evaluate the existing `devkit.commands` extension point and lazy loading, with no competing console entry points.
- **Q3 (Configuration Schema Ownership)**: Which package owns the base `.devkit/config.toml` and `.devkit/installation.json` schema validation, and how do downstream packages (`devkit-agt`, `devkit-spec`) contribute tool-specific configuration sections?
- **Q4 (Foundation Boundaries)**: Which parts of `devkit.core`, `devkit.search`, and `devkit.host` move into `devkit-dist` to support standalone operation, and which harness-specific services remain in `devkit-agt`?
- **Q5 (Bundled Content & Compatibility)**: Which bundled guides and auto-selection defaults belong to each package, and which existing CLI, configuration, receipt, and Python API behaviors are preserved?

## 3. Proposed Design & Impact
- **Package Layout**:
  - `packages/devkit-dist/src/devkit_dist/` (or `devkit/distribution/` if namespace package is preferred).
  - Package metadata published as `devkit-dist`.
  - The shared foundation and sole `devkit` console entry point ship with `devkit-dist`; `devkit-agt` supplies the higher-level harness engines.
- **Boundaries**:
  - `packages/devkit` (`devkit-agt`) takes a direct dependency on `devkit-dist`.
  - Core capabilities under `capabilities/distribution/` ([CAP-DIST-manifest-spec](file:///home/mj/projects/workbench/repos/devkit/docs/capabilities/distribution/CAP-DIST-manifest-spec.md), [CAP-DIST-content-packages](file:///home/mj/projects/workbench/repos/devkit/docs/capabilities/distribution/CAP-DIST-content-packages.md), [CAP-DIST-sync-and-transactions](file:///home/mj/projects/workbench/repos/devkit/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md), [CAP-DIST-workspace-ownership](file:///home/mj/projects/workbench/repos/devkit/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md)) become owned by `devkit-dist`.
  - Scope includes shared foundation ownership, CLI composition, package metadata, installation/release wiring, and affected architecture and consumer guides. Planning determines the precise module split.
- **Consumer Impact**:
  - Repositories that only deploy agent skills and playbooks can install `devkit-dist` without bringing in workflow/gate/evaluation engines.
  - Standalone installation also supports native hooks, context loading, and playbook operations.
  - Existing `devkit-agt` users retain 100% backwards compatibility through dependency inclusion and command re-export.

## 4. Lifecycle & Retirement Criteria
- Preliminary decisions: Record key decisions via `devkit spec proposal padr devkit-dist-package-separation "<title>"`.
- On acceptance (`plan-accept`): Hand off to feature spec bundle `sdd-spec-feature` via `devkit spec proposal handoff devkit-dist-package-separation`.
- On rejection: Record user rationale and reject proposal via `status: rejected`.
