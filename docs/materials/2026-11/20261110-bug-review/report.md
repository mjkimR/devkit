# Bug review: changed modules since the 2026-10-27 review

Read-only correctness review run before the next `maintenance/review-refactor` pass. Nothing was changed in the
repository; fixes are decided separately.

## Intake

- **Repository**: devkit monorepo, `main` at `1a871c7a` (clean).
- **Baseline**: `013d66ad` (2026-10-27). The previous module-wide bug review landed as `dev-bug-polish`
  (`badb9191`) and the review-refactor code pass (`docs/materials/2026-10/20261027-review-refactor-code-pass/`)
  started from `013d66ad`; both covered the code up to that commit.
- **Criteria**: correctness bugs and violations of the `AGENTS.md` contracts (layering, import boundaries, agent
  output contract, capability contracts). Duplication, dead code and style are left to review-refactor.
- **Tiers**:
  - Full read, changes first: devkit-agt (`workflow`; `rules`; `worktree`, `integration`, `gate`, `generated`;
    `maintenance_history`, `isolated_execution`, `compact` and non-feature modules), devkit-spec, devkit-docs,
    devkit-dist, devkit-adaptive.
  - Diff only (`013d66ad..HEAD`): devkit-catalog (Python), devkit-viewer (Python), devkit-core, devkit-mcp,
    devkit-dev.
  - Excluded (no change since the baseline): devkit-advisory, devkit-cli, devkit-starter.
- **Method**: eight read-only reviewers, one per scope above. Each listed what it read. Medium and high findings
  were rechecked against the code by the Host; findings marked PLAUSIBLE are unreproduced.

## Summary

| Severity | Count | Keys |
| --- | --- | --- |
| High | 1 | AN-01 |
| Medium | 9 | GT-1, GT-2, SP-1, SM-1, RU-1, DC-1, DC-2, DS-1, DS-2 |
| Low | 27 | the rest |

## Findings

Confidence: C = confirmed (reproduced or unambiguous from code), P = plausible.

### High

| Key | Location | Defect | Conf. | Fix direction |
| --- | --- | --- | --- | --- |
| AN-01 | `devkit_agt/features/isolated_execution/repositories/runtime.py:34-58` | `ps ... lstart=` is parsed positionally as five tokens; under `ko_KR`/`ja_JP` locales `lstart` has four, so every run turns `unknown` within a second and `cancel`/`clean` refuse, leaving checkouts and processes unmanaged. | C (reproduced with `LC_ALL=ko_KR.UTF-8`) | Run `ps` with `LC_ALL=C`; avoid positional parsing of `lstart`. |

### Medium

