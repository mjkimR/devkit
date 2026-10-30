# Worker records: questions, answers, problems and resolutions

Read when a Planning or Development run ends, when you process a run's questions or problem, or when `devkit workflow next` or `devkit workflow envelope check` prints `[PENDING_QUESTION]` or `[BLOCKED]` (session: no records).

One run leaves one `worker` envelope holding its questions and its problem; another actor's later action is a separate envelope naming it: an `answer` (`--answers-to`) or a `resolution` (`--resolves`). There is no separate question or problem kind.

## 1. The `worker` envelope (one per run)

Every run ends with exactly one, whether it completed, waits for answers or stopped on a problem. A worker writes its own; in `direct` mode you write it when you stop for the user or end the activity. A pause without a question or problem records `completed` with the pending step in its summary.

```bash
devkit workflow envelope worker --unit <dir> --stage <stage> --summary "<what this run did>" \
  --effort <low|medium|high> --check tests="PASS 14/14" --head <last work commit>
```

- `--stage` is the stage `devkit workflow next` names after the run's other records; `--effort` is the only record of the applied effort.
- **Final Planning return**: when `next` prints `[STAGE: - complete=yes]` while `proposal.md` is still `reviewing` (under `plan-accept = "auto"` before any acceptance ran), record the `worker` envelope at `direction-handoff`, never `handoff` or `-`: open questions recorded there hold `plan-accept`. The run records no acceptance or handoff effect; `devkit spec proposal accept` does.
- `--head` is `git -C <worktree> rev-parse HEAD` after the last work commit; the commit that adds the envelope is the run's final HEAD.
- **Questions**: add `--questions-file -`, a YAML list of `id`, `title` (at most 40 characters), `prompt`, `context` (what the answer decides and why it matters now, for a reader who has not seen the work), `options` (`{id, description, recommended}`, one recommended) and `allow_note`. An option that depends on a condition also states what holds when it does not.
- **Problem**: add `--problem "<cause>" --tried "<attempt>" --recovery "<recommended recovery>"`; `--status needs_input` when only the user can decide. A problem breaks the agreed goal, scope or contract or cannot be solved; a choice you can make, or waiting for answers, is not one.
- **Emergency commit**: a run that stops on a problem commits its unfinished work with the envelope. Only this commit may use `git commit --no-verify`, and only on ordinary commit-gate refusal of the unfinished files, never for sandbox or approval denial; name each skipped check in `--tried`.
- On any refused or unavailable approval, on every host, stop that operation and preserve the state; never reroute through another tool, path, process, broader request or setting.
- If the record or commit itself is denied, stop, preserve the state and return `failed` with the actual last commit, dirty paths and the absent/uncommitted record or commit; never invent a committed envelope.
- A malformed `worker` envelope holds the unit like a problem: fix the file.

## 2. Answers

Unanswered questions hold the gates from the run's stage on and the handoff until an `answer` envelope answers them; `devkit workflow answer` does not.

- Ask the user all questions in one round, with options and the recommendation.
- The run that processes the answers records them first in a commit of its own, then folds the decisions into the documents in a separate commit. In `local-orchestrated` mode the new worker writes the record from your rewritten answers; in `direct` mode you write it:

```bash
devkit workflow envelope answer --unit <dir> --stage <stage> --summary "q1, q2 decided" \
  --answers-to worker-NN.yaml --answers-file -    # - { question: q1, choice: a, decision: "...", constraints: [...], by: user }
```

- One decision sentence per question; `choice: null` for an answer outside the options; `constraints` only for what the answer adds.
- Name who decided each answer in its `by`: `user` for the user's decision, `host` for the Host's own decision within approved scope, `policy` for one a policy settles. The Host's rewritten answers name `by` per answer, and the recording run copies it; there is no `--by` flag. Any other value is refused (`ENVELOPE_ITEMS_INVALID`).
- A decision that settles one of the run's `assumptions` goes into `--settle N=<decision>` (`N` its 1-based position), not `constraints`.
- When a rejection or return to Backlog ends the Planning, close every open question the same way (`choice: null`, the reason as the decision) in the commit that ends it.
- An ambiguous answer becomes a new question, never a guess.
- To correct a recorded answer, write a later `answer` envelope for the same `worker` envelope whose summary names the corrected record (`"q3 corrected; corrects answer-01.yaml"`); never edit the earlier one.
- Direction that answers no recorded question goes into the documents and the next worker summary, without an `answer` envelope.

## 3. Problems and resolutions

`[BLOCKED: ...]` means a problem has no `resolution` naming it. It holds the gates from the problem's stage on, the handoff and `devkit worktree finish --merge`; `devkit workflow next` still names the stage where recovery runs. Only a `resolution` clears it.

- Decide the recovery inside the approved scope: fix or revert yourself (`git revert`, never reset), or send a new worker the recovery request. A recovery that needs the scope changed goes to the user and a close ([close](depth-and-close.md#close)).
- Record a problem you find yourself in your own `worker` envelope (`--problem`).
- Whoever fixed it writes the resolution in the same commit as the fix; one who could not writes none:

```bash
devkit workflow envelope resolution --unit <dir> --resolves worker-NN.yaml \
  --summary "<what was done and why it resolves the problem>"
```

Before merging a pull request, run `devkit workflow envelope check --unit <dir> --format json` on its head and merge only with `"blocked": false` and no `pending_questions`.
