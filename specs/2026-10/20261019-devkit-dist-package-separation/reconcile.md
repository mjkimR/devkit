---
reconcile_id: REC-devkit-dist-package-separation
feature: SPEC-devkit-dist-package-separation
status: resolved
targets:
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/architecture/ARCH-03-context.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-05-3-command-plugins.md
    resolution: modified
  - file: docs/architecture/ARCH-05-4-distribution-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/architecture/README.md
    resolution: modified
  - file: docs/capabilities/compact/CAP-CMP-bounded-execution.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/search/CAP-SRCH-document-search.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
  - file: docs/development/reference/README.md
    resolution: modified
  - file: docs/development/reference/advisory.md
    resolution: modified
  - file: docs/development/reference/compact.md
    resolution: modified
  - file: docs/development/reference/core.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/development/reference/gate.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/development/reference/search.md
    resolution: modified
  - file: docs/development/setup.md
    resolution: modified
---

# Reconcile: SPEC-devkit-dist-package-separation

The split of `devkit-agt` into `devkit-dist` and `devkit-agt` (`ADR-dist-foundation-ownership`,
`ADR-dist-module-split`, `ADR-dist-command-composition`, `ADR-dist-config-receipt-ownership`,
`ADR-dist-bundles-compatibility`) is reflected in place in the Living Spec:

- **Architecture**: `ARCH-05-1-containers` (three lockstep wheels, `devkit-dist` and `devkit-agt` sections),
  `ARCH-05-2-components` (per-wheel layering, dependency inversions including `devkit.config_tables`),
  `ARCH-05-3-command-plugins` (devkit-agt as first-party plugin, lookup precedence, the name-only harness list and
  `HARNESS_COMMAND_UNAVAILABLE`, tool installation form), `ARCH-05-4-distribution-components` (owner wheel, reserved
  table templates, `engines.py`, `guide/` versus `harness_guide`), `ARCH-07-deployment` (release assets, Git sources,
  lockstep, tool installation), `ARCH-01-introduction-and-goals`, `ARCH-03-context`, `ARCH-08-2-resource-taxonomy`
  and the architecture README.
- **Capabilities**: `CAP-DIST-content-packages` (the two wheels, built-in bundles including the `harness` bundle
  contract, the standalone signals), `CAP-DIST-sync-and-transactions` (receipt tool `devkit-dist` and the two-sided
  notice, reserved tables, `devkit.config_tables`, built-in auto-selection, the engine notice),
  `CAP-DIST-workspace-ownership` (format owners, overrides of an asset in another bundle), `CAP-DIST-manifest-spec`
  (engines of rule, gate and workflow kinds), `CAP-DIST-in-repo-bundles` (both mirrors, dependency rule),
  `CAP-DIST-context-and-playbooks`, `CAP-DIST-agent-projections` (entrypoint paths), `CAP-HOST-lifecycle-observation`,
  `CAP-SRCH-document-search`, `CAP-CMP-bounded-execution` (`harness:run`), `CAP-INT-mcp-services`.
- **Development references**: the module index gains the owning wheel; core (new error and directives), distribution
  (notices, template, bundles shipped), compact, search, host, gate, advisory, rules, setup and CI/CD.

Entrypoints (`spec-entrypoints` review): `CAP-DIST-content-packages` declares `discovery.py` and the
`harness_guide` area, `CAP-DIST-sync-and-transactions` adds `engines.py` and `config_template.py`; the other derived
candidates were the bundle's broad task boundaries (folded into whole package directories) and were not written.

No story changes: the stories under `docs/stories/` describe SDD and governance behavior the split leaves unchanged.
No ADR changes: the five ADRs stay as accepted; the inaccurate premise about first-party rule assets
(`advisory:python`) is recorded as a spec assumption and as feedback `FB-adr-standalone-rule-asset-claim`, and the
Living Spec states the exception. Outside the Living Spec, one link path in the evaluation material
`docs/materials/evaluations/hybrid-binaries.md` follows the moved `playbook_search.py`.

No deferred work is retained: every acceptance criterion is implemented; the cross-bundle preset hint stays a
non-goal settled by the user.
