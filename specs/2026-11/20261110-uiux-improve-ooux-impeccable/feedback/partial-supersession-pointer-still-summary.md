---
id: FB-partial-supersession-pointer-still-summary
title: The partial-supersession pointer reached Development still repeating the new ADR's summary
scope: repo
kind: friction
category: docs-mismatch
target: the spec-next post-handoff reference (partial-supersession pointer clarification)
origin: agent
severity: noise
recurring: true
status: promoted
created_at: 2026-11-10
---

# [FB-partial-supersession-pointer-still-summary] The partial-supersession pointer reached Development still repeating the new ADR's summary

## 1. Friction / Question (friction, question)

- **Context**: Development of a spec handed off with a PADR that supersedes an accepted ADR in part; the worker may
  edit that older ADR only for a clause 1 bundle-name repair.
- **Expectation**: The post-handoff step has the Host clarify each "Superseded in part by" pointer to name the
  replaced clauses before a worker starts (the route `FB-handoff-pointer-carries-summary-not-clauses` resolved to).
- **Actual**: The Host's post-handoff commit reworded the new ADR's own supersession sentence. The pointer below the
  older ADR's heading still repeats the new ADR's summary and names no clause.
- **Workaround (or Interpretation Chosen)**: Left the pointer unchanged, because the worker's scope covers only the
  clause 1 repair, and reported it to the Host.
- **Suggestion**: Have the post-handoff check, or a rule, compare the pointer text with the new ADR's summary and flag
  an exact copy, so the clarification cannot be applied to the wrong file.

## Evidence

```text
Older ADR, line under the heading: "Superseded in part by `ADR-impeccable-session-authority`: For user-selected
Impeccable craft work, we let one bounded session edit ..." (identical to the new ADR's summary).
Host commit after handoff: changes one line of the new ADR ("On promotion, this decision supersedes" ->
"This decision supersedes"); the older ADR is not touched.
```

## Disposition

- **Disposition**: `PROP-partial-adr-supersession-statements`: the replaced scope becomes a structured statement in the superseding ADR that handoff copies into the pointer and a rule checks, replacing the guidance-only clarification step.
