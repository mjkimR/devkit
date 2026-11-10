---
id: SPEC-lightweight-general-subagent
title: Lightweight general subagent for role-file delegation
summary: Add a neutral, tool-limited role-worker subagent to the auto-selected devkit bundle and route skill-local role-file delegation to it, so role children start without the full general-purpose tool and skill context.
status: in-progress
created: 2026-11-10
namespace: global
related_capabilities:
  - CAP-DIST-agent-projections
  - CAP-DIST-content-packages
  - CAP-DLV-deep-research
  - CAP-DLV-uiux-improvement
  - CAP-DLV-design-exploration
  - CAP-HARN-agent-guidance
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-lightweight-general-subagent] Lightweight general subagent for role-file delegation

## 1. Problem Statement & Motivation

Handed off from proposal PROP-lightweight-general-subagent on 2026-11-10. The decision is
`ADR-role-worker-subagent`; its Decision Outcome clauses and Confirmation are this spec's contract.

- **Preserved Materials**: `docs/materials/2026-11/20261110-lightweight-general-subagent`
  ([first-call-tokens.md](../../../docs/materials/2026-11/20261110-lightweight-general-subagent/first-call-tokens.md)).

Skill-local roles (deep-research, app-uiux-improve, design-explore) pass a role file to a general subagent so that no
role metadata enters global context (`ADR-skill-local-research-roles`). On Claude Code that subagent is the built-in
`general-purpose` type, which receives every tool, MCP tools included. Its children start at about 36k input tokens
on their first call, while the Host's prompt is about 1k tokens. Subagents with a restricted tool list start at 11k to
16k on the same machine.

A registered subagent costs the Host one listing line (name, description, tools) until it is spawned; its body loads
only for the child. One registered subagent with a neutral name and description keeps explicit-only skills
unadvertised, while a restricted tool list removes most of the fixed load.

**Hypothesis**: on Claude Code, a registered `role-worker` subagent limited to `Read, Grep, Glob, Bash, Edit, Write,
WebSearch, WebFetch, Agent` starts with a median first-call input of at most 18k tokens, against about 36k for
`general-purpose` on the same machine and Claude Code version, and the role-file callers' roles complete their
assignments with that tool list. Codex gains nothing, because its projection has no tool allowlist.

## 2. User Stories

- **US-1**: As a coordinator agent running an explicitly invoked skill, I want to delegate a skill-local role to a
  tool-limited subagent, so that each role child starts with about half the fixed context of `general-purpose`.
- **US-2**: As a consumer, I want the subagent to arrive wherever `devkit-dist` syncs, without selecting another
  bundle and without its name or description advertising an explicit-only skill.
- **US-3**: As a skill author, I want the skill-authoring guidance to tell me which subagent type a skill-local role
  uses, so that new skills assign it statically.

## 3. Non-Goals

1. **Scope Excluded**: `general-purpose` itself and any host's built-in subagent types.
2. **Scope Excluded**: the spec bundle's dedicated subagents and workflows, and `sdd-overall-refactor`'s general
   subagents for parallel drafting, edits and research, which carry no role file.
3. **Scope Excluded**: adaptive-dev's skill-local builder role, whose child holds commit authority and worktree
   ownership; the skill-authoring guidance names it as the exception.
4. **Scope Excluded**: a runtime fallback from `role-worker` to another subagent type, a bundle-to-bundle dependency
   key in `bundle.toml`, a new auto-selected bundle and a new feature edge in `.devkit/architecture.toml`.
5. **Scope Excluded**: release notes; they are written when the release is prepared.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The devkit bundle projects role-worker for every host

- **Given** a consumer that selects the `devkit` bundle's `core` preset and every agent (`claude-code`, `codex`,
  `antigravity`)
- **When** `sync_project` runs with the shipped `devkit` bundle
- **Then** `.devkit/managed/devkit/subagents/role-worker.md` exists and exactly three projections are written:
  - `.claude/agents/role-worker.md` with frontmatter `name: role-worker` and `tools: [Read, Grep, Glob, Bash, Edit,
    Write, WebSearch, WebFetch, Agent]`, a prompt naming `Host projection: native.`, and no `model` or `effort` key;
  - `.codex/agents/role-worker.toml` with `sandbox_mode = "workspace-write"`, `Host projection: emulated.` in
    `developer_instructions`, and no `model` or `model_reasoning_effort` key;
  - `.agents/agents/role-worker.md` with `tools: [view_file, grep_search, replace_file_content, run_command]`,
    `commandExecutionPolicy: sandbox`, `subagent: true`, a prompt naming `Host projection: unverified.`, and no
    `model` key.

