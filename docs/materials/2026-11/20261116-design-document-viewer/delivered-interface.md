# Delivered core interface for Viewer Task 5

Historical Planning pin: core-contract.md SHA-256
`1d724834426991e04904fd9f1677f60235de49764d9a1863ad9c8d112c55f413`; unchanged.
Current delivery: `002241b56fd8e5a446cbfa4f2e4bf42d25484455`, selected by
`ADR-area-scoped-design-bundles` and `CAP-DOCS-document-model`.

| Core Kind row | Historical assumption | Delivered consumer interface |
| --- | --- | --- |
| DESIGN, designs, AREA_BUNDLE, design.md, entrypoints true | Flat ID.md, no area | `<root>/designs/<area>/<ID>/design.md`; matching area; bundle directory is canonical ID |
| DOMAIN, domain, AREA, entrypoints false | Flat ID.md, no area | `<root>/domain/<area>/<ID>.md`; matching area |
| OPERATIONS, OPS, operations, FLAT, entrypoints false | Flat ID.md | Unchanged `<root>/operations/<ID>.md`; no area |

All retain Living Spec standing, EVERY_ROOT format, required summary/H1, draft default, retired terminal status
and their existing related_designs/domains/operations relation fields. Source rows were inspected in
packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py. Core alone validates schema.

Every DESIGN bundle file except its own design.md is parent-owned support, including README, files outside
artifacts and files at arbitrary depth. Identified support and nested anchors never gain canonical identities.
An orphan directory supplies no canonical node. Domain/OPS support remains beside the anchor under ID/artifacts.
Area moves preserve ID/references; DESIGN rename/root moves carry the whole bundle. Root moves change namespace.
Alias navigation resolves identity; stale ordinary paths remain missing. No registry/callback/dependency is added.

Baseline accepted-turn HEAD cff2ca7c0b2e888b16c0c348a0f5deed099f162e: `just viewer test` on 2026-11-16
returned 249 PASS / 1 FAIL. Actual retained-document read failed ENOENT on the removed flat DESIGN path.
Additional current grammar tests are run RED before runtime fixes. Current grammar matrix results follow in the
Task 5 evidence ledger. Old PASS cells in support-matrix.md describe the original flat-contract implementation.
