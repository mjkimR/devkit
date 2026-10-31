---
id: FB-compacted-integration-dismissed
title: Integration feedback, dismissed
summary: Worktree preparation and branch integration procedures.
target: docs/capabilities/integration/
status: dismissed
created_at: 2026-10-31
aliases:
  - FB-readiness-rule-api-change-undiagnosed
---

# [FB-compacted-integration-dismissed] Integration feedback, dismissed

## FB-readiness-rule-api-change-undiagnosed

- **Symptom**: Integration readiness reports a rule engine API change as a generic rules failure
- **Response**: dismissed by the user's decision
- **Reason**: this mismatch occurs exclusively when dogfooding devkit development inside this repository (modifying `BaseRule` / rule engine core APIs in a branch while running MCP from the base target), not in consumer repositories where devkit is an installed external package. For this rare dogfood scenario, the existing CLI merge route (`devkit worktree finish <branch> --merge --local-only` from the base checkout) is a sufficient and safe workaround without introducing additional engine diagnosis complexity.