| Key | Location | Defect | Conf. | Fix direction |
| --- | --- | --- | --- | --- |
| GT-1 | `devkit_agt/features/integration/cli.py:141-142`, `usecases/service.py:564-570`, `usecases/pull_request.py:524` | A step left `unknown` after a possibly-applied mutation (ff timeout, unconfirmed push) still yields `blocked` and exit 2, which the contract reserves for "nothing happened". | C | Count `unknown` (and post-ff landing mismatch) as a partial effect: `partial`, exit 1. |
| GT-2 | `devkit_agt/features/integration/usecases/pull_request.py:504-517` | The PR route raises `INTEGRATION_CLEANUP_INCOMPLETE` as an error (exit 1), stops later extensions and crashes on a malformed result; the local route and contract make it a warning. | C | Reuse the local route's cleanup loop. |
| SP-1 | `devkit_spec/features/delivery/cli/proposals.py:245,310`; `proposals/usecases/scaffold.py` | Under `adaptive-dev`, `devkit spec proposal new` and `padr` create files; `require_sdd` runs only in the `create_proposal()` wrapper the CLI bypasses. | C | Guard both use cases; add a CLI-level test. |
| SM-1 | `devkit_adaptive/features/assignment/services/verification.py:117-130` | One unreadable assignment worktree (unborn HEAD, missing base) makes `assignment list` fail with exit 2; the contract says it exits 0. | C (reproduced) | Catch per assignment and report a degraded observation. |
| RU-1 | `devkit_agt/features/rules/repositories/workspace/cache.py:395,429-431`; `services/targets.py:55-60` | On a case-insensitive file system, `rules check Docs` for `docs/` checks nothing and reports OK (exit 0). Predates the baseline. | C (reproduced) | Normalize a directory target to its on-disk spelling, or refuse an empty expansion. |
| DC-1 | `devkit_docs/features/documents/repositories/memo.py:52-53` | The document parse memo fingerprint omits the shared Markdown scanner in `devkit_agt`, so a scanner change keeps stale references. Regression from the split. | C | Add the scanner module to `FINGERPRINT_MODULES`. |
| DC-2 | `devkit_docs/features/documents/models/supersession.py:46-50` | An HTML comment line after a partial-supersession statement is appended to the statement, making `RULE-decision-supersession` (error) fail on matching texts. | C | Stop the continuation at comment lines or use scanner prose lines only. |
| DS-1 | `devkit_dist/features/distribution/repositories/snapshots.py:25`; `services/snapshots/source.py:145` | `bundle snapshot`/`refresh` reject a source reached through a symlinked ancestor (`/tmp`, `/var` on macOS) because the path is read before it is resolved. | C (reproduced) | Resolve source and absolute destination first; reject only symlinks inside them. |
| DS-2 | `devkit_dist/features/distribution/repositories/projection_git.py:27-29,95-102` | In a devkit root nested in a Git repository, `PROJECTION_NOT_IGNORED` advises patterns that do not clear the warning. | C (reproduced) | Prefix with the Git show-prefix, or name `<devkit root>/.gitignore`. |

### Low

