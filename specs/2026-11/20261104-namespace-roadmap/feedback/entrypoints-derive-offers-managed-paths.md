---
id: FB-entrypoints-derive-offers-managed-paths
title: devkit spec entrypoints derive offers .devkit/managed, .claude and the installation receipt as entrypoint candidates
scope: repo
kind: suggestion
category: tool-error
target: devkit spec entrypoints derive
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-04
---

# [FB-entrypoints-derive-offers-managed-paths] devkit spec entrypoints derive offers .devkit/managed, .claude and the installation receipt as entrypoint candidates

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the derivation joins every `_Boundary` path with every non-waived target. A task whose
  boundary names the regenerated copies (`.devkit/managed/`, `.claude/`, `.devkit/installation.json`) therefore gets
  those paths as `new=` candidates for every target, although `.devkit/managed/` is gitignored and never an
  entrypoint and the receipt and projections are generated.
- **Proposed Procedure**: drop gitignored paths and the `devkit sync` outputs (projected files, the receipt) from the
  candidates before listing, as `--exclude` does by hand.
- **Expected Benefit**: shorter candidate lines for a change that regenerates deployed copies; no risk of writing a
  generated path as an entrypoint.
- **Cost & Risk**: a path filter in the derivation; none observed.
- **Attempted**: hypothesis; in this session the wanted pair was applied with `--target` and `--code`.

## Evidence

```text
[CANDIDATES: CAP-DLV-proposal-planning ... new=.claude,.devkit/installation.json,.devkit/managed,packages/... missing=- folded=- declared=-]
tasks.md Task 3.1 _Boundary: `.devkit/managed/`, `.devkit/installation.json`, `.claude/`
```

## Disposition

- **Disposition**: `SPEC-entrypoint-generated-filter` filters known managed outputs and receipt-owned projections,
  including generated-only directories, while retaining authored/ignored files and shared scope classification.
  Explicit selectors cannot restore generated candidates. Verified by 98 focused integration tests, full affected
  fallback (6550 passed,15 skipped), independent Code Review and the recorded namespace-roadmap comparison
  (three generated candidate paths removed;17 authored candidates retained). Blanket gitignore exclusion was
  intentionally not adopted because ignored files can be authored implementation.
