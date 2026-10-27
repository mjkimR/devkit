---
id: FB-shared-agent-invocation-constant
title: The uv run devkit prefix is defined per package
scope: repo
kind: suggestion
category: other
target: devkit_dist.features.distribution.models.invocation; devkit_agt gate/workflow/worktree/rules errors; devkit_dist host errors
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-27
---

# [FB-shared-agent-invocation-constant] The uv run devkit prefix is defined per package

Code consistency: the agent-facing invocation from `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: distribution has `AGENT_INVOCATION`/`devkit_command()`, the gate has its own `DEVKIT`
  constant, and host, workflow, worktree and rules write `uv run devkit` literally; `devkit_dist.base.errors` still
  writes bare `devkit sync` in some fixes. devkit-agt features cannot import the distribution module under
  `.devkit/architecture.toml`.
- **Proposed Procedure**: one public constant in a module every feature may depend on (`devkit_dist.base` or
  `devkit_dist.features.project`), used by every `[FIX]`.
- **Expected Benefit**: one place to change the invocation; no bare `devkit` left in fixes.
- **Cost & Risk**: mechanical replacement across packages.
- **Attempted**: not attempted.

## Diagnostic Details

- **Reproduction**: `rg "uv run devkit" packages/*/src`.
- **Expected / Actual**: expected one definition; actual several.
- **Versions**: branch `dev-onboarding-polish`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation`.

## Evidence

```text
AGENT_INVOCATION (distribution), DEVKIT (gate), literals (host, workflow, worktree, rules)
```
