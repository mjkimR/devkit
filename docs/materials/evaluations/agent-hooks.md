# Agent Runtime Hooks Evaluation

Historical evaluation of a path-scoped context advisor. The shared lifecycle hook foundation is now implemented
separately in [Host Integration](../../host/overview.md). That foundation does not adopt the proposed advisor,
cross-host support or its latency target. Statements below describe the original evaluation, not current support.

- **Status**: Not adopted. Evaluation record (2026-10-14), from a technical spike run on 2026-10-03 for specrig, the
  predecessor of devkit-spec.
- **Decision**: devkit ships no agent runtime hooks for now: no consumer needs them yet. Hosts support the mechanism,
  so devkit can add it when a concrete need appears; [section 6](#6-adoption-criteria) lists what to settle then.
- **Target Modules**: `devkit.distribution` (a new projected asset kind), a new advisor command.
- **Related Documents**: [Native Agent Projections](../../distribution/agent-projections.md),
  [Workspace Ownership](../../distribution/workspace-ownership.md), `ARCH-08-2-resource-taxonomy`,
  [Agent-First Output](../../architecture/ARCH-08-1-agent-output.md).

## 1. Objectives

devkit's checks run after the agent acts: `devkit rules check` after files change, gates at commit time. An agent
runtime hook runs before the agent acts. The evaluated use case is a **pre-action context advisor**: just before an
agent reads or edits a file under an area with its own principles (for example `src/domain/payment/` and an
idempotency ADR), the hook injects a one- or two-line hint naming the rule, so the mistake is avoided instead of being
found by a check afterwards.

A post-action check cannot do this: it runs when work is saved or committed and cannot know which file the agent is
about to open. The capability needs the agent host to intercept the tool call.

## 2. Host Support

| Host | Pre-action interception | Hint injection | Assessment |
| --- | --- | --- | --- |
| Codex CLI and runtime | `PreToolUse` intercepts Bash, `apply_patch`, MCP and other local function tools | `hookSpecificOutput.additionalContext` is added as developer context | Directly implementable |
| Claude Code (terminal, IDE, the Code sessions of Claude desktop and cloud) | `PreToolUse` runs before every tool call, matched by tool name (`Read`, `Edit`, `Write`) | `hookSpecificOutput.additionalContext` is added to Claude's context | Directly implementable |
| Antigravity | Not evaluated | Not evaluated | Check before adoption |
| ChatGPT chat and desktop chat | No documented user-defined `PreToolUse` contract for local file tools; MCP apps are tools the model calls, not middleware around built-in tools | None | Not a target |

- **Codex** reads project hooks from `.codex/hooks.json` or `.codex/config.toml` and runs them only after the user's
  trust review. The input carries `tool_name` and `tool_input`. Some special tool paths and hosted tools bypass hooks.
- **Claude Code** reads shareable project hooks from `.claude/settings.json`; the input carries `tool_name` and
  `tool_input` as in Codex, so one advisor core can serve both through two thin adapters.
- Other channels considered: editor file-event hooks (for example Kiro) and Language Server Protocol diagnostics.

Because hooks can be bypassed and depend on trust settings, they are an **advisory layer, never a security
boundary**. Enforcement stays with rules and gates.

Sources (as of the spike; recheck before adoption):
[Codex Hooks](https://learn.chatgpt.com/docs/hooks),
[OpenAI Plugin Packaging](https://developers.openai.com/plugins/build/plugins),
[Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks),
[ChatGPT Developer Mode and MCP Apps](https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt).

## 3. Design Sketch

1. A stateless `advise` command reads the host's hook JSON on stdin, resolves the target path from `tool_input`, and
   looks up hints attached to that path.
2. No hint: empty output, exit `0`. Otherwise at most two lines of `additionalContext`.
3. Each `(session, hint ID)` pair is injected once per session.
4. Per-host adapters are matcher configuration only: Codex matches `apply_patch`, filesystem MCP read tools and, if
   needed, `Bash`; Claude Code matches `Read|Edit|Write`.
5. Hint sources are bundle content already scoped by path (instructions, rule targets) or a new path-to-hint table;
   which one is an open question.

## 4. Constraints from devkit's Contracts

- **Host settings are off limits today.** devkit never touches host settings or trust configuration
  ([Native Agent Projections, section 2](../../distribution/agent-projections.md#2-projection-rules)). Hook
  registration lives in host settings files (`.claude/settings.json`, `.codex/config.toml`) or a host file next to
  them (`.codex/hooks.json`). Support needs an explicit decision: a projected, receipt-owned hook file per host, a
  narrowly owned entry inside a settings file, or a printed snippet the user installs.
- **Output contract.** The hook's stdout must be the host's JSON (`hookSpecificOutput`), not devkit sentinels. The
  advisor is a documented exception to [Agent-First Output](../../architecture/ARCH-08-1-agent-output.md), like any host-defined protocol.
- **Fail-open.** A failing or slow advisor never blocks the tool call; it records a diagnostic and exits cleanly.
- **Context budget.** Hints are capped at two lines and deduplicated per session to avoid crowding the context.
- **Latency.** The hook runs on every matched tool call. The spike set a p95 budget of 10 ms; a Python process start
  alone may exceed that, so the budget and the runtime (a resident process, a cache, or a shell fast path) are part
  of the adoption work.

## 5. Proof-of-Concept Contracts

- **Given** a target path under an area with a linked hint, **when** a read or edit tool is called, **then** the hint
  ID and its one-line summary are added to the model's context exactly once, before the tool runs.
- **Given** a target path with no linked hint, **when** a tool is called, **then** the hook returns empty output and
  exit code `0`.
- **Given** the hook process fails or times out, **when** a tool is called, **then** the call proceeds (fail-open) and
  only a diagnostic is recorded.
- **Given** the same hint was already injected in the session, **when** another file of the same area is called,
  **then** no duplicate hint is injected.

## 6. Adoption Criteria

Adopt when a consumer repository has path-scoped principles that agents repeatedly miss before acting, and a proof of
concept on Codex and Claude Code with one shared advisor core passes section 5 and measurably improves task outcomes.
Drop the idea if host coupling makes the adapters unportable or the hints distract the agent more than they help.

Open questions to settle at adoption:

- The ownership model for host hook files (section 4) and how `devkit sync`, `remove` and `status` treat them.
- The hint source and its asset kind in the `ARCH-08-2-resource-taxonomy`.
- Antigravity support, and whether a host without hooks gets a fallback such as instruction text.
- The latency budget and runtime.
