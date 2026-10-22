---
id: SPEC-entrypoints-directory-apply
title: Apply directory code entrypoints
summary: Allow devkit spec entrypoints derive --apply with a directory path (--code ending in /) to record the directory entrypoint directly instead of expanding all matching candidate files.
status: planned
created: 2026-10-22
related_capabilities:
  - CAP-TRACE-code-entrypoints
related_usecases:
  - UC-keep-the-living-spec-consistent
workflow: sdd-spec-feature
---

# [SPEC-entrypoints-directory-apply] Apply directory code entrypoints

## 1. Problem Statement & Motivation

The `spec-entrypoints` skill instructs agents to "choose a directory (trailing `/`) only when the document owns the whole package". However, `devkit spec entrypoints derive` treated `--code` strictly as a filter matching candidate files from `tasks.md` boundaries. When `--apply --target <doc> --code <package>/` was passed with a trailing slash, all individual candidate files under that directory were written to the document's `entrypoints` list instead of the directory itself (`FB-entrypoints-directory-code-expands-to-files`).

Supporting directory-level `--code <dir>/` application ensures that documents owning a package or feature subtree can declare a clean single directory entrypoint through `derive --apply` without manual frontmatter edits.

## 2. Source Feedback

- [FB-entrypoints-directory-code-expands-to-files]: Entrypoints apply cannot write the directory entry the skill recommends.

## 3. User Stories

- **US-1**: As a developer or agent running `devkit spec entrypoints derive --apply`, I want passing `--code <dir>/` with a trailing slash to apply `<dir>/` as a single directory entrypoint on the targeted document and fold descendant candidates into it.
- **US-2**: As a developer, I want existing `--code <file>` filters without a trailing slash to keep their current behavior, preserving exact file filtering and selective entrypoint application.

## 4. Non-Goals

1. **Scope Excluded**: Automatic promotion of arbitrary subtrees into directory entrypoints without an explicit trailing `/` in `--code`.
2. **Scope Excluded**: Changing the underlying path normalization rules of `CAP-TRACE-code-entrypoints` (entrypoints frontmatter continues to compare normalized paths while rendering directory entrypoints with a trailing `/`).

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] Derive folds candidate files under directory `--code` with trailing slash
- **Given** a spec bundle whose `tasks.md` declares multiple code boundaries under directory `src/pkg/`
- **When** `devkit spec entrypoints derive --spec <dir> --code src/pkg/` is run
- **Then** `src/pkg/` appears as a candidate pair for matching documents, and descendant files under `src/pkg/` are marked as folded into `src/pkg`.

### [AC-02] Apply records directory entrypoint with trailing slash and collapses descendants
- **Given** a capability document targeted by `--target <CAP-ID>` and candidate files under `src/pkg/`
- **When** `devkit spec entrypoints derive --spec <dir> --apply --target <CAP-ID> --code src/pkg/` is executed
- **Then** `src/pkg/` is written to the document's `entrypoints` frontmatter, and individual candidate files under `src/pkg/` are not written.

### [AC-03] Bare path filters without trailing slash preserve existing behavior
- **Given** candidate files under `src/pkg/`
- **When** `devkit spec entrypoints derive --spec <dir> --code src/pkg` (without trailing slash) or `--code src/pkg/file.py` is run
- **Then** matching individual candidate files are retained without synthesizing a directory entrypoint.

### [AC-04] Directory code with trailing slash must name an existing directory
- **Given** a `--code` argument ending with `/` that points to a non-existent path or a non-directory file
- **When** `devkit spec entrypoints derive` is executed
- **Then** the command refuses with an advisory indicating the path is not an existing directory.
