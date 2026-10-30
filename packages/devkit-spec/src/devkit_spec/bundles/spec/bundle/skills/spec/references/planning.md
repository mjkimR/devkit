# Planning

Read this to run one Planning turn of a proposal on its `plan-<slug>` branch, from `draft` toward `plan-accept`. The runner is the Host in `direct` mode or a `planning-worker` (its contract adds worktree and return obligations); run the CLI from the assigned worktree. A document ID or CLI feature the worktree lacks is a problem for the Host to refresh the branch; never merge or emulate the command.

## Steps

1. On the first turn, set `status: reviewing` in `proposal.md` and commit.
   - If the proposal must be split (or has `needs_decompose: true`, or a `size` other than absent or exactly `S`, `M` or `L`), return it: set `status: draft` and `needs_decompose: true`, keep what you learned in `materials/`, close open questions with an `answer` envelope (`choice: null`, "Planning ended: returned to Backlog for decomposition"), commit and end. The Host continues with the [Backlog return procedure](backlog.md#return-from-planning-for-decomposition).
2. When answers to earlier questions arrived, record them first per [worker records](worker-records.md) §2, then fold the decisions into `proposal.md` and the PADRs.
   - New PADR: `devkit spec proposal padr <slug> "<title>" --summary "<Y-statement>"`; read the scaffold before writing its body.
   - Withdraw a PADR the answers dropped by deleting its file in the fold commit (handoff promotes every PADR left in `decisions/`); name it and the reason in the proposal's Planning decisions and remove references to it.
3. Review the proposal at the Planning `activity-effort` ([effort](effort.md); `high` rounds follow the [review loop](review-loop.md)).
   - Record each `scout` or `challenger` return with `devkit workflow envelope new --unit <proposal dir> --kind scout|challenger --stage spike --findings-file -`; comparisons and evidence go into `materials/`.
   - After folding a `challenger` round, close it with `devkit workflow envelope reverify --unit <proposal dir> --stage spike --from envelopes/challenger-NN.yaml`: `--resolve <N>` per folded finding, `--waive "<N>=<reason>"` for a P2 or P3 not taken; leave `Decision needed:` findings open for `plan-accept`. A later reverify of the same round starts from its last reverify: pass only the findings that turn closes.
   - Wait for every support role you start before relying on it; a failed role is a problem.
   - When the proposal drafts screens (a Screens section of `target-docs.md`, `ux-writing`), offer the optional `ux-reviewer` (`spec-ux-review`), each round recorded as `ux-review-NN.yaml` at `spike`; its open findings go into the `plan-accept` request beside the `challenger` and `scout` envelopes.
   - `devkit workflow next` may list `spike` as done before any review ran; only the recorded `scout`, `challenger` and `reverify` envelopes are Planning evidence.
4. Collect every question for the user in one round ([worker records](worker-records.md) §1-§2), after all work that does not depend on an answer.
5. Before the final work commit, update `dev_effort` in `proposal.md` if the settled design changed Development thoroughness. Run `devkit rules check <proposal dir>/proposal.md` and clear every `RULE-proposal-boundaries` report; name a path Development will create by its nearest existing parent.
   - For a before/after outcome against the base (a timing or a count), name a baseline a development worker can produce in its worktree: the head with the change disabled, or a measurement Planning takes on the same machine and records in `materials/`. Otherwise state that the Host takes the base measurement: a worker never checks out another commit.
6. End the turn as the [planning run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage) and [worker records](worker-records.md) §1 define: record feedback, then one `worker` envelope with `--stage`, `--effort`, `--head <last work commit>` and the questions via `--questions-file -`, committed with the turn's last changes. When `next` prints `[STAGE: - complete=yes]` while `proposal.md` is still `reviewing`, `--stage` is `direction-handoff`, never `handoff` or `-`.
