---
id: PROP-bundle-source-snapshots
title: Repository-committed bundle source snapshots
summary: "Copy reusable bundle sources into a local content package with provenance and explicit updates so consumer repositories can install private bundle content without upstream credentials."
status: draft
created_at: 2026-11-05
target_area: docs/capabilities/distribution/
priority: high
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/tests/
    - docs/capabilities/distribution/
    - docs/architecture/
    - docs/decisions/
    - docs/development/reference/
    - guides/install/
    - packages/devkit-dist/src/devkit_dist/bundles/devkit/
  excludes:
    - packages/devkit-core/
    - packages/devkit-spec/
    - .github/workflows/release.yml
    - scripts/release.sh
task_kind: feature
workflow: sdd-proposal
---

# [PROP-bundle-source-snapshots] Repository-committed bundle source snapshots

## 1. Background & Hypothesis

Private content packages shared through uv Git dependencies require upstream credentials in each consumer
environment. `CAP-DIST-in-repo-bundles` already supports ordinary content packages installed from local paths or a
workspace. `CAP-DIST-content-packages` discovers them through the same bundle entry points as installed wheels.
The bundle CLI exposes validation and planning, but no source snapshot or upstream refresh operation.

A repository-committed copy of upstream bundle sources could remove recurring private-content fetches while
retaining normal selection, synchronization, receipts and overrides. The hypothesis applies to private bundle
content; the devkit runtime and other Python dependencies still need their own installation path.

## 2. Technical Spike Questions

- **Q1 — Source completeness:** What is the minimum supported input: an installed content package, a local bundle
  root, or an authenticated upstream checkout? How are templates, included files and runtime imports accounted for?
- **Q2 — Packaging:** Should one snapshot package contain one bundle or several? How are bundle identity and Python
  module names preserved without duplicate discovery when upstream packages remain installed?
- **Q3 — Provenance and versioning:** How are source package/version, bundle version, available commit identity,
  content hash and local snapshot identity recorded without storing credentials or claiming an unknown commit?
- **Q4 — Refresh behavior:** How does an explicit refresh show additions, changes and removals, preserve project
  overrides, reject edited snapshot sources, and leave the previous snapshot usable after failure?
- **Q5 — Dependency boundary:** Which content-only bundles can be copied completely? How are bundles importing
  external Python modules or command plugins rejected or accompanied by explicit dependency requirements?
- **Q6 — Fresh clone:** What bootstrap is still required, and can installation and synchronization complete without
  contacting the private bundle origin when all declared runtime/build dependencies are otherwise available?

## 3. Proposed Design & Impact

Recommended starting direction, subject to Planning:

1. Read a complete bundle source from an explicitly supplied, accessible source. Package the source under a local
   content package, conventionally under `tools/`, and install it using the existing path/workspace mechanism.
2. Copy authoring sources and manifest data, including templates and required support files, rather than rendered
   `.devkit/managed/` copies or host projections. Validate supported content before accepting a snapshot.
3. Record credential-free provenance and deterministic content hashes. Keep upstream bundle versions separate from
   the local snapshot's identity; the consumer commit records which snapshot was adopted.
4. Refresh only on an explicit request. Present source differences, refuse silent overwrites of locally changed
   snapshot sources, and apply the new snapshot coherently. Use project overrides for consumer adaptations.
5. Resolve duplicate bundle discovery explicitly when replacing an installed upstream provider. Account for an
   upstream package that also provides other needed bundles or runtime plugins.
6. Reuse the installed-package loader and existing sync/receipt ownership. A second local bundle loader is not the
   starting direction. CLI names and any provenance file schema remain Planning decisions.

Illustrative outcome: an authorized maintainer snapshots a private team bundle into a consumer repository and
commits its local package plus provenance. A fresh consumer checkout installs that package and runs normal sync
without fetching the private team repository. A later maintainer refresh produces a reviewable source diff.

The expected runtime boundary is distribution. New cross-feature dependency edges are out of scope unless Planning
explicitly expands the declared boundary. Reconcile the result with `CAP-DIST-in-repo-bundles`,
`CAP-DIST-content-packages`, `CAP-DIST-workspace-ownership` and `CAP-DIST-sync-and-transactions`. Record an ADR if
Planning changes the accepted discovery or ownership decisions.

**Scope excluded:** copying the devkit runtime, arbitrary executable-package vendoring, eliminating all network
access, storing authentication material, background upstream tracking, automatic Git commits, a new package
registry, and automatic three-way merging of snapshot-source edits.

## 4. Lifecycle & Retirement Criteria

This is a queued draft with `medium` Planning and Development effort and estimated size `L`. Its priority is `high`
because it addresses repeated authentication friction. It does not depend on `PROP-selective-package-releases`:
source version plus content hash can identify a snapshot under either release policy.

Planning is ready for acceptance when supported bundle types, local packaging, provenance, duplicate-provider
handling, explicit refresh and failure behavior are specified. Confirm whether the motivating private dependency
contains content alone or runtime code before selecting the first supported scope.

Candidate Development acceptance checks:

- **AC1:** Given a supported private bundle and authorized source access, snapshot creation produces a valid local
  content package and credential-free provenance whose hashes match the copied sources.
- **AC2:** Given a clean consumer clone with runtime/build dependencies available and private-origin credentials
  absent, installing the local package and running sync reproduces the selected assets without fetching that origin.
- **AC3:** Given a changed upstream bundle, explicit refresh reports additions, changes and removals; unchanged
  inputs do not create content churn, and a failed refresh leaves the previous snapshot usable.
- **AC4:** Given local snapshot edits, duplicate bundle providers or unsupported external runtime dependencies, the
  operation reports an actionable condition without silently discarding content or claiming a complete snapshot.
- **AC5:** Given a project override, refresh preserves the adaptation and exposes upstream drift through the
  existing ownership mechanism.

Acceptance and handoff follow the existing proposal lifecycle. Narrow or reject the draft if the motivating
credential problem is confined to runtime installation and bundle snapshots do not address it.
