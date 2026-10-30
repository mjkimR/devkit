---
id: PLAN-git-operator-result-readiness
spec: SPEC-git-operator-result-readiness
---

# Technical Plan: `SPEC-git-operator-result-readiness` Separate effect, readiness, permission and next actor in git-operator results

## 1. Constitution & Invariant Review

- `ADR-composed-handoff-commits-its-own-transaction` decides the composed handoff commit; this plan implements it
  and changes no other decision. `ADR-host-cli-lifecycle-authority` holds: the commit is a lifecycle effect of an
  already authorized handoff, adds no approval and grants none.
- `ARCH-08-1-agent-output`: the stopped outcome keeps `[HANDOFF_STOPPED: ...]`, exit `1`, errors last and
  `[NEXT_ACTION: ...]` when there is no next command; the new error is an `AdvisoryError` with a stable code.
- `CAP-WT-task-worktrees` is unchanged: worktree start and setup stay as they are (non-goal 5).
- No architecture `MUST` changes; no new ADR is needed.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `features/delivery/usecases/native_handoff.py` | `HandoffUseCase._execute` commits after handoff and scope registration; the result gains `commit`; a refusal is a stopped result with `SPEC_HANDOFF_COMMIT_REFUSED` and `next_action`. |
| `features/delivery/usecases/native_plan_accept.py` | `accept_and_handoff` records `handoff` whenever the handoff writes landed, `handoff_commit` when the commit landed, carries `commit` and takes the handoff's `next_action`. |
| `features/delivery/cli/proposals.py` | `[HANDOFF: ...]` gains `commit=`; `[ACCEPTED: ...]` gains `commit=` for `accept_and_handoff`; the nested plain-handoff next command is printed only for a completed outcome. |
| `base/errors.py` | `HandoffCommitRefusedError` (`SPEC_HANDOFF_COMMIT_REFUSED`, `INPUT_ERROR`). |
| `bundles/spec/bundle/subagents/git-operator.md` | `checks.worker_input {head, dirty_paths}`, dirty paths as remaining effects, evidence separation, the GOP-06 authority wording. |
| `skills/spec-orchestrate/references/git-operator-{dispatch,operations}.md` | Host compares `checks.worker_input` before a worker; the `handoff` and `prepare-worktree` rows name `commit` and `checks.worker_input`. |
| `skills/spec-next/references/post-handoff.md`, `skills/spec/references/worktree.md.jinja` | Link fixes after the composed handoff are a later Host commit; the sibling base-merge conflict resolution. |
| `docs/capabilities/delivery/`, `docs/usecases/delivery/` | Living Spec reflection at `living-spec-draft` (`CAP-DLV-proposal-planning`, `CAP-DLV-delivery-workflows` §4.6.1, `UC-plan-and-hand-off-a-proposal`). |

No new dependency.

## 3. Component & Interface Design

```python
# native_handoff.py
HANDOFF_SUBJECT = "spec: hand off {slug} to Development"

def _dirty_paths(root: Path) -> list[str]:
    """Every path `git status --porcelain -z --untracked-files=all` reports, in its order."""

def _commit_handoff(root: Path, slug: str, base: str) -> str:
    """Stage the whole delta, commit once and return HEAD read after `git commit` returns.
    Raises HandoffCommitRefusedError (nothing landed) or HandoffStaleError (landed, but not one clean direct
    child of `base`; `.commit` carries the landed HEAD)."""
```

Result of `HandoffUseCase.execute` (added keys): `commit: str | None`; on refusal `next_action: str`, no
`next_command`, and the nested `handoff.next_command` is `None`.

```text
[HANDOFF: PROP-<slug> status=handed_off spec= dir= worktree=dev-<slug> effort= authority= commit=<sha>]
[NEXT_CMD: uv run devkit workflow next --unit <dir>]

[HANDOFF_STOPPED: PROP-<slug> status=needs_recovery spec= dir= worktree=dev-<slug> effort= authority= commit=-]
[NEXT_ACTION: "<fix in the dev-<slug> worktree, then commit there>"]
[ERROR]  (SPEC_HANDOFF_COMMIT_REFUSED) ...   [DETAIL] <commit output>   [TARGET] <dirty paths>
```

`git-operator` result: no new top-level field.

```yaml
checks:
  worker_input: {head: <sha>, dirty_paths: []}   # prepare-worktree and handoff
remaining_effects: [<each dirty path, with what it needs>]
```

## 4. Error Handling & Edge Cases

- **Refused commit** (pre-commit or commit-msg hook, identity, signing): nothing landed; the writes stay staged;
  `status: needs_recovery`, exit `1`, `SPEC_HANDOFF_COMMIT_REFUSED` with the last 20 nonblank output lines as details
  and every dirty path as targets; `next_action` names the worktree path. A rerun refuses the dirty worktree
  (`SPEC_HANDOFF_WORKTREE_CONFLICT`), as before.
- **Uncertain commit** (Git timed out or failed after the commit object landed): HEAD is read again; when it moved,
  the landed commit is verified like a successful one.
- **Landed but not clean** (a hook added a commit or left files): `status: needs_recovery`, `commit` is the landed
  HEAD, `SPEC_HANDOFF_STALE` with the parents or dirty paths; nothing is rolled back.
- **Handoff or setup failure before the commit**: unchanged; `commit` is `null`.
- The plain `devkit spec proposal handoff <slug>` takes another code path (`HandoffProposalUseCase`) and stays
  write-only.

## 5. Verification & Test Plan

| Criterion | Test |
| --- | --- |
| AC-01, AC-02, AC-04 | `packages/devkit-spec/tests/integration/features/delivery/test_handoff_commit.py` (real fixture repository: a metadata-rewriting post-commit hook, a refusing pre-commit hook, the plain handoff) |
| AC-02, AC-03 output | `packages/devkit-spec/tests/integration/features/delivery/test_composed_output.py` (`commit=`, no `[NEXT_CMD]` on refusal) |
| AC-03 | `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py` (refused handoff commit under `accept_and_handoff`; success carries `commit`) |
| AC-02 error | `packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py` (`INPUT_ERROR`, no placeholder in the fix) |
| AC-05, AC-06, AC-07 | `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` |
| AC-08 | `packages/devkit-spec/tests/integration/bundles/spec/test_handoff_language.py` (guidance) and the existing `tests/integration/features/proposals/test_unit_dependencies.py::test_carry_rewrite_namespaced_and_preserve_history` (incoming sibling `depends_on` rewrite) |

Commands: `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected` (with its `mode=full`
fallback), `just rules-check`, `uv run devkit sync --check`; `just smoke` only if packaging or CLI wiring changes
(the CLI output change is in an existing command, not its wiring). The baseline is the base head with the commit
step absent: the existing e2e handoff tests show `status=handed_off` with a dirty worktree there, and the new tests
show a clean single-parent commit on the head.
