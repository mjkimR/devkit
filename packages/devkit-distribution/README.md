# devkit-distribution

Distribution CLI (`devkit`) and runtime for packaging, projecting, and synchronizing AI agent assets across repositories.

---

## 1. Quick Start

Install the distribution CLI and content packages together into your project dev environment via `uv`:

```bash
# Add devkit-distribution and content packages
uv add --dev devkit-distribution devkit-starter

# Synchronize managed assets and project native agent configurations
uv run devkit sync --agent codex --agent claude-code

# Inspect synchronized assets and bundles
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then run `uv run --package devkit-distribution devkit sync --target <target-directory>`.

---

## 2. CLI Command Summary

| Command | Category | Description |
| --- | --- | --- |
| `devkit sync [options]` | Lifecycle | Synchronizes installed content wheels into `.devkit/managed/` and projects native agent assets. |
| `devkit list [--target <dir>]` | Inspection | Outputs JSON listing installed content packages, bundle metadata, presets, and asset paths. |
| `devkit inventory [--target <dir>]` | Inspection | Previews planned file inventories without modifying the filesystem. |
| `devkit recover [--target <dir>]` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to safely roll back an interrupted transaction. |
| `devkit get-context <bundle>` | Context | Returns bundle constitution and catalog of instruction headers for progressive loading. |
| `devkit playbook search <query>` | Context | Runs lexical BM25 search over synchronized playbooks. |
| `devkit explain-playbook <id>` | Context | Displays full markdown procedure and metadata for a specific playbook. |
| `devkit read <path> [--max-bytes N]` | Context | Safely reads managed file contents bounded by byte budget. |
| `devkit override list` | Customization | Lists active project overrides and their drift status. |
| `devkit override create <bundle>:<asset>` | Customization | Copies upstream asset to `.devkit/overrides/` and records upstream baseline digest. |
| `devkit override diff <bundle>:<asset>` | Customization | Shows 3-way diff between upstream baseline, updated wheel, and local override. |
| `devkit override accept <bundle>:<asset>` | Customization | Reconciles upstream updates and advances baseline digest. |
| `devkit override remove <bundle>:<asset>` | Customization | Unlinks local override and restores pristine upstream projection. |
| `devkit validate <path>` | Authoring | Verifies manifest syntax (`bundle.toml` schema 1) and relative file sources. |
| `devkit pack <path> -o <zip>` | Packaging | Builds a deterministic ZIP archive with sorted entries and normalized permissions. |

---

## 3. Project Configuration (`.devkit/config.toml`)

Consumer repositories can author an optional Git-tracked `.devkit/config.toml` to define baseline selections:

```toml
schema = 1
agents = ["codex", "claude-code"]
exclude_bundles = ["experimental-bundle"]

[presets]
starter = "daily"

[playbooks]
min_score = 0.1
limit = 5
max_bytes = 8192
```

Running `devkit sync` automatically applies configured agents, presets, and exclusions without requiring repeated CLI flags.

---

## 4. Architectural Specifications & Deep-Dives

Detailed technical designs and schemas are documented in `docs/distribution/`:

- [Distribution Architecture Overview](../../docs/distribution/overview.md): Core principles, architecture boundaries, and execution models.
- [Bundle Manifest Specification](../../docs/distribution/manifest-spec.md): `bundle.toml` schema 1, asset kinds, presets, and validation rules.
- [Workspace Ownership & Overrides](../../docs/distribution/workspace-ownership.md): Ownership invariants, pristine files, collision protection, and 3-way drift reconciliation.
- [Synchronization & Transactions (ACID Engine)](../../docs/distribution/sync-and-transactions.md): Write-ahead journal (`sync-journal.json`), advisory locking, atomic replacement, and rollback.
- [Native Agent Projections](../../docs/distribution/agent-projections.md): Projection matrix and adapter rules for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](../../docs/distribution/context-and-playbooks.md): Progressive disclosure, BM25 search, token budgets, and skill integration.
- [Transitive Dependencies](../../docs/distribution/transitive-dependencies.md): Python wheel composition, `[project.dependencies]`, and consumer opt-outs.
- [Resource Taxonomy](../../docs/architecture/resource-taxonomy.md): Three-tier guidance taxonomy and naming standards.
