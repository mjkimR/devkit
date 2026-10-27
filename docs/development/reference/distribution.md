# devkit_dist.features.distribution

Distribution commands of the `devkit` CLI: packaging, projecting and synchronizing AI agent assets. They ship in
the `devkit-dist` wheel with project support, `devkit_dist.features.search`, `devkit_dist.features.host` and the root command line; the harness
commands of `devkit-agt` mount under the same executable. The normative specifications are listed in
[section 5](#5-specifications).

---

## 1. Quick Start

```bash
base=https://github.com/mjkimR/devkit/releases/download/v<version>
uv add --dev "devkit-dist @ $base/devkit_dist-<version>-py3-none-any.whl" \
  "devkit-core @ $base/devkit_core-<version>-py3-none-any.whl" \
  "devkit-cli @ $base/devkit_cli-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl" \
  "devkit-starter @ $base/devkit_starter-0.1.0-py3-none-any.whl"                     # the CLI and a content package
uv run devkit add starter                              # devkit and advisory are deployed by default; select the rest
uv run devkit sync --agent codex --agent claude-code   # projections go to every supported agent unless narrowed
uv run devkit list
```

`devkit-agt` (the harness) depends on `devkit-dist` at the same version; a Git installation declares one of them, never
both, and a release-wheel installation of `devkit-agt` names the `devkit-dist`, `devkit-core`, `devkit-cli` and `devkit-advisory`
wheels next to it only because no index serves them.
In this monorepo, run `uv sync --all-packages` first, then `uv run --package devkit-dist devkit sync -w <target-directory>`.

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
by `devkit sync --locked` when it would change committed files, by `devkit status` when its report shows a problem,
and for `CONFIG_LOCAL_CHANGED` or `CONFIG_LOCAL_RENDER_STALE`. Other failures use their advisory exit status,
usually `2`, including an invalid argument such as a
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
| `devkit remove <bundle>...` | Deselects bundles in `.devkit/config.toml` (`false` for an auto-selected bundle), then synchronizes; a removed bundle's override directory stays and is named in `OVERRIDE_RETAINED`. |
| `devkit list` | Installed content packages, bundle metadata, available and default presets, selection state (`builtin`, `auto_select`, `opted_out`), synchronized asset paths and the `seeded` list. Like `devkit status` it does not check the recorded paths on disk, so a symlinked managed file never fails it (`devkit status` reports it). |
| `devkit status` | Read-only report of the installed state against the receipt; see [below](#devkit-status). |
| `devkit config show [--effective]` | Read-only effective checkout preferences (shared `.devkit/config.toml` with the ignored `.devkit/config.local.toml` over it, then defaults): `configuration`, `sources` (the workspace-relative file, or `default`, behind each dotted key), `execution_environment`, `presentation_language` and `notices` (`PRESENTATION_LANGUAGE_UNSUPPORTED`). `--effective` is the default and is accepted as is. |
| `devkit config template` | Writes the commented template into `.devkit/config.toml`: devkit's top-level keys, the tables installed engines register for the reserved names (`devkit.config_tables`: `[workflow.approvals]`, `[workflow.stages]` and `[worktree]` with `devkit-agt`), and the `[tool.<name>]` tables of the installed tools, at defaults or with marked examples when unset, only the parts the file lacks, keeping the bytes and line endings of existing lines (`CAP-DIST-sync-and-transactions`). Prints `path`, `state` (`created`, `updated`, or `unchanged` exactly when the file's bytes stay the same), `added` (every key and table name written, commented ones included) and `notices`; an invalid file is `CONFIG_INVALID` and is left alone. `--print` writes nothing and adds `text`, the whole file a write would produce. |
| `devkit recover` | Rolls back an interrupted transaction from the journal in `.devkit/transient/` without overwriting newer edits. Prints `recovered_files`: the number of files restored. |
| `devkit get-context <bundle>` | The bundle constitution, the header catalog of its instructions and the `documents` list of its declared context directory (`CAP-DIST-context-and-playbooks`). |
| `devkit playbook get <bundle>/<playbook>` | Exact receipt-backed retrieval by asset ID or declared alias (an exact ID wins; `alias` names the alias used; an alias several effective headers declare is `PLAYBOOK_ALIAS_AMBIGUOUS`): complete body, effective metadata, source path/hash and context requirements. JSON-only, no execution or discovery (`CAP-DIST-context-and-playbooks`). |
| `devkit playbook search <query>` | Search over synchronized playbook `name` and `description` (aliases are identifiers, never ranked): hybrid with the `search` extra (`devkit-dist[search]` or `devkit-agt[search]`), else lexical BM25; `--mode`, `--min-score`, `--min-similarity`, `--limit`, `--max-bytes` (`CAP-DIST-context-and-playbooks`). |
| `devkit override list` | Tracked project overrides: `bundle`, `asset`, `kind`, `relative_path` and `drift_detected`. The digests that decide the flag stay in the receipt. |
| `devkit override create <bundle>:<asset> [--force]` | Copies every upstream file of a selected, non-seeded asset to `.devkit/overrides/` (plus a baseline copy), records the current upstream as its baseline and synchronizes; `--force` overwrites existing override files and the baseline. |
| `devkit override diff <bundle>:<asset>` | Per file: what upstream changed since the baseline, and what the override changed; with `drift_detected`, no digests. |
| `devkit override accept <bundle>:<asset>` | Records the current upstream as the override's baseline after review, then synchronizes (as `create` does), returning the sync's notices; under `override_drift = "block"` with other overrides still drifting it only records the baseline (`OVERRIDE_SYNC_DEFERRED`). |
| `devkit override remove <bundle>:<asset>` | Deletes the override files of the asset's upstream files and its baseline, then synchronizes the pristine upstream files; any other project file under the override stays (`ORPHAN_LEFT`). |
| `devkit bundle validate <source>` | Verifies `bundle.toml`, the declared sources, the kind-specific headers (instructions, playbooks, workflows, role contracts) and every per-agent rule a sync applies (`CAP-DIST-manifest-spec`). `<source>` is the bundle directory. Prints `name`, `version` and `assets` (the number of declared assets). |
| `devkit bundle plan <source> [--preset <name>] [--agent <name>]...` | Previews every destination a local bundle deploys (managed copies, native projections, generated entry skills, seeded files), computed by the same inventory as `sync`, without a consumer project. Defaults: the default preset (else `all`) and every supported agent. Prints `bundle`, `version`, `preset`, `agents`, `assets` (as in the sync result), `files` (`destination`, `sha256`, `mode` as an octal string such as `"0644"`) and `seeded` (`destination`, `asset`, `sha256`). An unknown `--preset` is `SELECTION_INVALID` targeting `--preset`, with the plan command without `--preset` as its fix and one `[DETAIL]` plan command per declared preset. |

Override semantics are specified in `CAP-DIST-workspace-ownership`.

### Sync Options

A missing whole `.codex/hooks.json` can also be restored from unchanged receipt `host_hooks` under `--locked`;
existing shared host files are never edited by locked sync. See `CAP-HOST-lifecycle-observation`.

- `--agent <name>` (repeatable): narrows the projection targets, recorded as `agents` in `.devkit/config.toml`.
- `--no-agents`: records `agents = []`, which unlinks unchanged native projections and keeps managed copies.
- `--preset <bundle>[:<name>]`: selects `<bundle>` with `<name>` (else its default preset), replacing that bundle's
  entry. Repeat a bundle to select a union; `<bundle>:all` selects every asset.
- `--no-save`: applies selection/environment flags to this run only, without saving shared selection or local environment.
- `--cloud` / `--local`: mutually exclusive checkout environment selection; ordinary sync preserves the saved value.
- `--dry-run`: computes the inventory and returns the planned `actions` without writing files or configuration,
  under the shared (reader) project lock.
- `--format text|json` (also on `add` and `remove`): the `[SYNC]`/`[CHANGE]` lines (default) or the whole
  `SyncResult` object ([Sync output and notices](#sync-output-and-notices)).
- `--check`: read-only, for CI, under the shared (reader) project lock, without the post-sync preview `--dry-run` runs. Exits `1` when the workspace needs a synchronization (a missing or stale guidance
  block, a seeded file not written yet and a missing `.devkit/.gitignore` included), and says so with a
  `NOT_SYNCHRONIZED` error (fix `uv run devkit sync`, exit `1`): in text the last stderr block, after the result;
  in JSON under `errors`, which a `--check` result always carries (empty when nothing is needed). Concurrent configuration
  changes also exit `1` (`CONFIG_LOCAL_CHANGED`); other failures use their advisory exit status, such as `2` for
  a hand-edited managed file (`SYNC_CONFLICT`). Existing seeded files are never compared. An orphan alone does not fail `--check`: it is no
  longer managed, so it appears as an `ORPHAN_LEFT` warning on that run and as a `stray` file afterwards if it sits
  under the managed root.
- `--locked`: for a fresh clone, a new worktree and CI. Restores only the Git-ignored managed copies (and native
  projections a repository ignores) to canonical or validated personal output: it creates missing ones, updates
  and removes ones this clone's last sync left unchanged after a pull moved the receipt, and never writes the
  receipt, the root `AGENTS.md` block, seeded files (a deleted one stays missing) or `.devkit/.gitignore`. When the sync
  would change any of them (the installed bundles no longer match the receipt, or there is no receipt), it writes
  nothing and fails with `RECEIPT_STALE` (`INTERACTION`, exit `1`: a negative result, as for `--check`); each other
  error follows its code-specific exit status as in a plain sync: concurrent configuration changes are
  `CONFIG_LOCAL_CHANGED` (exit `1`), and a missing package is `SELECTION_INVALID` (exit `2`). It runs post-sync extensions only when it committed, and
  permits `--cloud` or `--local` to save the environment in the ignored local file, but no selection flag,
  `--dry-run`, `--check` or `--no-save` (`CAP-DIST-sync-and-transactions`).

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

[rules.severity_overrides]            # owned by devkit_agt.features.rules
RULE-file-length = "error"

[workflow]                            # owned by devkit_agt.features.workflow
default = "direct-delivery"

[worktree]                            # owned by devkit_agt.features.worktree
pull_request = "required"             # integrate through pull requests only (default "auto")

[gates.settings.message-nonempty]     # owned by devkit_agt.features.gate
enabled = true

[tool.example]                        # [tool.<name>] is passed through unread for tools built on devkit
option = "on"
```

A selection command that creates the file, and `devkit config template`, write commented managed-scope and update-policy keys,
the tables installed engines register for the reserved top-level names (`devkit.config_tables`, entry point named
after the table: devkit-agt registers `workflow` and `worktree`), and the registered `[tool.<name>]` tables of
installed tools (`devkit.config_template`). Values show defaults, or marked examples when unset by default
(`CAP-DIST-sync-and-transactions`). A template extension that fails is left out
with a `CONFIG_TEMPLATE_EXTENSION_FAILED` warning (`ConfigTemplateExtensionFailedNotice`: it failed to load, raised,
has a name that is not a `[tool.<name>]` name, or for `devkit.config_tables` not a reserved table, or returned no
valid tables; `what_to_report` names the entry point), in the command's `notices`, or in the sync result's when a
selection command created the file.

`devkit sync` passes the reserved tables `[rules]`, `[workflow]`, `[gates]`, `[worktree]` and `[integration]` through
untouched, whether or not `devkit-agt` is installed; see the
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
is a JSON string), `.devkit/config.toml` included when a selection command creates or changes it (also under
`--dry-run`, which renders the edit without writing it), and `[OK: the workspace matches the selection]` when there
is nothing to write. A command named in a `[FIX]` or `[DETAIL]` line is written as the agent runs it, `uv run devkit
...` (`ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`). The warnings
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
| `OVERRIDE_DRIFT` | `WARNING` | `override_drift` (`OverrideDriftError`) | an override hides upstream changes (`override_drift = "warn"`); also in `devkit status` `notices`, the same advisory | one advisory for every drifted override. `target_files`: their workspace-relative override files (`.devkit/overrides/<bundle>/...`); for one override `fix` is its `uv run devkit override diff <bundle>:<asset>` and `[DETAIL]` its `override accept`; for several `fix` is `uv run devkit override list` and `[DETAIL]` each `diff` and `accept` |
| `OVERRIDE_RETAINED` | `NOTICE` | `OverrideRetainedNotice` | `devkit remove` deselected a bundle whose `.devkit/overrides/<bundle>/` directory stays (applied again, with drift, when the bundle is selected again) | `target_files`: the directories; `fix`: `uv run devkit add <bundle>:<preset>...` with the presets the bundles deployed; `[DETAIL]`: delete the directories to drop the overrides |
| `OVERRIDE_SYNC_DEFERRED` | `NOTICE` | `OverrideSyncDeferredNotice` | `override accept` under `override_drift = "block"` recorded the baseline without synchronizing because other deployed overrides still drift; `sync --check` may report pending work until the last accept | message: the remaining overrides; `fix` and `[DETAIL]`: their `override diff` and `override accept` commands, as for `OVERRIDE_DRIFT` |
| `MCP_REGISTRATION_PENDING` | `NOTICE` | `McpRegistrationPendingNotice` | `sync --locked` left the desired local MCP registration of a selected host unwritten; also in `devkit status` `notices` while a synchronized checkout (one with a receipt) lacks it | message: the hosts; `fix`: `uv run devkit sync --registrations-only` |
| `MANAGED_FILE_STRAY` | `WARNING` | `StrayFilesNotice` | files under `.devkit/managed/` that neither the receipt nor the inventory owns | `target_files`: the files; `what_to_report`: move project-owned files out of the managed root |
| `GATE_HOOK_PRESERVED` | `WARNING` | `HookPreservedNotice` | an existing regular Git hook was preserved and chained during automatic installation | `details`: adapter path and unchanged executable mode; reported once when moved |
| `GATE_HOOK_INSTALL_SKIPPED` | `WARNING` | `HookInstallSkippedNotice` | automatic hook installation could not safely run | `details`: reason code and paths; `fix`: remediation |
| `POST_SYNC_EXTENSION_FAILED` | `WARNING` | `PostSyncExtensionFailedNotice` | a post-sync extension raised an exception other than an advisory, or returned something other than a list | `details`: the hook; `what_to_report`: the failure |
| `PRESENTATION_LANGUAGE_UNSUPPORTED` | `WARNING` | `PresentationLanguageUnsupportedNotice` | a shared or local `[presentation] language` other than `auto`, `en` or `ko` fell back to `en`; also returned by `devkit status` and `devkit config show` | `target_files`: the configuration file; `fix`: the accepted values and the file |
| `ASSET_UNPROJECTED` | `NOTICE` (brief) | `UnprojectedNotice` | a skill or subagent has no variant for a selected agent and was not projected | message: each `<bundle>:<asset> (<agent>)`; `target_files`: `.devkit/config.toml` (where the project narrows `agents`); `[DETAIL]`: the remedies |
| `BUNDLE_UNSELECTED` | `NOTICE` | `BundleUnselectedNotice` | installed bundles the project neither selected nor opted out of, reported once per clone when they appear (recorded in `.devkit/transient/seen-bundles.json`); never by `sync --locked`, which restores a committed selection | `fix`: `uv run devkit add <bundle>` for one bundle, else `uv run devkit list`; one `[DETAIL]` per bundle with its exact `uv run devkit add` command and presets |
| `HARNESS_ENGINE_MISSING` | `WARNING` | `HarnessEngineMissingNotice` | deployed `rule`, `gate` or `workflow` assets in an installation with no `devkit.commands` entry point named `rules`, `gate` or `workflow` (devkit-agt not installed); the assets are deployed as selected. Also in `devkit status` `notices` | message: each bundle with its kinds; `[DETAIL]`: one line per bundle; `fix`: the install directive that adds `devkit-agt` (shared with `HARNESS_COMMAND_UNAVAILABLE`, [core reference](core.md)) |
| `BUNDLE_AUTO_SELECTED` | `NOTICE` | `BundleAutoSelectedNotice` | auto-selected bundles of packages other than the first-party `devkit-dist` and `devkit-agt` that the sync deploys with their default preset and the previous receipt does not record | `fix`: `uv run devkit remove <bundle>` (opts out) for one bundle, else `uv run devkit list`; one `[DETAIL]` per bundle with its package and preset; `what_to_report`: the bundles now deployed |
| `TOOL_VERSION_CHANGED` | `NOTICE` (brief) | `ToolVersionChangedNotice` | the receipt now records a different running tool: `devkit-dist <recorded> -> <running>`, or with both packages when the package changed (`devkit-agt 0.1.1 -> devkit-dist 0.1.1`) | — |
| `POST_SYNC_NOTICE` | `NOTICE` (brief) | `PostSyncNotice` | a line a post-sync extension returned | `details`: the extension |

Each class above derives from `SyncNotice` (`SYNC_NOTICE`), which is never reported on its own. A post-sync extension may also return `AdvisoryError` objects with codes of its own, or raise one; they keep their level, except that an
`ERROR` is lowered to `WARNING` (`CAP-DIST-sync-and-transactions`).

### `devkit status`

`devkit status` never writes project files. It reports the selection, opted-out built-in bundles, managed file
counts (`ok`, `missing`, `stale`, `modified`, `mode-mismatch`, `unsafe`) with the offending paths (a state's path list
appears only when it names a path), override drift of deployed assets, the guidance block state (`ok`, `missing`,
`modified`, `unowned`, `disabled`, `invalid`), seeded paths as `{"counts": {"present", "missing"}, "missing": [...]}`
(each missing entry with `bundle`, `id` and `path`; the list appears only when one is missing), a pending journal,
and the recorded versus running tool version; without a receipt every entry describes an empty installation. What
needs acting on is listed under `errors`, each an error object with exit code `1`: missing managed files and stale ones, as this clone's last sync left them behind a receipt that moved (`NOT_SYNCHRONIZED`, fix `uv run devkit sync`), edited or mode-changed managed files
(`SYNC_CONFLICT`), recorded paths that became symlinks or non-regular files (`WORKSPACE_UNSAFE`), a root
`AGENTS.md` that is a symlink, malformed or not UTF-8 while the block is managed (`WORKSPACE_UNSAFE`,
`GUIDANCE_BLOCK_INVALID`; state `invalid`), a guidance block edited by hand (state `modified`) or not recorded by
the receipt and different from the block a plain `devkit sync` would write (state `unowned`), with the
`SYNC_CONFLICT` and fix `devkit sync` raises for it; an `unowned` block identical to the one sync writes is no
error, since the next sync adopts it without a write (nor is an `unowned` block while that sync cannot be planned:
the sync stops on the planning error first), a selected bundle whose package cannot be used
(`BUNDLE_PACKAGE_INVALID`) or is not installed (`SELECTION_INVALID`, as `devkit sync` raises it, for an entry of
`config.toml` or a bundle the receipt keeps deployed), a pending journal (`TRANSACTION_PENDING`, fix `uv run devkit recover`) and,
under `override_drift = "block"`, override drift (`OVERRIDE_DRIFT`, `INTERACTION`: review with `uv run devkit override
diff`, then `uv run devkit override accept`). It exits `1`
when `errors` is nonempty, whatever their own codes, and `2` only when it cannot run (for example an unreadable
receipt or configuration). An installed package the project does not deploy that cannot be used is a
`BUNDLE_PACKAGE_INVALID` warning under `notices` (also in `devkit list`), and deployed rule, gate or workflow assets
that no installed engine runs are a `HARNESS_ENGINE_MISSING` warning there, and override drift under the default
`override_drift = "warn"` is the `OVERRIDE_DRIFT` warning `devkit sync` reports; none changes the exit code except
under `--strict`. A selected host whose desired local MCP registration this checkout lacks (a fresh clone after
`sync --locked`) is the `MCP_REGISTRATION_PENDING` notice; a checkout without a receipt has no such notice, since
its next step, a plain `devkit sync`, registers too. Like every JSON-only command, status renders nothing on
stderr: its `errors` and `notices` are in the result. `sync --check` remains the check that says whether a sync is needed.

### Error codes

Every error the library raises is an `AdvisoryError`; the CLI renders it as it is. Foundation and project errors pass
through: an unreadable or invalid `.devkit/installation.json` (including paths devkit never writes) is
`ReceiptError` (`RECEIPT_INVALID`), an invalid `.devkit/config.toml` is `ConfigError` (`CONFIG_INVALID`), and
a malformed selector, query, search bound (`--limit`, `--min-score`, `--max-bytes`), workspace root, archive
`--output` or flag combination is `ArgumentError` (`ARGUMENT_INVALID`, `INPUT_ERROR`). Remediation is in each
error's `fix`, never in its message. The others are `DistributionError` subclasses from `devkit_dist.features.distribution.models.errors`:

| Class | Code | Mode | When |
| --- | --- | --- | --- |
| `DistributionError` | `DISTRIBUTION_FAILED` | `MAINTENANCE` | the base class, raised as it is only for an internal defect of `devkit_dist.features.distribution` |
| `BundleError` | `BUNDLE_INVALID` | `INPUT_ERROR` | `bundle.toml`, a declared source or an asset header is invalid or unreadable; from `bundle validate`, `plan` and `build`, `target_files` names the bundle directory |
| `PackageError` | `BUNDLE_PACKAGE_INVALID` | `MAINTENANCE` | an installed content package registers an unusable, misnamed or duplicate bundle, or its resource module fails to import or load; `fix` names the package to upgrade or uninstall. Only a selected bundle's package (or a duplicate) is an error; any other is a `WARNING` under `notices` (`CAP-DIST-content-packages`) |
| `SelectionError` | `SELECTION_INVALID` | `INPUT_ERROR` | an unknown or unselected bundle, preset, asset or override, or a selected bundle (by `config.toml`, or deployed per the receipt) whose package is not installed. `target_files` names the argument that named it (`SELECTIONS` of `add`, `--preset` of `sync` and `bundle plan`, `BUNDLES` of `remove`, `SELECTOR` of `override`, `BUNDLE_NAME` of `get-context`, `PLAYBOOK_ID` of `playbook get`), or the file (`.devkit/config.toml`, `.devkit/installation.json`) for a selection the project records. `fix` is one exact command: `uv run devkit remove <names>` for an uninstalled selected bundle (installing its package is a `[DETAIL]`), `uv run devkit add <bundle>` for an installed bundle `get-context` finds unselected, and otherwise `uv run devkit list`, with one `[DETAIL]` per preset in the caller's own form (`uv run devkit add <bundle>:<preset>`, `uv run devkit sync --preset <bundle>:<preset>`, `uv run devkit bundle plan <source> --preset <preset>`) when a preset is unknown or has to be named |
| `PlaybookAliasAmbiguousError` | `PLAYBOOK_ALIAS_AMBIGUOUS` | `INPUT_ERROR` | `devkit playbook get <bundle>/<alias>`: more than one effective playbook header of the bundle (overrides included) declares the alias; `target_files` names the declaring playbooks; `fix`: name the exact asset ID or keep the alias on one playbook |
| `NotSynchronizedError` | `NOT_SYNCHRONIZED` | `AUTO` (`devkit sync`) | no receipt, or a context file no longer matches it |
| `ReceiptStaleError` | `RECEIPT_STALE` | `INTERACTION` | `devkit sync --locked` refused because the committed state no longer matches the installed bundles (no receipt, a changed receipt, a missing or stale guidance block, or a missing `.devkit/.gitignore`); nothing was written and the exit code is `1`. `target_files`: the committed paths that would change (the receipt, `AGENTS.md`, seeded files, `.devkit/.gitignore`); `[DETAIL]`: up to 20 planned writes; `fix`: `uv run devkit sync`, once the user agrees; `what_to_report` asks whether to run it and commit what it changes |
| `ConflictError` | `SYNC_CONFLICT` | `INTERACTION` | hand-edited or unowned files (one error names every conflicting path of a sync), or an existing override (`fix`: `uv run devkit override create <bundle>:<asset> --force`). For managed files edited by hand (`managed files were edited: ...`, from `sync` and `status` alike) `fix` keeps the edits: move the files aside, run `uv run devkit override create <bundle>:<asset>` for each asset that deploys them, then copy the edits into the override files; discarding them is the `[DETAIL]` |
| `BundleConflictError` | `BUNDLE_CONFLICT` | `INTERACTION` | two selected bundles claim one path or one projected skill directory or subagent file, or a seeded and a managed file claim one path; when two bundles collide, `what_to_report` names both and each `[DETAIL]` is the `uv run devkit remove <bundle>` that deselects one |
| `OverrideDriftError` | `OVERRIDE_DRIFT` | `INTERACTION` | `override_drift = "block"` and an override hides upstream changes: whether the override takes over the change is the user's decision. `devkit sync` raises it (exit `2`) and `devkit status` lists it under `errors` (exit `1`), with the fields of the warning above |
| `UnsafeWorkspaceError` | `WORKSPACE_UNSAFE` | `BLOCKED` | a symlink or non-regular file where devkit reads or writes, a file where a destination's directory must be, or a reserved path |
| `LockHeldError` | `LOCK_HELD` | `DEFER` | another devkit command holds the project lock; also a `devkit_core.base.errors.LockHeldError`, so catching either class catches it |
| `PendingTransactionError` | `TRANSACTION_PENDING` | `AUTO` (`devkit recover`) | an interrupted sync left its journal |
| `RecoveryError` | `RECOVERY_BLOCKED` | `HALT` | the journal is unusable (one an earlier devkit wrote, without a `directories` entry, is refused with a `fix` to roll back with that version or by hand), or later edits block its rollback |
| `GuidanceBlockError` | `GUIDANCE_BLOCK_INVALID` | `INPUT_ERROR` | the root `AGENTS.md` has malformed devkit markers or is not UTF-8 |

---

## 4. Bundles Shipped With devkit

`devkit-dist` ships a bundle named `devkit` so that the guidance about devkit travels with the CLI version it
describes: a constitution (`AGENTS.md`) with the consumption contracts and three instructions, delivered through
`devkit get-context devkit`. It describes distribution only and names no harness command as a directive. It is
auto-selected with its default and only preset, `core`, which adds nothing to `AGENTS.md`; `uv run devkit remove
devkit` opts out. The sources live in `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/` and are the
consumer-facing mirror of these documents; keep them in step.

| Asset | Read before |
| --- | --- |
| `consumption` | Using, changing or troubleshooting devkit-managed assets: context loading, playbooks, overrides, selection and the sync/receipt lifecycle. |
| `resource-kinds` | Adding a rule, skill, subagent, instruction, playbook, workflow or gate: the decision tree and comparison of asset kinds. |
| `in-repo-bundle` | Adding repository-specific assets: shipping them as a bundle installed from the same repository. |

`devkit-agt` ships the `harness` bundle (`CAP-DIST-content-packages`), auto-selected wherever it is installed: a
constitution with the rules-and-gates and snapshot-gate contracts and the guidance for the harness. Its default
preset `core` adds nothing to `AGENTS.md`; the opt-in preset `run` (`uv run devkit add harness:run`) adds the
guidance fragment `run-pointer`, one `AGENTS.md` line that sends agents to `devkit run` for tests, linters and type
checks and to the `devkit-run` instruction. Its sources live in `packages/devkit/src/devkit_agt/bundles/harness/bundle/`.

| Asset | Read before |
| --- | --- |
| `harness-consumption` | Running, configuring or troubleshooting rules, commit gates or delivery workflows: their configuration tables, the `devkit-workflow` entry skill, `devkit rules`, `devkit gate` and snapshot gates. |
| `harness-assets` | Adding or testing a rule, gate or workflow asset, including the rules of an in-repository bundle in Git snapshot gates. |
| `devkit-run` | Running tests, linters or type checks directly, or setting up recipes for them: `devkit run` and its output; see [devkit_agt.features.compact](compact.md). |

Bundles shipped by `devkit-dist` or `devkit-agt` count as built in (`builtin` in `devkit list` and
`devkit status`). The other built-in bundles are documented with the module whose engine they use, but each lives in
a data-only resource module whose `__init__.py` imports nothing, so discovering it never imports that engine (a
failing engine import cannot make the bundle unusable):

| Bundle | Wheel | Resource module | Selection | Contents |
| --- | --- | --- | --- | --- |
| `advisory` | `devkit-dist` | `devkit_dist.bundles.advisory` | Auto-selected (`core`); `devkit add advisory:python` for Python repositories | Agent Advisory Protocol guides and, in `python`, `RULE-advisory-unique-code` (run by the rule engine of `devkit-agt`); see [devkit.advisory](advisory.md). |
| `git-commits` | `devkit-dist` | `devkit_dist.bundles.git_commits` | Opt-in: `devkit add git-commits` | Commit message conventions and their `AGENTS.md` pointer; see [devkit_agt.features.gate](gate.md#built-in-git-commits-bundle). |
| `authoring` | `devkit-agt` | `devkit_agt.bundles.authoring` | Opt-in: `devkit add authoring` (`all`), or one of the presets `skill-authoring`, `agent-guide-authoring` | Size rules and restructuring playbooks for skills and agent guides, the `agent-asset-writing` instruction and its wording rule; see [devkit_agt.features.rules](rules.md#built-in-authoring-bundle). |
| `harness` | `devkit-agt` | `devkit_agt.bundles.harness` | Auto-selected (`core`); `devkit add harness:run` for the `AGENTS.md` pointer | The harness guidance above. |

---

## 5. Specifications

- `ARCH-05-4-distribution-components`: principles, architecture units, module layout and library surface.
- `CAP-DIST-manifest-spec`: `bundle.toml` schema 1, asset kinds, presets, validation and archive builds.
- `CAP-DIST-content-packages`: the content wheel contract, installation, upgrades and dependency boundaries.
- `CAP-DIST-workspace-ownership`: workspace layout, ownership categories, the guidance block, seeded files and override drift.
- `CAP-DIST-sync-and-transactions`: the receipt, the selection model, and the transaction engine (lock, journal, recovery, post-sync extensions).
- `CAP-DIST-agent-projections`: projection matrix and role contracts for Codex, Claude Code and Antigravity.
- `CAP-DIST-context-and-playbooks`: `get-context`, the skill prerequisite, and playbook search/exact retrieval.
- `CAP-DIST-in-repo-bundles`: repository-owned assets as a content package installed from the same repository.
- `ARCH-08-2-resource-taxonomy`: guidance taxonomy and naming standards.

## Configurable Markdown templates

For instruction, guidance, document and skill assets, `name.md.jinja` renders to `name.md`; ordinary Markdown stays
literal. A skill directory contains exactly one of `SKILL.md` or `SKILL.md.jinja`; native projections always expose
`SKILL.md`.
Declare typed `[variables.<identifier>]` inputs in `bundle.toml` and set project values under
`[bundles.<bundle>.variables]` in `.devkit/config.toml`, then `devkit sync`. Templates use `{{ vars.language }}`.
The engine loads only during rendering. See `CAP-DIST-manifest-spec` for syntax and restrictions and
`CAP-DIST-sync-and-transactions` for input resolution, overrides and receipt behavior.


## Checkout-local preferences

Edit ignored `.devkit/config.local.toml` for `[execution].environment`, `[mcp].register`, `[playbooks]` search
preferences and `[bundles.<bundle>.variables]` scalar inputs. `devkit config show --effective` shows
values and source paths. Governance and bundle selection remain shared. `devkit sync --cloud` selects cloud;
`devkit sync --local` explicitly returns to local. Neither grants approval authority.

Personal rendering may change only ignored untracked human-readable asset kinds, preserving canonical receipt,
guidance and seeds. Details and persistence behavior: `CAP-DIST-sync-and-transactions`.

| Code | Exit | Action |
| --- | --- | --- |
| `CONFIG_LOCAL_KEY_FORBIDDEN` | 2 | Remove the local governance/selection/unknown key. |
| `CONFIG_LOCAL_NOT_IGNORED` | 2 | Untrack the named personal path and correct its effective ignore rule. |
| `CONFIG_LOCAL_RENDER_FORBIDDEN` | 2 | Remove the local variable or separate its shared template use. |
| `CONFIG_LOCAL_RENDER_STALE` | 1 | Run sync to refresh local evidence and output. |
| `CONFIG_LOCAL_CHANGED` | 1 | Finish concurrent configuration edits and rerun sync. |

For shared or personal approval/response defaults, set `[presentation] language = "ko"` (`auto`, `en`, `ko`)
in shared config or ignored `.devkit/config.local.toml`. `devkit config show --effective` reports the requested and
resolved language, source and fallback; another value falls back to `en`, which `devkit sync`, `devkit status`
and `devkit config show` report as a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning. Run sync for response-style
assets; approval forms read per request.
Explicit response-style bundle variables win. See `CAP-DIST-sync-and-transactions` and `CAP-INT-mcp-services`;
this does not localize host-owned controls or establish visible native Korean form support.
