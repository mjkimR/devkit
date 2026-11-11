---
id: PLAN-derived-reference-scope-extension
spec: SPEC-derived-reference-scope-extension
---

# Technical Plan: `SPEC-derived-reference-scope-extension` Derived reference documents as recorded worker scope extensions

## 1. Constitution & Invariant Review

The Tier B rule in `CAP-DLV-delivery-roles` is a `MUST` decided by
`ADR-recorded-adjacent-path-extensions-for-development-workers`. A new ADR supersedes in part only its list of
qualifying Tier B classes; annotation, record, review severity, Tier C and inspection decisions stay in force.
No architecture `MUST`, feature edge or package boundary changes (`ARCH-05-2-components`).

## 2. Architecture Overview & Impact

- Target area: delivery role contracts in `docs/`, the spec bundle's worker and review guidance, and the worker
  inspection tests in `devkit-spec`.
- Inspection code is unchanged: `protected()` in the worker feature's extension service already rejects
  `AGENTS.md` and `CLAUDE.md` and does not reject READMEs, quick references or guides. The capability's list of
  recognizable protected classes gains the agent instruction files it omits.

## 3. Component Breakdown & Interface Contracts

- **Derived reference class** (Tier B, fourth qualifying kind): an exact existing quick-reference document, user
  guide, or the README of a package that owns a source file the unit changes. Only passages that restate a public
  name, command or behavior the task changes are edited; no new file or section. The reason names the changed
  symbol, command or contract ID.
- **Exclusions**: agent instruction files, bundle and agent assets and release documents stay outside Tier B.
- **Bundle wording**: shipped assets name the class generically (quick reference, user guide, changed package's
  README) and cite no repository document IDs; the capability names devkit's paths
  (`docs/development/reference/`, `packages/<name>/README.md`, `tools/<name>/README.md`, `guides/`).

## 4. Verification & Test Plan

- `uv run devkit rules check` on the unit and changed documents (AC-01).
- `uv run pytest packages/devkit-spec/tests/integration/bundles/spec/test_scope_extension_guidance.py` (AC-02).
- `uv run pytest packages/devkit-spec/tests/integration/features/worker/test_scope_extensions.py` (AC-03).
- `uv run devkit sync --check`, lint, type checks and `just test-affected`.
