---
id: FB-integration-mcp-glossary-and-actor-row
title: Glossary and actor table still describe integration through MCP
scope: repo
kind: change-request
category: docs-mismatch
target: docs/glossary.md (Integration MCP), ARCH-04-1-ecosystem-boundaries
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-integration-mcp-glossary-and-actor-row] Glossary and actor table still describe integration through MCP

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the glossary entry **Integration MCP** defines a "Scoped Model Context Protocol server
  exposing devkit integration services", and the `ARCH-04-1-ecosystem-boundaries` role-to-actor table gives
  integration to the "Local Host via MCP". `CAP-INT-mcp-services` states that the lifecycle tools
  `integration_prepare`, `integration_integrate`, `integration_status` and `integration_resume` are not registered;
  integration runs through the Host-authorized `devkit integration` CLI.
- **Proposed Procedure**: replace or retire the glossary term (for example a **Scoped CLI integration** entry owned by
  `CAP-INT-mcp-services`) and change the actor row to the Host running `devkit integration`.
- **Expected Benefit**: an agent looking up the term does not expect integration tools that are not registered.
- **Cost & Risk**: two lines; a glossary term change may need a synonym in `docs/glossary.yaml`.
- **Attempted**: not edited: outside the 22 findings of `SPEC-living-spec-consistency-sweep` (found by its code
  review, finding 5 of `review-01.yaml`).

## Diagnostic Details

- **Reproduction**: `rg -n "Integration MCP" docs/glossary.md`; `rg -n "via MCP" docs/architecture/ARCH-04-1-ecosystem-boundaries.md`.
- **Expected / Actual**: CLI integration / MCP integration.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-INT-mcp-services`, `ADR-host-cli-lifecycle-authority`.

## Evidence

```text
docs/glossary.md: | **Integration MCP** | Scoped Model Context Protocol server exposing devkit integration services to coding agents. |
CAP-INT-mcp-services: The lifecycle tools integration_prepare, integration_integrate, integration_status and integration_resume are not registered.
```
