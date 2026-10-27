---
id: CAP-DIST-workspace-ownership
title: "Workspace Ownership & Overrides"
summary: "Shared and checkout-local ownership of managed assets, presentation preferences, guidance and project overrides."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/workspace.py
  - packages/devkit-dist/src/devkit_dist/features/project/services/presentation.py
created_at: 2026-10-17
---

# [CAP-DIST-workspace-ownership] Workspace Ownership and Overrides

## 1. Consumer Workspace Layout

```text
.devkit/
  .gitignore              # Seeded ignore rules plus managed /config.local.toml entry; preserves other rules (Git-tracked)
  config.toml             # Project configuration: selection, agents, module tables (Git-tracked)
  config.local.toml       # Optional checkout preferences; ignored and never receipt-owned
  generated.toml          # Optional generated-file registry of `devkit generated` (Git-tracked)
  installation.json       # Receipt: packages, selection, file hashes & modes (Git-tracked)
  managed/<bundle>/       # Upstream copies and rendered Markdown template outputs (generated)
  overrides/
    <bundle>/             # Full file replacements for managed assets (Git-tracked)
    .baseline/<bundle>/   # Upstream copies taken at create/accept, for `override diff` (Git-tracked)
  transient/
    lock                  # Project lock (fcntl.flock): exclusive for writers, shared for readers (a reader on a read-only file system reads without it)
    sync-journal.json     # Write-ahead journal of an unfinished transaction
    seen-bundles.json     # Installed bundles this clone was told about (BUNDLE_UNSELECTED is announced once)
    deployed.json         # Last deployed signatures and personal destination provenance
    local-render.json     # Personal signatures bound to canonical receipt, render mode and effective variables
<agent native paths>      # Projected native assets (.agents/, .codex/, .claude/)
AGENTS.md                 # Project-owned; only the DEVKIT:START/END block inside it is managed (Git-tracked)
<seeded targets>          # Files a seeded document asset wrote once; project-owned (Git-tracked)
```

## 2. Ownership Categories and Invariants

Selected lifecycle `hook` assets add one scoped ownership category: exact matcher groups in the shared
`.codex/hooks.json`, recorded under `host_hooks` rather than `files`. All foreign entries remain project-owned;
edited or missing owned groups conflict, and removal never adopts or deletes foreign entries. Planning, writes
and rollback use the same transaction. Host trust and permission settings are never changed.
See `CAP-HOST-lifecycle-observation`.

1. **Project configuration (`.devkit/config.toml`)**: owned by the developer. `devkit sync` never edits it on its
   own; only the selection commands (`devkit add`, `devkit remove`, and `devkit sync` selection flags without
   `--no-save`) edit `agents` and `[presets]`, preserving unrelated tables, comments and formatting. A selection
   command that creates the file writes the commented template with it, and `devkit config template` adds the parts
   of the template the file lacks, never changing a line
   (`CAP-DIST-sync-and-transactions`). The receipt cannot claim it. Its schema, the template renderer and the receipt
   format belong to `devkit-dist`; the reserved harness tables (`[rules]`, `[workflow]`, `[gates]`, `[worktree]`,
   `[integration]`) to the engines of `devkit-agt`, which contribute their commented templates through the
   `devkit.config_tables` entry points (`ADR-package-split-and-namespaces`).
2. **Managed assets (`.devkit/managed/<bundle>/`)**: generated files, regenerated deterministically by `devkit sync`.
   Ordinary files cache upstream bytes at their original relative paths. Supported `.md.jinja` sources instead
   produce rendered `.md` files using declared project inputs, after resolving raw project overrides;
   see `CAP-DIST-manifest-spec` and `CAP-DIST-sync-and-transactions`.
3. **Native projections**: copied or rendered files in agent directories
   (`CAP-DIST-agent-projections`), tracked by path, SHA-256 and mode in the receipt.
