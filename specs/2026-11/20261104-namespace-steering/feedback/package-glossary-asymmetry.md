---
id: FB-package-glossary-asymmetry
title: The root glossary lives in the steering directory but a package glossary does not, and namespace synonyms are not read
scope: repo
kind: suggestion
category: other
target: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-11-04
---

# [FB-package-glossary-asymmetry] The root glossary lives in the steering directory but a package glossary does not, and namespace synonyms are not read

The nature of the observation: a layout asymmetry between the root and namespace glossaries. Deferred work of
`SPEC-namespace-steering` (`ADR-namespace-steering-directories`, Follow-ups).

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the root glossary is `docs/steering/glossary.md` with `docs/steering/glossary.yaml` as the
  search synonyms; a package glossary stays at `docs/packages/<name>/glossary.md`, and `RULE-steering-documents`
  reports a `glossary.md` or `glossary.yaml` in `docs/packages/<name>/steering/`. Search synonyms are read from the
  root file only.
- **Proposed Procedure**: decide whether a package glossary moves into its steering directory (listed in that
  package's context, with `living_path` and every consumer updated) and whether `devkit docs search` reads a
  namespace's synonyms; or record the asymmetry as intended in `CAP-DOCS-namespaces`.
- **Expected Benefit**: one rule for where a glossary lives; package synonyms reach search.
- **Cost & Risk**: moving the package glossary changes the `living_path` mapping of `glossary.md` and every
  consumer's path; a second synonyms source changes search ranking.
- **Attempted**: hypothesis; moving package glossaries and namespace synonyms are non-goals of
  `SPEC-namespace-steering`.

## Diagnostic Details

- **Reproduction**: not applicable (a design follow-up).
- **Expected / Actual**: not applicable.
- **Versions**: devkit workspace at the Development branch of `SPEC-namespace-steering`.
- **Conditions**: a workspace with registered namespaces keeping package glossaries.
- **Workarounds Attempted**: not attempted; the package glossary keeps working at its current path.
- **Related Assets**: `living-spec-writing` (Glossary), `RULE-steering-documents`, `CAP-DOCS-namespaces` 4.5,
  `devkit_docs.features.documents.services.namespaces.living_path`.

## Evidence

```text
ADR-namespace-steering-directories, section 5 Follow-ups: "The asymmetry between the root glossary
(docs/steering/glossary.md) and package glossaries (docs/packages/<name>/glossary.md); namespace search synonyms."
```
