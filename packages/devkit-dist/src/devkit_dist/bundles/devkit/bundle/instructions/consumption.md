---
name: consumption
description: Read before using, changing or troubleshooting devkit-managed assets, including selection, overrides, sync, the receipt, status and recovery.
---

# Consuming devkit-managed assets

## What devkit owns in the workspace

| Path | In Git | Role |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Selected bundles and presets, target agents, `guidance_block`, `override_drift`, `[playbooks]`; tables reserved for `devkit-agt` engines and `[tool.<name>]` tables are passed through unread |
| `.devkit/config.local.toml` | no | Optional checkout-local execution, MCP registration, playbook and bundle-variable preferences |
| `.devkit/installation.json` | yes | Canonical receipt: packages, bundle versions, deployed paths, SHA-256 and mode of every file |
| `.devkit/overrides/<bundle>/` | yes | Project-owned replacements for upstream asset files (baselines under `.devkit/overrides/.baseline/`) |
| `.devkit/.gitignore` | yes | Seeded ignore rules; sync maintains `/config.local.toml` and preserves other entries |
| `.devkit/managed/<bundle>/` | no | Generated canonical or eligible personally rendered copies |
| `.devkit/transient/` | no | Lock, transaction journal, deployed signatures and personal-render evidence |
| `.claude/`, `.agents/`, `.codex/` projections | usually no | Native copies of skills and subagents for each selected agent |
| `.codex/hooks.json` | project choice | Shared host configuration; only receipt-recorded `host_hooks` matcher groups belong to devkit |
| `AGENTS.md` (root) | yes | Project-owned; only the `<!-- DEVKIT:START -->` ... `<!-- DEVKIT:END -->` block is managed |
| Seeded files (`seeded` in the receipt) | yes | Project-owned scaffolding (a docs tree, a policy file); edit freely. Sync writes one again only when it was deleted while its asset is still selected |

Commit the tracked paths with the change that required them. Projections stay
ignored per the repository's `.gitignore`; devkit never edits it or the Git index.

`uv run devkit sync` rebuilds the generated paths from the installed packages
and the configuration:

- On a modified managed file or a foreign file in its way, it halts with `SYNC_CONFLICT`.
- It adopts a foreign file identical to what it would write and never deletes foreign files.
- A modified file that is no longer selected stays in place as an `ORPHAN_LEFT`
  warning; ask the user before removing it.
- Follow each advisory's `[ACTION]`; report every `[WARN]` to the user.

The root `AGENTS.md` block is regenerated from the selection and hash-guarded
like a managed file; write project guidance outside the markers.
`guidance_block = false` turns the block off; a block edited by hand is then
left in place with an `ORPHAN_LEFT` warning.

Selected `hook` assets register installed handlers at native host events.

- Inspect registration, handler validity and the observer's last metadata with
  `devkit host status --format json`.
- Removing the bundle removes only its owned groups.
- Installation does not grant host enablement, trust or execution permissions.

Rule, gate and workflow assets deploy like any other kind; only an installed
`devkit-agt` runs them.

When a failing rule's remediation names a playbook:

1. Run the `uv run devkit playbook search` it names.
2. If the chosen playbook's bundle context is not loaded yet, run
   `uv run devkit get-context <bundle>`.
3. Read the chosen procedure from the returned path, then apply it.

## Retrieving an explicitly named playbook

When the user names an exact playbook for this task, or explicitly configures
an external schedule with its ID:

1. Run `uv run devkit playbook get <bundle>/<playbook>` with the case-sensitive
   manifest IDs. Its JSON result holds the complete body, effective metadata,
   source path and hash, and context requirements.
2. Unless already loaded in this agent context, run its context argv in the same
   workspace (or pass `-w`); reload after the context was lost.
3. Apply the full constitution and read the relevant instructions.
4. Read needed relative resources from the parent of `source.path`.

Retrieval reads overrides live, uses the deployed receipt for selection until
the next sync, and never executes or synchronizes.

- Start each execution fresh: check prerequisites, workflow gates, permissions
  and user constraints again.
- A schedule grants no future gated approval; unavailable approval UI is not approval.
- Leave cadence, launch, retries, overlap and history to the external system.

## Changing what is deployed

```bash
uv run devkit list                    # installed bundles, presets, selection state, deployed paths
uv run devkit add <bundle>            # select with the bundle's default preset, then sync
uv run devkit add <bundle>:<preset>   # add a preset to those the bundle already deploys
uv run devkit remove <bundle>         # deselect (an auto-selected bundle is recorded as false), then sync
uv run devkit sync --preset <bundle>:<preset>   # replace a bundle's presets
uv run devkit sync                    # converge to .devkit/config.toml
uv run devkit sync --no-save --agent claude-code --agent codex   # narrow projections for one run only
uv run devkit sync --locked           # fresh clone, CI: restore ignored copies, never change committed files
```

