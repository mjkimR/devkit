---
id: FB-subagent-followup-failure-lacks-diagnostic
title: Failed subagent continuation exposes no diagnostic
scope: upstream
kind: friction
category: tool-error
target: collaboration.followup_task
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-29
---

# [FB-subagent-followup-failure-lacks-diagnostic] Failed subagent continuation exposes no diagnostic

## 1. Friction / Question

- **Context**: A matched model probe reused an already-completed subagent for a second research turn.
- **Expectation**: Continuation either returns the requested result or an actionable failure cause.
- **Actual**: The lightweight agent returned only a generic turn-failed message, without a diagnostic or stable code.
- **Workaround**: A changed follow-up supplied the same cases inline and removed the input-file read. It completed.
  This does not identify the cause and was recorded as a delivery failure, not a model reasoning error.
- **Suggestion**: Surface the failure category, correlation identifier and whether retry is appropriate so callers
  can distinguish context, tool, model-service and permission failures without guessing.

## Diagnostic Details

- **Reproduction**: First continuation after a successful six-case response and live read-only probe failed once.
  A controlled reproduction was not attempted.
- **Expected / Actual**: Expected structured failure evidence; received generic text only.
- **Versions**: Codex host on 2026-10-29; exact host build unknown. Requested model gpt-6-luna.
- **Conditions**: Same agent identity, completed first turn, follow-up requested a file read and JSON response.
- **Workarounds Attempted**: New inline-input follow-up completed; causality unknown.
- **Related Assets**: collaboration.followup_task; model-probe-results.json in the current proposal materials.

## Evidence

```text
This agent's turn failed. If you still need this agent, use the available collaboration tools to give it another task.
```
