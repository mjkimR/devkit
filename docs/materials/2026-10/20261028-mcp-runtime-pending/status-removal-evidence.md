# Evidence for removing speculative general-status registration notices

Planning input head: `f28f062c384be327b1e8fe939f1199a4f01daa64`.
The user settled the removal direction. No executable probe, runtime installation or registration mutation ran.

- `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/status.py:419` calls
  `registration_pending_notices` only for a checkout with a receipt. The surrounding host-hook path is independent.
- `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py:1079` calls `unregistered_hosts` to
  construct that speculative notice. Source search found no other production caller of either helper.
- `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py:552` checks provider metadata,
  configuration, destination eligibility and ledger ownership without loading the provider. Those facts cannot
  establish its runtime result.
- `packages/devkit-mcp/src/devkit_mcp/features/runtime/usecases/configuration.py` retains selection in the optional
  provider. A read-only profile with no exposed tools returns `None`, distinct from `RuntimeUnavailable` and from a
  concrete launch descriptor. This is existing behavior, not a proposed provider change.
- `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py:1040` obtains pending hosts from the
  actual registration plan's `state == "write"` before withholding fresh-checkout registration writes in locked
  mode. Its `_registration_pending` helper and notice class must remain.
- `CAP-MCP-runtime-registration` describes metadata-only pending inspection; `CAP-DIST-sync-and-transactions`
  promises both locked-sync and general-status notices. The distribution quick reference repeats both claims.
  All three need coordinated wording changes during Development.

The earlier observation PADR and comparison material are withdrawn. Existing Scout/Challenger/worker envelopes
record the earlier direction as history and provide no implementation requirement for it. Low effort in this turn
requires no further support-role pass because the user supplied the complete direction.
