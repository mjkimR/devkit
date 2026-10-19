---
id: ADR-executor-neutral-planning-steps-in-a-spec-reference
title: Executor-neutral Planning steps in a spec reference
summary: Moves the executor-neutral Planning steps into spec/references/planning.md and keeps only the worker-specific obligations (worktree paths, nested roles, return fields, write boundaries, emergency commit) in the planning-worker contract.
proposal: SPEC-direct-planning-procedure
status: accepted
created_at: 2026-10-19
---

# [ADR-executor-neutral-planning-steps-in-a-spec-reference] Executor-neutral Planning steps in a spec reference

- **Status**: Accepted
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

The ordered Planning steps exist only in the `planning-worker` contract's `## Procedure` (steps 2 to 6). A Host that
runs Planning in `direct` mode has to read a subagent prompt written for another actor
(`FB-direct-planning-procedure-location`). Q1 asks which steps are executor-neutral and which belong to the role.

`CAP-DLV-delivery-workflows` puts a procedure in the contract only "for a role whose procedure no main session runs"
(`SPEC-subagent-procedure-in-contract`); the role table lists `planning-worker` as "none: the procedure is in the
contract". A `direct` Host does run Planning, so by that rule the steps belong on the skill side, as `spec-review` does
for `code-reviewer`.

## 2. Decision Drivers

- One place to change the Planning steps; no copy that can drift.
- A `direct` Host reaches the steps from the `spec` skill's routing table.
- The worker contract keeps everything only a nested, one-shot worker needs.

## 3. Considered Options

1. **Move the neutral steps to `spec/references/planning.md`; the contract cites it** (chosen).
2. Copy the steps into a reference and keep them in the contract: two texts to keep in step.
3. Point the routing table at the contract for `direct` Hosts: the FB's workaround, still a prompt for another actor.

## 4. Decision Outcome

Option 1. The split:

| Step (contract today) | Goes to |
| --- | --- |
| 2: first turn sets `status: reviewing` and commits; `needs_decompose` return with the closing `answer` envelope | reference |
| 3: answers recorded first in their own commit, then folded; PADRs with `--summary`, read the scaffold first | reference |
| 4: review depth per effort (citing `effort.md` and `review-loop.md`), recording each `scout`/`challenger` return as its envelope, evidence in `materials/` | reference |
| 4: start roles as nested subagents (Host -> worker -> role), wait for every one, never end the turn while one runs | contract |
| 5: questions in one round with a recommended option, ambiguity becomes a new question, `dev_effort` check | reference |
| 6: observed feedback, the `collect-feedback` sweep before the single `worker` envelope, its fields | reference |
| 1: worktree only, absolute paths and `git -C <worktree>`, scratch inside the worktree | contract |
| Input, Return (`final_head`), Write boundaries, On a problem (emergency commit, `--no-verify` rule) | contract |

The reference addresses "you" as the executor of the Planning turn and names the `direct` Host and the worker alike;
`worker-records.md` stays the source for envelope mechanics and is cited, not restated. The contract's `## Procedure`
keeps step 1, the nested-role rule and one step "Follow `.devkit/managed/spec/skills/spec/references/planning.md`",
by the managed path the contract already uses for `review-loop.md` and `sweep.md`.

## 5. Consequences

- The worker reads one more file at spawn (about 4.5 KB), as it already does for `review-loop.md` and `sweep.md`.
- Development updates the `planning-worker` row of the `CAP-DLV-delivery-workflows` role table (procedure in `spec/references/planning.md`)
  and the sentence on where worker procedures live; `CAP-HARN-agent-guidance` lists only the asset ids and needs no
  change.
- Tests that pin phrases in the contract body move with the text: `test_the_planning_worker_collects_questions_in_one_round`
  and the planning half of `test_a_run_records_its_questions_and_problem_in_one_worker_envelope` read the reference;
  `test_a_worker_commits_its_result_and_records_in_its_worktree` keeps its contract assertions (`git -C <worktree>`,
  `MUST NOT`, `final_head`, `devkit workflow envelope worker`), so those phrases stay in the contract.
  `test_every_restatement_cites_the_loop` keeps `review-loop.md` in the contract only if the contract still names
  it; otherwise the reference joins `CITING` in place of the contract.
