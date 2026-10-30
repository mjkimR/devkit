# Bundle Recommendations

How to choose opt-in bundles after the base installation. Entry point: [Installation Guide](../INSTALL_GUIDE.md).

A bundle is a set of assets; a preset selects part of it. `devkit` and `advisory` (and `harness` with `devkit-agt`,
`docs` with `devkit-docs`, `docs` and `spec` with `devkit-spec`) are deployed automatically; every other bundle deploys nothing until `uv run devkit add <bundle>[:<preset>]` selects
it. Recommend a bundle only on evidence from the repository or the user's answers, and select only what the user
approves.

## 1. See what is available

```bash
uv run devkit list
```

`devkit list` prints every installed bundle with its presets, default preset and selection state. Bundles from
`devkit-catalog` appear only once that package is installed (see
[Installation Guide, step 3](../INSTALL_GUIDE.md#step-3-package-sources)); install it only when a bundle you
recommend comes from it.

## 2. Match the repository

| Bundle (package) | Recommend when | Preset |
| --- | --- | --- |
| `docs` (`devkit-docs`) | The user wants document formats and validation without mandatory SDD. | Auto-selected `core`: writing instructions, document rules, shared templates and steering context. Optional `docs:docs-skeleton` seeds absent files. Install devkit-docs instead of devkit-agt. |
| `spec` (`devkit-spec`) | The user wants spec-driven delivery (specs with acceptance criteria, planned and reviewed changes, a Living Spec under `docs/`), or the repository already requires SDD feature delivery. | Not selected with `devkit add`: declare `devkit-spec` instead of `devkit-agt` ([Installation Guide, step 3](../INSTALL_GUIDE.md#step-3-package-sources)) and sync; default `core` deploys the `/spec` entry skill and its stage skills, the spec delivery workflows with the generated `devkit-workflow` skill, lifecycle rules and subagents; docs:core supplies shared writing instructions and document rules. `docs-skeleton` (`uv run devkit add docs:docs-skeleton`) seeds absent `docs/` files. |
| `harness:run` (built in, `devkit-agt`) | The repository has tests, linters or type checks that agents run. | Adds one `AGENTS.md` line sending agents to `devkit run` for bounded command output. |
| `git-commits` (built in) | `git log --format=%s -n 50` shows mostly `type(scope): subject`, or the user wants Conventional Commits. | Default `core`: the convention and an `AGENTS.md` pointer to it. |
| `authoring` (built in, `devkit-agt`) | The repository contains agent skills (`SKILL.md`) or playbooks. | `skill-authoring`: the `agent-asset-writing` instruction, the restructuring playbook, the size rule and the wording rule. |
| `authoring` (built in, `devkit-agt`) | The root `AGENTS.md` or `CLAUDE.md` is long or grows often. | `agent-guide-authoring` |
| `authoring` (built in, `devkit-agt`) | Both of the above. | Default `all` |
| `advisory:python` (built in) | The project depends on `devkit-advisory` at runtime, or builds Python CLIs that agents consume. | Adds the Python library guide and `RULE-advisory-unique-code` (run by `devkit-agt`). |
| `cli-tool` (`devkit-catalog`) | The repository builds, or the user plans, a Python command-line tool that agents run. | Default `all`: the `cli-tool-structure` instruction (click, `devkit-cli`, the required feature layout, import budget) and five structure rules run by `devkit-agt`; `guide`: the instruction only (the preset to take with `devkit-dist` alone). |
| `adaptive-dev` (`devkit-catalog`) | The user wants to discover and build an idea without per-change SDD records, with resumable current product context. | Explicit `core`: `/adaptive-dev`, three optional support roles and current-context template. Install devkit-docs plus devkit-catalog, choose shared adaptive-development policy, then `uv run devkit add adaptive-dev`. No devkit-spec dependency. |
| `deep-research` (`devkit-catalog`) | The user asks for an explicit research entry. Repository evidence alone never recommends it. | Explicit `core`: a user-invoked research entry, four optional research roles and one indexed material per investigation under `docs/materials/`. Install devkit-docs plus devkit-catalog, then `uv run devkit add deep-research`; it works under either development approach and needs no devkit-spec. |
| `response-style` (`devkit-catalog`) | The user wants answer-first replies that keep decision-critical facts, or a configurable default conversation language. | Default `all`: the `response-style` skill and an `AGENTS.md` line; `[presentation] language = "ko"` supplies an inherited Korean default; an explicit `[bundles.response-style.variables] language` value wins. Run sync after edits. |
| `maintenance` (`devkit-catalog`) | The user wants bounded drift review, evidence-based weekly reports with separately authorized publication, review and refactoring passes that reduce accumulated code, guidance and CLI surface, or measured performance passes over slow commands. | `upkeep`: drift-reconciliation and review-refactor; `reporting`: weekly-report; `refactoring`: review-refactor alone; `performance`: performance-pass with review-refactor; default `all`: the four playbooks. Selection never executes them; unavailable evidence remains explicit gaps. |

With `devkit-dist` alone, recommend no `devkit-agt` bundle, no `spec` and no rule asset (`advisory:python`, `cli-tool` other than
`cli-tool:guide`): nothing runs them.
Do not recommend a bundle without evidence for it. When a signal is weak (for example a few Conventional Commits
among many free-form messages), mention it as optional.

## 3. Present and select

Show the recommendations as a short table: bundle and preset, evidence, what it adds. Then, for the approved ones:

```bash
uv run devkit add <bundle>[:<preset>] ...     # one command may name several bundles
uv run devkit add --dry-run <bundle>          # preview the files first when unsure
```

- `devkit add` merges presets into what a bundle already deploys. To replace a bundle's presets instead, use
  `uv run devkit sync --preset <bundle>:<preset>`.
- Selections are recorded by preset name in `.devkit/config.toml`, so later upstream changes to a default preset
  never change them.
- New skills and playbooks create native projections: update the root `.gitignore` as described in
  [New Repository, section 4](new-repository.md#4-ignore-the-native-projections).
- Removing later: `uv run devkit remove <bundle>`.

## 4. Beyond the listed bundles

- **Project-specific assets**: when the analysis shows conventions that recur but no bundle covers (a release
  procedure, a domain rule), do not write them during installation. Tell the user devkit can ship them as an
  in-repository bundle and point to the `in-repo-bundle` instruction: `uv run devkit get-context devkit`.
- **Changing a deployed asset**: `uv run devkit override create <bundle>:<asset>` copies it to
  `.devkit/overrides/` for editing.


### Adaptive development policy

For development without SDD lifecycle records, install the document system and choose shared policy explicitly:

```toml
[development]
approach = "adaptive-dev"

[integration]
provider = "project"
```

Inspect `uv run devkit config show`; the absent approach defaults to `sdd`. Local/environment overrides are not
supported. Document checks and the project's run/build/lint/test commands remain active. Package or bundle selection
does not activate either approach. Installed spec extensions reject new SDD lifecycle records in adaptive development while
retaining existing SDD artifact checks. Independent project integration uses explicit passing review/tests/lint
claims and the ordinary approval/route/cleanup checks. Select `adaptive-dev:core` from devkit-catalog for `/adaptive-dev`;
all three support roles are optional. The coordinator maintains project-owned
`.devkit/adaptive-dev.md`; sync and re-selection preserve it. Baseline adoption is a separate explicit procedure;
installing assets or changing this setting does not establish a verified SDD baseline.
