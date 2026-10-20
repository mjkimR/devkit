---
id: FB-recurs-marker-on-fix-introduced-findings
title: A gap left by the previous round's fix is marked recurs and can no longer be self-verified
scope: repo
kind: question
category: spec-ambiguity
target: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/review-loop.md (sections 2 and 3, recurs marker)
skill: spec
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-recurs-marker-on-fix-introduced-findings] A gap left by the previous round's fix is marked recurs and can no longer be self-verified

## 1. Friction / Question (friction, question)

- **Context**: Planning review loop at `high`, cap round 4 of PROP-integration-follow-ups.
- **Expectation**: `recurs:` marks a finding that repeats an earlier one (the same defect coming back after its fix);
  section 2 says "A recurring finding can no longer be closed by self-verification".
- **Actual**: The cap-round challenger marked as `recurs:` findings that were gaps left by the previous round's fix
  (the cleanup-only request introduced to fix round 3 #1 lacked three definitions; a replacement command used an
  option Git does not have). Each came with a concrete suggested_action, but the marker excluded self-verification,
  so the cap batch had to be handed over although every fix was a concrete edit in the named sections.
- **Workaround (or Interpretation Chosen)**: Applied the suggested actions, did not claim self-verification for the
  recurring items, and reported the cap hand-over as a problem in the worker envelope with the recovery naming them.
- **Suggestion**: Say whether a finding against an incomplete fix of the same item counts as a recurrence, or give
  reviewers a separate marker (for example `follow-up:`) for a fix that is incomplete rather than reverted.

## Evidence

```text
challenger-04.yaml #1: "recurs: challenger-03.yaml #1; the cleanup-only request lacks its guard base ..."
challenger-04.yaml #2: "recurs: challenger-03.yaml #3; git pull has no -m option ..."
review-loop.md section 2: "A recurring finding can no longer be closed by self-verification."
```

## Disposition

`SPEC-feedback-review-auto-proposal` defines recurrence by the same failure condition persisting or returning,
including incomplete fixes. Distinct defects introduced by a fix remain new findings; shared location or causality
alone is insufficient. Existing escalation, out-of-scope exclusions and minor-fix conditions remain unchanged.
Independent medium review checked all three acceptance scenarios with no findings. Spec lint/type checks and
1,111 affected tests passed; the Living Spec mirrors the source guidance.
