# Runtime observation evidence and alternatives

Planning input head: `24abeb58abcbd1f371017627b28b60df0ddbcfe5`.
No runtime probe, registration mutation, installation or host launch ran during this investigation.

## Existing seams

- `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py:302` validates an exact ownership
  ledger schema. Adding advisory data there would expand strict ownership and journal semantics.
- `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py:419` calls the provider during
  registration planning. `RuntimeUnavailable` becomes a warning and per-host `runtime-unavailable` state, without
  producing a negative ledger record.
- `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py:552` implements provider-free pending
  detection. It checks metadata, registration config, destination eligibility and ledger ownership.
- `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py:1010` takes clone then project locks;
  ordinary sync applies registration after its asset result. Registrations-only sync uses the same guards and
  ordering at line 1253. These are existing observation-writer seams, not new commands.
- `packages/devkit-mcp/src/devkit_mcp/features/runtime/usecases/configuration.py:86` selects retained execution by
  common Git identity, registered worktrees, candidate interpreter paths, a subprocess probe, matching MCP/service
  versions, and imported locations. The default candidates at line 102 are the current interpreter and retained
  executor `.venv/bin/python`; explicit executable selection is a different invocation context.
- `packages/devkit-dist/tests/integration/features/host/test_mcp_onboarding.py:317` asserts that pending detection
  does not load a provider. Distribution reporting at
  `packages/devkit-dist/tests/integration/features/distribution/test_sync_reporting.py:154` covers the fresh clone
  whose locked restoration leaves registration pending.
- `CAP-MCP-runtime-registration` requires provider-free missing-registration inspection.
  `ADR-mcp-runtime-and-shared-artifacts` assigns runtime selection to the optional provider and local ownership to dist.

## Comparison

| Option | Evidence and benefit | Cost and risk | Conclusion |
| --- | --- | --- | --- |
| Current pending check | All data is already provider-free | Repeats a fix that returns runtime-unavailable | Does not address source feedback |
| Provider load in status | Registration plan already distinguishes runtime-unavailable | Imports optional provider, launches candidate interpreter probes; violates status contract | Exclude |
| Negative ledger field with no expiry | Small local persistence change | Strict schema/journal expansion; hides later available runtime indefinitely | Exclude |
| Complete dist-side runtime fingerprint | Could invalidate many installs | Selector inspects runtime imports and dependencies; completeness cannot be shown without duplicating provider | Exclude |
| Runtime-owned generation/signal | Provider could describe its own invalidators | Arbitrary installs and in-place repairs must update it; changes excluded provider boundary | Reconsider for strict immediate detection |
| Separate negative observation, key plus 300-second lifetime | No provider load in status; immediate known-input invalidation; guaranteed expiry | First status remains unknown; invisible repairs wait for remaining lifetime; recurring pending after expiry | Recommend |

## Verification limits and baseline

These are code/contract observations, not measured runtime costs. No claim compares execution timing or operation
counts to the base. Development can test behavior with fake provider results and clocks in the existing integration
fixtures. It needs no checkout of another revision and no retained-runtime installation.

A stat/metadata key is deliberately incomplete. Package repair can change usability without replacing the Python
executable or changing its reported distribution version. The hard expiry is therefore mandatory even when all
key inputs match. Planning does not claim strict immediate runtime recovery detection.

## Challenger fold verification

The mandatory medium Challenger found three P2 specification gaps. The worker checked their fold against the
existing code without running mutations:

1. `registrations.apply` returns immediately at line 601 for no changes, while `SetupMcpUseCase` raises at line 27
   before apply on runtime-unavailable. The proposal now makes negative persistence an explicit dist sync opt-in,
   keeps planning pure, handles observations outside that early return, and limits setup/remove to clearing on
   success. No runtime-provider edit is needed.
2. `unregistered_hosts` line 575 short-circuits destination parsing when no ownership record exists. The proposal
   now preserves validation on existing paths, and does not assert that the baseline parses every malformed file.
3. A readable negative in a nonwritable directory cannot always be removed. The proposal now allows the prior
   record to survive only to its original expiry on failed replace/clear and requires a fake-clock regression.

Support roles were read-only by instruction under Codex emulation. Before/after Git tree snapshots matched for
Scout (`52e121f8a11edba874ae2394135996c01b0952c7`) and Challenger
(`e19e1ed8b6996d454edde6822d4090a58bde2372`); their HEAD stayed at the Planning input commit. No explicit file read
outside this worktree was reported. Dependency/cache reads internal to the required `uv` runtime were not audited.
