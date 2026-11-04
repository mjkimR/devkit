---
id: PLAN-entrypoint-generated-filter
spec: SPEC-entrypoint-generated-filter
---

# Technical Plan: `SPEC-entrypoint-generated-filter`

## 1. Constitution & Invariant Review

No architectural invariant changes. `CAP-TRACE-code-entrypoints` gains an automatic-derivation exclusion without
restricting the shared path contract or manual declarations. Existing entrypoints-to-project dependency admits
the typed receipt reader; no new edge is introduced. This bounded candidate policy is recorded here rather than
adding a general governance rule or ADR.

## 2. Architecture Overview & Impact

The entrypoints repository loads the typed receipt and identifies generated paths. The derive service applies
that policy after shared path classification. The use case applies it again after selector synthesis, before
matching selectors or applying changes. The shared classifier remains untouched.

## 3. Component & Interface Design

Known outputs are .devkit/managed and every descendant, plus .devkit/installation.json. Receipt file_records add
exact projected files; seeded records do not add exclusions. A directory with owned descendants is generated-only
only when its current files and symlinks are all managed; mixed directories remain candidates. No gitignore query
is used. A symlink not itself owned is authored, never traversed for ownership inference.

The public derive signature stays unchanged. A small repository value supplies ownership queries and the service
adds `Reason.MANAGED_OUTPUT`. Explicit --code cannot synthesize excluded outputs: unmatched selectors keep
`SPEC_ENTRYPOINTS_CODE_UNMATCHED`. Malformed receipts retain `RECEIPT_INVALID`.

## 4. Error Handling & Edge Cases

No receipt means no inferred projection ownership, with known outputs still excluded. A malformed receipt fails
through the existing advisory rather than weakening the exclusion. Missing projected files remain excluded by
receipt ownership. Directory scanning never follows unowned symlink directories.

## 6. Verification & Test Plan

Integration tests cover AC-01, AC-02 and AC-04 with typed receipt fixtures; CLI tests exercise selector synthesis
and write refusal for AC-03. Shared-classifier regressions prove AC-05. Repeat the recorded real-bundle baseline.
Run `just lint-check devkit-spec`, `just check devkit-spec`, focused entrypoint tests and `just test-affected --base
00511ae149771e6197b51ba52f706992ff272161` with its full fallback preserved. Run cumulative CI rules against
700c339bba8e89b4d70f63c5628d14d25bd3ffdd. No wheel contract changes require a separate packaging build.

## 7. Measured Outcome

The recorded library derivation of `SPEC-namespace-roadmap` now offers none of [.claude,
.devkit/installation.json, .devkit/managed]; all three inputs carry managed-output skips. Seventeen unique authored
candidate paths remain. No baseline checkout, runtime timing claim or remote operation was used.
