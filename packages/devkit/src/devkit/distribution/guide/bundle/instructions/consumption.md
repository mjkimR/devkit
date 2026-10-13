---
name: consumption
description: Read before using, changing or troubleshooting devkit-managed assets in a repository. Covers loading bundle context, reading instructions on demand, invoking playbooks, running rules and gates, overrides, selection in .devkit/config.toml and the sync and receipt lifecycle.
---

# Consuming devkit-managed assets

## What devkit owns in the workspace

| Path | In Git | Role |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Selected bundles and presets, target agents, `guidance_block`, `override_drift`, `[playbooks]`, `[rules]`, `[workflow]`, `[gates]`; `[tool.<name>]` tables belong to other tools and are passed through unread |
| `.devkit/installation.json` | yes | Receipt: packages, bundle versions, deployed paths, SHA-256 and mode of every file |
| `.devkit/overrides/<bundle>/` | yes | Project-owned replacements for upstream asset files (baseline copies under `.devkit/overrides/.baseline/`) |
| `.devkit/.gitignore` | yes | Ignores `managed/` and `transient/`; seeded by sync when absent, then project-owned |
| `.devkit/managed/<bundle>/` | no | Pristine copies extracted from installed bundles |
| `.devkit/transient/` | no | The project lock and the journal of an interrupted sync |
| `.claude/`, `.agents/`, `.codex/` projections | usually no | Native copies of skills and subagents for each selected agent |
| `AGENTS.md` (root) | yes | Project-owned; only the `<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->` block is managed |
| Seeded files (`seeded` in the receipt) | yes | Project-owned; written once by a bundle, never updated or removed by sync |

`uv run devkit sync` rebuilds the generated paths from the installed packages
and the configuration; edit sources and configuration, never generated copies.
`sync` halts when a managed file that is still selected was modified, or when an
unmanaged file with other content sits where it must write, naming every such
file in one `SYNC_CONFLICT`; an unmanaged file identical to what it would write
is adopted as it is. A file left as this clone's last sync wrote it is not a
modification: after a pull that moves the committed receipt, `sync` updates it.
It never deletes foreign files. A modified file that is no
longer selected is left in place and reported as an `ORPHAN_LEFT` warning; ask
the user before removing it. Warnings (`[WARN]`
blocks on stderr: orphans, override drift, stray files under `.devkit/managed/`)
and notices (`[NOTICE]`) never fail a sync, but tell the user about warnings.

The root `AGENTS.md` block is the orientation every session reads: installed
bundles, the once-per-bundle `get-context` rule, the generated entry skills and
the bundles' guidance lines. It is regenerated from the selection and
hash-guarded like a managed file: write project guidance outside the markers.
`guidance_block = false` in `.devkit/config.toml` turns it off; a block edited
by hand is then left in place with an `ORPHAN_LEFT` warning.

Seeded files are scaffolding a bundle wrote on first sync (a docs tree, a
glossary, a policy file). Edit them freely: sync never compares, updates or
removes them, and deselecting the bundle keeps them. One deleted while its
asset is still selected is seeded again by the next sync.

## Loading bundle context

