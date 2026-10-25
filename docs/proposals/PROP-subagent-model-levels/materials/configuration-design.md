# Subagent level configuration design

## Existing implementation anchors

- Common role validation and deterministic host rendering:
  `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py`.
- Project configuration parsing, accepted keys and template sections:
  `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`.
- Shared configuration and checkout-local allowlist:
  `packages/devkit-dist/src/devkit_dist/features/project/repositories/local_config.py`.
  `read_local_config` rejects distribution policy outside its explicit allowlist.
- Common contracts reach `_BundleInventory._contract`; native variants take the separate copy path in `_project`:
  `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/inventory.py`.
- Sync preflight passes project inputs through `_plan_inventory` into `desired_inventory`:
  `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py`.
- `plan_bundle` invokes the same inventory without project state:
  `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/plan.py`.
- Integration checks already own source/common projection coverage:
  `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`.
- Shipped role expectations:
  `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`.

## Proposed schema

The common role contract gains an optional top-level `level` enum:
`inherit`, `light`, `standard`, `deep`. It is interpreted by devkit and never rendered as a native field.
All shipped spec roles omit the level and model/effort settings. Remove their uninterpreted `x-model-profile`.
Do not tie this enum to `activity-effort`.

```toml
[subagents]
# Optional. Absence allows a contract level; explicit inherit resets every common contract's level.
default_level = "inherit"

[subagents.levels.deep.codex]
# A nonempty host-native alias or identifier. This example overrides only effort.
effort = "high"

[subagents.roles."spec:scout"]
level = "light"
```

Only `default_level`, `levels` and `roles` are valid under `subagents`.
`levels` accepts `light`, `standard`, `deep`, each containing supported host names only.
Each host mapping accepts `model` and `effort`, both strings. No user-defined levels or additional fields.
`roles` maps a bundle-qualified asset ID to a table containing only `level`.
A role override is global across selected hosts; mapping overrides supply host-specific tuning.
No separate raw per-role model override is needed for this scope.

Model must be a nonempty string without control characters; it is an opaque host-native identifier.
The reserved string `inherit` resets that field to omission. Effort accepts host-supported values or `inherit`.
An absent field retains the built-in mapping field; TOML null and empty strings are invalid.
The `inherit` level cannot have mappings and always clears both fields.
For an overridden model, inherited built-in effort remains unless explicitly reset; document and test this.
For known supported model families, validate known effort restrictions. Unknown model identifiers stay valid
without network calls; their actual availability and effort compatibility belong to the host runtime.
Reject host-unsupported explicit effort regardless of the model string.

Selection order: role override > explicitly present project default > explicitly present contract level > omission.
The commented config template does not create an active default_level, preserving contract opt-in behavior.
Mapping selection and field merge are independent of level selection.

Keep this section shared-only. `config.local.toml` containing `subagents` fails with
`CONFIG_LOCAL_KEY_FORBIDDEN`. Do not add a local exception or persist personal rendering variants.

## Existing native settings and variant boundary

Common contracts retain their host-native model/effort escape hatch when no neutral selection exists.
These are explicit author overrides rather than inherited defaults. This preserves deliberate native contracts.
An explicitly declared contract level plus native model/effort in any host block is `BUNDLE_INVALID`, including
`level: inherit`, because the author must select one mechanism. Bundle validation checks this offline.
A project level selection intentionally replaces native model/effort fields on that common contract and preserves
all other settings. An implicit level omission preserves explicit native fields; explicit project `inherit`
removes them. These cases must have separate acceptance checks.

Native variants remain byte-for-byte copies. Global default_level applies only to common contracts; document
that boundary in config help. A role-specific override aimed at a native-variant asset fails with `CONFIG_INVALID`
while the asset's bundle is selected. Do not parse or rewrite native variants to retrofit level support.
An unsupported host block continues producing no file, regardless of the level.

Validate role keys against discovered installed bundles: an unknown bundle is invalid; when its bundle is
selected, a missing/non-subagent asset is invalid. An installed unselected bundle's well-formed role entry is
retained but dormant. Selected common assets excluded by a preset are also dormant. Malformed mapping fields
are always invalid even if their level or host is not selected. A role-specific native-variant override is
invalid for a selected bundle even if its asset is excluded by a preset, avoiding selection-dependent mistakes.

## Error and transaction behavior

Reuse `CONFIG_INVALID` for invalid levels, keys, values, mappings and applicable role selections.
Use `BUNDLE_INVALID` for invalid common contract levels and conflicting source declarations.
Use existing advisory metadata to produce an `INPUT_ERROR` action, exact target/key and correction.
No stdout advisories, new output format or network model validation is needed.
Model syntax accepted offline does not promise subscription access, alias existence or runtime compatibility.

Compute validated policy before filesystem mutations. Extend the typed ProjectConfig and inventory inputs;
use a distribution model module for immutable resolved values and a distribution service for pure resolution.
Services never depend on use cases. Native renderers receive resolved settings, not project file readers.
All callers of inventory retain a default policy argument; bundle plan uses contract and built-in defaults.
Do not add project-state reads to bundle plan or bundle validation.

Receipts track final projection bytes through existing file hashes. No new receipt schema or migration is needed.
Status, dry-run and sync use the same policy resolution and show pending changes through existing output.
Changing only mappings can change native projections without changing source contract bytes.
Returning to inherit removes stale owned native fields through the existing transaction.

## Verification plan

- Typed resolver checks for precedence, explicit resets, strict fields and combinations across all host/level pairs.
- Integration checks in test_subagent_contracts.py for ordinary and templated source contracts, escape hatches,
  native variants, unsupported blocks, override identities and dormant configuration.
- Source role tests verify no fixed model, effort or x-model-profile on shipped roles.
- Sync checks cover dry-run/status parity, receipt digests, stale field removal, no-write invalid preflight,
  idempotence and preservation of unrelated host/config files.
- Configuration checks cover shared-only policy, strict validation and commented template refresh.
- Run `just lint-check dist`, `just check dist`, checks for affected spec source tests and `just test-affected`.
  Use module selectors as the repository recipes define them; preserve test selector full fallback.
