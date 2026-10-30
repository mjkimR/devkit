---
id: MAT-planning-acceptance-route-comparison
title: Planning acceptance route and terminal-readiness comparison
summary: "Compare Host-run composed acceptance, an operator acceptance job and the split record-then-integrate route by Host actions per acceptance, and trace the no-current-stage readiness and the composed dry-run gap to their code."
created_at: 2026-10-30
---

# [MAT-planning-acceptance-route-comparison] Planning acceptance route and terminal-readiness comparison

## Evidence boundary

Read at `fdba6646` in the `plan-git-operator-planning-completion-route` worktree. Code paths are cited as they stand
there; `PROP-integration-merge-moved-target` is in Planning in parallel, so its settled direction (a conflict-free moved
target merged by the integrating command itself, refusal only on a real conflict or failing readiness) is treated as an
assumption, not as current behavior. No route was timed; the comparison counts Host actions, not tokens, cost or
latency.

## What the existing commands already do

- `devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff [--effort]` runs from the
  retained base (`_base_checkout` in `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`).
  One command checks Planning readiness on `plan-<slug>` (`_Acceptance.preview`), writes and commits the acceptance
  record on the Planning branch (`_Acceptance.accept`), merges the branch through the guarded integration service,
  cleans up, and with `accept_and_handoff` creates `dev-<slug>` and hands off.
- A rerun after a partial result whose acceptance commit already landed takes the `status: accepted` branch of the
  preview and continues with integration (`self.completed = ["acceptance_commit"]`).
- Generic `devkit integration prepare|integrate` refuses a proposal unit that is not `accepted` with its
  `gate:plan-accept` recorded (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py`), so
  the split route needs a separate acceptance record and commit before integration.
- `accept --mode` refuses `--check` and `--direct` with a usage error
  (`packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`, `accept_cmd`).

## Host actions per accepted proposal

| Route | Host actions | Observed |
| --- | --- | --- |
| A. Host runs composed `accept --mode` | 1 command, then verify the landed head and absent resources | This repository, 2026-10-30; consumer pilot first acceptance |
| B. Operator `accept-proposal` job running the same composed command | 1 dispatch with current authority, then verify the returned effects | Not exercised; `handoff` is already an operator job over the composed `handoff --effort` |
| C. Split: Host `accept` in the Planning worktree, commit, operator `prepare-integration`, operator `execute-integration` | 2 Host commands, 2 dispatches, then verify | Consumer pilot, five acceptances |

Route C costs about four Host actions where A and B cost one, and its intermediate state (accepted but not
integrated) is the same partial result the composed command already recovers by a rerun. Route C therefore adds
no capability beyond A or B.

## Terminal readiness under `plan-accept=auto`

`Evaluation.gate` (`packages/devkit/src/devkit_agt/features/workflow/usecases/evaluate.py`) passes an `auto` gate
by policy. In `sdd-proposal`, the `direction-handoff` exit `frontmatter(proposal.md status reviewing|accepted)` holds for
a `reviewing` proposal and `handoff` has no exit, so once feedback is swept `devkit workflow next` prints
`[STAGE: - complete=yes]` (`packages/devkit/src/devkit_agt/features/workflow/cli/render.py`) although no acceptance
command ran. `worker-records.md` §1 tells a worker to record `--stage` as the stage `next` names, which is `-` here.
The composed acceptance accepts this state as ready (`not evaluation.complete and ... stage != direction-handoff` is
false when complete), so the readiness is correct for the CLI and only the worker's stage choice lacks guidance.

Which stage a worker names matters (scout trace, `envelopes/scout-01.yaml`):

| Recorded `--stage` | Effect |
| --- | --- |
| `-` | Refused by the envelope authoring contract |
| An unknown stage name | Accepted at write time; holds every gate, `plan-intent` included, until `envelope commit` refuses it |
| `direction-handoff` | Open questions hold `plan-accept`; composed and basic acceptance both refuse |
| `handoff` | Open questions hold no gate; the basic acceptance under `ask` is not blocked (inferred), the composed one is |

## Order of writes in the composed acceptance

Preparation (`IntegrationService._prepare`: `plan_finish` containment, prospective policy, `_Acceptance.preview`,
finish guards, cleanup scopes) writes nothing. Then, under the integration lock: acceptance record and commit on
`plan-<slug>`, a fresh preparation, merge, cleanup and, for `accept_and_handoff`, the handoff. A refusal after the
acceptance commit needs the base to move between the two preparations
(`packages/devkit/tests/integration/features/integration/test_composition.py` covers it at the service level). A dry
run repeats only the first preparation, so it cannot exclude that race.
