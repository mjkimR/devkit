# Unified Agent Asset Distribution Architecture

**Status**: Architecture Specification & Implementation Blueprint  
**Tooling Package**: `devkit-distribution` (`devkit` CLI)  
**Consumer Root**: `.devkit/`  
**Current State**: Implemented local `bundle.toml` schema 1 validation, deterministic ZIP archive builds, and preset-based managed inventory planning. Consumer installation lifecycle, receipts, native agent adapters, dependency resolution, and isolated rule runtimes are pending.

For current command usage and manifest reference, see the [package README](../../packages/devkit-distribution/README.md).

---

## 1. Overview and Objectives

The `devkit` distribution system manages the unified distribution, projection, upgrade, audit, and restoration lifecycle for developer agent assets. It targets a curated set of personal AI coding agents (such as Codex, Claude Code, and Antigravity) while treating agent configurations, instructions, rules, and skills as first-class versioned packages.

### Core Principles

1. **Native Config Fidelity**: Preserve native configuration formats without forcing a compromised lowest-common-denominator schema. Native subagent definitions and tool configurations are copied verbatim; unsupported agent features fail explicitly during planning rather than being silently stripped or degraded.
2. **Decoupled Versioning**: Separate the distribution engine (`devkit-distribution`), the evaluation engine (`agent-rule-engine`), and content bundles. Project receipts lock exact bundle versions, archive digests, and runtime environments together.
3. **Deterministic Packaging**: Hermetic, reproducible bundle builds with fixed timestamps, normalized file permissions (POSIX `0644`/`0755`), sorted file inventories, and SHA-256 integrity digests.
4. **Explicit Ownership Boundaries**: Maintain strict isolation between pristine managed assets, project-specific local additions, explicit complete overrides, and untracked foreign files.
5. **Transactional Integrity**: All project-level installations, upgrades, and removals are planned upfront, checked for conflicts, and executed atomically with a durable journal to support rollback on interruption.

---

## 2. Architecture Units and Boundaries

The distribution architecture comprises five primary units:

```text
┌──────────────────────────────────────────────────────────────────┐
│                      Content Bundle (ZIP)                        │
│  - bundle.toml manifest (schema = 1)                             │
│  - Assets: skills, subagents, instructions, playbooks, rules     │
│  - Presets & optional native variants                            │
└─────────────────────────────────┬────────────────────────────────┘
                                  │ (Acquire & Ingest)
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              devkit-distribution (Python CLI: devkit)            │
│  - Manifest validation & deterministic archive build             │
│  - Inventory planner & conflict resolver                         │
│  - Transactional installer, receipt recorder & recovery journal   │
│  - Native agent projection adapters                              │
└──────────────────┬───────────────────────────────┬───────────────┘
                   │                               │
       (Projects & Manages)              (Dispatches to)
                   │                               │
                   ▼                               ▼
┌────────────────────────────────────┐ ┌───────────────────────────┐
│       Consumer Project Workspace   │ │     agent-rule-engine     │
│  - .devkit/installation.json       │ │  - Isolated rule runtime  │
│  - .devkit/managed/ (Clean cache)  │ │  - Sequential evaluation  │
│  - .devkit/overrides/ (Full repl.) │ │  - Convergence recheck    │
│  - .devkit/local/ (New assets)     │ │  - Pinned wheel / env     │
│  - Projected native agent files    │ └───────────────────────────┘
└────────────────────────────────────┘
```

| Unit | Responsibilities | Versioning Model |
| --- | --- | --- |
| `devkit-distribution` | CLI, manifest validator, bundle packager, planner, transactional workspace engine, native projection adapters | Semantic versioning (`X.Y.Z`) of the distribution package |
| `agent-rule-engine` | Governance rule discovery, sequential evaluation, autofix convergence recheck | Semantic versioning of the rule engine library & CLI |
| Content Bundle | Asset sources, native variants, dependencies, metadata | Semantic bundle version (`X.Y.Z`) and cryptographic archive digest |
| Preset | Named asset selection contracts declared within a bundle | Pinned to the defining bundle version |
| Consumer Receipt | Pinned versions, digests, presets, active agents, and ownership records | Explicit receipt schema version |

