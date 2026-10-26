# Planning

Read this to run one Planning turn of a proposal on its `plan-<slug>` branch, from `draft` toward `plan-accept`. The runner is the Host in `direct` mode or a `planning-worker`, whose contract adds its worktree and return obligations. Run the CLI from the assigned worktree. If the turn needs a document ID or CLI feature the worktree lacks, record it as a problem for the Host to refresh the branch; never merge or emulate the command.

## Steps

1. On the first turn set `status: reviewing` in `proposal.md` and commit it.
   - If the proposal must be split (or carries `needs_decompose: true`), return it: set `status: draft` and `needs_decompose: true`, keep what you learned in `materials/`, close open questions with an `answer` envelope (`choice: null`, "Planning ended: returned to Backlog for decomposition"), commit and end. The Host continues with the [Backlog return procedure](backlog.md#return-from-planning-for-decomposition).
2. If answers to earlier questions arrived, record them first as a commit of their own (`devkit workflow envelope answer --unit <proposal dir> --answers-to <worker-NN.yaml> --answers-file -`, [worker records](worker-records.md) §2), then fold the decisions into `proposal.md` and the PADRs in a separate commit.
   - Create a PADR with `devkit spec proposal padr <slug> "<title>" --summary "<Y-statement>"` and read the scaffold before writing its body.
   - Withdraw a PADR the answers dropped by deleting its file in the fold commit, because handoff promotes every PADR left in `decisions/`. Name it and the reason in the proposal's Planning decisions and remove references to it.
3. Review the proposal at the Planning `activity-effort` ([effort](effort.md); `high` rounds follow the [review loop](review-loop.md)).
   - Record each `scout` or `challenger` return with `devkit workflow envelope new --unit <proposal dir> --kind scout|challenger --stage spike --findings-file -`; put comparisons and evidence into `materials/`.
   - After folding a `challenger` round, close it with `devkit workflow envelope reverify --unit <proposal dir> --stage spike --from envelopes/challenger-NN.yaml`: `--resolve <N>` per folded finding, `--waive "<N>=<reason>"` for a P2 or P3 not taken; leave `Decision needed:` findings open for `plan-accept`. A later reverify of the same round starts from its last reverify, so pass only the findings that turn closes.
   - Wait for every support role you start before relying on its result; a role that fails is a problem.
   - `devkit workflow next` may list `spike` as done before any review ran; only the recorded `scout`, `challenger` and `reverify` envelopes are Planning evidence.
4. Collect every question for the user in one round, after finishing all work that does not depend on an answer. Give each a recommended option; an ambiguous answer becomes a new question, never a guess.
5. Before the final work commit, check `dev_effort` in `proposal.md` against the settled design and update it if Development thoroughness changed. Run `devkit rules check <proposal dir>/proposal.md` and clear every `RULE-proposal-boundaries` report; name a path Development will create by its nearest existing parent.
6. Record feedback and end the turn as the [planning run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage) and [worker records](worker-records.md) §1 define: one `worker` envelope with `--stage`, `--effort` and `--head <last work commit>`, the questions via `--questions-file -`, committed with the turn's last changes.
