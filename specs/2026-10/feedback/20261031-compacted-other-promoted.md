---
id: FB-compacted-other-promoted
title: Other feedback, promoted
summary: General operational feedback and development ergonomics.
target: other
status: promoted
created_at: 2026-10-31
aliases:
  - FB-config-template-has-no-preview
  - FB-current-reference-material
  - FB-derive-prints-every-pair
  - FB-entrypoints-apply-duplicate-key
  - FB-example-ids-in-acceptance-criteria
  - FB-just-test-package-relative-path
  - FB-smoke-response-style-instruction-path
  - FB-spec-status-stays-planned-during-build
  - FB-spec-summary-missing-from-new-guides
---

# [FB-compacted-other-promoted] Other feedback, promoted

## FB-config-template-has-no-preview

- **Symptom**: devkit config template cannot show the rendered template without writing the project config
- **Response**: devkit `ecff122`
- **Reason**: `devkit config template --print` writes nothing and returns the resulting file as `text`.

## FB-current-reference-material

- **Symptom**: A material used as a current map conflicts with materials being history
- **Response**: docs/development/port-map.md
- **Reason**: S-Lane; the map moved out of materials as a current development document; references, the accepted ADR included, became links (one-off exception approved by the user during the migration)

## FB-derive-prints-every-pair

- **Symptom**: entrypoints derive prints every boundary-target pair
- **Response**: src/devkit_spec/cli/entrypoints.py, `CAP-TRACE-code-entrypoints`
- **Reason**: S-Lane; the text output is one `[CANDIDATES]` line per document with its paths grouped by state (80 lines become 4 in the observed case); JSON keeps every pair

## FB-entrypoints-apply-duplicate-key

- **Symptom**: entrypoints derive --apply writes a second entrypoints key when created_at precedes the existing one
- **Response**: packages/devkit-spec/src/devkit_spec/entrypoints/apply.py
- **Reason**: an existing entrypoints key is replaced wherever it stands; created_at insertion only when there is none

## FB-example-ids-in-acceptance-criteria

- **Symptom**: Example IDs in acceptance criteria are checked as references
- **Response**: src/devkit_spec/bundle/skills/spec-specify/SKILL.md
- **Reason**: S-Lane; example and fixture IDs are written as plain text

## FB-just-test-package-relative-path

- **Symptom**: just test refuses a package-relative test file path
- **Response**: scripts/module.sh
- **Reason**: a selector is also resolved from the module directory, and the unknown-area error says where paths are taken from

## FB-smoke-response-style-instruction-path

- **Symptom**: just smoke asserts the removed response-style instruction path and fails on main
- **Response**: scripts/smoke.sh (commit c05b3c5)
- **Reason**: the smoke now checks the rendered response-style skill and its AGENTS.md pointer instead of the removed instruction path.

## FB-spec-status-stays-planned-during-build

- **Symptom**: A spec stays planned until it is completed
- **Response**: `SPEC-open-feedback-and-progress`
- **Reason**: `RULE-spec-progress` (warning, fixable) moves a draft or planned spec with a checked task to in-progress

## FB-spec-summary-missing-from-new-guides

- **Symptom**: The spec router and the feature output standard omit the summary
- **Response**: src/devkit_spec/bundle/skills/spec/SKILL.md, src/devkit_spec/bundle/skills/spec-specify/references/feature.md
- **Reason**: S-Lane; the router shows `--summary` and the output standard a `summary` line
