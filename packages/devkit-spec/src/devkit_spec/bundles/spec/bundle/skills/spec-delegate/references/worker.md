# Worker results

Read this when a worker returns. Record formats, questions, answers, problems, resolutions and permission failures: the `spec` skill's `references/worker-records.md`. Never write a worker's records for it.

## The last accepted head

A worker's range starts at the unit's last accepted head:

- Not blocked: the worktree's HEAD when you spawn the worker, after your own commits.
- Blocked: the head its blocked range started from, never the current HEAD, so the rejected commits stay in the range.
- Unaccountable after context loss: the branch's merge base with the base branch.

## Validate

Run `devkit spec worker inspect --format json` in the worktree. Override a derived input that differs from your record with `--base`, `--head`, `--scope`/`--scope-file`, `--unit` or `--base-checkout`; an override replaces the input, never unions with it. The accepted-turn `base`, ancestry and `changed_paths` remain the write audit.

- If a Planning turn creates a follow-up draft, verify that it is permitted by the payload and role contract before including it in the complete inspection scope: `devkit spec worker inspect --format json --scope <proposal dir> --scope <follow-up proposal dir>`. Repeat the unit directory because the override replaces derived scope.
- Cumulative rules use the independent `rules_base`, derived from the recorded base-branch merge base; `--rules-base` overrides only that input. Inspect its value and source (a manual `audit-base-fallback` when no base branch is recorded).
- Absent optional reconcile adds no scope; malformed present records remain not-run. A not-run check is not a pass.
- Pass `base`, `head` and `changed_paths` to read-only reviewers, and retain `rules_base` with the rules evidence.

The range from `<accepted>` to the returned final HEAD `<returned>` (the commit that holds the `worker` envelope) passes when:

- `<accepted>` and the envelope's `diff_scope.head` are ancestors of `<returned>`, and the worktree's HEAD is `<returned>`.
- `<returned>` adds this turn's `worker` envelope, absent at `<accepted>`: a turn committed in the base checkout fails here, since inspection derives its head from the branch's latest envelope.
- Every path of `git -C <worktree> diff --name-only <accepted> <returned>` is in declared scope, an admitted recorded adjacent extension or the independent sync-output class, the worker's records included; envelopes you committed since `<accepted>` are exempt only while unchanged since your commit.
- For each recorded adjacent extension, compare `(scope extension: <reason>)`, its owning positive checklist task
  ordinal and AC with `scope_extensions` in committed worker records. Prior-turn records support retained
  annotations; the highest worker sequence wins repeated paths. Historical records alone add no scope: the
  annotation must still exist. Confirm the annotation/reason accompanies the first source commit and that review
  covered necessity, documented same-feature ownership/test mirror or the exact affected existing Living Spec
  document, explicit denies, protected classes and test strength. Missing evidence is P2, denied/non-adjacent/
  out-of-goal writes are P1 and block the range. Changed metadata after review needs re-verification. New unannotated
  boundaries are checked against the payload/task diff; no sealed boundary journal is required.
- `checks.scope_extensions` must pass with the additive top-level list. It checks structural annotation/record/task/
  AC agreement and recognizable protected trees, not semantic adjacency or custom protected paths. Inspect remains
  optional locally and in cloud; no Hub invocation is promised. Validate evidence before an explicit scope override,
  then include admitted extensions in the complete scope: `--scope`/`--scope-file` still replace it, never union it.
- The worktree is clean.
- The unit's checks pass on `<returned>`, confirmed by CI or a rerun; for a run that stopped on a problem, validate its paths only.
- Each `(sync output)` entry `tasks.md` gained between `<accepted>` and `<returned>` passes only when you confirm all of these (`devkit spec worker inspect` derives its scope from `_Boundary:` at `<returned>`, so its scope pass is no evidence for that entry):
  - the worker's `sync_start` check is `PASS exit=0`;
  - `devkit sync --check` exits `0` on `<returned>`;
  - the path is under `seeded` or `files` in the returned head's `.devkit/installation.json`, is `.devkit/installation.json` itself, or is the file that holds the managed guidance block (`AGENTS.md`; the receipt records that block only as a hash).

Base advances (yours, another session's or an unknown author's) never block the range, and validation needs no base merge first; inspection's `base_checkout` is information you compare with nothing. A dirty base checkout still stops handoff and integration. Accepted residual: a worker commit made on the base branch through a wrong cwd, with the rest of its turn on its branch, passes every condition.

## Accept or block

- **Accept**: the next spawn starts from the accepted HEAD. Scope publication and ACKs are not worker duties.
- **Failed without a committed envelope** (dirty or uncommitted, e.g. a denied record or commit): block it. Inspect the actual HEAD and status against the scope, preserve the partial state, never commit its dirty paths as your own, and record the failure in your own envelope when permitted.
- **Block**:
  1. Record the violation as your own `worker` envelope at the stage `devkit workflow next --unit <dir>` names, one finding per violation:
     ```bash
     devkit workflow envelope worker --unit <dir> --stage <stage> --effort <activity-effort> --problem "<the committed range breaks its boundary or checks>" --recovery "<what must change>" --findings-file - --base <accepted> --head <returned>
     ```
  2. Commit it first. Never reset or amend; keep a pull request open and blocked.
  3. Fix it yourself or send a new worker the recovery request (a revert commit for an out-of-scope change); whoever fixes it commits the `resolution`.
  4. Validate again from the same last accepted head.

## Questions

Restate the questions for the user in one round (what each decides, why now, where each option leads), then hand the rewritten answers to a new worker, each naming who decided it (`by: user`, `host` or `policy`, the `spec` skill's `references/worker-records.md` §2).
