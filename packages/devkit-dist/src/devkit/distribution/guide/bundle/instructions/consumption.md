---
name: consumption
description: Read before using, changing or troubleshooting devkit-managed assets, including selection, overrides, sync, the receipt, status and recovery.
---

# Consuming devkit-managed assets

## What devkit owns in the workspace

| Path | In Git | Role |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Selected bundles and presets, target agents, `guidance_block`, `override_drift`, `[playbooks]`; tables reserved for `devkit-agt` engines and `[tool.<name>]` tables are passed through unread |
| `.devkit/installation.json` | yes | Receipt: packages, bundle versions, deployed paths, SHA-256 and mode of every file |
| `.devkit/overrides/<bundle>/` | yes | Project-owned replacements for upstream asset files (baselines under `.devkit/overrides/.baseline/`) |
| `.devkit/.gitignore` | yes | Ignores `managed/` and `transient/`; seeded by sync when absent, then project-owned |
| `.devkit/managed/<bundle>/` | no | Pristine copies extracted from installed bundles |
| `.devkit/transient/` | no | The project lock and the journal of an interrupted sync |
| `.claude/`, `.agents/`, `.codex/` projections | usually no | Native copies of skills and subagents for each selected agent |
| `.codex/hooks.json` | project choice | Shared host configuration; only receipt-recorded `host_hooks` matcher groups belong to devkit |
| `AGENTS.md` (root) | yes | Project-owned; only the `<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->` block is managed |
| Seeded files (`seeded` in the receipt) | yes | Project-owned; written once by a bundle, never updated or removed by sync |

Commit the tracked paths with the change that required them. Projections stay
ignored per the repository's `.gitignore`; devkit never edits it or the Git index.

`uv run devkit sync` rebuilds the generated paths from the installed packages
and the configuration. It halts with `SYNC_CONFLICT` on a modified managed file
or a foreign file in its way, adopts a foreign file identical to what it would
write, and never deletes foreign files. A modified file that is no longer
selected stays in place as an `ORPHAN_LEFT` warning; ask the user before
removing it. Follow each advisory's `[ACTION]`; report every `[WARN]` to the user.

The root `AGENTS.md` block is regenerated from the selection and hash-guarded
like a managed file: write project guidance outside the markers.
`guidance_block = false` turns it off; a block edited by hand is then left in
place with an `ORPHAN_LEFT` warning.

Seeded files are scaffolding a bundle wrote on first sync (a docs tree, a
policy file). Edit them freely; sync writes one again only when it was deleted
while its asset is still selected.

Selected `hook` assets register installed handlers at native host events;
`devkit host status --format json` inspects registration, handler validity and
the observer's last metadata. Removing the bundle removes only its owned
groups. Host enablement, trust and execution permissions stay separate: a
successful installation does not establish them.

Rule, gate and workflow assets are deployed like any other kind; their engines
come with `devkit-agt`, whose auto-selected `harness` bundle covers them.

When a failing rule's remediation names a playbook, run the
`uv run devkit playbook search` it names, read the chosen procedure from the
returned path, loading its bundle's context (`uv run devkit get-context <bundle>`)
first if not yet loaded, then apply it.

## Changing what is deployed

```bash
uv run devkit list                    # installed bundles, presets, selection state, deployed paths
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
can be selected. `BUNDLE_AUTO_SELECTED` names an auto-selected bundle when it
is first deployed: tell the user, and opt it out with `devkit remove <bundle>`
only when they ask. A deployed bundle whose package is not installed fails the
sync with `SELECTION_INVALID`, so a partial environment never deletes committed
files: run `uv sync` when the package belongs in the environment, or
`devkit remove <bundle>` when the user removed it.

`uv run devkit config template` adds commented keys for what the file lacks,
including the tables installed engines and tools register, with defaults or
marked examples; it never changes a line, and `--print` shows the result under
`text` without writing. Read those comments to learn what a setting does.

`devkit sync --locked` rebuilds only the Git-ignored copies the committed
receipt records and never writes the receipt, the `AGENTS.md` block or seeded
files; when those would change, it writes nothing and fails with `RECEIPT_STALE`.

## Customizing an upstream asset

```bash
uv run devkit override create <bundle>:<asset>   # copy the asset's files into .devkit/overrides/, then sync
uv run devkit override list                      # tracked overrides and their drift status
uv run devkit override diff <bundle>:<asset>     # per file: what upstream changed, what the override changed
uv run devkit override accept <bundle>:<asset>   # record the current upstream as the baseline after merging
uv run devkit override remove <bundle>:<asset>   # use upstream sources again
```

`create` copies every file of the asset (a whole skill directory). An override
file replaces its upstream file in projections, `get-context` and playbook
search; even an unchanged copy follows upstream only through `accept`. For a
`.md.jinja` asset, edit the raw template override and sync; agents read the
rendered managed `.md`. Bundle variables are set under
`[bundles.<bundle>.variables]` in `.devkit/config.toml`. Drift is reported when
any upstream file of the asset changes; `create --force` restarts the override
from the current upstream. Only assets of selected bundles can be overridden;
edit seeded files in place, and the repository's own assets in their source
bundle (`in-repo-bundle`).

## Checking the installed state

`uv run devkit status` compares the workspace with the receipt without changing
anything: managed files, override drift, the guidance block, seeded files,
package availability, a pending journal and the devkit version that wrote the
receipt. It lists what needs acting on under `errors`, each with its
`advisory`, and exits 1 when there is any. `uv run devkit sync --check` exits 1
with one `[CHANGE: ...]` line per pending write when a sync is needed, and 2 on
an error. Every command takes `-w <dir>` for another project.

## Recovering an interrupted sync

`TRANSACTION_PENDING`: run `uv run devkit recover`, which restores the files
the journal names to their state before the interrupted run, then run
`devkit sync` again. `LOCK_HELD`: another devkit command is running; wait for
it and never delete the lock.
