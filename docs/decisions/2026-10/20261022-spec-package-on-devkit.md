---
id: ADR-spec-package-on-devkit
title: devkit-spec as a Python layer on devkit
summary: "For spec-driven development beside devkit's generic engines, we build devkit-spec as a Python package mounted as devkit spec, with package-implemented rules, devkit-owned policy tables, spec-* skills and an opt-in docs skeleton, to keep devkit SDD-agnostic, accepting it follows devkit's versions."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-rebuild-spec-on-devkit
  - ADR-mount-under-the-devkit-command-line
  - ADR-policy-in-the-tool-spec-table
  - ADR-rules-implemented-in-the-package
  - ADR-skills-named-spec
  - ADR-docs-skeleton-is-opt-in
---

# [ADR-spec-package-on-devkit] devkit-spec as a Python layer on devkit

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @mjkimR
- **Involved Components/Capabilities**: `ARCH-03-context`, `ARCH-05-1-containers`, `ARCH-05-2-components`,
  `ARCH-08-cross-cutting`, `CAP-HARN-agent-guidance`, `CAP-HARN-command-mount`, `CAP-GOV-spec-rules`,
  `CAP-TRACE-code-entrypoints`, `CAP-DLV-project-policy`, `CAP-DLV-delivery-workflows`

---

## 1. Context & Problem Statement

Spec-driven development was originally delivered as a standalone Go CLI: its own installer and managed directory, its
own rule runner, workflow engine, commit command, worktree commands, search and a web viewer, shipped as one executable
per platform. devkit has since become the foundation for agent tooling with the same generic engines: asset
distribution, rules, workflows, commit gates, search, worktrees and the Agent Advisory Protocol. Keeping both meant two
implementations of every engine, two output contracts, platform builds and macOS runner minutes in CI.

Rebuilding on devkit raises the questions of the package's shape:

- **Commands**: devkit-spec needs commands of its own (`resolve`, `refs`, `list`, `search`, `new`, `proposal`,
  `entrypoints`, `scope`, `policy`). Agents, Git hooks and CI already run `uv run devkit ...`, and devkit offers the
  `devkit.commands` entry-point group: an installed package adds a command group to the `devkit` root group, imported
  only when its command runs.
- **Policy**: earlier implementations read policy from a dedicated configuration file (approvals per gate, the feedback
  sweep, pull requests, branch cleanup and `git.worktree`). `.devkit/config.toml` already models most of it:
  `[workflow.approvals]` (gate policy `ask`, `auto`, `off`), `[workflow.stages]` and `[worktree]` (`pull_request`,
  `delete_branch`, `setup`); devkit passes `[tool.<name>]` tables through unread.
- **Rules**: devkit's rule engine loads `kind = "rule"` assets from the synchronized copies of a bundle
  (`.devkit/managed/<bundle>/rules/<name>/rule.py`) and instantiates the rule classes a rule file defines; the guide
  beside the file is what `devkit rules explain` prints. The spec rules share a substantial library: the document
  index, the Markdown scanner, namespaces and the entrypoint path contract.
- **Skill names**: earlier skill designs used `sr` and `sr-*` (the specify-stage skill was `sr-spec`). devkit-spec ships
  them in the bundle `spec`, next to the command group `devkit spec` and the constitution returned by
  `devkit get-context spec`; users invoke skills by name and workflow definitions list them per stage.
- **Docs skeleton**: previously a `docs/` skeleton (`template/docs`, plus `glossary.yaml`) was written automatically on
  initialization. In devkit, a `kind = "document"` asset with `seeded = true` is written once where the target file is
  absent and is project-owned afterwards; the `spec` bundle declares `auto_select`, so its default preset deploys on the
  next `devkit sync` after installation.

---

## 2. Decision Drivers

- No second implementation of a generic engine devkit already has.
- devkit stays SDD-agnostic: the document model and its rules never move into devkit.
- No platform binaries and no Go toolchain in consumer projects.
- One agent-first output contract and one advisory format across all commands.
- CI cost of private runners (no macOS builds).
- One place for an agent to look for every command; devkit's startup path (lazy command loading), output options,
  Agent Advisory Protocol rendering and exit codes without reimplementing them; no drift between two root command
  groups.
- One source of truth per setting: devkit's engines act on the same value the agent reads; no second configuration
  file; agents read effective policy (defaults applied) through a command, never by parsing TOML.
- Rule code is tested and versioned with the package that defines the document model; every rule loads the same
  document index, and a file is parsed once per run; the deployed rule file stays stable; devkit's engine instantiates
  only classes defined in the rule file.
- One name for the bundle, the commands and the skills; skill names say what the skill does; no skill name that reads
  as a stutter or is confused with the router.
- Installing the package never writes documentation a project did not ask for; a new project can still start from the
  arc42 and Living Spec structure in one command; seeded files belong to the project once written.

---

## 3. Considered Options

### Package shape
- **Python layer on devkit** (selected by `ADR-rebuild-spec-on-devkit`): ships the methodology as a devkit bundle and
  the SDD commands as a devkit command group; one pure wheel (`py3-none-any`); devkit's engines reused as they are; one
  output contract and error boundary. Cons: devkit-spec follows devkit's minor versions and breaking changes; behaviour
  that depended on the standalone CLI's commands is reshaped where devkit cannot call devkit-spec.
