# Unified Agent Asset Distribution Architecture

**Status**: Architecture Specification & Reference Implementation  
**Tooling Package**: `devkit-distribution` (`devkit` CLI)  
**Consumer Root**: `.devkit/`  
**Current State**: Implemented uv-based content wheel distribution, entry-point discovery, deterministic bundle manifests and archive packaging, preset and agent selection, ACID transactional synchronization with durable journaling, and native agent projection for Codex and Claude Code.

For command usage and manifest reference, see the [package README](../../packages/devkit-distribution/README.md).  
For the reference content package implementation, see the [devkit-starter package](../../packages/devkit-starter/README.md).

---

## 1. Overview and Objectives

The `devkit` distribution system manages the unified distribution, projection, upgrade, audit, and restoration lifecycle for developer agent assets. It targets a curated set of personal AI coding agents (such as Codex, Claude Code, and Antigravity) while treating agent configurations, instructions, governance rules, playbooks, and skills as first-class versioned packages.

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
| Consumer Receipt | Pinned packages, bundle versions, selections, asset paths, file hashes/modes | Explicit receipt schema version (`schema = 1`) in `.devkit/installation.json` |

### Codebase Organization

The distribution tool lives in `packages/devkit-distribution/src/devkit_distribution/`, with test suites located under `packages/devkit-distribution/tests/`:

- `bundles/`:
  - `manifest.py`: Manifest schema definition (`bundle.toml` schema 1), TOML parsing, slug/version validation, path sanitization (`safe_source`), and asset inventory resolution.
  - `package.py`: Deterministic local ZIP packaging with normalized epoch timestamps, POSIX permissions, sorted archive entries, and hashed inventory verification.
- `installation/`:
  - `discovery.py`: Discovery of installed content wheels via `importlib.metadata` entry points and live resource materialization via `importlib.resources`.
  - `inventory.py`: Computation of desired managed and native file inventories, preset filtering, agent target directory mappings, and destination collision detection.
  - `sync.py`: Project synchronization lifecycle, receipt validation, conflict evaluation, and recovery orchestration.
  - `transaction.py`: Project advisory locking (`fcntl.flock`), write-ahead journaling (`sync-journal.json`), atomic file writes (`mkstemp` + rename + directory `fsync`), and rollback recovery.
- `cli/`:
  - Click-based `devkit` command-line interface providing `bundle validate`, `bundle build`, `plan`, `sync`, `list`, and `recover`.

---

## 3. Package & Bundle Specification (`bundle.toml`)

### Content Wheel Contract

Content packages distribute assets as standard Python wheels installed into the consumer project's development environment. A content wheel registers an entry point under the `devkit_distribution.bundles` group:

```toml
[project.entry-points."devkit_distribution.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

```text
src/package_b_playbooks/
  __init__.py               # Empty module; strictly no side effects
  bundle/
    bundle.toml             # Manifest declaring metadata and assets
    playbooks/review.md
    instructions/development.md
    skills/review/
      SKILL.md
```

#### Discovery & Isolation Rules
- **Resource Module Reference**: The entry point value must point to an importable Python module, not a callable.
- **Root Directory**: The bundle contents and `bundle.toml` reside under the module's `bundle/` directory.
- **No Side Effects**: Loading a resource module triggers standard Python module initialization. Modules must keep `__init__.py` free of runtime side effects.
- **Static Inspection**: Synchronizing a bundle reads files purely through `importlib.resources.as_file`; it never executes rule scripts or imports rule code.
- **Unique Bundle Names**: Bundle names must be unique across all installed packages in the environment. Multiple packages declaring the same bundle name trigger an immediate error.
- **Non-Python Repositories**: Upstream repositories without Python logic (such as prompt collections or Go tools) can map their native directory layout into a content wheel at build time using Hatch `force-include` without modifying their original file structure.

### Asset Kinds

A bundle declares assets across five supported kinds:

- `skill`: A directory containing `SKILL.md` along with supporting scripts, references, and assets. The entire directory tree is preserved, maintaining executable permissions (`0755`) for scripts.
- `subagent`: Native agent persona definitions or configuration files.
- `instruction`: Contextual guidance and prompt markdown documents linked to agent startup instructions.
- `playbook`: Operational workflows, checklists, and procedural guides.
- `rule`: Python-based governance rules evaluated by `agent-rule-engine`.

### Manifest Syntax (`schema = 1`)

Every asset is identified by a logical tuple: `(bundle, kind, id)`. Asset IDs must be unique within each bundle.

```toml
schema = 1
name = "starter-workflow"
version = "0.1.0"

