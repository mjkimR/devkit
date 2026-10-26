---
id: FB-new-seed-sync-output-outside-boundaries
title: A new docs-skeleton seed writes a repository path no boundary names
scope: repo
kind: friction
category: missing-capability
target: RULE-proposal-boundaries
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-new-seed-sync-output-outside-boundaries] A new docs-skeleton seed writes a repository path no boundary names

## 1. Friction / Question (friction, question)

- **Context**: Development of `SPEC-ux-documentation` added `seed/docs/ux/README.md` to the `spec` bundle's
  `docs-skeleton` seed, which this repository selects.
- **Expectation**: The handed-off boundaries list every tracked file the agreed change makes `devkit sync` write, as
  they did for `.devkit/installation.json` and `AGENTS.md`.
- **Actual**: `devkit sync` seeded `docs/ux/README.md`; the path did not exist at Planning, so `RULE-proposal-boundaries`
  could not admit it, and `devkit sync --check` exited `1` until the Host extended the write scope, stopping the
  worker on a problem.
- **Workaround (or Interpretation Chosen)**: The worker recorded a problem; the Host admitted the path and the worker
  committed the seed.
- **Suggestion**: When a proposal adds a seed to a preset the repository selects, have Planning name the seeded
  target path (accepted as a path the change creates), or let `devkit sync --check` list such seeds so the handoff
  write scope includes them.

## Evidence

```text
uv run devkit sync          -> [CHANGE: seed docs/ux/README.md]
uv run devkit sync --check  -> seed=1 docs/ux/README.md, exit 1 (before the scope extension)
.devkit/config.toml         -> [presets] spec = ["core", "docs-skeleton"]
```
