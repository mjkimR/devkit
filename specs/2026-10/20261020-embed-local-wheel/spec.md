---
id: SPEC-embed-local-wheel
title: embed-local-wheel
summary: "Commit the devkit-embed model wheel into the repository and switch package sources to a local path dependency to eliminate network synchronization checks."
status: planned
created: 2026-10-20
related_capabilities: ["CAP-SRCH-document-search"]
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-embed-local-wheel] Commit devkit-embed Wheel to Repository

## 1. Problem Statement & Motivation

Currently, `packages/devkit-dist/pyproject.toml` defines the dependency source for `devkit-embed` as a direct HTTP URL pointing to a GitHub release asset (`https://github.com/mjkimR/devkit/releases/download/v0.1.0/devkit_embed-0.1.0-py3-none-any.whl`). Because `uv` treats direct HTTP URL dependencies as potentially mutable external resources, `uv run` unconditionally queries remote HTTP caching headers (triggering DNS resolution) during automatic environment synchronization.

In restricted-network environments, sandboxed agent runs, and offline developer checkouts, this DNS lookup fails before any command can run, blocking basic operational commands such as `devkit get-context` or `just check` even though the package is already present in the local virtual environment. Committing the prebuilt 14 MB wheel directly into the repository and switching `[tool.uv.sources]` to a local file `path` reference eliminates all remote HTTP lookups, ensuring full offline and sandbox reliability.

### Source feedback

- `FB-planning-context-command-can-trigger-unavailable-sync`: Planning context command triggers unavailable dependency synchronization over remote GitHub DNS.

## 2. User Stories

- **US-1**: As a developer or agent running in an air-gapped or sandboxed environment, I want `uv run` and devkit commands to execute without network checks for `devkit-embed`, so that operations succeed reliably without DNS failures.
- **US-2**: As a maintainer running test and smoke suites (`just smoke`, `just test-dist`), I want tests to resolve `devkit-embed` from the committed wheel, so that local verification never depends on remote release asset availability.

## 3. Non-Goals

1. **Model Regeneration**: Does not modify or re-train the underlying `potion-base-8M` embedding model weights or tokenizer.
2. **PyPI Publishing**: Does not publish `devkit-embed` to public PyPI as part of this specification.
3. **Workspace Inclusion**: Does not convert `models/devkit-embed` into an editable workspace member; the prebuilt wheel remains the installed artifact.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Committed Model Wheel
- **Given** the repository checkout,
- **When** checking `models/devkit-embed/wheels/`,
- **Then** `devkit_embed-0.1.0-py3-none-any.whl` is present and tracked in Git, matching SHA-256 `2b8534b60d85e36c2027e2c0d13d110289fa877b9c0b2639b8c4daedbe461f38`.

### [AC-02] Local Path Source Configuration
- **Given** `packages/devkit-dist/pyproject.toml` and root `pyproject.toml`,
- **When** inspecting `[tool.uv.sources]`,
- **Then** `devkit-embed` references the local committed wheel via `path`, with no remote `url` dependency.

### [AC-03] Offline Execution Verification
- **Given** a network-isolated environment without DNS or internet access,
- **When** `uv run` executes commands that import `devkit_embed` or run devkit tools with search capabilities,
- **Then** the command completes successfully with exit code 0 and triggers no network calls or DNS errors.

### [AC-04] Verification Scripts and Smoke Tests
- **Given** workspace development scripts (`scripts/_lib.sh`, `scripts/smoke.sh`, `scripts/release.sh`),
- **When** resolving the model wheel path for packaging and consumer tests,
- **Then** the scripts resolve the committed local wheel file path instead of parsing a remote release URL.

### [AC-05] Living Spec and Feedback Resolution
- **Given** `CAP-SRCH-document-search.md`, `README.md`, and `FB-planning-context-command-can-trigger-unavailable-sync`,
- **When** the specification is implemented,
- **Then** the Living Spec documents reflect the committed repository wheel source, and the feedback entry is recorded as resolved.