4. **Foreign files**: devkit manages only files recorded in the receipt and preserves every other file. A planned
   write onto an existing file the receipt does not record aborts the sync before any write
   (`unowned destinations already exist: <paths>`, `SYNC_CONFLICT`), unless the file is identical to the desired
   content (bytes and execute bit): such a file (for example a Git-ignored projection left on disk when the receipt
   was reset) is adopted into the receipt without a write. One `SYNC_CONFLICT` names every conflicting path of the
   sync: unowned files, user-modified files and the guidance block. Files under `.devkit/managed/` that neither the
   receipt nor the inventory owns are left untouched and reported as `stray` (`MANAGED_FILE_STRAY`): they are never
   deployed or removed, but consumers scanning the directory could pick them up. Project-owned content belongs
   outside the managed root (custom rules under a `--rules-dir`, overrides under `.devkit/overrides/`).
5. **User modifications**: a deployed file whose content or execute bit differs from its receipt signature is a
   user modification, unless it is identical to the desired content (nothing to write) or to the signature this
   clone's last sync left in `.devkit/transient/deployed.json`. The receipt is committed but the files it records are
   Git-ignored: a pull that moves the receipt leaves each untouched file as the clone's last sync wrote it, and such a
   **stale** file is updated (or removed, when nothing desires it any more) like any other owned file. Other
   permission bits (`0664` under umask `002`, `0600`) are never part of a signature. A clone without the local record
   (a fresh clone, or one that never synced) judges by the receipt alone.
   - Still desired: the sync aborts before any write (`SYNC_CONFLICT`, naming every such file).
   - No longer desired (package removal, deselection, preset narrowing, an asset removed or renamed upstream): the
     file is an **orphan**. It stays on disk, is dropped from the receipt's `files`, and the sync continues with an
     `ORPHAN_LEFT` warning naming it; the user deletes or moves it. From the next sync on, an orphan under
     `.devkit/managed/` is a stray file.
   - Only files byte-for-byte identical to their recorded signature are ever deleted.
6. **Host guidance block (root `AGENTS.md`)**: the
   `ARCH-08-2-resource-taxonomy` between `<!-- DEVKIT:START -->`
   and `<!-- DEVKIT:END -->`.
   - Content: the installed bundle names, the once-per-bundle `devkit get-context` rule, the generated entry
     skills, then the selected `guidance` fragments ordered by bundle name and asset id; deterministic for a given
     selection, source content and template inputs. A project changes a fragment with `devkit override create <bundle>:<asset>`, never inside the
     markers. Ordinary overridden instructions are cited by their override paths; template instructions are cited
     by their rendered managed `.md` paths, including when their raw `.md.jinja` source is overridden.
   - Placement: the file is created when absent, the block appended when it has no markers, and replaced in place
     otherwise. Bytes outside the markers are project-owned. Each marker stands on a line of its own; a marker
     elsewhere, or more than one of either, is malformed and stops the sync (`GUIDANCE_BLOCK_INVALID`). The block is
     written with the file's line ending, and its digest is taken over LF line endings, so a line-ending conversion
     is not an edit.
   - Ownership: the receipt records the block's SHA-256 under `guidance_block`. A block whose digest differs is a
     user modification and aborts the sync before any write; a deleted block is written again; markers the receipt
     does not know are an unowned collision, unless the block between them is exactly the one sync writes, which is
     adopted without a write.
   - `AGENTS.md` must be a regular file while the block is managed; a symlink stops the sync (`WORKSPACE_UNSAFE`:
     make `AGENTS.md` the file and point other names at it, or set `guidance_block = false`).
   - `guidance_block = false`: on that transition the receipt stops recording the block. A block whose digest still
     matches is removed (the file too, when nothing else is in it), and only the blank line sync added goes with it:
     project text on both sides stays a paragraph apart. An edited block is left in place with an `ORPHAN_LEFT`
     warning. With no recorded block, sync never reads `AGENTS.md`.
   - `CLAUDE.md` is never written; the project points it at `AGENTS.md` with its own symlink or include line.