Run `uv run devkit get-context <bundle>` once per bundle in the current agent
context, before using that bundle's skills, playbooks or workflows. It returns
`constitution` (the bundle's `AGENTS.md`, when it ships one) and `instructions`
(each synchronized instruction's YAML `header` and absolute `path`; bodies are
never returned). Read a body only when its description matches the current
work. Do not re-run the command per skill or turn; reload only when the context
is gone. Skills deployed by devkit open with this prerequisite, so following a
skill satisfies it.

`uv run devkit list` prints installed bundles, their presets, selection state
and deployed paths without loading any context.

## Playbooks

Playbooks hold procedures for occasional tasks; they are not part of the
context and not searched during ordinary work. Use one only when the user
invokes the `devkit-playbook` skill for the current task, or when a rule
violation's remediation points to it. The skill runs
`uv run devkit playbook search "<English query>"`, which returns headers and
paths; read the chosen procedure from its path, loading its bundle's context
first if needed.

## Workflows

When a bundle ships a workflow definition, `devkit sync` generates the
`devkit-workflow` entry skill. It runs `devkit workflow next` to compute the
current stage of a work unit; the stage skills the definition names do the
work. Follow the entry skill rather than inferring the stage yourself.

## Rules and commit gates

Synchronized rules are plugin packages whose files the receipt lists, and they
load automatically:

```bash
uv run devkit rules check                     # working tree, linter phase
uv run devkit rules check --staged            # exactly what a commit would contain
uv run devkit rules check --ci --base origin/main
uv run devkit rules fix --dry-run
uv run devkit rules explain <RULE-id>
uv run devkit rules test [<RULE-id>]            # the tests in each rule's folder (needs pytest)
```

Configure a rule's severity, phase or settings in `[rules]` of
`.devkit/config.toml`; the managed rule files are hash-checked. Gates work the
same way through `devkit gate` and `[gates]`; per-clone gate settings go in
`.git/devkit.config`, which lists every installed gate as a commented table
(uncomment a table's header and only the keys you change: an uncommented key replaces
its `.devkit/config.toml` value; devkit only appends tables for new gates). Snapshot gates (`--staged`,
`--ci`) evaluate the Git tree and trust the committed receipt: a managed rule
that is missing or differs from the receipt's hash fails the gate, and its
`[FIX]` says to run `devkit sync` and commit the receipt.

## Changing what is deployed

```bash
uv run devkit add <bundle>            # select with the bundle's default preset, then sync
uv run devkit add <bundle>:<preset>   # add a preset to those the bundle already deploys
uv run devkit remove <bundle>         # deselect (an auto-selected bundle is recorded as false), then sync
uv run devkit sync --locked           # fresh clone, CI: restore ignored copies, never change committed files
uv run devkit sync --preset <bundle>:<preset>   # replace a bundle's presets
uv run devkit sync                    # converge to .devkit/config.toml
uv run devkit sync --no-save --agent claude-code --agent codex   # narrow projections for one run only
```

Without `agents` in `.devkit/config.toml`, every supported agent gets
projections. A bundle must be installed (`uv add --dev <package>`) before it
can be selected. A bundle that declares `auto_select` is deployed with its
default preset as soon as its package is installed, without an entry;
`BUNDLE_AUTO_SELECTED` names it when it is first deployed, so tell the user,
and opt it out with `devkit remove <bundle>` only when they ask. Removal is
explicit: a deployed bundle whose package is not installed is a sync error
(`SELECTION_INVALID`), auto-selected or not, so a partial environment never
deletes committed files. Run `uv sync` when the package belongs in the
environment; run `devkit remove <bundle>` when the user removed the package.

`uv run devkit config template` writes every key `.devkit/config.toml` accepts
as a comment at its default: devkit's own keys and the `[tool.<name>]` tables
of installed tools. Read those comments to learn what a setting does and what
applies while it is unset; uncomment a key to change it. The command only adds
what the file lacks and never changes a line.

`devkit sync --locked` rebuilds only what the committed receipt records
(Git-ignored managed copies) and never writes the receipt, the `AGENTS.md`
block or seeded files. When those would change it writes nothing and fails
with `RECEIPT_STALE` (exit 1, `INTERACTION`): a bundle source, the lock or the
selection changed without its receipt. Ask the user before running a plain
`devkit sync` and committing what it changes.

## Customizing an upstream asset

```bash
uv run devkit override create <bundle>:<asset>   # copy the asset's files into .devkit/overrides/, then sync
uv run devkit override list                      # tracked overrides and their drift status
uv run devkit override diff <bundle>:<asset>     # per file: what upstream changed, what the override changed
uv run devkit override accept <bundle>:<asset>   # record the current upstream as the baseline after merging
uv run devkit override remove <bundle>:<asset>   # back to the pristine upstream files
```

`create` copies every file of the asset (all files of a skill directory). Each
override file replaces its upstream file in projections, `get-context` and
playbook search; unchanged copies still follow upstream only through `accept`.
Drift is reported when any upstream file of the asset changes; `create --force`
replaces the override with the current upstream and makes that the baseline.
An asset that is deselected keeps its tracked override while the override files
remain, so drift is still reported once it is selected again. Only assets of
selected bundles can be overridden; seeded files are edited in place, and the
repository's own assets in their source bundle (see `in-repo-bundle`).

## Checking the installed state

`uv run devkit status` reports, without changing anything, how the workspace
compares with the receipt: missing, modified, execute-bit-changed or symlinked
managed files, override drift of deployed assets, the guidance block state, seeded files that no longer
exist, a selected bundle whose package is missing or broken, a pending journal, and whether the running `devkit` version wrote the
receipt. Whatever needs acting on is listed under `errors`, each with its
`advisory` (`action`, `fix`); follow them. It exits 1 when there is any, else 0.
`uv run devkit sync --check` says whether a sync is needed (exit 1, one
`[CHANGE: ...]` line per pending write); exit 2 means an error, such as a
hand-edited managed file, reported as an advisory block on stderr. `sync`,
`add` and `remove` print `[SYNC]`/`[CHANGE]` lines (`--format json` for the
whole result); the other commands print one JSON object that carries their
advisories, with nothing on stderr. Every command takes `-w <dir>` for a
project other than the current directory's.

## Recovering an interrupted sync

`TRANSACTION_PENDING`: run `uv run devkit recover`. It restores the files named
in the journal under `.devkit/transient/` to their state before the interrupted
run, refusing (`RECOVERY_BLOCKED`) if one was edited since; then run
`devkit sync` again. `LOCK_HELD`: another devkit command is running; wait for
it and never delete the lock.

## Commit discipline

Commit `.devkit/config.toml`, `.devkit/installation.json`, `.devkit/overrides/`,
`.devkit/.gitignore`, the root `AGENTS.md` and newly seeded files with the
change that required them. `.devkit/.gitignore` (seeded by sync when absent,
then project-owned) keeps `.devkit/managed/` and `.devkit/transient/` out of
Git. Keep the native projections ignored according to the repository's
`.gitignore`; devkit never edits it or the Git index.
