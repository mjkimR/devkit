# devkit.distribution

Distribution commands of the `devkit` CLI and runtime for packaging, projecting, and synchronizing AI agent assets across repositories.

---

## 1. Quick Start

Install the distribution CLI and content packages together into your project dev environment via `uv`:

```bash
# Add devkit and content packages
uv add --dev devkit devkit-starter

# devkit and advisory are deployed by default; every other bundle is selected with devkit add
uv run devkit add starter

# Native projections go to Codex, Claude Code and Antigravity by default; narrow them if needed
uv run devkit sync --agent codex --agent claude-code

# Inspect synchronized assets and bundles
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then run `uv run --package devkit devkit sync -w <target-directory>`.

Every distribution command takes `-w/--workspace-root <dir>`. Without it, the project root is the nearest
directory (the current one first, then its parents, up to the Git top level) that contains `.devkit/`, else
the Git top level, else the current directory; a `-w` that is not an existing directory is `ARGUMENT_INVALID`.
Commands print exactly one JSON object on stdout: the result (`override list` wraps its entries as
`{"overrides": [...]}`), or `{"error": {...}}` when the command fails, with the Agent Advisory Protocol block
on stderr. Exit code `0` is success; `1` is returned by `devkit sync --check` when a synchronization is needed
and by `devkit status` when its report shows a problem (a missing, modified or mode-mismatched file, a pending
journal, or override drift); `2` is any error, including an invalid argument such as a malformed
`bundle[:preset]` or `--agent` combined with `--no-agents` (see
[Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)).
`devkit status` reports; `sync --check` remains the check that says whether a sync is needed.

The package also registers the `devkit` guide bundle (`devkit.distribution.guide`), an
instruction-only bundle that tells agents in a consumer repository how devkit-managed assets are
consumed and authored, and opt-in practice bundles. See [section 4](#4-bundles-shipped-with-devkit).

---

## 2. CLI Command Summary

| Command | Category | Description |
| --- | --- | --- |
| `devkit sync [options]` | Lifecycle | Synchronizes selected bundles into `.devkit/managed/`, projects native agent assets, writes seeded files that do not exist yet, maintains the `<!-- DEVKIT:START -->` block in the root `AGENTS.md`, and warns about stray files under the managed root. |
| `devkit add <bundle>[:<preset>]...` | Selection | Adds bundles or presets to the selection in `.devkit/config.toml` (default preset when none is named; presets join those the bundle already deploys) and synchronizes. |
| `devkit remove <bundle>...` | Selection | Deselects bundles in `.devkit/config.toml` and synchronizes. |
| `devkit list` | Inspection | Outputs JSON listing installed content packages, bundle metadata, presets, selection state, and asset paths. |
| `devkit status` | Inspection | Read-only JSON: managed file counts (`ok`/`missing`/`modified`/`mode-mismatch`), override drift, guidance block state, seeded paths, pending journal, recorded vs running tool version, opted-out built-in bundles, and the problems to act on under `errors` (exit `1` when there are any). Never writes project files. |
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
Installing a content wheel only makes its bundle available; such a bundle is deployed only when it has a `[presets]` entry. The bundles built into `devkit` that declare `auto_select` (`devkit`, `advisory`) are deployed with their default preset unless `[presets]` names them or opts out with `<bundle> = false` (`devkit remove` writes it for such a bundle; `devkit add` replaces it). The other built-in bundles (`authoring`, `git-commits`) are opt-in like content bundles. `devkit list` marks built-in bundles (`builtin`), auto-selected ones (`auto_select`) and opt-outs (`opted_out`); `devkit status` lists the opt-outs.

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
`devkit add <bundle>:<preset>` joins the preset to those the bundle already deploys (`devkit add advisory:python`
records `advisory = ["core", "python"]`); `devkit sync --preset` replaces a bundle's presets.
Top-level keys outside this list are rejected, except `[tool.<name>]` tables, which devkit never inspects.
Running `devkit sync` applies the configured agents and presets without repeated CLI flags, and lists installed but unselected bundles.

Every sync also writes a short orientation block into the root `AGENTS.md` between `<!-- DEVKIT:START -->` and
`<!-- DEVKIT:END -->`: the installed bundles, the once-per-bundle `devkit get-context` rule, the generated entry
skills and the `guidance` fragments of the selected bundles, ordered by bundle and asset id (for example the
`git-commits` pointer to the commit conventions). Text outside the markers is yours and is preserved; the block itself
is hash-guarded like a managed file, so edit it only by changing the selection or by overriding a fragment. Commit `AGENTS.md` with the receipt. See
[Workspace Ownership](workspace-ownership.md#2-ownership-categories-and-invariants).

A bundle can also scaffold project-owned files: a `document` asset with `seeded = true` and a workspace `target`
(for example a `docs/` skeleton or a glossary) is written once, only where the target does not exist, and is then
yours. Sync never compares, updates or removes it, deselecting the bundle leaves it, and the receipt only notes which
asset seeded which path (`devkit list` shows the `seeded` list). Commit seeded files like any project file.
A managed file you edited by hand stops the sync while it is still part of the selection. Once it is no longer
desired (deselected, or removed upstream), sync leaves it in place, forgets it in the receipt and reports an
`ORPHAN_LEFT` warning naming it; delete it yourself. The receipt also records the `devkit`
version that wrote it. A different running version alone is not a change: the receipt is rewritten with the
running version, and a `TOOL_VERSION_CHANGED` notice reported, the next time the sync writes anything;
`devkit status` shows the mismatch. Packages built on devkit can register a `devkit.post_sync` entry point
(`hook(root, result) -> list[str | AdvisoryError] | None`) to react after a successful sync; hooks run after the
project lock is released, what they return becomes notices (an `ERROR`-level item is lowered to `WARNING`), and they
never fail the sync. The library surface
(`sync_project`, `load_bundle`, `get_context`, `search_playbooks`, `get_project_status`, `get_project_listing`, the
override operations and their result dataclasses, each with `to_dict()`) is exported from `devkit.distribution`.

### Sync output and notices

`sync`, `add` and `remove` print the `SyncResult` object: `dry_run`, `selection`, `packages`, `assets`, `actions`,
`drift`, `stray`, `unprojected`, `unselected` and `notices`. `drift`, `stray`, `unprojected` and `unselected` are
facts for programs; `notices` holds what the agent must know about them and about the rest of the sync, as
`AdvisoryError` objects at level `WARNING` or `NOTICE` (serialized as `code`, `level`, `message`, `exit_code` `0`,
`advisory`). The library builds every notice, so an embedding caller receives the same list. The CLI prints the
result, then each notice on stderr as a `[WARN]` or `[NOTICE]` block
([Agent Advisory Protocol](../advisory/protocol.md#3-block-format)); `-q` hides the notices, never the warnings, and
`--strict` exits `1` when there is a warning. `override create` and `override remove` carry the notices of the sync
they run in their own `notices` list.

| Code | Level | Class | When | Fields |
| --- | --- | --- | --- | --- |
| `ORPHAN_LEFT` | `WARNING` | `OrphanLeftNotice` | a hand-edited managed file is no longer desired: left in place, dropped from the receipt | `target_files`: the files; `what_to_report`: delete or move them |
| `OVERRIDE_DRIFT` | `WARNING` | `OverrideDriftError.with_level` | an override hides upstream changes (`override_drift = "warn"`) | `target_files`: the overrides; `fix`: `devkit override diff <bundle>:<asset>` |
| `MANAGED_FILE_STRAY` | `WARNING` | `StrayFilesNotice` | files under `.devkit/managed/` that neither the receipt nor the inventory owns | `target_files`: the files; `what_to_report`: move project-owned files out of the managed root |
| `POST_SYNC_HOOK_FAILED` | `WARNING` | `PostSyncHookFailedNotice` | a post-sync hook raised or returned something other than a list | `details`: the hook; `what_to_report`: the failure |
| `SUBAGENT_UNPROJECTED` | `NOTICE` (brief) | `SubagentUnprojectedNotice` | a subagent has no native variant for a selected agent and was not projected | message: each `<bundle>:<asset> (<agent>)`; `target_files`: `.devkit/config.toml` (where the project narrows `agents`); `[DETAIL]`: the remedies |
| `BUNDLE_UNSELECTED` | `NOTICE` | `BundleUnselectedNotice` | installed bundles the project neither selected nor opted out of, reported once per clone when they appear (recorded in `.devkit/transient/seen-bundles.json`) | `fix`: `devkit add <bundle>` for one bundle, else `devkit list`; one `[DETAIL]` per bundle with its exact `devkit add` command and presets |
| `TOOL_VERSION_CHANGED` | `NOTICE` (brief) | `ToolVersionChangedNotice` | the receipt now records a different running `devkit` version (`devkit <recorded> -> <running>`) | — |
| `POST_SYNC_NOTICE` | `NOTICE` (brief) | `PostSyncNotice` | a line a post-sync hook returned | `details`: the hook |

A hook may also return `AdvisoryError` objects with codes of its own; they are kept at their level, except that an
`ERROR` is lowered to `WARNING`, because a hook cannot fail a sync that already wrote its files.

`devkit status` lists what needs acting on under `errors`, each an error object with exit code `1`, and renders
each on stderr as an advisory block: missing managed files (`NOT_SYNCHRONIZED`, fix `devkit sync`), edited or
mode-changed managed files (`SYNC_CONFLICT`), a pending journal (`TRANSACTION_PENDING`, fix `devkit recover`) and
override drift (`OVERRIDE_DRIFT`, `INTERACTION`: review with `devkit override diff`, then `devkit override accept`).

### Error codes

Every error the library raises is an `AdvisoryError`; the CLI renders it as it is. `devkit.core` errors pass
through: an unreadable or invalid `.devkit/installation.json` (including paths devkit never writes) is
`ReceiptError` (`RECEIPT_INVALID`), an invalid `.devkit/config.toml` is `ConfigError` (`CONFIG_INVALID`), and
a malformed selector, query, search bound (`--limit`, `--min-score`, `--max-bytes`), workspace root, archive
`--output` or flag combination is `ArgumentError` (`ARGUMENT_INVALID`, `INPUT_ERROR`). Remediation is in each
error's `fix`, never in its message. The others are `DistributionError` subclasses from `devkit.distribution.errors`:

| Class | Code | Mode | When |
| --- | --- | --- | --- |
| `BundleError` | `BUNDLE_INVALID` | `INPUT_ERROR` | `bundle.toml`, a declared source or an asset header is invalid |
| `PackageError` | `BUNDLE_PACKAGE_INVALID` | `MAINTENANCE` | an installed content package registers an unusable or duplicate bundle |
| `SelectionError` | `SELECTION_INVALID` | `INPUT_ERROR` | an unknown or unselected bundle, preset, asset or override |
| `NotSynchronizedError` | `NOT_SYNCHRONIZED` | `AUTO` (`devkit sync`) | no receipt, or a context file no longer matches it |
| `ConflictError` | `SYNC_CONFLICT` | `INTERACTION` | a hand-edited or unowned file, or an existing override |
| `BundleConflictError` | `BUNDLE_CONFLICT` | `INTERACTION` | two selected bundles, or a seeded and a managed file, claim one path |
| `OverrideDriftError` | `OVERRIDE_DRIFT` | `BLOCKED` | `override_drift = "block"` and an override hides upstream changes |
| `UnsafeWorkspaceError` | `WORKSPACE_UNSAFE` | `BLOCKED` | a symlink or non-regular file where devkit reads or writes, or a reserved path |
| `LockHeldError` | `LOCK_HELD` | `DEFER` | another devkit command holds the project lock |
| `PendingTransactionError` | `TRANSACTION_PENDING` | `AUTO` (`devkit recover`) | an interrupted sync left its journal |
| `RecoveryError` | `RECOVERY_BLOCKED` | `HALT` | the journal is unusable, or later edits block its rollback |
| `GuidanceBlockError` | `GUIDANCE_BLOCK_INVALID` | `INPUT_ERROR` | the root `AGENTS.md` has malformed devkit markers or is not UTF-8 |

The `[rules]`, `[workflow]` and `[gates]` tables are owned by `devkit.rules`, `devkit.workflow` and `devkit.gate`
and are passed through untouched by `devkit sync`; see the [Rules Reference](../rules/reference.md#project-configuration),
the [Workflow Reference](../workflow/reference.md#configuration) and the
[Commit Gate Overview](../gate/overview.md#6-configuration-layers). Rules shipped as `kind = "rule"`
assets are recorded in the receipt and loaded by `devkit rules` without flags, and subagents may ship either native
files per agent or one host-neutral role contract that `devkit sync` renders per agent; see
[Native Agent Projections](agent-projections.md).

---

## 4. Bundles Shipped With devkit

`devkit` ships one bundle of its own, named `devkit`, so that the guidance about devkit
travels with the CLI version it describes. It contains no code assets: a constitution (`AGENTS.md`)
with the consumption contracts and three instructions, delivered to agents through
`devkit get-context devkit`.

| Asset | Read before |
| --- | --- |
| `consumption` | Using, changing or troubleshooting devkit-managed assets: context loading, playbooks, rules and gates, overrides, selection and the sync/receipt lifecycle. |
| `resource-kinds` | Adding a rule, skill, subagent, instruction, playbook, workflow or gate: the decision tree and comparison of asset kinds. |
| `in-repo-bundle` | Adding repository-specific assets: shipping them as a bundle installed from the same repository. |

It is built in: selected by default (`auto_select`) with its preset `core` (the only one); `uv run devkit remove devkit`
opts the project out. The sources live in `src/devkit/distribution/guide/bundle/` and are validated by the package tests.

The other bundles in the package belong to the module whose engine they use:

| Bundle | Selection | Contents |
| --- | --- | --- |
| `advisory` | Auto-selected (`core`) | Agent Advisory Protocol guides; see [devkit.advisory](../advisory/reference.md). |
| `authoring` | Opt-in: `devkit add authoring` (`all`), or one of the presets `skill-authoring`, `agent-guide-authoring` | Size rules and restructuring playbooks for skills and agent guides; see [devkit.rules](../rules/reference.md#built-in-authoring-bundle). |
| `git-commits` | Opt-in: `devkit add git-commits` | Commit message conventions and their `AGENTS.md` pointer; see [devkit.gate](../gate/reference.md#built-in-git-commits-bundle). |

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