7. **Seeded files (write-once scaffolding)**: the `target` of a seeded `document` asset
   (`CAP-DIST-manifest-spec`).
   - Written only when the destination does not exist, as a `seed` action through the same journal as every other
     write. An existing file there is not a collision; it is left alone. Before the first seed (while the receipt
     does not record the path under `seeded`), a directory or symlink at the target, two selected bundles seeding
     one path, or a seeded path equal to a managed or projected destination stop the sync before any write.
   - Once recorded, the path is project-owned: never compared, updated, removed or hash-checked, not even by
     `sync --check`, and only tested for presence, so whatever the project puts there (an edit, a symlink, a
     directory) never fails `sync` or `status`; deselecting the bundle leaves it. One deleted while its asset is
     still selected is seeded again by the next plain sync (until then `sync --check` exits `1`); `sync --locked`
     never writes it and does not fail for it. One deleted below a directory the project replaced by a symlink stays
     missing: devkit never writes through a project symlink, and neither sync fails for it.
   - The receipt records which asset seeded which path under `seeded`, never under `files`; the record is
     informational. Seeded files are never receipt-verified context files; a bundle's declared context document
     directory (`context_documents`, `CAP-DIST-context-and-playbooks`) may still list the project files in it,
     seeded ones included, read from the workspace without a hash check.
8. **Git policy**: commit `.devkit/config.toml`, `.devkit/generated.toml`, `.devkit/overrides/`,
   `.devkit/installation.json`, `.devkit/.gitignore`, the root `AGENTS.md` and seeded files.
   - `.devkit/managed/` and `.devkit/transient/` are ignored by `.devkit/.gitignore`. A writing sync seeds it when
     it is absent (a `seed` action, so `sync --check` exits `1` until then) and preserves project comments/rules afterwards. Every writing sync manages exactly `/config.local.toml`, appending it when absent; other existing entries are not rewritten. A deleted file is seeded again. The receipt never records it.
   - Native copies (`.agents/`, `.codex/`, `.claude/`) live beside project-owned files, so ignoring them is left to
     the repository's own `.gitignore`; devkit never modifies the repository's `.gitignore` or the Git index.

## 3. Project Overrides and Drift Review

An override customizes an upstream asset without a fork. It is a set of complete files under
`.devkit/overrides/<bundle>/<path in the bundle>`, not patches: agents and tools read and edit them as ordinary files,
and upstream line shifts cannot make them fail to apply.

Template overrides keep raw `.md.jinja` sources and baselines at the original bundle-relative paths. The sync
renders the effective source into managed `.md` output; guidance and `get-context` cite that rendered file, whose
final bytes must match the canonical receipt or validated local render ledger. Changes to a raw template require a sync before consumers read their effect.
Raw-source override digests and upstream drift checks remain independent of template inputs and final output hashes.

### Creating an Override

`devkit override create <bundle>:<asset>` copies every upstream file of the asset (all files of a skill or directory
source) to `.devkit/overrides/<bundle>/...` and to `.devkit/overrides/.baseline/<bundle>/...` as ordinary
`0644`/`0755` files, then synchronizes, all under one project lock; when the sync fails before it commits, the
override files are put back as they were (a failure after the commit leaves them, since the receipt cites them). The
bundle must be selected and the asset part of its selected presets; seeded assets cannot be overridden. The current
upstream digest becomes the recorded baseline. `--force` overwrites existing override files, and with them the
baseline, so drift recorded against the old one is gone.

An override replaces individual files: files missing from the override directory are read from upstream, and extra
files are ignored. For ordinary assets, projections, `get-context` and playbook search read the override in place of the upstream file.
A symlink anywhere on an override path (`.devkit/overrides` itself, a bundle directory, a file) stops the sync
before any write (`WORKSPACE_UNSAFE`): override content never comes from outside the project.

### Drift Detection

The first sync that sees an override records it in the receipt under `overrides.<bundle>.<asset>`:
`baseline_upstream_sha256` is a digest over **every** upstream file of the asset (SHA-256 of the sorted
`path NUL sha256` lines), `override_sha256` the same over the override files, and `relative_path` names the asset
(its authored `SKILL.md` or `SKILL.md.jinja` entry, file or directory source).

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