### Codebase Organization

The distribution tool lives in `packages/devkit-distribution/src/devkit_distribution/`, with test suites located under `packages/devkit-distribution/tests/`:

- `bundles/`: Manifest schema definitions, TOML parsing, validation, deterministic ZIP packaging, and archive inspection.
- `workspace/`: Workspace layout, `.devkit/` directory management, `installation.json` receipts, and ownership auditing.
- `installation/`: Plan generation, diff calculation, transactional lock, write-ahead journal, and rollback recovery.
- `agents/`: Native agent projection adapters, file rendering contracts, and configuration hooks.
- `cli/`: Click-based `devkit` command-line interface.

---

## 3. Bundle Specification (`bundle.toml`)

Bundles are authored in source directories and packaged into deterministic ZIP archives. Authors keep their natural workspace layout; the manifest maps logical assets to relative source paths.

### Asset Kinds

- `skill`: A directory containing `SKILL.md` along with supporting scripts, references, and assets. Directory trees and executable file permissions (`0755`) are preserved.
- `subagent`: Native agent persona definitions or configuration files.
- `instruction`: Contextual guidance and prompt markdown documents linked to agent startup instructions.
- `playbook`: Operational workflows, checklists, and procedural guides.
- `rule`: Python-based governance rules (standalone files or isolated packages).

### Identity and Contract

Every asset is identified by a logical tuple: `(bundle, kind, id)`. Asset IDs must be unique within each bundle.

```toml
schema = 1
name = "starter-workflow"
version = "0.1.0"

[compatibility]
distributor = ">=0.1.0,<0.2.0"

[[assets]]
id = "review"
kind = "skill"
source = "skills/review"
targets = ["codex", "claude-code"]

[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/codex/reviewer.toml"
claude-code = "native/claude-code/reviewer.md"

[[assets]]
id = "development"
kind = "instruction"
source = "instructions/development.md"

[[assets]]
id = "review-flow"
kind = "playbook"
source = "playbooks/review.md"

[presets.daily]
assets = ["development", "review-flow", "review"]
```

### Manifest Rules and Validation

- **Strict Schema**: Unknown top-level or table keys cause immediate validation failure.
- **Source Paths**: Must be existing relative POSIX paths without path traversal (`..`), symlinks, or special device files.
- **Variants vs. Source**: An asset declares either a single `source` or a `variants` mapping matching supported agent names, never both.
- **Preserves Native Content**: Native files declared in `variants` remain untouched during packaging; the packager does not parse or sanitize vendor-specific options.
- **Exact Dependencies**: Version resolution in v1 requires exact versions to guarantee determinism without an unbounded constraint solver.

### Deterministic Archive Build

The `devkit bundle build` command produces a bit-for-bit reproducible ZIP archive:
- Files are sorted lexicographically by archive path.
- Entry timestamps are pinned to a fixed epoch (e.g., `1980-01-01 00:00:00 UTC`).
- File permissions are normalized to POSIX `0644` (regular files) or `0755` (executables).
- An internal SHA-256 manifest inventory is embedded to verify integrity before extraction.

---

## 4. Consumer Workspace & Ownership Model

Consuming projects integrate bundles under a dedicated root directory: `.devkit/`.

```text
.devkit/
  installation.json       # Pinned versions, digests, selections, ownership (Committed to Git)
  local/                  # Project-defined private assets and custom policies (Committed to Git)
  overrides/<bundle>/     # Full replacements for upstream managed assets (Committed to Git)
  managed/<bundle>/       # Clean extracted upstream assets (Generated, Git-ignored)
  runtime/                # Isolated virtualenv and rule dependencies (Host-specific, Git-ignored)
  transient/              # Transaction lock and journal (Git-ignored)
<agent native paths>      # Projected native assets (e.g., .codex/, .claude/, .gemini/)
```

### Ownership Categories

1. **Managed Assets (`.devkit/managed/<bundle>/`)**:
   - Exact unpacked representation of the verified bundle archive.
   - Read-only cache, never directly edited by users; safely regenerated on `restore`.
2. **Local Assets (`.devkit/local/`)**:
   - New assets authored specifically within the consumer project.
   - Must not collide with managed logical IDs `(bundle, kind, id)` or projected target file paths.
