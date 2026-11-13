---
id: SPEC-snapshot-subdirectory-source-commit
title: Record the source commit for snapshots of subdirectory providers
summary: "Restore verified snapshot source commits for providers below a Git repository root while preserving copied-input verification and explicit metadata refresh."
status: completed
created: 2026-11-13
related_capabilities: [CAP-DIST-in-repo-bundles]
related_usecases: [UC-snapshot-bundle-sources]
workflow: sdd-spec-bugfix
---

# [SPEC-snapshot-subdirectory-source-commit] Record verified subdirectory source commits

## 1. Problem Statement & Motivation

A bundle source snapshot of a committed content provider below its Git repository root records a null source
commit. The provider's copied inputs match HEAD, but `source_commit()` gives `ls-tree` repository-relative paths
while running from the provider directory. `CAP-DIST-in-repo-bundles` section 8 rules 4–7 and 10 already define
verified identity, deterministic preview, reviewed adoption and idempotence.

## 2. Defect Characterization

- **Current behavior**: a provider at `tools/content` produces `source.commit=null` because the relative path is
  resolved again from `tools/content`. Planning reproduced this at baseline `7161366d4c1908f13cea6e54c771c42244d9ad0d`.
- **Expected behavior and its basis**: record the captured HEAD when every copied input's bytes and normalized
  executable mode match that immutable commit, following `CAP-DIST-in-repo-bundles` section 8 rule 5.
- **Behavior to preserve**: root-provider identity, equivalent unlinked path spelling, captured-HEAD binding,
  null identity for modified/untracked inputs and explicit preview/reviewed refresh remain unchanged.
- **Reproduction conditions**: create a real Git fixture with its provider at `tools/content`, commit it, create
  a snapshot and compare recorded identity to HEAD. The retained subdirectory regression fails before the fix.

## 3. Non-Goals

- **Scope Excluded**: provenance schema, digest algorithm, result codes, refresh protocol and source-path admission changes.
- **Scope Excluded**: altered symlink handling, Git environment handling, timeout policy or automatic snapshot repair.
- **Scope Excluded**: package, feature dependency, architecture or lasting policy changes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Verified subdirectory identity and path equivalence

- **Given** a committed content provider below its Git repository root at `tools/content`.
- **When** creating a snapshot from its absolute path and previewing from an equivalent unlinked relative spelling.
- **Then** provenance records the captured HEAD, the digests match and preview reports no changed files.

### [AC-02] Copied-input verification remains intact

- **Given** a subdirectory provider whose copied files have uncommitted byte or executable-mode changes.
- **When** creating or refreshing a snapshot.
- **Then** provenance records null identity; a root provider still records its verified commit and the existing
  captured-HEAD race regression continues to reject bytes belonging only to a later commit.

### [AC-03] Metadata-only refresh uses the existing explicit protocol

- **Given** an unchanged committed subdirectory provider and a valid snapshot whose older identity is null.
- **When** previewing refresh, applying the reviewed digest pair and applying again.
- **Then** preview changes only `snapshot.json`, changes the digest and reports `packaging_changed=false` without
  destination writes; apply records HEAD with `BUNDLE_SNAPSHOT_UPDATED`, and the repeat returns
  `BUNDLE_SNAPSHOT_UNCHANGED` without changing any destination file modification time.

## 5. Living Spec Impact

The fix restores the existing capability and use case without a new public contract. The blueprint
`PROP-snapshot-subdirectory-source-commit-target` has no canonical targets. Planning evidence is retained at
`docs/materials/2026-11/20261113-snapshot-subdirectory-source-commit/source-commit-probe.md`.
