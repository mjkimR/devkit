---
name: testing
description: Read before authoring, moving or organizing workspace tests across unit, integration and e2e tiers.
---

# Testing Tiers

The root `AGENTS.md` gives test locations and commands. Put each test in the tier its execution boundary allows:

| Tier | Allowed | Not allowed |
| --- | --- | --- |
| `unit` | In-memory objects and test doubles | Disk, Git, subprocesses, network |
| `integration` | In-process layers, files under `tmp_path`, `CliRunner().invoke()`, the few Git commands a fixture repository needs | Spawning `devkit` or Python, Git hooks, full repository lifecycles |
| `e2e` | `devkit` or `python -m` subprocesses, Git hooks, worktree lifecycles, spec workflows, MCP confirmation | |

Example of the e2e boundary: `packages/devkit/tests/e2e/features/gate/test_hooks.py` runs a real `git commit` that
triggers the commit-msg hook.

`just test-affected` skips e2e tests unless one changed or `--e2e` is passed; run `just test-e2e [module]` when a
change touches an end-to-end flow.
