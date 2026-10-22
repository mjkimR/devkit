---
name: harness-consumption
description: Read before running, configuring or troubleshooting rules, commit gates or delivery workflows, including their .devkit/config.toml tables and per-clone gate settings.
---

# Running the devkit harness

- The engines own `[rules]`, `[gates]`, `[workflow]`, `[worktree]` and
  `[integration]` in `.devkit/config.toml`; `uv run devkit config template --print`
  shows the commented defaults the file lacks.
- Follow the generated `devkit-workflow` entry skill instead of inferring a work
  unit's stage yourself; it runs `devkit workflow next`.
- Run `uv run devkit rules check` for the working tree, `--staged` for exactly
  what a commit would contain, and `uv run devkit rules explain <RULE-id>` for a
  rule's guide.
- The built-in `rules-check` gate runs the `--staged` evaluation on every commit;
  `enabled = false` in `[gates.settings.rules-check]` turns it off.
- Put per-clone gate settings in `.git/devkit.config`: uncomment a listed gate's
  table header and only the keys you change.

Done when `uv run devkit rules check --staged` exits `0` for the change you commit.
