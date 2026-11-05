---
id: PROP-selective-package-releases-target
title: Target Living Spec changes for selective package releases
summary: "Proposed release-version, inventory and installation contract targets for selective package releases."
status: draft
proposal: PROP-selective-package-releases
created_at: 2026-11-05
targets:
  - file: docs/architecture/ARCH-07-deployment.md
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
  - file: docs/decisions/2026-11/20261102-package-ownership-and-release-version.md
---

# Target Living Spec changes for selective package releases

These are proposed Development targets, not current contracts. The proposal and
`PADR-selective-package-versions` hold the direction pending acceptance.

| Document | Planned change | Verification |
| --- | --- | --- |
| `ARCH-07-deployment` | Replace all-wheels-equal/tag-URL topology with release vs package vs bundle versions, canonical wheel comparisons, exact-pin closure, tracked plans, completed inventories, original artifact reuse, bootstrap and failure behavior; preserve model/npm policies | Release-tooling tests and installed consumer scenarios |
| `CAP-DIST-content-packages` | Describe an inventory-selected wheel set and actual-version exact pins instead of lockstep companions; preserve discovery and package isolation | Wheel consumer dependency resolution and dist-only isolation |
| `CAP-DIST-in-repo-bundles` | Remove same-version rationale while retaining one top-level Git devkit requirement and existing workspace/path loading | Git consumer install and documentation review |
| `ADR-package-ownership-and-release-version` | Add partial supersession for release/version clauses and same-version dependency qualifiers, preserving all other decisions | ADR review against promoted decision and architecture |

Promote `PADR-selective-package-versions` only through the normal handoff. Keep the old ADR accepted because it
continues to own unrelated decisions. No new capability, document kind, use case, feature edge or UX screen is needed.

Keep README, distribution/advisory references and installation guides in step. Review every concrete install command
for mixed artifact URLs, including extras and tool installs. Keep the dist-owned consumer instruction in step with
`CAP-DIST-in-repo-bundles` if its same-version claim changes; the actual instruction is a bundle source edit and
requires authoring context before Development. Generated projections and receipt follow normal sync ownership.

Expected implementation ownership is repository release tooling (`scripts/`, release workflow, version/lock metadata)
and release-related package tests, not distribution runtime behavior. Source-text changes in distribution-owned
bundles are limited to the installation/version guidance stated here. Narrow Development task boundaries to exact
files and documented generated sync outputs.
