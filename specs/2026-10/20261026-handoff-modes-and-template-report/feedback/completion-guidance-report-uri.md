---
id: FB-completion-guidance-report-uri
title: The completion reference still preserves a report URI on stale recovery
scope: repo
kind: change-request
category: instruction-conflict
target: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja (Policy)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-completion-guidance-report-uri] The completion reference still preserves a report URI on stale recovery

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the `spec` skill's completion reference says "A stale source or report invalidates the old
  request: ... preserving the source SHA, report URI, authority and recovery state", while acceptance and handoff
  take no published report (`CAP-DLV-proposal-incubation`, the Host-authorized lifecycle CLI).
- **Proposed Procedure**: drop "or report" and "report URI" from that line, so the guidance preserves the source SHA,
  authority and recovery state.
- **Expected Benefit**: no agent looks for a report URI to carry across a stale recovery.
- **Cost & Risk**: one sentence in a bundle source and a `devkit sync`.
- **Attempted**: found by the reconcile check of `SPEC-handoff-modes-and-template-report`; outside its write targets.

## Diagnostic Details

- **Reproduction**: `rg -n "report URI" packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`.
- **Expected / Actual**: no report wording / "report URI".
- **Versions**: `dev-handoff-modes-and-template-report`.
- **Conditions**: a stale proposal acceptance or handoff recovery.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-proposal-incubation`, `FB-handoff-refusals-emit-maintenance`.
