# Host-neutral role contract

A role contract registers the role as its own agent on every host. No archetype wraps it, so it carries its own constraints and return contract.

## Write the file

1. Create `subagents/<prefix>-<role>.md` in the project bundle from the skeleton below.
2. Set `role` to the asset ID, prefixed with the project or bundle name and distinct from every installed agent ID; two bundles declaring one agent ID stop the sync with `BUNDLE_CONFLICT`.
3. Give `hosts` one block each for `claude-code`, `codex` and `antigravity`; a contract that omits one is invalid.
4. Copy the host settings from the archetype whose authority matches, then remove what the role does not need; add no tool or wider sandbox than that archetype has.
5. For a host the project does not use, write `status: unsupported` and no other key; that host receives no file.
6. Use `status: emulated` where the host's settings approximate the boundary and `status: unverified` where the role has not been run on that host; reserve `native` for a boundary the host enforces.
7. Leave `model`, `effort` and `model_reasoning_effort` out of every host block. Add a top-level `level` (`inherit`, `minimal`, `compact`, `lean`, `standard`, `deep` or `maximal`) on the user's request alone.
8. Write the body with the rewrite rules, and end it with the provenance line.

```markdown
---
role: <prefix>-<role>
title: <Role title>
description: <One sentence naming what the role checks and returns.>
hosts:
  claude-code:
    status: emulated
    tools: [Read, Grep, Glob]
  codex:
    status: emulated
    sandbox_mode: read-only
  antigravity:
    status: unverified
    tools: [view_file, grep_search]
    commandExecutionPolicy: "off"
---

# <Role title>

<One sentence: the bounded result this role returns.>

## Constraints

- Follow the caller's governing workflow, project instructions and authority.
- Work inside the assigned absolute paths and actions; keep product sources, index and HEAD read-only.
- Report a needed commit, push, deployment or installation to the caller instead of performing it.

## Procedure

1. Confirm the goal, source/base identity, absolute boundaries, checks, stop condition and return contract.
2. <Domain check: what to inspect and the condition that makes it a defect.>

## Return

Return status (`completed`, `needs_input` or `failed`), result, source identity, actual changed paths, commands and outcomes, defects with evidence, assumptions, unverified areas and next action.

Source: <url> at <commit>, `<path>`; rewritten for this project.
```

The skeleton's host blocks are read-only; for a role that writes, copy the writing archetype's blocks and keep the constraint lines that match them.

## Declare and deploy it

```toml
[[assets]]
id = "<prefix>-<role>"
kind = "subagent"
source = "subagents/<prefix>-<role>.md"
```

- `uv run devkit bundle validate <bundle source>` refuses an unknown key, a missing host or a `level` combined with a native model or effort field (`BUNDLE_INVALID`).
- `uv run devkit sync` renders one file per host from its block: `.claude/agents/<id>.md`, `.codex/agents/<id>.toml` and `.agents/agents/<id>.md`. A host whose status is `unsupported` receives none.
- Each projection is prefixed with the contract's managed path and host status, so the role states when the host does not enforce its boundaries.

## Select a model level without editing the contract

When the user wants a level for this project and the contract declares none, record it in `.devkit/config.toml` under the bundle-qualified role and run `uv run devkit sync`:

```toml
[subagents.roles."<bundle>:<prefix>-<role>"]
level = "lean"
```

## Use it

Invoke the role through the host's registered-role mechanism so its tool list and sandbox apply, and supply the assignment fields an archetype receives.
