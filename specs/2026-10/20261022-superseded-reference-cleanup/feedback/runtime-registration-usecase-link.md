---
id: FB-runtime-registration-usecase-link
title: The integration use case cites CAP-MCP-runtime-registration without a trace link
scope: repo
kind: suggestion
category: missing-capability
target: CAP-MCP-runtime-registration
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-runtime-registration-usecase-link] The integration use case cites CAP-MCP-runtime-registration without a trace link

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: Extension 7g of `UC-drive-development-to-integration` cites `CAP-MCP-runtime-registration`
  for the `MCP_RUNTIME_STALE` recovery, but the use case's `capabilities:` list does not name it, and the
  capability's `usecases` list does not name the use case.
- **Proposed Procedure**: Add `CAP-MCP-runtime-registration` to the use case's `capabilities:` and
  `UC-drive-development-to-integration` to the capability's `usecases` in one change, so `RULE-traceability-link`
  holds for the pair.
- **Expected Benefit**: `devkit spec refs` and the viewer show the use case among the capability's consumers, and a
  change to the stale-runtime contract finds the use case that restates its recovery.
- **Cost & Risk**: Two frontmatter lines; none beyond the rules check.
- **Attempted**: Tested: adding only the use case side fails `RULE-traceability-link`
  (`CAP-MCP-runtime-registration.md does not list UC-drive-development-to-integration in usecases`); capability files
  were outside the write scope of `SPEC-superseded-reference-cleanup`.

## Diagnostic Details

- **Reproduction**: Add `- CAP-MCP-runtime-registration` to the use case's `capabilities:` and run
  `uv run devkit rules check docs/usecases/delivery/UC-drive-development-to-integration.md`.
- **Expected / Actual**: Exit 0 once both sides list each other / one `RULE-traceability-link` error with one side only.
- **Versions**: devkit worktree on `dev-superseded-reference-cleanup`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: The use case cites the capability in the extension text only.
- **Related Assets**: `UC-drive-development-to-integration`, `CAP-MCP-runtime-registration`,
  `RULE-traceability-link`.

## Evidence

```text
[VIOLATION: RULE-traceability-link severity=error file=docs/usecases/delivery/UC-drive-development-to-integration.md
 line=20 ... message="UC-drive-development-to-integration links CAP-MCP-runtime-registration, but
 docs/capabilities/mcp/CAP-MCP-runtime-registration.md does not list UC-drive-development-to-integration in usecases"]
```
