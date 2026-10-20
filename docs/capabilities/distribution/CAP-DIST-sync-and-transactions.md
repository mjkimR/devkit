---
id: CAP-DIST-sync-and-transactions
title: "Synchronization & Transactions"
summary: "Transactional deployment of bundle assets, atomic journal safety, recovery, the receipt and configuration formats devkit-dist owns, the selection model, and sync and status notices."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit/distribution/installation/inventory.py
  - packages/devkit-dist/src/devkit/distribution/installation/overrides.py
  - packages/devkit-dist/src/devkit/distribution/installation/engines.py
  - packages/devkit-dist/src/devkit/distribution/installation/config_template.py
created_at: 2026-10-17
---

# [CAP-DIST-sync-and-transactions] Synchronization and Transactions

## 1. The Installation Receipt (`.devkit/installation.json`)

Selected lifecycle hooks also record an optional `host_hooks` array, each entry containing `host`, qualified
`asset`, `event`, `handler`, `command`, `matcher` and integer `timeout`. These records own exact groups in shared host
configuration; the shared file is never claimed by `files`. See `CAP-HOST-lifecycle-observation`.

The receipt is the single record of the installed state, committed to Git, `schema = 1`:

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
      "starter": ["daily"]
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
  "overrides": {
    "starter": {
      "development": {
        "kind": "instruction",
        "relative_path": "instructions/development.md",
        "baseline_upstream_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "override_sha256": "8f434346648f6b96df8932b12bc85d0d12e624c92ee24041b6179b0051280879"
      }
    }
  },
  "files": {
    ".devkit/managed/starter/bundle.toml": {
      "mode": 420,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  },
  "guidance_block": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "seeded": [
    { "bundle": "starter", "id": "docs-skeleton", "path": "docs/README.md" }
  ],
  "tool": { "package": "devkit-dist", "version": "0.1.1" }
}
```

- `packages`: package and bundle names and versions of **selected** bundles only.
- `selection`: the effective agents and presets the last sync applied. It is an audit record, never read back as a
  selection input.
- `assets`: each deployed asset's workspace paths. A seeded asset has an empty `paths` and a `seeded` array of its
  targets.
- `files`: SHA-256 and mode (`0644` or `0755`) of every deployed file. Modes are compared by their execute bit only.
- `overrides`: tracked overrides per asset, with the digests defined in
  `CAP-DIST-workspace-ownership`. An override of an asset that is later
  not deployed (its bundle deselected, its preset narrowed) keeps its record while its files remain, so drift is still
  reported when the asset is selected again.
- `guidance_block`: the SHA-256 of the root `AGENTS.md` block (markers included, LF line endings); absent under
  `guidance_block = false`. `AGENTS.md` itself is never listed under `files`.
- `seeded`: for every selected seeded asset, the paths it seeds (bundle, asset id, path), sorted by path; present
  only while such an asset is selected, informational, never a selection input.
- `tool`: the distributor that wrote the receipt, `devkit-dist` (`ADR-dist-config-receipt-ownership`). A different
  running tool alone is not a change: a sync with nothing else to do keeps the receipt byte for byte (so
  `sync --check` stays clean across teammates on different versions); the next sync that writes anything records the
  running tool with a `TOOL_VERSION_CHANGED` notice, which names the package on both sides when it changed (a receipt
  written by the single `devkit-agt` wheel of earlier releases: `devkit-agt 0.1.1 -> devkit-dist 0.1.1`). A mismatch
  never refuses anything, an older receipt stays readable (the schema version does not change), and the version pin
  lives in `uv.lock`. Each bundle's `packages` record names the wheel that ships it.

The receipt format (`devkit.core.receipt`) and its writer belong to `devkit-dist`, as does the
`.devkit/config.toml` schema below.

The receipt holds no absolute paths or timestamps. It is read with the strict reader of `devkit.core.receipt`
(unknown keys, wrong types, non-canonical or escaping paths are `RECEIPT_INVALID`) plus distribution ownership
rules: `files` may only name managed or projected destinations, and asset `paths` only those or the bundle's own
`.devkit/overrides/<bundle>/` files.

## 2. Asset Selection Model

Installing a package makes its bundle **available**. A bundle that declares `auto_select`
(`CAP-DIST-manifest-spec`) is also **selected** with its
`default_preset` from then on, whether the package was added directly or arrived as a runtime dependency of another
one, until `.devkit/config.toml` names it (other presets) or sets it to `false` (opted out). Every other bundle is
selected only by an entry in `config.toml`. Among the built-in bundles (`CAP-DIST-content-packages`), `devkit` and
`advisory` of `devkit-dist` and `harness` of `devkit-agt` are auto-selected; `git-commits` and `authoring` are not. The rationale is recorded in
`ARCH-08-2-resource-taxonomy`.

### Project Configuration (`.devkit/config.toml`, `schema = 1`)

```toml
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter = "daily"                       # one preset
advisory = ["core", "python"]           # union of several presets
team-backend = "all"                    # reserved preset: every asset
devkit = false                          # opt out of an auto-selected bundle
```

- **Top-level keys**: `schema`, `agents`, `presets`, `playbooks`, `rules`, `workflow`, `gates`, `worktree`,
  `integration`, `guidance_block`, `override_drift`, `bundles`, `tool`; anything else is `CONFIG_INVALID`. The list is
  the same whether or not `devkit-agt` is installed, so a configuration reads the same in both installations and
  typos are still caught.
- **`schema`**: optional; `1` is the only version. `devkit add` writes it when it creates the file.
- **`agents`**: the projection targets. Absent, every supported agent (`antigravity`, `claude-code`, `codex`);
  `[]` (written by `devkit sync --no-agents`) turns projection off while managed copies stay.
- **`[presets]`**: the selection. A bundle with an entry is synchronized with the presets it names; an
  auto-selected bundle without one is synchronized with its `default_preset`; no other bundle is synchronized. The value is a preset name or a
  nonempty array of unique preset names (the union of their assets); `all` is reserved in every bundle. `false`
  opts an auto-selected bundle out, and is allowed for a bundle that is not installed (it then takes effect if the
  package arrives later). A bundle selected by an entry that no installed package provides is an error: install it
  or `devkit remove` it. So is a bundle the receipt records as deployed without an entry, once its package is no
  longer installed ([below](#unselected-and-auto-selected-bundles)).
- **`guidance_block`**: `false` stops `devkit sync` from managing the root `AGENTS.md` block (default `true`).
- **`override_drift`**: `"warn"` (default) or `"block"`; see
  `CAP-DIST-workspace-ownership`.
- **`[playbooks]`**: search defaults; see `CAP-DIST-context-and-playbooks`.
- **`[rules]`, `[workflow]`, `[gates]`, `[worktree]`, `[integration]`**: reserved names owned by `devkit.rules`,
  `devkit.workflow`, `devkit.gate`, `devkit.worktree` and `devkit.integration` (`devkit-agt`); passed through
  untouched, never read by distribution.
- **`[tool.<name>]`**: the extension namespace, as in `pyproject.toml`. A tool built on devkit keeps its own policy
  there and reads it itself; devkit only checks that `<name>` matches `[a-z][a-z0-9_-]*` and the value is a table,
  so a mistyped devkit key elsewhere is still an error.

### Commented Template

A selection command that creates `config.toml`, and `devkit config template` for an existing one, write commented managed-scope and update-policy keys, the
tables installed engines register for the reserved names (with `devkit-agt`: workflow and worktree settings), and
the registered tables of installed tools. Values show defaults; settings unset by default show marked examples:

```toml
schema = 1

