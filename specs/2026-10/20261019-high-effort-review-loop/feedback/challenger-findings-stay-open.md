---
id: FB-challenger-findings-stay-open
title: Challenger envelope findings stay open after they are folded into the proposal
scope: repo
kind: friction
category: missing-capability
target: devkit workflow envelope check
skill: spec
agent: claude-code
origin: agent
severity: noise
recurring: true
status: resolved
created_at: 2026-10-19
---

# [FB-challenger-findings-stay-open] Challenger envelope findings stay open after they are folded into the proposal

## 1. Friction / Question (friction, question)

- **Context**: Planning folded every finding of two `challenger` rounds into `proposal.md` and the PADR, then
  prepared the `plan-accept` request, which lists the support-role envelopes from `devkit workflow envelope check`.
- **Expectation**: the effort record shows whether the challenger's findings were addressed.
- **Actual**: `envelope check` reports `challenger-01 ... open_findings=15` and `challenger-02 ... open_findings=4`.
  `reverify` closes only a `review` round, so a challenger finding can never be marked resolved or waived; the request
  shows open counts for findings that are settled.
- **Workaround (or Interpretation Chosen)**: stated the disposition of each round in the next round's summary and in
  the `worker` envelope's summary.
- **Suggestion**: either let `reverify` (or a `--resolve` on a later challenger envelope) close challenger findings, or
  have `envelope check` omit `open_findings` for kinds that no check reads, so the count is not mistaken for open
  work.

## Evidence

- `devkit workflow envelope check --unit docs/proposals/PROP-high-effort-review-loop`:
  `challenger-01.yaml ... open_findings=15`, `challenger-02.yaml ... open_findings=4`, `[OK: 5 envelopes]`.
- `CAP-DLV-workflow-envelopes`: "A `reverify` envelope must name the `review-NN.yaml` it closes."

- **Disposition**: PROP-envelope-record-gaps: closing folded challenger findings and the round count before markers (Q1)
- **Disposition (resolved)**: `SPEC-envelope-record-gaps` lets `devkit workflow envelope reverify --from envelopes/challenger-NN.yaml`
  close a challenger round (`ADR-review-and-reconcile-verification`); `envelope check` reports the deciding state of
  review and challenger rounds alike. Verified by `packages/devkit/tests/workflow/test_envelope_record_gaps.py` (AC-01 to AC-05).
