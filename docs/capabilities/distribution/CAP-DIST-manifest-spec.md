---
id: CAP-DIST-manifest-spec
title: "Manifest Specification"
summary: "Bundle schema, asset kinds, execution-aware Markdown templates with bounded presentation-language inheritance, validation and deterministic archive builds."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/
  - packages/devkit-core/src/devkit_core/core/yaml.py
created_at: 2026-10-17
---

# [CAP-DIST-manifest-spec] Bundle Manifest Specification (`bundle.toml`)

Schema version `1`. How a bundle reaches a project as a Python package is specified in
`CAP-DIST-content-packages`.

## 1. Bundle Layout

A bundle is a directory with `bundle.toml` at its root, an optional `AGENTS.md` or `AGENTS.md.jinja` constitution (returned by
`devkit get-context`, see `CAP-DIST-context-and-playbooks`) and the asset sources the manifest declares:

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
standards are in the `ARCH-08-2-resource-taxonomy`.

- `skill`: a directory containing exactly one of `SKILL.md` or `SKILL.md.jinja` and supporting files; the whole tree is deployed, executable bits
  (`0755`) preserved. One `source` serves every agent; `variants` ship a directory per agent. `invocation` (optional,
  `auto` or `user`, default `auto`) says who starts the skill: under `user` only an explicit user invocation does,
  and each projection carries the agent's native setting
  (`CAP-DIST-agent-projections`).
- `subagent`: a delegated agent persona: native files per agent (`variants`, copied verbatim) or one host-neutral
  role contract (`source`) rendered per selected agent. See `CAP-DIST-agent-projections`.
- `instruction`: Markdown whose YAML frontmatter declares a nonempty `name` and `description`, the header
  `devkit get-context` catalogs. Every file of the source, including each file of a directory source, carries one.
