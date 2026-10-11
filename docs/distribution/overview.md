# Unified Agent Asset Distribution Architecture: Overview

**Status**: Architecture Specification & Reference Implementation  
**Tooling Package**: `devkit-distribution` (`devkit` CLI)  
**Consumer Root**: `.devkit/`  
**Related Documents**:
- [Bundle Manifest Specification](manifest-spec.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Synchronization & Transactions](sync-and-transactions.md)
- [Native Agent Projections](agent-projections.md)
- [Context Loading & Playbooks](context-and-playbooks.md)
- [Transitive Dependencies](transitive-dependencies.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Overview and Objectives

The `devkit` distribution system manages the unified packaging, distribution, projection, upgrade, audit, and restoration lifecycle for developer agent assets. It targets personal AI coding agents (such as Codex, Claude Code, and Antigravity) while treating agent configurations, instructions, governance rules, playbooks, and skills as first-class versioned packages.

AI coding agents typically rely on vendor-specific directories (such as `.agents/`, `.codex/`, or `.claude/`) with disjointed configuration schemas, divergent subagent formats, and ad-hoc file placement conventions. The `devkit` distribution architecture addresses these challenges by establishing a structured contract between content producers, distribution tooling, and consumer workspaces.

### Core Principles

1. **Native Config Fidelity**: Preserve native configuration formats without forcing a compromised lowest-common-denominator schema. Native subagent definitions and tool configurations are copied verbatim; unsupported agent features fail explicitly during planning rather than being silently stripped, modified, or degraded.
2. **Decoupled Versioning & uv Ecosystem Synergy**: Leverage standard Python packaging infrastructure (`uv`, wheels, `importlib.metadata`, and `uv.lock`) instead of inventing custom archive resolvers, external release downloaders, or bespoke caching systems. Consumer projects install content wheels directly as dev dependencies.
3. **Deterministic Packaging & Ingestion**: Reproducible bundle manifests, static resource verification, normalized POSIX file permissions (`0644`/`0755`), and strict relative path containment without execution side effects.
4. **Explicit Ownership Boundaries & Conflict Protection**: Maintain strict isolation between pristine managed assets, project-specific local additions, explicit complete overrides, and untracked foreign files. Any unmanaged collision or modified deployed file halts synchronization immediately to prevent data loss.
5. **Transactional Integrity & Fault Tolerance**: All project-level installations, upgrades, and removals are planned upfront, checked for conflicts, and executed atomically using advisory locking, a write-ahead journal (`sync-journal.json`), temporary sibling writes, and automated rollback recovery.

---

## 2. Architecture Units and Boundaries

The distribution architecture comprises five primary units:

```text
┌──────────────────────────────────────────────────────────────────┐
│                   Python Content Wheels (uv)                     │
│  - Installed via `uv add --dev <content-wheel>`                  │
│  - Entry point: `devkit_distribution.bundles`                    │
│  - Resource module containing `bundle/bundle.toml` & assets      │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ (importlib discovery)
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              devkit-distribution (Python CLI: devkit)            │
│  - Entry-point & resource discovery (`importlib.resources`)      │
│  - Manifest validation, inventory planning & preset selection    │
│  - ACID transaction engine, advisory locking & write journal     │
│  - Native agent projection adapters (Codex, Claude Code)         │
│  - Progressive playbook search & context loading                 │
│  - Local authoring validator & deterministic ZIP builder         │
└──────────────────┬───────────────────────────────┬───────────────┘
                   │                               │
       (Projects & Manages)              (Dispatches to)
                   │                               │
                   ▼                               ▼
┌────────────────────────────────────┐ ┌───────────────────────────┐
│       Consumer Project Workspace   │ │     agent-rule-engine     │
│  - .devkit/installation.json       │ │  - Governance evaluation  │
│  - .devkit/managed/<bundle>/       │ │  - Rule discovery         │
│  - .devkit/transient/ (lock/journ) │ │  - Convergence recheck    │
│  - Projected native agent files    │ │  - Wheel dependencies via │
│    (.agents/, .codex/, .claude/)   │ │    consumer uv environment│
└────────────────────────────────────┘ └───────────────────────────┘
```

| Unit | Responsibilities | Distribution & Versioning Model |
| --- | --- | --- |
| `devkit-distribution` | CLI, manifest validator, bundle packager, planner, transactional workspace engine, native projection adapters | Semantic versioning (`X.Y.Z`) as a standard Python package |
| Content Wheel | Versioned asset sources, native variants, dependencies, metadata | Python wheel with semantic package version and bundle version |
| `bundle.toml` | Manifest declaring assets, kinds, sources/variants, and presets | Pinned to `schema = 1` contract within the wheel's resource module |
| `agent-rule-engine` | Governance rule discovery, sequential evaluation, autofix convergence recheck | Monorepo package/CLI; rules declare dependencies through wheels |
| Project Config | Declarative baseline agent targets, bundle presets, and exclusions | Optional TOML (`schema = 1`) in `.devkit/config.toml` (Git-tracked) |
| Consumer Receipt | Pinned packages, bundle versions, selections, asset paths, file hashes/modes | Explicit receipt schema version (`schema = 1`) in `.devkit/installation.json` |

---

## 3. Subsystem Implementation Layout

The distribution tooling lives in `packages/devkit-distribution/src/devkit_distribution/`:

- `bundles/`:
  - `manifest.py`: Manifest schema definition (`bundle.toml` schema 1), TOML parsing, slug/version validation, path sanitization (`safe_source`), and asset inventory resolution.
  - `package.py`: Deterministic local ZIP packaging with normalized epoch timestamps, POSIX permissions, sorted archive entries, and hashed inventory verification.
  - `playbooks.py`: Frontmatter parsing and structural normalization for playbooks.
  - `guidance.py`: Generating host instructions and guidance pointers.
- `installation/`:
  - `discovery.py`: Discovery of installed content wheels via `importlib.metadata` entry points and live resource materialization via `importlib.resources`.
  - `inventory.py`: Computation of desired managed and native file inventories, preset filtering, agent target directory mappings, and destination collision detection.
  - `sync.py`: Project synchronization lifecycle, receipt validation, conflict evaluation, and recovery orchestration.
  - `transaction.py`: Project advisory locking (`fcntl.flock`), write-ahead journaling (`sync-journal.json`), atomic file writes (`mkstemp` + rename + directory `fsync`), and rollback recovery.
  - `overrides.py`: Overrides authoring, baseline digest tracking, upstream drift detection, and 3-way diff reconciliation.
  - `playbook_search.py`: Lexical BM25 search over managed playbooks.
  - `reading.py`: Ownership and integrity verification for reading receipt-managed context files.
- `cli/`:
  - Click-based `devkit` CLI providing `sync`, `list`, `plan`, `get-context`, `playbook search`, `recover`, `override`, and `bundle` (`validate`, `build`).
