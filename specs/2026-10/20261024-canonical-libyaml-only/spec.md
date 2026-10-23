---
id: SPEC-canonical-libyaml-only
title: Require libyaml for consistent YAML parsing
summary: "Require PyYAML LibYAML safe parsing for Python runtime frontmatter and standalone YAML inputs. Define installation eligibility, distinct missing-binding failures, and parser and fixer verification."
status: in-progress
created: 2026-10-24
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-DLV-workflow-envelopes
  - CAP-DLV-workflow-definitions
  - CAP-DIST-manifest-spec
related_usecases:
  - UC-find-the-right-documents
workflow: sdd-spec-feature
---

# [SPEC-canonical-libyaml-only] Require libyaml for consistent YAML parsing

## 1. Problem Statement & Motivation

Python YAML readers currently choose different parsers. The frontmatter reader prefers LibYAML but routes scanner-sensitive or deeply nested input through PyYAML's Python loader and retries C-parser errors through Python. Standalone workflow records, CLI YAML, glossary data, bundle invocation settings and node-based fixers also select loaders independently. Input acceptance and parser locations can therefore depend on the call site or whether PyYAML's optional C binding is installed.

This feature gives Python runtime YAML reads one safe LibYAML parser boundary. It keeps schema validation owned by each format and preserves targeted text edits. If the binding is missing, an operation that reads YAML fails as an execution error before using a cached YAML result or writing a fixer output.

The accepted parser decision is `ADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries`. The source feedback `FB-canonical-c-yaml-contract` remains open until this feature is implemented and verified.

## 2. User Stories

- **US-01**: As a developer or coding agent, I want every Python YAML reader to use the same LibYAML implementation so that a document has consistent acceptance and parser locations across validation, workflow and distribution commands.
- **US-02**: As a developer or coding agent, I want a clear installation error when LibYAML is unavailable so that a command does not misreport a dependency problem as invalid user YAML or silently skip a document.
- **US-03**: As a developer or coding agent, I want existing metadata fixers to preserve unrelated text so that adopting one parser does not rewrite comments, formatting or document bodies.

## 3. Non-Goals

1. **Browser YAML parsing** — Scope Excluded: changing `packages/devkit-viewer/frontend/` or its npm YAML parser. Browser rendering does not validate Python documents.
2. **New YAML language** — Scope Excluded: implementing YAML 1.2, a custom scanner grammar or another fallback parser. LibYAML's accepted syntax defines Python runtime parsing.
3. **Universal format schemas** — Scope Excluded: applying frontmatter duplicate-key, mapping or string-key checks to standalone YAML formats. Each format keeps its existing schema and validation rules.
4. **Generic authoring and serialization** — Scope Excluded: adding a generic metadata-writing CLI, replacing output-only serializers or reformatting complete YAML documents. Existing typed operations and targeted fixers remain the authoring paths.
5. **Platform and dependency guarantees** — Scope Excluded: adding operating-system support, a full platform CI matrix, a PyYAML extension metadata guarantee or source-build toolchain management. Installation guidance documents compatible wheels and verifies the binding at runtime.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Python readers share the safe C parser
- **Given** each inventoried Python YAML value-load, node-compose and scalar round-trip path
- **When** the path parses YAML
- **Then** it uses the shared `devkit_core.core.yaml` LibYAML safe boundary and keeps its existing format-specific schema; a source audit finds no production Python-loader fallback in scope.

### [AC-02] Missing binding is an execution failure
- **Given** PyYAML has no usable `yaml.CSafeLoader`
- **When** a scoped YAML read, composition, cold or warm document-index load, or fixer runs
- **Then** it raises `YAML_BINDING_UNAVAILABLE` through the existing CLI or MCP advisory boundary with exit code `2` and a deterministic reinstall action; JSON mode emits one error object, and no invalid-document warning, empty hint, fixer success or file write substitutes for the failure.
- **And** non-YAML help and text-only frontmatter `locate()` remain usable without the binding.

### [AC-03] Frontmatter keeps its schema and reports parser locations
- **Given** Markdown with valid or malformed frontmatter, including duplicate keys, non-mapping values, non-string keys, dates, aliases, recursive values and delimiter edge cases
- **When** shared parsing or document indexing runs with LibYAML available
- **Then** existing frontmatter validation and value types remain; malformed documents retain `SPEC_DOCUMENT_INVALID` behavior while valid documents remain indexed, and a parser mark is reported as a 1-based document line and column when available.

### [AC-04] Standalone YAML keeps format-specific validation
- **Given** workflow decisions or envelopes, CLI-supplied YAML, glossary YAML, proposal reports or bundle invocation settings
- **When** each reader receives valid or malformed input
- **Then** the shared parser handles syntax, the existing owning format handles its schema and empty-document behavior, and malformed-input codes and exit semantics remain unchanged with source and parser coordinates when available.

### [AC-05] Fixers preserve text outside the edited value
- **Given** a supported metadata fixer input with comments, Unicode before a node, quoted scalars, flow or block lists, unrelated frontmatter fields and LF or CRLF line endings
- **When** the fixer updates its requested field
- **Then** only the requested value changes, unrelated header and body bytes remain identical, and the result reloads through the shared C parser.
- **And** when the binding is missing or replacement validation fails, the operation reports failure and leaves the file bytes unchanged.

### [AC-06] Memo does not hide parser changes or missing bindings
- **Given** an existing document parse memo
- **When** the shared parser implementation changes or an index operation runs without the C binding
- **Then** the parser fingerprint invalidates results from the old implementation, and availability is checked before a warm memo result is reused.

### [AC-07] Supported installation instructions match runtime checks
- **Given** the documented `uv add` or `uv tool install` route and installed-wheel consumers for dist-only and harness packages
- **When** the project installs PyYAML and a consumer parses YAML
- **Then** guidance uses `--no-build-package pyyaml`, the runtime confirms a usable C binding, and parsing succeeds; simulated binding absence returns `YAML_BINDING_UNAVAILABLE` in both consumer environments.
- **And** guidance does not require system LibYAML development headers for a compatible binary wheel.

## 5. Carried Materials

- `docs/materials/2026-10/20261024-canonical-libyaml-only/readers.md` inventories Python readers, broad exception handlers, memo use and existing typed authoring operations.
- `docs/materials/2026-10/20261024-canonical-libyaml-only/installation.md` records the PyYAML wheel evidence, installation conditions and platform limits.
- `docs/materials/2026-10/20261024-canonical-libyaml-only/probe.py` and `probe-results.json` record the local pre-implementation corpus comparison. The result is not proof of all YAML syntax or foreign-platform behavior.

## 6. References

- `ADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries`
- `CAP-DOCS-document-model`
- `CAP-DLV-workflow-envelopes`
- `CAP-DLV-workflow-definitions`
- `CAP-DIST-manifest-spec`
- `UC-find-the-right-documents`
