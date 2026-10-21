---
id: FB-common-exclusion-policy-helper
title: Centralize common exclusion policy for independent local services
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-dist/src/devkit/host/registrations.py and packages/devkit-dist/src/devkit/shared/local.py
skill: spec-review
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-21
---

# [FB-common-exclusion-policy-helper] Centralize common exclusion policy for independent local services

## Suggestion

- **Current Procedure**: Host registration and artifact initialization independently discover worktrees, inspect tracked/visible paths, and coordinate through the literal common lock name devkit-mcp.lock.
- **Proposed Procedure**: Evaluate a core-owned exclusion policy helper with explicit directory/file semantics and a shared lock identity. Preserve both domains' existing authority and transaction rules.
- **Expected Benefit**: Make cross-service exclusion coordination explicit and reuse tests for negative-ignore and foreign-worktree cases.
- **Cost & Risk**: A shared helper must not weaken registration journaling or artifact refusal-without-writes behavior. This is follow-up design, not authorization to refactor either service now.
- **Attempted**: Source inspection and artifact regression tests only; no helper extraction was implemented.

## Diagnostic Details

- **Reproduction**: Compare registrations.clone_lock and shared.local._initialize; inspect both tracked/ignored worktree checks.
- **Expected / Actual**: Independent services serialize exclusion changes, but share their lock identity by repeated literal and maintain separate eligibility algorithms.
- **Versions**: devkit-dist 0.1.1 Development sources.
- **Conditions**: Same-user POSIX local stores under linked Git worktrees.
- **Workarounds Attempted**: Artifact code uses the existing common lock name and tests negative-ignore refusal before effects; registration code remains unchanged.
- **Related Assets**: `CAP-MCP-runtime-registration`, `CAP-COLL-shared-artifacts`.

## Evidence

```text
host/registrations.py: clone_lock uses common / "devkit-mcp.lock"
shared/local.py: _initialize uses common / "devkit-mcp.lock"
Independent review found absent-store negative-ignore and probe-filename safety gaps;
deterministic artifact regression tests were added and passed after the fixes.
```
