---
name: harness-consumption
description: Read before running, configuring or troubleshooting repository rules, commit gates or delivery workflows of devkit-agt. Covers their configuration tables in .devkit/config.toml, the devkit-workflow entry skill, devkit rules and devkit gate, per-clone gate settings and Git snapshot gates.
---

# Running the devkit harness

`devkit-agt` mounts its engines under the `devkit` executable of `devkit-dist`:
`devkit rules`, `devkit workflow`, `devkit gate`, `devkit worktree`,
`devkit generated`, `devkit integration` and `devkit run`. Their assets (rules,
gates, workflow definitions) are deployed by `devkit sync` and recorded in the
receipt like every other asset; the `devkit` bundle's `consumption` instruction
covers that lifecycle.

## Configuration tables

The engines own reserved tables of `.devkit/config.toml`, which distribution
passes through unread:

| Table | Owner | Holds |
| --- | --- | --- |
| `[rules]` | rule engine | Exclusions, severity and phase overrides, per-rule settings |
| `[gates]` | commit gate | Gate settings (`[gates.settings.<gate>]`) |
| `[workflow]` | workflow engine | Layout, approval policies (`[workflow.approvals]`) and stage switches (`[workflow.stages]`) |
| `[worktree]` | task worktrees | Integration policy, branch cleanup, setup command, stale period |
| `[integration]` | integration | The readiness provider of approval-bound integration |

`uv run devkit config template` adds the commented `[workflow.approvals]`,
`[workflow.stages]` and `[worktree]` tables at their defaults when the file
lacks them.

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
its `.devkit/config.toml` value; devkit only appends tables for new gates). The
built-in `rules-check` gate runs the `--staged` evaluation on every commit; turn it
off with `enabled = false` in `[gates.settings.rules-check]`. Snapshot gates (`--staged`,
`--ci`) evaluate the Git tree and trust the committed receipt: a managed rule
that is missing or differs from the receipt's hash fails the gate, and its
`[FIX]` says to run `devkit sync` and commit the receipt.
