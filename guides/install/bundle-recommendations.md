# Bundle Recommendations

How to choose opt-in bundles after the base installation. Entry point: [Installation Guide](../INSTALL_GUIDE.md).

A bundle is a set of assets; a preset selects part of it. `devkit` and `advisory` (and `harness` with `devkit-agt`)
are deployed automatically; every other bundle deploys nothing until `uv run devkit add <bundle>[:<preset>]` selects
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
| `harness:run` (built in, `devkit-agt`) | The repository has tests, linters or type checks that agents run. | Adds one `AGENTS.md` line sending agents to `devkit run` for bounded command output. |
| `git-commits` (built in) | `git log --format=%s -n 50` shows mostly `type(scope): subject`, or the user wants Conventional Commits. | Default `core`: the convention and an `AGENTS.md` pointer to it. |
| `authoring` (built in, `devkit-agt`) | The repository contains agent skills (`SKILL.md`) or playbooks. | `skill-authoring`: the `agent-asset-writing` instruction, the restructuring playbook, the size rule and the wording rule. |
| `authoring` (built in, `devkit-agt`) | The root `AGENTS.md` or `CLAUDE.md` is long or grows often. | `agent-guide-authoring` |
| `authoring` (built in, `devkit-agt`) | Both of the above. | Default `all` |
| `advisory:python` (built in) | The project depends on `devkit-advisory` at runtime, or builds Python CLIs that agents consume. | Adds the Python library guide and `RULE-advisory-unique-code` (run by `devkit-agt`). |
| `cli-tool` (`devkit-catalog`) | The repository builds, or the user plans, a Python command-line tool that agents run. | Default `all`: the `cli-tool-structure` instruction (click, `devkit-cli`, the required feature layout, import budget) and five structure rules run by `devkit-agt`; `guide`: the instruction only (the preset to take with `devkit-dist` alone). |
| `response-style` (`devkit-catalog`) | The user wants answer-first replies that keep decision-critical facts, or a configurable default conversation language. | Default `all`: the `response-style` skill and an `AGENTS.md` line; `[presentation] language = "ko"` supplies an inherited Korean default; an explicit `[bundles.response-style.variables] language` value wins. Run sync after edits. |
| `maintenance` (`devkit-catalog`) | The user wants bounded drift review or evidence-based weekly reports with separately authorized publication. | `upkeep`: drift-reconciliation; `reporting`: weekly-report; default `all`: both independent playbooks. Selection never executes them; unavailable evidence remains explicit gaps. |

With `devkit-dist` alone, recommend no `devkit-agt` bundle and no rule asset (`advisory:python`, `cli-tool` other than
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
