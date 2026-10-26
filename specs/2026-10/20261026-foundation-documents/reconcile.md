---
reconcile_id: REC-foundation-documents
spec: SPEC-foundation-documents
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-release-handbook.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/architecture/README.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-steering-documents-directory.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/README.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/steering/glossary.yaml
    resolution: modified
---

# [REC-foundation-documents] Reconcile: Steering documents for project-wide background

## Living Spec changes

- `CAP-DIST-context-and-playbooks` section 1 and 2: the context also lists the declared context documents; a new
  `documents` item states the declaration source (receipt-verified managed `bundle.toml`), the workspace read under
  the same lock without a hash check, the listing and symlink rules, the 4096-byte header prefix, `null` for every
  unreadable value and that `devkit-dist` caps nothing itself.
- `CAP-DIST-manifest-spec`: the manifest example shows `context_documents`, and Validation gains **Context
  documents**: an optional top-level string in the seeded `target` grammar, `BUNDLE_INVALID` otherwise.
- `CAP-DIST-workspace-ownership` rule 7: seeded files are never receipt-verified context files, but a declared context
  directory may list project files, seeded ones included (the amendment `ADR-bundle-context-lists-project-documents`
  names).
- `CAP-DOCS-document-model`: rule 3.1.9 **Steering documents** (flat, ID-free, outside index and search, glossary as
  first member, no namespace copy, who lists, bounds and checks them); the summary paragraph says the reference rule
  also reads steering files without graph edges.
- `CAP-DOCS-document-search`: the synonym file is `docs/steering/glossary.yaml` in rule 4, the example and
  `SPEC_GLOSSARY_INVALID`.
- `CAP-GOV-spec-rules`: twelve rules; the catalog row of `RULE-steering-documents` and section 3.14 with its findings,
  targeting and settings; `RULE-document-reference` section 3.3 names `docs/steering/glossary.md` for Owners and adds
  the steering cited-ID check; `related` lists the steering rule.
- `CAP-HARN-agent-guidance`: rule 1 says every role contract loads the spec context and the constitution names the
  steering list and its trigger; section 4.2 shows `documents` in the response and the constitution's section 2; the
  seeded tree shows `steering/glossary.md` and `glossary.yaml`.
- `CAP-DLV-release-handbook`: the generated glossary page reads the glossary at the source commit; section 4.3 states
  the steering path, the fallback to `docs/glossary.md` and `HANDBOOK_GLOSSARY_MISSING`, which section 4.2 lists with
  exit `2`.
- `CAP-DLV-delivery-workflows` rule 9: the reflection names `docs/steering/glossary.md`.
- `ARCH-08-2-resource-taxonomy`: the bundle context includes the titles and summaries of the declared directory.
- `ADR-steering-documents-directory` Consequences: it amends the glossary paths of `ADR-spec-package-on-devkit` and
  `ADR-writing-and-terminology-guidance`.
- `docs/README.md`, `docs/architecture/README.md` and `docs/development/reference/distribution.md`: the steering
  directory, the moved glossary link and the `documents` list.
- `docs/steering/glossary.md` and `glossary.yaml` (moved from the docs root with `git mv`): steering frontmatter, the
  row **Steering document** (Avoid: foundation, background) and its synonym cluster. The cluster uses the two-word
  forms `foundation document` and `background document`, because the single words would expand every query about the
  `devkit-core` foundation layer.

- No change: `CAP-VIEW-repository-viewer` specifies `docs/` grouped by chapter without naming the chapters, so the
  viewer's `Steering` group in place of `Glossary` (AC-15) needs no contract text.
- `reconcile-check-01` findings: `CAP-DIST-manifest-spec` and `ARCH-08-2-resource-taxonomy` now state the
  `context_documents` exception to "seeded files are never catalogued"; `CAP-GOV-spec-rules` section 3.3 limits
  "outside its scope" to the Owner check.

## Entrypoints

`CAP-DIST-context-and-playbooks` gains `usecases/context.py` and `services/bundles/context_documents.py`, the code
of its new `documents` contract. `CAP-DIST-manifest-spec` already lists `services/bundles/`, `CAP-GOV-spec-rules`
lists `features/governance/` and the bundle rules, and `CAP-DOCS-document-search` and `CAP-DOCS-document-model` cover
the search and documents features, so no other entrypoint changes.

## Source feedback

None: the proposal carried no FB IDs.

## Deferred work

None. `PROP-ux-documentation` (Planning, another branch) still names the old glossary path in its proposal text; it
adds `docs/steering/ux-objects.md` and its own wording on top of this change when it hands off.
