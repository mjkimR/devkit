# Worker records: questions, answers, problems and resolutions

Read this when a Planning or Development run ends, when you process a run's questions or problem, and when `devkit workflow next` or `devkit workflow envelope check` prints `[PENDING_QUESTION]` or `[BLOCKED]`. devkit owns the format and the checks; this says who writes what (session: no records).

The rule: **one run leaves one `worker` envelope; what another actor does later is a separate envelope that names it.** The questions a run asks and the problem it stopped on live in its `worker` envelope; the answers live in an `answer` envelope (`answers_to`), the fix in a `resolution` envelope (`resolves`). There is no separate question or problem kind.

## 1. The `worker` envelope (one per run)

Every run of one activity's turn ends with exactly one `worker` envelope, not one per stage: completed, waiting for answers or stopped by a problem. A worker writes its own; in `direct` mode you write it whenever you stop for the user or end the activity.

```bash
devkit workflow envelope worker --unit <dir> --stage <stage> --summary "<what this run did>" \
  --effort <low|medium|high> --check tests="PASS 14/14" --head <last commit>
```

- Always pass `--stage` (the stage `devkit workflow next` names once the run's other records are written) and `--effort` (the only record of the effort the run applied).
- `--head <last commit>` is `git -C <worktree> rev-parse HEAD` after the run's last work commit, before the commit that adds this envelope. That next commit (alone, or with the run's last changes) is the run's **final HEAD**, the one it returns to you, so `diff_scope.head` is always the parent side of the final HEAD, never equal to it: validate the range up to the final HEAD and check that `diff_scope.head` is its ancestor ([spec-delegate's worker reference](../../spec-delegate/references/worker.md)).

- **Questions**: add `--questions-file <path>|-`, a YAML list of `id`, `title` (40 characters at most), `prompt`, optional `context` (what the answer decides and why it matters, for a reader who has not seen the work), `options` (`{id, description, recommended}`, at most one recommended) and `allow_note`; the status becomes `needs_input`. Gather every question of the round in it; finish everything that does not depend on an answer first.
- **Problem**: add `--problem "<cause>" --tried "<attempt>" --recovery "<recommended recovery>"`; the status becomes `failed`, or pass `--status needs_input` when only the user can decide. A run that both asks and hit a problem records both (`needs_input`). A malformed `worker` envelope holds the unit like a problem (from the stage it states, or every gate when none is readable): fix the file, never answer that stage's gate again.
- **Emergency commit**: a run that stops on a problem commits its unfinished work with the envelope, so the next actor sees the state. This commit alone may use `git commit --no-verify` when the commit gate refuses the unfinished files; name every check it skipped in the problem (`--tried "commit gate rules-check refused: RULE-x in spec.md"`). Every other commit keeps the gate.
- A problem is only what breaks the agreed goal, scope or contract, or what cannot be solved at all; a choice you can decide is not one, and neither is waiting for answers.

Before the last work commit, capture observed feedback inside the proposal or spec, even on questions or problems; Planning runs also follow [planning run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage).

## 2. Answers

Unanswered questions (`[PENDING_QUESTION: ...]`) hold the gate of the run's stage and every later one, and the handoff, until answered by an `answer` envelope, never `devkit workflow answer`.

- Ask the user all questions in one round with their options and recommendation; ask back at once about anything ambiguous.
- The run that processes the answers records them first, in a commit of its own, then folds the decisions into the documents (proposal and PADRs, or `spec.md` and `plan.md`) in a separate commit. In `local-orchestrated` the new worker writes the record from your rewritten answers; in `direct` you write it:

```bash
devkit workflow envelope answer --unit <dir> --stage <stage> --summary "q1, q2 decided" \
  --answers-to worker-NN.yaml --answers-file -    # - { question: q1, choice: a, decision: "...", constraints: [...] }
```

- One decision sentence per question; `choice: null` for an answer outside the options; `constraints` only for what the answer adds. When a rejection or a return to Backlog for decomposition ends the Planning, the party ending it closes every question still open the same way: `choice: null` and the reason (`"Planning ended: rejected by the user"`) as the decision, in the commit that ends it; otherwise the open questions hold the Planning branch's merge. Never the raw conversation, the reasoning or the question again. An answer that leaves something ambiguous becomes a new question in the next run's `worker` envelope, never a guess.

## 3. Problems and resolutions

`[BLOCKED: ...]` means a problem has no `resolution` that names it (or a `worker` envelope is malformed: fix the file). It holds the gates of the problem's stage and later ones, the handoff and `devkit worktree finish --merge`; `devkit workflow next` still names the current stage, where the recovery runs. A later commit, a successful `worker` envelope, a comment or a rerun request clears nothing.

- You decide the recovery inside the approved scope, with strong autonomy: fix or revert yourself (`git revert`, never reset), or send a new worker the recovery request. Record a problem you find yourself (a worker's range you cannot accept) in your own `worker` envelope (`--problem`). A recovery that needs the scope changed goes to the user and a close ([classification](classification.md) §4).
- Whoever actually fixed it writes the resolution, in the same commit as the fix; one who could not fix it writes none and records what it tried in its own `worker` envelope:

```bash
devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml \
  --summary "<what was done and why it resolves the problem>"
```

## 4. Checking and integrating

`devkit workflow envelope check --unit <dir>` lists the files, `[BLOCKED]` and `[PENDING_QUESTION]` (`--format json`: `blocked`, `problems`, `pending_questions`, `malformed_workers`). Whoever merges a pull request (you, `spec-integrate` or the cloud service) runs it on the PR head first and merges only with `"blocked": false` and no `pending_questions`; `devkit worktree finish --merge` checks the same itself.