- `playbook`: a procedure for an occasional task, found through explicit playbook search or retrieved by its exact
  manifest ID or a declared alias (a previous asset ID in the header's `aliases`); header rules are in
  `CAP-DIST-context-and-playbooks`.
- `rule`: Python governance rules run by `devkit_agt.features.rules`, shipped as one plugin package directory per asset (see
  **Plugin packages** below). The receipt lists every deployed file under the asset's `paths` and `devkit rules`
  loads the package from there; a consumer configures the rules in `[rules]` of `.devkit/config.toml`.
- `workflow`: one Markdown delivery workflow definition (frontmatter `id` and `stages`) run by `devkit_agt.features.workflow`.
  Distribution validates the header only (`devkit workflow validate` checks stage semantics). When at least one
  workflow is synchronized, `devkit sync` generates the `devkit-workflow` entry skill under
  `.devkit/managed/_devkit/skills/`, projects it into every selected agent, and records the definition under
  `entrypoints` in the receipt so `devkit workflow` finds it without configuration.
- `gate`: Python commit gates in one plugin package directory per asset, run by `devkit_agt.features.gate` at a Git hook stage,
  loaded from the receipt's `paths` and configured in `[gates]` of `.devkit/config.toml` or the per-clone `.git/devkit.config`; see the
  `CAP-GATE-commit-gates`.
- The engines of `rule`, `workflow` and `gate` assets (`devkit_agt.features.rules`, `devkit_agt.features.workflow`, `devkit_agt.features.gate`) ship with
  `devkit-agt`; `devkit-dist` deploys these kinds without them and reports them with `HARNESS_ENGINE_MISSING`
  (`CAP-DIST-sync-and-transactions`).
- `hook`: one declarative TOML file selecting a host, event and installed service handler. Sync manages exact
  registrations in a shared host file, recorded under `host_hooks` in the receipt. Codex command hooks are the
  initial target; see `CAP-HOST-lifecycle-observation` for schema, deployment and runtime.
- `document`: plain files with no engine semantics. Unseeded, a managed copy agents read by path. With
  `seeded = true` and a `target`, a **seeded** asset: written once to the workspace-relative `target` (a directory
  source to `target/<relative path>`, executable bits preserved) when that path does not exist, then project-owned;
  this is how a bundle scaffolds a docs tree, a glossary or a policy file. Seeded files are never catalogued by
  `get-context`, playbook search or projections. Runtime behavior:
  `CAP-DIST-workspace-ownership`.
- `guidance`: a fragment of the root `AGENTS.md` guidance block, for a pointer every agent session must see (for
  example "read the commit conventions before writing a commit message"). The source is one Markdown file of list
  items: every line is a `- ` item or a two-space continuation line, no blank lines or HTML comments, at most 300
  UTF-8 bytes. `{path:<asset-id>}` names another asset of the same bundle; `devkit sync` replaces it with the path
  agents read (the rendered managed `.md` for templates; otherwise the project override, else the managed copy). A fragment is also deployed as a managed copy and may be
  overridden; the override must meet the same rules. With `guidance_block = false` fragments are written nowhere.
  Block placement and ordering: `CAP-DIST-workspace-ownership`.

## 3. Manifest Syntax

```toml
schema = 1
name = "starter-workflow"
version = "0.1.0"
default_preset = "daily"
context_documents = "docs/steering"       # optional: get-context lists this directory's Markdown titles

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
  leave it off for content a project adds deliberately (the built-in `devkit`, `advisory` and `harness` bundles set
  it, `git-commits` and `authoring` do not). Until a project selects presets explicitly, upgrades follow the current
  `default_preset`. See the `CAP-DIST-sync-and-transactions`.

## 4. Validation

- **Strict schema**: unknown top-level keys or table fields are errors.
- **Slugs**: bundle names, asset ids and preset names match `^[a-z][a-z0-9-]*$`.
- **Versions**: bundle versions are `MAJOR.MINOR.PATCH`.
- **Source paths**: canonical relative POSIX paths (validated by `devkit_core.core.paths`); `..`, redundant `.` segments
  or separators, symlinks and special files are rejected, and so are backslashes, so a manifest names the same files
  on every platform.
- **Editing by-products**: inside a directory source, `.DS_Store`, `__pycache__/` and `*.pyc` are not bundle content:
  never validated, deployed, hashed or archived.
- **Source vs. variants**: an asset declares either one `source` or a `variants` mapping, never both. Only `skill`
  and `subagent` assets, the kinds projected per agent (`CAP-DIST-agent-projections`),
  may declare `variants`; its keys must be supported agent names (`antigravity`, `claude-code`, `codex`).
- **Skills**: a `skill` source or variant is a directory containing exactly one of `SKILL.md` or `SKILL.md.jinja`.
  The final entry is UTF-8 with valid YAML mapping frontmatter when present; rendering and validation precede
  insertion of the context prerequisite. Declaring both entries is `BUNDLE_INVALID`. `codex` and `antigravity` variants
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
  [`devkit_core.core.plugins`](../../development/reference/core.md). Guides, resources and tests ship in the same directory; a rule's
  tests in its `tests/` folder run with `devkit rules test` (`CAP-GOV-rule-authoring`).
- **Native subagents**: each `subagent` variant is one file with the agent's native suffix: `.toml` for `codex`,
  `.md` for `claude-code` and `antigravity`.
- **Headers**: instruction, playbook and workflow headers and role contracts follow the frontmatter grammar of
  `devkit_core.core.frontmatter` (a `---` opener, a `---` or `...` closer, a YAML mapping without duplicate keys).
  Python YAML syntax uses `devkit_core.core.yaml` and its LibYAML safe loader. If the PyYAML C binding is unavailable, the read fails with `YAML_BINDING_UNAVAILABLE` and exit `2`; it does not become a `BUNDLE_INVALID` header warning or use Python parsing.
- **Role contracts**: a `subagent` declared with `source` is a single Markdown file whose frontmatter has `role` equal
  to the asset id, `title`, `description`, a `hosts` table with a block for every supported agent (valid statuses,
  allowlisted keys), and a nonempty body (`CAP-DIST-agent-projections`).
- **Workflows**: two `workflow` assets of one bundle may not declare the same header `id`.
- **Playbook aliases**: across the `playbook` assets of one bundle, no header alias may equal a playbook asset ID of
  the bundle (its own included) or an alias another playbook already declares (`BUNDLE_INVALID`;
  `ADR-playbook-aliases-as-identifiers`).
- **Presets**: asset lists are nonempty, unique and reference declared ids.
- **Verbatim native content**: `subagent` variant files are never parsed, modified or stripped. Skill variants are
  deployed like a skill `source`, context prerequisite included
  (`CAP-DIST-context-and-playbooks`).
- **Guidance fragments**: a single `source` file (no `variants`, never `seeded`) meeting the fragment rules above.
  Each `{path:<asset-id>}` names an asset of the bundle with exactly one file `source` that is neither `guidance` nor
  seeded, and every preset that selects the fragment selects the named assets too.
- **Context documents**: `context_documents` (optional top-level string) names one workspace directory whose
  Markdown files `devkit get-context` lists by `title` and `summary` (`CAP-DIST-context-and-playbooks`). It follows
  the seeded `target` grammar below; another type or an unsafe path is `BUNDLE_INVALID`.
- **Seeded assets**: `seeded` (boolean, default `false`) is allowed only on a `document` with a single `source`, and
  requires `target`; `target` is rejected otherwise. `target` is a normalized relative POSIX path (no `..`, leading
  `/`, backslash or `.` segment) whose first segment is not `.devkit`, `.agents`, `.claude` or `.codex`, which has
  no `.git` segment at any depth, and which is not `AGENTS.md`, all compared case-insensitively (macOS file systems
  usually are). Two selected bundles may not seed the same path.

## 5. Deterministic Local Archive Build

`build_source(source, output)` remains an application usecase for deterministic local ZIP export and
verification. It has no public CLI command; projects receive bundles as installed wheels, not archives.

- Entries are sorted by archive path, timestamps pinned to `1980-01-01 00:00:00 UTC`, modes normalized to `0644` or
  `0755`.
- Raw constitution templates retain their source-relative `AGENTS.md.jinja` name in archives, so reloaded sources still render for the selected environment.
- An embedded `inventory.json` records the SHA-256 and mode of every archived file.
- A failed build leaves no partial archive; an existing output file is never replaced.

## Markdown templates and bundle variables

An instruction, guidance, document or skill source, or a common host-neutral subagent contract, MAY contain explicit `.md.jinja` files. The constitution MAY be `AGENTS.md.jinja`; coexistence with `AGENTS.md` is `BUNDLE_INVALID`. Only explicit templates render; ordinary Markdown preserves literal Jinja syntax. Native subagent variants and executable workflow, rule, hook and gate assets do not support templates. Another template kind or preceding extension is `BUNDLE_INVALID`. The final `.jinja` suffix alone is removed from each
managed and native skill destination and from directory-seeded filenames. An explicit seeded `target` remains the authored path.
Two distinct source paths mapping to the same managed destination, or a file and its descendant, are
`BUNDLE_INVALID`, even with identical bytes.

The manifest declares every configurable input, using identifier names matching `[a-z][a-z0-9_]*`:

```toml
[variables.language]
type = "string"
default = "auto"

[variables.max_items]
type = "integer"
default = 3

[variables.show_examples]
type = "boolean"
default = false
```

`type` is required and exactly `string`, `boolean` or `integer`; `default` is optional and must have that exact type
(booleans are not integers). The optional `default_from = "presentation.language"` is valid only for string
variables and only for this exact reference; another reference or type raises `BUNDLE_INVALID`. No other declaration
keys are accepted. An absent consumer value inherits the resolved presentation preference in workspace planning.
An explicit bundle value always wins, including `auto` and free text. Projectless planning uses the ordinary declared
default. Without either a resolving binding or a default, the input is required.
Variable declarations validate without rendering; template content validation occurs on inventory planning.
`bundle plan` uses defaults and fails with `CONFIG_INVALID` for a required input it cannot resolve.

Project configuration supplies inputs as defined by `CAP-DIST-sync-and-transactions`. Templates receive only the
resolved `vars` mapping and reserved `execution.environment`, exactly `local` or `cloud`. Sync resolves the invocation flag, effective workspace setting, then the local default once before canonical and effective inventory planning. Projectless planning uses `local`. The reserved input is independent of configurable bundle variables. No project-wide configuration, process environment, paths, clock, loader or global functions are exposed. Jinja uses a sandbox,
StrictUndefined, UTF-8, LF output, no HTML escaping, preserved trailing newlines and no Python attribute access or
calls. Available filters are `lower`, `upper`, `trim`, `default`, `replace`, `length`; built-in Jinja tests remain
available. The sandbox limits access, not resource consumption; bundles remain installed, trusted content.

Syntax, evaluation, UTF-8 and rendered instruction-header, skill-frontmatter, subagent-contract or guidance errors are
`BUNDLE_INVALID` before writes. Rendered skill files obey the manifest-owned invocation restrictions before native
settings and context prerequisites are inserted; these checks and common subagent contract validation run even with no selected agents. Templated common contracts render before host validation/projection and always cite the final managed `.md` file, with raw override provenance recorded separately. Ordinary Markdown contracts cite the override path when present.
Guidance fragment formatting, the 300-byte limit, path references and selected target requirements apply to the
rendered text. These checks also apply to project template overrides. Ordinary source validation is unchanged.
Jinja is imported only when a `.md.jinja` file actually renders, never merely by loading a bundle or its manifest.
