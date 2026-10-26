---
id: FB-adoption-usecase-confirmed-offer
title: Adoption use case omits the confirmed intake offer
scope: repo
kind: change-request
category: docs-mismatch
target: UC-adopt-in-an-existing-repository
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-adoption-usecase-confirmed-offer] Adoption use case omits the confirmed intake offer

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `UC-adopt-in-an-existing-repository` step 5 says the developer asks the agent for the
  `brownfield-adoption` playbook. Since `SPEC-spec-playbook-discovery`, the playbook's prerequisite reads "the user
  invoked or confirmed this playbook", and `spec` intake can offer it for a request such as "how do I adopt devkit
  here?" (`ADR-spec-intake-playbook-discovery`).
- **Proposed Procedure**: step 5 and the matching scenario Given add "or confirms the one-line offer `spec` intake
  makes", as `UC-reconcile-living-spec-drift` and `UC-inspect-weekly-repository-progress` already state for the
  maintenance playbooks.
- **Expected Benefit**: the adoption flow reads like the maintenance flows for the same entry mechanism.
- **Cost & Risk**: one use case edit; none to behavior.
- **Attempted**: not edited: `docs/usecases/harness/` was outside the write scope of the Development run.
- **Restart condition and acceptance**: the integration of `SPEC-spec-playbook-discovery` when the Host widens the
  docs scope, or the next change touching the use case; done when step 5 names the confirmed offer and
  `devkit rules check docs/usecases` passes.

## Evidence

```text
UC-adopt-in-an-existing-repository step 5: "The developer asks the agent for the brownfield-adoption playbook".
brownfield-adoption Prerequisites: "The user invoked or confirmed this playbook; that invocation authorizes the moves."
```

## Disposition

Resolved at the integration of `SPEC-spec-playbook-discovery`: `UC-adopt-in-an-existing-repository` step 5
and scenario 4 name the confirmed one-line offer `spec` intake makes beside the explicit request.
