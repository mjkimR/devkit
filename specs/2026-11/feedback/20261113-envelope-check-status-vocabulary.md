---
id: FB-envelope-check-status-vocabulary
title: Envelope --check accepts only PASS, FAIL or SKIP, so a check not rerun must be recorded as SKIP
scope: repo
kind: friction
category: missing-capability
target: devkit workflow envelope new --check
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-13
---

# [FB-envelope-check-status-vocabulary] Envelope --check accepts only PASS, FAIL or SKIP, so a check not rerun must be recorded as SKIP

## 1. Friction / Question (friction, question)

- **Context**: A consumer reviewer recorded `review-01` for a spec Unit. It relied on the implementer's passing
  `just check` and `just lint` at the same head instead of rerunning them.
- **Expectation**: The check result can say that a check passed earlier at the same head and was not rerun.
- **Actual**: `--check` accepts only `name=PASS|FAIL|SKIP[ detail]`. The reviewer's "not rerun" status was refused,
  so it became `SKIP NOT RERUN ...`. A reader cannot tell a skipped check from one that passed at the same head.
- **Workaround (or Interpretation Chosen)**: `build: SKIP NOT RERUN just check / just lint; implementer reported PASS
  at same head <sha>`.
- **Suggestion**: Either document in the review guidance that a check inherited from the same head is recorded as
  `SKIP` with the source envelope named in the detail, or add a distinct result (for example `INHERITED`) that stage
  exits treat like `SKIP`.

## Diagnostic Details

- **Reproduction**: `devkit workflow envelope new --kind review ... --check "build=NOT_RERUN ..."` in a consumer Unit;
  exact command not retained.
- **Expected / Actual**: Expected a status for a check not rerun; actual refusal of any value outside
  PASS, FAIL and SKIP.
- **Versions**: consumer-installed devkit, revision unknown; option help checked at devkit `569379a06`.
- **Conditions**: `review-refine` stage of a `sdd-spec-feature` Unit in a consumer repository.
- **Workarounds Attempted**: recorded `SKIP` with a detail; accepted.
- **Related Assets**: `devkit workflow envelope new --help` (`--check TEXT  Check result name=PASS|FAIL|SKIP[ detail]`),
  `CAP-DLV-workflow-envelopes`, the `spec` skill's `references/review-loop.md`.

## Evidence

```text
review-01.yaml (consumer): build: SKIP NOT RERUN just check / just lint; implementer reported PASS at same head <sha>
devkit workflow envelope new --help: --check TEXT  Check result name=PASS|FAIL|SKIP[ detail] (repeatable)
```

## Disposition

Resolved through `SPEC-feedback-guidance-clarifications`. Reviewer checks not rerun use SKIP with source envelope and exact SHA; supplied input is distinct from executed checks. PASS/FAIL/SKIP remain unchanged.

Verification: AC-02; test_feedback_guidance.py check provenance scenario; spec bundle 685 passed, docs bundle 9 passed, affected all-tier 2664 passed
and independent code review with no findings at f356771f1224f847d459c39e339a0b8c31480030, retained in the Unit's
build-check-01 and review-01 envelopes. This resolves the authorized guidance scope; live consumer/model behavior
remains best effort and unverified.
