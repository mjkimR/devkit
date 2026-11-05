---
id: PADR-bundle-source-snapshots
title: Local content packages for bundle snapshots
summary: "For private bundle reuse, we copy complete supported content providers into repository-owned packages with provenance and explicit refresh, to avoid private-origin fetches, accepting explicit provider replacement."
proposal: PROP-bundle-source-snapshots
status: draft
created_at: 2026-11-05
---

# [PADR-bundle-source-snapshots] Local content packages for bundle snapshots

## 1. Context & Problem Statement

Private content dependencies need credentials in every consumer. Existing local content packages already support
normal discovery, receipts and overrides, but manual copying supplies no coherent provenance or refresh behavior.
Bundle names are globally unique across installed providers, including unselected bundles.

## 2. Decision Drivers

- Reproduce bundle sources without fetching the private origin after adoption.
- Preserve ordinary package discovery, source ownership and override behavior.
- Make updates reviewable and refuse local source loss.
- Keep runtime-package vendoring and credential handling outside the feature.

## 3. Considered Options

- Manual copy into a local package: usable now, but refresh safety and provenance are maintained ad hoc.
- A complete supported content provider in a generated local package: uses existing discovery with explicit
  replacement and adds a small snapshot inventory/refresh boundary.
- Selected-bundle extraction with provider precedence: keeps an upstream provider but changes discovery semantics.
- A second local loader: removes the packaging step but duplicates selection and ownership.
- Arbitrary wheel/runtime vendoring: includes non-content dependencies and exceeds the private-content scope.

## 4. Decision Outcome

Choose the ordinary local package with complete supported provider replacement.

- A snapshot contains original source manifests/assets from every bundle of one supported content-only provider;
  it remains a normal dev dependency with distinct wrapper modules and unchanged bundle names. →
  `CAP-DIST-in-repo-bundles` snapshot packaging (MUST).
- Self-contained bundle Python assets remain supported within the declared devkit/stdlib/relative import subset;
  non-content providers and unsupported dependency closure are refused before writes. →
  `CAP-DIST-in-repo-bundles` supported inputs (MUST).
- Credential-free source identity, optional verified commit and canonical byte/mode hashes identify an adoption;
  unchanged inputs leave local package/version bytes unchanged. → `CAP-DIST-in-repo-bundles` provenance (MUST).
- Refresh is explicit, reports changes and requires matching reviewed/current digests; local drift is refused and
  reported write failures restore the prior package. → `CAP-DIST-in-repo-bundles` refresh (MUST).
- Discovery preserves its global duplicate-name refusal, so installation replaces the complete original provider
  explicitly rather than shadowing selected bundles. → `CAP-DIST-content-packages` snapshot providers (MUST).
- Normal sync still owns receipts/projections and project overrides; source snapshot refresh is a separate
  operation. → `CAP-DIST-sync-and-transactions` snapshot boundary (MUST),
  `CAP-DIST-workspace-ownership` snapshot sources and overrides (MUST).

This extends ordinary package tooling and preserves the no-second-loader decision; it supersedes no ADR.

## 5. Consequences

Consumers can commit reviewable private bundle content and bootstrap it without the private origin when runtime
and build dependencies are available. Maintainers need an accessible source checkout for explicit refresh and must
replace the original provider in the dependency graph. Static source/dependency checks support a bounded subset;
arbitrary dynamic runtime closure is not certified. No private consumer package has been inspected in Planning.

## 6. Confirmation

Development adds source/provenance/rollback integration tests and built-package consumer coverage under
`packages/devkit-dist/tests/`, including multi-bundle replacement and supported Python rules. Existing dist-only
checks verify no harness runtime import is introduced. Review verifies that capabilities restate the clauses and
consumer instructions separate copying, dependency replacement and sync.
