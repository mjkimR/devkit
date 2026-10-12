# Workspace Ownership and Overrides

## 1. Consumer Workspace Layout

```text
.devkit/
  config.toml             # Project configuration: selection, agents, module tables (Git-tracked)
  installation.json       # Receipt: packages, selection, file hashes & modes (Git-tracked)
  managed/<bundle>/       # Pristine copies of upstream bundle files (generated)
  overrides/
    <bundle>/             # Full file replacements for managed assets (Git-tracked)
    .baseline/<bundle>/   # Upstream copies taken at create/accept, for `override diff` (Git-tracked)
  transient/
    lock                  # Project lock (fcntl.flock): exclusive for writers, shared for readers
    sync-journal.json     # Write-ahead journal of an unfinished transaction
    seen-bundles.json     # Installed bundles this clone was told about (BUNDLE_UNSELECTED is announced once)
<agent native paths>      # Projected native assets (.agents/, .codex/, .claude/)
AGENTS.md                 # Project-owned; only the DEVKIT:START/END block inside it is managed (Git-tracked)
<seeded targets>          # Files a seeded document asset wrote once; project-owned (Git-tracked)
```

## 2. Ownership Categories and Invariants

1. **Project configuration (`.devkit/config.toml`)**: owned by the developer. `devkit sync` never edits it on its
   own; only the selection commands (`devkit add`, `devkit remove`, and `devkit sync` selection flags without
   `--no-save`) edit `agents` and `[presets]`, preserving unrelated tables, comments and formatting. The receipt
   cannot claim it.
2. **Managed assets (`.devkit/managed/<bundle>/`)**: a read-only cache of the upstream bundle files at their
   original relative paths, regenerated deterministically by `devkit sync`.
3. **Native projections**: copied or rendered files in agent directories
   ([Agent Projections](agent-projections.md)), tracked by path, SHA-256 and mode in the receipt.
4. **Foreign files**: devkit manages only files recorded in the receipt and preserves every other file. A planned
   write onto an existing file the receipt does not record aborts the sync before any write
   (`unowned destination already exists: <path>`, `SYNC_CONFLICT`). Files under `.devkit/managed/` that neither the
   receipt nor the inventory owns are left untouched and reported as `stray` (`MANAGED_FILE_STRAY`): they are never
   deployed or removed, but consumers scanning the directory could pick them up. Project-owned content belongs
   outside the managed root (custom rules under a `--rules-dir`, overrides under `.devkit/overrides/`).
5. **User modifications**: a deployed file whose content or execute bit differs from its receipt signature is a
   user modification; other permission bits (`0664` under umask `002`, `0600`) are not.
   - Still desired: the sync aborts before any write.
   - No longer desired (package removal, deselection, preset narrowing, an asset removed or renamed upstream): the
     file is an **orphan**. It stays on disk, is dropped from the receipt's `files`, and the sync continues with an
     `ORPHAN_LEFT` warning naming it; the user deletes or moves it. From the next sync on, an orphan under
     `.devkit/managed/` is a stray file.
   - Only files byte-for-byte identical to their recorded signature are ever deleted.
