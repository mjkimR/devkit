# Synchronization and Transaction Safety (ACID Engine)

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit-distribution`  
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
  "tool": { "package": "devkit-distribution", "version": "0.1.0" }
}
```

### Receipt Properties
- `tool` records which distributor wrote the receipt (package name and version from the installed distribution metadata). It is rewritten on every sync; the first sync after an upgrade prints `NOTICE: devkit-distribution <recorded> -> <running>` and `devkit status` reports whether the recorded and running versions match. A mismatch never refuses anything: the version pin lives in `uv.lock`, the receipt only makes the change visible.
- `guidance_block` is the SHA-256 of the managed block in the root `AGENTS.md` (markers included). It is absent when `guidance_block = false` is configured. The file itself is never listed under `files`, because only the block is owned ([Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants)).
- `seeded` lists, for every selected seeded `document` asset, the workspace paths it seeds (bundle, asset id, path), sorted by path. It is present only while such an asset is selected and is informational: seeded files are project-owned, never appear under `files`, and the list is never read back as a selection input. A seeded asset's entry under `assets` has an empty `paths` and a `seeded` array of its targets.
- Tracks exact package names, package versions, bundle names, and bundle versions of **selected** bundles only. Installed but unselected bundles are not recorded.
- Records the effective agent and preset selection applied by the last sync. The recorded selection is an audit record: it is never read back as an input for later selections.
- Stores active project overrides with their baseline upstream digests and local override hashes.
- Stores deployed asset mappings linking logical asset IDs to physical workspace file paths.
- Records expected SHA-256 digests and POSIX file modes (`0644` or `0755`) for every deployed file.
- Omits absolute filesystem paths and machine timestamps to ensure clean Git diffs across workstations.

---

## 2. Asset Selection Model

### Principle: Explicit Opt-In

Installing a content wheel makes its bundle **available**; it never makes the bundle **selected**. `devkit sync` deploys only bundles the consumer project has selected in `.devkit/config.toml`. This keeps transitive runtime dependencies (for example, a library that ships its own usage guide) from injecting assets into a workspace that did not ask for them, and it makes every deployed asset traceable to a reviewed, Git-tracked line of configuration.

### Project Configuration (`.devkit/config.toml`, `schema = 1`)

```toml
schema = 1
agents = ["codex", "claude-code"]

[presets]
starter = "daily"                       # one preset
error-advisory = ["core", "python"]     # union of several presets
team-backend = "all"                    # reserved preset: every asset

[playbooks]
min_score = 0.1
limit = 5
max_bytes = 8192
```

