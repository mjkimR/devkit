# Bundle Manifest Specification (`bundle.toml`)

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit-distribution`  
**Schema Version**: `1`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Transitive Dependencies](transitive-dependencies.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Content Wheel Contract

Content packages distribute assets as standard Python wheels installed into the consumer project's development environment. A content wheel registers an entry point under the `devkit_distribution.bundles` group:

```toml
[project.entry-points."devkit_distribution.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

```text
src/package_b_playbooks/
  __init__.py               # Empty module; strictly no runtime side effects
  bundle/
    bundle.toml             # Manifest declaring metadata and assets
    AGENTS.md               # Optional bundle constitution
    playbooks/review.md
    instructions/development.md
    skills/review/
      SKILL.md
```

### Discovery & Isolation Rules
- **Resource Module Reference**: The entry point value must point to an importable Python module, not a callable.
- **Root Directory**: The bundle contents and `bundle.toml` reside under the module's `bundle/` directory.
- **No Side Effects**: Loading a resource module triggers standard Python module initialization. Modules must keep `__init__.py` free of runtime side effects.
- **Static Inspection**: Synchronizing a bundle reads files purely through `importlib.resources.as_file`; it never executes rule scripts or imports rule code.
- **Unique Bundle Names**: Bundle names must be unique across all installed packages in the environment. Multiple packages declaring the same bundle name trigger an immediate error.
- **Non-Python Repositories**: Upstream repositories without Python logic (such as prompt collections or Go tools) can map their native directory layout into a content wheel at build time using Hatch `force-include` without modifying their original file structure.

---

## 2. Asset Kinds

A bundle declares assets across five supported kinds:

- `skill`: A directory containing `SKILL.md` along with supporting scripts, references, and assets. The entire directory tree is preserved, maintaining executable permissions (`0755`) for scripts.
- `subagent`: Native agent persona definitions or configuration files.
- `instruction`: Contextual guidance and prompt markdown documents linked to agent startup instructions.
- `playbook`: Operational workflows, checklists, and procedural guides.
- `rule`: Python-based governance rules evaluated by `agent-rule-engine`.

For full classification criteria, guidance placement rules, and naming standards, see the [Resource Taxonomy](../architecture/resource-taxonomy.md).

---

## 3. Manifest Syntax (`schema = 1`)

Every asset is identified by a logical tuple: `(bundle, kind, id)`. Asset IDs must be unique within each bundle.

```toml
schema = 1
name = "starter-workflow"
version = "0.1.0"

[[assets]]
id = "review"
kind = "skill"
source = "skills/review"

[[assets]]
id = "reviewer"
kind = "subagent"
[assets.variants]
codex = "native/codex/reviewer.toml"
claude-code = "native/claude-code/reviewer.md"

[[assets]]
id = "development"
kind = "instruction"
source = "instructions/development.md"

[[assets]]
id = "review-flow"
kind = "playbook"
source = "playbooks/review.md"

[presets.daily]
assets = ["development", "review-flow", "review"]
```

---

## 4. Manifest Rules and Validation

- **Strict Schema**: Unknown top-level keys or unrecognized table fields trigger immediate validation errors.
- **Slug Validation**: Bundle names and asset IDs must match lowercase slug regex `^[a-z][a-z0-9-]*$`.
- **Semantic Versioning**: Bundle versions must strictly follow `MAJOR.MINOR.PATCH` format.
- **Relative Path Sanitization**: Source paths must be relative POSIX paths. Paths containing traversal segments (`..`), backslashes (`\`), symlinks, or special device files are strictly rejected.
- **Source vs. Variants**: An asset must declare either a single `source` or a `variants` mapping matching supported agent names, never both.
- **Skills Integrity**: A `skill` source must point to a directory containing a valid `SKILL.md` file.
- **Verbatim Native Content**: Files declared under `variants` remain untouched during packaging and sync. The distributor does not parse, modify, or strip vendor-specific configuration keys.

---

## 5. Deterministic Local Archive Build

The `devkit bundle build <source> --output <zip>` command produces bit-for-bit reproducible ZIP archives for local authoring and verification:
- Files are sorted lexicographically by archive path.
- Entry timestamps are pinned to a fixed epoch (`1980-01-01 00:00:00 UTC`).
- File permissions are normalized to POSIX `0644` (regular files) or `0755` (executables).
- An internal SHA-256 inventory manifest is embedded to verify integrity before extraction.

*(Note: ZIP archives serve as a portable local export mechanism; the primary project synchronization transport uses installed uv content wheels).*
