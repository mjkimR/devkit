---
id: FB-integration-approval-review-before-elicitation
title: Automatic tool review rejects integration before native approval can be requested
scope: unknown
kind: friction
category: instruction-conflict
target: devkit.integration.mcp integration_integrate and Codex automatic tool approval review
skill: spec
agent: codex
origin: user
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-18
---

# [FB-integration-approval-review-before-elicitation] Automatic tool review rejects integration before native approval can be requested

## 1. Friction / Question

- **Context**: Calling integration_integrate to obtain native confirmation for a prepared local integration.
- **Expectation**: The call reaches its native confirmation UI before any merge, worktree removal, branch deletion or scoped cleanup.
- **Actual**: Automatic tool review rejected the call before dispatch because explicit authorization for its eventual merge and cleanup effects was absent. The server therefore could not request that authorization through elicitation.
- **Workaround**: Explicit conversational authorization for the exact effects preceded a subsequent successful MCP confirmation and integration.
- **Suggestion**: Make the pre-confirmation validation, lack of integration mutations, fail-closed responses and exact approval binding explicit in the tool description. Keep destructive annotations accurate. Measure native behavior after refreshing the client connection; description changes alone are not established to resolve the host review outcome.

## Diagnostic Details

- **Reproduction**: Observed one automatic rejection before integration_integrate reached native elicitation.
- **Expected / Actual**: Expected a scoped native confirmation form; actual tool rejection cited missing explicit authorization for main integration, worktree/branch removal and proposal/scope cleanup.
- **Versions**: devkit-agt 0.1.1; automatic reviewer version unknown.
- **Conditions**: Codex automatic tool approval review with a local stdio MCP server and dev-integration ask policy.
- **Workarounds Attempted**: Conversational authorization followed by native elicitation succeeded. Updated server descriptions and pre-confirmation preservation pass real SDK protocol tests; the connected host still advertises old metadata until reconnection.
- **Related Assets**: packages/devkit/src/devkit/integration/mcp.py, packages/devkit/src/devkit/integration/service.py and packages/devkit/tests/integration/test_mcp.py.

## Evidence

```text
Automatic rejection: exact merge and cleanup side effects lacked explicit user approval.
No native form was reached on that call.
Later integration returned status completed, authority mcp-elicitation and ui_action accept.
Fresh SDK list_tools exposes the clarified description; the current host tool catalog still exposes the previous description.
```

- **Disposition**: dismissed. Pre-confirmation descriptions and fail-closed handling were already incorporated in `packages/devkit/src/devkit/integration/mcp.py`. The host reviewer's policy behavior of rejecting the dispatch prior to interactive elicitation is external to devkit repository control.

