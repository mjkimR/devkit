# Bundle selection and installation

## Question

How do available bundles, requested selection, conceptual assets, projected paths and receipt evidence relate?

## Relationship overview

An installed Python content package makes a bundle available. Availability follows package installation and
dependency resolution; it does not by itself describe every asset deployed to the workspace
(`CAP-DIST-content-packages` §§1–3).

Requested selection combines the project's preset configuration with a bundle's declared auto-selection defaults.
An available bundle without auto-selection needs an explicit configuration entry; an auto-selected bundle can be
narrowed or opted out. `CAP-DIST-sync-and-transactions` §2 owns selection inputs and effective configuration.
`CAP-DIST-manifest-spec` §§2–3 owns assets, preset membership and manifest identity.

| Concept | Relationship to the next concept | Authoritative detail |
| --- | --- | --- |
| Available bundle | Supplies assets and presets that selection can request | `CAP-DIST-content-packages` and `CAP-DIST-manifest-spec` |
| Requested selection | Determines the selected assets and agent targets applied by sync | `CAP-DIST-sync-and-transactions` §2 |
| Conceptual asset | Identified by `(bundle, kind, id)`; a source can yield multiple physical representations | `CAP-DIST-manifest-spec` §2 |
| Managed and projected destinations | Represent selected assets in managed content and supported host paths according to kind and selected agents | `CAP-DIST-agent-projections` |
| Installation receipt | Records the applied selection, asset paths and installed file evidence | `CAP-DIST-sync-and-transactions` §1 |

For example, one selected skill can have a managed copy under `.devkit/managed/` and a native representation under
`.agents/skills/`. These paths represent the same conceptual asset rather than separate requested assets.
Kinds have different projection behavior; a seeded document instead becomes project-owned at its target.
`CAP-DIST-agent-projections` owns host destinations; `CAP-DIST-manifest-spec` §2 owns kind and seeded-asset semantics.

The receipt's `selection` records what the last sync applied. It is audit evidence, never another selection input.
Its `assets` associate deployed representations with their bundle/asset identity, while `files` records digests and
modes. Seeded targets have their separate evidence. `CAP-DIST-sync-and-transactions` §1 owns these distinctions.
A path alone therefore does not establish a new asset identity or a requested selection.

## Authority boundary and next useful step

This entry explains the relationship chain; it adds no transaction guarantee, readiness test or recovery procedure.
For why a bundle is available, resolve `CAP-DIST-content-packages` and read §§1–3.
For what is requested or what the receipt proves, resolve `CAP-DIST-sync-and-transactions` and read §2 or §1.
For asset/preset syntax, resolve `CAP-DIST-manifest-spec`; for a host destination, resolve `CAP-DIST-agent-projections`.
For sync's implementation mechanism, follow the selected design link in the transaction capability.
Read only the owner needed for the question; understanding this chain requires no schema or Python class catalog.
