---
id: FB-compacted-mcp-dismissed
title: MCP feedback, dismissed
summary: Model Context Protocol services and tool registration.
target: docs/capabilities/mcp/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-integration-approval-review-before-elicitation
---

# [FB-compacted-mcp-dismissed] MCP feedback, dismissed

## FB-integration-approval-review-before-elicitation

- **Symptom**: Automatic tool review rejects integration before native approval can be requested
- **Response**: Dismissed outcome
- **Reason**: dismissed. Pre-confirmation descriptions and fail-closed handling were already incorporated in `packages/devkit/src/devkit/integration/mcp.py`. The host reviewer's policy behavior of rejecting the dispatch prior to interactive elicitation is external to devkit repository control.
