# devkit-distribution

Distribution CLI (`devkit`) and runtime for packaging, projecting, and synchronizing AI agent assets across repositories.

---

## 1. Quick Start

Install the distribution CLI and content packages together into your project dev environment via `uv`:

```bash
# Add devkit-distribution and content packages
uv add --dev devkit-distribution devkit-starter

# Select the devkit guide bundle shipped with this package, then a content bundle
uv run devkit add devkit
uv run devkit add starter

# Native projections go to Codex, Claude Code and Antigravity by default; narrow them if needed
uv run devkit sync --agent codex --agent claude-code

# Inspect synchronized assets and bundles
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then run `uv run --package devkit-distribution devkit sync --target <target-directory>`.

The package also registers the `devkit` guide bundle (`devkit_distribution.guide`), an
instruction-only bundle that tells agents in a consumer repository how devkit-managed assets are
consumed and authored. See [section 4](#4-the-devkit-guide-bundle).

---

## 2. CLI Command Summary

| Command | Category | Description |
| --- | --- | --- |
| `devkit sync [options]` | Lifecycle | Synchronizes selected bundles into `.devkit/managed/`, projects native agent assets, writes seeded files that do not exist yet, maintains the `<!-- DEVKIT:START -->` block in the root `AGENTS.md`, and warns about stray files under the managed root. |
| `devkit add <bundle>[:<preset>]...` | Selection | Selects bundles in `.devkit/config.toml` (default preset when none is named) and synchronizes. |
| `devkit remove <bundle>...` | Selection | Deselects bundles in `.devkit/config.toml` and synchronizes. |
| `devkit list [--target <dir>]` | Inspection | Outputs JSON listing installed content packages, bundle metadata, presets, selection state, and asset paths. |
| `devkit status [--target <dir>]` | Inspection | Read-only JSON: managed file counts (`ok`/`missing`/`modified`/`mode-mismatch`), override drift, guidance block state, seeded paths, pending journal, recorded vs running tool version. Never writes. |
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
agents = ["codex", "claude-code"]     # optional; absent means every supported agent, [] means none
guidance_block = true                 # optional; false stops sync from managing the block in root AGENTS.md
override_drift = "warn"               # optional; "block" aborts sync while an override's upstream has changed

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

[tool.specrig]                        # [tool.<name>] is passed through unread for tools built on devkit
worktree = "on"
```

`devkit add`, `devkit remove`, and the `devkit sync` selection flags edit these entries for you (`--no-save` for a one-off run).
Top-level keys outside this list are rejected, except `[tool.<name>]` tables, which devkit never inspects.
Running `devkit sync` applies the configured agents and presets without repeated CLI flags, and lists installed but unselected bundles.

Every sync also writes a short orientation block into the root `AGENTS.md` between `<!-- DEVKIT:START -->` and
`<!-- DEVKIT:END -->`: the installed bundles, the once-per-bundle `devkit get-context` rule and the generated entry
skills. Text outside the markers is yours and is preserved; the block itself is hash-guarded like a managed file, so
edit it only by changing the selection. Commit `AGENTS.md` with the receipt. See
[Workspace Ownership](../../docs/distribution/workspace-ownership.md#2-ownership-categories-and-invariants).

A bundle can also scaffold project-owned files: a `document` asset with `seeded = true` and a workspace `target`
(for example a `docs/` skeleton or a glossary) is written once, only where the target does not exist, and is then
yours. Sync never compares, updates or removes it, deselecting the bundle leaves it, and the receipt only notes which
asset seeded which path (`devkit list` shows the `seeded` list). Commit seeded files like any project file.
A managed file you edited by hand stops the sync while it is still part of the selection. Once it is no longer
desired (deselected, or removed upstream), sync leaves it in place, forgets it in the receipt and prints
`NOTICE: left modified file in place: <path>`; delete it yourself. The receipt also records the `devkit-distribution`
version that wrote it; the first sync after an upgrade prints a `NOTICE` and `devkit status` shows the mismatch.
Packages built on devkit can register a `devkit.post_sync` entry point (`hook(root, result) -> list[str] | None`)
to react after a successful sync; the strings they return are printed as notices and never fail the sync.

The `[rules]` table is owned by `agent-rule-engine` and is passed through untouched by `devkit sync`; see the
[agent-rule-engine README](../agent-rule-engine/README.md#project-configuration). Rules shipped as `kind = "rule"`
assets are recorded in the receipt and loaded by `agent-rules` without flags, and subagents may ship either native
files per agent or one host-neutral role contract that `devkit sync` renders per agent; see
[Native Agent Projections](../../docs/distribution/agent-projections.md).

---

## 4. The `devkit` Guide Bundle

`devkit-distribution` ships one bundle of its own, named `devkit`, so that the guidance about devkit
travels with the CLI version it describes. It contains no code assets: a constitution (`AGENTS.md`)
with the consumption contracts and three instructions, delivered to agents through
`devkit get-context devkit`.

| Asset | Read before |
| --- | --- |
| `consumption` | Using, changing or troubleshooting devkit-managed assets: context loading, playbooks, rules and gates, overrides, selection and the sync/receipt lifecycle. |
| `resource-kinds` | Adding a rule, skill, subagent, instruction, playbook, workflow or gate: the decision tree and comparison of asset kinds. |
| `in-repo-bundle` | Adding repository-specific assets: shipping them as a bundle installed from the same repository. |

Select it like any other bundle with `uv run devkit add devkit` (preset `core`, the only one). The
sources live in `src/devkit_distribution/guide/bundle/` and are validated by the package tests.

---

## 5. Architectural Specifications & Deep-Dives

Detailed technical designs and schemas are documented in `docs/distribution/`:

- [Distribution Architecture Overview](../../docs/distribution/overview.md): Core principles, architecture boundaries, and execution models.
- [Bundle Manifest Specification](../../docs/distribution/manifest-spec.md): `bundle.toml` schema 1, asset kinds, presets, default preset, and validation rules.
- [Workspace Ownership & Overrides](../../docs/distribution/workspace-ownership.md): Ownership invariants, pristine files, collision protection, and 3-way drift reconciliation.
- [Synchronization & Transactions (ACID Engine)](../../docs/distribution/sync-and-transactions.md): Write-ahead journal (`sync-journal.json`), advisory locking, atomic replacement, and rollback.
- [Native Agent Projections](../../docs/distribution/agent-projections.md): Projection matrix and adapter rules for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](../../docs/distribution/context-and-playbooks.md): Progressive disclosure, BM25 search, token budgets, and skill integration.
- [Transitive Dependencies](../../docs/distribution/transitive-dependencies.md): Python wheel composition, `[project.dependencies]`, and consumer opt-in.
- [In-Repository Bundles](../../docs/distribution/in-repo-bundles.md): Repository-owned assets shipped as a content package installed from the same repository as a dev dependency.
- [Resource Taxonomy](../../docs/architecture/resource-taxonomy.md): Three-tier guidance taxonomy and naming standards.
