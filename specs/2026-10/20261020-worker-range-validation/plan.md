---
id: PLAN-worker-range-validation
spec: SPEC-worker-range-validation
---

# Technical Plan: `SPEC-worker-range-validation`

## 1. Constitution & Invariant Review

None. `ADR-informational-range-inspection-reuses-existing-checks` fixes the contract. The helper adds evidence to
`CAP-DLV-delivery-workflows` without adding enforcement. Libraries return values; CLI output uses core helpers.

## 2. Architecture Overview & Impact

Add `devkit_spec.worker` for read-only Git snapshots, input derivation and check aggregation; mount a small Click
worker group under `devkit_spec.cli`. Reuse the existing boundary and reconciliation parser and committed envelope
collector. Call existing rules/workflow commands once, capturing their structured output and advisories unchanged.
No new dependencies. Tests use temporary Git repositories and controlled check runners.

## 3. Component & Interface Design

`inspect [--unit] [--base] [--head] [--scope ... | --scope-file] [--base-checkout] [--format json]` reports value/source
pairs, scope entries with task/feedback provenance, compared SHA values, changed paths, optional outside-scope
and base-checkout observations, and named pass/fail/not-run checks. Scope matches literal file/directory prefixes
at path-component boundaries. Scope-file is UTF-8 with one nonempty repository-relative prefix per line.

Read records via `git show HEAD:path` and earlier envelope-added commits; do not create checkout snapshots.
Use the existing envelope collector on those texts. Git marker and branch correspondence follow the accepted ADR.
Required-input errors instruct explicit flags; unavailable scope leaves other checks running.

## 4. Verification & Test Plan

Real Git fixtures exercise first and repeated turns, blocked/recovered results, ambiguous records, dirty record
independence, prefix matching, rename paths, base checkout lookup, explicit overrides and invalid inputs.
CLI tests verify JSON/text, check aggregation, exit codes, stable causes and no writes. Run package lint and type
checks, relevant tests with `just test-affected`, cumulative rules, and independent high-effort code and reconcile
reviews. Update reviewer guidance and delivery capability; resolve only the verified linked feedback.
