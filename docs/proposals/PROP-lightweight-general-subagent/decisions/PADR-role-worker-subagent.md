---
id: PADR-role-worker-subagent
title: Shared role-worker subagent for skill-local roles
summary: "For skill-local role delegation, we ship a tool-limited role-worker subagent in the auto-selected devkit bundle and assign it statically per role, to cut each child's fixed context by about half, accepting one listing line in every consumer and a widened devkit-bundle contract."
proposal: PROP-lightweight-general-subagent
supersedes: [ADR-skill-local-research-roles, ADR-package-ownership-and-release-version]
status: draft
created_at: 2026-11-10
---

# [PADR-role-worker-subagent] Shared role-worker subagent for skill-local roles

- **Status**: Draft
- **Date**: 2026-11-10

---

## 1. Context & Problem Statement

Skill-local roles (deep-research, app-uiux-improve, design-explore) pass a role file to a general subagent so that no
role metadata enters global context. On Claude Code that subagent is `general-purpose`, which receives every tool,
MCP tools included. It starts each child at about 36k input tokens, while subagents with a restricted tool list start
at 11k to 16k on the same machine (`PROP-lightweight-general-subagent` materials). A per-role registered subagent
would cut the load but expose role descriptions outside explicit invocation. The `devkit` bundle, the only
auto-selected `devkit-dist` bundle that fits, is limited to distribution guidance with instructions only.

## 2. Decision Drivers

- Lower the fixed context of each role child.
- Keep explicit-only skills and their roles out of global listings.
- Guarantee availability without a bundle dependency mechanism or caller fallback logic.
- Keep the change small for a personal project.

## 3. Considered Options

- Keep `general-purpose` for every role: no change, but each child keeps the full tool and skill load.
- Register one subagent per role: lowest load per role, but role descriptions become globally visible.
- One neutral, tool-limited `role-worker` in the `devkit` bundle: one neutral listing line, guaranteed with
  `devkit-dist`, but it widens the `devkit` bundle contract.
- The same subagent in a new auto-selected `devkit-dist` bundle: leaves the `devkit` contract alone, but adds a
  bundle, its documentation and tests for one asset.

## 4. Decision Outcome

The choice is one neutral, tool-limited `role-worker` in the `devkit` bundle, because it lowers the load per child,
exposes no role or skill name and arrives wherever `devkit-dist` syncs, with the fewest new parts.

- The `devkit` bundle's `core` preset ships the `role-worker` subagent. Its Claude Code block allows only Read, Grep,
  Glob, Bash, Edit, Write, WebSearch, WebFetch and Agent; its Codex block is emulated with workspace-write and its
  Antigravity block is unverified. → CAP-DIST-agent-projections (planned)
- `role-worker` reads the role file its prompt names and follows it as the assignment contract; without one, it
  treats the prompt as the assignment.
- A skill's instructions assign the subagent type per role or assignment: `role-worker` by default, and
  `general-purpose` for an assignment that needs a capability outside the `role-worker` tool list, such as
  interacting with a running UI. This is a fixed mapping, not a runtime fallback. → `CAP-DLV-deep-research` rule 11
  (MUST)
- A caller that cannot find `role-worker` stops that delegation and reports the missing subagent and its cause.
- The `devkit` bundle holds distribution guidance and general subagents that other bundles share.

Supersedes in part `ADR-skill-local-research-roles`: the clause that a general subagent receives the selected role path and bounded assignment.

Supersedes in part `ADR-package-ownership-and-release-version`: the clause that the `devkit` bundle keeps only distribution guidance.

## 5. Consequences

- Each role child starts with roughly half the input tokens on Claude Code; the gain grows with the host's MCP and
  skill set, and Codex gains nothing because it has no tool allowlist.
- Every consumer gets one more listing line and new projection files on upgrade; release notes mention them.
- A project that sets `devkit = false` loses role delegation in these skills until it re-enables the bundle.
- Follow-up: when another skill adds local roles, its author assigns `role-worker` or names `general-purpose` per
  role, as the skill-authoring playbook says.

## 6. Confirmation

- A devkit-dist integration test asserts the `role-worker` projection for all three hosts with their statuses and the
  Claude Code tool list, and `test_guide_bundle.py` admits the subagent.
- Catalog integration tests assert that deep-research, app-uiux-improve and design-explore name `role-worker`.
- Review checks the token reduction: at least five `role-worker` children with a median first-call input of at most
  18k tokens against a same-machine `general-purpose` sample.
