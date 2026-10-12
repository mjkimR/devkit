# Unified Agent Asset Distribution Architecture: Overview

**Status**: Architecture Specification & Reference Implementation  
**Tooling Package**: `devkit` (`devkit` CLI)  
**Consumer Root**: `.devkit/`  
**Related Documents**:
- [Bundle Manifest Specification](manifest-spec.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Synchronization & Transactions](sync-and-transactions.md)
- [Native Agent Projections](agent-projections.md)
- [Context Loading & Playbooks](context-and-playbooks.md)
- [Transitive Dependencies](transitive-dependencies.md)
- [In-Repository Bundles](in-repo-bundles.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Overview and Objectives

The `devkit` distribution system manages the unified packaging, distribution, projection, upgrade, audit, and restoration lifecycle for developer agent assets. It targets personal AI coding agents (such as Codex, Claude Code, and Antigravity) while treating agent configurations, instructions, governance rules, playbooks, and skills as first-class versioned packages.

AI coding agents typically rely on vendor-specific directories (such as `.agents/`, `.codex/`, or `.claude/`) with disjointed configuration schemas, divergent subagent formats, and ad-hoc file placement conventions. The `devkit` distribution architecture addresses these challenges by establishing a structured contract between content producers, distribution tooling, and consumer workspaces.

### Core Principles

1. **Native Config Fidelity**: Preserve native configuration formats without forcing a compromised lowest-common-denominator schema. Native subagent definitions and tool configurations are copied verbatim, never converted between hosts: an agent without a native variant gets no projection and the sync reports it (`unprojected`), and a role contract that does not mention a selected agent fails the sync, rather than anything being silently stripped, modified, or degraded.
2. **Decoupled Versioning & uv Ecosystem Synergy**: Leverage standard Python packaging infrastructure (`uv`, wheels, `importlib.metadata`, and `uv.lock`) instead of inventing custom archive resolvers, external release downloaders, or bespoke caching systems. Consumer projects install content wheels directly as dev dependencies.
3. **Deterministic Packaging & Ingestion**: Reproducible bundle manifests, static resource verification, normalized POSIX file permissions (`0644`/`0755`), and strict relative path containment without execution side effects.
4. **Explicit Ownership Boundaries & Conflict Protection**: Maintain strict isolation between pristine managed assets, assets added through in-repository bundles, explicit complete overrides, and untracked foreign files. Any unmanaged collision or modified deployed file halts synchronization immediately to prevent data loss.
5. **Transactional Integrity & Fault Tolerance**: All project-level installations, upgrades, and removals are planned upfront, checked for conflicts, and executed atomically using advisory locking, a write-ahead journal (`sync-journal.json`), temporary sibling writes, and automated rollback recovery.

---

## 2. Architecture Units and Boundaries

The distribution architecture comprises these units:

```text
┌──────────────────────────────────────────────────────────────────┐
│                   Python Content Wheels (uv)                     │
│  - Installed via `uv add --dev <content-wheel>`                  │
│  - Entry point group: `devkit.bundles`                           │
│  - Resource module containing `bundle/bundle.toml` & assets      │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ (importlib discovery)
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   devkit (Python CLI: devkit)                    │
│  - Entry-point & resource discovery (`importlib.resources`)      │
│  - Manifest validation, inventory planning & preset selection    │
│  - ACID transaction engine, advisory locking & write journal     │
│  - Native projections (Codex, Claude Code, Antigravity)          │
│  - Progressive playbook search & context loading                 │
│  - Local authoring validator & deterministic ZIP builder         │
└──────────────────┬───────────────────────────────┬───────────────┘
                   │                               │
       (Projects & Manages)           (Receipt read by)
                   │                               │
                   ▼                               ▼
┌────────────────────────────────────┐ ┌───────────────────────────┐
│       Consumer Project Workspace   │ │   Receipt consumers       │
│  - .devkit/installation.json       │ │  - devkit.rules: rule     │
│  - .devkit/managed/<bundle>/       │ │    assets                 │
│  - .devkit/transient/ (lock, jrnl) │ │  - devkit.workflow: defs, │
│  - Projected native agent files    │ │    checks, roles          │
│    (.agents/, .codex/, .claude/)   │ │  - devkit.gate: gates     │
└────────────────────────────────────┘ └───────────────────────────┘
```

| Unit | Responsibilities | Distribution & Versioning Model |
| --- | --- | --- |
| `devkit` | CLI, manifest validator, bundle packager, planner, transactional workspace engine, native projection adapters | Semantic versioning (`X.Y.Z`) as a standard Python package |
| Content Wheel | Versioned asset sources, native variants, dependencies, metadata | Python wheel with semantic package version and bundle version |
| `bundle.toml` | Manifest declaring assets, kinds, sources/variants, presets, and an optional default preset | Pinned to `schema = 1` contract within the wheel's resource module |
| Receipt consumers (`devkit.rules`, `devkit.workflow`, `devkit.gate`) | Load the rule, workflow, workflow-check, subagent and gate assets recorded in the receipt | Modules of the same `devkit` package; asset code declares its dependencies through wheels |
| Project Config | Bundle selection with presets, agent targets, playbook search defaults, guidance block and override drift policy, plus the tables of the other modules | TOML (`schema = 1`) in `.devkit/config.toml` (Git-tracked); no entry means not deployed, except built-in bundles, which are deployed with their default preset unless set to `false`; `[rules]`, `[workflow]` and `[gates]` are owned by their modules, `[tool.<name>]` by other tools |
| Consumer Receipt | Pinned packages and bundle versions of selected bundles, applied selection, asset paths, file hashes/modes | Explicit receipt schema version (`schema = 1`) in `.devkit/installation.json` |

---

## 3. Subsystem Implementation Layout

The distribution tooling lives in `packages/devkit/src/devkit/distribution/`. It builds on `devkit.core`
(frontmatter grammar, the typed receipt reader, safe relative paths, project root discovery) and may import
only `devkit.core` and `devkit.advisory`. The library surface is exported from `devkit.distribution`
(`sync_project`, `load_bundle`, `get_context`, `search_playbooks`, the override operations, `plan_bundle`,
`project_status`, `project_listing` and their `TypedDict` results).

- `bundles/` (authoring side; no workspace knowledge):
  - `common.py`: slug and version grammars, the reserved `all` preset, supported agent names.
  - `manifest.py`: `bundle.toml` schema 1, source path rules (canonical relative POSIX, no backslash, no symlink), seeded targets, `source_files` (skips `.DS_Store`, `__pycache__/`, `*.pyc`), and kind-specific validation at load.
  - `instructions.py`, `playbooks.py`, `workflows.py`, `subagents.py`: headers of each kind on the shared frontmatter grammar; role contract rendering per agent.
  - `guidance.py`: the context-loading prerequisite inserted after a skill's frontmatter.
  - `package.py`: deterministic ZIP archives with a hashed inventory.
- `installation/` (consumer workspace side):
  - `workspace.py`: well-known paths (`.devkit/...`, root `AGENTS.md`), path safety for reads and writes, file content and mode normalization.
  - `transaction.py`: the project lock (`.devkit/transient/lock`), the write-ahead journal, atomic replacement, recovery and directory pruning.
  - `receipt.py`: strict receipt reading (`devkit.core.receipt` plus ownership rules) and serialization.
  - `config.py`: `.devkit/config.toml` reading, selection resolution, and edits checked before a sync and saved after it.
  - `discovery.py`: installed bundles via the `devkit.bundles` entry-point group; built-in bundles.
  - `inventory.py`: the desired state (`Inventory`): managed copies, native projections per agent, role contract rendering, generated entry skills, seeds and override tracking.
  - `overrides.py`: which file a deployment reads (override or upstream) and whole-asset drift tracking.
  - `override_commands.py`: `override create|diff|accept|remove|list`.
  - `sync.py`: `sync_project` (lock, `sync_locked`, then post-sync hooks) and recovery.
  - `guidance_block.py`: the root `AGENTS.md` block.
  - `context.py`, `playbook_search.py`, `reading.py`: agent-facing reads of receipt-recorded files under the shared lock.
  - `status.py`, `plan.py`, `results.py`: `status` and `list` reports, `bundle plan`, and the JSON result types.
  - `playbook_skill.py`, `workflow_skill.py`: the generated `devkit-playbook` and `devkit-workflow` entry skills.
  - `hooks.py`: the `devkit.post_sync` extension point.
- `errors.py`: the `DistributionError` hierarchy (`BundleError`, `SelectionError`, `ConflictError`, `LockHeldError`, ...), each an `AdvisoryError` with a stable code; see the [reference](reference.md#error-codes).
- `cli/`: the distribution commands of the `devkit` CLI: `sync`, `add`, `remove`, `list`, `status`, `recover`, `get-context`, `playbook search`, `override` (`create`, `diff`, `accept`, `remove`, `list`) and `bundle` (`validate`, `plan`, `build`). Every command takes `-w/--workspace-root`, prints one JSON document (the result, or `{"error": {...}}`), renders an error as an advisory on stderr and exits `2` on error (`1` only for `sync --check` when a sync is needed).
