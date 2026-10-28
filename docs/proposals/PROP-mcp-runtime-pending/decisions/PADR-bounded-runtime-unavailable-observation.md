---
id: PADR-bounded-runtime-unavailable-observation
title: Bound provider-free runtime-unavailable observations
summary: "For provider-free registration status, we retain a negative runtime observation for at most 300 seconds with input invalidation, to avoid repeated unhelpful fixes, accepting bounded stale suppression after unobserved runtime repairs."
proposal: PROP-mcp-runtime-pending
status: draft
created_at: 2026-10-28
---

# [PADR-bounded-runtime-unavailable-observation] Bound provider-free runtime-unavailable observations

## 1. Context & Problem Statement

`CAP-MCP-runtime-registration` keeps status provider-free. A missing local registration can therefore report
`MCP_REGISTRATION_PENDING` while the registration attempt returns `MCP_RUNTIME_UNAVAILABLE`.
`ADR-mcp-runtime-and-shared-artifacts` assigns retained runtime selection and requirements to the optional provider.
Dist cannot establish a complete runtime fingerprint from metadata without duplicating that selection logic.

## 2. Decision Drivers

- Suppress retries that the same observed runtime absence cannot satisfy.
- Preserve provider-free, read-only status and the dist-only installation boundary.
- Bound stale suppression after runtime installation or repair.
- Keep advisory evidence separate from registration ownership and recovery authority.

## 3. Considered Options

1. Keep pending on every eligible missing registration. This preserves all current boundaries but retains the
   recorded unhelpful retry loop.
2. Load the provider during status. This establishes availability for that invocation but introduces interpreter
   probes and optional-runtime imports into ordinary status, changing its explicit contract.
3. Cache a negative with a complete filesystem fingerprint. The provider's probes depend on imports, service
   metadata and worktree relationships; a dist-owned complete fingerprint duplicates runtime selection and can
   silently miss in-place repairs.
4. Add a runtime-owned invalidation signal. This can improve immediate detection when every relevant mutation
   updates the signal, but requires a provider contract and installation/repair coverage outside this bounded work.
5. Cache a negative for 300 seconds with input invalidation. This needs one local advisory record and retains the
   provider boundary, accepting a maximum stale window for repairs not visible in the key.

## 4. Decision Outcome

Choose option 5, as detailed by `PROP-mcp-runtime-pending` and `materials/runtime-observation-options.md`.

- Only completed ordinary nonlocked sync and registrations-only sync with default registration context can create
  the negative observation, including when no host or ledger changes occur. Plan stays pure. Status and locked
  routes never write it. Runtime setup refuses unavailable runtime before writing; successful setup/remove can
  clear an observation. Registration never consults the observation to skip runtime selection.
- The observation key includes configuration bytes, configured selection, provider/service metadata, checkout
  identity and default interpreter identity. Known changes invalidate immediately.
- Lifetime is strictly less than 300 seconds; changed or unreadable inputs, malformed records and future times
  disable reuse. Unknown in-place runtime repairs become visible at expiry or an earlier registration retry.
- Use `.devkit/transient/mcp/runtime-observation.json` as expendable cache. Keep the strict ownership ledger and
  recovery journal semantics unchanged. Unsafe cache inputs fall back to existing behavior. Failed replacement or clearing can leave a prior readable
  negative valid only to its original expiry; failures never renew it.

## 5. Consequences

Repeated status calls stop recommending an unchanged failed registration during the observation window. No
provider import, runtime installation, host launch, trust approval or external send is introduced.

The first status still cannot know runtime availability. A repair that preserves the observation key can leave
pending suppressed for the remainder of 300 seconds. Expiry can restore pending even when the runtime is still
missing; the next explicit registration attempt supplies fresh evidence. Clock rollback past the recorded time
invalidates the record. There is no promise of wall-clock precision if the operating system clock is inaccurate.

If strict immediate detection becomes a requirement, reopen the runtime-provider availability contract and its
mutation coverage. Do not extend the cache lifetime or portray a partial filesystem fingerprint as complete.

## 6. Confirmation

Development integration coverage belongs in the existing host onboarding and distribution reporting/output
contract tests. AC-1 through AC-7 cover no-provider-loading, no-write status, exact expiry, input invalidation,
explicit retry, no-op persistence, setup refusal, override isolation, failed-clear expiry and unchanged
ownership/recovery behavior. Existing host validation paths retain their semantics; no unowned-host parse is added.
`just test-dist` verifies the dist-only dependency boundary. Review the key against provider selection inputs;
no test can prove it detects every runtime repair, so the 300-second expiry is required independently.
