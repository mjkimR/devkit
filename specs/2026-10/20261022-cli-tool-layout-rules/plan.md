---
id: PLAN-cli-tool-layout-rules
spec: SPEC-cli-tool-layout-rules
---

# Technical Plan: `SPEC-cli-tool-layout-rules` Feature layout and layer rules for cli-tool

## 1. Architecture Overview & Impact

- Target Area: the `cli-tool` bundle of `devkit-catalog` (two new rule packages, the manifest, the instruction), its
  bundle test and the consumer smoke expectation, `CAP-CLI-agent-cli-toolkit`, the catalog README and the bundle
  recommendation row.
- No runtime package changes: the rules are data loaded by `devkit rules` from the synchronized copy, like the
  existing three.

## 2. Component Breakdown & Interface Contracts

- `rules/layout/` (`RULE-cli-tool-layout`, linter, error): for every Python file under `include`, not `exclude`,
  find the package (below the last `src`), then its first segment below the package must be in `root_modules`
  (+ `extra_root_modules`); below `features/<feature>/` the first segment must be in `feature_modules`
  (+ `extra_feature_modules`); a module directly in `features/` other than `__init__.py` is reported. One violation
  per file at line 1, naming the segment and where it belongs.
- `rules/layers/` (`RULE-cli-tool-layers`, linter, error): parse each file, classify it (root `cli`/`__main__`,
  `base`/`utils`, root `errors`, feature layer, feature `__init__`), resolve every import outside `if TYPE_CHECKING:`
  (absolute ones with the package prefix, relative ones against the file's package) and report:
  - `click` or `devkit_cli` imported outside CLI modules (root `cli`, root `__main__`, a feature's `cli`);
  - a feature layer importing a higher-ranked layer; a transport importing a layer other than `usecases`, `models`,
    `errors`;
  - `base` or `utils` importing a feature;
  - the root `cli` importing a feature at module level.
  One violation per import, at its line.
- Settings for both: `include` (`["**/src/**"]`), `exclude` (test patterns); layout adds `extra_root_modules` and
  `extra_feature_modules` (`[]`).
- Manifest: assets `layout` and `layers` in the default `all`; `guide` unchanged.
- Instruction: the layout section says the feature layout is required and names both rules; the rules section lists
  five.

## 3. Verification & Test Plan

- Rule tests in each rule's `tests/` for AC-01 to AC-07; the bundle test and smoke assert five rules (AC-08).
- `just test catalog`, `just lint`, `just check`, `just rules-check`, `just test-affected`, `just smoke`.
