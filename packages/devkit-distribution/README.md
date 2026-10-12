# devkit-distribution

Distribution CLI (`devkit`) and runtime for packaging, projecting, and synchronizing AI agent assets across repositories.

---

## 1. Quick Start

Install the distribution CLI and content packages together into your project dev environment via `uv`:

```bash
# Add devkit-distribution and content packages
uv add --dev devkit-distribution devkit-starter

# Select a bundle (recorded in .devkit/config.toml) and synchronize it
uv run devkit add starter

# Project native agent configurations
uv run devkit sync --agent codex --agent claude-code

# Inspect synchronized assets and bundles
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then run `uv run --package devkit-distribution devkit sync --target <target-directory>`.

---

## 2. CLI Command Summary

| Command | Category | Description |
| --- | --- | --- |
| `devkit sync [options]` | Lifecycle | Synchronizes selected bundles into `.devkit/managed/`, projects native agent assets, and warns about stray files under the managed root. |
| `devkit add <bundle>[:<preset>]...` | Selection | Selects bundles in `.devkit/config.toml` (default preset when none is named) and synchronizes. |
| `devkit remove <bundle>...` | Selection | Deselects bundles in `.devkit/config.toml` and synchronizes. |
| `devkit list [--target <dir>]` | Inspection | Outputs JSON listing installed content packages, bundle metadata, presets, selection state, and asset paths. |
| `devkit plan <source> [--preset <name>]` | Authoring | Previews managed inventory for a local bundle without writing to a project. |
| `devkit recover [--target <dir>]` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to safely roll back an interrupted transaction. |
| `devkit get-context <bundle>` | Context | Returns bundle constitution and catalog of instruction headers for progressive loading. |
| `devkit playbook search <query>` | Context | Runs lexical BM25 search over synchronized playbooks. |
| `devkit override list` | Customization | Lists active project overrides and their drift status. |
| `devkit override create <bundle>:<asset>` | Customization | Copies upstream asset to `.devkit/overrides/` and records upstream baseline digest. |
| `devkit override diff <bundle>:<asset>` | Customization | Shows 3-way diff between upstream baseline, updated wheel, and local override. |
| `devkit override accept <bundle>:<asset>` | Customization | Reconciles upstream updates and advances baseline digest. |
| `devkit override remove <bundle>:<asset>` | Customization | Unlinks local override and restores pristine upstream projection. |
| `devkit bundle validate <source>` | Authoring | Verifies manifest syntax (`bundle.toml` schema 1) and relative file sources. |
| `devkit bundle build <source> --output <zip>` | Packaging | Builds a deterministic ZIP archive with sorted entries and normalized permissions. |

---

## 3. Project Configuration (`.devkit/config.toml`)

Consumer repositories declare which installed bundles to deploy in a Git-tracked `.devkit/config.toml`.
Installing a content wheel only makes its bundle available; a bundle is deployed only when it has a `[presets]` entry.

```toml
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter = "daily"                     # a preset name, "all", or an array of presets (union)

[playbooks]
min_score = 0.1
limit = 5
max_bytes = 8192

[rules.phase_overrides]
RULE-markdown-link = "hygiene"

[rules.severity_overrides]
RULE-file-length = "error"

[rules.settings.RULE-file-length]
max_lines = 300
```

`devkit add`, `devkit remove`, and the `devkit sync` selection flags edit these entries for you (`--no-save` for a one-off run).
Running `devkit sync` applies the configured agents and presets without repeated CLI flags, and lists installed but unselected bundles.
The `[rules]` table is owned by `agent-rule-engine` and is passed through untouched by `devkit sync`; see the
[agent-rule-engine README](../agent-rule-engine/README.md#project-configuration). Rules shipped as `kind = "rule"`
assets are recorded in the receipt and loaded by `agent-rules` without flags, and subagents may ship either native
files per agent or one host-neutral role contract that `devkit sync` renders per agent; see
[Native Agent Projections](../../docs/distribution/agent-projections.md).

---

## 4. Architectural Specifications & Deep-Dives

Detailed technical designs and schemas are documented in `docs/distribution/`:

- [Distribution Architecture Overview](../../docs/distribution/overview.md): Core principles, architecture boundaries, and execution models.
- [Bundle Manifest Specification](../../docs/distribution/manifest-spec.md): `bundle.toml` schema 1, asset kinds, presets, default preset, and validation rules.
- [Workspace Ownership & Overrides](../../docs/distribution/workspace-ownership.md): Ownership invariants, pristine files, collision protection, and 3-way drift reconciliation.
- [Synchronization & Transactions (ACID Engine)](../../docs/distribution/sync-and-transactions.md): Write-ahead journal (`sync-journal.json`), advisory locking, atomic replacement, and rollback.
- [Native Agent Projections](../../docs/distribution/agent-projections.md): Projection matrix and adapter rules for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](../../docs/distribution/context-and-playbooks.md): Progressive disclosure, BM25 search, token budgets, and skill integration.
- [Transitive Dependencies](../../docs/distribution/transitive-dependencies.md): Python wheel composition, `[project.dependencies]`, and consumer opt-in.
- [Resource Taxonomy](../../docs/architecture/resource-taxonomy.md): Three-tier guidance taxonomy and naming standards.
