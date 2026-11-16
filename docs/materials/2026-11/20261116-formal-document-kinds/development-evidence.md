# Formal role core development evidence

## Identity outcome and migration

Baseline bb0192c549888dc7d34c98a60304480283d32c56: four current role files have no id frontmatter; no
canonical operations document exists. Reading those exact Git objects without checkout gives zero formal role
nodes. Head `uv run devkit docs list design domain operations --format json` gives five active formal nodes.
This is an identity-coverage measurement, not a timing/performance claim.

The four former canonical paths are absent. Their exact source bytes remain reachable from the baseline Git
commit; preserved completed specs/materials citing those paths are historical source coordinates, not redirects.
Archived operations bytes and the pinned core contract remain unchanged. No path-shaped aliases were added.

| Baseline source coordinate | SHA256 |
| --- | --- |
| docs/designs/distribution-transactions.md | a08acf1f18b0cc5d4fb0b17cb151dd45e0b35a1a78210174b5baea2a4b5be99a |
| docs/designs/distribution-transactions/file-directory-replacement.md | 612f92d7807eba1dc4a9aeb5b354fcb1a0b0d83b39ab41a92da4aa5f59dd033d |
| docs/domain/delivery-relationships.md | 1066b3fab27eeda3799d7e817d366bf65121c25a271bbdc8933da920605f6cb1 |
| docs/domain/bundle-selection-and-installation.md | ebf009410c46ee825e8bd1a5e2f7208e377138f1316cf730474bd2c3f8de0604 |

Current capability/glossary ingress uses full formal IDs. The design entry links its independent formal detail;
the flattened detail source link was repaired from ../../../packages to ../../packages. No behavioral guarantee
or recovery permission moved. Existing historical materials/completed specs were not rewritten.

## Actual ordinary destinations

Every ordinary local link in the five migrated nodes was resolved from its document directory and checked for
existence; these links are not claimed as indexed reference edges.

| Current node | Relative destination | Result |
| --- | --- | --- |
| docs/designs/DESIGN-distribution-file-directory-replacement.md | ../../packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/transaction.py | exists |
| docs/operations/OPS-distribution-sync.md | ../development/reference/distribution.md | exists |
| docs/operations/OPS-distribution-sync.md | ../development/reference/distribution.md | exists |
| docs/operations/OPS-distribution-sync.md | ../../packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/consumption.md | exists |

## F1–F6 support evidence

| Contract / existing surface | Implemented owner and evidence |
| --- | --- |
| F1 Kind/Python/prefix/JSON/order, exact role schema | models/kinds.py and model.py; test_kinds.py asserts appended public values, unchanged prior ordering, table facts and fingerprint; test_formal_kinds.py exercises all three real roles, global/package roots, invalid metadata/path/H1/status/reserved fields |
| F2 index/list/filter/history/status, resolve/aliases/refs/rewrite/memo | test_real_role_discovery_alias_refs_history_and_memo and namespace controls; direct CLI JSON keys and kind values asserted, aliases resolve retired targets and current typed refs rewrite canonically; an independent Python process refuses fresh parsing and successfully decodes all three kinds/relations from the persistent disk memo |
| F2 search modes/exact pinning | deterministic local embedding test exercises dense/hybrid/auto for all three actual kinds; lexical and exact ID pinning exercised per role; no network/model download used |
| F3 identity/format/summary/reference rules | owned governance integration tests and existing rule wrapper regression; new typed relation negative shapes, prefix, duplicate and missing controls; retired role nodes stay checked; opt-in typed role metadata on indexed MAT is validated without rewriting its freeform prose |
| F3 artifact boundaries | same-root same-kind canonical-parent classification, ID-free named-parent support and stray/orphan/identified/symlink-parent negative cases, including every parser-recognized identity field via shared IDENTITY_FIELDS and valid fenced identity examples; real staged parent-only deletion reaches unchanged dependent artifacts while respecting exclusions; binary support needs an owner but no fake ID |
| F3/F5 source anchors | optional DESIGN paths, reverse --file, safe/dead path controls and real staged source deletion of a retired DESIGN; DOMAIN/OPS reject field |
| F4 bundle registration/inventory/sync/get-context | eleven selected instruction assets, nine template files including compatibility pointer, source sync and exact distribution inventories; built-wheel docs-only consumer authors all three roles from shipped templates and resolves/lists/searches them without devkit-spec |
| F5 maintenance and migration | both global/package starting roots exercise rename + alias, root move, split and cross-kind transfer with exactly one data-file parent and checked bytes; retired predecessor remains valid; five current nodes and ordinary source links audited above |
| F6 existing contracts/regression | owned unit/integration/rule wrappers, lint/type/affected checks; docs-to-spec dependency remains absent, existing IDs/JSON keys/error/sentinel shapes retained |
| Required lifecycle L1–L4 | Pending separate implementation under PROP-design-document-lifecycle; not claimed by core evidence |
| Required viewer V1–V4 | Pending separate implementation under PROP-design-document-viewer; not claimed by core evidence |

Checks and reviewed source SHAs are recorded in the Unit envelopes. Semantic statement ownership and the ordinary
link audit are reviewed independently from deterministic schema checks. No docs MCP API was invented.
