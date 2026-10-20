# Engine and tooling evidence for direct acceptance

Planning material for `SPEC-draft-direct-acceptance` (2026-10-19): what the current devkit and devkit-spec code allow,
from a read-only `scout` pass at base `298dd9e` (envelope `scout-01.yaml`). Paths are repository-relative.

## Gate order in `sdd-proposal`

- Stages in order: `intent-proposal` (`plan-intent`), `spike` (optional), `collect-feedback` (not optional, exit
  `envelope-check-pass(feedback swept)`), `direction-handoff` (`plan-accept`, exit
  `frontmatter(proposal.md status reviewing|accepted)`), `handoff` (no exit), `exception`
  (`packages/devkit-spec/src/devkit_spec/bundle/workflows/sdd-proposal.md`).
- The engine answers only an open request of the current stage; anything else is `REQUEST_UNKNOWN`
  (`packages/devkit/src/devkit/workflow/answers.py:104-113`, `evaluation/requests.py:86-104`). A stage's gate is asked
  only once its exit checks hold (`evaluation/evaluate.py:364-366`), and the frontmatter check reads the working tree
  (`evaluation/primitives.py:54-63`).
- So a direct acceptance has a fixed order: record `plan-intent` while `intent-proposal` is current (the draft);
  satisfy `collect-feedback`; write `status: accepted` to disk; record `plan-accept`; commit. Recording `plan-accept`
  before the status change fails with `REQUEST_UNKNOWN`.

## The `collect-feedback` exit

- It needs the latest `feedback` envelope with `status: completed` and a `swept` check starting with `PASS`
  (`primitives.py:95-103`). `--given` does not satisfy a disk check (`evaluate.py:155-163`).
- `[workflow.stages] collect-feedback = "off"` skips it, but project-wide and for Development as well
  (`packages/devkit/src/devkit/workflow/project/config.py`). Making it `optional` in `sdd-proposal` alone passes the
  shared-stage validation (`definition/validation.py:36`), but an optional unmet stage is passed over, so normal
  Planning would stop requiring the sweep too (`evaluate.py:372-373`).
- `devkit workflow envelope new --kind feedback --stage collect-feedback` does not check the current stage
  (`workflow/cli/envelope.py:120-208`), so the executor of a direct acceptance can write a real sweep of its own
  session before accepting. The only documented skip token today is `skipped=capture.requested-only`.
- Conclusion: the schema of `sdd-proposal` can stay as it is if the executor of the direct acceptance sweeps its own
  session (the acceptance exchange, usually zero observations, a valid PASS). The claim in the draft's §1.1 that the
  workflow "does not need Planning to run" holds only with that sweep.

## What the handoff checks and carries

- It refuses a branch other than `dev-<slug>`, a missing proposal, a status other than `accepted`,
  `needs_decompose: true`, invalid fields, a slug conflict and existing targets
  (`packages/devkit-spec/src/devkit_spec/proposals/handoff.py:259-296, 325-327, 439-442`).
- It does **not** require a recorded `gate:plan-accept`, evaluate the workflow stage, or check feedback envelopes,
  open questions or holds; a missing gate is simply not carried, with no warning (`handoff.py:276-296, 607-626`).
- It carries the body into `spec.md`/`plan.md`/`tasks.md`, `target-docs.md`, PADRs promoted to ADRs, open feedback,
  materials, `namespace`, `summary`, `milestone`, `decomposed_from`, `supersedes`, and both gate records by name;
  `dev_effort` is returned in the result. There is no `issue` field anywhere in devkit-spec.
- The only code that validates a complete Planning outcome (status, both gates, evaluation complete, no hold) is the
  `plan-<slug>` integration check (`packages/devkit-spec/src/devkit_spec/integration.py:236-283`). It runs only on
  the MCP local integration path (`integration_integrate`, `packages/devkit/src/devkit/integration/service.py:140-142`);
  `devkit worktree finish --merge` runs only the envelope-hold guard (`packages/devkit/src/devkit/worktree/cli.py:216`).
  So today nothing reliably checks a hand-set `status: accepted` before the handoff.
- `devkit spec proposal check` has no modes; it refuses while `plan-<slug>` exists or the status is not `draft`
  (`proposals/backlog.py:31-58`). No rule, commit gate or hygiene check looks at proposal status transitions;
  `devkit workflow answer` makes no branch check.
