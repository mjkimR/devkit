---
id: PLAN-language-setting-coverage
spec: SPEC-language-setting-coverage
---

# Technical Plan: `SPEC-language-setting-coverage`

## Constitution and Invariant Review

The accepted `ADR-shared-language-preference-with-bounded-approval-content` preserves wheel layering,
canonical receipts, local-render restrictions and existing approval authority. No additional ADR is required.
Integrated prerequisites supply core.local_config and core.mcp_context; no alternate configuration resolver is needed.

## Architecture and Interfaces

Extend runtime-table validation with presentation.language and add a dependency-free immutable result carrying
requested, resolved, source and fallback fields. Expose it through effective configuration inspection.
Use the existing invocation binding to select the owning workspace for domain rendering; read once before each form.
Keep the language result outside immutable business scope and preserve all existing environment/identity guards.

Extend string Variable declarations with the single default_from reference presentation.language. Inventory planning
receives the shared or effective language result appropriate to its existing canonical/local pass. Explicit consumer
values remain higher priority, including shared auto and free text. Projectless planning retains the declared default.
Response-style opts in through its source manifest only; Host owns installed-asset sync and receipts.

Keep English/Korean static copy beside integration and handoff. Rendering preserves interpolated evidence, exact
schema values and escaping/truncation. Both languages explain the choice in the message itself.

## Failure Modes

Malformed configuration and wrong types retain CONFIG_INVALID. Unsupported strings resolve to English with provenance.
Invalid default_from declarations raise BUNDLE_INVALID. Existing local asset eligibility, tracked-output refusals,
stale-scope guards, absent native form handling and explicit affirmative approval remain mandatory.

## Verification

Cover AC-01 with core and CLI configuration tests; AC-02 with manifest, inventory and local-render tests;
AC-03 and AC-04 with bilingual domain and SDK fixtures, including semantic independent review.
Record per-host native UI coverage as unverified if harmless fixtures cannot be observed (AC-05).
Run lint, types, just test-affected, dist-only checks and governance checks (AC-06), independent medium code review,
and separate reconcile review. Reconcile target-docs into canonical contracts and concise references.

## Execution Assumptions

This worker uses its assigned worktree and commits at stage boundaries. Confinement is emulated with explicit paths,
scoped commands and Host range validation. No native path isolation is claimed. Native UI evidence does not authorize
business actions or real configuration changes. Integration remains the Host's responsibility.

The core presentation helper reads the core-internal invocation binding through a local import, preserving the
existing runtime API and all guards. This avoids editing mcp_context outside the worker's write scope. Native
terminal forms remain explicitly unverified per host in `MAT-language-development-evidence`.
