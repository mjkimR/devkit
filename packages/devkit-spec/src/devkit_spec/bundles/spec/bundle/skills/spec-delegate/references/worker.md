# Worker results

Read this in Steps 4 to 6 of `spec-delegate` for a `planning-worker` or `development-worker`.

A worker is one-shot: it runs one turn in its activity branch's worktree and commits at every stage boundary. When
record/commit access is permitted, it ends with its head returned and exactly one `worker` envelope, also when it
stops on a question or a problem.

You validate the committed range, accept or block it, and decide what a recorded problem needs. Do not write the
worker's records for it. Record formats: the `spec` skill's
`references/worker-records.md`.

## The last accepted head

The range a worker is judged on starts at the unit's *last accepted head*:

- A unit that is not blocked: the worktree's HEAD when you spawn the worker (`git -C <worktree> rev-parse HEAD`), after
  your own commits (blocks, recoveries) are in.
- A blocked unit keeps the head its blocked range started from. Never pass a blocked unit's current HEAD as the base:
  the rejected commits must stay in the range.
- After context loss, when you cannot account for the last accepted head, validate the whole branch: from its merge
  base with the base branch.

Pass it as `diff_scope` base, and record the base checkout's `git -C <base> status --short` and HEAD before spawning.

## Validate the cumulative range

Run `devkit spec worker inspect --format json` in the worker worktree to collect the existing range, declared-scope,
cleanliness, committed-envelope, cumulative-rules and workflow checks.

- Inputs derive from committed records. Override one when the Host's record differs:
  - `--base <accepted>` and `--head <returned>` when the Host's recorded range differs;
  - `--scope <prefix>` repeated (or `--scope-file <file>`, one prefix per line) for the complete payload scope when it
    differs from the documents;
  - `--unit` and `--base-checkout` for those derived inputs.
- Each override replaces its input; scope overrides never union with the derived paths.
- The result names input and scope provenance, compared commits, changed paths, per-check pass/fail/not-run states
  and base-checkout observations. Existing codes and actions remain in the check results.
- Assess the cause of a not-run check; its absence is never evidence of a pass.
- Exit 0 means all executed checks passed, 1 a negative result, 2 unresolved required inputs or invalid invocation.

Inspection is evidence, not an approval gate or scope authority:

- The payload's boundaries and the acceptance procedure below still apply. Compare the base-checkout observations to
  the saved pre-spawn state yourself.
- The helper writes nothing, repairs nothing and never expands scope.
- Pass its JSON result, or at least `base`, `head` and `changed_paths`, to read-only reviewers.
- Existing separate commands remain available for focused verification.

From the last accepted head to the worker's *final HEAD* (`<returned>`: the `final_head` it returns, the commit that
contains its `worker` envelope), the range passes when all of these hold:

- `git -C <worktree> merge-base --is-ancestor <accepted> <returned>` succeeds, and the worktree's HEAD is `<returned>`.
- The envelope's `diff_scope.head` is an ancestor of `<returned>` (`merge-base --is-ancestor <diff_scope.head> <returned>`).
  It is the head of the work the worker did, committed before the envelope, so it is never `<returned>`: evidence
  about the work, not the end of the range.
- Every path of `git -C <worktree> diff --name-only <accepted> <returned>` is in the write scope, the worker's own
  records under `<unit>/envelopes/` and `<unit>/decisions/` included.
  - The rule covers every path except the records you wrote under `<unit>/envelopes/` since `<accepted>` (your
    blocking `worker` envelopes and your resolutions). Each of those must be unchanged since your commit of it
    (`git -C <worktree> diff <your commit> <returned> -- <envelope>` is empty).
  - After context loss, take as yours only the envelope commits `git log` shows touching nothing else and whose
    records you can account for; otherwise block.
- `git -C <worktree> status --short` is empty; the base checkout's status and HEAD are as recorded.
- The unit's checks pass on `<returned>`: the worker's results, confirmed by the pull request's CI or by rerunning them
  in the worktree. If the worker stopped on a problem, it returns unfinished work: validate its paths, not its checks.

## Accept or block

- **Accept**: write nothing; run `devkit spec scope update --spec <dir>`. The next spawn starts from HEAD.
- **Block**: the violation is a problem your validation run found.
  1. Record it as that run's own `worker` envelope at the unit's current stage (`devkit workflow next --unit <dir>`
     names it; `build-verify`, or `fix-verify` in `sdd-spec-bugfix`, while building), one finding per violation
     (path or check, cause):
     ```bash
     devkit workflow envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem "<the committed range breaks its boundary or checks>" --recovery "<what must change>" --findings-file - --base <accepted> --head <returned>
     ```
  2. Commit it before anything else, so the worktree stays clean.
  3. Keep the commits: never reset or amend; a pull request stays open and blocked (changes requested or a failing
     required check). A blocked unit goes to no review and no integration (`worker-records.md` §3).
  4. Send a new worker the findings as a recovery request, or fix it yourself, with further commits on the same
     branch (a revert commit for an out-of-scope change). Whoever fixes it commits a `resolution` naming your
     envelope with the fix.
  5. Then validate the cumulative range again from the same last accepted head.

A unit is blocked while any problem, a worker's or yours, has no resolution that names it (`[BLOCKED]` in
`devkit workflow next` and `devkit workflow envelope check`); a later commit or a successful `worker` envelope clears
nothing. A comment or a rerun request alone resolves nothing.

## Questions and problems

- **Questions** (`needs_input` without a problem; `[PENDING_QUESTION]`):
  - Put the questions of the worker's envelope to the user in one round. Restate each for the user instead of
    relaying it: what the answer decides and why it is asked now, and what each option leads to (scope, size,
    effort, what changes for the user).
  - Ask back at once about anything ambiguous.
  - Hand the rewritten answers to a new worker, which records them first as an `answer` envelope naming that
    `worker` envelope.
  - Waiting for answers needs no resolution, but it holds the gates from the run's stage on, and the handoff, until
    answered.
- **Problems** (`failed`, or `needs_input` with a problem):
  - Read the cause, what was tried and the recommended recovery, and decide it as the `spec` skill's
    `references/worker-records.md` §3 describes.
  - Inside the approved scope, fix or revert it yourself, or send a new worker the recovery request. Commit the
    resolution only with a fix that actually solved it.
  - If a problem needs the scope changed, it goes to the user and a close.

A worker records its feedback inside its own unit before its last work commit; a Planning run also returns fresh sweep
evidence ([run coverage](../../spec-feedback/references/sweep.md#planning-run-coverage)): validate the range against it.

## Permission failures and incomplete preservation

- Unavailable or denied approval stops the actual operation.
- A worker may attempt its failed record and emergency commit only through still-permitted scoped operations.
- If either also cannot run, require a `failed` return naming the actual last SHA, dirty paths, cause, commands
  tried, recommended recovery and absent/uncommitted record/commit. Accept no fabricated envelope, clean tree or
  committed final HEAD.
- `--no-verify` is only for an ordinary commit-gate refusal during the emergency commit, never for sandbox or approval
  denial. Do not switch tools, paths, processes, broader requests or host settings to evade refusal.

The Host MUST block a failed dirty or uncommitted return, even when no worker envelope could be written.

- Inspect actual HEAD/status and the cumulative allowed paths without accepting it as a clean committed result.
  Preserve the partial state.
- When permitted, record the failure in the Host's subsequent run and recover inside approved scope; never
  impersonate the worker's missing record.
- A still-denied Host operation stops too.
- Acceptance continues to require the ancestry, boundary, clean-base and check validations above; failed
  preservation weakens none of them.
