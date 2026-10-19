---
id: ADR-codex-native-worker-execution
title: Codex workers use native invocation with emulated boundaries
summary: "Codex Planning and Development workers use native subagents with emulated contract boundaries, explicit worktree paths and command-scoped approvals. Refusal preserves truthful partial results and leaves recovery to the Host."
proposal: SPEC-codex-native-workers
status: accepted
created_at: 2026-10-19
---

# [ADR-codex-native-worker-execution] Codex workers use native invocation with emulated boundaries

- **Status**: Accepted
- **Date**: 2026-10-19

## 1. Context & Problem Statement

The current contracts mark Codex workers unsupported because default project writes do not include sibling
worktrees or shared Git administration. `MAT-codex-native-worker-evidence` demonstrates native invocation with
individual approved commands. Native spawning does not enforce a worker-specific path boundary. The caller still
validates the complete committed range under `ADR-worker-delivers-committed-result`.

## 2. Decision Drivers

Support the demonstrated mechanism, preserve host trust and approval controls, retain normal devkit worktrees,
and report partial failures truthfully. Keep the change sized to existing contracts and instruction tests.

## 3. Considered Options

| Option | Execution and access | Cost and limitation | Decision |
| --- | --- | --- | --- |
| Keep Codex unsupported | Host performs all work in direct mode | Discards demonstrated native execution with approved commands | Retain as runtime fallback only |
| Native subagent with emulated boundaries | Named projection or generic effective-contract loading, individual command approvals | Caller verifies boundaries; unavailable approvals can stop work | Recommended |
| Separate process worker | Process launcher, permission configuration and output capture | New lifecycle and settings work without a demonstrated need | Excluded |

## 4. Decision Outcome

Both worker contracts SHOULD declare Codex `status: emulated` and `sandbox_mode: workspace-write`. Their native
invocation mechanism is `collaboration.spawn_agent`; the status describes contract enforcement, not the existence
of native spawning. Workers inherit session reasoning effort and set no model or approval-policy key. Existing
rendering already supports these settings; changing the renderer/allowlist is unnecessary.

The caller SHOULD prefer the projected named role and pass only its payload. If it is unavailable, diagnose
projection/session-root availability separately from trust. A generic native subagent MAY read the effective
managed or override contract when host project-instruction loading is permitted; the payload identifies that
contract by absolute path and labels the call emulated. An explicit host trust restriction MUST NOT be bypassed by
a generic role, another tool or a settings edit. Role absence alone does not prove the root is untrusted. Missing
required capabilities select existing Host direct execution or `needs_input` for required isolation before spawning.

Every worker command MUST set its cwd to the absolute worktree path and every Git command MUST use
`git -C <worktree>`. Absolute paths also apply to nested-role read scopes. The default cwd may be the base checkout.
Scratch files remain in an ignored path inside the worker's allowed unit/worktree boundary. The prompt and caller
diff checks enforce the task boundary; `workspace-write` is not per-worker confinement and Git administration is shared.

When an operation needs access beyond the active sandbox, the worker MUST request a command-scoped approval with
its exact operation, target and justification. This includes sibling files, shared Git index/commit administration,
registry writes and verification requiring unavailable network access. No broad persistent prefix, host settings
change or success-based grant is introduced. An approved call authorizes that operation only; safe optional checks
are diagnostics, never access promises for the next call.

On unavailable or refused approval the worker MUST stop that operation and preserve the actual result. It SHOULD
write its failed worker record and emergency commit through still-permitted, scoped operations. It MUST NOT retry a
denied action with an alternate tool, path, process or broader request to evade refusal. A command that failed for
another cause can be retried only after the cause/input changes and authorization permits it. Only an ordinary
commit-gate refusal permits the existing emergency `--no-verify` exception; approval or filesystem denial does not.

If the record or emergency commit also cannot run, the worker MUST return `failed` to the Host with the cause,
commands tried, recommended recovery, actual last commit SHA, dirty paths and which record/commit is absent or
uncommitted. It MUST NOT invent a committed envelope, clean tree or final HEAD containing the record. The Host
blocks acceptance and owns a subsequent recovery run and its records. The existing clean committed range remains
the successful-worker contract; failure reporting does not weaken it.

Keep the one-shot worker lifecycle, normal sibling worktrees, mandatory nested roles, stage gates, one worker record
per run and Host cumulative range validation. No bounded-turn mechanism is required; retire that requirement from
the replaced process-worker direction. Claude Code metadata/behavior stay unchanged; Antigravity stays unverified.

## 5. Consequences

Codex roles become projected by normal sync and can use tested native mechanisms where scoped approvals work.
Approval refusal and inability to preserve a committed result remain visible failure modes. Deterministic contract
and projection tests cover the instruction branches; this Planning run and the integrated Development run supply
live generic-role execution evidence. Named-role loading and denied approvals have not been live validated, and no
general host/version or persistent-grant guarantee follows. The Host validates this Planning return before
`plan-accept`; promotion follows normal handoff only after user acceptance.
