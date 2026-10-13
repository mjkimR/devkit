# devkit.distribution

Distribution commands of the `devkit` CLI: packaging, projecting and synchronizing AI agent assets. The normative
specifications are listed in [section 5](#5-specifications).

---

## 1. Quick Start

```bash
uv add --dev devkit devkit-starter                     # the CLI and a content package
uv run devkit add starter                              # devkit and advisory are deployed by default; select the rest
uv run devkit sync --agent codex --agent claude-code   # projections go to every supported agent unless narrowed
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then `uv run --package devkit devkit sync -w <target-directory>`.

Every distribution command takes `-w/--workspace-root <dir>`. Without it, the project root is the nearest
directory (the current one first, then its parents, up to the Git top level; outside a Git work tree, never the
home directory or above it) that contains `.devkit/`, else the Git top level, else the current directory; a `-w` that is not an existing directory is `ARGUMENT_INVALID`.
`sync`, `add` and `remove` print text by default (see [Sync output and notices](#sync-output-and-notices)) and
take `--format json`. Every other command prints exactly one JSON object on stdout: the result (`override list`
wraps its entries as `{"overrides": [...]}`), or `{"error": {...}}` when the command fails. A JSON result carries
its errors, warnings and notices, so nothing is rendered on stderr in JSON mode; in text mode they are Agent
Advisory Protocol blocks on stderr. Exit code `0` is success; `1` is returned by `devkit sync --check` when a synchronization is needed
and by `devkit status` when its report shows a problem; `2` is any error, including an invalid argument such as a
malformed `bundle[:preset]` or `--agent` combined with `--no-agents` (see
[Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)).

---

## 2. CLI Commands

| Command | Description |
| --- | --- |
| `devkit sync [options]` | Synchronizes the selection: managed copies under `.devkit/managed/`, native projections, seeded files that do not exist yet and the root `AGENTS.md` guidance block, in one transaction ([Synchronization & Transactions](sync-and-transactions.md#3-transaction-safety-guarantees)). |
| `devkit add <bundle>[:<preset>]...` | Joins bundles or presets to the selection in `.devkit/config.toml` (default preset when none is named), then synchronizes. |
| `devkit remove <bundle>...` | Deselects bundles in `.devkit/config.toml` (`false` for an auto-selected bundle), then synchronizes. |
| `devkit list` | Installed content packages, bundle metadata, available and default presets, selection state (`builtin`, `auto_select`, `opted_out`), synchronized asset paths and the `seeded` list. |
| `devkit status` | Read-only report of the installed state against the receipt; see [below](#devkit-status). |
| `devkit recover` | Rolls back an interrupted transaction from the journal in `.devkit/transient/` without overwriting newer edits. Prints `recovered_files`: the number of files restored. |
| `devkit get-context <bundle>` | The bundle constitution and the header catalog of its instructions ([Context Loading](context-and-playbooks.md#2-bundle-context-devkit-get-context)). |
| `devkit playbook search <query>` | Search over synchronized playbook headers: hybrid with the `devkit[search]` extra, else lexical BM25; `--mode`, `--min-score`, `--min-similarity`, `--limit`, `--max-bytes` ([Playbook Search](context-and-playbooks.md#3-playbook-discovery-and-search-devkit-playbook)). |
| `devkit override list` | Tracked project overrides and their drift status. |
| `devkit override create <bundle>:<asset> [--force]` | Copies every upstream file of a selected, non-seeded asset to `.devkit/overrides/` (plus a baseline copy), records the current upstream as its baseline and synchronizes; `--force` overwrites existing override files and the baseline. |
| `devkit override diff <bundle>:<asset>` | Per file: what upstream changed since the baseline, and what the override changed. |
| `devkit override accept <bundle>:<asset>` | Records the current upstream as the override's baseline after review. |
| `devkit override remove <bundle>:<asset>` | Deletes the override and its baseline, then synchronizes the pristine upstream files. |
| `devkit bundle validate <source>` | Verifies `bundle.toml`, the declared sources, the kind-specific headers (instructions, playbooks, workflows, role contracts) and every per-agent rule a sync applies ([Manifest Specification, section 4](manifest-spec.md#4-validation)). `<source>` is the bundle directory. Prints `name`, `version` and `assets` (the number of declared assets). |
| `devkit bundle plan <source> [--preset <name>] [--agent <name>]...` | Previews every destination a local bundle deploys (managed copies, native projections, generated entry skills, seeded files), computed by the same inventory as `sync`, without a consumer project. Defaults: the default preset (else `all`) and every supported agent. Prints `bundle`, `version`, `preset`, `agents`, `assets` (as in the sync result), `files` (`destination`, `sha256`, `mode`) and `seeded` (`destination`, `asset`, `sha256`). |
| `devkit bundle build <source> --output <zip>` | Builds a deterministic ZIP archive ([Manifest Specification, section 5](manifest-spec.md#5-deterministic-local-archive-build)). Prints `path`, `sha256` (of the archive) and `files` (the number of archived files, `inventory.json` included). |

Override semantics are specified in [Workspace Ownership, section 3](workspace-ownership.md#3-project-overrides-and-drift-review).

### Sync Options

- `--agent <name>` (repeatable): narrows the projection targets, recorded as `agents` in `.devkit/config.toml`.
- `--no-agents`: records `agents = []`, which unlinks unchanged native projections and keeps managed copies.
- `--preset <bundle>[:<name>]`: selects `<bundle>` with `<name>` (else its default preset), replacing that bundle's
  entry. Repeat a bundle to select a union; `<bundle>:all` selects every asset.
- `--no-save`: applies the selection flags to this run only, without editing `.devkit/config.toml`.
- `--dry-run`: computes the inventory and returns the planned `actions` without writing files or configuration.
- `--format text|json` (also on `add` and `remove`): the `[SYNC]`/`[CHANGE]` lines (default) or the whole
  `SyncResult` object ([Sync output and notices](#sync-output-and-notices)).
- `--check`: read-only, for CI. Exits `1` when the workspace needs a synchronization (a missing or stale guidance
  block, a seeded file not written yet and a missing `.devkit/.gitignore` included) and `2` on any error (for example a hand-edited managed file,
  `SYNC_CONFLICT`). Existing seeded files are never compared. An orphan alone does not fail `--check`: it is no
  longer managed, so it appears as an `ORPHAN_LEFT` warning on that run and as a `stray` file afterwards if it sits
  under the managed root.

---

## 3. Project Configuration (`.devkit/config.toml`)

The Git-tracked selection. Its keys, the selection rules and their resolution order are specified in
[Synchronization & Transactions, section 2](sync-and-transactions.md#2-asset-selection-model).

```toml
schema = 1
agents = ["codex", "claude-code"]     # optional; absent means every supported agent, [] means none
guidance_block = true                 # optional; false stops sync from managing the block in root AGENTS.md
override_drift = "warn"               # optional; "block" aborts sync while an override's upstream has changed

[presets]
starter = "daily"                     # a preset name, "all", or an array of presets (union)
devkit = false                        # opt out of an auto-selected bundle

[playbooks]
mode = "auto"                         # auto, lexical, dense or hybrid
min_score = 0.1                       # BM25 floor
min_similarity = 0.35                 # cosine floor of dense and hybrid
limit = 5
max_bytes = 8192

[rules.severity_overrides]            # owned by devkit.rules
RULE-file-length = "error"

[workflow]                            # owned by devkit.workflow
default = "direct-delivery"

[worktree]                            # owned by devkit.worktree
pull_request = true

[gates.settings.message-nonempty]     # owned by devkit.gate
enabled = true

[tool.example]                        # [tool.<name>] is passed through unread for tools built on devkit
option = "on"
```

`devkit sync` passes `[rules]`, `[workflow]` and `[gates]` through untouched; see the
[Rules Reference](../rules/reference.md#project-configuration), the
[Workflow Reference](../workflow/reference.md#configuration) and the
[Commit Gate Overview](../gate/overview.md#6-configuration-layers).

### Sync output and notices

`sync`, `add` and `remove` print what the synchronization wrote, or would write under `--dry-run` and `--check`,
never the deployed state it kept, which is the same on every run:

```text
[SYNC: create=1 update=1 remove=0 seed=0 dry_run=no]
[CHANGE: create .claude/skills/review/SKILL.md]
[CHANGE: update .devkit/installation.json]
```

One `[CHANGE: <create|update|remove|seed> <path>]` line follows per write (a path with spaces, quotes or brackets
is a JSON string), and `[OK: the workspace matches the selection]` when there is nothing to write. The warnings
and notices follow on stderr as `[WARN]` and `[NOTICE]` blocks
([Agent Advisory Protocol](../advisory/protocol.md#3-block-format)); `-q` hides the notices, never the warnings, and
`--strict` exits `1` when there is a warning.

`--format json` prints the whole `SyncResult` object instead: `dry_run`, `selection`, `packages`, `assets`,
`actions`, `drift`, `stray`, `unprojected`, `unselected` and `notices`, with nothing on stderr. `drift`, `stray`,
`unprojected` and `unselected` are facts for programs; `notices` holds what the agent must know about them and
about the rest of the sync, as `AdvisoryError` objects at level `WARNING` or `NOTICE` (serialized as `code`,
`level`, `message`, `exit_code` `0`, `advisory`). The library builds every notice, so an embedding caller receives
the same list. `override create` and `override remove` carry the notices of the sync
they run in their own `notices` list.

| Code | Level | Class | When | Fields |
| --- | --- | --- | --- | --- |
| `ORPHAN_LEFT` | `WARNING` | `OrphanLeftNotice` | a hand-edited managed file is no longer desired, or a hand-edited guidance block under `guidance_block = false`: left in place, dropped from the receipt | `target_files`: the files; `what_to_report`: delete or move them |
| `OVERRIDE_DRIFT` | `WARNING` | `OverrideDriftError.with_level` | an override hides upstream changes (`override_drift = "warn"`) | `target_files`: the overrides; `fix`: `devkit override diff <bundle>:<asset>` |
| `MANAGED_FILE_STRAY` | `WARNING` | `StrayFilesNotice` | files under `.devkit/managed/` that neither the receipt nor the inventory owns | `target_files`: the files; `what_to_report`: move project-owned files out of the managed root |
| `POST_SYNC_HOOK_FAILED` | `WARNING` | `PostSyncHookFailedNotice` | a post-sync hook raised or returned something other than a list | `details`: the hook; `what_to_report`: the failure |
| `ASSET_UNPROJECTED` | `NOTICE` (brief) | `UnprojectedNotice` | a skill or subagent has no variant for a selected agent and was not projected | message: each `<bundle>:<asset> (<agent>)`; `target_files`: `.devkit/config.toml` (where the project narrows `agents`); `[DETAIL]`: the remedies |
| `BUNDLE_UNSELECTED` | `NOTICE` | `BundleUnselectedNotice` | installed bundles the project neither selected nor opted out of, reported once per clone when they appear (recorded in `.devkit/transient/seen-bundles.json`) | `fix`: `devkit add <bundle>` for one bundle, else `devkit list`; one `[DETAIL]` per bundle with its exact `devkit add` command and presets |
| `BUNDLE_AUTO_SELECTED` | `NOTICE` | `BundleAutoSelectedNotice` | auto-selected bundles of packages other than `devkit` that the sync deploys with their default preset and the previous receipt does not record | `fix`: `devkit remove <bundle>` (opts out) for one bundle, else `devkit list`; one `[DETAIL]` per bundle with its package and preset; `what_to_report`: the bundles now deployed |
| `TOOL_VERSION_CHANGED` | `NOTICE` (brief) | `ToolVersionChangedNotice` | the receipt now records a different running `devkit` version (`devkit <recorded> -> <running>`) | — |
| `POST_SYNC_NOTICE` | `NOTICE` (brief) | `PostSyncNotice` | a line a post-sync hook returned | `details`: the hook |

Each class above derives from `SyncNotice` (`SYNC_NOTICE`), which is never reported on its own. A post-sync hook may also return `AdvisoryError` objects with codes of its own; they keep their level, except that an
`ERROR` is lowered to `WARNING` ([hooks](sync-and-transactions.md#post-sync-hooks)).

### `devkit status`

`devkit status` never writes project files. It reports the selection, opted-out built-in bundles, managed file
counts (`ok`, `missing`, `modified`, `mode-mismatch`, `unsafe`) with the offending paths, override drift of deployed
assets, the guidance block state (`ok`, `missing`, `modified`, `unowned`, `disabled`, `invalid`), seeded paths and whether each exists, a pending journal,
and the recorded versus running tool version; without a receipt every entry describes an empty installation. What
needs acting on is listed under `errors`, each an error object with exit code `1`: missing managed files (`NOT_SYNCHRONIZED`, fix `devkit sync`), edited or mode-changed managed files
(`SYNC_CONFLICT`), recorded paths that became symlinks or non-regular files (`WORKSPACE_UNSAFE`), a root
`AGENTS.md` that is a symlink, malformed or not UTF-8 while the block is managed (`WORKSPACE_UNSAFE`,
`GUIDANCE_BLOCK_INVALID`; state `invalid`), a selected bundle whose package cannot be used
(`BUNDLE_PACKAGE_INVALID`), a pending journal (`TRANSACTION_PENDING`, fix `devkit recover`) and
override drift (`OVERRIDE_DRIFT`, `INTERACTION`: review with `devkit override diff`, then `devkit override accept`). It exits `1`
when `errors` is nonempty, whatever their own codes, and `2` only when it cannot run (for example an unreadable
receipt or configuration). An installed package the project does not deploy that cannot be used is a
`BUNDLE_PACKAGE_INVALID` warning under `notices` (also in `devkit list`), which changes no exit code except under
`--strict`. `sync --check` remains the check that says whether a sync is needed.

### Error codes

Every error the library raises is an `AdvisoryError`; the CLI renders it as it is. `devkit.core` errors pass
through: an unreadable or invalid `.devkit/installation.json` (including paths devkit never writes) is
`ReceiptError` (`RECEIPT_INVALID`), an invalid `.devkit/config.toml` is `ConfigError` (`CONFIG_INVALID`), and
a malformed selector, query, search bound (`--limit`, `--min-score`, `--max-bytes`), workspace root, archive
`--output` or flag combination is `ArgumentError` (`ARGUMENT_INVALID`, `INPUT_ERROR`). Remediation is in each
error's `fix`, never in its message. The others are `DistributionError` subclasses from `devkit.distribution.errors`:

| Class | Code | Mode | When |
| --- | --- | --- | --- |
| `DistributionError` | `DISTRIBUTION_FAILED` | `MAINTENANCE` | the base class, raised as it is only for an internal defect of `devkit.distribution` |
| `BundleError` | `BUNDLE_INVALID` | `INPUT_ERROR` | `bundle.toml`, a declared source or an asset header is invalid or unreadable; from `bundle validate`, `plan` and `build`, `target_files` names the bundle directory |
| `PackageError` | `BUNDLE_PACKAGE_INVALID` | `MAINTENANCE` | an installed content package registers an unusable, misnamed or duplicate bundle, or its resource module fails to import or load; `fix` names the package to upgrade or uninstall. Only a selected bundle's package (or a duplicate) is an error; any other is a `WARNING` under `notices` ([Content Packages](content-packages.md#1-content-wheel-contract)) |
| `SelectionError` | `SELECTION_INVALID` | `INPUT_ERROR` | an unknown or unselected bundle, preset, asset or override |
| `NotSynchronizedError` | `NOT_SYNCHRONIZED` | `AUTO` (`devkit sync`) | no receipt, or a context file no longer matches it |
| `ConflictError` | `SYNC_CONFLICT` | `INTERACTION` | hand-edited or unowned files (one error names every conflicting path of a sync), or an existing override |
| `BundleConflictError` | `BUNDLE_CONFLICT` | `INTERACTION` | two selected bundles claim one path or one projected skill directory or subagent file, or a seeded and a managed file claim one path |
| `OverrideDriftError` | `OVERRIDE_DRIFT` | `BLOCKED` | `override_drift = "block"` and an override hides upstream changes |
| `UnsafeWorkspaceError` | `WORKSPACE_UNSAFE` | `BLOCKED` | a symlink or non-regular file where devkit reads or writes, or a reserved path |
| `LockHeldError` | `LOCK_HELD` | `DEFER` | another devkit command holds the project lock |
| `PendingTransactionError` | `TRANSACTION_PENDING` | `AUTO` (`devkit recover`) | an interrupted sync left its journal |
| `RecoveryError` | `RECOVERY_BLOCKED` | `HALT` | the journal is unusable, or later edits block its rollback |
| `GuidanceBlockError` | `GUIDANCE_BLOCK_INVALID` | `INPUT_ERROR` | the root `AGENTS.md` has malformed devkit markers or is not UTF-8 |

---

## 4. Bundles Shipped With devkit

`devkit` ships a bundle named `devkit` so that the guidance about devkit travels with the CLI version it describes:
a constitution (`AGENTS.md`) with the consumption contracts and four instructions, delivered through
`devkit get-context devkit`. It is auto-selected with its default preset, `core`, which adds nothing to `AGENTS.md`;
`uv run devkit remove devkit` opts out. The opt-in preset `run` (`uv run devkit add devkit:run`) adds the guidance
fragment `run-pointer`, one `AGENTS.md` line that sends agents to `devkit run` for tests, linters and type checks
and to the `devkit-run` instruction. The sources live in `src/devkit/distribution/guide/bundle/` and are the consumer-facing mirror of these
documents; keep them in step.

| Asset | Read before |
| --- | --- |
| `consumption` | Using, changing or troubleshooting devkit-managed assets: context loading, playbooks, rules and gates, overrides, selection and the sync/receipt lifecycle. |
| `resource-kinds` | Adding a rule, skill, subagent, instruction, playbook, workflow or gate: the decision tree and comparison of asset kinds. |
| `in-repo-bundle` | Adding repository-specific assets: shipping them as a bundle installed from the same repository. |
| `devkit-run` | Running tests, linters or type checks directly, or setting up recipes for them: `devkit run` and its output; see [devkit.compact](../compact/reference.md). |

The other built-in bundles belong to the module whose engine they use:

| Bundle | Selection | Contents |
| --- | --- | --- |
| `advisory` | Auto-selected (`core`) | Agent Advisory Protocol guides; see [devkit.advisory](../advisory/reference.md). |
| `authoring` | Opt-in: `devkit add authoring` (`all`), or one of the presets `skill-authoring`, `agent-guide-authoring` | Size rules and restructuring playbooks for skills and agent guides; see [devkit.rules](../rules/reference.md#built-in-authoring-bundle). |
| `git-commits` | Opt-in: `devkit add git-commits` | Commit message conventions and their `AGENTS.md` pointer; see [devkit.gate](../gate/reference.md#built-in-git-commits-bundle). |

---

## 5. Specifications

- [Overview](overview.md): principles, architecture units, module layout and library surface.
- [Bundle Manifest Specification](manifest-spec.md): `bundle.toml` schema 1, asset kinds, presets, validation and archive builds.
- [Content Packages](content-packages.md): the content wheel contract, installation, upgrades and dependency boundaries.
- [Workspace Ownership & Overrides](workspace-ownership.md): workspace layout, ownership categories, the guidance block, seeded files and override drift.
- [Synchronization & Transactions](sync-and-transactions.md): the receipt, the selection model, and the transaction engine (lock, journal, recovery, post-sync hooks).
- [Native Agent Projections](agent-projections.md): projection matrix and role contracts for Codex, Claude Code and Antigravity.
- [Context Loading & Playbooks](context-and-playbooks.md): `get-context`, the skill prerequisite, and playbook search.
- [In-Repository Bundles](in-repo-bundles.md): repository-owned assets as a content package installed from the same repository.
- [Resource Taxonomy](../architecture/resource-taxonomy.md): guidance taxonomy and naming standards.
