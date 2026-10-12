# Bundle Manifest Specification (`bundle.toml`)

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit`  
**Schema Version**: `1`  
**Related Documents**:
- [Distribution Overview](overview.md)
- [Workspace Ownership & Overrides](workspace-ownership.md)
- [Transitive Dependencies](transitive-dependencies.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Content Wheel Contract

Content packages distribute assets as standard Python wheels installed into the consumer project's development environment. A content wheel registers an entry point under the `devkit.distribution.bundles` group:

```toml
[project.entry-points."devkit.bundles"]
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

A bundle declares assets across nine supported kinds:

- `skill`: A directory containing `SKILL.md` along with supporting scripts, references, and assets. The entire directory tree is preserved, maintaining executable permissions (`0755`) for scripts.
- `subagent`: A delegated agent persona. Either native files per agent (`variants`, copied verbatim) or one host-neutral role contract (`source`, a single Markdown file) whose frontmatter declares `role` (equal to the asset id), `title`, `description`, an optional `skill` and a `hosts` table with one block per agent (`claude-code`, `codex`, `antigravity`). Each block carries a `status` (`native`, `emulated`, `unsupported`, `unverified`) and only allowlisted host-native keys; `devkit sync` renders the projection for each selected agent from that block, writes no file for `unsupported`, and fails for an agent the contract does not mention. The body is the role's prompt. See [Agent Projections](agent-projections.md).
- `instruction`: Contextual guidance: Markdown documents whose YAML frontmatter declares a nonempty `name` and `description` (the header `devkit get-context` catalogs). Every file of an instruction source, including each file of a directory source, must carry such a header; it is validated when the bundle is loaded.
- `playbook`: Operational workflows, checklists, and procedural guides.
- `rule`: Python-based governance rules evaluated by `devkit.rules`. The receipt lists every deployed file under the asset's `paths`, and `devkit rules` loads them from there; a consumer configures them in `[rules]` of `.devkit/config.toml` rather than editing the managed copy.
- `workflow`: A single Markdown delivery workflow definition (frontmatter `id` and `stages`) evaluated by `devkit.workflow`. Distribution validates the header only; `devkit workflow validate` validates stage semantics. When at least one workflow asset is synchronized, `devkit sync` generates the shared `devkit-workflow` entry skill under `.devkit/managed/_devkit/skills/` and projects it into every selected agent's skill directory, and the receipt records the definition under `entrypoints` so `devkit workflow` discovers it without configuration.
- `workflow-check`: Python check evaluators (`BaseCheck` subclasses) that `devkit.workflow` adds to its check registry. Deployed and recorded like `rule` files; the engine loads them from the receipt. See [Workflow Definitions and Checks](../workflow/definition-and-checks.md).
- `gate`: A Python commit gate run by `devkit.gate` at a Git hook stage. Like rules, deployed files are listed in the receipt under the asset's `paths` and loaded from there at commit time; a consumer configures them in `[gates]` of `.devkit/config.toml` or the per-clone `.git/devkit.config`. See [Commit Gate Overview](../gate/overview.md).
- `document`: Plain files with no engine semantics. Unseeded, a document is a managed copy under `.devkit/managed/<bundle>/` (reference material agents read by path). With `seeded = true` and a `target`, it is a **seeded** asset: written once to the workspace-relative `target` when that path does not exist, then owned by the project. A directory source seeds every file under it to `target/<relative path>`, preserving executable bits. Only `document` assets may be seeded; this is how a bundle scaffolds a documentation tree, a glossary or a policy file that the project is expected to edit. Seeded files are never catalogued by `get-context`, playbook search or projections. See [Workspace Ownership, section 2](workspace-ownership.md#2-ownership-categories-and-invariants).

For full classification criteria, guidance placement rules, and naming standards, see the [Resource Taxonomy](../architecture/resource-taxonomy.md).

---

## 3. Manifest Syntax (`schema = 1`)

Every asset is identified by a logical tuple: `(bundle, kind, id)`. Asset IDs must be unique within each bundle.

```toml
schema = 1
name = "starter-workflow"
version = "0.1.0"
default_preset = "daily"

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
antigravity = "native/antigravity/reviewer.md"

[[assets]]
id = "challenger"
kind = "subagent"
source = "subagents/challenger.md"     # host-neutral role contract, rendered per agent

[[assets]]
id = "development"
kind = "instruction"
source = "instructions/development.md"

[[assets]]
id = "review-flow"
kind = "playbook"
source = "playbooks/review.md"

[[assets]]
id = "direct-delivery"
kind = "workflow"
source = "workflows/direct-delivery.md"

[[assets]]
id = "docs-skeleton"
kind = "document"
seeded = true                          # written once to target, then project-owned
source = "seed/docs"                   # a directory: every file lands under target/
target = "docs"

[presets.daily]
assets = ["development", "review-flow", "review"]

[presets.delivery]
assets = ["development", "review-flow", "review", "direct-delivery"]
```

### Presets and the Default Preset

- **Presets** (`[presets.<slug>]`) name purpose-specific asset subsets. Each preset lists one or more unique, declared asset IDs.
- **Reserved `all` preset**: Every bundle implicitly provides a preset named `all` that selects every declared asset. Authors cannot declare `[presets.all]`.
- **`default_preset`** (optional): Names the preset a consumer receives when it selects the bundle without naming a preset (for example `devkit add starter-workflow`). The value must be a declared preset or `all`.
- The default preset is a recommendation applied **only at selection time**. Installing the wheel never selects the bundle, and consumer configuration records the resolved preset name rather than a reference to the default, so a later upstream change to `default_preset` never changes an existing consumer selection. See [Synchronization & Transactions](sync-and-transactions.md#2-asset-selection-model).
- A bundle without `default_preset` must be selected with an explicit preset name.

---

## 4. Manifest Rules and Validation

- **Strict Schema**: Unknown top-level keys or unrecognized table fields trigger immediate validation errors.
- **Slug Validation**: Bundle names and asset IDs must match lowercase slug regex `^[a-z][a-z0-9-]*$`.
- **Semantic Versioning**: Bundle versions must strictly follow `MAJOR.MINOR.PATCH` format.
- **Relative Path Sanitization**: Source paths must be canonical relative POSIX paths (validated by `devkit.core.paths`). Paths containing traversal segments (`..`), redundant `.` segments or separators, symlinks, or special device files are rejected. Backslashes are rejected too, as an authoring rule, so a manifest names the same files on every platform.
- **Editing By-Products**: Inside a directory source, `.DS_Store` files, `__pycache__/` directories and `*.pyc` files are not bundle content: they are never validated, deployed, hashed or archived.
- **Source vs. Variants**: An asset must declare either a single `source` or a `variants` mapping, never both. `variants` keys must be supported agent names (`antigravity`, `claude-code`, `codex`); any other key is rejected.
- **Skills Integrity**: A `skill` source must point to a directory containing a valid `SKILL.md` file.
- **Header Integrity**: Instruction, playbook and workflow headers and role contracts follow the one frontmatter grammar of `devkit.core.frontmatter` (a `---` opener, a `---` or `...` closer, a YAML mapping without duplicate keys).
- **Contract Integrity**: A `subagent` declared with `source` must be a single Markdown file whose frontmatter has `role` equal to the asset id, `title`, `description`, a nonempty `hosts` table with valid statuses and allowlisted keys, and a nonempty body.
- **Preset Integrity**: Preset names are slugs and `all` is reserved. Preset asset lists must be nonempty, unique, and reference declared asset IDs. `default_preset` must name a declared preset or `all`.
- **Verbatim Native Content**: Files declared under `variants` remain untouched during packaging and sync. The distributor does not parse, modify, or strip vendor-specific configuration keys.
- **Seeded Assets**: `seeded` is a boolean (default `false`) allowed only on `document` assets declared with a single `source`. A seeded asset requires `target`, and `target` is rejected otherwise. `target` is a normalized relative POSIX path (no `..`, no leading `/`, no backslashes, no `.`) whose first segment is not `.devkit`, `.git`, `.agents`, `.claude` or `.codex`, and which is not `AGENTS.md`, all compared case-insensitively. Two selected bundles may not seed the same path.

---

## 5. Deterministic Local Archive Build

The `devkit bundle build <source> --output <zip>` command produces bit-for-bit reproducible ZIP archives for local authoring and verification:
- Files are sorted lexicographically by archive path.
- Entry timestamps are pinned to a fixed epoch (`1980-01-01 00:00:00 UTC`).
- File permissions are normalized to POSIX `0644` (regular files) or `0755` (executables).
- An `inventory.json` with the SHA-256 and mode of every archived file is embedded, so the archive can be checked against it.
- A build that fails leaves no partial archive behind; an existing output file is never replaced.

*(Note: ZIP archives serve as a portable local export mechanism; the primary project synchronization transport uses installed uv content wheels).*
