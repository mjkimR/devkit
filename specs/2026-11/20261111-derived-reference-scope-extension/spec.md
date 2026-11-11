---
id: SPEC-derived-reference-scope-extension
title: Derived reference documents as recorded worker scope extensions
summary: Let a Development worker record an exact existing quick-reference, package README or guide file that restates a changed public name or behavior as a Tier B extension, keeping AGENTS.md and protected classes out.
status: completed
created: 2026-11-11
related_capabilities:
  - CAP-DLV-delivery-roles
related_usecases:
  - UC-drive-development-to-integration
workflow: sdd-spec-feature
---

# [SPEC-derived-reference-scope-extension] Derived reference documents as recorded worker scope extensions

## 1. Problem Statement & Motivation

A Development worker's write scope is an estimate made before the work. Its purpose is to anticipate the files a
unit touches and to protect files the unit must not change; collisions caused by a later extension are an accepted
cost. `ADR-recorded-adjacent-path-extensions-for-development-workers` lets a worker record an exact adjacent file
(Tier B), but the only documents it admits are existing Living Spec documents whose reason names a contract ID.

The repository guide requires quick references, package READMEs and guides to stay in step with the Living Spec and
the packages. These derived documents restate public names and behavior without being Living Spec documents, so
workers judge them inconsistently: one unit admitted `docs/development/reference/distribution.md` and another a
package README by naming a restated contract ID, while another left `docs/development/reference/core.md` without
the row for a new public module because it restated no contract ID. The Host then fixed it in a separate commit.

- **US-1**: As a Host, I want a Development worker to update the derived reference document that restates what its
  task changed, so that the unit lands with its references in step and without a recovery commit.
- **US-2**: As a reviewer, I want one stated class with a named reason, so that I judge the extension the same way
  in every unit.

The change extends a step of `UC-drive-development-to-integration` (the worker's Development turn).

## 2. Source feedback

- `FB-core-reference-row-for-memo-helper` (resolved): evidence of the inconsistent judgment; it stays terminal.

## 3. Non-Goals

1. **Scope Excluded**: agent instruction files (`AGENTS.md`, `CLAUDE.md`), bundle and agent assets (skills,
   playbooks, instructions, role files, guidance fragments) and release documents stay outside Tier B.
2. **Scope Excluded**: a README of a package that owns none of the unit's changed sources, a new document, a new
   section and edits beyond the passages restating the changed name or behavior stay outside the class.
3. **Scope Excluded**: other-package tests, accepted ADR changes and other Tier C classes keep their current rules.
4. **Scope Excluded**: no conflict check against other active units' boundaries is added; collisions from an
   extension are accepted.
5. **Scope Excluded**: inspection gains no semantic check of the new class; it remains a reviewer judgment.

## 4. Acceptance Criteria & Behavioral Contracts

This changes a `MUST` in `CAP-DLV-delivery-roles`; an ADR that supersedes in part
`ADR-recorded-adjacent-path-extensions-for-development-workers` is required before the capability changes.

### [AC-01] The decision and capability state the derived reference class

- **Given** the decision records and `CAP-DLV-delivery-roles`
- **When** `uv run devkit rules check` runs on the changed documents
- **Then** an accepted ADR supersedes in part `ADR-recorded-adjacent-path-extensions-for-development-workers` for
  the qualifying Tier B classes, the earlier ADR carries the identical pointer statement, and the capability's
  Tier B rule admits an exact existing quick-reference document, guide or the README of a package or tool that owns a changed source whose edited
  passages restate a public name, command or behavior the task changes, with a reason naming that symbol, command
  or contract ID
- **And** the check reports 0 violations for these documents

### [AC-02] Shipped worker and review guidance carry the same class in both environments

- **Given** the spec bundle rendered for `local` and `cloud`
- **When** `test_scope_extension_guidance.py` runs
- **Then** the development worker role, the `spec-review` scope extension reference and the `spec-delegate` worker
  reference each state the derived reference class, its reason requirement, the restating-passage limit and the
  exclusion of agent instruction files, and the test passes for both environments

### [AC-03] Inspection accepts a recorded derived reference extension and keeps agent instruction files protected

- **Given** a unit whose task annotates `docs/development/reference/core.md`, `packages/example/README.md` or
  `guides/INSTALL_GUIDE.md` as a scope extension with a matching worker record
- **When** `devkit spec worker inspect` runs
- **Then** `checks.scope_extensions` is `pass` and the exit code is 0
- **And** the same evidence for `AGENTS.md` or `packages/example/CLAUDE.md` fails `checks.scope_extensions` with
  `SPEC_WORKER_SCOPE_EXTENSION_INVALID`
