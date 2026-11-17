---
id: FB-viewer-adr-summaries-name-library-hosts
title: Two viewer ADR summaries still name library sources and hosts
scope: repo
kind: suggestion
category: instruction-conflict
target: docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-17
---

# [FB-viewer-adr-summaries-name-library-hosts] Two viewer ADR summaries still name library sources and hosts

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `SPEC-viewer-host-wording` marked the library-host body statements of
  `ADR-viewer-namespace-roadmap-discovery` and `ADR-viewer-indexed-decision-supersession` as history, citing
  `ADR-internal-repository-viewer`. Their frontmatter summaries were outside its agreed scope and still read
  "across local and library sources" and "one read-only viewer across hosts".
- **Proposed Procedure**: Decide whether a decision-time ADR summary should be reworded after a later ADR removes
  the hosts it names; if so, reword both summaries in a wording pass without changing either decision.
- **Expected Benefit**: Search and list output, which show summaries, no longer suggest a second viewer host.
- **Cost & Risk**: Wording only; a summary rewrite must keep the Y-statement's decision unchanged.
- **Attempted**: Hypothesis; observed while doing the body wording pass.

## Evidence

```text
docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md:4 summary "... across local and library sources ..."
docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md:4 summary "... one read-only viewer across hosts ..."
```

## Disposition

Resolved by `SPEC-viewer-adr-summary-wording`. The user decided that a decision-time summary is reworded after a
later ADR removes the hosts it names. The `summary` of `ADR-viewer-namespace-roadmap-discovery` now reads "For viewer
roadmap discovery, we ..." and the `summary` of `ADR-viewer-indexed-decision-supersession` now names the quality "to
keep the viewer read-only without running each repository's Python environment"; each Y-statement keeps its
decision and downside, and `git diff main -- docs/decisions/` changes only the two summary lines. The `rg` checks
for library or host wording in both summaries exit 1, `devkit rules check --ci --base main` exits 0 and
`just test-affected --base main` passed 18 tests.