## devkit project configuration, tracked by Git. A commented key shows its default: uncomment it to change it. ...

## Managed scope: what devkit sync deploys, and for which agents.
## [presets] selects bundles: <bundle> = "<preset>", an array of presets, or "all"; ...
# agents = ["antigravity", "claude-code", "codex"]  # array of agent names; agents that skills and subagents ...
# guidance_block = true  # boolean; devkit sync manages the DEVKIT block of the root AGENTS.md

## Update policy: how devkit sync takes upstream changes.
# override_drift = "warn"  # "warn" or "block"; upstream changed a file a project override replaces: ...

[presets]
spec = "core"

## Workflow approval gates: names come from workflow definitions; the gate below is an example.
# [workflow.approvals]
#   integration = "ask"  # ask | auto | off; approve integrating the change into the base

## Workflow stages: policies apply by stage id; unset stages use on.
# [workflow.stages]
#   collect-feedback = "on"  # on | off; set off to skip feedback collection

## Git worktree behavior.
# [worktree]
#   pull_request = "auto"  # "auto" | "required"; required refuses worktree finish --merge
#   delete_branch = true   # boolean; delete the merged branch with git branch -d
#   setup = "uv sync"      # example; string; unset: no setup command
#   stale_after = "14d"    # "<N>d" | "<N>w"; idle plan-*/dev-* branches are reported

