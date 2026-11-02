---
id: FB-stale-approval-form-clause
title: ADR approval-form text rules describe the removed MCP confirmation channel
scope: repo
kind: change-request
category: docs-mismatch
target: ADR-configuration-language-and-rendering
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-02
---

# [FB-stale-approval-form-clause] ADR approval-form text rules describe the removed MCP confirmation channel

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ADR-configuration-language-and-rendering` still sets rules for MCP confirmation forms. It
  requires every choice to be explained even when the host omits schema metadata, provider text to be shown verbatim,
  and local text to keep "native approval routes". Two later commits removed the MCP-native approval paths and the
  confirmation channel.
- **Proposed Procedure**: Retire those clauses through a new ADR that partially supersedes the ADR, as
  `ADR-retire-scheduled-roadmap-review` did for the roadmap review. The still-valid part, domain-owned static English
  and Korean copy, is already restated in `CAP-DIST-sync-and-transactions` and `CAP-DLV-proposal-planning`.
- **Expected Benefit**: The accepted ADRs stop describing an interface that no longer exists.
- **Cost & Risk**: Low; it changes no behavior.
- **Attempted**: Hypothesis. `SPEC-adr-normative-outcomes` left these clauses unmarked and did not restate them.

## Diagnostic Details

- **Reproduction**: `rg "ctx.elicit|elicit\(" packages/` finds nothing.
- **Expected / Actual**: Expected an approval form to exist; observed that it was removed.
- **Versions**: base `fceda9d2`; removal commits `2a491881`, `8f570521`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: none.
- **Related Assets**: `ADR-host-cli-lifecycle-authority`, `CAP-INT-mcp-services`.

## Evidence

```text
CAP-INT-mcp-services states that ADR-host-cli-lifecycle-authority superseded the native confirmation interface; under
`ask` the Host presents the scope in conversation.
```