### [AC-02] The devkit bundle admits shared subagents and stays out of AGENTS.md

- **Given** the shipped `devkit` bundle manifest
- **When** it is loaded
- **Then** its `core` preset selects the three instructions `consumption`, `resource-kinds` and `in-repo-bundle` and
  the subagent `role-worker`; it ships no other asset kind and no guidance fragment, so a sync with `devkit:core`
  writes no line inside the root `AGENTS.md` block for the bundle.

### [AC-03] The role-worker contract is neutral and follows the named role file

- **Given** the `role-worker` contract
- **When** its frontmatter and body are read
- **Then** it omits `level`; its `role`, `title` and `description` name no skill, bundle or research role; and its
  body directs the child to:
  - read the role file the prompt names before acting and follow it as the assignment contract;
  - treat the prompt as the assignment when it names no role file;
  - delegate only independent work, preferring `role-worker` or a fitting dedicated subagent over `general-purpose`.

### [AC-04] deep-research assigns role-worker to every role

- **Given** the deep-research skill
- **When** its `SKILL.md` step 4 and `references/orchestration.md` are read
- **Then** both name `role-worker` as the subagent type for the selected role file, and the orchestration reference
  states that a coordinator that cannot find `role-worker` stops that delegation and reports the missing subagent and
  its cause instead of spawning another type.

### [AC-05] app-uiux-improve assigns subagent types per assignment

- **Given** the app-uiux-improve skill's `references/orchestration.md`
- **When** a local-role assignment is dispatched
- **Then** an assignment that interacts with a running UI names `general-purpose`, every other assignment names
  `role-worker`, and a missing `role-worker` stops that delegation with the missing subagent and its cause reported.

### [AC-06] design-explore assigns role-worker to its roles

- **Given** the design-explore skill's `references/orchestration.md`
- **When** a local role is dispatched
- **Then** every role names `role-worker` unless the assignment interacts with a running UI, which names
  `general-purpose`, and a missing `role-worker` stops that delegation with the missing subagent and its cause
  reported.

### [AC-07] Skill authors assign role-worker by default

- **Given** the skill-authoring playbook's `references/roles.md`
- **When** an author writes delegation for a skill-local role
- **Then** it makes `role-worker` the default subagent type, tells the author to name `general-purpose` for a role or
  assignment that needs a capability outside the `role-worker` tool list, tells the author to make a missing
  `role-worker` stop the delegation with its cause reported, and names a role whose child holds commit authority or
  worktree ownership (adaptive-dev's builder) as the exception that keeps its own delegation.

## 5. Assumptions

- The Antigravity block carries `commandExecutionPolicy: sandbox` like `swarm-worker`, whose host blocks the
  proposal names as the precedent (Q3); the payload lists only its status and tools.
- The contract body ends with a default return (status, result, evidence, assumptions, unverified areas) for a prompt
  that names no return fields, so a child without a role file still returns a checkable result.
- `docs/development/reference/distribution.md` §4, which restates the `devkit` bundle's contents from
  `CAP-DIST-content-packages`, is updated in step as a recorded scope extension.
- The authoring bundle's integration test is the test mirror of the skill-authoring playbook and carries AC-07's
  check as a recorded scope extension.

## 6. Manual Check

With the method of
[first-call-tokens.md](../../../docs/materials/2026-11/20261110-lightweight-general-subagent/first-call-tokens.md),
at least five `role-worker` children have a median first-call input of at most 18k tokens, compared with a
`general-purpose` sample from the same machine and Claude Code version. The Host runs it in a fresh session after
landing, because a running session does not load a subagent projected during it; it is review evidence, not a test.

## 7. Planning Decisions

- **D1** (user): `role-worker` lives in the `devkit` bundle as minimal distribution infrastructure; only `devkit` and
  `advisory` are auto-selected from `devkit-dist`, and no other existing bundle fits.
- **D2** (user): design-explore joins the role-file callers.
- **D3** (user): callers assign subagent types statically per role or assignment; running-UI interaction uses
  `general-purpose`, everything else `role-worker`.
- The name `role-worker` (user) names the role-file pattern, names no skill, bundle or research role, and avoids the
  `lean` subagent model level name (`ADR-subagent-levels`).
- `swarm-worker` is not reused: its contract carries commit authority and an owned implementation assignment, and
  `devkit-adaptive` is not always installed.
