---
name: consumption
description: Read before using, changing or troubleshooting devkit-managed assets in a repository. Covers loading bundle context, reading instructions on demand, invoking playbooks, running rules and gates, overrides, selection in .devkit/config.toml and the sync and receipt lifecycle.
---

# Consuming devkit-managed assets

## What devkit owns in the workspace

| Path | Tracked in Git | Role |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Selected bundles and presets, target agents, `[rules]`, `[gates]`, `[playbooks]` settings; `[tool.<name>]` tables belong to other tools and are passed through unread |
| `.devkit/installation.json` | yes | Receipt: packages, bundle versions, deployed paths, SHA-256 and mode of every file |
| `.devkit/overrides/<bundle>/` | yes | Project-owned replacements for single upstream asset files |
| `.devkit/managed/<bundle>/` | no | Pristine copies extracted from installed bundles |
| `.devkit/transient/` | no | Lock and write-ahead journal for an interrupted sync |
| `.claude/`, `.agents/`, `.codex/` projections | usually no | Native copies of skills and subagents for each selected agent |
| `AGENTS.md` (root) | yes | Project-owned; only the `<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->` block in it is managed |
| Seeded files (paths listed under `seeded` in the receipt) | yes | Project-owned; written once by a bundle's seeded `document` asset, never updated or removed by sync |

Generated paths are rebuilt by `uv run devkit sync` from the installed packages
and the configuration. Edit sources and configuration, never generated copies.
`sync` halts when a managed file that is still selected was modified, or when an
unmanaged file sits where it needs to write; it never deletes foreign files. A
modified file that is no longer selected is left in place and reported as
`NOTICE: left modified file in place: <path>`; remove it yourself.

The block in the root `AGENTS.md` is the orientation index every session reads:
installed bundles, the once-per-bundle `get-context` rule and the generated entry
skills. It is regenerated from the selection and hash-guarded like a managed
file, so do not edit between the markers; write project guidance outside them.
`guidance_block = false` in `.devkit/config.toml` turns the block off.

Seeded files are scaffolding a bundle left behind on first sync (a docs tree,
a glossary, a policy file). Edit them freely: sync never compares, updates or
removes them, an upstream change to the bundle does not reach them, and
deselecting the bundle keeps them. If one is deleted while its asset is still
selected, the next sync seeds it again from the bundle.

## Loading bundle context

Run `uv run devkit get-context <bundle>` once per bundle in the current agent
context, before using that bundle's skills, playbooks or workflows. The response
contains:

- `constitution`: the bundle's `AGENTS.md`, when the bundle ships one.
- `instructions`: one entry per synchronized instruction with its YAML `header`
  (name and description) and absolute `path`. Bodies are never returned.

Together these form the bundle's context. Read an instruction body from its
path only when its description matches the current work. Do not re-run the
command for each skill or turn; reload only when the context is no longer
available. Skills deployed by devkit carry this prerequisite at the top of their
body, so following a skill already satisfies it.

`uv run devkit list` prints installed bundles, their presets, selection state
and deployed asset paths without loading any context.

## Playbooks

Playbooks hold procedures for occasional tasks. They are not part of the
default context and are not searched during ordinary work. Use them only when
the user explicitly invokes the `devkit-playbook` skill for the current task,
or when a rule violation's remediation points to one. The skill runs
`uv run devkit playbook search "<English query>"`, which returns candidate
headers and paths; read the selected procedure from its path and load its
bundle's context first if it is not already available.

## Workflows

When a bundle ships a workflow definition, `devkit sync` generates the
`devkit-workflow` entry skill. It runs `agent-workflow next` to compute the
current stage of a work unit; stage skills named by the definition perform the
work. Follow the entry skill rather than inferring the stage yourself.

## Rules and commit gates

Synchronized rules are plain Python files listed in the receipt. They load
automatically:

```bash
uv run agent-rules check                     # working tree, linter phase
uv run agent-rules check --staged            # exactly what a commit would contain
uv run agent-rules check --ci --base origin/main
uv run agent-rules fix --dry-run
uv run agent-rules explain <RULE-id>
```

Configure a rule's severity, phase or settings in `[rules]` of
`.devkit/config.toml`; the managed rule file is hash-checked and must not be
edited. Gates work the same way through `commit-gate` and `[gates]`.

Snapshot gates (`--staged`, `--ci`) evaluate the Git tree and trust the
committed receipt. A managed rule that is missing or differs from the receipt's
hash fails the gate with a message to run `devkit sync` and commit the receipt.

## Changing what is deployed

```bash
uv run devkit add <bundle>            # select with the bundle's default preset, then sync
uv run devkit add <bundle>:<preset>   # select a specific preset
uv run devkit remove <bundle>         # deselect, then sync
uv run devkit sync                    # converge to .devkit/config.toml
uv run devkit sync --no-save --agent claude-code --agent codex   # narrow projections for one run only
```

Omitting `agents` in `.devkit/config.toml` projects to every supported agent.
A bundle must be installed as a dev dependency before it can be selected:
`uv add --dev <package>`. Deselect before uninstalling; a selected bundle that
is no longer installed is a sync error.

## Customizing an upstream asset

To change the content of a file that an upstream bundle ships:

```bash
uv run devkit override create <bundle>:<asset>   # copy into .devkit/overrides/, record baseline
uv run devkit override list                      # overrides and their drift status
uv run devkit override diff <bundle>:<asset>     # baseline vs new upstream vs override
uv run devkit override accept <bundle>:<asset>   # advance the baseline after reviewing upstream changes
uv run devkit override remove <bundle>:<asset>   # back to the pristine upstream file
```

An override replaces one asset file and is projected in place of the managed
copy. For assets the repository owns itself, edit the source bundle instead
(see the `in-repo-bundle` instruction).

## Checking the installed state

`uv run devkit status` prints, without writing anything, how the workspace
compares with the receipt: managed files that are missing, modified or have a
wrong mode, overrides whose upstream changed, the guidance block state, seeded
files that no longer exist, a pending journal, and whether the `devkit`
version that wrote the receipt is the one running. Use `uv run devkit sync
--check` to learn whether a sync is needed; use `status` to learn why.

## Recovering an interrupted sync

If `devkit sync` or `devkit get-context` reports a pending transaction, run
`uv run devkit recover`. It rolls the files named in the journal under
`.devkit/transient/` back to their state before the interrupted run and refuses
if one of them was edited since; then run `devkit sync` again.

## Commit discipline

Commit `.devkit/config.toml`, `.devkit/installation.json` and
`.devkit/overrides/` with the change that required them. Keep
`.devkit/managed/`, `.devkit/transient/` and the native projections ignored
according to the repository's own `.gitignore`; devkit never edits `.gitignore`
or the Git index.
