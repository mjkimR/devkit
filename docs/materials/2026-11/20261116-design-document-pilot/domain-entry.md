# From an available bundle to recorded installation

**Reader question:** How does an available bundle become selected assets and projected paths, and what does a receipt record?

This is a non-normative relationship view of the distribution domain. Availability describes what the Python
installation supplies; requested selection describes what the project wants; the receipt describes the installation
last applied. These are different observations of the same bundle, not three competing selection inputs.

## Relationship view

1. An installed content wheel exposes bundles for discovery. `CAP-DIST-content-packages` §§1–3 owns availability
   and its boundary with deployment. Installing a wheel can make several bundles available.
2. A bundle manifest describes assets and presets. `CAP-DIST-manifest-spec` §3, “Presets and the Default Preset”,
   owns how a preset names an asset subset and when auto-selection applies. The effective selection follows
   `CAP-DIST-sync-and-transactions` §2: availability alone does not explain every deployment choice.
3. Selected assets have managed destinations and, for projected kinds, host destinations. For example, a selected
   Codex skill has a native directory under `.agents/skills/`. `CAP-DIST-agent-projections` §1 owns the matrix;
   not every asset kind is projected.
4. The receipt ties the applied selection to bundle versions, asset paths and file evidence.
   `CAP-DIST-sync-and-transactions` §1 owns the fields and their meaning, including the audit-only selection.

For an available-but-unexpected bundle, next inspect selection in `CAP-DIST-sync-and-transactions` §2.
For a path question, next inspect `CAP-DIST-agent-projections` §1 and the receipt's `assets`/`files` meaning in
`CAP-DIST-sync-and-transactions` §1. No design document is prerequisite to these conceptual questions.

## Evidence boundary

This composition adds the availability → selection → destination → recorded-evidence relationship in one place.
The glossary keeps “devkit bundle” and “projection” terminology. Validity, identity, presets and receipt schema
stay with the cited owners; this draft establishes no alternate invariant or executable instruction.