- Install a bundle's package (`uv add --dev <package>`) before selecting the bundle.
- Without `agents` in `.devkit/config.toml`, every supported agent gets projections.
- When `BUNDLE_AUTO_SELECTED` names an auto-selected bundle on its first
  deployment, tell the user. Opt it out with `devkit remove <bundle>` only when they ask.
- A deployed bundle whose package is not installed fails the sync with
  `SELECTION_INVALID`, so a partial environment never deletes committed files.
  Run `uv sync` when the package belongs in the environment, or
  `devkit remove <bundle>` when the user removed it.
- `sync --locked` rebuilds only the Git-ignored copies the committed receipt
  records. When the receipt, the `AGENTS.md` block or seeded files would change,
  it writes nothing and fails with `RECEIPT_STALE`. It permits eligible ignored
  personal output and `--cloud` or `--local` environment persistence.

To learn what a setting does, run `uv run devkit config template`: it adds
commented keys for what the file lacks, including the tables installed engines
and tools register, and never changes an existing line. `--print` shows the
result under `text` without writing.

## Checkout-local preferences

Use ignored `.devkit/config.local.toml` for `[execution] environment = "local" | "cloud"`,
`[mcp] register = true | false`, `[playbooks]` search preferences and scalar
`[bundles.<bundle>.variables]` values. Governance, selection and commands stay
shared; unknown local keys fail with `CONFIG_LOCAL_KEY_FORBIDDEN`. Do not store
secrets in the file. `uv run devkit config show --effective --format json` shows
values, sources and the execution environment.

- `uv run devkit sync --cloud` saves cloud execution; `--local` returns to local.
  Ordinary sync keeps the saved environment; `--no-save`, `--dry-run` and
  `--check` do not persist it.
- Cloud means interactive approval is unavailable, never approval to act; local
  does not prove the host can interact.

Personal variables may change only ignored, untracked skill, instruction,
subagent and playbook content; receipt hashes, guidance, seeds, paths, modes and
executable assets stay canonical. A tracked or unignored personal destination
fails with `CONFIG_LOCAL_NOT_IGNORED`, a forbidden render change with
`CONFIG_LOCAL_RENDER_FORBIDDEN`. On `CONFIG_LOCAL_RENDER_STALE` (missing or stale
local evidence), run sync. Remove the personal variables and sync to restore
canonical output.

## Customizing an upstream asset

```bash
uv run devkit override create <bundle>:<asset>   # copy the asset's files into .devkit/overrides/, then sync
uv run devkit override list                      # tracked overrides and their drift status
uv run devkit override diff <bundle>:<asset>     # per file: what upstream changed, what the override changed
uv run devkit override accept <bundle>:<asset>   # record the current upstream as the baseline after merging
uv run devkit override remove <bundle>:<asset>   # use upstream sources again
```

- `create` copies every file of the asset (a whole skill directory).
- An override file replaces its upstream file in projections, `get-context`,
  playbook search and exact retrieval. Even an unchanged copy follows upstream
  only through `accept`.
- For a `.md.jinja` asset, edit the raw template override and sync; agents read
  the rendered managed `.md`.
- Set bundle variables under `[bundles.<bundle>.variables]` in `.devkit/config.toml`.
- Drift is reported when any upstream file of the asset changes; `create --force`
  restarts the override from the current upstream.
- Override only assets of selected bundles. Edit seeded files in place, and the
  repository's own assets in their source bundle (`in-repo-bundle`).

## Checking the installed state

- `uv run devkit status` compares the workspace with the receipt without
  changing anything: managed files, override drift, the guidance block, seeded
  files, package availability, a pending journal and the devkit version that
  wrote the receipt. It lists what needs acting on under `errors`, each with its
  `advisory`, and exits `1` when there is any.
- `uv run devkit sync --check` exits `1` with one `[CHANGE: ...]` line per
  pending write when a sync is needed, and on a concurrent configuration change
  (`CONFIG_LOCAL_CHANGED`); other failures use their advisory exit status.
- Every command takes `-w <dir>` for another project.

## Recovering an interrupted sync

- `TRANSACTION_PENDING`: run `uv run devkit recover`, which restores the files
  the journal names to their state before the interrupted run, then run
  `uv run devkit sync` again.
- `LOCK_HELD`: another devkit command is running. Wait for it; do not delete the lock.

## Completion

After a change to what is deployed, `uv run devkit status` and
`uv run devkit sync --check` both exit `0`.
