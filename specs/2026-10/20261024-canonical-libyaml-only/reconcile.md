---
reconcile_id: REC-canonical-libyaml-only
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-definitions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
---

The implementation confirms the accepted parser boundary. Python frontmatter and standalone YAML reads use the shared LibYAML safe loader; missing binding is an execution error before memo reuse or format validation. Each owning format retains its schema, and frontmatter locations remain document-relative. Deployment guidance treats a compatible wheel and runtime binding check as the supported uv route without claiming universal platform support.

`packages/devkit-core/src/devkit_core/core/yaml.py` is recorded as an entrypoint on the five capabilities whose Python YAML read contracts use this shared boundary. `ARCH-07-deployment` is not entrypoint-bearing. Existing envelope, manifest and search implementation entrypoints remain listed.

`FB-canonical-c-yaml-contract` is resolved by this implementation; its disposition cites the full `just test-affected`, `just test-e2e`, `just smoke` and targeted integration verification. No deferred required work remains.
