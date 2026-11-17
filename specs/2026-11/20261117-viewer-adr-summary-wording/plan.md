---
id: PLAN-viewer-adr-summary-wording
spec: SPEC-viewer-adr-summary-wording
---

# Technical Plan: `SPEC-viewer-adr-summary-wording` Reword viewer ADR summaries that name library hosts

## 1. Architecture Overview & Impact

- Target Area: the `summary` frontmatter of `ADR-viewer-namespace-roadmap-discovery` and
  `ADR-viewer-indexed-decision-supersession`.
- A documentation-only wording repair under the spec constitution's ADR rule: an existing ADR may be edited for
  wording without changing its decision. No code, capability, design, domain or operations document is affected;
  no test or fixture quotes either summary (`rg` over the repository finds the strings only in the ADRs and in
  `SPEC-viewer-host-wording` history).

## 2. Component Breakdown & Interface Contracts

- `ADR-viewer-namespace-roadmap-discovery`: drop the context qualifier "across local and library sources"; the
  concern becomes "viewer roadmap discovery". Decision, quality and downside are unchanged.
- `ADR-viewer-indexed-decision-supersession`: replace the quality "to retain one read-only viewer across hosts"
  with the host-neutral quality its drivers and selected option state: one read-only browser read path that runs
  no repository Python environment. Concern, decision and downside are unchanged.
- Both summaries stay within the 300 characters of `RULE-document-summary`.

## 3. Verification & Test Plan

- The `rg` commands of AC-01 and AC-02 exit 1.
- `git diff main -- docs/decisions/` shows only the two summary lines (AC-03).
- `uv run devkit rules check --ci --base main` exits 0 (AC-04); `just test-affected --base main` passes.
