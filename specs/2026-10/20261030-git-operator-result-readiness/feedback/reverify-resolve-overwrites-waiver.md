---
id: FB-reverify-resolve-overwrites-waiver
title: Reverify resolve silently turns a waived finding into a resolved one
scope: repo
kind: friction
category: tool-error
target: devkit workflow envelope reverify
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-reverify-resolve-overwrites-waiver] Reverify resolve silently turns a waived finding into a resolved one

## 1. Friction / Question (friction, question)

- **Context**: A second reverify of a Planning challenger round, started `--from` the round's first reverify, to close
  the findings the user's answers settled.
- **Expectation**: The planning reference says a later reverify passes only the findings that turn closes. A number
  naming a finding the earlier reverify already closed is an input error, or at least a notice.
- **Actual**: `--resolve 7` named a finding the first reverify had waived. The command wrote it as
  `resolution: resolved` while keeping its `waiver:` text, reported `open_findings=1` for the finding actually meant
  and printed no notice.
- **Workaround (or Interpretation Chosen)**: The worker deleted the uncommitted envelope and reran with the intended
  number.
- **Suggestion**: Refuse or warn when `--resolve` or `--waive` names a finding the source envelope already closed.

## Evidence

```text
[ENVELOPE: envelopes/reverify-02.yaml kind=reverify seq=02 status=completed open_findings=1]
  resolution: resolved
  waiver: The delta comes from git status like the Host commits it replaces; ...
```

- **Disposition (resolved)**: `SPEC-envelope-answer-decider` refuses a `devkit workflow envelope reverify` whose
  `--resolve N` or `--waive N` names a carried finding the source envelope already closed, with
  `ENVELOPE_FINDING_CLOSED`, `[TARGET]` the flags and numbers, `[DETAIL]` the numbered carried findings and nothing
  written. Verified by `packages/devkit/tests/integration/features/workflow/test_envelope_answer_decider.py` (AC-06,
  AC-07).
