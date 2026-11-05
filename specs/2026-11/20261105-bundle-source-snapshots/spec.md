---
id: SPEC-bundle-source-snapshots
title: Repository-committed bundle source snapshots
summary: "Copy complete supported content providers into local packages with credential-free provenance and guarded explicit refresh, retaining normal discovery and sync."
status: in-progress
created: 2026-11-05
related_capabilities: [CAP-DIST-in-repo-bundles, CAP-DIST-content-packages, CAP-DIST-workspace-ownership, CAP-DIST-sync-and-transactions]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-bundle-source-snapshots] Repository-committed bundle source snapshots

## 1. Problem Statement & Motivation

Private content-package Git dependencies require upstream authentication in every consumer. An accessible source
checkout can instead become a committed local content package, using the existing loader and ownership contract.
`ADR-bundle-source-snapshots` settles whole-provider replacement, bounded dependency support and explicit refresh.
The retained source/Planning evidence and `PROP-bundle-source-snapshots-target` constrain this implementation.

## 2. User Stories

- **US-1**: As a maintainer, I can snapshot all bundles of an accessible content provider and install that local
  package without retaining a dependency on the private origin.
- **US-2**: As a maintainer, I can review upstream differences and explicitly adopt them without losing authored
  snapshot changes or project overrides.

## 3. Non-Goals

**Scope Excluded**: runtime-package vendoring, arbitrary builds/import execution, upstream access and credentials,
automatic Git commits, dependency/config/receipt edits, automatic sync, partial-provider shadowing, a second loader,
automatic merges of local edits and an all-network-free bootstrap promise. No new feature dependency is admitted.
Static import support is an inspectable subset, not a proof of arbitrary Python behavior.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Copy complete supported sources without execution

- **Given** a static content-only `src/` checkout with only resource-module `devkit.bundles` entry points, no runtime
  dependencies, and empty/docstring-only resource initializers.
- **When** `bundle snapshot SOURCE --to DEST --package NAME` runs within a consumer root.
- **Then** it returns one JSON result and exit 0, creates an ordinary version `0.0.0` local package with every bundle,
  preserves original names/versions, bytes, executable modes, variants, templates, bundle-local helpers and named
  license/notice files, and writes schema-1 `snapshot.json` with matching ordered hashes and no source paths, URLs,
  credentials or timestamps. Self-contained rule/gate code using stdlib, documented devkit APIs and in-tree relative
  imports is supported. Unsupported imports, dynamic import syntax, external declarative handlers, mixed entry points,
  dependencies, unsafe resources and unsupported build mappings return `BUNDLE_SNAPSHOT_UNSUPPORTED` or
  `BUNDLE_SNAPSHOT_INVALID` (exit 2) before destination writes. Inspection executes no provider code/build.

### [AC-02] Install the committed local wrapper independently

- **Given** a fresh consumer with devkit/build dependencies available and the private origin unavailable.
- **When** it replaces the original provider with the committed editable wrapper and runs normal locked sync.
- **Then** entry points reproduce selected sources without importing or fetching the original provider. A built-wheel
  consumer test verifies this with multi-bundle fixtures, and a harness-equipped fixture executes a supported rule.
  Dist-only checks still pass without devkit-agt; runtime/build availability remains a prerequisite.

### [AC-03] Review and apply an idempotent coherent refresh

- **Given** an intact snapshot and changed upstream files, executable modes, metadata or removed/added bundles.
- **When** `bundle refresh DEST --source SOURCE --check` previews, then apply supplies both `--expect` current digest
  and `--candidate` reviewed candidate digest.
- **Then** preview writes nothing and returns deterministic added/modified/removed paths plus digests. Matching apply
  coherently replaces payload and provenance; unchanged inputs write nothing, including after editable discovery has
  created bytecode. The nonrecursive aggregate excludes its own digest and provenance-file hash. A recoverable
  injected write/validation failure returns `BUNDLE_SNAPSHOT_WRITE_FAILED` (exit 2) and preserves the previous package.

### [AC-04] Refuse drift and unsupported state without content loss

- **Given** authored snapshot edits/additions, stale current/candidate digests, invalid/unknown provenance, symlinks,
  overlapping/protected/out-of-root destinations or duplicate installed bundle providers.
- **When** creation, preview, apply or ordinary discovery encounters that state.
- **Then** the snapshot command returns `BUNDLE_SNAPSHOT_CONFLICT` (exit 2), `BUNDLE_SNAPSHOT_INVALID` (exit 2), or
  `BUNDLE_SNAPSHOT_UNSUPPORTED` (exit 2), and normal discovery retains `BUNDLE_PACKAGE_INVALID` for duplicates.
  No authored content is silently overwritten; only `__pycache__` and `*.pyc` are excluded from local drift.

### [AC-05] Keep overrides and synchronization ownership separate

- **Given** a consumer project override and an intact snapshot.
- **When** it refreshes sources and then runs ordinary sync.
- **Then** refresh changes only the snapshot directory and returns subsequent actions; project config, lock, receipt,
  projections, overrides and Git stay untouched by that operation. Normal sync preserves the override and reports
  upstream drift through the existing ownership protocol.

### [AC-06] Explain complete provider replacement and metadata changes

- **Given** multiple source bundle entry points or a refresh adding/removing bundles.
- **When** snapshot/refresh completes or rejects a mixed runtime provider.
- **Then** JSON names the complete replacement set and exact install/provider-removal actions. Changed packaging
  metadata requires `uv sync --reinstall-package NAME`; selected removed bundles require explicit `devkit remove`.
  It neither silently removes selections nor invents discovery precedence. Unsupported metadata names its cause.

## 5. Assumptions & Verification Limits

The first supported input is an accessible local static Hatch-style content checkout; no private sample was supplied.
The public starter/catalog layouts establish input shape, while fixtures establish the exact dependency subset.
`--workspace-root` uses the existing consumer-root contract. No product screen changes. No performance claim.
Codex projection is emulated: absolute workdirs, per-operation approval, range audits and reviewer snapshots replace
native confinement. The Host verifies final landed content separately.
