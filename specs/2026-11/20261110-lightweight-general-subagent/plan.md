---
id: PLAN-lightweight-general-subagent
spec: SPEC-lightweight-general-subagent
---

# Technical Plan: `SPEC-lightweight-general-subagent` Lightweight general subagent for role-file delegation

## 1. Constitution & Invariant Review

`ADR-role-worker-subagent` decides the change. It supersedes in part `ADR-skill-local-research-roles` (the clause
that a general subagent receives the selected role path; rule 1, no registered research subagents, remains) and
`ADR-package-ownership-and-release-version` (the clause that the `devkit` bundle keeps only distribution guidance).
Both ADRs already carry their pointers. The `devkit` bundle stays dependency-free: a role contract is data that
`devkit-dist` already projects (`CAP-DIST-agent-projections`), so no import, package, feature or feature edge is
added (`ARCH-05-2-components`). No other invariant changes.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/` | New role contract `subagents/role-worker.md`; `bundle.toml` declares it and adds it to the `core` preset. |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/` | `SKILL.md` step 4 and `references/orchestration.md` name `role-worker` and the stop-and-report rule. |
| `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/` | `references/orchestration.md` maps running-UI assignments to `general-purpose`, others to `role-worker`. |
| `packages/devkit-catalog/src/devkit_catalog/design_explore/` | `references/orchestration.md` names `role-worker`, with the same running-UI exception. |
| `packages/devkit/src/devkit_agt/bundles/authoring/.../skill-authoring/references/roles.md` | `role-worker` becomes the default type for skill-local roles, with the `general-purpose` and commit-authority exceptions. |
| Living Spec | `CAP-DIST-agent-projections` and `CAP-DIST-content-packages` list `role-worker`; the three delivery capabilities and `CAP-HARN-agent-guidance` name the assigned types; `ADR-role-worker-subagent`'s planned trace becomes current. |
| Sync outputs | This repository selects the `devkit` bundle, so `devkit sync` writes the managed contract, three projections and the receipt. |

## 3. Component & Interface Design

The contract follows the role contract format of `CAP-DIST-agent-projections` with the `swarm-worker` host blocks:

```yaml
role: role-worker
title: Role Worker
description: Carries out one delegated assignment, following the role file its prompt names when there is one.
hosts:
  claude-code: {status: native, tools: [Read, Grep, Glob, Bash, Edit, Write, WebSearch, WebFetch, Agent]}
  codex: {status: emulated, sandbox_mode: workspace-write}
  antigravity: {status: unverified, tools: [view_file, grep_search, replace_file_content, run_command],
                commandExecutionPolicy: sandbox}
```

No `level` and no native `model`/`effort` key, so every projection inherits the model. The body is a short numbered
procedure: read the named role file first and follow it; stop on a missing role file; without one, treat the prompt
as the assignment; stay within the stated boundaries; delegate only independent work, preferring `role-worker` or a
fitting dedicated subagent over `general-purpose`; return the role file's fields or a default return.

Callers name the subagent type in the dispatch instruction itself (static per role or assignment). A missing
`role-worker` is a stop-and-report directive in each orchestration reference, not a fallback.

## 4. Error Handling & Edge Cases

- `devkit = false`: no `role-worker` projection; the callers stop the delegation and report the missing subagent with
  its cause (bundle deselected or host without the projection).
- A consumer-owned `.claude/agents/role-worker.md` is a foreign file and follows the existing workspace-ownership
  safeguards (`CAP-DIST-workspace-ownership`); nothing new is added.
- A role file that is missing or unreadable stops the child before it acts.

## 5. Verification & Test Plan

| AC | Check |
| --- | --- |
| AC-01, AC-02, AC-03 | `packages/devkit-dist/tests/integration/features/distribution/test_guide_bundle.py`: manifest asset set and kinds, sync projections for all three hosts with statuses, tools, no model keys, and the contract's neutral wording and procedure. |
| AC-04 | `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` |
| AC-05 | `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py` |
| AC-06 | `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py` |
| AC-07 | `packages/devkit/tests/integration/bundles/authoring/test_bundle.py` |

Commands, run synchronously in the worktree: `just lint-check`, `just check`, `just rules-check`,
`just test-affected` (default tier), `just test-dist`, `uv run devkit sync --check` and
`uv run devkit generated check`. Agent-asset self-containment: the `rg` ID scan of `agent-asset-writing` over each
edited bundle directory and `uv run devkit rules check --phase hygiene <asset>`.

The manual token check (spec §6) is pending Host evidence after landing; Development records it as not run.