- **Allowed top-level fields**: `schema`, `agents`, `presets`, `playbooks`, `rules`, `workflow`, `gates`, `guidance_block`, `override_drift`, `tool`. Unknown fields are rejected. `guidance_block = false` stops `devkit sync` from managing the block in the root `AGENTS.md` (default `true`). `override_drift = "block"` makes upstream drift behind any override abort the sync before it writes (default `"warn"`: the drift is reported and the sync proceeds); see [Workspace Ownership, section 3](workspace-ownership.md#3-project-overrides--3-way-drift-review-architecture). `[rules]` is owned by `agent-rule-engine` (phase and severity overrides, typed settings), `[workflow]` by `agent-workflow-engine` and `[gates]` by `agent-commit-gate`; `devkit` passes them through untouched.
- **`[tool.<name>]`** is the extension namespace, as in `pyproject.toml`: any tool built on devkit keeps its own policy in `[tool.<name>]` and reads it itself. `devkit` only checks that `<name>` matches `[a-z][a-z0-9_-]*` and that the value is a table; the contents are never inspected, so no registration is needed and devkit does not learn the tool's schema. Everything outside `[tool]` stays an explicit allowlist so a mistyped devkit key is still an error.
- **`agents`** narrows native projection. Absent, every supported agent (`antigravity`, `claude-code`, `codex`) is a target; `agents = []` (written by `devkit sync --no-agents`) turns projection off while managed copies stay.
- **`[presets]`** is the selection: a bundle is synchronized if and only if it has an entry. The value is a preset name or a nonempty array of unique preset names; an array selects the union of their assets. `all` is a reserved preset available in every bundle.
- **Selected but not installed**: A selected bundle that no installed package provides is an error. Install the package or deselect the bundle with `devkit remove <bundle>`.
- **`schema`**: Optional; `1` is the only supported version. `devkit add` writes it when it creates the file.

### Resolution Order

1. **CLI selection flags** (`--agent`, `--no-agents`, `--preset`) on `devkit sync`, and the `devkit add` / `devkit remove` commands, edit the matching entries of `config.toml` and then synchronize. Edits preserve unrelated tables, comments, and formatting. `--no-save` applies the flags to a single run without editing the file; `--dry-run` and `--check` never edit it.
2. **Project configuration** (`config.toml`) is the only persistent selection input.
3. **Built-in defaults**: no agents, no bundles, and playbook search defaults (`limit=5`, `min_score=0.1`, `max_bytes=8192`).

The receipt is not a resolution tier. A selection exists only while it is written in `config.toml` (or passed with `--no-save` for one run).

### Selecting a Bundle

```bash
devkit add starter                # resolves the bundle's default_preset and records it, e.g. starter = "daily"
devkit add error-advisory:python  # records the named preset
devkit add error-advisory:core error-advisory:python   # repeat a bundle to record a union
devkit remove starter             # deselects; unchanged deployed files are removed
```

- `devkit add` replaces any existing entry for the named bundle. When no preset is named, it uses the bundle's `default_preset` ([Manifest Specification](manifest-spec.md#presets-and-the-default-preset)); a bundle without one must be added with an explicit preset.
- The **resolved** preset name is written, never a symbolic default, so upstream releases cannot silently change what a consumer deploys.

### Unselected Bundle Notice

When installed bundles are not selected, `devkit sync` still succeeds and reports them in the JSON result under `unselected` (bundle, package, available presets, default preset). A notice on stderr names them together with the `devkit add <bundle>` command. `devkit list` shows the selection state of every installed bundle.

---

## 3. Transaction Safety Guarantees (ACID Engine)

All mutating operations enforce strict transactional safety:

1. **Pre-Flight Validation**: Computes the complete desired file inventory, the seeded files whose targets do not exist yet, and the root `AGENTS.md` guidance block; scans existing disk state, verifies file and block ownership, and checks for collisions before writing any bytes. The JSON result lists every planned write under `actions` (`create`, `update` or `remove` per managed path, `seed` for a seeded file, `AGENTS.md` included). A managed file that was edited by hand and is still desired aborts the sync; one that was edited and is no longer desired (deselected, removed or renamed upstream) is left on disk, dropped from the receipt and listed under `orphans` ([Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants)).
2. **Project Advisory Lock**: Acquires an exclusive, non-blocking file lock via `fcntl.flock` in `/tmp` keyed by SHA-256 hash of the target project directory path (`devkit-<uid>-<hash>.lock`). Concurrent operations fail immediately with an informative message.
3. **Write-Ahead Journal**: Before modifying disk, pending operations (file additions, modifications, unlinks) and base64-encoded backups of existing file contents are flushed to `.devkit/transient/sync-journal.json`.
4. **Atomic Replacement**: New and updated files are written to temporary sibling files (`.devkit-write-*`), permissions applied via `fchmod`, flushed with `fsync`, and atomically moved into place using `os.replace`. Directory entries are synced using directory `fsync`.
5. **Rollback Recovery**: If an operation is killed or interrupted mid-flight, subsequent `sync` invocations detect the existing journal and halt. Running `devkit recover` inspects every recorded file and safely restores original contents provided the file has not undergone subsequent user modifications.
6. **Post-Sync Hooks**: After the transaction has committed (never on `--dry-run` or `--check`), `devkit sync` calls every callable registered under the `devkit.post_sync` entry-point group, in sorted entry-point name order, as `hook(root: Path, result: dict) -> list[str] | None`. The strings a hook returns are appended to the result's `notices` and printed as `NOTICE: <text>` on stderr. A hook that raises becomes `NOTICE: post-sync hook <name> failed: <error>`; it cannot fail or roll back the sync, because the files are already on disk. This is how a package built on devkit reacts to a changed workspace (for example, checking in-flight work units against a changed workflow definition) without devkit knowing the package.

### Result and Notices

The JSON result of `sync`, `add` and `remove` carries, besides `actions`, `selection`, `packages`, `assets` and `unselected`: `drift` (overrides whose upstream changed), `orphans` (modified files left behind, see above), `stray` (unmanaged files under the managed root), `unprojected` (subagents without a native variant) and `notices` (free-text lines: orphans, a tool upgrade, post-sync hook output). Everything in `notices` is also printed to stderr as `NOTICE: <text>`; drift and stray files are `WARNING` lines.

---

## 4. Lifecycle Command Matrix

| Command | Lifecycle Phase | Description |
| --- | --- | --- |
| `devkit sync [options]` | Deployment | Synchronizes selected bundles: computes plan, performs pre-flight conflict checks, executes atomic transaction, updates the root `AGENTS.md` guidance block, and updates receipt. |
| `devkit add <bundle>[:<preset>]...` | Selection | Records bundle selections in `config.toml` (resolving `default_preset` when no preset is named), then synchronizes. |
| `devkit remove <bundle>...` | Selection | Removes bundle selections from `config.toml`, then synchronizes. |
| `devkit list [--target <dir>]` | Discovery | Outputs JSON listing installed content packages, bundle metadata, available and default presets, selection state, and synchronized asset paths. |
| `devkit status [--target <dir>]` | Inspection | Read-only JSON summary of the installed state against the receipt: selection, managed file counts (`ok`, `missing`, `modified`, `mode-mismatch`) with the offending paths, override drift, guidance block state (`ok`, `missing`, `modified`, `unowned`, `disabled`), seeded paths and whether each exists, a pending journal, and the recorded versus running tool version. Exits 0 unless the receipt or configuration cannot be read; it never writes. |
| `devkit plan <source> [--preset <name>]` | Authoring | Previews managed file inventory for a local bundle source without writing to a consumer project. Without `--preset`, previews the default preset, or `all` when none is declared. |
| `devkit get-context <bundle>` | Context | Returns bundle constitution and catalog of instruction headers for progressive loading. |
| `devkit playbook search <query>` | Context | Runs lexical BM25 search over synchronized playbooks. |
| `devkit override list` | Customization | Lists active project overrides and their drift status. |
| `devkit override create <bundle>:<asset>` | Customization | Copies upstream asset to `.devkit/overrides/` and records upstream baseline digest. |
| `devkit override diff <bundle>:<asset>` | Customization | Shows 3-way diff between upstream baseline, updated wheel, and local override. |
| `devkit override accept <bundle>:<asset>` | Customization | Reconciles upstream updates and advances baseline digest. |
| `devkit override remove <bundle>:<asset>` | Customization | Unlinks local override and restores pristine upstream projection. |
| `devkit recover [--target <dir>]` | Fault Tolerance | Uses write-ahead journal in `.devkit/transient/` to roll back an interrupted transaction without overwriting newer edits. |
| `devkit bundle validate <source>` | Authoring | Verifies manifest syntax, schema rules, and existence of declared local source files. |
| `devkit bundle build <source> --output <zip>` | Packaging | Produces a deterministic ZIP archive with inventory hashes and normalized file permissions. |

### Sync Options and Modes
- `--agent <name>`: Narrows the agent targets (recorded as `agents` in `config.toml`). Repeatable; without any `agents` entry every supported agent is a target.
- `--no-agents`: Clears agent targets and unlinks unchanged native projections.
- `--preset <bundle>[:<name>]`: Selects `<bundle>` with `<name>` (or its default preset), replacing that bundle's entry in `config.toml`. Repeat a bundle to select a union. Use `<bundle>:all` for every asset.
- `--no-save`: Applies selection flags to this run only, without editing `config.toml`.
- `--dry-run`: Computes inventory and returns planned actions without writing to disk or configuration.
- `--check`: Read-only execution for CI pipelines. Exits with code `1` if workspace requires synchronization, a missing or stale `AGENTS.md` guidance block or a seeded file that was never written included. Seeded files that exist are never compared. An orphan alone does not fail `--check`: the modified file is no longer managed, so there is nothing to synchronize; it appears under `orphans` on that run and as a `stray` file afterwards if it sits under the managed root.
