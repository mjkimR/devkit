---
name: harness-consumption
description: Read before running, configuring or troubleshooting rules, commit gates or delivery workflows, including their .devkit/config.toml tables and per-clone gate settings.
---

# Running the devkit harness

`devkit-agt` adds `devkit rules`, `devkit workflow`, `devkit gate`,
`devkit worktree`, `devkit generated`, `devkit integration` and `devkit run` to
the `devkit` executable.

## Configuration tables

The engines own these tables of `.devkit/config.toml`:

| Table | Owner | Holds |
| --- | --- | --- |
| `[rules]` | rule engine | Exclusions, severity and phase overrides, per-rule settings |
| `[gates]` | commit gate | Gate settings (`[gates.settings.<gate>]`) |
| `[workflow]` | workflow engine | Layout, approval policies (`[workflow.approvals]`) and stage switches (`[workflow.stages]`) |
| `[worktree]` | task worktrees | Integration policy, branch cleanup, setup command, stale period |
| `[integration]` | integration | The readiness provider of approval-bound integration |

If the file lacks the `[workflow.approvals]`, `[workflow.stages]` or `[worktree]`
tables, `uv run devkit config template` adds them, commented, at their defaults.

## Workflows

A workflow definition makes `devkit sync` generate the `devkit-workflow` entry
skill. Follow that skill instead of inferring a work unit's stage yourself: it
runs `devkit workflow next` to compute the stage, and the stage skills the
definition names do the work.

## Rules and commit gates

Synchronized rules load automatically from the receipt:

```bash
uv run devkit rules check                     # working tree, linter phase
uv run devkit rules check --staged            # exactly what a commit would contain
uv run devkit rules check --ci --base origin/main
uv run devkit rules fix --dry-run
uv run devkit rules explain <RULE-id>
uv run devkit rules test [<RULE-id>]          # the tests in each rule's folder (needs pytest)
```

- The built-in `rules-check` gate runs the `--staged` evaluation on every
  commit; set `enabled = false` in `[gates.settings.rules-check]` to turn it off.
- Put per-clone gate settings in `.git/devkit.config`, which lists every
  installed gate as a commented table. Uncomment a table's header and only the
  keys you change; each replaces its `.devkit/config.toml` value.

## Completion

`uv run devkit rules check --staged` exits `0` for the change you commit.
