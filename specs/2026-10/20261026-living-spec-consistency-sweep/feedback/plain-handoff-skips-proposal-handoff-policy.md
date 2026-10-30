---
id: FB-plain-handoff-skips-proposal-handoff-policy
title: The plain proposal handoff reads no proposal-handoff policy
scope: repo
kind: question
category: spec-ambiguity
target: devkit spec proposal handoff
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-plain-handoff-skips-proposal-handoff-policy] The plain proposal handoff reads no proposal-handoff policy

## 1. Friction / Question (friction, question)

- **Context**: Aligning `CAP-DLV-delivery-workflows` §4.3 and `CAP-DLV-project-policy` rule 4 with the shipped
  `proposal-handoff` boundary in `SPEC-living-spec-consistency-sweep`.
- **Expectation**: `proposal-handoff` is one of the three main decision boundaries, so every route that starts
  Development from an accepted proposal would read it.
- **Actual**: only `devkit spec proposal handoff <slug> --effort <level>` (`HandoffUseCase`) and
  `accept --mode accept_and_handoff` read it. The plain `devkit spec proposal handoff <slug>` in a `dev-<slug>`
  checkout (`HandoffProposalUseCase`) reads no approval policy.
- **Workaround (or Interpretation Chosen)**: the documents now name `handoff --effort` as the reader; the plain path's
  behavior was not changed or decided.
- **Suggestion**: decide whether the plain handoff must check `proposal-handoff` (refuse or require the Host's
  decision under `ask`), or state in `CAP-DLV-proposal-planning` that it is the Host-run step after that decision.

## Diagnostic Details

- **Reproduction**: read `handoff_cmd` in `delivery/cli/proposals.py`: without `--effort` it calls
  `HandoffProposalUseCase().execute(root, slug)`; `approval_policy(..., "proposal-handoff")` is called only in
  `native_handoff.py` and `native_plan_accept.py`.
- **Expected / Actual**: a policy check on every Development start / none on the plain path.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: `[workflow.approvals] proposal-handoff = "ask"`, a checkout on `dev-<slug>`.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-proposal-planning`, `CAP-DLV-project-policy`, `ADR-host-cli-lifecycle-authority`.

## Evidence

```text
proposals.py handoff_cmd: if effort is not None: HandoffUseCase(root).execute(slug, effort) ... else HandoffProposalUseCase().execute(root, slug)
native_handoff.py:121 authority = approval_policy(self.root, "proposal-handoff")
```

## Disposition

Answered by `SPEC-handoff-modes-and-template-report` (decision 3, no code change): `CAP-DLV-proposal-planning` and `CAP-DLV-project-policy` rule 4 state that the plain `devkit spec proposal handoff <slug>` in a `dev-<slug>` checkout is the Host-run step after the `proposal-handoff` decision and reads no policy itself, while `handoff --effort` and `accept --mode accept_and_handoff` read the policy. A policy check with a new approval flag was rejected: the CLI does not authenticate the conversational decision, and the composed handoff would check twice.
