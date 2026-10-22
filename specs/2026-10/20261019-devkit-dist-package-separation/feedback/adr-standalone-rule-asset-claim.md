---
id: FB-adr-standalone-rule-asset-claim
title: Bundle compatibility ADR says no standalone first-party bundle ships rule assets
scope: repo
kind: question
category: docs-mismatch
target: ADR-dist-bundles-compatibility (section 3, harness guidance of the devkit bundle)
skill: spec-specify
agent: claude-code
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-19
---

# [FB-adr-standalone-rule-asset-claim] Bundle compatibility ADR says no standalone first-party bundle ships rule assets

## 1. Friction / Question

- **Context**: Development checked the premises of the accepted ADRs against the base before specifying. The ADR
  assigns the `advisory` bundle to `devkit-dist` as data only and states that no first-party bundle installable
  without `devkit-agt` ships rule, gate or workflow assets.
- **Expectation**: The inventory behind that statement covers every preset of the bundles that move to `devkit-dist`.
- **Actual**: The `advisory` bundle's opt-in `python` preset ships the `unique-code` rule asset
  (`RULE-advisory-unique-code`), and its bundle area carries rule code that imports `devkit.rules`.
- **Workaround (or Interpretation Chosen)**: Kept the decided assignment (the statement is a rationale, not a
  contract). A standalone project selecting `advisory:python` receives `HARNESS_ENGINE_MISSING`, which the ADR's
  generic notice covers; the `devkit-dist` layering test treats rule code under a data area's `bundle/` as bundle
  content allowed to use the rule API. Recorded as a spec assumption; the Living Spec states the exception.
- **Suggestion**: A human confirms the interpretation. A future ADR touching bundle assignment could state the
  exception explicitly; Planning inventories of bundle content could list assets per preset, not per default preset.

## Diagnostic Details

- **Reproduction**: Read `packages/devkit/src/devkit/advisory_guide/bundle/bundle.toml` at the handoff commit and
  compare with the ADR's sentence about first-party standalone bundles.
- **Expected / Actual**: Expected no rule asset in `advisory`; actual: `[presets.python] assets = ["agent-advisory",
  "agent-advisory-python", "unique-code"]` with `kind = "rule"`.
- **Versions**: devkit-agt 0.1.1 at the spec handoff commit.
- **Conditions**: Development of the spec handed off from PROP-devkit-dist-package-separation.
- **Workarounds Attempted**: Interpretation above; verified by the standalone smoke (`devkit add advisory:python` in
  a `devkit-dist` only consumer exits 0 with `HARNESS_ENGINE_MISSING`).
- **Related Assets**: `ADR-package-split-and-namespaces`, `CAP-DIST-content-packages`,
  `packages/devkit-dist/tests/distsupport/layering.py` (`BUNDLE_CONTENT_ALLOWED`).

## Evidence

```text
ADR-dist-bundles-compatibility, section 3: "No first-party bundle installable without devkit-agt ships rule, gate or
  workflow assets (only devkit-spec, which requires devkit-agt, and authoring, which ships with it, do)"
advisory_guide/bundle/bundle.toml: id = "unique-code", kind = "rule", source = "rules/unique_code"
  [presets.python] assets = ["agent-advisory", "agent-advisory-python", "unique-code"]
previous layering table: "advisory_guide": {"rules"}
```

- **Disposition**: No change: the ADR stays as accepted rationale, and the Living Spec already states the exception (CAP-DIST-manifest-spec, CAP-DIST-in-repo-bundles: rule assets deploy without devkit-agt with HARNESS_ENGINE_MISSING)
