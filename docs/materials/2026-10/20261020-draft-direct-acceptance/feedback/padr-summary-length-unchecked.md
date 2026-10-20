---
id: FB-padr-summary-length-unchecked
title: devkit spec proposal padr accepts a summary that RULE-document-summary then refuses
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal padr --summary
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-padr-summary-length-unchecked] devkit spec proposal padr accepts a summary that RULE-document-summary then refuses

## 1. Friction / Question (friction, question)

- **Context**: Planning of `SPEC-draft-direct-acceptance` scaffolded two PADRs with
  `devkit spec proposal padr <slug> "<title>" --summary "<text>"`, as the planning-worker contract requires.
- **Expectation**: a command that writes the `summary` the summary rule governs either validates it or warns, so a
  scaffolded PADR is valid when written.
- **Actual**: both commands succeeded with 320- and 309-character summaries; the next
  `devkit rules check <proposal dir>` reported two `RULE-document-summary` errors (300 characters at most), which the
  commit gate would also refuse.
- **Workaround (or Interpretation Chosen)**: shortened both summaries by hand and reran the rule check.
- **Suggestion**: have `padr` (and `proposal new --summary`) apply the same length limit before writing, refusing
  with the rule's remediation, or print the rule's warning in its notices.

## Diagnostic Details

- **Reproduction**: `devkit spec proposal padr <slug> "<title>" --summary "<a 320-character sentence>"`, then
  `devkit rules check docs/proposals/PROP-<slug>`.
- **Expected / Actual**: expected a refusal or notice at scaffold time; actual success, then a rule error.
- **Versions**: worktree at base `298dd9e`.
- **Conditions**: default rule set; summary written through the command flag.
- **Workarounds Attempted**: manual shortening; resolved.
- **Related Assets**: `devkit spec proposal padr`, `RULE-document-summary`, planning-worker contract step 3.

## Evidence

```text
[PADR: PADR-direct-acceptance-command-and-handoff-guard path=docs/proposals/PROP-draft-direct-acceptance/decisions/... proposal=PROP-draft-direct-acceptance]
[VIOLATION: RULE-document-summary severity=error file=.../PADR-direct-acceptance-command-and-handoff-guard.md line=4 message="summary has 320 characters; keep it to one or two sentences (300 at most)"]
[VIOLATION: RULE-document-summary severity=error file=.../PADR-eligibility-for-direct-acceptance.md line=4 message="summary has 309 characters; ..."]
```

- **Disposition**: `SPEC-summary-length-guard`, implementation commit ec04a75: shared summary validation rejects
  more than 300 stripped characters before spec, proposal or PADR writes. Verified with
  `pytest packages/devkit-spec/tests/proposals/test_proposal_summary.py -q` as part of a focused 77-test passing
  run; its library and CLI boundary cases accept 300, reject 301 with ARGUMENT_INVALID targeting --summary,
  and assert no filesystem changes on rejection.