3. **Overrides (`.devkit/overrides/<bundle>/<kind>/<id>`)**:
   - Full replacement of an existing managed asset. Partial directory overlays for skills are rejected to prevent orphaned reference files.
   - The receipt stores the baseline digest of the upstream asset at the time the override was introduced.
   - Upgrades check whether upstream content has changed; if the upstream baseline differs, the user must review and acknowledge the drift.
4. **Project Native Projections**:
   - Copies or projections placed in agent-specific paths (e.g., `.codex/skills/`, `.claude/skills/`).
   - The distributor tracks file paths and SHA-256 hashes in `installation.json`.
   - **Foreign File Protection**: The distributor never assumes broad ownership of agent directories. Files created manually or by other tools are preserved. Collisions with untracked files abort execution unless explicitly adopted.
   - Shared configuration files (such as global instruction indexes) use isolated markers; formats lacking lossless modification contracts are not edited automatically.

---

## 5. Agent Native Adapters and Projection

Adapters bridge the generic asset model to vendor-specific agent implementations.

### Adapter Responsibilities

Each agent adapter encapsulates:
- Target destination paths and supported directory structures.
- Supported asset kinds and capability constraints.
- Instruction discovery and session entrypoint configuration.
- Native registration hooks and manifest conventions.

### Fidelity and Fallback Policy

- **No Silent Degrades**: If a target agent does not support subagents, the adapter will not downgrade the asset to a skill or strip parameters. Instead, planning fails with an explicit missing capability error.
- **Unverified Options**: Unknown agent options in native files are preserved verbatim. If configuration keys are unverified for the agent's target version range, they are flagged as warnings requiring explicit confirmation during planning.
- **Instruction Discovery**: For instructions and playbooks, adapters inject links or entrypoints into the host's primary bootstrap files (e.g., system prompts or startup instructions) so the agent can discover and read content on demand.
- **Preconditions**: Authentication credentials, user trust prompts, and host global configurations are audited as prerequisites; the distributor does not automatically alter host-level user environments.

---

## 6. Rule Distribution and Isolated Execution

Governance rules evaluated by `agent-rule-engine` have specialized distribution and isolation requirements.

### Single-File Rules vs. Packaged Rules

- **Zero-Dependency Rules**: Self-contained `.py` scripts that rely only on standard libraries and `agent_rule_engine` interfaces. Can be projected directly into the engine's rule discovery directory.
- **Packaged Rules**: Rules that require external dependencies, third-party libraries, or complex relative imports. Packaged as Python wheels with pinned dependency manifests.

### Runtime Isolation

Rule execution must never pollute the host system Python or the consumer project's primary virtual environment:
- The bundle declares engine version compatibility, supported Python versions, and pinned dependencies.
- `devkit` provisions an isolated virtual environment at `.devkit/runtime/`.
- During evaluation, execution is dispatched to the pinned runtime; PATH-based Python resolution is disabled.
- Bundles are never imported or executed during packaging or installation. Syntax, manifests, and hashes are validated purely via static inspection.
- Duplicate rule IDs across built-in, bundle, and local scopes are treated as errors unless declared as an explicit override.

---

## 7. Lifecycle Operations and State Management

### The Installation Receipt (`installation.json`)

The receipt is the single source of truth for the installed state. It is committed to source control and contains:
- Receipt schema version.
- Pinned bundle sources, versions, and archive SHA-256 digests.
- Active preset and asset selections.
- Engine version and runtime lock specifications.
- Inventory of projected files, file modes, and SHA-256 checksums.
- Override baseline digests.
- Retired file records (for safe cleanup).

It intentionally excludes absolute filesystem paths, operating system tokens, authentication secrets, and transient timestamps.

### Command Matrix

