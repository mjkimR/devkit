---
id: FB-canonical-c-yaml-contract
title: Adopt a canonical C-loader YAML contract across CLI validation and fixers
scope: repo
kind: change-request
category: other
target: packages/devkit-core/src/devkit_core/core/frontmatter.py and CLI YAML validation/fixer call sites
origin: user
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-canonical-c-yaml-contract] Adopt a canonical C-loader YAML contract across CLI validation and fixers

Parser consistency: optional Python and C YAML loaders accept different syntax.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `SPEC-frontmatter-libyaml` accelerates ordinary headers with C and routes scanner-sensitive
  characters, deep syntax and C errors to Python to preserve existing behavior.
- **Proposed Procedure**: Inventory CLI and fixer YAML loaders, define C-based accepted syntax, and give those
  callers one shared loader and validator. Guarantee libyaml installation or define a stable missing-runtime
  failure. Add explicit authoring rules for canonical notation and autofix only transformations whose values and
  comments can be preserved. Remove Python compatibility routing only after the replacement contract is verified.
- **Expected Benefit**: One accepted syntax across validation and fixers, with fewer compatibility paths.
- **Cost & Risk**: This changes the YAML grammar and deployment assumptions. Quoting, block indicators and BOM
  cleanup need separate semantic-preservation checks. The validator must inspect malformed headers even when the
  document index excludes them. Ordinary question marks, hashes and quoted text must remain representable.
- **Attempted**: The current unit verifies optional acceleration only. C-only syntax and conservative Python
  routing were probed; a canonical loader and fixer were not implemented.

## Diagnostic Details

- **Reproduction**: Compare the strict Python and C loaders on flow scalars with question marks, block scalar
  indicators immediately followed by a hash, and trailing U+FEFF.
- **Expected / Actual**: Expected shared acceptance; C accepts three syntax families that Python rejects.
- **Versions**: Python 3.12.3, PyYAML 6.0.3 with libyaml.
- **Conditions**: C loader availability; YAML syntax at scanner-sensitive positions.
- **Workarounds Attempted**: Conservative Python routing passed 116 regressions and 2,960 differential probes.
- **Related Assets**: `SPEC-frontmatter-libyaml`, its evidence.md and `CAP-DOCS-document-model`.

## Restart and acceptance

Start a separate grammar/deployment spec after inventorying the YAML callers. Verify guaranteed C availability or
its explicit failure, equal CLI/fixer validation, stable strict error contracts, value/comment-preserving fixes,
and representative performance. This is excluded from the current grammar-preserving optimization.

## Evidence

```text
Strict C accepts a: [b?,c]; strict Python raises FrontmatterError.
Strict C accepts a: |# followed by a block body; strict Python raises FrontmatterError.
Strict C ignores trailing U+FEFF; strict Python raises FrontmatterError.
The compatibility guard makes all 2,960 sampled insertion inputs agree.
```

## Disposition

Resolved by `SPEC-canonical-libyaml-only`: the inventoried Python YAML value, node and scalar-validation readers now use the shared LibYAML safe boundary, including frontmatter, workflow records, bundle invocation and governance fixers. Missing bindings fail with `YAML_BINDING_UNAVAILABLE` instead of falling back to Python parsing. Verification: `just test-affected` passed (4,887 passed, 12 skipped), `just test-e2e` passed (272 passed, 11 skipped), `just smoke` passed, and targeted workflow, distribution, document and fixer integration suites passed.
