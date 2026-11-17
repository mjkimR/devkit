---
id: DOMAIN-bundle-selection-and-installation
title: "Bundle selection and installation"
status: active
area: distribution
summary: "Relates available bundles, requested selection, conceptual assets, projected paths and receipt evidence."
related_capabilities: [CAP-DIST-content-packages, CAP-DIST-sync-and-transactions, CAP-DIST-manifest-spec, CAP-DIST-agent-projections]
related_designs: [DESIGN-distribution-file-directory-replacement]
---

# [DOMAIN-bundle-selection-and-installation] Bundle selection and installation

Readers confuse available bundles, requested selection, conceptual assets, projected paths and receipt evidence: a
deployed path or a receipt entry can look like a requested selection or a separate asset.

## Relationship overview

An installed Python content package makes a bundle available. Availability follows package installation and
dependency resolution; it does not by itself describe every asset deployed to the workspace
(`CAP-DIST-content-packages` §§1–3).

Requested selection combines the project's preset configuration with a bundle's declared auto-selection defaults.
An available bundle without auto-selection needs an explicit configuration entry; an auto-selected bundle can be
narrowed or opted out.

| Concept or relationship | Distinction | Authoritative owner |
| --- | --- | --- |
| Available bundle | Supplies assets and presets that selection can request | `CAP-DIST-content-packages` and `CAP-DIST-manifest-spec` |
| Requested selection | Determines the selected assets and agent targets applied by sync | `CAP-DIST-sync-and-transactions` §2 |
| Conceptual asset | Identified by `(bundle, kind, id)`; a source can yield multiple physical representations | `CAP-DIST-manifest-spec` §2 |
| Managed and projected destinations | Represent selected assets in managed content and supported host paths according to kind and selected agents | `CAP-DIST-agent-projections` |
| Installation receipt | Records the applied selection, asset paths and installed file evidence | `CAP-DIST-sync-and-transactions` §1 |

For example, one selected skill can have a managed copy under `.devkit/managed/` and a native representation under
`.agents/skills/`. These paths represent the same conceptual asset rather than separate requested assets.
Kinds have different projection behavior; a seeded document instead becomes project-owned at its target
(`CAP-DIST-manifest-spec` §2 owns kind and seeded-asset semantics).

The receipt's `selection` records what the last sync applied. It is audit evidence, never another selection input.
Its `assets` associate deployed representations with their bundle/asset identity, while `files` records digests and
modes. Seeded targets have their separate evidence. A path alone therefore does not establish a new asset identity
or a requested selection.

## Update triggers

- `CAP-DIST-content-packages` §§1–3 change what makes a bundle available.
- `CAP-DIST-sync-and-transactions` §2 changes the selection inputs, or §1 the receipt fields `selection`, `assets` or
  `files`.
- `CAP-DIST-manifest-spec` §2 changes asset identity or kinds, or `CAP-DIST-agent-projections` the destinations of a
  kind.
