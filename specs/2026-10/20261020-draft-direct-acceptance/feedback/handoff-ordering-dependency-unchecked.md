---
id: FB-handoff-ordering-dependency-unchecked
title: An accepted proposal's ordering dependency on another repository is not checked before Development starts
scope: repo
kind: question
category: spec-ambiguity
target: spec skill references/worktree.md (premise check after handoff)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-20
---

# [FB-handoff-ordering-dependency-unchecked] An accepted proposal's ordering dependency on another repository is not checked before Development starts

## 1. Friction / Question (friction, question)

- **Context**: the accepted proposal of `SPEC-draft-direct-acceptance` says the workbench strategy-layer update
  comes first and that Development checks that text against the PADRs before changing code.
- **Expectation**: the premise check after handoff, or the Host's Development start, says what a worker does when
  such a cross-repository premise is not yet met.
- **Actual**: at this Development's base the workbench text still named this work as a follow-up. The premise check
  rule ("a difference inside the agreed scope is an assumption, one that breaks the agreement is a problem") does not
  say whether an unmet ordering dependency in another repository breaks the agreement.
- **Workaround (or Interpretation Chosen)**: treated it as inside the agreement, since nothing in this repository
  depends on the workbench text and integration is the Host's: implemented from the promoted ADRs, recorded the
  difference as an assumption in `spec.md` and as an open finding asking the Host to land the workbench update before
  or with `dev-integration`.
- **Suggestion**: state in the worktree reference's premise check that an ordering dependency outside the repository
  is checked by the Host before it starts Development, and that a worker records an unmet one as an assumption with
  a finding for the integration decision.

## Diagnostic Details

- **Reproduction**: hand off a proposal whose design names a prerequisite change in another repository, before that
  change lands, and start Development.
- **Expected / Actual**: expected a stated rule; actual an interpretation by the worker.
- **Versions**: base b8c3a77.
- **Conditions**: cross-repository ordering dependency in the proposal's design section.
- **Workarounds Attempted**: the interpretation above.
- **Related Assets**: `spec` skill `references/worktree.md` (proposal Development), development-worker contract step 2.

## Evidence

```text
workbench strategy layer, 01 §5.1: "Planning 없이 바로 수락하는 경로는 후속(devkit-spec PROP-draft-direct-acceptance)이다."
proposal §4: "The workbench strategy-layer update (§3.2) comes first; Development here follows it."
```

## Disposition

Dismissed: cross-repository coordination belongs to the Host's judgment for the particular task. No general
repository-external prerequisite inspection, new worker instruction or automated gate is needed. Explicit
dependencies in an agreed task still matter; this disposition declines a universal procedure rather than
authorizing agents to ignore those dependencies.