- **Keep the standalone Go CLI next to devkit** (rejected by `ADR-rebuild-spec-on-devkit`): no porting work, but every
  engine twice, two receipts, two hook systems, two output contracts; platform builds remain.
- **Move spec-driven development into devkit** (rejected by `ADR-rebuild-spec-on-devkit`): one package, but devkit stops
  being SDD-agnostic and every devkit consumer receives one methodology's rules and commands.
- **Port to Python as a standalone tool** (rejected by `ADR-rebuild-spec-on-devkit`): no dependency on devkit, but
  duplicates devkit as the Go CLI does, only in another language.

### Command entry
- **`devkit spec` through `devkit.commands`** (selected by `ADR-mount-under-the-devkit-command-line`): one executable;
  `devkit --help` lists `spec`; devkit's error boundary; an import failure fails only `devkit spec`
  (`COMMAND_PLUGIN_INVALID`). Cons: the plugin is visible only in the environment devkit-spec is installed in;
  `devkit --version` reports devkit only.
- **A separate `devkit-spec` console script** (rejected by `ADR-mount-under-the-devkit-command-line`): duplicates the
  root group, its options and its boundary; two executables; the groups drift.
- **`python -m devkit_spec`** (rejected by `ADR-mount-under-the-devkit-command-line`): not discoverable from
  `devkit --help`; a second invocation convention.

### Policy location
- **devkit's tables for what devkit models, `[tool.spec]` for the rest** (selected by
  `ADR-policy-in-the-tool-spec-table`): devkit's engines read their own settings; no duplicate keys. Cons: policy spans
  several tables, which is why the policy command exists.
- **Everything in `[tool.spec]`** (rejected by `ADR-policy-in-the-tool-spec-table`): two sources of truth; devkit's
  engines would not see the mirrored values.
- **A devkit-spec configuration file** (rejected by `ADR-policy-in-the-tool-spec-table`): a second file to find,
  validate and keep consistent.

### Rule code location
- **Logic in `devkit_spec.rules`, thin subclass files in the bundle** (selected by
  `ADR-rules-implemented-in-the-package`): rules are ordinary package modules covered by the package's tests and share
  `document_index(ctx)` and the other helpers. Cons: the deployed file imports `devkit_spec`, so the package must be
  installed wherever `devkit rules` runs.
- **Full rule code in the deployed rule files** (rejected by `ADR-rules-implemented-in-the-package`): the shared
  library is duplicated or loaded by path; code tested as copies; a change rewrites every managed file.
- **Built-in rules in devkit** (rejected by `ADR-rules-implemented-in-the-package`): puts the document model into devkit.

### Skill names
- **`spec`, `spec-*`, with `sr-spec` renamed `spec-specify`** (selected by `ADR-skills-named-spec`): names match the
  bundle and commands; stage skills match stage ids. Cons: users relearn the names.
- **Keep `sr`, `sr-*`** (rejected by `ADR-skills-named-spec`): a legacy prefix unrelated to the bundle and the commands.
- **Mechanical rename including `spec-spec`** (rejected by `ADR-skills-named-spec`): a stutter, easy to confuse with the
  `spec` router.

### Docs skeleton
- **A separate `docs-skeleton` preset** (selected by `ADR-docs-skeleton-is-opt-in`): no surprise files; one command for
  a new project. Cons: one more step for projects that want it.
- **The skeleton in the `core` preset** (rejected by `ADR-docs-skeleton-is-opt-in`): writes into existing `docs/` trees
  wherever a seeded file is absent.
- **No skeleton** (rejected by `ADR-docs-skeleton-is-opt-in`): new projects rebuild the directory structure, arc42
  chapters and glossary by hand.

---

## 4. Decision Outcome

- **Python layer on devkit**: devkit-spec is a Python package on devkit's public surface. It keeps only what is
  spec-driven: the document model (kinds, directories, ID grammar, frontmatter, references, namespaces), the
  methodology (routes, workflow definitions, stage skills, role contracts, templates, docs skeleton, reconciliation)
  and the policy that turns devkit's engines into SDD behaviour (which rules run, which checks gate a stage, how search
  scopes and pins documents, which routes run in a worktree). devkit stays SDD-agnostic and owns every generic engine.
  (ADR-rebuild-spec-on-devkit)
  Superseded in part by `ADR-document-package`: the document model and the document rules live in devkit-docs,
  which devkit-spec depends on.
- **Command mount**: devkit-spec ships its commands as the `devkit spec` group through
  `[project.entry-points."devkit.commands"] spec = "devkit_spec.cli:cli"`, with no console script; the commands inherit
  devkit's loading, output contract and error boundary. (ADR-mount-under-the-devkit-command-line)
- **Version**: `devkit spec --version` prints `[VERSION: devkit-spec <version>]`; `devkit --version` reports devkit
  only. (ADR-mount-under-the-devkit-command-line)
