# devkit.distribution

Distribution commands of the `devkit` CLI and runtime for packaging, projecting, and synchronizing AI agent assets across repositories.

---

## 1. Quick Start

Install the distribution CLI and content packages together into your project dev environment via `uv`:

```bash
# Add devkit and content packages
uv add --dev devkit devkit-starter

# The bundles built into devkit (devkit, advisory) are selected by default; select a content bundle
uv run devkit add starter

# Native projections go to Codex, Claude Code and Antigravity by default; narrow them if needed
uv run devkit sync --agent codex --agent claude-code

# Inspect synchronized assets and bundles
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then run `uv run --package devkit devkit sync -w <target-directory>`.

Every distribution command takes `-w/--workspace-root <dir>`. Without it, the project root is the nearest
directory (the current one first, then its parents, up to the Git top level) that contains `.devkit/`, else
the Git top level, else the current directory. Commands print JSON on stdout. Exit code `0` is success,
`1` is returned only by `devkit sync --check` when a synchronization is needed, and `2` is any error. The
commands run on POSIX systems (macOS, Linux); they rely on `fcntl` file locks.

The package also registers the `devkit` guide bundle (`devkit.distribution.guide`), an
instruction-only bundle that tells agents in a consumer repository how devkit-managed assets are
consumed and authored. See [section 4](#4-the-devkit-guide-bundle).

---

## 2. CLI Command Summary

| Command | Category | Description |
| --- | --- | --- |
| `devkit sync [options]` | Lifecycle | Synchronizes selected bundles into `.devkit/managed/`, projects native agent assets, writes seeded files that do not exist yet, maintains the `<!-- DEVKIT:START -->` block in the root `AGENTS.md`, and warns about stray files under the managed root. |
| `devkit add <bundle>[:<preset>]...` | Selection | Selects bundles in `.devkit/config.toml` (default preset when none is named) and synchronizes. |
| `devkit remove <bundle>...` | Selection | Deselects bundles in `.devkit/config.toml` and synchronizes. |
| `devkit list` | Inspection | Outputs JSON listing installed content packages, bundle metadata, presets, selection state, and asset paths. |
| `devkit status` | Inspection | Read-only JSON: managed file counts (`ok`/`missing`/`modified`/`mode-mismatch`), override drift, guidance block state, seeded paths, pending journal, recorded vs running tool version, opted-out built-in bundles. Never writes project files. |
| `devkit recover` | Fault Tolerance | Uses the write-ahead journal in `.devkit/transient/` to safely roll back an interrupted transaction. |
| `devkit get-context <bundle>` | Context | Returns bundle constitution and catalog of instruction headers for progressive loading. |
| `devkit playbook search <query>` | Context | Runs lexical BM25 search over synchronized playbooks. |
| `devkit override list` | Customization | Lists tracked project overrides and their drift status. |
| `devkit override create <bundle>:<asset> [--force]` | Customization | Copies every upstream file of a selected asset to `.devkit/overrides/` (and a baseline copy) and synchronizes; the receipt records the upstream digest. |
| `devkit override diff <bundle>:<asset>` | Customization | Per file: upstream vs override, and recorded baseline vs current upstream. |
| `devkit override accept <bundle>:<asset>` | Customization | Records the current upstream as the override's baseline after review. |
| `devkit override remove <bundle>:<asset>` | Customization | Deletes the override and its baseline and synchronizes the pristine upstream files. |
| `devkit bundle validate <source>` | Authoring | Verifies manifest syntax (`bundle.toml` schema 1), relative file sources and kind-specific headers. |
| `devkit bundle plan <source> [--preset <name>] [--agent <name>]...` | Authoring | Previews every destination a local bundle deploys (managed copies, native projections, generated entry skills, seeded files) without a consumer project. |
| `devkit bundle build <source> --output <zip>` | Packaging | Builds a deterministic ZIP archive with sorted entries and normalized permissions. |

---

## 3. Project Configuration (`.devkit/config.toml`)

Consumer repositories declare which installed bundles to deploy in a Git-tracked `.devkit/config.toml`.
Installing a content wheel only makes its bundle available; such a bundle is deployed only when it has a `[presets]` entry. The bundles built into `devkit` (`devkit`, `advisory`) are deployed with their default preset unless `[presets]` names them or opts out with `<bundle> = false` (`devkit remove` writes it for a built-in bundle; `devkit add` replaces it). `devkit list` marks built-in bundles (`builtin`) and opt-outs (`opted_out`); `devkit status` lists the opt-outs.

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

[workflow]                            # owned by devkit.workflow (layout, approvals, stages); see docs/workflow/reference.md
default = "direct-delivery"

[gates.settings.message-nonempty]     # owned by devkit.gate (enable/disable a gate, its settings); see docs/gate/overview.md
enabled = true

[tool.example]                        # [tool.<name>] is passed through unread for tools built on devkit
option = "on"
```

