---
id: PROP-devkit-dist-package-separation
title: Separate asset distribution into independent devkit-dist package
summary: Extracts agent asset distribution, bundle manifests, and sync logic into a standalone devkit-dist package to decouple distribution from developer harness tooling.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-17
target_area: capabilities/distribution/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
    - capabilities/host/
    - capabilities/search/
    - capabilities/compact/
    - capabilities/integration/
    - architecture/
    - development/
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
- **Over-scoped installation for pure distribution consumers**: Consumers (such as service repositories like `app-common` or host agents) that only need asset synchronization or skills/subagents projections get the entire harness engine, its command surface and its auto-deployed guidance. The third-party dependency set is the same either way (click, pyyaml, jinja2, tomlkit are needed by distribution itself); the gain is the harness code, commands and guidance not installed or deployed.
- **Unclear boundaries between delivery workflow and asset distribution**: Delivery workflows and commit gates operate on top of distribution receipts, but the core asset packaging and synchronization protocol has zero dependency on workflow state machines or rule AST evaluation.

### 1.2 Hypothesis
Extracting `devkit.distribution` and the foundation it needs into a dedicated `packages/devkit-dist` package provides clean modularization:
1. `devkit-advisory`: The Agent Advisory Protocol library (standard library only); unchanged.
2. `devkit-dist`: The shared foundation (`devkit.core`, `devkit.search`, `devkit.host`), bundle manifests, agent projection, sync transactions, the receipt, asset discovery, context loading, playbooks, native hooks, and the sole `devkit` console script.
3. `devkit-agt`: The developer harness (rule engine, delivery workflows, commit gates, task worktrees, generated files, integration, bounded command execution `devkit run`) and its guidance bundles (`authoring`, the new auto-selected `harness`), mounted under `devkit` as first-party command plugins.
4. `devkit-spec`: Spec-Driven Development (SDD) Living Spec extension, proposals, and lifecycle rules; still built on `devkit-agt`.

## 2. Technical Spike Questions
The standalone scope and foundation ownership are decided in `PADR-dist-foundation-ownership`:
- Installing `devkit-dist` alone provides the distribution commands, including native hook support, context loading, and playbook functionality, without installing the harness engines.
- `devkit-dist` owns the shared foundation required by those features and the sole `devkit` console entry point. `devkit-agt` depends on it and supplies the harness engines; `devkit-dist` does not depend on `devkit-agt`.

Planning settled the questions below, with the user's answers to `harness-guidance`, `compact-home` and `standalone-harness-signals` (`envelopes/answer-01.yaml`); options, evidence and the challenger's reviews are in `materials/20261019-package-split-evidence.md`.

- **Q1 (Packaging & Namespace)**: Keep the `devkit.*` import paths in the shared PEP 420 namespace; no `devkit_dist` top-level package. `PADR-dist-module-split`.
- **Q2 (CLI and Entrypoint Aggregation)**: `devkit-dist` owns `devkit.cli` with only its own built-in commands; `devkit-agt` mounts `rules`, `workflow`, `gate`, `worktree`, `generated` and `integration` through the existing `devkit.commands` entry point group. `run` is mounted the same way. A standalone installation answers a harness command name with a coded error (exit `2`, directive to add `devkit-agt`) from a name-only list consulted only when no command of that name is installed; `devkit-dist` never imports or locates a harness module. `PADR-dist-command-composition`.
- **Q3 (Configuration Schema Ownership)**: `devkit-dist` owns the `.devkit/config.toml` schema, its template renderer and the receipt; harness tables stay reserved pass-through names, their commented templates move to `devkit-agt` through a `devkit.config_tables` entry point group; `[tool.<name>]` contributions are unchanged. `PADR-dist-config-receipt-ownership`.
- **Q4 (Foundation Boundaries)**: `devkit.core`, `devkit.search` and `devkit.host` move whole; the harness engines stay. `devkit.compact` (`devkit run`) stays in `devkit-agt` (user answer), so the standalone scope of `PADR-dist-foundation-ownership` is not widened. `PADR-dist-module-split`.
- **Q5 (Bundled Content & Compatibility)**: `devkit`, `advisory` and `git-commits` ship with `devkit-dist`, `authoring` with `devkit-agt`; behavior, names and import paths are preserved, ownership metadata changes in place, and the three wheels are released in lockstep. The harness guidance and the `devkit run` guidance of the `devkit` bundle move to a new auto-selected `harness` bundle shipped by `devkit-agt` (user answer), so the `devkit` bundle keeps only distribution guidance; the `run` preset becomes `harness:run`, a selection break accepted in place without shims. A standalone installation that deploys rule, gate or workflow assets (third-party or in-repo bundles only) gets a coded `WARNING` notice from `devkit sync` and `devkit status`, detected by `devkit.commands` entry point name only. `PADR-dist-bundles-compatibility`.
- **Open confirmation** (raised by the re-reviews of the folded answers, `envelopes/challenger-03.yaml` and `challenger-04.yaml`): the bundle name `harness`, which also names the `devkit-spec` capability area (question `harness-bundle-name`).