6. **Host guidance block (root `AGENTS.md`)**: the
   [host guidance block](../architecture/resource-taxonomy.md#1-host-guidance-block) between `<!-- DEVKIT:START -->`
   and `<!-- DEVKIT:END -->`.
   - Content: the installed bundle names, the once-per-bundle `devkit get-context` rule, the generated entry
     skills, then the selected `guidance` fragments ordered by bundle name and asset id; deterministic for a given
     selection. A project changes a fragment with `devkit override create <bundle>:<asset>`, never inside the
     markers; an overridden instruction a fragment names is cited by its override path.
   - Placement: the file is created when absent, the block appended when it has no markers, and replaced in place
     otherwise. Bytes outside the markers are project-owned. Each marker stands on a line of its own; a marker
     elsewhere, or more than one of either, is malformed and stops the sync (`GUIDANCE_BLOCK_INVALID`). The block is
     written with the file's line ending, and its digest is taken over LF line endings, so a line-ending conversion
     is not an edit.
   - Ownership: the receipt records the block's SHA-256 under `guidance_block`. A block whose digest differs is a
     user modification and aborts the sync before any write; a deleted block is written again; markers the receipt
     does not know are an unowned collision.
   - `AGENTS.md` must be a regular file while the block is managed; a symlink stops the sync (`WORKSPACE_UNSAFE`:
     make `AGENTS.md` the file and point other names at it, or set `guidance_block = false`).
   - `guidance_block = false`: on that transition the block is removed (the file too, when nothing else is in it)
     if its digest still matches, and the receipt stops recording it. With no recorded block, sync never reads
     `AGENTS.md`.
   - `CLAUDE.md` is never written; the project points it at `AGENTS.md` with its own symlink or include line.
7. **Seeded files (write-once scaffolding)**: the `target` of a seeded `document` asset
   ([Manifest Specification](manifest-spec.md#2-asset-kinds)).
   - Written only when the destination does not exist, as a `seed` action through the same journal as every other
     write. An existing file there is not a collision; it is left alone. A directory or symlink at the target, two
     selected bundles seeding one path, or a seeded path equal to a managed or projected destination stop the sync
     before any write.
   - Once written, the file is project-owned: never compared, updated, removed or hash-checked, not even by
     `sync --check`; deselecting the bundle leaves it. One deleted while its asset is still selected is seeded again
     by the next sync (until then `sync --check` exits `1`).
   - The receipt records which asset seeded which path under `seeded`, never under `files`; the record is
     informational. Seeded files are not bundle context.
8. **Git policy**: commit `.devkit/config.toml`, `.devkit/overrides/`, `.devkit/installation.json`, the root
   `AGENTS.md` and seeded files. Ignore `.devkit/managed/`, `.devkit/transient/` and native copies according to the
   repository's own `.gitignore`; devkit never modifies `.gitignore` or the Git index.

## 3. Project Overrides and Drift Review

An override customizes an upstream asset without a fork. It is a set of complete files under
`.devkit/overrides/<bundle>/<path in the bundle>`, not patches: agents and tools read and edit them as ordinary files,
and upstream line shifts cannot make them fail to apply.

### Creating an Override

`devkit override create <bundle>:<asset>` copies every upstream file of the asset (all files of a skill or directory
source) to `.devkit/overrides/<bundle>/...` and to `.devkit/overrides/.baseline/<bundle>/...` as ordinary
`0644`/`0755` files, then synchronizes, all under one project lock; when the sync fails, the override files are put
back as they were. The bundle must be selected and the asset part of its selected presets; seeded assets cannot be
overridden. `--force` overwrites existing override files.

An override replaces individual files: files missing from the override directory are read from upstream, and extra
files are ignored. Projections, `get-context` and playbook search read the override in place of the upstream file.

### Drift Detection

The first sync that sees an override records it in the receipt under `overrides.<bundle>.<asset>`:
`baseline_upstream_sha256` is a digest over **every** upstream file of the asset (SHA-256 of the sorted
`path NUL sha256` lines), `override_sha256` the same over the override files, and `relative_path` names the asset
(its `SKILL.md`, file or directory source).

On every sync the current upstream digest is compared with the baseline. Because it covers every file, a change to a
skill's script is drift even when only its `SKILL.md` is overridden. On drift the override stays projected and:

- under `override_drift = "warn"` (default), the sync reports an `OVERRIDE_DRIFT` warning:
  ```text
  [WARN]   (OVERRIDE_DRIFT) upstream drift behind the override of starter:development
  [ACTION] CONTINUE — The operation succeeded; this does not block it. Do not retry
           or undo it. Tell the user about it ([REPORT] when present); run [FIX]
           only when they ask for it.
  [TARGET] .devkit/overrides/starter/development.md
  [FIX]    devkit override diff starter:development
  [REPORT] Upstream changed an asset this project overrides; review the diff, then accept it or keep the override
  ```
- under `override_drift = "block"`, the sync aborts before any write (`OVERRIDE_DRIFT`), naming every drifted
  `bundle:asset`, with the `devkit override diff` / `devkit override accept` commands as its `fix`. Choose it where
  an override shadows governance content (rules, gates, workflows); `warn` keeps prose upgrades flowing.

`devkit status` reports drift under `errors` and exits `1` under either policy.

### Reconciliation

- `devkit override diff <bundle>:<asset>` returns, for each overridden file and each upstream file changed since the
  baseline copy, `upstream_diff` (baseline copy to current upstream: what upstream changed) and `diff` (current
  upstream to the override: what the project changed). A diff is `null` when there is nothing to compare (no
  baseline copy, a file that is not overridden, a non-UTF-8 file). The result also carries `drift_detected` and both
  digests. An agent merges the upstream changes into the override files.
- `devkit override accept <bundle>:<asset>` then records the current upstream digest as the baseline (through the
  journal) and refreshes the baseline copies; it fails for an asset without a tracked override.
- `devkit override remove <bundle>:<asset>` deletes the override and baseline files, prunes empty directories and
  synchronizes the pristine upstream files, under one lock with the same rollback as `create`; the receipt entry
  disappears with that sync.
