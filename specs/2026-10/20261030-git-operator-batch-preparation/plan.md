---
id: PLAN-git-operator-batch-preparation
spec: SPEC-git-operator-batch-preparation
---

# Technical Plan: `SPEC-git-operator-batch-preparation` Bounded batch preparation for git-operator

## 1. Constitution & Invariant Review

None. The change adds a list form to an agent-facing role contract and its Host guidance; no architecture `MUST`,
ADR or CLI contract changes. `ADR-reusable-lifecycle-resource-manager` (no daemon, no global lock, serialized jobs in
one conversation) holds: items run serially in one operator conversation. `CAP-WT-task-worktrees` stays unchanged
because each item runs the existing `devkit worktree start`. `CAP-DLV-delivery-workflows` §4.6.1 gains the list
rules in the `living-spec-draft` stage.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md` | Input: the preparation list (AC-01). Procedure: serial run, base-ref check, stop rule, no setup/sync repair (AC-02, AC-04). Authority and boundaries: one sentence that a list's authority covers only its listed items (AC-05). Return: the list return shape and status rule (AC-03). |
| `.../skills/spec-orchestrate/references/git-operator-dispatch.md` | One paragraph on dispatching a preparation list and one on accepting and retrying it (AC-04). |
| `.../skills/spec-orchestrate/references/git-operator-operations.md` | The `prepare-worktree` row names the list run and stop (AC-06). |
| `.../skills/spec-delegate/references/payload.md` | The `git-operator` row: a preparation list repeats every field per item (AC-06). |
| `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` | Contract-text tests for AC-01..AC-06, tagged with the AC IDs. |
| `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md` §4.6.1 | EARS rules for the list (Living Spec reflection, `spec-sync`). |

No new dependency. `devkit sync` rewrites the projected copies under `.devkit/managed/` and the recorded digests in
`.devkit/installation.json`; the worker commits them as sync outputs.

## 3. Component & Interface Design

The list return is a non-normative example in the role contract; its keys are normative:

```yaml
status: completed | needs_input | failed
summary: concise actual result
items: []          # one single-job return per attempted item, in listed order, unchanged
not_attempted: []  # {identity, intended_effects, cli_result: {status: null, exit_code: null, effects: []}}
```

- `items[i]` is exactly the single-job return (status, summary, identity, observed_refs, completed_effects,
  remaining_effects, checks.worker_input, blocker_codes, cli_result, unverified_areas). No field is added to it.
- List status: `completed` only when every listed item is `completed`; otherwise `needs_input` when any attempted
  item is `needs_input`; otherwise `failed`.

The stop rule is evaluated by the operator before each item (base HEAD equals the dispatched base ref) and after it
(role status `completed`). The Host-side retry dispatches a new list; it never edits the previous one.

## 4. Error Handling & Edge Cases

- **Moved base ref before an item**: that item is attempted with `needs_input`, the changed-ref blocker and the null
  CLI result; later items are not attempted (spec assumption 3).
- **Refused or unavailable host approval**: that item carries a host-permission blocker code and the null CLI
  result; the operator never reroutes; later items are not attempted.
- **Zero-exit setup or sync warning** (`WORKTREE_SETUP_FAILED`, `WORKTREE_SYNC_FAILED`): the worktree is kept, the
  item is `needs_input` with the warning's remainder; the operator runs no `[FIX]`, sync or registration repair.
- **Zero-exit notice** (`WORKTREE_REMOTE_UNCHECKED`, a registration advisory): reported on its item; the item is
  `completed` only when its `checks.worker_input` and effects say so.
- **Repository-wide cause** (a broken `post-checkout` hook, an offline setup command): the stop rule bounds the cost
  to one item, because the code does not show whether later items fail too.

## 5. Verification & Test Plan

| Scenario | Check |
| --- | --- |
| AC-01..AC-06 | `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` (new tests tagged with the AC IDs; the GOP-06 regression test stays unchanged) |
| AC-07 | `git -C <worktree> diff --stat 133819ed -- packages/devkit/` is empty; `just test devkit packages/devkit/tests/integration/features/worktree packages/devkit/tests/e2e/features/worktree` passes unchanged |
| Projection and sync | `uv run devkit sync --check` exit 0 after `uv run devkit sync` |
| Repository checks | `just lint-check devkit-spec`, `just check devkit-spec`, `just rules-check`, `just test-affected` (with its `mode=full` fallback) |

`test_agent_output_contract.py::test_fixes_carry_no_placeholder` fails on the base before this change (owned by a
sibling unit); it is reported, not fixed. The live stop and retry behavior of a real partial list is not exercised by
these checks and stays unverified (spec non-goal 5).