## [tool.spec]: the settings of devkit-spec; devkit passes [tool.*] tables through unread.
# [tool.spec]
#   worktree = true  # boolean; route 2 and above (formal specs, proposals) run in a task worktree

## The work-scope registry of `devkit spec scope`.
# [tool.spec.scope]
#   namespace = "team"  # example; string of letters, ...; unset: a hash of the Git common directory
#   timeout = 10  # integer from 1 to 300; seconds one registry command may wait
```

- **Layout**: as in the `CAP-GATE-commit-gates`, prose is commented twice
  (`##`), keys and table headers once (`#`), so uncommenting a whole table yields valid TOML and leaves the prose a
  comment. A key unset by default shows an example marked `example;`; an array of tables (`[[...]]`) shows example
  values.
- **devkit's keys**: `agents` and `guidance_block` (managed scope, with a note on `[presets]`) and `override_drift`
  (update policy), at the defaults `read_config` applies. They go right after the file's last top-level key, because
  TOML reads a key below a table header as part of that table; a file without top-level keys gets them first. A
  commented `agents` lists the agents devkit supports now; leaving it unset also projects for those a later devkit
  adds.
- **Reserved tables**: a package registers a callable under the `devkit.config_tables` entry-point group, named
  after a reserved top-level table, returning `list[devkit.core.TemplateTable]` with paths below that table. devkit
  renders them after the project's tables and before tool tables, in entry-point name order and without an intro
  line. `devkit-agt` registers `workflow` (`[workflow.approvals]` with the gate name `integration` at `ask`,
  `[workflow.stages]` with `collect-feedback` at `on`: representative names, not a fixed schema) and `worktree`
  (`pull_request = "auto"`, `delete_branch = true`, `stale_after = "14d"`, no setup command; `setup = "uv sync"` is
  marked as an example), so each template lives with the engine that applies it and a standalone `devkit-dist`
  template shows no harness table. With `devkit-agt` installed these tables render right after the project's tables
  and before any `[tool.*]` table, in the order and text shown above (`ADR-dist-config-receipt-ownership`). See `CAP-DLV-workflow-orchestration` and `CAP-WT-task-worktrees` for their
  behavior.
