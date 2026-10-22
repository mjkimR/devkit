---
id: SPEC-frontmatter-libyaml
title: Accelerate strict frontmatter parsing with libyaml
summary: "Use libyaml for ordinary frontmatter while retaining Python-loader validation and diagnostics."
status: planned
created: 2026-10-22
related_capabilities: [CAP-DOCS-document-model]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-frontmatter-libyaml] Accelerate strict frontmatter parsing with libyaml

## 1. Problem Statement & Motivation

The shared frontmatter loader uses Python YAML parsing even when libyaml is available. Switching the parser alone
accepts deeply nested YAML that the existing loader rejects and changes YAML diagnostics.

## 2. User Stories

- **US-1**: As a calling tool, I want faster frontmatter parsing without losing strict validation or diagnostics.

## 3. Non-Goals

- **Scope Excluded**: Document walking, memo formats, CLI output contracts, dependencies and YAML grammar changes.
- **Scope Excluded**: Replacing the Python loader's recursion behavior with a new public nesting limit.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Equal ordinary results
- **Given** valid frontmatter including dates, timestamps, merge overrides and Unicode
- **When** it is loaded with or without libyaml
- **Then** the resulting mappings and Python value types are equal.

### [AC-02] Strict diagnostics
- **Given** duplicate keys, invalid YAML, impossible dates or invalid header shapes
- **When** the header is loaded with or without libyaml
- **Then** the same FrontmatterError message is returned as the Python implementation.

### [AC-03] Deep nesting and aliases
- **Given** deeply nested syntax or recursive aliases
- **When** the header is loaded with libyaml
- **Then** deep syntax uses the Python loader, retaining its acceptance or nested-too-deep error, and recursive
  aliases retain the Python loader's behavior without an infinite validation walk.

### [AC-04] No-libyaml fallback
- **Given** PyYAML exposes no CSafeLoader
- **When** the frontmatter module is imported and used
- **Then** valid headers load and invalid headers fail through the Python loader without import errors.

### [AC-05] Measured improvement
- **Given** the same preloaded repository headers on the same machine
- **When** nine alternating runs compare the Python loader and the guarded libyaml implementation
- **Then** mappings are equal and the libyaml median parsing time is at least twice as fast.

## Source feedback

`FB-strict-frontmatter-loader-without-libyaml`: implement and verify the optional C parser, strict errors,
deep nesting behavior and Python fallback. Resolve the source only after verification.

## Assumptions

The base is main at b5cfd8d27fed749003d0ed8ca8e12d1b5554e1e0. This unit has no direct prerequisites.
