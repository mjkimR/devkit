---
id: PADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries
title: Require the LibYAML safe parser at YAML read boundaries
summary: "For consistent Python YAML inputs, we require the LibYAML safe loader at read boundaries, to align accepted syntax and diagnostics, accepting loss of Python-parser fallback."
proposal: PROP-canonical-libyaml-only
status: draft
created_at: 2026-10-24
---

# [PADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries] Require the LibYAML safe parser at YAML read boundaries

- **Status**: Draft
- **Date**: 2026-10-24

---

## 1. Context & Problem Statement

Python YAML readers select different parsers, and the shared frontmatter reader preserves Python acceptance with
scanner/depth routing and a fallback. Fixers compose nodes separately. A missing optional PyYAML C extension can
therefore change accepted syntax. `PROP-canonical-libyaml-only` inventories these readers and their failure paths.

## 2. Decision Drivers

- One parser implementation for Python runtime YAML values and node positions.
- Explicit dependency failure that cannot be mistaken for invalid user data.
- Existing format schemas, surgical edits and agent-facing advisory contracts.
- Eligibility evidence separate from untested platform support claims.

## 3. Considered Options

| Option | Benefit | Cost or failure |
| --- | --- | --- |
| Keep C acceleration with Python fallback | Preserves existing Python acceptance | Retains separate grammar routes and duplicate parsing. |
| Require C at module import or all CLI startup | Detects installation failure early | Blocks text-only and non-YAML commands. |
| Require C at Python YAML read boundaries | Consistent syntax; unrelated operations remain available | Requires reader migration, cache checks and distinct dependency errors. |

## 4. Decision Outcome

Choose required C parsing at Python YAML read boundaries.

1. devkit-core owns lazy C availability, safe value loading and node composition.
2. Frontmatter applies its strict schema on that parser; standalone formats retain their schemas.
3. A missing binding raises `YAML_BINDING_UNAVAILABLE` as an execution advisory before parsing or cached-result reuse.
4. Malformed input retains the owning format's code, with source and parser coordinates when available.
5. Fixers retain targeted text edits and validate generated replacements before writing.
6. Installation documentation prefers compatible binary wheels. Existing source builds require a usable C binding.
7. Output-only serialization and browser/npm parsing remain outside this implementation decision.

The shared boundary does not add a second scanner grammar or Python retry.

## 5. Consequences

Python runtime readers share C syntax and marks. Missing dependencies stop operations instead of hiding documents.
Some Python-parser outcomes and diagnostic prose change. Tests assert stable codes and structured locations rather
than Python exception strings. Warm memo reuse needs a capability check and the shared module in its fingerprint.
Wheel metadata does not prove runtime behavior on every platform; Development records the environments actually run.
The normal binary-wheel installation route needs no system libyaml development headers.

## 6. Confirmation

- Shared/frontmatter tests under `packages/devkit-core/tests/unit/core/` cover canonical C behavior and missing binding.
- Document memo tests cover invalidation and cold/warm dependency failure.
- Existing governance/entrypoint fixer tests verify Unicode positions, comments, line endings and no unsafe writes.
- Workflow/distribution tests cover standalone and CLI YAML, error propagation and typed-record round trips.
- Existing `tests/e2e/smoke.sh` wheel scenarios cover isolated consumers through the thin `scripts/smoke.sh` entrypoint;
  review audits production load/compose calls.
- `just lint-check`, `just check`, `just test-affected`, `just test-dist` and `just smoke` supply Development verification.
