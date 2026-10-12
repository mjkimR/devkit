---
name: consumption
description: Read before using, changing or troubleshooting devkit-managed assets in a repository. Covers loading bundle context, reading instructions on demand, invoking playbooks, running rules and gates, overrides, selection in .devkit/config.toml and the sync and receipt lifecycle.
---

# Consuming devkit-managed assets

## What devkit owns in the workspace

| Path | Tracked in Git | Role |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Selected bundles and presets, target agents, `guidance_block`, `override_drift`, `[playbooks]`, `[rules]`, `[workflow]` and `[gates]` settings; `[tool.<name>]` tables belong to other tools and are passed through unread |
| `.devkit/installation.json` | yes | Receipt: packages, bundle versions, deployed paths, SHA-256 and mode of every file |
| `.devkit/overrides/<bundle>/` | yes | Project-owned replacements for upstream asset files (with upstream baseline copies under `.devkit/overrides/.baseline/`) |
| `.devkit/managed/<bundle>/` | no | Pristine copies extracted from installed bundles |
| `.devkit/transient/` | no | The project lock (`lock`) and the write-ahead journal of an interrupted sync |
| `.claude/`, `.agents/`, `.codex/` projections | usually no | Native copies of skills and subagents for each selected agent |
| `AGENTS.md` (root) | yes | Project-owned; only the `<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->` block in it is managed |
| Seeded files (paths listed under `seeded` in the receipt) | yes | Project-owned; written once by a bundle's seeded `document` asset, never updated or removed by sync |

Generated paths are rebuilt by `uv run devkit sync` from the installed packages
and the configuration. Edit sources and configuration, never generated copies.
`sync` halts when a managed file that is still selected was modified, or when an
unmanaged file sits where it needs to write; it never deletes foreign files. A
modified file that is no longer selected is left in place and reported as an
`ORPHAN_LEFT` notice (`[NOTICE: (ORPHAN_LEFT) left modified file in place:
<path> ...]` on stderr); ask the user before removing it. Notices never fail a
sync; `[WARNING: (CODE) ...]` lines (override drift, stray files under
`.devkit/managed/`) deserve a look.

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
`devkit-workflow` entry skill. It runs `devkit workflow next` to compute the
current stage of a work unit; stage skills named by the definition perform the
work. Follow the entry skill rather than inferring the stage yourself.

## Rules and commit gates

Synchronized rules are plain Python files listed in the receipt. They load
automatically:

```bash
uv run devkit rules check                     # working tree, linter phase
uv run devkit rules check --staged            # exactly what a commit would contain
uv run devkit rules check --ci --base origin/main
uv run devkit rules fix --dry-run
uv run devkit rules explain <RULE-id>
```

Configure a rule's severity, phase or settings in `[rules]` of
`.devkit/config.toml`; the managed rule file is hash-checked and must not be
edited. Gates work the same way through `devkit gate` and `[gates]`.

Snapshot gates (`--staged`, `--ci`) evaluate the Git tree and trust the
committed receipt. A managed rule that is missing or differs from the receipt's
hash fails the gate; its `[FIX]` says to run `devkit sync` and commit the receipt.

## Changing what is deployed

```bash
uv run devkit add <bundle>            # select with the bundle's default preset, then sync
uv run devkit add <bundle>:<preset>   # select a specific preset
uv run devkit remove <bundle>         # deselect (a built-in bundle is recorded as false), then sync
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
uv run devkit override create <bundle>:<asset>   # copy the asset's files into .devkit/overrides/, then sync
uv run devkit override list                      # tracked overrides and their drift status
uv run devkit override diff <bundle>:<asset>     # per file: what upstream changed, what the override changed
uv run devkit override accept <bundle>:<asset>   # record the current upstream as the baseline after merging
uv run devkit override remove <bundle>:<asset>   # back to the pristine upstream files
```

`create` copies every file of the asset (all files of a skill directory). Edit
the copies you need; each override file is used in place of its upstream file
in projections, `get-context` and playbook search, and files you leave unchanged
still follow upstream only through `accept`. Drift is reported when any upstream
file of the asset changes. Only assets of selected bundles can be overridden,
and seeded files are edited in place instead. For assets the repository owns
itself, edit the source bundle instead (see the `in-repo-bundle` instruction).

## Checking the installed state

`uv run devkit status` prints, without changing anything, how the workspace
compares with the receipt: managed files that are missing, modified or have a
different execute bit, overrides whose upstream changed, the guidance block state, seeded
files that no longer exist, a pending journal, and whether the `devkit`
version that wrote the receipt is the one running. Whatever needs acting on (a
missing, modified or mode-mismatched file, a pending journal, or override drift)
is listed under `errors` and rendered as an advisory block on stderr; follow its
`[ACTION]` and `[FIX]`. It exits 1 when there is any and 0 otherwise. Use `uv run devkit sync
--check` to learn whether a sync is needed (exit 1; exit 2 means an error such
as a hand-edited managed file, reported as an advisory with its code on stderr
and as `{"error": ...}` on stdout); use `status` to learn why. Every command takes
`-w <dir>` for a project other than the one containing the current directory.

## Recovering an interrupted sync

If a devkit command reports `TRANSACTION_PENDING`, run `uv run devkit
recover`. It rolls the files named in the journal under `.devkit/transient/`
back to their state before the interrupted run and refuses (`RECOVERY_BLOCKED`)
if one of them was edited since; then run `devkit sync` again. `LOCK_HELD`
means another devkit command is running: wait for it, do not delete the lock.

## Commit discipline

Commit `.devkit/config.toml`, `.devkit/installation.json`,
`.devkit/overrides/`, the root `AGENTS.md` and newly seeded files with the change
that required them. Keep
`.devkit/managed/`, `.devkit/transient/` and the native projections ignored
according to the repository's own `.gitignore`; devkit never edits `.gitignore`
or the Git index.
