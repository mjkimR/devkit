---
id: PROP-lightweight-general-subagent
title: Lightweight general subagent for role-file delegation
summary: "Add a neutral, tool-limited general subagent to the auto-selected devkit bundle and route deep-research role delegation to it, so role-file children start without the full general-purpose tool and skill context."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-10
target_area: capabilities/distribution/
namespace: global
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/distribution/
    - capabilities/delivery/
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/
    - packages/devkit-catalog/src/devkit_catalog/deep_research/
  excludes:
    - packages/devkit-adaptive/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-lightweight-general-subagent] Lightweight general subagent for role-file delegation

## 1. Background & Hypothesis

`ADR-skill-local-research-roles` keeps deep-research's four role documents inside the skill and has the coordinator
spawn a general subagent with the selected role file path (`CAP-DLV-deep-research` rules 1 and 11). The ADR avoids
registering research roles because registered descriptions are visible outside the explicit invocation.

On Claude Code the general subagent is the built-in `general-purpose` type, which receives every tool (`tools: *`).
Five recent `general-purpose` children in this repository started with 35,986 to 36,133 input tokens on their first
call, while the Host's prompt was 2,570 to 3,006 characters (about 1k tokens). The roughly 35k-token remainder is
fixed load: the base system prompt, every tool schema (including MCP, Artifact and Workflow tools), the skill listing
and the project instruction files. Only the instruction files (about 3.5k tokens) are expected to stay.

A registered subagent costs the Host one listing line (name, description, tools) until it is spawned; its body loads
only for the child. A single registered subagent with a neutral name and description therefore keeps explicit-only
skills unadvertised, while a restricted tool list removes most of the fixed load.

**Hypothesis**: a registered general subagent limited to `Read, Grep, Glob, Bash, Edit, Write, WebSearch, WebFetch,
Agent` starts with substantially fewer first-call input tokens than `general-purpose`, and deep-research's four roles
complete their assignments with that tool list.

## 2. Technical Spike Questions

- **Q1**: How many first-call input tokens does the restricted subagent use on Claude Code compared with the measured
  ~36k of `general-purpose`, and how much of the difference comes from the `Agent` tool's schema, which lists every
  available agent type?
- **Q2**: Do the four deep-research roles (`direction-explorer`, `discovery-critic`, `discovery-planner`,
  `research-investigator`) need any tool outside the list, such as an MCP knowledge source?
- **Q3**: What are the Codex and Antigravity host blocks? Codex exposes `sandbox_mode` but no tool allowlist, so the
  token reduction may be Claude Code only; the contract needs a status (`native` or `emulated`) per host.
- **Q4**: Which name? `lean` is already a subagent model level in the glossary (`ADR-subagent-levels`), so
  `lean-worker` could be read as a model level. Candidates: `lean-worker`, `general-worker`, `role-worker`.
- **Q5**: Should `adaptive-dev`'s `swarm-worker` be reused instead? It already has a similar Claude Code tool list,
  but its contract is implementation-specific (commit authority, owned assignment) and `devkit-adaptive` is not
  always installed.

## 3. Proposed Design & Impact

- **New subagent asset** in `devkit-dist`'s `devkit` bundle, added to its `core` preset. The bundle declares
  `auto_select = true` and `devkit-dist` provides the `devkit` executable, so every project that syncs any bundle
  receives it unless the owner opts out with `devkit = false`. `bundle.toml` has no bundle-to-bundle dependency key,
  and none is added.
- **Role contract** (`subagents/<name>.md`):
  - Name and description stay neutral and name no skill, bundle or research role.
  - `level` is omitted, so the model is inherited (`CAP-DIST-agent-projections` §3 rule 1).
  - `claude-code`: `tools: [Read, Grep, Glob, Bash, Edit, Write, WebSearch, WebFetch, Agent]`; no MCP, Artifact,
    Workflow or Skill tools.
  - The body says to read the role file the prompt names first and follow it as the assignment contract. It
    re-delegates only independent work, preferring this subagent or a fitting dedicated one over `general-purpose`.
    Markdown is not a permission boundary.
- **Deep research**: `SKILL.md` step 4 and `references/orchestration.md` spawn the new subagent instead of a
  general subagent, with no fallback.
- **Living Spec**:
  - Revise `CAP-DLV-deep-research` rule 11.
  - Add the asset to `CAP-DIST-agent-projections` or the `devkit` bundle description where bundle contents are listed.
  - Record a PADR that supersedes in part `ADR-skill-local-research-roles` (the "general subagent" clause only).
    Rule 1 (no registered research subagents) remains, because the new subagent is not a research role.
- **Out of scope**: changing `general-purpose`, other bundles' delegation, and the spec bundle's dedicated
  subagents.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1 to Q5 with a measurement on Claude Code and records the subagent-name and ADR-supersession
  decisions as PADRs.
- On acceptance: `devkit spec proposal accept lightweight-general-subagent --by user`, then handoff to one
  `sdd-spec-feature` spec.
- On rejection: `status: rejected` with the user's reason in the commit message. Deep research keeps spawning a
  general subagent.