## 3. Proposed Design & Impact
- **Package Layout**:
  - `packages/devkit-dist/src/devkit/` (wheel `devkit-dist`) ships `devkit/core`, `devkit/search`, `devkit/host`, `devkit/distribution`, `devkit/cli.py`, `devkit/__main__.py` and the data-only bundle areas it owns, into the namespace shared with `devkit-advisory` and `devkit-agt`.
  - `packages/devkit/` stays the `devkit-agt` source tree (rules, workflow, gate, worktree, generated, integration, compact, the `authoring` bundle and the new data-only `harness` bundle area) and pins `devkit-dist` to its own version; its `search` and `mcp` extras pass through to `devkit-dist`'s.
- **Boundaries**:
  - `devkit-dist` never imports a `devkit-agt` area; a per-wheel layering test enforces it, and the `devkit-dist` tests run without `devkit-agt` installed.
  - The distribution contracts (`CAP-DIST-manifest-spec`, `CAP-DIST-content-packages`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-workspace-ownership`, `CAP-DIST-agent-projections`, `CAP-DIST-context-and-playbooks`, `CAP-DIST-in-repo-bundles`), `CAP-HOST-lifecycle-observation` and `CAP-SRCH-document-search` describe behavior owned by `devkit-dist`.
  - Scope includes shared foundation ownership, CLI composition, package metadata, installation/release wiring, the affected architecture documents and consumer guides.
- **Consumer Impact**:
  - Repositories that only deploy agent skills and playbooks can install `devkit-dist` without bringing in workflow/gate/evaluation engines, their commands or their guidance; third-party dependencies stay the same.
  - Standalone installation also supports native hooks, context loading, and playbook operations. It deploys no harness or `devkit run` guidance, and a harness command name (`devkit rules`, `devkit run`, ...) or a deployed rule, gate or workflow asset no engine runs is reported with a stable code and a directive to add `devkit-agt`.
  - Existing `devkit-agt` users keep every command, option, output, code, configuration key and import path, except the enumerated changes of `PADR-dist-bundles-compatibility` (bundle content, the `harness` entry, receipt names, two preset selections): `devkit-agt` includes `devkit-dist` as a dependency and mounts its commands under the same names. The first writing `devkit sync` after the upgrade rewrites the receipt's tool and package names and deploys the auto-selected `harness` bundle, committed with the upgrade. Two selections change: `devkit:run` stops the sync until it becomes `harness:run`, and `devkit:all` no longer deploys the `devkit run` guidance (no alias; this repository selects only `devkit:core`, so no selection here changes).

## 4. Lifecycle & Retirement Criteria
- Preliminary decisions: Record key decisions via `devkit spec proposal padr devkit-dist-package-separation "<title>"`.
- On acceptance (`plan-accept`): Hand off to feature spec bundle `sdd-spec-feature` via `devkit spec proposal handoff devkit-dist-package-separation`.
- On rejection: Record user rationale and reject proposal via `status: rejected`.
