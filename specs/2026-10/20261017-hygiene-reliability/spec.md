---
id: SPEC-hygiene-reliability
title: Repair hygiene reliability and rule reference size
summary: "Preserve shared hook interpreters during sync, validate envelope revisions, retain finding severity, and split the rules reference."
status: completed
created: 2026-10-17
related_capabilities:
  - CAP-GATE-commit-gates
  - CAP-DLV-workflow-envelopes
  - CAP-GOV-rule-authoring
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-hygiene-reliability] Repair hygiene reliability and rule reference size

## 1. Problem Statement & Motivation

Sync replaces shared hook fallbacks with a disposable worktree interpreter. Envelope authoring accepts unknown
hexadecimal commit IDs and rejects reviewers' severity metadata. The rules reference exceeds its 400-line budget.
These problems make repository maintenance and review evidence harder to trust.

## 2. User Stories

- **US-1**: As a coding agent, I want durable hook fallbacks and verified review revisions so checks remain usable.
- **US-2**: As a reviewer, I want finding severity preserved without encoding it in issue text.
- **US-3**: As a rule author, I want a compact command reference linked to library examples.

## 3. Non-Goals

1. **Scope Excluded**: Integration dispatch, remote Git operations, host adapters and standalone Planning decisions.
2. **Scope Excluded**: Severity-based approval or exit-code changes and retrospective rewriting of old envelopes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Preserve a valid shared fallback during automatic sync
- **Given** shared managed hook entries with an executable interpreter that imports devkit.gate
- **When** automatic sync runs in a linked worktree and that worktree is subsequently removed
- **Then** each existing valid fallback is retained and the shared hooks can still run.

### [AC-02] Repair missing or invalid fallbacks and honor explicit installs
- **Given** an absent or invalid fallback, or an explicit gate install with a valid replacement interpreter
- **When** installation runs
- **Then** missing or invalid entries use the validated current interpreter, while explicit installs replace the fallback.

### [AC-03] Resolve envelope scope revisions in Git workspaces
- **Given** a Git workspace and authoring flags naming an existing hexadecimal head and base revision
- **When** any envelope authoring command writes diff_scope
- **Then** both supplied revisions are stored as full commit IDs; unknown or non-commit revisions fail with
  ENVELOPE_FLAG_INVALID and exit 2 before an envelope file is written.

### [AC-04] Preserve authoring outside Git and hexadecimal head syntax
- **Given** a workspace outside Git, or a head value that is not hexadecimal
- **When** envelope authoring runs
- **Then** outside Git existing lexical behavior is retained, and non-hexadecimal heads remain ENVELOPE_FLAG_INVALID.

### [AC-05] Retain optional severity metadata through review and reverify
- **Given** findings with optional non-empty string severity labels
- **When** findings are authored, loaded, rendered and carried into reverify
- **Then** labels are retained without affecting open-finding counts or checks; omitted severity remains omitted;
  empty, non-string severity and unknown finding keys are rejected.

### [AC-06] Split the rules reference without broken links
- **Given** the command reference and its library examples
- **When** library documentation is moved into a linked reference
- **Then** both references have at most 400 lines, existing inbound section links are updated, and the whole-workspace
  hygiene check reports no file-length violation for either reference.

## 5. Implementation Assumptions

- Severity is descriptive free-text metadata so existing reviewer vocabularies remain usable.
- Revision resolution is performed at CLI authoring, where the workspace root is known. Pure composition and historical
  loading do not consult Git, preserving portable evidence and library use.
- Automatic installation preserves a valid fallback per stage under the existing clone lock. Explicit install remains
  the supported way to select a replacement interpreter.