[[assets]]
id = "review"
kind = "skill"
source = "skills/review"

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

- **Strict Schema**: Unknown top-level keys or unrecognized table fields trigger immediate validation errors.
- **Slug Validation**: Bundle names and asset IDs must match lowercase slug regex `^[a-z][a-z0-9-]*$`.
- **Semantic Versioning**: Bundle versions must strictly follow `MAJOR.MINOR.PATCH` format.
- **Relative Path Sanitization**: Source paths must be relative POSIX paths. Paths containing traversal segments (`..`), backslashes (`\`), symlinks, or special device files are strictly rejected.
- **Source vs. Variants**: An asset must declare either a single `source` or a `variants` mapping matching supported agent names, never both.
- **Skills Integrity**: A `skill` source must point to a directory containing a valid `SKILL.md` file.
- **Verbatim Native Content**: Files declared under `variants` remain untouched during packaging and sync. The distributor does not parse, modify, or strip vendor-specific configuration keys.

### Deterministic Local Archive Build

The `devkit bundle build` command provides an optional local export helper producing bit-for-bit reproducible ZIP archives:
- Files are sorted lexicographically by archive path.
- Entry timestamps are pinned to a fixed epoch (`1980-01-01 00:00:00 UTC`).
- File permissions are normalized to POSIX `0644` (regular files) or `0755` (executables).
- An internal SHA-256 inventory manifest is embedded to verify integrity before extraction.
*(Note: ZIP archives serve as a portable local export mechanism; the primary project synchronization transport uses installed uv content wheels).*

---

## 4. Consumer Workspace & Ownership Model

Consuming projects integrate bundles under a dedicated root directory: `.devkit/`.

```text
.devkit/
  installation.json       # Pinned packages, bundle versions, selections, file hashes & modes (Git-tracked)
  managed/<bundle>/       # Clean extracted upstream resources from wheels (Generated, Git-ignored)
  transient/              # Transaction lock and recovery journal (Git-ignored)
    sync-journal.json     # Active write-ahead journal
  overrides/<bundle>/     # (Future) Full replacements for managed assets (Git-tracked)
  local/                  # (Future) Project-authored custom assets (Git-tracked)
<agent native paths>      # Projected native assets (e.g., .agents/, .codex/, .claude/)
```

### Ownership Categories

1. **Managed Assets (`.devkit/managed/<bundle>/`)**:
   - Exact unpacked representation of upstream bundle resources extracted from installed wheels.
   - Read-only cache. Always regenerated deterministically by `devkit sync`.
   - Preserves original relative paths for instructions, playbooks, and rules.
2. **Project Native Projections**:
   - Copied projections placed into agent-specific directories (such as `.agents/skills/`, `.claude/skills/`, `.codex/agents/`, `.claude/agents/`).
   - Tracked explicitly by file path, SHA-256 hash, and POSIX mode in `installation.json`.
3. **Foreign File Protection**:
   - The distributor strictly manages only files recorded in `installation.json`.
   - Files created manually or by other tools in native agent directories are preserved.
   - If a synchronization step targets a file that already exists but is not recorded in the receipt, it is treated as an unmanaged collision and sync aborts immediately.
4. **User Modification Detection**:
   - If a deployed file's disk content or mode differs from its recorded receipt signature, it is treated as a user modification.
   - Sync aborts immediately across the entire project before making any disk changes.
   - Package removal or preset narrowing will only delete files that remain byte-for-byte identical to their recorded receipt signature. Modified files are never deleted.
5. **Git & Ignore Policy**:
   - The receipt (`.devkit/installation.json`) must be committed to version control.
   - Generated resources (`.devkit/managed/`), transient transaction files (`.devkit/transient/`), and generated native copies should be ignored according to the consumer repository's own `.gitignore` policy.
   - `devkit` never automatically modifies `.gitignore` or the Git index.

---

## 5. Agent Native Adapters and Projection

Adapters bridge the abstract bundle asset model to concrete vendor-specific directory hierarchies.

### Agent Projection Matrix

| Agent | Target Kind | Destination Path in Project | Source Contract |
| --- | --- | --- | --- |
| `codex` | `skill` | `.agents/skills/<asset-id>/` | Common `source` or `variants.codex` directory |
| `codex` | `subagent` | `.codex/agents/<asset-id>.toml` | `variants.codex` single `.toml` file |
| `claude-code` | `skill` | `.claude/skills/<asset-id>/` | Common `source` or `variants.claude-code` directory |
| `claude-code` | `subagent` | `.claude/agents/<asset-id>.md` | `variants.claude-code` single `.md` file |

### Multi-Agent Projection Semantics

- **Shared Skills**: Skills are directory-based assets. The entire source directory (including supporting references and executable scripts) is projected into `.agents/skills/<asset-id>/` for Codex and `.claude/skills/<asset-id>/` for Claude Code.
- **Native Subagents**: Subagents require an explicit native file for each target agent. Codex requires a `.toml` configuration file; Claude Code requires a `.md` markdown definition.
- **No Lossy Downgrades**: If a selected agent does not have a native variant defined for a subagent, synchronization fails immediately with an explicit error. The distributor never attempts heuristic conversions or parameter stripping.
- **Target Selection**:
  - `devkit sync --agent codex`: Projects assets for Codex.
  - `devkit sync --agent codex --agent claude-code`: Projects assets for both agents simultaneously.
  - `devkit sync --no-agents`: Clears native agent selections and safely unlinks unchanged native projections while keeping managed resources intact.
  - Running `devkit sync` without `--agent` preserves previously recorded agent selections from the receipt.

### Host Environment Boundaries

- **Bootstrap Instructions**: Instructions (`kind = "instruction"`) and playbooks (`kind = "playbook"`) remain in `.devkit/managed/<bundle>/` and are recorded in the receipt's asset index. Discovered via `devkit list`.
- **No Host Mutation**: The distributor does not automatically modify host system settings, user credentials, agent trust configurations, or global instruction files (e.g., `AGENTS.md` or `CLAUDE.md`). Session integration is handled explicitly by developer configuration or entry point linking.

---

## 6. Rule Distribution and Engine Integration

Governance rules evaluated by `agent-rule-engine` have specialized distribution requirements:

- **Wheel Dependency Resolution**: Python rules distributed via content wheels declare their third-party dependencies as standard wheel dependencies in `pyproject.toml`. These dependencies are resolved and locked by `uv` within the consumer project's environment.
- **Resource Placement**: Synced rule scripts are placed into `.devkit/managed/<bundle>/rules/` preserving their original relative structure.
- **Decoupled Evaluation**: Synchronizing files does not automatically trigger rule execution. Rule evaluation is dispatched separately through `agent-rules` or `just rules-check`.
- **Static Inspection**: Bundles are inspected purely as static resources during packaging, discovery, and sync. Rule code is never imported or executed during distribution lifecycle operations.
- **Plugin Integration (Follow-up)**: Dynamic rule plugin discovery, namespace isolation, and engine evaluation APIs represent planned future extensions.

---

## 7. Lifecycle Operations, Receipts & Transaction Safety

### The Installation Receipt (`.devkit/installation.json`)

The receipt is the single source of truth for the installed state. It is committed to source control and adheres to `schema = 1`:

```json
{
  "schema": 1,
  "packages": [
    {
      "package": "devkit-starter",
      "package_version": "0.1.0",
      "bundle": "starter",
      "bundle_version": "0.1.0"
    }
  ],
  "selection": {
    "agents": ["codex", "claude-code"],
    "presets": {
      "starter": "daily"
    }
  },
  "assets": [
    {
      "bundle": "starter",
      "id": "review",
      "kind": "skill",
      "paths": [
        ".agents/skills/review/SKILL.md",
        ".claude/skills/review/SKILL.md",
        ".devkit/managed/starter/skills/review/SKILL.md"
      ]
    }
  ],
  "files": {
    ".devkit/managed/starter/bundle.toml": {
      "mode": 420,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  }
}
```

Receipt properties:
- Tracks exact package names, package versions, bundle names, and bundle versions.
- Records active agent selections and active preset restrictions.
- Stores deployed asset mappings linking logical asset IDs to physical workspace file paths.
- Records expected SHA-256 digests and POSIX file modes (`0644` or `0755`) for every deployed file.
- Omits absolute filesystem paths and machine timestamps to ensure clean Git diffs across developer workstations.

### Command Matrix

| Command | Lifecycle Phase | Contract |
| --- | --- | --- |
| `devkit bundle validate <source>` | Authoring | Verifies manifest syntax, schema rules, and existence of declared local source files. |
| `devkit bundle build <source> --output <zip>` | Packaging | Produces a deterministic ZIP archive with inventory hashes and normalized file permissions. |
| `devkit plan <source> [--preset <name>]` | Evaluation | Previews desired managed inventory for a local bundle source without inspecting a consumer project. |
| `devkit sync [options]` | Deployment | Discovers installed content packages, computes plan, performs pre-flight conflict checks, executes atomic transaction, and updates receipt. |
| `devkit list [--target <dir>]` | Discovery | Outputs JSON listing installed content packages, bundle metadata, available presets, and synchronized asset paths. |
| `devkit recover [--target <dir>]` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to roll back an interrupted transaction without overwriting newer edits. |

### Sync Options and Modes

- `--agent <name>`: Adds an agent target to active selections (persisted in receipt). Repeatable.
- `--no-agents`: Clears all active agent selections and unlinks unchanged native projections.
- `--preset <bundle>:<name>`: Restricts synchronization for `<bundle>` to `<name>`. Repeatable across bundles.
- `--all-assets`: Clears recorded preset restrictions, restoring full bundle asset deployment.
- `--dry-run`: Computes inventory and returns planned actions without writing to disk.
- `--check`: Read-only execution for CI pipelines. Returns JSON actions and exits with code `1` if workspace requires synchronization.

### Transaction Safety Guarantees (ACID Engine)

All mutating operations enforce strict transactional safety:

1. **Pre-Flight Validation**: Computes the complete desired file inventory, scans existing disk state, verifies file ownership, and checks for collisions before writing any bytes.
2. **Project Advisory Lock**: Acquires an exclusive, non-blocking file lock via `fcntl.flock` in `/tmp` keyed by SHA-256 hash of the target project directory path (`devkit-<uid>-<hash>.lock`). Concurrent operations fail immediately with an informative message.
3. **Write-Ahead Journal**: Before modifying disk, pending operations (file additions, modifications, unlinks) and base64-encoded backups of existing file contents are flushed to `.devkit/transient/sync-journal.json`.
4. **Atomic Replacement**: New and updated files are written to temporary sibling files (`.devkit-write-*`), permissions applied via `fchmod`, flushed with `fsync`, and atomically moved into place using `os.replace`. Directory entries are synced using directory `fsync`.
5. **Rollback Recovery**: If an operation is killed or interrupted mid-flight, subsequent `sync` invocations detect the existing journal and halt. Running `devkit recover` inspects every recorded file and safely restores original contents provided the file has not undergone subsequent user modifications.

---

## 8. Distribution Mechanism and Ecosystem Integration

### The uv Dev Dependency Model

Rather than establishing an external artifact registry or proprietary CLI resolver, `devkit` relies on Python's mature packaging ecosystem:

```bash
# Add distribution CLI and content packages to the project
uv add --dev devkit-distribution devkit-starter package-b-playbooks

# Synchronize resources into the project
uv run devkit sync --agent codex --agent claude-code

# Verify synchronized resources
uv run devkit list
```

#### Why Project-Level Dev Dependencies?
Running `uv tool install --global devkit-distribution` installs the CLI into an isolated tool environment. In that isolated environment, `importlib.metadata` cannot discover content packages installed inside the consumer project's virtual environment. Using `uv run devkit sync` ensures the CLI executes within the project's dev environment, discovering all installed content wheels seamlessly.

#### Upgrades and Teardown
- **Upgrade**: Run `uv lock --upgrade-package <package>`, then run `uv run devkit sync`.
- **Teardown**: Run `uv remove --dev <package>`, then run `uv run devkit sync`.
- **Clean Checkout Replication**: Run `uv sync`, then run `uv run devkit sync`. If the repository ignores managed and native files, `sync` cleanly reconstructs all projections from installed wheels.

---

## 9. Verification and Future Scope

### Verification Commands

All changes in the monorepo must pass standard verification targets:

| Target | Command |
| --- | --- |
| Code Formatting & Linting | `just lint devkit-distribution` |
| Static Type Checking | `just check devkit-distribution` |
| Test Suite | `just test devkit-distribution` |
| Governance Rules | `just rules-check` |

### Test Suite Coverage

The automated test suite in `packages/devkit-distribution/tests/` covers:
- Package and entry-point discovery via `importlib.metadata`.
- Duplicate bundle name rejection across packages.
- Preset filtering, `--all-assets` clearing, and invalid preset rejection.
- Verbatim preservation of native configuration bytes and file modes.
- Re-execution idempotency (no-op runs preserve receipt bytes exactly).
- Update and package removal handling (clean deletion of unedited files).
- Foreign file collision detection and user modification protection.
- Symlink and path traversal security rejections.
- `--dry-run` and `--check` validation.
- ACID transaction execution, lock contention, and rollback recovery via `devkit recover`.

### Implementation Roadmap

```text
Phase 1: Manifest & Local Packaging (Complete)
  ├── bundle.toml schema 1 validation
  ├── Deterministic ZIP packager (devkit bundle build)
  └── Local preview planner (devkit plan)

Phase 2: UV Wheel Distribution & Sync Core (Complete)
  ├── Entry-point discovery via devkit_distribution.bundles
  ├── Workspace layout (.devkit/managed, .devkit/transient)
  ├── Transactional ACID engine with lock, journal & recover
  ├── Installation receipt (.devkit/installation.json)
  └── Native projection adapters for Codex and Claude Code

Phase 3: Project Overrides & Drift Review (Upcoming)
  ├── Project override directory (.devkit/overrides/<bundle>/)
  ├── Baseline upstream digest tracking in receipt
  └── Upstream change detection and interactive drift review

Phase 4: Instruction Integration & Session Hooks (Upcoming)
  ├── Entry-point link injection into AGENTS.md / CLAUDE.md
  ├── Host environment prerequisite auditing (trust, auth)
  └── Custom project asset authoring in .devkit/local/

Phase 5: Rule Engine Plugin API & Runtime Isolation (Upcoming)
  ├── agent-rule-engine dynamic plugin loader for managed rules
  ├── Rule ID collision detection across bundles
  └── rules check and rules fix command dispatch

Phase 6: Multi-Agent Expansion & Ecosystem Validation (Upcoming)
  ├── Antigravity adapter (.agents/rules/, .agents/skills/)
  ├── Live session verification across agent CLIs
  └── End-to-end repository pilot and CI verification
```
