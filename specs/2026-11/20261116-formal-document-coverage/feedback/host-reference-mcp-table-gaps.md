---
id: FB-host-reference-mcp-table-gaps
title: Host reference MCP code table lacks MCP_REGISTRATION_PENDING and has two-column rows in a three-column table
scope: repo
kind: friction
category: docs-mismatch
target: docs/development/reference/host.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-host-reference-mcp-table-gaps] Host reference MCP code table lacks MCP_REGISTRATION_PENDING and has two-column rows in a three-column table

## 1. Friction / Question (friction, question)

- **Context**: Routing MCP symptoms to the host reference's code rows from a new operations entry.
- **Expectation**: Every MCP code the capability names has a row under the reference's MCP services table, each with the table's columns.
- **Actual**: `MCP_REGISTRATION_PENDING` (`CAP-MCP-runtime-registration`, withheld registration writes) has no row; the rows from `MCP_RUNTIME_STALE` to `HOST_MCP_ARGUMENT_INVALID` have two cells in a three-column table; no row has an anchor.
- **Workaround (or Interpretation Chosen)**: The operations entry routes that code to the capability section and links the table heading.
- **Suggestion**: Add the missing row and align the row cells.

## Diagnostic Details

- **Reproduction**: Read-only reading of the reference and capability.
- **Expected / Actual**: A row per capability code.
- **Versions**: repository head of the formal-document-coverage Development branch.
- **Conditions**: not applicable
- **Workarounds Attempted**: not attempted
- **Related Assets**: docs/development/reference/host.md, CAP-MCP-runtime-registration

## Evidence

```text
rg MCP_REGISTRATION_PENDING docs/development/reference/host.md -> no match
CAP-MCP-runtime-registration: locked sync returns MCP_REGISTRATION_PENDING
```

## Disposition

- **Disposition**: Resolved in SPEC-remaining-feedback-fixes: the host reference MCP services table gives every row a Level and mode cell and adds the MCP_REGISTRATION_PENDING NOTICE row; rows stay without anchors, like every other table in that file.
