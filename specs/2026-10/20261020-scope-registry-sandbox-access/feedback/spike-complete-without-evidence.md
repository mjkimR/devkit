---
id: FB-spike-complete-without-evidence
title: Proposal spike reports done before substantive Planning evidence exists
scope: repo
kind: friction
category: spec-ambiguity
target: devkit workflow next (sdd-proposal spike completion)
skill: spec
agent: codex
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-20
---

# [FB-spike-complete-without-evidence] Proposal spike reports done before substantive Planning evidence exists

## 1. Friction / Question

- **Context**: A first medium Planning turn had only a draft proposal and plan-intent record.
- **Expectation**: Stage navigation should distinguish an unperformed spike from completed investigation.
- **Actual**: After only changing the proposal status, next reported spike done and directed collect-feedback.
- **Workaround**: Followed planning.md independently, gathering evidence and requesting scout/challenger reviews.
- **Suggestion**: Clarify that this stage result does not prove investigation, or require explicit spike evidence.
  A check must still allow valid low-effort planning without forcing support-role envelopes.

## Diagnostic Details

- **Reproduction**: Run workflow next on a reviewing proposal with no spike checklist or support envelopes.
- **Expected / Actual**: Pending substantive Planning / spike marked done before evidence was recorded.
- **Versions**: Repository base 3efccb03e332e6d0d98aa8487f373fa3aab885f2.
- **Conditions**: sdd-proposal; medium effort; plan-intent accepted; no implementation.
- **Workarounds Attempted**: Followed Planning procedure rather than treating next as completion evidence.
- **Related Assets**: spec references/planning.md; sdd-proposal workflow.

## Evidence

```text
[DONE: intent-proposal spike]
[STAGE: collect-feedback human_gate=- role=developer isolation=none]
[CHECK: envelope-check-pass(feedback swept) class=disk evaluated=true detail="no feedback envelope"]
```

## Disposition

Dismissed after reassessment. Spike is an optional investigation stage; necessary investigation and review
remain responsibilities of the existing Planning and Challenger procedures. The observed evidence concerns the
CLI's `done` display, not a proposal incorrectly accepted because required investigation was omitted. A separate
completion mechanism is not justified by this case. No workflow or runtime change is made.
