---
reconcile_id: REC-justfile-standard-templates
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-command-design.md
    resolution: modified
  - file: docs/usecases/harness/UC-design-command-entrypoints.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: guides/install/bundle-recommendations.md
    resolution: modified
  - file: guides/install/existing-repository.md
    resolution: modified
  - file: guides/install/new-repository.md
    resolution: modified
  - file: packages/devkit-catalog/README.md
    resolution: modified
  - file: docs/proposals/PROP-multi-runtime-project-harness/proposal.md
    resolution: modified
  - file: docs/proposals/PROP-multi-runtime-project-harness/target-docs.md
    resolution: modified
---

# Reconcile: SPEC-justfile-standard-templates

CAP-HARN-command-design owns the creation guidance and its conditional opt-in delivery. Its use case covers
new entry points, existing-command reuse and preservation of public commands. CAP-DIST-content-packages records
the instruction-only packaging. Catalog/install recommendation tables identify the selection trigger; native
setup examples distinguish per-commit checks from full verification and preserve existing task interfaces.
The deferred runtime proposal now names this spec as the owner of its onboarding examples.

No runtime detector, scaffold CLI, automatic gate setup, mandatory recipe names or command-removal engine was
added. The new content root follows ARCH-05-2-components without changing an architecture contract or feature edge.
No new glossary term is introduced. The actual pilot repository was unavailable; a temporary Node fixture and
justfile parsing verify examples without claiming pilot evidence. Runtime adapter/external-rule work remains
explicitly deferred in PROP-multi-runtime-project-harness.

Entrypoints retain the new instruction for the capability and use case. Reject package-wide, test, metadata
and guide candidates; CAP-DIST-content-packages already owns catalog packaging through its existing entry point.
