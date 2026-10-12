# Workspace Ownership and Overrides Model

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit-distribution`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Synchronization & Transactions](sync-and-transactions.md)
- [Bundle Manifest Specification](manifest-spec.md)

---

## 1. Consumer Workspace Directory Structure

Consuming projects integrate bundles under a dedicated root directory: `.devkit/`.

```text
.devkit/
  config.toml             # Project-authored configuration: selected bundles/presets and agents (Git-tracked)
  installation.json       # Pinned packages, bundle versions, selections, file hashes & modes (Git-tracked)
  managed/<bundle>/       # Clean extracted upstream resources from wheels (Generated, Git-ignored)
  overrides/<bundle>/     # Full file replacements for managed assets (Git-tracked)
    .baseline/<bundle>/   # Pristine baseline copies preserved for 3-way drift diff (Git-tracked)
  transient/              # Transaction lock and recovery journal (Git-ignored)
    sync-journal.json     # Active write-ahead journal
<agent native paths>      # Projected native assets (e.g., .agents/, .codex/, .claude/)
```

---

## 2. Ownership Categories and Invariants

1. **Project Configuration (`.devkit/config.toml`)**:
   - Project-authored, Git-tracked TOML file declaring the selected bundles and their presets (`[presets]`) and the `agents` targets. Only selected bundles are deployed.
   - Owned by the developer. `devkit sync` never edits it on its own; only explicit selection commands (`devkit add`, `devkit remove`, and `devkit sync` selection flags without `--no-save`) edit the `agents` and `[presets]` entries, preserving unrelated tables, comments, and formatting.
   - Receipt files cannot claim ownership of `config.toml`.
2. **Managed Assets (`.devkit/managed/<bundle>/`)**:
   - Exact unpacked representation of upstream bundle resources extracted from installed wheels.
   - Read-only cache. Always regenerated deterministically by `devkit sync`.
   - Preserves original relative paths for instructions, playbooks, and rules.
3. **Project Native Projections**:
   - Copied projections placed into agent-specific directories (such as `.agents/skills/`, `.claude/skills/`, `.codex/agents/`, `.claude/agents/`).
   - Tracked explicitly by file path, SHA-256 hash, and POSIX mode in `installation.json`.
4. **Foreign File Protection**:
   - The distributor strictly manages only files recorded in `installation.json`.
   - Files created manually or by other tools in native agent directories are preserved.
   - If a synchronization step targets a file that already exists but is not recorded in the receipt, it is treated as an unmanaged collision and sync aborts immediately with `CollisionError`.
5. **User Modification Detection**:
   - If a deployed file's disk content or mode differs from its recorded receipt signature, it is treated as a user modification.
   - Sync aborts immediately across the entire project before making any disk changes.
   - Package removal, bundle deselection, or preset narrowing will only delete files that remain byte-for-byte identical to their recorded receipt signature. Modified files are never deleted.
6. **Git & Ignore Policy**:
   - The project configuration (`.devkit/config.toml`), overrides (`.devkit/overrides/`), and receipt (`.devkit/installation.json`) must be committed to version control.
   - Generated resources (`.devkit/managed/`), transient transaction files (`.devkit/transient/`), and generated native copies should be ignored according to the consumer repository's own `.gitignore` policy.
   - `devkit` never automatically modifies `.gitignore` or the Git index.

---

## 3. Project Overrides & 3-Way Drift Review Architecture

Consuming projects frequently require customizing an upstream guide, playbook, or skill for repository-specific nuances without maintaining a full upstream fork.

### Full-File Replacement Authoring Model

Overrides are stored as complete, valid files under `.devkit/overrides/<bundle>/<relative-path>` rather than unified `.patch` files:
- **Clean Readability & Tooling**: Overrides remain standard Markdown, TOML, or Python documents. They can be read, syntax-highlighted, formatted, and linted by standard IDE tools and AI agents without diff parser dependencies.
- **Zero Patch Drift / Rejection**: Eliminates fragile `patch reject` (`.rej`) failures caused by upstream line-number shifts or minor prose wording updates.
- **Direct Agent Editing**: AI coding agents can interact directly with the entire customized asset rather than having to parse and edit diff syntax.

### Baseline Digest Tracking

When an asset override is initialized (`devkit override create <bundle>:<asset>`), the current upstream resource's SHA-256 digest is saved into the receipt under `baseline_upstream_sha256`.

### Upstream Drift Detection

During `devkit sync`:
- If an overridden asset's upstream wheel is upgraded, `sync` compares the newly installed upstream digest with the recorded `baseline_upstream_sha256`.
- If the digests match, synchronization proceeds without interruption, projecting the local override into target agent directories.
- If the digests differ (`new_upstream_sha256 != baseline_upstream_sha256`), `sync` detects upstream drift, retains the local override projection safely, and emits an advisory:
  ```text
  WARNING: Upstream changed for overridden asset 'starter:development' (drift detected).
  Run 'devkit override diff starter:development' to review changes.
  ```

### Agent-Assisted 3-Way Reconciliation

To reconcile upstream updates with local customizations:
- `devkit override diff <bundle>:<asset>` provides a structured 3-way comparison:
  1. **Base**: Original upstream file content when the override was established.
  2. **Theirs (Upstream)**: Updated upstream file content in the current wheel package.
  3. **Mine (Override)**: Local customized file in `.devkit/overrides/<bundle>/...`.
- AI coding agents can inspect this 3-way diff, identify what new guidelines, contracts, or fixes upstream introduced, and intelligently merge those changes into the project's `.devkit/overrides/` file.
- `devkit override list` displays all active overrides and indicates whether upstream drift has been detected.
- Once merged, running `devkit override accept <bundle>:<asset>` updates `baseline_upstream_sha256` to the new upstream digest.
- Running `devkit override remove <bundle>:<asset>` unlinks the local override, cleans the receipt entry, and restores pristine upstream managed projection on the next sync.
