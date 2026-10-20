---
id: ADR-select-tests-by-file-with-finer-spec-dependency-nodes
title: Select tests by file with finer spec dependency nodes
summary: "Use per-test-file selection and module-level devkit_spec dependency nodes while preserving conservative fallback, fixtures and explicit dynamic dependency coverage."
proposal: SPEC-affected-test-granularity
status: accepted
created_at: 2026-10-20
---

# [ADR-select-tests-by-file-with-finer-spec-dependency-nodes] Select tests by file with finer spec dependency nodes

- **Status**: Accepted
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

Area/package test groups combine unrelated imports; devkit_spec also has one production node. The measured
file-only split reduces excess tests but cannot narrow that package's internal changes. Static selection is an
existing local optimization under `ADR-nightly-ci-verification`, not a complete runtime dependency proof.

## 2. Decision Drivers

Reduce demonstrated false positives, preserve required consumers and full fallbacks, keep the selector stateless,
and avoid changing production architecture solely for test performance.

## 3. Considered Options

Keep broad groups; split files alone; split files and devkit_spec source modules; build function-level or recorded
runtime coverage analysis. The third option addresses both observed causes with bounded implementation scope.

## 4. Decision Outcome

Select per-file test groups and opt-in module-level devkit_spec nodes. Keep other production owners coarse by
default. Resolve helpers, applicable conftests, relative imports, initializers and re-exports conservatively.
Use broad owner dependencies for static uncertainty and full fallback for unsafe/unknown change mapping or parse
failure. Retain existing explicit data/structural/frontend checks and all full triggers. No implicit package edge
on every fine spec test may defeat the new granularity; opaque consumers explicitly retain a broad dependency.

Do not use deferred imports to conceal real dependencies, and do not add helper extraction or runtime coverage
storage to this implementation. Validate reductions on same-revision before/after collection matrices alongside
independent positive and negative dependency fixtures. Exact numerical reductions are evidence, not authority to
omit required coverage.

## 5. Consequences

The graph parser and selector tests gain complexity around Python package initialization and test helpers.
Conservative cases still select large groups or the full suite. That is intentional: complete nightly and release
CI remains necessary, and some changes inherently have broad consumers. Future workspace packages use the existing
broad default until explicit finer coverage is justified. The MCP packaging work may change inventory and baseline
counts, requiring normal base refresh and measurement rather than concurrent blind edits to the selector.
