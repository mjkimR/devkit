---
id: FB-cross-package-bundle-fixture-needs-host-round-trip
title: A test in another package that copies a changed bundle manifest forces a Host round trip
scope: repo
kind: suggestion
category: missing-capability
target: .devkit/managed/spec/subagents/development-worker.md (Write boundaries, Tier B adjacency)
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-11-10
---

# [FB-cross-package-bundle-fixture-needs-host-round-trip] A test in another package that copies a changed bundle manifest forces a Host round trip

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: A Development worker that changes a declared bundle manifest may update only tests in the
  declared roots or their test mirror. A test in another package that loads that bundle as a fixture is
  non-adjacent, so the worker stops with a problem and the Host grants and fixes the path.
- **Proposed Procedure**: Either keep the rule and leave this record as evidence that it costs one round trip, or
  admit as a Tier B extension an existing test that loads the declared bundle source directly, limited to updating
  its fixture for the approved manifest change and never weakening its assertions.
- **Expected Benefit**: One worker stop, one Host recovery commit and one worker restart fewer for a one-line
  mechanical fixture update.
- **Cost & Risk**: Widens worker authority into another package's tests; the reviewer would have to judge whether a
  fixture change is mechanical or weakens the test.
- **Attempted**: Hypothesis. In this unit the Host fixed the fixture in its own commit and made it robust (a regex
  append with a count assertion instead of a literal replacement).

## Diagnostic Details

- **Reproduction**: Add an asset to the `devkit` bundle's `core` preset and run `just test-affected`.
- **Expected / Actual**: Expected the worker to fix the tests the approved change affects. Actual: the harness
  bundle's integration test replaced the literal `core` preset line to build an older bundle, the replacement
  silently no longer matched, and the test failed with `SelectionError`; the file was outside the write scope.
- **Versions**: devkit 0.1.6 workspace at the unit's branch.
- **Conditions**: local-orchestrated Development worker with a payload write scope limited to the changed bundles.
- **Workarounds Attempted**: Recorded a worker problem; the Host granted and fixed the path in its own commit.
- **Related Assets**: `packages/devkit/tests/integration/bundles/harness/test_bundle.py`,
  `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/bundle.toml`, `SPEC-lightweight-general-subagent`.

## Evidence

```text
FAILED packages/devkit/tests/integration/bundles/harness/test_bundle.py::test_an_override_of_a_moved_asset_stops_applying_and_is_recreated_in_harness
SelectionError: asset devkit:devkit-run is not part of the selected presets: core
1 failed, 317 passed
```

- **Disposition**: Normal behavior: development-worker Tier B stops before a non-adjacent write by design, and the brittle fixture is already hardened (harness test_bundle regex with a count). Name foreseeable cross-package fixture tests in the initial scope instead; widening Tier B would need a proposal.
