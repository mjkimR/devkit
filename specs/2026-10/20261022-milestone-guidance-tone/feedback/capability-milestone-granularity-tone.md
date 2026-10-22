---
id: FB-capability-milestone-granularity-tone
title: Capability keeps SHOULD wording for milestone granularity
scope: repo
kind: question
category: spec-ambiguity
target: CAP-HARN-agent-guidance
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-capability-milestone-granularity-tone] Capability keeps SHOULD wording for milestone granularity

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-milestone-guidance-tone` softened the granularity wording of the roadmap README, the seed README
  and the milestone template from SHOULD/SHOULD NOT to recommendations.
- **Expectation**: the agreed intent named those three documents; the write scope allowed capability edits only for the
  historical-document statement.
- **Actual**: the milestone paragraph of `CAP-HARN-agent-guidance` still says "Authors SHOULD describe ..." and "it
  SHOULD NOT exist solely as a sequencing gate".
- **Workaround (or Interpretation Chosen)**: kept, because RFC 2119 SHOULD already means "recommended" (spec Non-Goal
  4); the guidance documents and the capability agree in meaning.
- **Suggestion**: a human confirms the interpretation, or a later edit rephrases that sentence as a preference to
  match the guidance tone.

## Diagnostic Details

- **Reproduction**: `rg -n "SHOULD NOT exist solely" docs/capabilities`.
- **Expected / Actual**: not applicable.
- **Versions**: this unit's head.
- **Conditions**: write scope of this Development turn.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-HARN-agent-guidance`, `ADR-milestone-merging`.

## Evidence

```text
CAP-HARN-agent-guidance: "it SHOULD NOT exist solely as a sequencing gate"
```
