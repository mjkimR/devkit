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
      "starter": "daily"
    },
    "exclude_bundles": ["experimental-bundle"]
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
  }
}
```

### Receipt Properties
- Tracks exact package names, package versions, bundle names, and bundle versions.
- Records active agent selections and active preset restrictions.
- Stores active project overrides with their baseline upstream digests and local override hashes.
- Stores deployed asset mappings linking logical asset IDs to physical workspace file paths.
- Records expected SHA-256 digests and POSIX file modes (`0644` or `0755`) for every deployed file.
- Omits absolute filesystem paths and machine timestamps to ensure clean Git diffs across workstations.

---

## 2. Configuration Precedence

Target agents, bundle presets, and excluded bundles are resolved across three precedence tiers:

1. **Explicit CLI Options**: CLI arguments (`--agent`, `--no-agents`, `--preset`, `--exclude-bundle`, `--all-assets`) take highest precedence for temporary or ad-hoc runs and are persisted into the receipt.
2. **Project Configuration (`.devkit/config.toml`)**: A Git-tracked repository configuration declaring default agents, presets, and excluded bundles:
   ```toml
   schema = 1
   agents = ["codex", "claude-code"]
   exclude_bundles = ["starter"]

   [presets]
   starter = "daily"

   [playbooks]
   min_score = 0.1
   limit = 5
   max_bytes = 8192
   ```
   When running `devkit sync` without flags, values in `config.toml` take precedence over previous receipt state.
3. **Receipt State (`.devkit/installation.json`)**: When neither CLI options nor `config.toml` specify a selection, the existing receipt's selections are preserved.

---

## 3. Transaction Safety Guarantees (ACID Engine)

All mutating operations enforce strict transactional safety:

1. **Pre-Flight Validation**: Computes the complete desired file inventory, scans existing disk state, verifies file ownership, and checks for collisions before writing any bytes.
2. **Project Advisory Lock**: Acquires an exclusive, non-blocking file lock via `fcntl.flock` in `/tmp` keyed by SHA-256 hash of the target project directory path (`devkit-<uid>-<hash>.lock`). Concurrent operations fail immediately with an informative message.
3. **Write-Ahead Journal**: Before modifying disk, pending operations (file additions, modifications, unlinks) and base64-encoded backups of existing file contents are flushed to `.devkit/transient/sync-journal.json`.
4. **Atomic Replacement**: New and updated files are written to temporary sibling files (`.devkit-write-*`), permissions applied via `fchmod`, flushed with `fsync`, and atomically moved into place using `os.replace`. Directory entries are synced using directory `fsync`.
5. **Rollback Recovery**: If an operation is killed or interrupted mid-flight, subsequent `sync` invocations detect the existing journal and halt. Running `devkit recover` inspects every recorded file and safely restores original contents provided the file has not undergone subsequent user modifications.

---

## 4. Lifecycle Command Matrix

| Command | Lifecycle Phase | Description |
| --- | --- | --- |
| `devkit sync [options]` | Deployment | Discovers installed content packages, computes plan, performs pre-flight conflict checks, executes atomic transaction, and updates receipt. |
| `devkit list [--target <dir>]` | Discovery | Outputs JSON listing installed content packages, bundle metadata, available presets, and synchronized asset paths. |
| `devkit plan <source> [--preset <name>]` | Authoring | Previews managed file inventory for a local bundle source without writing to a consumer project. |
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
- `--agent <name>`: Adds an agent target to active selections (persisted in receipt). Repeatable.
- `--no-agents`: Clears all active agent selections and unlinks unchanged native projections.
- `--preset <bundle>:<name>`: Restricts synchronization for `<bundle>` to `<name>`. Repeatable across bundles.
- `--exclude-bundle <name>`: Excludes `<name>` from synchronization. Repeatable across bundles.
- `--all-assets`: Clears recorded preset restrictions, restoring full bundle asset deployment.
- `--dry-run`: Computes inventory and returns planned actions without writing to disk.
- `--check`: Read-only execution for CI pipelines. Exits with code `1` if workspace requires synchronization.
