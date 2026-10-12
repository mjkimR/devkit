# Synchronization and Transaction Safety (ACID Engine)

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Transitive Dependencies](transitive-dependencies.md)

---

## 1. The Installation Receipt (`.devkit/installation.json`)

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
  "tool": { "package": "devkit", "version": "0.1.0" }
}
```

### Receipt Properties
- `tool` records which distributor wrote the receipt (package name and version from the installed distribution metadata). A different running version alone is not a change: a sync with nothing else to do keeps the receipt byte for byte (so `devkit sync --check` stays clean across teammates on different versions). The next sync that writes anything records the running version and reports a `TOOL_VERSION_CHANGED` notice (`devkit <recorded> -> <running>`); `devkit status` reports whether the recorded and running versions match. A mismatch never refuses anything: the version pin lives in `uv.lock`, the receipt only makes the change visible.
- `guidance_block` is the SHA-256 of the managed block in the root `AGENTS.md` (markers included, line endings normalized to LF). It is absent when `guidance_block = false` is configured. The file itself is never listed under `files`, because only the block is owned ([Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants)).
- `seeded` lists, for every selected seeded `document` asset, the workspace paths it seeds (bundle, asset id, path), sorted by path. It is present only while such an asset is selected and is informational: seeded files are project-owned, never appear under `files`, and the list is never read back as a selection input. A seeded asset's entry under `assets` has an empty `paths` and a `seeded` array of its targets.
- Tracks exact package names, package versions, bundle names, and bundle versions of **selected** bundles only. Installed but unselected bundles are not recorded.
- Records the effective agent and preset selection applied by the last sync. The recorded selection is an audit record: it is never read back as an input for later selections.
- Stores tracked project overrides per asset: `relative_path` names the asset (its `SKILL.md`, file or directory source), `baseline_upstream_sha256` and `override_sha256` are digests over every upstream file of the asset and every override file of it (SHA-256 of the sorted `path NUL sha256` lines). An override of a bundle that is later deselected keeps its record while its files remain under `.devkit/overrides/`, so drift during that time is still reported when the bundle is selected again.
- Stores deployed asset mappings linking logical asset IDs to physical workspace file paths.
- Records expected SHA-256 digests and POSIX file modes (`0644` or `0755`) for every deployed file. Modes are compared by their execute bit only: a group-writable checkout (`0664` under umask `002`) or a `0600` copy is not an edit.
- The distribution validates the receipt with the strict reader of `devkit.core.receipt` (unknown keys, wrong types, non-canonical or escaping paths are errors) and adds its own ownership rules: `files` may only name managed or projected destinations, and asset `paths` only those or the bundle's own `.devkit/overrides/<bundle>/` files.
- Omits absolute filesystem paths and machine timestamps to ensure clean Git diffs across workstations.

---

## 2. Asset Selection Model

### Principle: Explicit Opt-In for Content Packages

Installing a content wheel makes its bundle **available**; it never makes the bundle **selected**. `devkit sync` deploys only bundles the consumer project has selected in `.devkit/config.toml`. This keeps transitive runtime dependencies (for example, a library that ships its own usage guide) from injecting assets into a workspace that did not ask for them, and it makes every deployed asset traceable to a reviewed, Git-tracked line of configuration.

Auto-selected built-in bundles are the exception: the bundles shipped inside the `devkit` distribution itself that declare `auto_select = true` (`devkit` and `advisory`) are selected with their default preset unless the configuration names them (which selects other presets) or sets them to `false` (which opts out). They come from the tool the project already chose to install, so they cannot leak in transitively; discovery rejects `auto_select` in any other package. Built-in bundles without it (`authoring`, `git-commits`) are opt-in practices and follow the principle above.

### Project Configuration (`.devkit/config.toml`, `schema = 1`)

```toml
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter = "daily"                       # one preset
advisory = ["core", "python"]           # union of several presets
team-backend = "all"                    # reserved preset: every asset
devkit = false                          # opt out of an auto-selected built-in bundle

