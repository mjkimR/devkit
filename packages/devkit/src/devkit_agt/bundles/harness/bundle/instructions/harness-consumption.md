---
name: harness-consumption
description: Read before running, configuring or troubleshooting rules, commit gates or delivery workflows, including their .devkit/config.toml tables and per-clone gate settings.
---

# Running the devkit harness

`devkit-agt` mounts `devkit rules`, `devkit workflow`, `devkit gate`,
`devkit worktree`, `devkit generated`, `devkit integration` and `devkit run`
under the `devkit` executable. Their assets are deployed like any other (the
`devkit` bundle's `consumption` instruction).

## Configuration tables

The engines own these tables of `.devkit/config.toml`:

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

A workflow definition makes `devkit sync` generate the `devkit-workflow` entry
skill, which runs `devkit workflow next` to compute a work unit's current stage;
the stage skills the definition names do the work. Follow the entry skill
instead of inferring the stage yourself.

## Rules and commit gates

Synchronized rules load automatically from the receipt:

```bash
uv run devkit rules check                     # working tree, linter phase
uv run devkit rules check --staged            # exactly what a commit would contain
uv run devkit rules check --ci --base origin/main
uv run devkit rules fix --dry-run
uv run devkit rules explain <RULE-id>
uv run devkit rules test [<RULE-id>]            # the tests in each rule's folder (needs pytest)
```

Put per-clone gate settings in `.git/devkit.config`, which lists every
installed gate as a commented table. Uncomment a table's header and only the
keys you change; each replaces its `.devkit/config.toml` value.

The built-in `rules-check` gate runs the `--staged` evaluation on every commit.
To turn it off, set `enabled = false` in `[gates.settings.rules-check]`.
