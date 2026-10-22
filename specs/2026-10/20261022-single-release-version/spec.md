---
id: SPEC-single-release-version
title: One workspace release version
summary: "A root VERSION file drives workspace package versions and internal dependency pins for one release tag."
status: in-progress
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-single-release-version] One workspace release version

## 1. Problem Statement & Motivation

Preparing one release requires editing multiple versions and dependency pins by hand.
All workspace distributions should share the version of one release tag.

## 2. User Stories

- **US-1**: As a maintainer, I want to edit one version value and synchronize release metadata with one command.

## 3. Non-Goals

1. **Scope Excluded**: Publishing, pushing or creating a Git tag.
2. **Scope Excluded**: Changing the separately built devkit-embed model version or frontend npm package version.
3. **Scope Excluded**: Replacing Hatchling or adding a dynamic metadata plugin.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Synchronize workspace metadata

- **Given** root VERSION contains a plain X.Y.Z version without leading zeroes
- **When** the maintainer runs `just version-sync`
- **Then** every workspace project version and versioned internal dependency requirement equals VERSION, uv regenerates uv.lock, and exit is 0 with one VERSION result sentinel.
- **Then** existing formatting, external dependencies and the model version remain unchanged.

### [AC-02] Detect stale metadata before release

- **Given** VERSION differs from a workspace version or internal constraint
- **When** `just version-check` or `just release-build vX.Y.Z` runs
- **Then** it exits nonzero before building wheels and names the synchronization command.
- **Given** metadata is synchronized but the release tag differs from VERSION
- **When** the release build runs
- **Then** it exits nonzero before building wheels.

### [AC-03] Reject invalid input without mutations

- **Given** VERSION is missing or contains an invalid version
- **When** synchronization or checking runs
- **Then** it exits 2 without changing package metadata or uv.lock.
- **Given** metadata already matches VERSION
- **When** checking runs
- **Then** it exits 0 without writing files or invoking uv.

### [AC-04] Prepare 0.1.2

- **Given** the existing workspace
- **When** this change is complete
- **Then** all eleven workspace packages and their versioned internal requirements use 0.1.2, uv.lock is current, and release wheel metadata agrees with the single version.

### [AC-05] Synchronize bundled asset versions

- **Given** a workspace package contains src/**/bundle.toml manifests
- **When** synchronization or checking runs
- **Then** manifest versions are synchronized to VERSION or reported stale, preserving other manifest content.