| Command | Lifecycle Phase | Contract |
| --- | --- | --- |
| `bundle validate` | Authoring | Verifies manifest syntax, schema rules, and existence of declared local source files. |
| `bundle build` | Packaging | Produces a deterministic ZIP archive with inventory hashes and normalized file permissions. |
| `plan` | Evaluation | Calculates desired inventory, detects file collisions, verifies agent capabilities, and outputs state diff without modifying disk. |
| `install` | Deployment | Validates plan, acquires bundles, extracts managed trees, applies overrides, writes native projections, and writes `installation.json`. |
| `restore` | Replication | Reconstructs `.devkit/managed/` and native projections using only `installation.json` on a clean checkout. Operates offline if cache is present. |
| `upgrade` | Maintenance | Updates bundles to target versions, recalculates diffs, checks upstream drift for overridden assets, and updates receipt. |
| `status / audit` | Verification | Detects missing files, checksum drift, unmanaged modifications to native projections, and runtime environment validity. |
| `recover` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to roll back partially written files after an interrupted process. |
| `remove` | Teardown | Safely unlinks managed and projected files recorded in the receipt. Preserves `.devkit/local/`, overrides, and foreign files. |
| `list / show` | Discovery | Inspects available assets, kinds, active presets, and paths to resolved documents. |
| `rules check / fix` | Governance | Dispatches rule evaluation or repair passes through the isolated `.devkit/runtime/` environment. |

### Transaction Safety and Journaling

All mutating operations (`install`, `upgrade`, `restore`, `remove`) enforce ACID-style safety guarantees:
1. **Pre-Flight Validation**: Full plan computation and conflict detection prior to writing any bytes.
2. **Lock Acquisition**: File lock in `.devkit/transient/lock` prevents concurrent executions.
3. **Write-Ahead Journal**: Actions (file additions, modifications, unlinks) are logged to `.devkit/transient/journal.json` before execution.
4. **Atomic Replacement**: Files are written to temporary sibling files and renamed atomically into place.
5. **Rollback on Failure**: If execution is interrupted, `recover` restores original contents from recorded before-state hashes.

---

## 8. Release Acquisition and Transport

The acquisition layer fetches bundles into a local host cache before project projection:

- **Transport Channels**:
  - Phase 1: Local directories and local ZIP archive paths.
  - Phase 2: Private GitHub Releases with authenticated HTTPS downloads.
  - Optional: Direct Git repository commits (pinned by commit hash and verified archive digest, not floating branch names).
- **Transport Cache**: Downloaded archives are validated against declared SHA-256 checksums and cached in the user's tool cache directory.
- **Offline Determinism**: Once artifacts reside in the local cache, `install` and `restore` execute completely offline without network access.
- **CLI Distribution**: The `devkit` CLI and `agent-rule-engine` are packaged as standard Python wheels, installed and executed via `uv tool` or virtual environments.

---

## 9. Implementation Roadmap

```text
Phase 1: Bundle Core & Plan (Current)
  ├── bundle.toml schema 1 validation
  ├── Deterministic ZIP packager
  └── In-memory inventory planning & preset selection

Phase 2: Consumer Workspace & Single Agent Adapter
  ├── .devkit/ workspace layout & installation.json receipt
  ├── Transactional write journal & atomic file writes
  ├── Basic adapter (e.g., Codex or Claude Code)
  └── install, restore, status, and recover commands

Phase 3: Overrides & Drift Management
  ├── Full asset overrides (.devkit/overrides/)
  ├── Baseline digest tracking in receipt
  ├── Upgrade workflow with upstream drift detection
  └── Removal & clean retirement of untampered projections

Phase 4: Rule Engine Integration & Runtime Isolation
  ├── Isolated virtualenv provisioning (.devkit/runtime/)
  ├── Packaged wheel support for complex rules
  ├── Duplicate rule ID prevention across scopes
  └── rules check and rules fix command dispatch

Phase 5: Release Acquisition & Multi-Agent Pilot
  ├── Local cache manager & archive digest verification
  ├── Remote transport (GitHub Releases)
  ├── Secondary agent adapters (Antigravity)
  └── End-to-end repository pilot & CI verification
```

### Verification Criteria

Code changes must pass monorepo checks before completion:
- `just lint devkit-distribution`: Code formatting and Ruff linting.
- `just check devkit-distribution`: Static type checking via Pyright.
- `just test devkit-distribution`: Unit tests covering manifest parsing, packaging determinism, path sanitization, and state transitions.
- `just rules-check`: Repository-wide governance validation.
