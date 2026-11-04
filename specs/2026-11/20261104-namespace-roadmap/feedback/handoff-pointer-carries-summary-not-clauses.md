---
id: FB-handoff-pointer-carries-summary-not-clauses
title: The handoff's partial supersession pointer carries the ADR summary, so Development rewrites it to name the replaced clauses
scope: repo
kind: suggestion
category: redundant-step
target: packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-04
---

# [FB-handoff-pointer-carries-summary-not-clauses] The handoff's partial supersession pointer carries the ADR summary, so Development rewrites it to name the replaced clauses

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: handoff writes `Superseded in part by <ADR-ID>: <summary>` into each ADR the promoted PADR
  supersedes, with the new ADR's whole `summary` as the clause text. The decisions README asks the pointer to say what
  was replaced; a summary states the new decision, not the replaced clauses, so Development rewrote the line to name
  the two clauses the PADR's Decision Outcome listed.
- **Proposed Procedure**: let the PADR declare the replaced clauses (for example a `supersedes_clauses:` list or a
  conventional "Replaces, in part:" paragraph in its Decision Outcome) that handoff copies into the pointer; or keep
  the summary but have the post-handoff link check name the pointer as a line to reread, so the rewrite is an
  expected step rather than a discovery.
- **Expected Benefit**: one less Development edit of a ledger ADR per partially superseding PADR; pointers that read
  as the README describes.
- **Cost & Risk**: a PADR field or convention to parse; a pointer that quotes clauses can go stale when the earlier
  ADR's wording is repaired.
- **Attempted**: hypothesis; in this session the rewrite was done by hand in the build commit.

## Evidence

```text
handoff.py:14: writes one "Superseded in part by `ADR-<slug>`: <summary>" line below the heading of ...
ledger ADR after handoff: Superseded in part by `ADR-namespace-milestone-roots`: For a monorepo whose packages run on their own cadence, we let ...
docs/decisions/README.md: "the earlier ADR ... otherwise stays accepted with a 'Superseded in part by' line"
```

## Disposition

Resolved through the guidance alternative by the session change to
`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/post-handoff.md`.
The Host reviews partial-supersession pointers against the promoted ADR's Decision Outcome and commits any
needed clause clarification before starting a worker, preserving the earlier ADR's other decisions.
No PADR metadata or handoff API was added. Independent medium Code Review passed with no findings;
`just test-affected --base 6b24d5dd` passed 1,626 tests, and asset hygiene and sync checks passed.
