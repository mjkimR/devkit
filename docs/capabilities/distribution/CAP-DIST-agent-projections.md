---
id: CAP-DIST-agent-projections
title: "Native Agent Projections"
summary: "Projects role contracts and opt-in model levels into native Claude Code, Codex and Antigravity files, with inherited defaults and project mappings."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/subagents.py
  - packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/inventory.py
created_at: 2026-10-17
---

# [CAP-DIST-agent-projections] Native Agent Projections

Skills and subagents are projected into each selected agent's own directories. Every supported agent
(`codex`, `claude-code`, `antigravity`) is a target unless `agents` in `.devkit/config.toml` narrows the list; the
flags that set it are in the [reference](../../development/reference/distribution.md#sync-options), and `devkit bundle plan <source> --agent <name>`
previews the projections of a bundle before it is installed.

## 1. Projection Matrix

| Agent | Kind | Destination | Source |
| --- | --- | --- | --- |
| `codex` | `skill` | `.agents/skills/<asset-id>/` | `source` or `variants.codex` directory |
| `codex` | `subagent` | `.codex/agents/<asset-id>.toml` | `variants.codex` `.toml` file, or the contract's `hosts.codex` block |
| `claude-code` | `skill` | `.claude/skills/<asset-id>/` | `source` or `variants.claude-code` directory |
| `claude-code` | `subagent` | `.claude/agents/<asset-id>.md` | `variants.claude-code` `.md` file, or the contract's `hosts.claude-code` block |
| `antigravity` | `skill` | `.agents/skills/<asset-id>/` | `source` or `variants.antigravity` directory |
| `antigravity` | `subagent` | `.agents/agents/<asset-id>.md` | `variants.antigravity` `.md` file, or the contract's `hosts.antigravity` block (rendered with `subagent: true`, `mainAgent: false`) |

Instructions, playbooks, documents and role contracts are not projected; they stay under `.devkit/managed/<bundle>/`
and are reached through `get-context`, playbook search or their paths.

## 2. Projection Rules

- **Skills**: the whole directory, supporting files and executable bits (`0755`) included. A skill with `variants`
  and no `source` gets no projection for an agent it has no variant for, reported like a subagent below
  (`ASSET_UNPROJECTED`). One skill directory has one owner: two bundles shipping a skill of the same id are a
  `BUNDLE_CONFLICT` even when their files agree.
- **Skill templates**: `.md.jinja` files, including `SKILL.md.jinja`, render with resolved bundle variables and the canonical execution environment to
  `.md` before context prerequisites and native invocation settings are inserted. Projections contain rendered
  files only; plain Markdown stays literal. Rendered entry frontmatter and project overrides follow
  `CAP-DIST-manifest-spec`.
- **Skill invocation**: a skill declared with `invocation = "user"` gets each agent's native "explicit invocation
  only" setting in its projections; the managed copy omits native invocation settings. Claude Code: `SKILL.md` gains
  `disable-model-invocation: true` as the last frontmatter key (a frontmatter block is added when the file has
  none). `.agents/skills/` (Codex, shared with Antigravity): `agents/openai.yaml` gains
  `policy.allow_implicit_invocation: false`, appended to a shipped file that has no `policy` (its bytes are kept),
  written into its `policy` mapping otherwise (the file is re-serialized), or generated when the skill ships none.
  Antigravity has no such setting and follows the skill body. `auto` skills receive no native invocation setting.
- **Shared directory**: Codex and Antigravity both read `.agents/skills/`. Identical projections for both
  (including the generated `devkit-playbook` and `devkit-workflow` skills) are written once and stay while either
  agent is selected; differing bytes for one path are a collision error, so `codex` and `antigravity` skill
  variants of one asset must be identical (checked by `devkit bundle validate`).
- **Native subagents** (`variants`): one native file per supported agent, copied verbatim (`.toml` for Codex, `.md`
  for Claude Code and Antigravity). Native variants do not support templates. No conversion or key stripping: an agent without a variant gets no projection,
  and `devkit sync` reports it under `unprojected` and as an `ASSET_UNPROJECTED` notice (remedies: add the
  variant, ship a role contract, or narrow `agents`).
- **Role contracts** (`source`): one host-neutral Markdown file, optionally an explicit `.md.jinja` template, whose `hosts` table holds an explicit block per agent. Templates render and validate before any projection, including with no selected agents. Managed output and cited contract paths use final `.md` names; overrides retain raw template provenance. The projection is rendered deterministically from that block and its resolved model level (frontmatter keys for Claude Code and
  Antigravity, TOML keys plus `developer_instructions` for Codex), and the prompt is prefixed with the contract's
  managed path, its procedure skill and the host status. Only the host's allowlisted keys are accepted, a host with
  `status: unsupported` gets no file, and a contract that does not name every agent is invalid (`BUNDLE_INVALID`
  from `devkit bundle validate` and discovery). `emulated` and `unverified` projections tell the agent that the host
  does not enforce the boundaries itself.
- **Host configuration boundary**: selected `hook` assets manage only their receipt-recorded matcher groups in
  `.codex/hooks.json` (`CAP-HOST-lifecycle-observation`); foreign entries are
  preserved. devkit never touches other host settings, credentials, trust configuration or user-level instruction files. Outside `.devkit/` and the agent directories it writes only the guidance block of the root
  `AGENTS.md` and seeded files (`CAP-DIST-workspace-ownership`);
  `CLAUDE.md` is never written.

### Role Contract Format

```markdown
---
role: reviewer                      # equals the asset id and the projected file name
title: Reviewer
description: Reviews a change against its specification and returns findings with evidence.
skill: review                       # optional: the procedure the role executes
level: deep                         # optional: inherit | light | standard | deep; conflicts with native model/effort
hosts:
  claude-code:
    status: native                  # native | emulated | unsupported | unverified
    tools: [Read, Grep, Glob]       # allowed: tools, disallowedTools, model, permissionMode, maxTurns,
                                    #   skills, memory, background, omitClaudeMd, effort, isolation, color
  codex:
    status: emulated
    sandbox_mode: read-only         # allowed: model, model_reasoning_effort, sandbox_mode
  antigravity:
    status: native
    tools: [view_file, grep_search] # allowed: tools, model, commandExecutionPolicy, skills, plugins
    commandExecutionPolicy: "off"
---
# Reviewer
... the prompt, verbatim ...
```

Values are strings, integers, booleans or lists of strings. The rendered `description` (`<title>. <description>`)
is a quoted scalar whose line breaks are escaped, never folded. Because every supported agent is a target by
default, a contract names all three hosts (`status: unsupported` for a host that gets no file). The contract
stays under `.devkit/managed/<bundle>/` and may be overridden like any asset. Ordinary Markdown contracts cite
the override path when present. Templated contracts always cite their rendered managed `.md` file; raw override
provenance is recorded separately.

Keys of the form `x-<name>` (`x-[a-z][a-z0-9-]*`, any YAML value) are extension keys for tools built on devkit
(for example `x-model-profile`, `x-git-actions`). devkit validates only their shape, never renders or interprets
them; they stay readable in the managed copy and in `read_contract(...).extensions`. Any other unknown key is
rejected.

## 3. Subagent Model Levels

1. **Default inheritance**: WHEN a common contract has no explicit level or project selection, devkit MUST retain
   authored native model/effort fields; contracts without those fields inherit through the host's native rules.
   `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`.
2. **Source conflicts**: IF an explicit source `level` is combined with native `model`, `effort` or
   `model_reasoning_effort` in any host block, THEN validation MUST reject it with `BUNDLE_INVALID`.
   `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`.
3. **Explicit resolution**: WHEN a level is explicitly selected, devkit MUST replace only model/effort fields
   with its resolved settings; `inherit` removes both fields. `level` is not emitted as a native field.
   `packages/devkit-dist/tests/unit/features/distribution/test_subagent_levels.py`.
4. **Variant boundary**: WHERE a subagent ships native variants, devkit MUST preserve their bytes and skip global
   level selection; a role-specific override in a selected bundle is `CONFIG_INVALID`, including an excluded asset.
   Unsupported host blocks still emit no file. `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`.

| Subagent model level | Claude Code model / effort | Codex model / effort | Antigravity model |
| --- | --- | --- | --- |
| `inherit` | omit / omit | omit / omit | omit |
| `light` | `haiku` / `low` | `gpt-6-luna` / `low` | `flash` |
| `standard` | `sonnet` / `medium` | `gpt-6.1-sol` / `medium` | `pro` |
| `deep` | `opus` / `high` | `gpt-6-astra` / `high` | `pro` |

Antigravity has no supported effort field. Multiple levels may share a native tier. Mappings are resource presets,
not quality or compute equivalences. Host defaults, provider alias resolution, invocation settings and organization
policy can override the requested runtime behavior. Omission does not guarantee the parent's exact effort on
Antigravity. Model/effort inheritance is independent of conversation-history inheritance.

`CAP-DIST-sync-and-transactions` defines shared project overrides, validation and precedence. Delivery
`activity-effort` remains procedural depth. Bundle plan uses built-in mappings and source levels without reading
project config. `ADR-subagent-level-projection` records this policy and its native-runtime limitations.