[playbooks]
min_score = 0.1
limit = 5
max_bytes = 8192
```

- **Allowed top-level fields**: `schema`, `agents`, `presets`, `playbooks`, `rules`, `workflow`, `gates`, `guidance_block`, `override_drift`, `tool`. Unknown fields are rejected. `guidance_block = false` stops `devkit sync` from managing the block in the root `AGENTS.md` (default `true`). `override_drift = "block"` makes upstream drift behind any override abort the sync before it writes (default `"warn"`: the drift is reported and the sync proceeds); see [Workspace Ownership, section 3](workspace-ownership.md#3-project-overrides-and-drift-review). `[rules]` is owned by `devkit.rules` (phase and severity overrides, typed settings), `[workflow]` by `devkit.workflow` and `[gates]` by `devkit.gate`; `devkit` passes them through untouched.
- **`[tool.<name>]`** is the extension namespace, as in `pyproject.toml`: any tool built on devkit keeps its own policy in `[tool.<name>]` and reads it itself. `devkit` only checks that `<name>` matches `[a-z][a-z0-9_-]*` and that the value is a table; the contents are never inspected, so no registration is needed and devkit does not learn the tool's schema. Everything outside `[tool]` stays an explicit allowlist so a mistyped devkit key is still an error.
- **`agents`** narrows native projection. Absent, every supported agent (`antigravity`, `claude-code`, `codex`) is a target; `agents = []` (written by `devkit sync --no-agents`) turns projection off while managed copies stay.
- **`[presets]`** is the selection: a bundle from a content package is synchronized if and only if it has an entry; an auto-selected built-in bundle is synchronized with its `default_preset` unless it has an entry. The value is a preset name or a nonempty array of unique preset names; an array selects the union of their assets. `all` is a reserved preset available in every bundle. `false` opts an auto-selected bundle out; `devkit remove <bundle>` writes it for such a bundle (and deletes the entry of any other) and `devkit add <bundle>` replaces it.
- **Selected but not installed**: A selected bundle that no installed package provides is an error. Install the package or deselect the bundle with `devkit remove <bundle>`.
- **`schema`**: Optional; `1` is the only supported version. `devkit add` writes it when it creates the file.

### Resolution Order

1. **CLI selection flags** (`--agent`, `--no-agents`, `--preset`) on `devkit sync`, and the `devkit add` / `devkit remove` commands, edit the matching entries of `config.toml` and then synchronize. Edits preserve unrelated tables, comments, and formatting. `--no-save` applies the flags to a single run without editing the file; `--dry-run` and `--check` never edit it.
2. **Project configuration** (`config.toml`) is the only persistent selection input.
3. **Built-in defaults**: every supported agent (`antigravity`, `claude-code`, `codex`), the auto-selected built-in bundles with their default preset, no other bundles, and playbook search defaults (`limit=5`, `min_score=0.1`, `max_bytes=8192`).

The receipt is not a resolution tier. A selection exists only while it is written in `config.toml` (or passed with `--no-save` for one run).

### Selecting a Bundle

```bash
devkit add starter                # resolves the bundle's default_preset and records it, e.g. starter = "daily"
devkit add advisory:python        # joins the named preset: advisory = ["core", "python"]
devkit add starter:review starter:release  # several presets at once
devkit remove starter             # deselects; unchanged deployed files are removed
```

- `devkit add`, `devkit remove` and the selection flags of `devkit sync` check that `config.toml` can be rewritten (a regular file, not a symlink, in a writable directory) before anything is synchronized, and save it after the sync succeeded.
- `devkit add` joins the named presets to those the bundle already deploys (its configured entry, or the default preset of an auto-selected bundle), existing presets first; it never drops one. `devkit sync --preset <bundle>:<preset>` replaces the bundle's presets, and `devkit remove` deselects it. When no preset is named, `add` uses the bundle's `default_preset` ([Manifest Specification](manifest-spec.md#presets-and-the-default-preset)); a bundle without one must be added with an explicit preset.
- The **resolved** preset name is written, never a symbolic default, so upstream releases cannot silently change what a consumer deploys.

### Unselected Bundle Notice

When installed bundles are not selected, `devkit sync` still succeeds and reports them in the JSON result under `unselected` (bundle, package, available presets, default preset). A `BUNDLE_UNSELECTED` notice (`[NOTICE]` block on stderr, in `notices` in the JSON) names them, with `devkit add <bundle>` as its `fix`. `devkit list` shows the selection state of every installed bundle.

---

## 3. Transaction Safety Guarantees (ACID Engine)

All mutating operations enforce strict transactional safety:

1. **Pre-Flight Validation**: Computes the complete desired file inventory, the seeded files whose targets do not exist yet, and the root `AGENTS.md` guidance block; scans existing disk state, verifies file and block ownership, and checks for collisions before writing any bytes. The JSON result lists every planned write under `actions` (`create`, `update` or `remove` per managed path, `seed` for a seeded file, `AGENTS.md` included). A managed file that was edited by hand and is still desired aborts the sync; one that was edited and is no longer desired (deselected, removed or renamed upstream) is left on disk, dropped from the receipt and reported once, as an `ORPHAN_LEFT` warning ([Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants)).
2. **Project Advisory Lock**: `fcntl.flock` on `.devkit/transient/lock` (POSIX only). Writers (`sync`, `add`, `remove`, `recover`, `override create|accept|remove`) take it exclusively and fail immediately when it is held (`LOCK_HELD`, a `DEFER` advisory: retry once the other command finishes). Readers (`get-context`, `playbook search`, `status`, `list`, `override list|diff`) share it with each other, so parallel agents can load context at the same time, and wait up to ten seconds for a writer to finish.
3. **Write-Ahead Journal**: Before modifying disk, pending operations (file additions, modifications, unlinks) and base64-encoded backups of existing file contents are flushed to `.devkit/transient/sync-journal.json`.
4. **Atomic Replacement**: New and updated files are written to temporary sibling files (`.devkit-write-*`), permissions applied via `fchmod`, flushed with `fsync`, and atomically moved into place using `os.replace`. Directory entries are synced using directory `fsync`.
5. **Directory Pruning**: Removing a managed or projected file also removes the directories it leaves empty, up to its owned prefix (`.claude/skills/<id>/` goes, `.claude/skills/` stays). Seeded targets' directories are never pruned.
6. **Rollback Recovery**: If an operation is killed or interrupted mid-flight, subsequent `sync` invocations detect the existing journal and stop with `TRANSACTION_PENDING` (fix: `devkit recover`). Running `devkit recover` inspects every recorded file and safely restores original contents provided the file has not undergone subsequent user modifications; a later edit stops it with `RECOVERY_BLOCKED` (`HALT`).
7. **Post-Sync Hooks**: After the transaction has committed and the project lock is released (never on `--dry-run` or `--check`), `devkit sync` (and `devkit override create|remove`, which synchronize) calls every callable registered under the `devkit.post_sync` entry-point group, in sorted entry-point name order, as `hook(root: Path, result: dict) -> list[str | AdvisoryError] | None`, where `result` is the sync result's JSON object (`SyncResult.to_dict()`). Each returned string becomes a `POST_SYNC_NOTICE` notice (its `details` name the hook) and each returned `AdvisoryError` is kept with its own code and level, except that an `ERROR` is lowered to `WARNING`; both are appended to the result's `notices` (for `override create|remove`, to the change's `notices`) and printed as `[NOTICE]` or `[WARN]` blocks on stderr. A hook that raises or returns anything else becomes a `POST_SYNC_HOOK_FAILED` warning; it cannot fail or roll back the sync, because the files are already on disk. This is how a package built on devkit reacts to a changed workspace (for example, checking in-flight work units against a changed workflow definition) without devkit knowing the package. Because the lock is released, a hook may call devkit's read operations such as `get_context`.

### Result and Notices

The JSON result of `sync`, `add` and `remove` carries, besides `actions`, `selection`, `packages`, `assets` and `unselected`: `drift` (overrides whose upstream changed), `stray` (unmanaged files under the managed root), `unprojected` (subagents without a native variant) and `notices`. The first four are facts for programs; `notices` is what the agent must know, as advisories at level `WARNING` (`ORPHAN_LEFT`, `OVERRIDE_DRIFT`, `MANAGED_FILE_STRAY`, `POST_SYNC_HOOK_FAILED`) or `NOTICE` (`SUBAGENT_UNPROJECTED`, `BUNDLE_UNSELECTED`, `TOOL_VERSION_CHANGED`, `POST_SYNC_NOTICE`), each serialized as `code`, `level`, `message`, `exit_code` `0` and `advisory`. The library builds the list; the CLI prints the result, then each entry on stderr as a `[WARN]` or `[NOTICE]` block. Warnings and notices never fail the sync (`--strict` exits `1` on a warning). See the [reference](reference.md#sync-output-and-notices).

---

## 4. Lifecycle Command Matrix

| Command | Lifecycle Phase | Description |
| --- | --- | --- |
| `devkit sync [options]` | Deployment | Synchronizes selected bundles: computes plan, performs pre-flight conflict checks, executes atomic transaction, updates the root `AGENTS.md` guidance block, and updates receipt. |
| `devkit add <bundle>[:<preset>]...` | Selection | Joins bundle presets to the selection in `config.toml` (resolving `default_preset` when no preset is named), then synchronizes. |
| `devkit remove <bundle>...` | Selection | Removes bundle selections from `config.toml`, then synchronizes. |
| `devkit list` | Discovery | Outputs JSON listing installed content packages, bundle metadata, available and default presets, selection state, and synchronized asset paths. |
| `devkit status` | Inspection | Read-only JSON summary of the installed state against the receipt: selection, opted-out built-in bundles, managed file counts (`ok`, `missing`, `modified`, `mode-mismatch`) with the offending paths, override drift, guidance block state (`ok`, `missing`, `modified`, `unowned`, `disabled`), seeded paths and whether each exists, a pending journal, and the recorded versus running tool version. Without a receipt every entry describes an empty installation. Problems to act on (a missing, modified or mode-mismatched file, a pending journal, override drift) are listed under `errors` and make it exit `1`, whatever their own codes; it exits `2` only when it cannot run (for example an unreadable receipt or configuration). It never writes project files. |
| `devkit get-context <bundle>` | Context | Returns bundle constitution and catalog of instruction headers for progressive loading. |
| `devkit playbook search <query>` | Context | Runs lexical BM25 search over synchronized playbooks. |
| `devkit override list` | Customization | Lists tracked project overrides and their drift status. |
| `devkit override create <bundle>:<asset> [--force]` | Customization | Copies every upstream file of a selected, non-seeded asset to `.devkit/overrides/` and synchronizes, under one lock; a failed sync puts the override files back as they were. |
| `devkit override diff <bundle>:<asset>` | Customization | Per file: upstream vs override, and recorded baseline vs current upstream. |
| `devkit override accept <bundle>:<asset>` | Customization | Records the current upstream digest as the baseline (journaled) and refreshes the baseline copies; fails for an untracked override. |
| `devkit override remove <bundle>:<asset>` | Customization | Deletes the override and baseline files and synchronizes, under one lock with the same rollback. |
| `devkit recover` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to roll back an interrupted transaction without overwriting newer edits. |
| `devkit bundle validate <source>` | Authoring | Verifies manifest syntax, schema rules, declared local source files and kind-specific headers (instructions, playbooks, workflows, role contracts). |
| `devkit bundle plan <source> [--preset <name>] [--agent <name>]...` | Authoring | Previews every destination a local bundle source deploys, computed by the same inventory as `sync` (managed copies, native projections, generated entry skills, seeded files), without a consumer project. Without `--preset`, the default preset, or `all` when none is declared; without `--agent`, every supported agent. |
| `devkit bundle build <source> --output <zip>` | Packaging | Produces a deterministic ZIP archive with inventory hashes and normalized file permissions. |

### Sync Options and Modes
- `-w, --workspace-root <dir>`: The project root (every distribution command takes it). Default: the nearest directory with `.devkit/` (up to the Git top level), else the Git top level, else the current directory.
- `--agent <name>`: Narrows the agent targets (recorded as `agents` in `config.toml`). Repeatable; without any `agents` entry every supported agent is a target.
- `--no-agents`: Clears agent targets and unlinks unchanged native projections.
- `--preset <bundle>[:<name>]`: Selects `<bundle>` with `<name>` (or its default preset), replacing that bundle's entry in `config.toml`. Repeat a bundle to select a union. Use `<bundle>:all` for every asset.
- `--no-save`: Applies selection flags to this run only, without editing `config.toml`.
- `--dry-run`: Computes inventory and returns planned actions without writing to disk or configuration.
- `--check`: Read-only execution for CI pipelines. Exits with code `1` if the workspace requires synchronization (a missing or stale `AGENTS.md` guidance block and a seeded file that is not written yet included) and `2` on any error (for example a user-modified managed file, `SYNC_CONFLICT`). Seeded files that exist are never compared. An orphan alone does not fail `--check`: the modified file is no longer managed, so there is nothing to synchronize; it appears as an `ORPHAN_LEFT` warning on that run and as a `stray` file afterwards if it sits under the managed root.
