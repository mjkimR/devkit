---
id: SPEC-file-byte-budgets
title: Measure file hygiene budgets in bytes
summary: "Replace line-count hygiene budgets with raw byte budgets, retaining the rule ID, warning phase and consolidated-record eligibility while migrating settings and current guidance."
status: planned
created: 2026-11-10
related_capabilities: [CAP-GOV-evaluation-lifecycle, CAP-GOV-rule-authoring]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-file-byte-budgets] Measure file hygiene budgets in bytes

## 1. Problem Statement & Motivation

Line count depends on wrapping, tables and code formatting. It does not consistently measure the amount an agent
loads. The instructed change replaces the metric of `RULE-file-length` with raw file bytes while keeping its
advisory purpose. `ADR-consolidated-record-budgets` needs a partial replacement for its line units and settings;
its eligibility and rule-local resolution choices remain in force.

## 2. User Stories

- **US-1**: As an agent reviewing document size, I want a byte budget that counts the exact evaluated file content.
- **US-2**: As a project owner, I want byte settings and current guidance without a silent line-to-byte conversion.

## 3. Non-Goals

- **Scope Excluded**: A hard gate, automatic file splitting, tokenization or a second line-budget mode.
- **Scope Excluded**: Generic resolver/cache redesign, new feature edges, renaming the existing rule or moving it
  from its builtin ownership.
- **Scope Excluded**: Rewriting historical specs or earlier ADR outcome clauses, and editing the concurrent delivery
  document split.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Raw byte boundaries

- **Given** a targeted file and a positive byte budget, including UTF-8 multibyte text, one long line, LF/CRLF,
  final-newline variants, empty content and undecodable bytes.
- **When** the rule reads the evaluated content through `ctx.cache.read_bytes`.
- **Then** exactly-at-budget content passes; one byte over reports a non-fixable `RULE-file-length` warning at
  line 1 with actual and selected limit bytes, without newline normalization or replacement-text reencoding.

### [AC-02] Consolidated budgets keep their selection semantics

- **Given** ordinary and optional consolidated byte budgets, qualifying ADR/terminal feedback aliases and valid
  path overrides, or malformed/nonqualifying headers.
- **When** targeted Markdown exceeds its ordinary budget.
- **Then** existing eligibility selects `max(max_bytes, consolidated_max_bytes)`; invalid headers keep the ordinary
  budget, and unnecessary header reads remain absent. The optional global default stays `None`.

### [AC-03] Typed byte settings replace line settings

- **Given** `max_bytes`, `consolidated_max_bytes`, extensions and path overrides.
- **When** settings are resolved.
- **Then** the ordinary default is 49152 bytes, valid positive integers apply, and booleans, strings, nonpositive
  values and obsolete `max_lines`/`consolidated_max_lines` keys fail before rule execution with
  `RULES_SETTINGS_INVALID`; no automatic conversion or fallback occurs.

### [AC-04] Target and snapshot boundaries remain exact

- **Given** selected/excluded paths and a staged or CI snapshot whose bytes differ from the live file.
- **When** the byte rule runs through the existing evaluator and workspace cache.
- **Then** only targeted configured extensions are checked, and findings use the selected snapshot bytes rather
  than live filesystem size.

### [AC-05] CLI identity and advisory phase remain stable

- **Given** an over-budget file or byte settings.
- **When** CLI check or explain runs in text or JSON.
- **Then** output retains `RULE-file-length`, hygiene/warning defaults, line 1 and numeric bytes; explain exposes
  byte settings/defaults, and the ordinary linter phase still does not run this hygiene rule.

### [AC-06] Current contracts and configuration agree

- **Given** the delivered builtin, repository configuration, guides, examples and consolidation playbooks.
- **When** project checks and document comparison run.
- **Then** the project uses 65536 bytes for CAP paths and optional consolidated records, current examples use byte
  keys, historical outcomes remain intact behind a matching partial pointer, and all required native checks pass.

## 5. Implementation Assumptions

- `FileLengthRule` and its module/ID remain stable; the constructor setting is named `max_bytes`.
- Bytes are raw evaluated file bytes; Markdown normally uses UTF-8. This is not a token-count guarantee.
- CLI-only output changes add no person-operated screen.
- The Host admitted `docs/development/reference/rules.md` for the same setting migration. Other document-hygiene
  files remain outside this Unit.
