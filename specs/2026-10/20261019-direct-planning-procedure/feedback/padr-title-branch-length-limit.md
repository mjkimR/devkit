---
id: FB-padr-title-branch-length-limit
title: PADR title refused with the branch-length reason of a proposal slug
scope: repo
kind: friction
category: docs-mismatch
target: devkit spec proposal padr
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-padr-title-branch-length-limit] PADR title refused with the branch-length reason of a proposal slug

## 1. Friction / Question (friction, question)

- **Context**: recording a PADR for `SPEC-direct-planning-procedure` in a `planning-worker` run.
- **Expectation**: the `planning-worker` contract and the proposal template show `devkit spec proposal padr <slug>
  "<title>"` with no length limit; a PADR has no branch of its own.
- **Actual**: a 69-character title was refused with `SPEC_PROPOSAL_SLUG_INVALID`, explaining that `plan-<slug>` and
  `dev-<slug>` branches must fit 64 characters, a reason that applies to proposal slugs, not PADR ids.
- **Workaround (or Interpretation Chosen)**: shortened the title; one retry.
- **Suggestion**: either state the 59-character PADR title limit where the command is documented, or give the PADR
  path its own code and reason (an id length limit) so the message matches the object.

## Diagnostic Details

- **Reproduction**: `devkit spec proposal padr direct-planning-procedure "Planning steps split between a spec reference
  and the worker contract" --summary x`.
- **Expected / Actual**: expected a PADR or a PADR-specific refusal; got the proposal slug refusal.
- **Versions**: devkit-spec at the `plan-direct-planning-procedure` branch, base `97cdcd8`.
- **Conditions**: `local-orchestrated` Planning, `planning_effort: low`.
- **Workarounds Attempted**: shorter title, succeeded.
- **Related Assets**: `packages/devkit-spec/src/devkit_spec/errors.py` (`SPEC_PROPOSAL_SLUG_INVALID`), the
  `planning-worker` contract step 3.

## Evidence

```text
[ERROR]  (SPEC_PROPOSAL_SLUG_INVALID) title 'planning-steps-split-between-a-spec-reference-and-the-worker-contract'
is 69 characters; at most 59, so its activity branches plan-<slug> and dev-<slug> fit 64 characters
[FIX]    Pass a shorter title
```

- **Disposition**: `session` task `dev-feedback-resolutions`: parameterized `limit` in `devkit_spec.proposals.scaffold.new_slug` with default `SLUG_LIMIT`, and passed `limit=None` in `create_padr`. Verified with `pytest packages/devkit-spec/tests/proposals/test_proposal_scaffold.py -k test_create_padr_title_longer_than_proposal_slug_limit`: a 69-character title is accepted and creates the matching PADR file.

