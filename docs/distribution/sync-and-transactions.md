# Synchronization and Transactions

## 1. The Installation Receipt (`.devkit/installation.json`)

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
  "tool": { "package": "devkit", "version": "0.1.0" }
}
```

- `packages`: package and bundle names and versions of **selected** bundles only.
- `selection`: the effective agents and presets the last sync applied. It is an audit record, never read back as a
  selection input.
- `assets`: each deployed asset's workspace paths. A seeded asset has an empty `paths` and a `seeded` array of its
  targets.
- `files`: SHA-256 and mode (`0644` or `0755`) of every deployed file. Modes are compared by their execute bit only.
- `overrides`: tracked overrides per asset, with the digests defined in
  [Workspace Ownership, section 3](workspace-ownership.md#drift-detection). An override of a bundle that is later
  deselected keeps its record while its files remain, so drift is still reported when the bundle is selected again.
- `guidance_block`: the SHA-256 of the root `AGENTS.md` block (markers included, LF line endings); absent under
  `guidance_block = false`. `AGENTS.md` itself is never listed under `files`.
- `seeded`: for every selected seeded asset, the paths it seeds (bundle, asset id, path), sorted by path; present
  only while such an asset is selected, informational, never a selection input.
- `tool`: the distributor that wrote the receipt. A different running version alone is not a change: a sync with
  nothing else to do keeps the receipt byte for byte (so `sync --check` stays clean across teammates on different
  versions); the next sync that writes anything records the running version with a `TOOL_VERSION_CHANGED` notice.
  A mismatch never refuses anything; the version pin lives in `uv.lock`.

The receipt holds no absolute paths or timestamps. It is read with the strict reader of `devkit.core.receipt`
(unknown keys, wrong types, non-canonical or escaping paths are `RECEIPT_INVALID`) plus distribution ownership
rules: `files` may only name managed or projected destinations, and asset `paths` only those or the bundle's own
`.devkit/overrides/<bundle>/` files.

## 2. Asset Selection Model

Installing a content wheel makes its bundle **available**, never **selected**: `devkit sync` deploys only bundles
selected in the Git-tracked `.devkit/config.toml`, so a transitive dependency cannot inject assets, and every
deployed asset traces to a reviewed line of configuration. The exception is the built-in bundles declaring
`auto_select` (`devkit`, `advisory`): they come with the tool the project chose to install and are deployed with
their default preset unless configured otherwise. The other built-in bundles (`authoring`, `git-commits`) are
opt-in.

### Project Configuration (`.devkit/config.toml`, `schema = 1`)

```toml
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter = "daily"                       # one preset
advisory = ["core", "python"]           # union of several presets
team-backend = "all"                    # reserved preset: every asset
devkit = false                          # opt out of an auto-selected built-in bundle
```

- **Top-level keys**: `schema`, `agents`, `presets`, `playbooks`, `rules`, `workflow`, `gates`, `guidance_block`,
  `override_drift`, `tool`; anything else is `CONFIG_INVALID`.
- **`schema`**: optional; `1` is the only version. `devkit add` writes it when it creates the file.
- **`agents`**: the projection targets. Absent, every supported agent (`antigravity`, `claude-code`, `codex`);
  `[]` (written by `devkit sync --no-agents`) turns projection off while managed copies stay.
- **`[presets]`**: the selection. A content bundle is synchronized if and only if it has an entry; an auto-selected
  built-in bundle is synchronized with its `default_preset` unless it has one. The value is a preset name or a
  nonempty array of unique preset names (the union of their assets); `all` is reserved in every bundle. `false`
  opts an auto-selected bundle out. A selected bundle that no installed package provides is an error: install it or
  `devkit remove` it.
- **`guidance_block`**: `false` stops `devkit sync` from managing the root `AGENTS.md` block (default `true`).
- **`override_drift`**: `"warn"` (default) or `"block"`; see
  [Workspace Ownership, section 3](workspace-ownership.md#drift-detection).
- **`[playbooks]`**: search defaults; see [Context Loading & Playbooks](context-and-playbooks.md#search-engine).
- **`[rules]`, `[workflow]`, `[gates]`**: owned by `devkit.rules`, `devkit.workflow` and `devkit.gate`; passed
  through untouched.
- **`[tool.<name>]`**: the extension namespace, as in `pyproject.toml`. A tool built on devkit keeps its own policy
  there and reads it itself; devkit only checks that `<name>` matches `[a-z][a-z0-9_-]*` and the value is a table,
  so a mistyped devkit key elsewhere is still an error.

### Resolution Order

1. **CLI selection**: `--agent`, `--no-agents` and `--preset` on `devkit sync`, and `devkit add` / `devkit remove`,
   edit the matching entries of `config.toml` (preserving unrelated tables, comments and formatting), then
   synchronize. `--no-save` applies the flags to one run; `--dry-run` and `--check` never edit the file.
2. **`config.toml`**: the only persistent selection input. The receipt is not a resolution tier.
3. **Built-in defaults**: every supported agent, the auto-selected bundles with their default preset, no other
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
  ([Manifest Specification](manifest-spec.md#presets-and-the-default-preset)), and a bundle without one needs an
  explicit preset. `devkit add` replaces a `false` entry.
- `devkit sync --preset <bundle>:<preset>` replaces the bundle's presets.
- `devkit remove` deletes a content bundle's entry and writes `false` for an auto-selected bundle.
- The **resolved** preset name is written, never a symbolic default, so upstream releases cannot change what a
  consumer deploys.
- Selection commands check that `config.toml` can be rewritten (a regular file, not a symlink, in a writable
  directory) before synchronizing, and save it after the sync succeeded.

### Unselected Bundles

Every `devkit sync` lists installed bundles that are not selected under `unselected` (bundle, package, available
presets, default preset, and `opted_out` when set to `false`). The `BUNDLE_UNSELECTED` notice announces only the
bundles neither selected nor opted out of that this clone has not been told about: a writing sync (not `--dry-run`
or `--check`) records the installed names in the Git-ignored `.devkit/transient/seen-bundles.json`, and a missing or
unreadable record only repeats the announcement. An opted-out bundle is never announced.

## 3. Transaction Safety Guarantees

Every mutating command follows these steps:

1. **Pre-flight**: computes the desired inventory, the seeded files whose targets are absent and the guidance
   block; checks ownership and collisions on disk before writing a byte
   ([Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants)). The result
   lists every planned write under `actions` (`create`, `update` or `remove` per path, `seed` for a seeded file,
   `AGENTS.md` included).
2. **Project lock**: `fcntl.flock` on `.devkit/transient/lock` (POSIX only). Writers (`sync`, `add`, `remove`,
   `recover`, `override create|accept|remove`) take it exclusively and fail at once when it is held (`LOCK_HELD`,
   `DEFER`). Readers (`get-context`, `playbook search`, `status`, `list`, `override list|diff`) share it and wait
   up to ten seconds for a writer.
3. **Write-ahead journal**: pending operations and base64 backups of the files they replace are flushed to
   `.devkit/transient/sync-journal.json` before the disk changes.
4. **Atomic replacement**: each file is written to a temporary sibling (`.devkit-write-*`), `fchmod`ed, `fsync`ed and
   moved into place with `os.replace`; directory entries are `fsync`ed.
5. **Directory pruning**: removing a managed or projected file removes the directories it leaves empty, up to its
   owned prefix (`.claude/skills/<id>/` goes, `.claude/skills/` stays). Seeded targets' directories are never
   pruned.
6. **Recovery**: a later `sync` that finds the journal stops with `TRANSACTION_PENDING` (fix: `devkit recover`).
   `devkit recover` restores every recorded file whose content has not changed since; a later edit stops it with
   `RECOVERY_BLOCKED` (`HALT`).

### Post-Sync Hooks

After the transaction committed and the lock is released (never on `--dry-run` or `--check`), `devkit sync` (and
`devkit override create|remove`, which synchronize) calls every callable registered under the `devkit.post_sync`
entry-point group, in sorted entry-point name order, as
`hook(root: Path, result: dict) -> list[str | AdvisoryError] | None`, where `result` is `SyncResult.to_dict()`.
Each returned string becomes a `POST_SYNC_NOTICE` (its `details` name the hook); each returned `AdvisoryError`
keeps its code and level, except that an `ERROR` is lowered to `WARNING`. Both join the result's `notices` (for
`override create|remove`, the change's `notices`). A hook that raises or returns anything else becomes a
`POST_SYNC_HOOK_FAILED` warning; a hook can never fail or roll back the sync, because the files are already on disk.
This is how a package built on devkit reacts to a changed workspace without devkit knowing it; since the lock is
released, a hook may call devkit reads such as `get_context`.

The result fields and every notice code are listed in the
[reference](reference.md#sync-output-and-notices); warnings and notices never fail a sync except under `--strict`.
