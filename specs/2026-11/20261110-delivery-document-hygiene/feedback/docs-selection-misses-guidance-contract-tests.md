---
id: FB-docs-selection-misses-guidance-contract-tests
title: Documentation selection misses a coupled guidance contract test
scope: repo
kind: friction
category: tool-error
target: scripts/affected_tests.py
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-10
---

# [FB-docs-selection-misses-guidance-contract-tests] Documentation selection misses a coupled guidance contract test

## 1. Friction / Question

- **Context**: Delivery role contracts moved intact from the workflow capability to a focused role capability.
- **Expectation**: The affected selection for that move exercises the guidance test that reads the contract.
- **Actual**: The document-only selection passed 17 tests without selecting the scratch-cleanup guidance test.
  A later full fallback found its hardcoded old capability path, despite the contract remaining intact.
- **Workaround**: Follow the new contract owner in the existing test, preserving every assertion, then run the
  targeted test and the complete selected fallback on the integrated target.
- **Suggestion**: Add the old and new delivery capability paths to the selection of their coupled guidance tests.
  Keep selection conservative without introducing a general dependency graph.

## Diagnostic Details

- **Reproduction**: The document Unit's source checks passed at `c46dfaca`; integrated full selection at `c399ec1a`
  failed the old-owner assertion in `test_scratch_cleanup_guidance.py`.
- **Expected / Actual**: Expected the document-only selection to include that assertion; it selected eight paths
  and passed 17 tests, while the full selection found one failure.
- **Versions**: Source revisions above; Python 3.12.8 on macOS.
- **Conditions**: A capability section moves, with a Python guidance test reading its former owner by path.
- **Workarounds Attempted**: The exact pointer repair passed all five tests in its file; no assertions were removed.
- **Related Assets**: `scripts/affected_tests.py`,
  `packages/devkit-spec/tests/integration/bundles/spec/test_scratch_cleanup_guidance.py`,
  `CAP-DLV-delivery-workflows`, `CAP-DLV-delivery-roles`.

## Evidence

```text
Document-only source verification: 17 passed; E2E selection empty.
Integrated full selection: 1 failed, 6539 passed, 4 skipped.
Failure: test_the_delivery_workflow_contract_mirrors_the_guidance read the old workflow capability.
Pointer-only repair: 5 passed; all positive and negative contract assertions retained.
```

- **Disposition**: scripts/affected_tests.py: a `docs/capabilities/delivery/` DATA row selects test_scratch_cleanup_guidance; verified by test_a_delivery_capability_selects_the_guidance_test_that_reads_it. The class of tests reading documents by path is delivered by `SPEC-select-tests-by-read-document-paths`.
