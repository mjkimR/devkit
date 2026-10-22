---
id: FB-remote-shared-adapter-follow-up
title: Track a concrete remote shared artifact adapter
scope: repo
kind: suggestion
category: missing-capability
target: devkit.shared public adapter protocol and registration contract
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-21
---

# [FB-remote-shared-adapter-follow-up] Track a concrete remote shared artifact adapter

## 2. Suggestion / Change Request

- **Current Procedure**: `SPEC-worker-shared-state-mcp` delivers local artifacts and a public remote extension
  protocol/registration contract. A local store or test adapter cannot share reports between independent hosts.
- **Proposed Procedure**: Preserve this item through handoff and promote it to a separate concrete remote artifact
  adapter Backlog proposal when cross-host consumption is needed. Do not implement a backend as incidental scope.
- **Expected Benefit**: Keeps deferred cross-host behavior discoverable without claiming that protocol support is
  production support; provider-specific decisions receive their own acceptance and evidence.
- **Cost & Risk**: Provider dependencies, authentication, namespace authorization, deployments and operating costs
  remain unsettled. No service or credentials are configured by this record.
- **Attempted**: Repository evidence and Planning comparison only; no production remote adapter was built or tested.

## Dependencies and Restart Criteria

Destination: a new Backlog proposal for one concrete remote shared artifact adapter. Start when an identified
cross-host consumer needs shared reports, the public protocol/conformance suite is available, and a provider,
authentication method, repository namespace provisioning owner and integration test environment can be selected.
The new Planning must settle atomic create/live-retry semantics, generation expiry and cleanup, concurrent CLI
access across hosts, authorization isolation, endpoint configuration, observability and operating cost. Its
acceptance evidence must use the real backend across separate hosts; a protocol fake is insufficient. Remote
scope-registry coordination remains separate because artifact storage grants no ownership or write authority.

## Diagnostic Details

- **Reproduction**: Inspect the proposal's selected local-first option, artifact protocol and AC6.
- **Expected / Actual**: Extension availability is testable now; actual cross-host sharing needs an installed and
  configured production adapter that this delivery excludes.
- **Versions**: Planning based on worktree start d0c4428c01650ada6069606e6c340e9f065c16fa.
- **Conditions**: Independent hosts lack a common local filesystem; local linked worktrees do not have this gap.
- **Workarounds Attempted**: Selected local adapter for immediate review-report consumer; no remote workaround run.
- **Related Assets**: `SPEC-worker-shared-state-mcp`, `SPEC-proposal-review-and-approval`,
  `CAP-COLL-work-scope-registry` and the planned devkit.shared adapter authoring reference.

## Evidence

```text
worker-01 question remote-first-delivery: a protocol/test adapter cannot provide cross-host cloud sharing.
answer-01 decision: local adapter plus public remote adapter protocol/registration; concrete backend deferred.
proposal AC6: test adapter conformance explicitly does not constitute remote production evidence.
```

- **Disposition**: dismissed. `CAP-COLL-shared-artifacts` states that local storage provides no cross-host sharing, and a cross-host attempt is refused at once (a URI from another namespace fails in `get`; cloud refuses `shared_put`), so the need surfaces when it arises; no current consumer reads reports across hosts. A concrete remote adapter starts as its own proposal when one does.
