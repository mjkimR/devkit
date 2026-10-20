---
id: FB-native-language-form-evidence-gap
title: Observe harmless bilingual terminal form fixtures
scope: repo
kind: suggestion
category: missing-capability
target: docs/materials/2026-10/20261020-language-setting-coverage/development-evidence.md
skill: spec-feedback
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-20
---

# [FB-native-language-form-evidence-gap] Observe harmless bilingual terminal form fixtures

## 2. Suggestion / Change Request

- **Current Procedure**: Domain and SDK fixtures verify supplied English/Korean content, canonical replies and
  unchanged authority, while native visible-form status remains explicitly unverified for both terminal hosts.
- **Proposed Procedure**: When an independently authorized native test surface is available, run a data-returning
  fixture in Codex CLI and Claude Code. Record exact client/server/SDK/protocol versions, requested message/schema,
  observed metadata omissions/transforms, canonical enum selection, boolean widget, accept/decline/cancel behavior,
  and client-owned buttons, validation and permission prompts. It must have no handoff, worktree, merge, push,
  cleanup or real trust/config mutation handler.
- **Expected Benefit**: Separate evidence of visible Korean rendering from protocol carriage, without overclaiming
  host support or using actual business actions as a UI test.
- **Cost & Risk**: Requires an observed native terminal surface and intentional fixture connection. Do not change
  real configuration/trust solely to gather evidence, or treat unavailable UI as approval.
- **Attempted**: Version inspection and SDK stdio/domain tests completed. No live native fixture was launched.

## Diagnostic Details

- **Reproduction**: Version commands returned Codex CLI 0.163.0 and Claude Code 2.1.304. SDK fixture messages and
  canonical replies passed in both languages; neither host's visible form was observed.
- **Expected / Actual**: Supplied content is verified; native displayed titles/descriptions/widgets remain unknown.
- **Versions**: devkit-mcp 0.1.1; MCP SDK 1.30.0; latest SDK protocol 2025-11-25.
- **Conditions**: Isolated Development worktree with emulated scope confinement, no observed native form surface.
- **Workarounds Attempted**: Retained per-host unverified status in `MAT-language-development-evidence` and canonical
  contracts. This allowed evidence gap does not defer an implementation requirement.
- **Related Assets**: `SPEC-language-setting-coverage`, `CAP-INT-mcp-services`, `CAP-DLV-proposal-incubation`.

## Evidence

```text
Codex CLI: 0.163.0
Claude Code: 2.1.304
MCP SDK: 1.30.0
Native visible form: unverified for each host
Domain/SDK tests: supplied message and schema/reply behavior verified
```
