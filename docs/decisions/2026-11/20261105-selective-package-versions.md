---
id: ADR-selective-package-versions
title: Selective package versions and immutable release inventories
summary: "For independently consumed workspace wheels, we advance changed distributions and exact-pin dependents under one release number, to reduce version churn, accepting mixed versions and release inventories."
proposal: SPEC-selective-package-releases
supersedes:
  - ADR-package-ownership-and-release-version
status: accepted
created_at: 2026-11-05
---

# [ADR-selective-package-versions] Selective package versions and immutable release inventories

- **Status**: Accepted
- **Date**: 2026-11-05

## 1. Context & Problem Statement

Lockstep metadata advances independently consumed `devkit-advisory` without a distribution change.
`ADR-package-ownership-and-release-version` also embeds same-version requirements in ownership clauses, so changing
only its Single release version section would leave contradictory rules. Wheel consumers have no package index;
they need a complete resolvable set of explicit artifact URLs.

## 2. Decision Drivers

- Preserve unchanged package and bundle identities.
- Keep one human-selected release version and ordinary static metadata for standalone package builds.
- Retain exact internal dependency compatibility and package isolation.
- Preserve original published wheel bytes and installable release sets.
- Keep the mechanism in existing repository release tooling.

## 3. Considered Options

- **Lockstep versions:** no release-inventory migration, but does not meet unchanged advisory version stability.
- **Selective versions with exact pins:** minimizes unrelated churn while preserving the existing pin contract;
  requires reverse-dependency propagation and artifact inventories.
- **Selective versions with ranges:** reduces some dependent churn but adds a compatibility window and resolver
  combinations without evidence that they are necessary for the requested outcome.

## 4. Decision Outcome

Choose selective versions with exact pins for version stability without expanding the compatibility promise.

- Root `VERSION` selects a release number; only distributions with significant wheel content or dependency metadata
  changes take that number. Bundles advance only for their own source changes. → `ARCH-07-deployment` section 1.1
  (MUST).
- A normalized wheel comparison ignores only the owning version fields and derived container records. Dependency
  metadata remains significant after recorded generated preparation edits are logically unwound; bundle
  enumeration retains its existing byproduct exclusions. Exact-pin dependents advance to a fixed point.
  → `ARCH-07-deployment` section 1.1 (MUST).
- A complete release inventory records actual package versions and original artifact URLs and digests. Unchanged
  published wheels retain their original bytes and location. → `ARCH-07-deployment` section 1.1 (MUST).
- Wheel installation commands name the selected dependency closure with each artifact's original URL. Git sources
  remain pinned to one monorepo commit with consistent exact pins. → `CAP-DIST-content-packages` section 2 (MUST).
- This decision replaces the old ADR's Single release version clauses and only the same-version qualifiers in
  its foundation, MCP runtime and harness dependency clauses. All package ownership, dependency direction, import,
  configuration, bundle assignment and CLI version-source decisions remain in force. The old ADR stays accepted with a partial-supersession notice.

## 5. Consequences

Unchanged advisory/content distributions can retain their versions across releases. An advisory change still
advances its exact-pin reverse dependencies; a lower-level change can therefore advance many packages.

Comparisons may build all wheels and add release inventory validation; no build-time improvement is claimed.
Original releases must retain referenced assets. Historical bootstrap requires verified original wheel files and
checksums. The first selective release cannot proceed while that provenance is missing.

Compatible ranges, independent package version selection and registry publication remain outside this decision.

## 6. Confirmation

Selective identity, closure and inventory checks are covered in
`packages/devkit/tests/integration/package/test_version_script.py` and
`packages/devkit/tests/integration/package/test_lockstep.py` with selective identity, closure and inventory checks.
Release-tooling tests cover canonicalization, bootstrap provenance, artifact corruption, incomplete preparation
and publish retry. Installed consumer tests verify wheel/Git sets outside the source workspace and preserve
advisory-only and dist-without-agt isolation. The first selective release additionally requires verified historical originals; fixture validation does not establish their availability.
