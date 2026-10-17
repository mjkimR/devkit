# devkit.distribution

Distribution commands of the `devkit` CLI: packaging, projecting and synchronizing AI agent assets. The normative
specifications are listed in [section 5](#5-specifications).

---

## 1. Quick Start

```bash
base=https://github.com/mjkimR/devkit/releases/download/v0.1.0
uv add --dev "devkit-agt @ $base/devkit_agt-0.1.0-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-0.1.0-py3-none-any.whl" \
  "devkit-starter @ $base/devkit_starter-0.1.0-py3-none-any.whl"                     # the CLI and a content package
uv run devkit add starter                              # devkit and advisory are deployed by default; select the rest
uv run devkit sync --agent codex --agent claude-code   # projections go to every supported agent unless narrowed
uv run devkit list
```

In this monorepo, run `uv sync --all-packages` first, then `uv run --package devkit-agt devkit sync -w <target-directory>`.

Every distribution command takes `-w/--workspace-root <dir>`. Without it, the devkit root is the Git top level
of the current directory; outside a Git work tree it is the nearest directory (the current one first, then its
parents, never the home directory or above it) that contains `.devkit/`, else the current directory. A `-w` that is
not an existing directory, or one below the top level of a Git work tree, is `ARGUMENT_INVALID`: inside a
repository `.devkit/` lives at the top level only. A `.devkit/` below the top level of a work tree whose top level
has none is `DEVKIT_ROOT_NESTED` ([core reference](core.md)).
`sync`, `add` and `remove` print text by default (see [Sync output and notices](#sync-output-and-notices)) and
take `--format json`. Every other command prints exactly one JSON object on stdout: the result (`override list`
wraps its entries as `{"overrides": [...]}`), or `{"error": {...}}` when the command fails. A JSON result carries
its errors, warnings and notices, so nothing is rendered on stderr in JSON mode; in text mode they are Agent
Advisory Protocol blocks on stderr. Exit code `0` is success; `1` is returned by `devkit sync --check` when a synchronization is needed,
by `devkit sync --locked` when it would change committed files, and by `devkit status` when its report shows a problem; `2` is any error, including an invalid argument such as a
malformed `bundle[:preset]` or `--agent` combined with `--no-agents` (see
`ARCH-08-cross-cutting`).

---

## 2. CLI Commands

Lifecycle `hook` assets use these same bundle and sync commands. Bundle plans include `host_hooks`; project status
includes hook registration problems. Detailed handler and observation inspection is `devkit host status`.
Shared-file ownership, codes and setup: [Host Integration Reference](host.md).

| Command | Description |
| --- | --- |
| `devkit sync [options]` | Synchronizes the selection: managed copies under `.devkit/managed/`, native projections, seeded files that do not exist yet and the root `AGENTS.md` guidance block, in one transaction (`CAP-DIST-sync-and-transactions`). |
| `devkit add <bundle>[:<preset>]...` | Joins bundles or presets to the selection in `.devkit/config.toml` (default preset when none is named), then synchronizes. |
| `devkit remove <bundle>...` | Deselects bundles in `.devkit/config.toml` (`false` for an auto-selected bundle), then synchronizes. |
| `devkit list` | Installed content packages, bundle metadata, available and default presets, selection state (`builtin`, `auto_select`, `opted_out`), synchronized asset paths and the `seeded` list. Like `devkit status` it does not check the recorded paths on disk, so a symlinked managed file never fails it (`devkit status` reports it). |
| `devkit status` | Read-only report of the installed state against the receipt; see [below](#devkit-status). |
| `devkit config template` | Writes the commented template into `.devkit/config.toml`: devkit's top-level keys, common workflow and worktree tables, and the `[tool.<name>]` tables of the installed tools, at defaults or with marked examples when unset, only the parts the file lacks (`CAP-DIST-sync-and-transactions`). Prints `path`, `state` (`created`, `updated`, `unchanged`), `added` (the key and table names written) and `notices`; an invalid file is `CONFIG_INVALID` and is left alone. `--print` writes nothing and adds `text`, the whole file a write would produce. |
| `devkit recover` | Rolls back an interrupted transaction from the journal in `.devkit/transient/` without overwriting newer edits. Prints `recovered_files`: the number of files restored. |
| `devkit get-context <bundle>` | The bundle constitution and the header catalog of its instructions (`CAP-DIST-context-and-playbooks`). |
| `devkit playbook search <query>` | Search over synchronized playbook headers: hybrid with the `devkit-agt[search]` extra, else lexical BM25; `--mode`, `--min-score`, `--min-similarity`, `--limit`, `--max-bytes` (`CAP-DIST-context-and-playbooks`). |
| `devkit override list` | Tracked project overrides and their drift status. |
| `devkit override create <bundle>:<asset> [--force]` | Copies every upstream file of a selected, non-seeded asset to `.devkit/overrides/` (plus a baseline copy), records the current upstream as its baseline and synchronizes; `--force` overwrites existing override files and the baseline. |
| `devkit override diff <bundle>:<asset>` | Per file: what upstream changed since the baseline, and what the override changed. |
| `devkit override accept <bundle>:<asset>` | Records the current upstream as the override's baseline after review. |
| `devkit override remove <bundle>:<asset>` | Deletes the override files of the asset's upstream files and its baseline, then synchronizes the pristine upstream files; any other project file under the override stays (`ORPHAN_LEFT`). |
| `devkit bundle validate <source>` | Verifies `bundle.toml`, the declared sources, the kind-specific headers (instructions, playbooks, workflows, role contracts) and every per-agent rule a sync applies (`CAP-DIST-manifest-spec`). `<source>` is the bundle directory. Prints `name`, `version` and `assets` (the number of declared assets). |
| `devkit bundle plan <source> [--preset <name>] [--agent <name>]...` | Previews every destination a local bundle deploys (managed copies, native projections, generated entry skills, seeded files), computed by the same inventory as `sync`, without a consumer project. Defaults: the default preset (else `all`) and every supported agent. Prints `bundle`, `version`, `preset`, `agents`, `assets` (as in the sync result), `files` (`destination`, `sha256`, `mode`) and `seeded` (`destination`, `asset`, `sha256`). |
| `devkit bundle build <source> --output <zip>` | Builds a deterministic ZIP archive (`CAP-DIST-manifest-spec`). Prints `path`, `sha256` (of the archive) and `files` (the number of archived files, `inventory.json` included). |

Override semantics are specified in `CAP-DIST-workspace-ownership`.

### Sync Options

A missing whole `.codex/hooks.json` can also be restored from unchanged receipt `host_hooks` under `--locked`;
existing shared host files are never edited by locked sync. See `CAP-HOST-lifecycle-observation`.

- `--agent <name>` (repeatable): narrows the projection targets, recorded as `agents` in `.devkit/config.toml`.
- `--no-agents`: records `agents = []`, which unlinks unchanged native projections and keeps managed copies.
- `--preset <bundle>[:<name>]`: selects `<bundle>` with `<name>` (else its default preset), replacing that bundle's
  entry. Repeat a bundle to select a union; `<bundle>:all` selects every asset.
- `--no-save`: applies the selection flags to this run only, without editing `.devkit/config.toml`.
- `--dry-run`: computes the inventory and returns the planned `actions` without writing files or configuration,
  under the shared (reader) project lock.
- `--format text|json` (also on `add` and `remove`): the `[SYNC]`/`[CHANGE]` lines (default) or the whole
  `SyncResult` object ([Sync output and notices](#sync-output-and-notices)).
- `--check`: read-only, for CI, under the shared (reader) project lock. Exits `1` when the workspace needs a synchronization (a missing or stale guidance
  block, a seeded file not written yet and a missing `.devkit/.gitignore` included) and `2` on any error (for example a hand-edited managed file,
  `SYNC_CONFLICT`). Existing seeded files are never compared. An orphan alone does not fail `--check`: it is no
  longer managed, so it appears as an `ORPHAN_LEFT` warning on that run and as a `stray` file afterwards if it sits
  under the managed root.
- `--locked`: for a fresh clone, a new worktree and CI. Restores only the Git-ignored managed copies (and native
  projections a repository ignores) to the committed receipt, exactly as recorded: it creates missing ones, updates
  and removes ones this clone's last sync left unchanged after a pull moved the receipt, and never writes the
  receipt, the root `AGENTS.md` block, seeded files (a deleted one stays missing) or `.devkit/.gitignore`. When the sync
  would change any of them (the installed bundles no longer match the receipt, or there is no receipt), it writes
  nothing and fails with `RECEIPT_STALE` (`INTERACTION`, exit `1`: a negative result, as for `--check`); every other
  error exits `2` as in a plain sync (a missing package is `SELECTION_INVALID`). It runs post-sync extensions only when it committed, and
  takes no other selection or mode flag (`CAP-DIST-sync-and-transactions`).

---

## 3. Project Configuration (`.devkit/config.toml`)

The Git-tracked selection. Its keys, the selection rules and their resolution order are specified in
`CAP-DIST-sync-and-transactions`.

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
pull_request = "required"             # integrate through pull requests only (default "auto")

[gates.settings.message-nonempty]     # owned by devkit.gate
enabled = true

[tool.example]                        # [tool.<name>] is passed through unread for tools built on devkit
option = "on"
```

A selection command that creates the file, and `devkit config template`, write commented managed-scope and update-policy keys,
common workflow and worktree settings, and the registered `[tool.<name>]` tables of installed tools. Values show
defaults, or marked examples when unset by default
(`CAP-DIST-sync-and-transactions`). A template extension that fails is left out
with a `CONFIG_TEMPLATE_EXTENSION_FAILED` warning (`ConfigTemplateExtensionFailedNotice`: it failed to load, raised,
has a name that is not a `[tool.<name>]` name, or returned no valid tables; `what_to_report` names the entry point),
in the command's `notices`, or in the sync result's when a selection command created the file.

`devkit sync` passes `[rules]`, `[workflow]` and `[gates]` through untouched; see the
[Rules Reference](rules.md#project-configuration), the
[Workflow Reference](workflow.md#configuration) and the
`CAP-GATE-commit-gates`.

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
(`CAP-ADV-agent-advisory-protocol`); `-q` hides the notices, never the warnings, and
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
| `ORPHAN_LEFT` | `WARNING` | `OrphanLeftNotice` | a hand-edited managed file is no longer desired, or a hand-edited guidance block under `guidance_block = false`: left in place, dropped from the receipt; or `override remove` left project files under the override that no upstream file of the asset has | `target_files`: the files; `what_to_report`: delete or move them |
| `OVERRIDE_DRIFT` | `WARNING` | `OverrideDriftError.with_level` | an override hides upstream changes (`override_drift = "warn"`) | `target_files`: the overrides; `fix`: `devkit override diff <bundle>:<asset>` |
| `MANAGED_FILE_STRAY` | `WARNING` | `StrayFilesNotice` | files under `.devkit/managed/` that neither the receipt nor the inventory owns | `target_files`: the files; `what_to_report`: move project-owned files out of the managed root |
| `GATE_HOOK_PRESERVED` | `WARNING` | `HookPreservedNotice` | an existing regular Git hook was preserved and chained during automatic installation | `details`: adapter path and unchanged executable mode; reported once when moved |
| `GATE_HOOK_INSTALL_SKIPPED` | `WARNING` | `HookInstallSkippedNotice` | automatic hook installation could not safely run | `details`: reason code and paths; `fix`: remediation |
| `POST_SYNC_EXTENSION_FAILED` | `WARNING` | `PostSyncExtensionFailedNotice` | a post-sync extension raised an exception other than an advisory, or returned something other than a list | `details`: the hook; `what_to_report`: the failure |
| `ASSET_UNPROJECTED` | `NOTICE` (brief) | `UnprojectedNotice` | a skill or subagent has no variant for a selected agent and was not projected | message: each `<bundle>:<asset> (<agent>)`; `target_files`: `.devkit/config.toml` (where the project narrows `agents`); `[DETAIL]`: the remedies |
| `BUNDLE_UNSELECTED` | `NOTICE` | `BundleUnselectedNotice` | installed bundles the project neither selected nor opted out of, reported once per clone when they appear (recorded in `.devkit/transient/seen-bundles.json`) | `fix`: `devkit add <bundle>` for one bundle, else `devkit list`; one `[DETAIL]` per bundle with its exact `devkit add` command and presets |
| `BUNDLE_AUTO_SELECTED` | `NOTICE` | `BundleAutoSelectedNotice` | auto-selected bundles of packages other than `devkit` that the sync deploys with their default preset and the previous receipt does not record | `fix`: `devkit remove <bundle>` (opts out) for one bundle, else `devkit list`; one `[DETAIL]` per bundle with its package and preset; `what_to_report`: the bundles now deployed |
| `TOOL_VERSION_CHANGED` | `NOTICE` (brief) | `ToolVersionChangedNotice` | the receipt now records a different running `devkit` version (`devkit <recorded> -> <running>`) | — |
| `POST_SYNC_NOTICE` | `NOTICE` (brief) | `PostSyncNotice` | a line a post-sync extension returned | `details`: the extension |

Each class above derives from `SyncNotice` (`SYNC_NOTICE`), which is never reported on its own. A post-sync extension may also return `AdvisoryError` objects with codes of its own, or raise one; they keep their level, except that an
`ERROR` is lowered to `WARNING` (`CAP-DIST-sync-and-transactions`).

### `devkit status`

`devkit status` never writes project files. It reports the selection, opted-out built-in bundles, managed file
counts (`ok`, `missing`, `stale`, `modified`, `mode-mismatch`, `unsafe`) with the offending paths, override drift of deployed
assets, the guidance block state (`ok`, `missing`, `modified`, `unowned`, `disabled`, `invalid`), seeded paths and whether each exists, a pending journal,
and the recorded versus running tool version; without a receipt every entry describes an empty installation. What
needs acting on is listed under `errors`, each an error object with exit code `1`: missing managed files and stale ones, as this clone's last sync left them behind a receipt that moved (`NOT_SYNCHRONIZED`, fix `devkit sync`), edited or mode-changed managed files
(`SYNC_CONFLICT`), recorded paths that became symlinks or non-regular files (`WORKSPACE_UNSAFE`), a root
`AGENTS.md` that is a symlink, malformed or not UTF-8 while the block is managed (`WORKSPACE_UNSAFE`,
`GUIDANCE_BLOCK_INVALID`; state `invalid`), a guidance block edited by hand (state `modified`) or not recorded by
the receipt and different from the block a plain `devkit sync` would write (state `unowned`), with the
`SYNC_CONFLICT` and fix `devkit sync` raises for it; an `unowned` block identical to the one sync writes is no
error, since the next sync adopts it without a write (nor is an `unowned` block while that sync cannot be planned:
the sync stops on the planning error first), a selected bundle whose package cannot be used
(`BUNDLE_PACKAGE_INVALID`) or is not installed (`SELECTION_INVALID`, as `devkit sync` raises it, for an entry of
`config.toml` or a bundle the receipt keeps deployed), a pending journal (`TRANSACTION_PENDING`, fix `devkit recover`) and
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
| `PackageError` | `BUNDLE_PACKAGE_INVALID` | `MAINTENANCE` | an installed content package registers an unusable, misnamed or duplicate bundle, or its resource module fails to import or load; `fix` names the package to upgrade or uninstall. Only a selected bundle's package (or a duplicate) is an error; any other is a `WARNING` under `notices` (`CAP-DIST-content-packages`) |
| `SelectionError` | `SELECTION_INVALID` | `INPUT_ERROR` | an unknown or unselected bundle, preset, asset or override, or a selected bundle (by `config.toml`, or deployed per the receipt) whose package is not installed; `fix`: install it (`uv sync`) or `devkit remove <bundle>` |
| `NotSynchronizedError` | `NOT_SYNCHRONIZED` | `AUTO` (`devkit sync`) | no receipt, or a context file no longer matches it |
| `ReceiptStaleError` | `RECEIPT_STALE` | `INTERACTION` | `devkit sync --locked` refused because the committed state no longer matches the installed bundles (no receipt, a changed receipt, a missing or stale guidance block, or a missing `.devkit/.gitignore`); nothing was written and the exit code is `1`. `target_files`: the committed paths that would change (the receipt, `AGENTS.md`, seeded files, `.devkit/.gitignore`); `[DETAIL]`: up to 20 planned writes; `fix`: `devkit sync`, then commit the files it changes, once the user agrees |
| `ConflictError` | `SYNC_CONFLICT` | `INTERACTION` | hand-edited or unowned files (one error names every conflicting path of a sync), or an existing override |
| `BundleConflictError` | `BUNDLE_CONFLICT` | `INTERACTION` | two selected bundles claim one path or one projected skill directory or subagent file, or a seeded and a managed file claim one path |
| `OverrideDriftError` | `OVERRIDE_DRIFT` | `BLOCKED` | `override_drift = "block"` and an override hides upstream changes |
| `UnsafeWorkspaceError` | `WORKSPACE_UNSAFE` | `BLOCKED` | a symlink or non-regular file where devkit reads or writes, a file where a destination's directory must be, or a reserved path |
| `LockHeldError` | `LOCK_HELD` | `DEFER` | another devkit command holds the project lock; also a `devkit.core.LockHeldError`, so catching either class catches it |
| `PendingTransactionError` | `TRANSACTION_PENDING` | `AUTO` (`devkit recover`) | an interrupted sync left its journal |
| `RecoveryError` | `RECOVERY_BLOCKED` | `HALT` | the journal is unusable (one an earlier devkit wrote, without a `directories` entry, is refused with a `fix` to roll back with that version or by hand), or later edits block its rollback |
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
| `devkit-run` | Running tests, linters or type checks directly, or setting up recipes for them: `devkit run` and its output; see [devkit.compact](compact.md). |

The other built-in bundles are documented with the module whose engine they use, but each lives in a data-only
resource module whose `__init__.py` imports nothing, so discovering it never imports that engine (a failing engine
import cannot make the bundle unusable):

| Bundle | Resource module | Selection | Contents |
| --- | --- | --- | --- |
| `advisory` | `devkit.advisory_guide` | Auto-selected (`core`) | Agent Advisory Protocol guides; see [devkit.advisory](advisory.md). |
| `authoring` | `devkit.authoring_guide` | Opt-in: `devkit add authoring` (`all`), or one of the presets `skill-authoring`, `agent-guide-authoring` | Size rules and restructuring playbooks for skills and agent guides; see [devkit.rules](rules.md#built-in-authoring-bundle). |
| `git-commits` | `devkit.commits_guide` | Opt-in: `devkit add git-commits` | Commit message conventions and their `AGENTS.md` pointer; see [devkit.gate](gate.md#built-in-git-commits-bundle). |

---

## 5. Specifications

- `ARCH-05-4-distribution-components`: principles, architecture units, module layout and library surface.
- `CAP-DIST-manifest-spec`: `bundle.toml` schema 1, asset kinds, presets, validation and archive builds.
- `CAP-DIST-content-packages`: the content wheel contract, installation, upgrades and dependency boundaries.
- `CAP-DIST-workspace-ownership`: workspace layout, ownership categories, the guidance block, seeded files and override drift.
- `CAP-DIST-sync-and-transactions`: the receipt, the selection model, and the transaction engine (lock, journal, recovery, post-sync extensions).
- `CAP-DIST-agent-projections`: projection matrix and role contracts for Codex, Claude Code and Antigravity.
- `CAP-DIST-context-and-playbooks`: `get-context`, the skill prerequisite, and playbook search.
- `CAP-DIST-in-repo-bundles`: repository-owned assets as a content package installed from the same repository.
- `ARCH-08-2-resource-taxonomy`: guidance taxonomy and naming standards.