`devkit add`, `devkit remove`, and the `devkit sync` selection flags edit these entries for you (`--no-save` for a one-off run).
Top-level keys outside this list are rejected, except `[tool.<name>]` tables, which devkit never inspects.
Running `devkit sync` applies the configured agents and presets without repeated CLI flags, and lists installed but unselected bundles.

Every sync also writes a short orientation block into the root `AGENTS.md` between `<!-- DEVKIT:START -->` and
`<!-- DEVKIT:END -->`: the installed bundles, the once-per-bundle `devkit get-context` rule and the generated entry
skills. Text outside the markers is yours and is preserved; the block itself is hash-guarded like a managed file, so
edit it only by changing the selection. Commit `AGENTS.md` with the receipt. See
[Workspace Ownership](workspace-ownership.md#2-ownership-categories-and-invariants).

A bundle can also scaffold project-owned files: a `document` asset with `seeded = true` and a workspace `target`
(for example a `docs/` skeleton or a glossary) is written once, only where the target does not exist, and is then
yours. Sync never compares, updates or removes it, deselecting the bundle leaves it, and the receipt only notes which
asset seeded which path (`devkit list` shows the `seeded` list). Commit seeded files like any project file.
A managed file you edited by hand stops the sync while it is still part of the selection. Once it is no longer
desired (deselected, or removed upstream), sync leaves it in place, forgets it in the receipt and prints
`NOTICE: left modified file in place: <path>`; delete it yourself. The receipt also records the `devkit`
version that wrote it. A different running version alone is not a change: the receipt is rewritten with the
running version, and a `NOTICE` printed, the next time the sync writes anything; `devkit status` shows the mismatch.
Packages built on devkit can register a `devkit.post_sync` entry point (`hook(root, result) -> list[str] | None`)
to react after a successful sync; hooks run after the project lock is released, the strings they return are
printed as notices and never fail the sync. The library surface (`sync_project`, `load_bundle`, `get_context`,
`search_playbooks`, the override operations and their typed results) is exported from `devkit.distribution`.

The `[rules]`, `[workflow]` and `[gates]` tables are owned by `devkit.rules`, `devkit.workflow` and `devkit.gate`
and are passed through untouched by `devkit sync`; see the [Rules Reference](../rules/reference.md#project-configuration),
the [Workflow Reference](../workflow/reference.md#configuration) and the
[Commit Gate Overview](../gate/overview.md#6-configuration-layers). Rules shipped as `kind = "rule"`
assets are recorded in the receipt and loaded by `devkit rules` without flags, and subagents may ship either native
files per agent or one host-neutral role contract that `devkit sync` renders per agent; see
[Native Agent Projections](agent-projections.md).

---

## 4. The `devkit` Guide Bundle

`devkit` ships one bundle of its own, named `devkit`, so that the guidance about devkit
travels with the CLI version it describes. It contains no code assets: a constitution (`AGENTS.md`)
with the consumption contracts and three instructions, delivered to agents through
`devkit get-context devkit`.

| Asset | Read before |
| --- | --- |
| `consumption` | Using, changing or troubleshooting devkit-managed assets: context loading, playbooks, rules and gates, overrides, selection and the sync/receipt lifecycle. |
| `resource-kinds` | Adding a rule, skill, subagent, instruction, playbook, workflow or gate: the decision tree and comparison of asset kinds. |
| `in-repo-bundle` | Adding repository-specific assets: shipping them as a bundle installed from the same repository. |

It is built in: selected by default with its preset `core` (the only one); `uv run devkit remove devkit`
opts the project out. The sources live in `src/devkit/distribution/guide/bundle/` and are validated by the package tests.

---

## 5. Architectural Specifications & Deep-Dives

Detailed technical designs and schemas are documented in `docs/distribution/`:

- [Distribution Architecture Overview](overview.md): Core principles, architecture boundaries, and execution models.
- [Bundle Manifest Specification](manifest-spec.md): `bundle.toml` schema 1, asset kinds, presets, default preset, and validation rules.
- [Workspace Ownership & Overrides](workspace-ownership.md): Ownership invariants, pristine files, collision protection, and override drift review.
- [Synchronization & Transactions (ACID Engine)](sync-and-transactions.md): Write-ahead journal (`sync-journal.json`), advisory locking, atomic replacement, and rollback.
- [Native Agent Projections](agent-projections.md): Projection matrix and adapter rules for Codex, Claude Code, and Antigravity.
- [Context Loading & Playbooks](context-and-playbooks.md): Progressive disclosure, BM25 search, token budgets, and skill integration.
- [Transitive Dependencies](transitive-dependencies.md): Python wheel composition, `[project.dependencies]`, and consumer opt-in.
- [In-Repository Bundles](in-repo-bundles.md): Repository-owned assets shipped as a content package installed from the same repository as a dev dependency.
- [Resource Taxonomy](../architecture/resource-taxonomy.md): Three-tier guidance taxonomy and naming standards.