- **Policy**: approvals, stage switches and worktree integration stay in devkit's tables (`[workflow.approvals]`,
  `[workflow.stages]`, `[worktree]`); `[tool.spec]` holds `worktree`, `[[tool.spec.namespaces]]` and
  `[tool.spec.scope]`; `devkit spec policy` prints the effective values of both. Mapping: approvals to
  `[workflow.approvals]` (`ADR-delivery-decision-boundaries`), the feedback sweep to `[workflow.stages]`
  (`collect-feedback`), `pull_request` and branch cleanup to `[worktree]`, `git.worktree` to `[tool.spec] worktree`.
  (ADR-policy-in-the-tool-spec-table)
  Superseded in part by `ADR-document-package`: namespaces are `[[tool.docs.namespaces]]`, owned by devkit-docs.
- **Rules**: the spec rules are implemented and tested in the package; each `bundle/rules/<name>/rule.py` imports the
  package's rule class and subclasses it, with the guide `guide.md` beside it. Rules read files only through
  `ctx.cache` so snapshot runs and rechecks see the right tree. (ADR-rules-implemented-in-the-package)
- **Skill names**: the bundle's skills are named `spec` and `spec-<x>` after the bundle and command group; the
  specify-stage skill is `spec-specify`, not `spec-spec`. The workflow `skills:` lists and the role contracts' `skill`
  fields use these names. (ADR-skills-named-spec)
- **Docs skeleton**: the seeded `docs/` skeleton (Living Spec directories, arc42 chapters, glossary and search synonyms)
  ships in its own preset, `[presets.docs-skeleton] assets = ["docs-skeleton"]`, added with
  `devkit add spec:docs-skeleton`, so installing devkit-spec never writes files into an existing `docs/` tree.
  (ADR-docs-skeleton-is-opt-in)
- **Generic first**: a generic capability devkit-spec needs is added to devkit first. (ADR-rebuild-spec-on-devkit)

---

## 5. Consequences

- **Positive**:
  - One wheel and one executable; devkit's targeting and snapshot runs apply to the spec rules; a generic improvement
    made in devkit benefits devkit-spec at once. (ADR-rebuild-spec-on-devkit)
  - Every command keeps devkit's output contract (`ARCH-08-cross-cutting`); `devkit spec` is imported only when it
    runs, so built-in commands never pay for it. (ADR-mount-under-the-devkit-command-line)
  - `[GATE_POLICY ...]`, `[STAGE_POLICY ...]` and `[GIT_POLICY ...]` lines reflect exactly what devkit's engines use,
    with `source=config|default`. (ADR-policy-in-the-tool-spec-table)
  - The rule implementation and its tests change together; the managed copy is a stable one-liner and the guide is the
    only rule text a project reads. (ADR-rules-implemented-in-the-package)
  - The skeleton is written once where absent and never updated by later syncs; `glossary.yaml` lives at
    `docs/glossary.yaml`, the synonym list of `devkit spec search`. (ADR-docs-skeleton-is-opt-in)
- **Negative / Risks**:
  - devkit is pinned to a minor range (`devkit>=0.1,<0.2`) and devkit-spec moves with it; devkit's `workflow next` and
    `worktree finish` cannot call devkit-spec, so the skills run the scope commands
    (`ADR-worktrees-branches-and-scope`); some earlier features were dropped (derived-data cache, web viewer,
    per-kind listing filters). (ADR-rebuild-spec-on-devkit)
  - The plugin is visible only in the environment devkit-spec is installed in; the `spec` name is reserved for this
    plugin by convention; a broken install surfaces as `COMMAND_PLUGIN_INVALID` on `devkit spec` only.
    (ADR-mount-under-the-devkit-command-line)
  - A malformed `[tool.spec]` is `SPEC_CONFIG_INVALID`; in a rule run it fails the run (devkit's
    `RULES_EXECUTION_FAILED`, exit `2`) instead of being a violation. (ADR-policy-in-the-tool-spec-table)
    Superseded in part by `ADR-document-package`: rule runs read only `[tool.docs]`; a malformed `[tool.spec]` is
    reported by the commands that read it.
  - A project, its commit gate and its CI must install devkit-spec in the environment that runs `devkit rules check`
    (`ARCH-07-deployment`). (ADR-rules-implemented-in-the-package)
  - Users relearn the skill names. (ADR-skills-named-spec)
  - Improvements to the seed reach existing projects only when they copy them by hand. (ADR-docs-skeleton-is-opt-in)
- **Follow-ups**: this repository selects the preset (`spec = ["core", "docs-skeleton"]`) and has replaced the seeded
  content with its own Living Spec. (ADR-docs-skeleton-is-opt-in)

---

## 6. Confirmation

- `packages/devkit-spec/tests/e2e/package/test_package.py`: the entry points are installed, `spec` is not a built-in
  devkit command and `devkit` mounts the `spec` group, `devkit sync` deploys the default preset and its rules run,
  `devkit config template` writes the spec tables, and the docs skeleton is opt-in and passes the rules.
- `packages/devkit-spec/tests/integration/features/policy/test_cli_policy.py`: `devkit spec policy` reports the
  effective policy.
- The rule folders under `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/*/tests/` test each rule
  against the package's implementation.
