---
id: CAP-DIST-manifest-spec
title: "Manifest Specification"
summary: "Schema, asset kinds, presets, validation, and deterministic archive builds for devkit bundles."
area: distribution
status: active
created_at: 2026-10-17
---

# [CAP-DIST-manifest-spec] Bundle Manifest Specification (`bundle.toml`)

Schema version `1`. How a bundle reaches a project as a Python package is specified in
[Content Packages](../../distribution/content-packages.md).

## 1. Bundle Layout

A bundle is a directory with `bundle.toml` at its root, an optional `AGENTS.md` constitution (returned by
`devkit get-context`, see [Context Loading](../../distribution/context-and-playbooks.md)) and the asset sources the manifest declares:

```text
bundle/
  bundle.toml
  AGENTS.md                 # optional constitution
  instructions/development.md
  playbooks/review.md
  skills/review/SKILL.md
```

## 2. Asset Kinds

Every asset is identified by `(bundle, kind, id)`; ids are unique within a bundle. Classification criteria and naming
standards are in the [Resource Taxonomy](../../architecture/resource-taxonomy.md).

- `skill`: a directory containing `SKILL.md` and supporting files; the whole tree is deployed, executable bits
  (`0755`) preserved. One `source` serves every agent; `variants` ship a directory per agent. `invocation` (optional,
  `auto` or `user`, default `auto`) says who starts the skill: under `user` only an explicit user invocation does,
  and each projection carries the agent's native setting
  ([Agent Projections](../../distribution/agent-projections.md#2-projection-rules)).
- `subagent`: a delegated agent persona: native files per agent (`variants`, copied verbatim) or one host-neutral
  role contract (`source`) rendered per selected agent. See [Agent Projections](../../distribution/agent-projections.md).
- `instruction`: Markdown whose YAML frontmatter declares a nonempty `name` and `description`, the header
  `devkit get-context` catalogs. Every file of the source, including each file of a directory source, carries one.
- `playbook`: a procedure for an occasional task, found through playbook search; header rules are in
  [Context Loading & Playbooks, section 3](../../distribution/context-and-playbooks.md#3-playbook-discovery-and-search-devkit-playbook).
- `rule`: Python governance rules run by `devkit.rules`, shipped as one plugin package directory per asset (see
  **Plugin packages** below). The receipt lists every deployed file under the asset's `paths` and `devkit rules`
  loads the package from there; a consumer configures the rules in `[rules]` of `.devkit/config.toml`.
- `workflow`: one Markdown delivery workflow definition (frontmatter `id` and `stages`) run by `devkit.workflow`.
  Distribution validates the header only (`devkit workflow validate` checks stage semantics). When at least one
  workflow is synchronized, `devkit sync` generates the `devkit-workflow` entry skill under
  `.devkit/managed/_devkit/skills/`, projects it into every selected agent, and records the definition under
  `entrypoints` in the receipt so `devkit workflow` finds it without configuration.
- `gate`: Python commit gates in one plugin package directory per asset, run by `devkit.gate` at a Git hook stage,
  loaded from the receipt's `paths` and configured in `[gates]` of `.devkit/config.toml` or the per-clone `.git/devkit.config`; see the
  [Commit Gate Overview](../../gate/overview.md).
- `hook`: one declarative TOML file selecting a host, event and installed service handler. Sync manages exact
  registrations in a shared host file, recorded under `host_hooks` in the receipt. Codex command hooks are the
  initial target; see [Host Integration](../../host/overview.md#2-hook-assets) for schema, deployment and runtime.
- `document`: plain files with no engine semantics. Unseeded, a managed copy agents read by path. With
  `seeded = true` and a `target`, a **seeded** asset: written once to the workspace-relative `target` (a directory
  source to `target/<relative path>`, executable bits preserved) when that path does not exist, then project-owned;
  this is how a bundle scaffolds a docs tree, a glossary or a policy file. Seeded files are never catalogued by
  `get-context`, playbook search or projections. Runtime behavior:
  [Workspace Ownership, section 2](../../distribution/workspace-ownership.md#2-ownership-categories-and-invariants).
- `guidance`: a fragment of the root `AGENTS.md` guidance block, for a pointer every agent session must see (for
  example "read the commit conventions before writing a commit message"). The source is one Markdown file of list
  items: every line is a `- ` item or a two-space continuation line, no blank lines or HTML comments, at most 300
  UTF-8 bytes. `{path:<asset-id>}` names another asset of the same bundle; `devkit sync` replaces it with the path
  agents read (the project override, else the managed copy). A fragment is also deployed as a managed copy and may be
  overridden; the override must meet the same rules. With `guidance_block = false` fragments are written nowhere.
  Block placement and ordering: [Workspace Ownership, section 2](../../distribution/workspace-ownership.md#2-ownership-categories-and-invariants).

## 3. Manifest Syntax

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
id = "release"
kind = "skill"
source = "skills/release"
invocation = "user"                    # only an explicit user invocation starts it

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

- `[presets.<slug>]` names a purpose-specific asset subset. Every bundle also has the reserved preset `all`
  (every declared asset); `[presets.all]` cannot be declared.
- `default_preset` (optional) is the preset a consumer receives when selecting the bundle without naming one (for
  example `devkit add starter-workflow`); it must be a declared preset or `all`. `devkit add` records the resolved
  preset name, so a later upstream change to `default_preset` never changes an explicit selection. A bundle without
  it must be selected with an explicit preset.
- `auto_select` (optional boolean, default `false`) deploys the bundle with its `default_preset`, which is then
  required, as soon as its package is installed, without `devkit add`; a project opts out with
  `[presets] <bundle> = false`. Any package may set it, and it applies to a package installed as a runtime dependency
  of another one as well. Set it when the default preset is what nearly every project installing the package wants;
  leave it off for content a project adds deliberately (the built-in `devkit` and `advisory` bundles set it,
  `authoring` and `git-commits` do not). Until a project selects presets explicitly, upgrades follow the current
  `default_preset`. See the [selection model](../../distribution/sync-and-transactions.md#2-asset-selection-model).

## 4. Validation

- **Strict schema**: unknown top-level keys or table fields are errors.
- **Slugs**: bundle names, asset ids and preset names match `^[a-z][a-z0-9-]*$`.
- **Versions**: bundle versions are `MAJOR.MINOR.PATCH`.
- **Source paths**: canonical relative POSIX paths (validated by `devkit.core.paths`); `..`, redundant `.` segments
  or separators, symlinks and special files are rejected, and so are backslashes, so a manifest names the same files
  on every platform.
- **Editing by-products**: inside a directory source, `.DS_Store`, `__pycache__/` and `*.pyc` are not bundle content:
  never validated, deployed, hashed or archived.
- **Source vs. variants**: an asset declares either one `source` or a `variants` mapping, never both. Only `skill`
  and `subagent` assets, the kinds projected per agent ([Agent Projections](../../distribution/agent-projections.md#1-projection-matrix)),
  may declare `variants`; its keys must be supported agent names (`antigravity`, `claude-code`, `codex`).
- **Skills**: a `skill` source or variant is a directory containing a `SKILL.md` that is UTF-8 and, when it opens a
  frontmatter block, closes it (sync inserts the context prerequisite after it). `codex` and `antigravity` variants
  project to the same `.agents/skills/<asset-id>/` and must be identical (same files, bytes and modes). The ids
  `devkit-playbook` and `devkit-workflow` are reserved for the entry skills `devkit sync` generates.
- **Skill invocation**: only `skill` assets declare `invocation`, and only `auto` or `user`. `bundle.toml` is the one
  place a bundle sets it: a skill source or variant whose `SKILL.md` frontmatter declares `disable-model-invocation`,
  or whose `agents/openai.yaml` declares `policy.allow_implicit_invocation`, is invalid whatever its `invocation`,
  and so is an `agents/openai.yaml` that is not a YAML mapping (with an optional `policy` mapping). A project
  override of the skill is held to the same rule at sync.
- **Plugin packages**: the `source` of a `rule` or `gate` asset is a directory (a file is
  `BUNDLE_INVALID` with a fix naming the directory to move it into). Every `.py` file in it, recursively, is a module
  of one package, except files under a `tests` directory, `test_*.py`, `*_test.py`, `__pycache__` and hidden
  entries; `__init__.py` is optional. The directory must contain at least one module, every directory and file name
  of a module must be a Python identifier, and no module may have two files (`a.py` beside `a/__init__.py` or
  beside a package directory `a/`). Modules import each other relatively; the loading model is
  [`devkit.core.plugins`](../../core/reference.md). Guides, resources and tests ship in the same directory; a rule's
  tests in its `tests/` folder run with `devkit rules test` ([Testing a Rule](../../rules/rule-authoring.md#6-testing-a-rule)).
- **Native subagents**: each `subagent` variant is one file with the agent's native suffix: `.toml` for `codex`,
  `.md` for `claude-code` and `antigravity`.
- **Headers**: instruction, playbook and workflow headers and role contracts follow the frontmatter grammar of
  `devkit.core.frontmatter` (a `---` opener, a `---` or `...` closer, a YAML mapping without duplicate keys).
- **Role contracts**: a `subagent` declared with `source` is a single Markdown file whose frontmatter has `role` equal
  to the asset id, `title`, `description`, a `hosts` table with a block for every supported agent (valid statuses,
  allowlisted keys), and a nonempty body ([format](../../distribution/agent-projections.md#role-contract-format)).
- **Workflows**: two `workflow` assets of one bundle may not declare the same header `id`.
- **Presets**: asset lists are nonempty, unique and reference declared ids.
- **Verbatim native content**: `subagent` variant files are never parsed, modified or stripped. Skill variants are
  deployed like a skill `source`, context prerequisite included
  ([Context Loading](../../distribution/context-and-playbooks.md#skill-prerequisite)).
- **Guidance fragments**: a single `source` file (no `variants`, never `seeded`) meeting the fragment rules above.
  Each `{path:<asset-id>}` names an asset of the bundle with exactly one file `source` that is neither `guidance` nor
  seeded, and every preset that selects the fragment selects the named assets too.
- **Seeded assets**: `seeded` (boolean, default `false`) is allowed only on a `document` with a single `source`, and
  requires `target`; `target` is rejected otherwise. `target` is a normalized relative POSIX path (no `..`, leading
  `/`, backslash or `.` segment) whose first segment is not `.devkit`, `.agents`, `.claude` or `.codex`, which has
  no `.git` segment at any depth, and which is not `AGENTS.md`, all compared case-insensitively (macOS file systems
  usually are). Two selected bundles may not seed the same path.

## 5. Deterministic Local Archive Build

`devkit bundle build <source> --output <zip>` produces a bit-for-bit reproducible ZIP for local export and
verification; projects receive bundles as installed wheels, not archives.

- Entries are sorted by archive path, timestamps pinned to `1980-01-01 00:00:00 UTC`, modes normalized to `0644` or
  `0755`.
- An embedded `inventory.json` records the SHA-256 and mode of every archived file.
- A failed build leaves no partial archive; an existing output file is never replaced.
