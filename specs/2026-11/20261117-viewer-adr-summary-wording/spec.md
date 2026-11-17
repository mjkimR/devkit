---
id: SPEC-viewer-adr-summary-wording
title: Reword viewer ADR summaries that name library hosts
summary: Reword the frontmatter summaries of two viewer ADRs that still name library sources and hosts, without changing either decision.
status: completed
created: 2026-11-17
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-adr-summary-wording] Reword viewer ADR summaries that name library hosts

## 1. Problem Statement & Motivation

`ADR-internal-repository-viewer` left the viewer one host, `devkit viewer serve`, with no library host.
`SPEC-viewer-host-wording` marked the library-host body statements of `ADR-viewer-namespace-roadmap-discovery` and
`ADR-viewer-indexed-decision-supersession` as history, but their frontmatter summaries were outside its scope and
still read "across local and library sources" and "one read-only viewer across hosts". `devkit docs list` and
`devkit docs search` show these summaries, so a reader still infers a second viewer host or a library source.

The user decided that a decision-time summary is reworded after a later ADR removes the hosts it names, as a
wording repair that keeps the decision.

## 2. User Stories

- **US-1**: As a reader of `devkit docs list` or `devkit docs search` output, I want the two viewer ADR summaries to
  state their decisions without naming a library source or a second host, so that I do not infer a viewer host the
  project removed.

## 3. Non-Goals

1. **Scope Excluded**: no decision change. Each Y-statement keeps its concern, decision and accepted downside; only
   the host wording changes. No new ADR, no `supersedes`, `status` or body change, and each Decision Outcome
   section stays byte-identical to the base.
2. **Scope Excluded**: no code, test, capability, use case or other ADR change.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Namespace roadmap ADR summary names no library source

- **Given** `ADR-viewer-namespace-roadmap-discovery` after the change
- **When** `rg -n -i "^summary:.*(library|host)" docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md`
  runs
- **Then** it prints no line (exit 1), and the summary is still a Y-statement that matches global and namespace
  roadmap paths without reading the namespace registry, to preserve reader independence, accepting that
  unregistered directories can appear.

### [AC-02] Indexed supersession ADR summary names no second host

- **Given** `ADR-viewer-indexed-decision-supersession` after the change
- **When** `rg -n -i "^summary:.*(library|hosts)" docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md`
  runs
- **Then** it prints no line (exit 1), and the summary is still a Y-statement that derives supersession in the
  browser and shows it beside each decision body, accepting tested duplication of the document query semantics.

### [AC-03] Only the summary lines change

- **Given** the two ADR files after the change
- **When** `git diff main -- docs/decisions/` runs
- **Then** the only changed lines are the two `summary:` frontmatter lines (two removed, two added).

### [AC-04] Documents stay valid

- **Given** the changed documents and this unit
- **When** `uv run devkit rules check --ci --base main` runs
- **Then** it reports no violation (exit 0).

## 5. Source feedback

- `FB-viewer-adr-summaries-name-library-hosts`: the whole scope above; this unit resolves it.
