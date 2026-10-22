# Planning

Read this to run one turn of a proposal's Planning on its `plan-<slug>` branch, taking a `draft` proposal toward `plan-accept`. "You" is whoever runs the turn: the Host in `direct` mode or a `planning-worker` in `local-orchestrated` mode, whose contract adds its worktree, nested-role, return and write-boundary obligations. The depth per effort is in [effort](effort.md); the mechanics of the `worker` envelope, its questions, answers, problems and resolutions are in [worker records](worker-records.md).

## Worktree context and refresh

- Read operational instructions from the assigned worktree and run its CLI with that worktree as cwd. Entry-checkout
  instructions do not establish support for newer commands in an older worktree.
- Before starting or resuming a turn that needs documents or CLI features from a newer base, the Host incorporates
  that base and synchronizes the assigned worktree's installed instructions under existing Git and permission policy,
  then resumes with the refreshed context.
- When the turn does not depend on the base's changes, do not refresh solely because the base advanced.
- If a running worker discovers that a required document ID or CLI feature is absent, it records the dependency as a
  problem for Host refresh. It does not merge, resolve IDs from another branch, hide missing references as plain
  prose, or fabricate envelope YAML to emulate unsupported commands.

## Steps

1. On the first turn set `status: reviewing` in `proposal.md` and commit it.
   - If the proposal is marked `needs_decompose: true`, or you find it must be split, it goes back: set `status: draft` and `needs_decompose: true`, keep what you learned in `materials/`, close every question still open from an earlier run with an `answer` envelope (`choice: null`, the decision "Planning ended: returned to Backlog for decomposition"), commit and end.
   - Return the committed result to the Host for the [Backlog return procedure](backlog.md#return-from-planning-for-decomposition); setting `draft` alone does not release the Planning branch.
   - A worker does not merge, remove branches or create decomposed children in Planning.
2. When answers to earlier questions came (with a worker's payload, or from the user in `direct` mode), record them first, as a commit of their own.
   - Write an `answer` envelope naming the `worker` envelope that asked (`devkit workflow envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml> --answers-file -`): one choice and one decision sentence per question plus any new constraint, and `--settle N=<decision>` for each of the worker's `assumptions` the answers settle. Do not record the raw conversation.
   - Then fold the decisions into `proposal.md` and the PADRs in a separate commit.
   - Record a new PADR with `devkit spec proposal padr <slug> "<title>" --summary "<Y-statement by the decision-writing instruction>"`; `RULE-document-summary` refuses the handoff commit without a summary.
   - Read the scaffolded PADR before writing its body. Give an existing PADR without a summary one.
3. Review the proposal to the end at the Planning `activity-effort`:
   - `low`: questions only, no `scout` or `challenger`.
   - `medium`: one `challenger` pass always, and a `scout` when the direction needs evidence.
   - `high`: two or more options compared, a `scout` and then a `challenger` always, the `challenger` in the bounded rounds of [review loop](review-loop.md). Read it for the round rules: a new `challenger-NN` per round whose summary starts with `round <N>;`; a hand-over is a problem or a question in your `worker` envelope.
   - Record each `scout` or `challenger` return as its envelope (`devkit workflow envelope new --unit <proposal dir> --kind scout|challenger --stage spike ... --findings-file -`), which the `plan-accept` request reads. Put comparisons and evidence into `materials/`.
   - At `medium` and `high`, after folding a `challenger` round into the proposal, close it with one `devkit workflow envelope reverify --unit <proposal dir> --stage spike --from envelopes/challenger-NN.yaml`: `--resolve <N>` for each folded finding, `--waive "<N>=<reason>"` for a P2 or P3 not taken, and `Decision needed:` findings left open for `plan-accept`.
   - Wait for every support role you start to return before relying on its result, and never end the turn while one is still running. A role that fails or cannot finish is a problem.
   - Run this step at the Planning effort whatever `next` lists. `spike` has no exit check, so `devkit workflow next` may list it under `[DONE]` before any review ran: that is not Planning evidence. The evidence is the `scout` and `challenger` envelopes and their `reverify` recorded at `spike` (none at `low`).
4. Collect the questions for the user in one round, never stopping at the first: finish everything that does not depend on an answer first.
   - Give each question a recommended option when one is clear, else several options with one recommended.
   - An answer that leaves something ambiguous becomes a new question, never a guess.
   - Put the questions into this turn's `worker` envelope (step 5), never into a file of their own.
   - Before the final work commit, check `dev_effort` in `proposal.md` against the settled design and target boundaries; update it if the expected Development thoroughness changed.
   - Before the final work commit, run `devkit rules check <proposal dir>/proposal.md` and clear every `RULE-proposal-boundaries` report. Name a path the Development will create by its nearest existing parent directory, with the new path in the proposal text.
5. Record feedback, then end the turn with one `worker` envelope.
   - Before the last work commit, record concrete observations in this proposal's `feedback/` under `capture=observed`, also when waiting for answers or stopping on a problem.
   - Before every return, run the enabled `collect-feedback` sweep over this run and the committed records and write a fresh `feedback` envelope before the single `worker` envelope. Do not reuse a prior run's PASS as coverage.
   - Stage-off writes no sweep envelope but keeps observed capture; requested-only writes a policy-skip PASS without observations; incomplete coverage is `swept=FAIL <gap>` with `--unverified "<gap>"`. For the commands read [planning run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage).
   - End the turn with exactly one `worker` envelope: `devkit workflow envelope worker --unit <proposal dir> --stage <stage> --effort <activity-effort> --head <your last work commit> ...`. Pass as `--stage` the stage `next` names after the run's other records, and always pass `--effort`.
   - When questions wait, add `--questions-file -`, which makes the envelope `needs_input`. Give each question `id`, `title`, `prompt`, `context` and `options` with one `recommended`, written for the user: `context` says what the answer decides and why it matters now, each option what it leads to.
   - When you stop on a problem, add the problem.
   - Commit the envelope with the turn's last changes.
