---
id: PROP-lightweight-general-subagent
title: Lightweight general subagent for role-file delegation
summary: "Add a neutral, tool-limited role-worker subagent to the auto-selected devkit bundle and route skill-local role-file delegation to it, so role children start without the full general-purpose tool and skill context."
status: reviewing                         # draft | reviewing | accepted | rejected
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
    - capabilities/harness/
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/
    - packages/devkit-catalog/src/devkit_catalog/deep_research/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/src/devkit_catalog/design_explore/
    - packages/devkit-catalog/tests/
    - packages/devkit-dist/tests/
    - packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/skill-authoring/
  excludes:
    - packages/devkit-adaptive/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
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

Three other assets use the same pattern: app-uiux-improve's and design-explore's `references/orchestration.md` pass a
role file to a general subagent, and the skill-authoring playbook's `references/roles.md` tells authors to do so for
every skill-local role.

**Hypothesis**: on Claude Code, a registered `role-worker` subagent limited to `Read, Grep, Glob, Bash, Edit, Write,
WebSearch, WebFetch, Agent` starts with a median first-call input of at most 18k tokens, against about 36k for
`general-purpose` on the same machine and Claude Code version, and the role-file callers' roles complete their
assignments with that tool list. The gain grows with the host's tool set (MCP servers, skills); a consumer with few
MCP servers gains less.

## 2. Technical Spike Questions

- **Q1** (answered): neighbours with the same tool shape start at about 15k tokens; `development-worker` and
  `planning-worker` carry `Agent` and stay at about 15k, so the `Agent` listing costs at most a few thousand tokens
  ([first-call-tokens.md](materials/first-call-tokens.md)).
- **Q2** (partly answered): the four deep-research roles read sources, use the web, run authorized experiments with
  Bash and write scratch notes; the tool list covers them. app-uiux-improve's `designer` and `critic` may inspect a
  running UI, which on Claude Code goes through a browser MCP server outside the list (`SKILL.md:36-37`). Open
  decision D3.
- **Q3** (answered): host blocks follow `swarm-worker`. `claude-code` is `native` with the tool list; `codex` is
  `emulated` with `sandbox_mode: workspace-write` and has no tool allowlist, so it gains no token reduction;
  `antigravity` is `unverified` with `view_file, grep_search, replace_file_content, run_command`. No block is
  `unsupported`, so every selected host receives a projection.
- **Q4** (answered): `swarm-worker` is not reused. Its contract carries commit authority and an owned implementation
  assignment, and `devkit-adaptive` is not always installed.

## 3. Proposed Design & Impact

- **New `role-worker` subagent asset**, auto-selected through `devkit-dist` (placement: open decision D1). Every project
  that syncs any bundle receives it unless the owner opts out with `devkit = false`. `bundle.toml` has no
  bundle-to-bundle dependency key, and none is added.
- **Role contract** (`subagents/role-worker.md`):
  - The name `role-worker` is the user's decision: it names the role-file pattern, names no skill, bundle or
    research role, and avoids the `lean` subagent model level (`ADR-subagent-levels`). The description stays
    equally neutral.
  - `level` is omitted, so the model is inherited (`CAP-DIST-agent-projections` §3 rule 1). Host blocks as in Q3.
  - The body says to read the role file the prompt names first and follow it as the assignment contract; without a
    named role file, it treats the prompt as the assignment. It re-delegates only independent work, preferring
    `role-worker` or a fitting dedicated subagent over `general-purpose`. Markdown is not a permission boundary.
- **Role-file callers** spawn `role-worker` instead of a general subagent, with no fallback. When `role-worker` is
  not available (`devkit = false` or a host without the projection), the caller stops that delegation and reports the
  missing subagent and its cause instead of spawning another type:
  - deep-research: `SKILL.md` step 4 and `references/orchestration.md`;
  - app-uiux-improve: `references/orchestration.md`;
  - design-explore: `references/orchestration.md` (open decision D2);
  - skill-authoring playbook: `references/roles.md` directs new skill-local roles to `role-worker`.
- **Living Spec**:
  - `CAP-DLV-deep-research` rule 11, `CAP-DLV-uiux-improvement`, `CAP-DLV-design-exploration` (with D2) and
    `CAP-HARN-agent-guidance` where they name a general subagent.
  - `CAP-DIST-agent-projections` or the owning distribution capability lists `role-worker` with its host statuses.
  - One PADR supersedes in part `ADR-skill-local-research-roles` (the "general subagent" clause only; rule 1, no
    registered research subagents, remains) and, under D1 option (a), the `devkit`-bundle clause of
    `ADR-package-ownership-and-release-version`.
- **Tests**:
  - Update `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py:146` ("general subagent") and the
    matching app-uiux-improve and design-explore assertions.
  - Under D1 option (a), update `packages/devkit-dist/tests/integration/features/distribution/test_guide_bundle.py`,
    which asserts the `devkit` bundle holds instructions only.
  - Add a devkit-dist integration test that syncs the owning bundle and asserts the `role-worker` projection for all
    three hosts with their statuses and the Claude Code `tools` list.
- **Manual check** (Development, review evidence, not a test): with the method of
  [first-call-tokens.md](materials/first-call-tokens.md), at least five `role-worker` children have a median
  first-call input of at most 18k tokens, compared with a `general-purpose` sample from the same machine and Claude
  Code version.
- **Out of scope**:
  - `general-purpose` itself;
  - the spec bundle's dedicated subagents;
  - `sdd-overall-refactor`'s general subagents for parallel drafting, edits and research, which carry no role file;
  - adaptive-dev's skill-local builder role (`delegation.md`), whose child holds commit authority and worktree
    ownership; `roles.md` names it as the exception.

## 4. Planning decisions

- Q1, Q3 and Q4 are settled as above; the Q3 host statuses and the no-role-file behaviour follow the
  `challenger-01` findings.
- Release notes mention the new projection files that every consumer receives on upgrade.

## 5. Open decisions

- **D1**: where `role-worker` lives, given that `ADR-package-ownership-and-release-version` limits the `devkit` bundle
  to distribution guidance with instructions only.
- **D2**: whether design-explore joins the callers.
- **D3**: how app-uiux-improve roles cover running-UI inspection without browser MCP tools.

## 6. Lifecycle & Retirement Criteria

- On acceptance: `devkit spec proposal accept lightweight-general-subagent --by user`, then handoff to one
  `sdd-spec-feature` spec.
- On rejection: `status: rejected` with the user's reason in the commit message. Role-file callers keep spawning a
  general subagent.