| Key | Location | Defect | Conf. |
| --- | --- | --- | --- |
| WF-01 | `devkit_agt/features/workflow/repositories/envelope_commit.py:518,649` | `git commit` under the fixed 60 s Git timeout; slow hooks or signing make every attempt `ENVELOPE_COMMIT_UNCERTAIN`. | P |
| WF-02 | `workflow/services/envelope/commit.py:92` | Commit subject built from the parsed sequence, not the file stem (`worker-007.yaml` → `worker-07`). | C |
| WF-03 | `workflow/cli/envelope.py:181-184` | `[ENVELOPE_COMMIT: ...]` inserts `unit` without `field_value`. | C |
| WF-04 | `workflow/usecases/commit_envelope.py:38,63,87-90` | No `--anchor`; a multi-anchor unit can never commit, and inner codes are rewrapped as `ENVELOPE_COMMIT_INVALID`. Latent. | C |
| RU-2 | `rules/services/targets.py:32,75-86` | Unicode normalization applied to the whole absolute path, workspace root included. | P |
| RU-3 | `rules/cli/commands.py:116` | Plugin omission code and rule ID printed raw into the sentinel; code not validated as UPPER_SNAKE. | P |
| RU-4 | `rules/services/evaluator.py:127-130,206-223` | A finding whose rule becomes omitted on recheck is reported `fixed`. | P |
| GT-3 | `integration/usecases/pull_request.py:499` | PR route reports `worktree_remove: completed` when no worktree existed. | C |
| GT-4 | `integration/usecases/service.py:591-604` | A refused integrate still reports the prospective build's seeded artifacts and regen warning. | C |
| GT-5 | `worktree/repositories/pull_request.py:105,115,434`; `integration/models/errors.py` | Recovery `[FIX]` texts give `integrate` commands that are refused under `ask` without a digest. | C |
| AN-02 | `isolated_execution/repositories/runtime.py:263-301` | An unexecutable native command is recorded as `setup_failed`. | C |
| AN-03 | `isolated_execution/repositories/runs.py:72-83,148-155` | `exec start` reports `unknown` (exit 2) if `state.json` is late on a loaded host, inviting duplicate runs. | P |
| AN-04 | `isolated_execution/services/lifecycle.py:24-26,67-70` | Cleanup refuses when the old supervisor PID was reused, without comparing process identity. | C |
| AN-05 | `maintenance_history/services/publication.py:129-139` | Contents API read fails for files over 1 MB; a lost-response retry marks a published run `failed`. | P |
| AN-06 | `isolated_execution/cli.py:49-53` | `EXECUTION_CLEANUP` sentinel missing from `CAP-HARN-isolated-execution` §4 and the exec reference. | C |
| SP-2 | `devkit_spec/features/proposals/usecases/accept.py:306-315` | `accept --check` can never report `eligible=no` with exit 1, contrary to `CAP-DLV-proposal-lifecycle`. | C |
| SP-3 | `devkit_spec/features/policy/services/config.py:166-168` | A legacy `[[tool.spec.namespaces]]` fails with a generic error that does not name `[[tool.docs.namespaces]]`. | C |
| SP-4 | `devkit_spec/features/proposals/usecases/scaffold.py:606-625` | Proposal creation has no roll-back; a partial write blocks reruns with `ProposalExistsError`. | P |
| DC-3 | `devkit_docs/features/documents/models/supersession.py:31,45` | `str.splitlines()` vs the scanner's `\n` split misaligns lines after U+2028 and similar. | C |
| DS-3 | `devkit_dist/.../services/bundles/context_documents.py:226-233` | `get-context` providers raising `SystemExit`, or failing discovery, abort the command. | C |
| DS-4 | `devkit_dist/.../repositories/snapshots.py:41` | A Finder `.DS_Store` in a snapshot blocks refresh as authored changes. | C |
| DS-5 | `devkit_dist/.../usecases/playbook_search.py:157` | Explicit dense/hybrid search skips `SEARCH_EXTRA_MISSING` when no playbook is synchronized. | P |
| SM-2 | `devkit_adaptive/.../services/operations.py:55-59` | `return --final <rev>` resolves in the caller's repository, `--base` in the assignment worktree. Contract silent; needs a decision. | C (behaviour) |
| SM-3 | `devkit_adaptive/.../repositories/ledger.py:31-46` | A malformed ledger event crashes with `UNEXPECTED_ERROR` instead of `ADAPTIVE_LEDGER_UNREADABLE`. | C |
| SM-4 | `devkit_adaptive/.../services/validation.py:38`; `repositories/governing.py:33` | A symlink loop in a path argument gives `UNEXPECTED_ERROR` instead of an input error. | C |
| SM-5 | `devkit_adaptive/.../repositories/ledger.py:52-59` | Any `OSError` in the locked body is reported as `ADAPTIVE_LEDGER_UNWRITABLE`. | P |
| SM-6 | `devkit_viewer/features/browse/repositories/worktree.py:129,134` | Frontmatter delimiters with trailing Unicode whitespace are read differently from core. | C |

## Checked without findings

- Import boundaries and layering in every scope; no library `print`.
- The shared Markdown scanner rewrite: old and new `count_tasks`, `extract_links` and `fenced_lines` agree on all
  1740 tracked Markdown files.
- devkit-spec ↔ devkit-docs split: all devkit-spec modules import; entry points are consistent.
- devkit-dist without devkit-agt: `scripts/dist_only.sh` passed 1350 tests.
- Test runs by reviewers: devkit-docs 679 passed; workflow unit and integration 557 passed.

## Coverage gaps

- devkit-agt `workflow/usecases/evaluate.py` and `handoff.py` were reviewed through the diff only; the previous
  review also checked `evaluate.py` only by name and pattern.
- devkit-agt `worktree/usecases/lifecycle.py` unchanged parts and the GitHub adapter in
  `worktree/repositories/pull_request.py`; merge-tree handling of file/directory or rename conflicts on generated
  paths (probe not run).
- devkit-agt `rules`: `repositories/discovery.py`, workspace `catalog`/`facts`/`relocation`, built-in
  `secret_leak` and `clean_artifacts`.
- devkit-spec `scope/usecases/{flow,query,history}.py`, `scope/cli`, `proposals/usecases/{backlog,prune}.py`,
  `worker/usecases/summary.py`.
- devkit-docs unchanged bodies of `index.py`, `search.py` ranking and `ux.py` flow-graph code.
- devkit-dist `features/search/services/*`.
- Bundle Markdown, rule test files and the viewer frontend were out of scope.
