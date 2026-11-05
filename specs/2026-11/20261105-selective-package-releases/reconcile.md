---
reconcile_id: REC-selective-package-releases
status: resolved
targets:
  - file: README.md
    resolution: modified
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-3-command-plugins.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-package-ownership-and-release-version.md
    resolution: modified
  - file: docs/decisions/2026-11/20261105-selective-package-versions.md
    resolution: modified
  - file: docs/development/reference/advisory.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: packages/devkit-advisory/README.md
    resolution: modified
  - file: packages/devkit-cli/README.md
    resolution: modified
  - file: packages/devkit-dist/README.md
    resolution: modified
  - file: packages/devkit-starter/README.md
    resolution: modified
  - file: packages/devkit/README.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-document-system.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-mcp-runtime-and-shared-artifacts.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-rules-run-workspace-cache.md
    resolution: modified
---

# Reconcile: `SPEC-selective-package-releases`

## Retained contracts

`ARCH-07-deployment` owns shared release vs actual package/bundle versions, canonical wheel comparisons,
exact-pin fixed-point propagation, verified original artifacts, bootstrap, deterministic plans, incomplete
preparation, retry and metadata conflict refusal. Completed-plan rollover verifies provenance and never unwinds
published edits. Logical current versions reject an older inconsistent baseline.

`CAP-DIST-content-packages` and `CAP-DIST-in-repo-bundles` retain package isolation and one-commit Git sources;
wheel commands use each inventory artifact's original URL. `ADR-selective-package-versions` restates its accepted
policy; the old ADR preserves all ownership, layering, import, configuration, bundle and CLI version-source clauses.
Its same-version qualifiers are replaced throughout the affected outcome clauses.

Host-admitted exact targets `ARCH-01-introduction-and-goals`, `ARCH-05-1-containers`,
`ARCH-05-3-command-plugins` and `CAP-CLI-agent-cli-toolkit` change only release/equality qualifiers and traces.
The CLI public names, semver policy and installed dist version source remain. Release/package/inventory terminology
is registered in the existing glossary; no existing unrelated row or synonym file changed.

Root and package READMEs and distribution/advisory quick references use selected actual versions and inventory URLs.
Existing installation guides and shipped source instructions already use one Git source and contain no conflicting
same-version assertion; no source bundle asset changed. They need no sync output or contract rewrite.
The model artifact and viewer npm policies remain independent.

The Host-admitted `ADR-document-system` and `ADR-mcp-runtime-and-shared-artifacts` version qualifiers are partially
superseded by `ADR-selective-package-versions`, with exact notices and outcome traces; all subsystem/approval
choices remain. `ADR-rules-run-workspace-cache` retains its no-shim/no-consumer/cache decisions and drops only the
obsolete trailing lockstep rationale. The accepted-ADR audit found no further current equality requirement.

## Verification

- All six ACs map to completed tasks and release regressions. HIGH code review rounds 1 and 2 were fixed and closed;
  fresh round 3 passed with no new or recurring finding.
- `UV_OFFLINE=1 just test-affected --base 0e17cd72d96d5111e39731291241472d7cd3f87b` preserved mode=full:
  6668 passed, 15 skipped, 152.80 seconds at code HEAD 93a3be2f0ca59da8e8d957256718a0f42ba3f337.
- Package lint/format and types, scoped release-script lint/types, and committed branch rules passed.
  The cycle tests prove older-baseline refusal, N to N+1 preparation, invalid completion provenance refusal,
  preservation of comparison-time authored dependency/comment/tool edits, unpublished mismatches and new packages.
- Local original-wheel fixtures measured the policy count in one process: lockstep assigns all five workspace
  packages; a dist bundle change selects two and retains advisory/core/CLI. No latency improvement is claimed.
- Clean wheel, Git and tool fixtures resolve exact selected versions outside the workspace with optional extras;
  the existing full suite retains advisory standard-library and dist-without-agt checks.
- The active-doc scan covers space-separated, line-wrapped and hyphenated equality wording in prose and diagrams and has no remaining release-equality assertion. Historical bootstrap terminology and the
  retained test filename test_lockstep.py are intentional.

## Entrypoint review and limits

Entrypoint derivation is reviewed at this stage. Capability edits restate release policy and install guidance;
existing capability runtime doorways remain applicable. No release helper is added as an unrelated runtime doorway.

There is no deferred implementation or changed acceptance criterion. Real historical original assets were not
provided or fetched, and no release/tag/publication occurred. First use requires explicit verified originals;
fixture checks establish local behavior, not remote availability. Metadata preservation is a pre-write captured-input
comparison; it provides no global lock or unrelated source snapshot guarantee. Codex role boundaries are emulated
by absolute worktree scopes and pre/post snapshots, not native confinement.