`devkit status` follows the same policy: under `warn` drift is the `OVERRIDE_DRIFT` warning under `notices` (exit
`0`, `1` under `--strict`), under `block` it is listed under `errors` and status exits `1`. Both report drift only for deployed
assets: the record of an asset that is not deployed (its bundle deselected, its preset narrowed) is kept while its
override files remain, and its drift is reported once it is selected again. For an asset its bundle no longer has,
or whose bundle is no longer installed, that means files under the record's own override path (the skill directory
for a skill), whatever other overrides the bundle has. `devkit remove <bundle>` leaves the bundle's override
directory in place and names it in an `OVERRIDE_RETAINED` notice (the directory as `[TARGET]`; delete it to drop the
overrides, or select the bundle again to apply them).

Overrides resolve by bundle name and path. When an asset belongs to another bundle than the one an override names
(an override of `devkit:devkit-run`, an asset of the `harness` bundle), the override does not apply: the asset
deploys from upstream, the override files stay in place with their record while they remain, and the project
re-creates the override with `devkit override create <bundle>:<asset>` under the asset's bundle. An override of an asset that keeps its
bundle and path but loses content keeps applying, with drift reported, until the project reconciles it.

### Reconciliation

- `devkit override diff <bundle>:<asset>` returns, for each overridden file and each upstream file changed since the
  baseline copy, `upstream_diff` (baseline copy to current upstream: what upstream changed) and `diff` (current
  upstream to the override: what the project changed). A diff is `null` when there is nothing to compare (no
  baseline copy, a file that is not overridden, a non-UTF-8 file). The result also carries `drift_detected` and both
  digests. An agent merges the upstream changes into the override files.
- `devkit override accept <bundle>:<asset>` then records the current upstream digest as the baseline, refreshes the
  baseline copies and synchronizes under the same lock, as `create` does, so the merged override files are deployed
  and recorded and `sync --check` passes; the sync's notices are returned with the result. When that sync fails
  before it commits, the baseline copies and the receipt are put back. Under `override_drift = "block"` that sync
  does not refuse on the drift of other overrides, which it still reports as the `OVERRIDE_DRIFT` warning, so drifted
  overrides can be accepted one at a time. It fails for an asset without a tracked override.
- `devkit override remove <bundle>:<asset>` deletes the override files of the asset's upstream files and the
  baseline files, prunes empty directories and synchronizes the upstream sources (rendered for templates), under one lock with the same
  rollback as `create`; the receipt entry disappears with that sync. Any other project file under the asset's override
  paths stays and is reported as an `ORPHAN_LEFT` warning. For a tracked override of an asset its installed bundle
  no longer has (removed or renamed upstream), it deletes every file under the recorded override path and its
  baseline, and the sync drops the record.


## Checkout-local ownership

`.devkit/config.local.toml` and `.devkit/transient/local-render.json` belong only to this checkout. Sync refuses
tracked local configuration or personal outputs and effective ignore negations with `CONFIG_LOCAL_NOT_IGNORED`
(exit 2), naming the source path and required ignore/index action. It never changes the Git index. Dry-run/check
report the ignore edit; locked sync refuses a required `.devkit/.gitignore` change. Projects tracking native
projections must explicitly untrack and ignore the affected outputs before personalization. Canonical execution mode is not a personal preference: ordinary sync may rewrite tracked managed/projection files when switching local/cloud. Personal variables still cannot alter constitutions or guidance. The receipt records actual render mode; no-save rendering leaves persisted runtime settings unchanged. The receipt, root
guidance, seeds and shared config stay canonical; see `CAP-DIST-sync-and-transactions`.

## Presentation preference ownership

`presentation.language` belongs to shared configuration with an optional ignored checkout-local override, using
the same copy-and-diverge worktree semantics as other allowed local preferences. Core owns validation, exact
`auto/en/ko` resolution, unsupported-string English fallback with a visible `PRESENTATION_LANGUAGE_UNSUPPORTED`
warning, and source metadata; see `CAP-DIST-sync-and-transactions`.
Canonical asset planning uses shared preferences; eligible personal rendering uses effective preferences and local
ledger evidence. The preference never authorizes a tracked output write, a forbidden asset difference or execution.
Explicit bundle-variable values override inherited presentation defaults, regardless of which layer supplied them.
