---
id: SPEC-post-merge-hygiene
title: Repair post-integration package hygiene
summary: "Repair invalid seeded document metadata and align package installation, smoke verification and documentation with the monorepo."
status: in-progress
created: 2026-10-17
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-HARN-command-mount
related_stories:
  - US-adopt-in-an-existing-repository
workflow: sdd-spec-bugfix
---

# [SPEC-post-merge-hygiene] Repair post-integration package hygiene

## 1. Problem Statement & Motivation

The integrated SDD package works in the workspace, but new consumers receive three invalid architecture documents.
Installation and development instructions still describe the standalone repository, and the consumer smoke builds
its wheel without installing it. Architecture and CI documentation also disagree with the current repository.

## 2. Defect Characterization

- **Current behavior**: unquoted summaries containing a colon in three docs-skeleton files produce
  SPEC_DOCUMENT_INVALID warnings and disappear from the document index. The existing skeleton test checks the
  rules command's successful exit but never checks index completeness. The README points at the former repository
  and recipes absent from this monorepo. CI docs promise push/PR checks absent from the workflow definition.
- **Expected behavior and its basis**: the opted-in docs skeleton in `CAP-HARN-agent-guidance` consists of valid
  documents discoverable by the commands in `CAP-HARN-command-mount`; installation, CI and structure references
  describe the current repository and its existing automation.
- **Behavior to preserve**: docs seeding remains opt-in and writes only absent files; the base-only consumer smoke,
  runtime-only advisory install, existing command groups, hooks and model search keep working.
- **Reproduction conditions**: install the three local wheels in a fresh project, run devkit sync, add
  spec:docs-skeleton and load the document index. Its problems contain the three malformed architecture summaries.
  The regression test extends test_the_docs_skeleton_is_opt_in_and_passes_the_rules before modifying the seed.

## 3. Non-Goals

1. **Scope Excluded**: runtime API changes, dependency/version policy changes, CI trigger changes, and unrelated
   workflow or documentation redesign. CI documentation follows existing triggers.
2. **Scope Excluded**: automatically rewriting previously seeded consumer-owned documents.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Seeded documents remain discoverable
- **Given** a fresh consumer that explicitly selects spec:docs-skeleton
- **When** its document index is loaded
- **Then** no parsing problems exist and every seeded architecture file resolves by its stem ID.

### [AC-02] Wheel smoke exercises the integrated SDD package
- **Given** wheels built from every workspace package
- **When** the consumer smoke runs
- **Then** it preserves the base-only checks, installs devkit-spec by wheel path, verifies its command mount,
  checks opt-in seeding and all seeded architecture IDs, and runs the spec rules.

### [AC-03] Installation and development instructions match the monorepo
- **Given** the package README, root agent package list and release installation notes
- **When** their instructions and package sources are inspected
- **Then** devkit-spec uses the monorepo subdirectory or explicit release wheels, development recipes exist,
  and release notes include its wheel with its required base wheels.

### [AC-04] CI and architecture references match existing behavior
- **Given** the CI workflow, package metadata and canonical projection/worktree contracts
- **When** CI, container and deployment documentation is compared to them
- **Then** CI describes manual/reusable invocation and the actual rules command, devkit-spec appears in package
  topology and release artifacts, Codex skills use .agents/skills, and worktrees use sibling directories.

### [AC-05] Existing installation boundaries remain intact
- **Given** a consumer that has not opted into docs-skeleton, or one with an existing seeded document
- **When** it syncs and selects the skeleton
- **Then** no docs are created before opt-in, existing content is preserved, and base/advisory smoke checks pass.