- **Tool tables**: a package registers a callable under the `devkit.config_template` entry-point group, named after
  its `[tool.<name>]` table. Called with no argument, it returns `list[devkit.core.TemplateTable]`
  ([Core Reference](../../development/reference/core.md#modules)); devkit renders the headers from the entry-point name, so a tool
  never writes outside its own table, and the template is the same for every project. The tables go at the end of
  the file in entry-point name order, after one intro line per tool naming its package.
- **Append-only**: a key whose name the file mentions (set, or in any comment) and a table whose header the file
  mentions (commented or not) or defines (dotted keys included) are left out, so no line is changed or removed and
  an uncommented line stays where the developer put it. A part deleted from the file is added again by the next
  `devkit config template`. A file that cannot be read or does not validate (`CONFIG_INVALID`) is never written.
- **Selection edits**: a new `agents` or `[presets]` entry goes right after the last key-value entry of its table,
  not after the comments that follow it, so a commented tool table never takes the entry as its own once
  uncommented.
- **Failures**: an extension that fails to load, raises, is not named like a `[tool.<name>]` table
  (`devkit.config_template`) or a reserved table (`devkit.config_tables`), or returns anything but valid tables is
  left out with a `CONFIG_TEMPLATE_EXTENSION_FAILED` warning, and the command succeeds; when a selection command created the file, the warning joins the sync result's `notices`.
- **Preview**: `devkit config template --print` writes nothing (no file, no `.devkit/`, no lock file) and adds
  `text`, the whole file a write would produce, to the output; `state` and `added` are those the write would report,
  and an invalid file is `CONFIG_INVALID` as for a write.
- `devkit sync` never adds to the template; after installing a tool, `devkit config template` adds its tables.

### Resolution Order

1. **CLI selection**: `--agent`, `--no-agents` and `--preset` on `devkit sync`, and `devkit add` / `devkit remove`,
   edit the matching entries of `config.toml` (preserving unrelated tables, comments and formatting), then
   synchronize. `--no-save` applies the flags to one run; `--dry-run` and `--check` never edit the file.
2. **`config.toml`**: the only persistent selection input. The receipt is not a resolution tier.
3. **Defaults**: every supported agent, the installed auto-selected bundles with their default preset, no other
   bundles, playbook search `limit=5`, `min_score=0.1`, `max_bytes=8192`.

### Selecting a Bundle

```bash
devkit add starter                # records the resolved default preset, e.g. starter = "daily"
devkit add advisory:python        # joins the named preset: advisory = ["core", "python"]
devkit add starter:review starter:release  # several presets at once
devkit remove starter             # deselects; unchanged deployed files are removed
```

- `devkit add` joins the named presets to those the bundle already deploys (its entry, or the default preset of an
  auto-selected bundle), existing presets first, and never drops one; without a preset it uses `default_preset`
  (`CAP-DIST-manifest-spec`), and a bundle without one needs an
  explicit preset. `devkit add` replaces a `false` entry.
- `devkit sync --preset <bundle>:<preset>` replaces the bundle's presets.
- `devkit remove` deletes the entry of a bundle that is not auto-selected and writes `false` for an auto-selected
  one. A bundle the receipt keeps deployed without an installed package gets neither: the sync drops it from the
  receipt, and a later install of the package selects it again like any new one.
- The **resolved** preset name is written, never a symbolic default, so an upstream change to `default_preset`
  does not change an explicit selection. An auto-selected bundle without an entry follows its current
  `default_preset`; `devkit add <bundle>` pins it.
- Selection commands render their edit under the project lock, from `config.toml` as it is then (so concurrent
  selection commands never lose an edit), check that the file can be rewritten (a regular file, not a symlink, in a
  writable directory), and plan from that selection in memory. The configuration edit commits through the same journal as outputs and local environment changes. Post-sync extensions see the committed selection.

### Unselected and Auto-Selected Bundles

Every `devkit sync` lists installed bundles that are not selected under `unselected` (bundle, package, available
presets, default preset, and `opted_out` when set to `false`). The `BUNDLE_UNSELECTED` notice announces only the
bundles neither selected nor opted out of that this clone has not been told about: a writing sync (not `--dry-run`
or `--check`) records the installed names in the Git-ignored `.devkit/transient/seen-bundles.json`, and a missing or
unreadable record only repeats the announcement. An opted-out bundle is never announced.

The `BUNDLE_AUTO_SELECTED` notice names the auto-selected bundles of packages other than the first-party
`devkit-dist` and `devkit-agt` (whose bundles are built in, `harness` included) that a sync
deploys with their `default_preset` while the previous receipt does not record them: a package that was just
installed, or one whose new release declares `auto_select`. Its `[FIX]` names `devkit remove <bundle>`, which opts
out. Since the receipt is Git-tracked, a clone that receives the updated receipt is not told again.

A package that cannot be loaded, or is not installed, cannot be read for `auto_select`. When the receipt records its
bundle as deployed and `config.toml` neither names it nor opts it out, it stays selected with its recorded presets:
`devkit sync` (and every command that synchronizes, except `devkit remove` of that bundle) fails with
`BUNDLE_PACKAGE_INVALID` (cannot be loaded) or `SELECTION_INVALID` (not installed), so neither a broken upgrade nor a partial environment
(`uv sync --package`, `--no-dev`, `--only-group`) removes committed files. Removal is explicit: `devkit remove
<bundle>`, before or after the package leaves the lock. A package that cannot be loaded and is not deployed is the
usual warning.

## 3. Transaction Safety Guarantees

Every mutating command follows these steps:

1. **Pre-flight**: computes the desired inventory, the seeded files whose targets are absent and the guidance
   block; checks ownership and collisions on disk before writing a byte
   (`CAP-DIST-workspace-ownership`). The result
   lists every planned write under `actions` (`create`, `update` or `remove` per path, `seed` for a seeded file,
   `AGENTS.md` included).
2. **Project lock**: `fcntl.flock` on `.devkit/transient/lock` (`devkit.core.file_lock`, POSIX only). Writers
   (`sync`, `add`, `remove`, `recover`, `override create|accept|remove`) take it exclusively and fail at once when it is held (`LOCK_HELD`,
   `DEFER`). Readers (`get-context`, `playbook search`, `status`, `list`, `override list|diff`, and `sync`, `add`
   and `remove` under `--dry-run` or `--check`, which write nothing) share it and wait
   up to ten seconds for a writer; in a project without `.devkit/` they take no lock, so reading never creates it. A
   reader that gets `EROFS`, `EACCES` or `EPERM` creating or opening the lock (a read-only review sandbox) reads
   without it; writers still fail.
3. **Write-ahead journal**: pending operations, base64 backups of the files they replace, the directories the
   writes will create and those a written file replaces are flushed to `.devkit/transient/sync-journal.json` before
   the disk changes. A file standing where a destination's directory must be (a project file `.claude/skills/review`
   when a skill `review` is deployed) is `WORKSPACE_UNSAFE` before any write, already in the pre-flight (`--dry-run`
   and `--check` included); its `[FIX]` moves that file out of the way. A managed or projected file the same sync
   deletes is no obstacle (an upstream asset whose file became a directory): deletions are journaled and applied
   before writes, and a rollback restores the file in place of the directory. The reverse holds too (an upstream
   asset whose directory became a file, `notes/SKILL.md` to `notes`): a managed or projected directory whose files
   the same sync all deletes is removed once they are, just before the file is written in its place, and a rollback
   restores its files in place of the file. Such a directory that holds anything else (a file devkit does not own or
   does not delete, a symlink) is `WORKSPACE_UNSAFE` in the pre-flight, whose `[FIX]` moves it out of the way.
4. **Atomic replacement**: each file is written with `devkit.core.atomic_write_bytes` (a temporary sibling,
   `fchmod`ed, `fsync`ed and moved into place with `os.replace`); directory entries are `fsync`ed, deletions' too.
5. **Directory pruning**: removing a managed or projected file removes the directories it leaves empty, up to its
   owned prefix (`.claude/skills/<id>/` goes, `.claude/skills/` stays). Seeded targets' directories are never
   pruned by a committed sync. A rolled-back transaction (a failed write, or `devkit recover`) also removes the
   directories it created, seeded targets' included, once they are empty again; a directory that existed before
   it, or that holds anything else, stays.
6. **Recovery**: a later `sync` that finds the journal stops with `TRANSACTION_PENDING` (fix: `devkit recover`).
   `devkit recover` restores every recorded file whose content has not changed since; a later edit stops it with
   `RECOVERY_BLOCKED` (`HALT`). The journal format is not versioned across devkit releases: a journal an earlier
   devkit wrote (without `directories`) is `RECOVERY_BLOCKED` too, and its `[FIX]` says to run `devkit recover` with
   the version that wrote it, or to roll back by hand (write back the `before` of each listed file that equals its
   base64 `before` or `after`, deleting the file when `before` is null; a file that equals neither was edited after
   the sync, so decide which content to keep), delete the journal and run `devkit sync`.

### Post-Sync Extensions

After the transaction committed (with the configuration a selection command saved) and the lock is released (never
on `--dry-run` or `--check`), `devkit sync` (and
`devkit override create|remove`, which synchronize) calls every callable registered under the `devkit.post_sync`
entry-point group, in sorted entry-point name order, as
`extension(root: Path, result: dict) -> list[str | AdvisoryError] | None`, where `result` is `SyncResult.to_dict()`.
Each returned string becomes a `POST_SYNC_NOTICE` (its `details` name the extension); each returned `AdvisoryError`
keeps its code and level, except that an `ERROR` is lowered to `WARNING`. Both join the result's `notices` (for
`override create|remove`, the change's `notices`). An `AdvisoryError` an extension raises is kept the same way, with an
`extension: <name>` detail; any other exception, or a return value of another type, becomes a
`POST_SYNC_EXTENSION_FAILED` warning; an extension can never fail or roll back the sync, because the files are already on disk.
This is how a package built on devkit reacts to a changed workspace without devkit knowing it; since the lock is
released, an extension may call devkit reads such as `get_context`. `devkit-agt` registers one,
`gate-hooks`, which installs shared Git hook dispatchers and active gate entries and keeps the commented gate settings template current
(`CAP-GATE-commit-gates`); a standalone `devkit-dist` installation installs no Git hooks.

### Engine Notice

Rule, gate and workflow assets are deployed and recorded like any other kind, but only `devkit-agt` runs them.
When the deployed assets of a sync (`--dry-run`, `--check` and `--locked` included) or of the receipt `devkit status`
reads include such kinds and no `devkit.commands` entry point named after their engine (`rules`, `gate`,
`workflow`) is installed, the result's `notices` carry one `HARNESS_ENGINE_MISSING` warning naming each bundle with
its kinds, whose `[FIX]` adds `devkit-agt` to the installation (`CAP-DIST-content-packages`). It changes no exit code
except under `--strict`, and the assets are deployed as before. Engine presence is read from entry point names only;
distribution never imports or locates an engine.

The result fields and every notice code are listed in the
[reference](../../development/reference/distribution.md#sync-output-and-notices); warnings and notices never fail a sync except under `--strict`.

### Locked Synchronization

An unchanged receipt may also restore an absent whole host hook file from its `host_hooks` registrations. Existing
shared host files require a plain sync for any change; see `CAP-HOST-lifecycle-observation`.

The receipt, the root `AGENTS.md` block and seeded files are Git-tracked state that every clone shares; the managed
copies under `.devkit/managed/` (and native projections a repository ignores) are rebuilt per clone. `devkit sync
--locked` rebuilds only the latter: it plans a plain sync, and commits it only when the receipt it would write is the
committed one (the `tool` version aside, which it leaves as committed) and every planned action restores an ignored
copy to it: a `create` of a missing file the receipt records, an `update` of a recorded file still as this clone's
last sync left it (`.devkit/transient/deployed.json`), or a `remove` of such an unchanged file the receipt no longer
records. The last two are a clone whose committed receipt moved under it (a pull of another clone's sync). Since the
receipt is unchanged, each written file carries its canonical or validated personal SHA-256 and the recorded mode; a hand-edited copy is a
`SYNC_CONFLICT` as in a plain sync. A seeded file the receipt records but the project deleted is left missing (a plain
sync seeds it again). Any other plan (a seed, the guidance block, `.devkit/.gitignore`, a new or changed
receipt) writes nothing and raises `ReceiptStaleError` (`RECEIPT_STALE`): an `INTERACTION` error with exit code `1`,
since updating committed files is the user's decision and an agent must not retry it away with a plain sync. Its
`[TARGET]` names the committed paths that would change and its `[DETAIL]` lines the planned writes.

A fresh clone (`just init`), `devkit worktree start` and CI run it; whoever changes a bundle source, the lock or
the selection runs a plain `devkit sync` and commits what it changes. In CI, `devkit sync --locked` after the
environment is installed both restores the managed copies the later steps read and fails when a bundle source or
an upgraded package no longer matches the committed receipt. `sync --check` stays the read-only check for a
workspace that is already synchronized.

### Bundle template inputs

`bundles` is an additional accepted top-level configuration key. Each `[bundles.<bundle>.variables]` table supplies
only that bundle's declared inputs; bundle names use the bundle slug grammar and variable names use identifiers.
Values are strings, booleans or integers. Each bundle table accepts only `variables`. Shape/type errors are
`CONFIG_INVALID`; undeclared inputs, declaration-type mismatches and missing required inputs are `CONFIG_INVALID`
when planning a selected bundle. Unselected bundle settings remain stored without requiring installation or selection.

```toml
[bundles.response-style.variables]
language = "ko"
```

Shared project values override manifest defaults and determine canonical inventory and receipt hashes. Eligible checkout-local values override shared values only for personal rendering, as described below. Changes to shared output hashes still require an ordinary sync.

Template overrides retain their `.md.jinja` source paths and raw-source digests. Inventory chooses the upstream or
project override, renders and validates it, then writes the resulting `.md` into the managed tree. Receipt asset
paths and guidance references name that managed result even when a template is overridden, so get-context reads
only rendered content. Skill entry and supporting Markdown templates follow the same raw override and rendered
consumer-path contract; native skill projections receive rendered filenames and contents. Non-template overrides retain their existing paths and ownership behavior. A template error
aborts before transaction writes; override commands restore their preliminary writes when planning fails.


### Checkout-local configuration and execution

`.devkit/config.local.toml` is an optional, ignored, regular TOML file. It accepts optional `schema = 1`,
`[execution] environment = "local" | "cloud"`, `[mcp] register = true | false`, the existing `[playbooks]`
search settings, and scalar `[bundles.<bundle>.variables]` inputs. Shared configuration also accepts `execution`
and `mcp`; environment defaults to `local`, registration to `true`. Registration reconciliation belongs to the
MCP service. The local file is not a secret store.

Core `read_effective_config(root)` returns values and leaf-key source paths. Tables merge recursively; scalars and
arrays replace whole values without type coercion. Array replacement is a merge primitive, not permission to use
arrays in local fields. Every present local input is validated, including settings the immediate reader does not
use. Unknown local keys, including governance, selection and command settings, fail with
`CONFIG_LOCAL_KEY_FORBIDDEN` (exit 2). Invalid TOML, schema, types, symlinks and nonregular files fail with
`CONFIG_INVALID` (exit 2) naming the source. Unknown bundle variables are checked when that bundle is selected.
`read_project_config(root)` remains explicitly shared-only for policy and snapshots.

`devkit config show --effective [--format json]` returns `configuration`, per-key `sources`, and
`execution_environment` under the project read lock. `resolve_execution_environment(root)` requires an existing
bound devkit workspace and returns `environment` and its `source`; it never searches another checkout. Missing
local files use shared/default values. Cloud means interactive approval is unavailable, never permission to change
an ask policy to auto; local does not prove host interactivity. No process-global environment latch exists.

`sync --cloud` and `sync --local` are mutually exclusive and select the invocation's environment in memory.
A writing sync saves only that local key, preserving other local bytes and the file mode. Ordinary sync retains the
saved selection. `--no-save` suppresses shared selection and environment persistence. Dry-run and check report the
pending local edit without saving it; check exits 1 when it or any other write is needed. The result includes
`execution_environment`. Locked sync permits an ignored environment edit and eligible personal output only while
canonical receipt and tracked outputs remain fixed; otherwise `RECEIPT_STALE` writes nothing. Shared configuration
writers never edit local preferences. Shared/local input snapshots are rechecked before writes; concurrent changes
raise `CONFIG_LOCAL_CHANGED` (exit 1, rerun). Journal failures restore the prior environment and output; post-sync
extension warnings retain the committed environment.

### Personal rendering and evidence

Sync builds canonical inventory from shared variables and compares a second inventory using effective variables.
Only bytes of assets with kind `skill`, `instruction`, `subagent` or `playbook` may differ, at ignored untracked
destinations. Asset selection, paths, modes, manifests, constitutions, executable asset kinds, hooks, guidance and
seeds remain canonical. A forbidden difference is `CONFIG_LOCAL_RENDER_FORBIDDEN` (exit 2), before any write.
Existing template-kind validation can reject an executable template earlier during bundle loading.

`.devkit/transient/local-render.json` records only differing file signatures, bound to the canonical receipt digest
and effective variable digest. The deployed ledger records actual output. Context and status use a validated runtime
receipt view; core receipt loading, rule/workflow/gate engines and snapshot checks retain canonical authority.
Missing or stale evidence or changed variables raise `CONFIG_LOCAL_RENDER_STALE` (exit 1, run sync). Missing outputs
use normal sync repair and hand edits retain conflict checks. Removing preferences restores canonical bytes and
removes obsolete local evidence. The personal language fixture is `[bundles.response-style.variables] language = "ko"`.
