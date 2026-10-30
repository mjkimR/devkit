---
id: FB-citation-test-not-selected-by-docs-changes
title: A docs change that makes a bundle citation resolve does not select the citation test
scope: repo
kind: suggestion
category: other
target: scripts/affected_tests.py
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-citation-test-not-selected-by-docs-changes] A docs change that makes a bundle citation resolve does not select the citation test

Affected test selection gap for a test that reads repository data.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `tools/devkit-dev/tests/integration/test_bundle_citations.py` reads `docs/` and `specs/` to
  decide which backticked IDs in shipped bundle text resolve here. `just test-affected` selects it through its
  imports of the shipping modules, so a bundle text change selects it, but a `docs/` change (a new document whose ID
  a bundle already cites as an example) does not: the `DATA` map of `scripts/affected_tests.py` lists other tests for
  `docs/`.
- **Proposed Procedure**: Add the test to the `docs/` entry of `DATA` (and a `specs/` entry if one is wanted).
- **Expected Benefit**: The collision is caught by the development run instead of the nightly full CI.
- **Cost & Risk**: One more test (about 0.3 s) on every `docs/` change.
- **Attempted**: Hypothesis; the script was outside the write scope of `SPEC-shipped-bundle-citations-and-doc-fixes`.

## Evidence

```text
scripts/affected_tests.py DATA "docs/" -> test_documented_codes.py (three packages), test_docs.py, test_library.py
select() on a bundle file of each shipping package -> partial selection including test_bundle_citations.py
```
