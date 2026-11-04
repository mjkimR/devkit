---
reconcile_id: REC-namespace-steering
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-namespace-steering-directories.md
    resolution: modified
---

# Reconcile: SPEC-namespace-steering

## Impact

- `CAP-GOV-spec-rules`: 3.1 table row and 3.14 cover every registered namespace's `docs/packages/<name>/steering/`
  per directory (targeting, caps, directory-named messages, the glossary findings, unregistered directories
  skipped); the `RULE-document-reference` steering-files paragraph names the namespace directories.
- `CAP-DIST-context-and-playbooks` 2: the working directory and `--for` (`ARGUMENT_INVALID`), the
  `devkit.context_documents` provider contract, `documents` merging, `documents_elsewhere`, `notices` and
  `CONTEXT_DOCUMENTS_EXTENSION_FAILED` with the JSON-only channel rule.
- `CAP-DIST-manifest-spec` Context documents: providers may add directories; the manifest declares one.
- `CAP-DIST-workspace-ownership` 7: provider directories list project files as the declared one does.
- `CAP-DOCS-namespaces` 3.4 (the two rules over a namespace's `steering/`) and 4.5 (the `docs` provider contract).
- `CAP-DOCS-document-model` rule 9 and the bundle paragraph: a registered namespace keeps package background in its
  steering directory without a glossary file; the `docs` package registers the provider.
- `ARCH-05-2-components`: `devkit.context_documents` joins the public entry-point groups.
- `docs/steering/glossary.md` **Steering document**: both directories, both ADRs and the entry-point group.
- `CAP-HARN-agent-guidance` 4.2: the quoted `devkit get-context spec` result carries the two new keys
  (reconcile-check-01 P1).
- `docs/development/reference/distribution.md`: the `get-context` row and the `CONTEXT_DOCUMENTS_EXTENSION_FAILED`
  code row (reconcile-check-01 P2).
- `ADR-namespace-steering-directories` (accepted) and the "Superseded in part" pointer in `ADR-steering-documents`
  were written by the handoff transaction; no decision changed in Development. One wording repair of the ADR's
  provider-failure clause (the JSON-only channel; reconcile-check-01 P3) without changing its decision.

## Deferred work

Follow-ups the decision records, outside this spec's scope (`SPEC-namespace-steering` Non-Goals):

- A namespace copy of `docs/steering/ux-objects.md` for the UX rules work of `MS-monorepo-namespace-support`:
  `FB-namespace-ux-objects-copy`.
- The root glossary (`docs/steering/glossary.md`) versus package glossary (`docs/packages/<name>/glossary.md`)
  asymmetry, and namespace search synonyms: `FB-package-glossary-asymmetry`.

Entrypoints: `CAP-DOCS-namespaces` gains the provider module and `CAP-DIST-context-and-playbooks` the `get-context`
CLI adapter (`spec-entrypoints`); both are `modified` targets above.

## Source feedback

None: Planning carried no open feedback IDs into the proposal.
