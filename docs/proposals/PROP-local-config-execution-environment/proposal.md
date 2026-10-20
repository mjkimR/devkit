---
id: PROP-local-config-execution-environment
title: Local configuration and execution environments
summary: "Add ignored checkout-local configuration overlays and an explicit cloud execution environment, including deterministic worktree behavior and sync controls."
status: reviewing
created_at: 2026-10-20
target_area: distribution/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit/distribution/
    - packages/devkit/src/devkit/worktree/
    - docs/capabilities/distribution/
  excludes:
    - packages/devkit-advisory/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-local-config-execution-environment] Local configuration and execution environments

## 1. Background & Hypothesis

Shared configuration cannot express personal preferences and execution-environment constraints without changing
tracked repository files. A response-style language preference is one concrete consumer; a cloud run that cannot
request interactive approval is another. Introduce `.devkit/config.local.toml` as an ignored local overlay while
keeping `.devkit/config.toml` the shared configuration. Manage `/config.local.toml` in `.devkit/.gitignore` without
replacing unrelated ignore entries.

This supplies the configuration contract consumed by `PROP-standalone-devkit-mcp`. Execution environment describes
runtime constraints; it does not grant approval or turn an ask policy into automatic execution.

## 2. Technical Spike Questions

- **Q1: Effective configuration.** Define which settings permit local overrides, their validation and precedence,
  and which consumers currently read config directly. Prefer defaults, shared config, then local config; merge
  tables by key and replace arrays. Decide whether approval-policy overrides are allowed rather than granting
  authority through an unrestricted overlay. Define explicit destinations for config-writing commands.
- **Q2: Worktree semantics.** Ignored files do not follow Git worktree creation. Compare inheritance from the
  retained checkout with creation-time copying and explicit execution-context propagation. Personal preferences
  and cloud constraints need deterministic behavior; a missing or stale copy must not silently enable interactive
  approval in a cloud run. Account for independent clones and server processes anchored to the retained base.
- **Q3: Rendered artifacts and receipts.** Identify whether local variables change tracked generated assets,
  receipts, locked sync or snapshot verification. Define how personal language settings avoid unintended shared
  changes without weakening reproducibility or treating a local file as a secret store.
- **Q4: Environment controls.** Prefer `[execution] environment = "cloud"` with a defined local default.
  Specify `devkit sync --cloud`, an explicit return-to-local operation, ordinary sync preserving the saved value,
  and dry-run/check behavior. Define when the local setting is saved if sync fails and how callers inspect the
  effective environment. Cloud means interactive approval is unavailable; headless local execution still requires
  independent host-capability checks.

## 3. Proposed Design & Impact

Provide one effective configuration contract for participating readers, with explicit local persistence and
validation. `devkit sync --cloud` records the cloud environment in the local overlay and synchronizes using that
configuration. Planning settles the exact schema and return-to-local command before Development.

Expected acceptance evidence:

- A local language override changes the effective preference without editing shared config; absent local config
  preserves existing behavior. Malformed local config reports a stable actionable error instead of being ignored.
- Nested tables and arrays follow documented merge rules; config-writing commands modify only their selected
  destination. Existing ignore entries survive management of the local-config entry.
- Ordinary sync retains a saved environment, cloud selection and local restoration are explicit, and read-only
  modes do not unexpectedly persist environment changes.
- Linked worktrees and retained-base services observe the intended execution constraints; missing local files or
  stale inheritance cannot silently change a cloud approval restriction into interactive availability.
- Local rendering, receipts and snapshot checks follow the chosen contract, with evidence for both personal
  preference changes and unchanged shared configuration.

Expected contract changes include `CAP-DIST-sync-and-transactions` and `CAP-DIST-workspace-ownership`.
Planning identifies all config readers and expands implementation/test boundaries where needed. No current
capability is changed by this draft.

Scope excluded: MCP package extraction or registration, implementing approval enforcement, shared worker storage,
policy-authorized automatic integration, host sandbox/trust changes, and a general secrets-management system.
`PROP-standalone-devkit-mcp` owns runtime approval enforcement using this configuration.

## 4. Lifecycle & Retirement Criteria

Keep this as a draft until Planning settles merge semantics, write destinations, worktree propagation and rendered
artifact ownership. Its configuration contract should be available before the environment-dependent registration
and approval portions of `PROP-standalone-devkit-mcp`; the independent package extraction can proceed in parallel.
Acceptance and Development require their own explicit decisions. This draft does not set the current environment
or change approval policy.
