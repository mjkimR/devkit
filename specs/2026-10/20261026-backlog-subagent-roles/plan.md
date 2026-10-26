---
id: PLAN-backlog-subagent-roles
spec: SPEC-backlog-subagent-roles
---

# Technical Plan: `SPEC-backlog-subagent-roles` Backlog triage and decomposer subagent roles

## 1. Constitution & Invariant Review

None. The roles follow the read-only support-role pattern of `CAP-DLV-delivery-workflows` section 4.6 and the effort
presets of `ADR-orchestration-workers`; the size gate follows the `needs_decompose` precedent of
`CAP-DLV-proposal-incubation` (a blocking line under `SPEC_PROPOSAL_NOT_ELIGIBLE`, an attach reason under
`WORKTREE_ATTACH_REFUSED`), so no error class, schema or `devkit-agt` contract changes. The `spec-delegate` snapshot
replaces a caller procedure, not a capability MUST; `CAP-DLV-delivery-workflows` describes the post-run comparison and
is updated in reconcile.

## 2. Architecture Overview & Impact

| Component | Change | AC |
| --- | --- | --- |
| `bundle/subagents/triage.md`, `decomposer.md` (new) | Contracts with the `challenger` host matrix; the body cites the procedure by managed path | AC-01, AC-02 |
| `bundle/bundle.toml` | Two `kind = "subagent"` assets and their `presets.core` entries | AC-03 |
| `skills/spec-delegate/SKILL.md`, `references/payload.md` | Role list, payload rows, the tree snapshot before and after a support role | AC-04, AC-05 |
| `playbooks/feedback-hygiene/SKILL.md` | Step 1 delegates `triage` above 5 items on a native host | AC-04 |
| `skills/spec/references/backlog.md.jinja` | Decomposer delegation, Host verification and application, the two `XL` exits, reclassification condition | AC-04, AC-10 |
| `skills/spec/SKILL.md.jinja` | The Host judges `size` and shows it in the plan-intent request; reads the unmet size check as the decompose directive | AC-10 |
| `skills/spec/references/planning.md` | Step 1 returns a size-failing proposal for decomposition | AC-10 |
| `skills/spec-next/references/next-work.md` | `XL` drafts are not eligible; Backlog actions name the decomposer | AC-04, AC-10 |
| `workflows/sdd-proposal.md` | `intent-proposal` exit adds `frontmatter(proposal.md size S\|M\|L\|)`; notes | AC-06, AC-07, AC-10 |
| `templates/proposal.md`, `seed/docs/proposals/README.md`, `features/proposals/usecases/scaffold.py` | The `XL` definition and examples | AC-11 |
| `features/proposals/models/axes.py` | `SIZE`, `SIZES` and `size_blocker(meta)`: the one predicate | AC-08, AC-09 |
| `features/proposals/usecases/accept.py` | `_direct_conditions` adds the size blocking line after `needs_decompose` | AC-08 |
| `features/delivery/usecases/attach.py` | A `plan-` attach of a non-accepted proposal adds the size reason | AC-09 |

No new dependency: `delivery` already imports `proposals.models.axes`.

## 3. Component & Interface Design

```python
SIZE = "size"
SIZES = ("S", "M", "L")

def size_blocker(meta: Mapping[str, object]) -> str | None:
    """``None`` when ``size`` is absent or exactly S, M or L; else the decompose directive naming the value."""
```

- Blocking line (`accept --direct`): `size: <value> (decompose first: split with --decomposed-from or promote to a
  milestone; allowed: S, M, L or absent)`.
- Attach reason (`plan-` only, proposal not `accepted`): `<unit> has size: <value>: Backlog decomposes it before
  Planning (split with --decomposed-from or promote to a milestone; allowed: S, M, L or absent)`. A `dev-` attach and
  the readiness of an accepted proposal never see it.
- Workflow exit: the generic `frontmatter` primitive reads a missing field as `""`, so `S|M|L|` is "absent or S, M,
  L"; the engine prints `detail="size=<value>"` and keeps the gate request closed under `ask` and `auto`.
- Snapshot (`spec-delegate`): before the call and after it,
  `index="$(git rev-parse --git-path devkit-delegate.index)"; GIT_INDEX_FILE="$index" git read-tree HEAD &&
  GIT_INDEX_FILE="$index" git add -A && GIT_INDEX_FILE="$index" git write-tree` prints a tree of the whole working
  tree (tracked edits and untracked, non-ignored files) without touching the real index; with HEAD unchanged,
  `git diff --name-only <before> <after>` lists every path the role wrote, and must be empty except a Scout's agreed
  `materials/` path. The temporary index lives in the worktree's Git directory, which no status lists.

## 4. Error Handling & Edge Cases

- `size: xl`, a number or a typo fail the predicate like `XL`; the value is shown as read.
- A size edited to `XL` after plan-intent shows `intent-proposal` unmet again; a Planning run returns it (step 1).
- A decomposer `needs_input` on an `XL` draft: the Host shows the user a size correction; only the user changes size.
- A role run that changes the snapshot: the Host reports and reverts the paths and discards the result.

## 5. Decisions

- The snapshot applies to every support role (spec assumption 1): one check for clean and dirty trees.
- The size reason on `plan-` is limited to a proposal that is not `accepted`, because integration readiness of a
  `plan-` branch runs the same attach check on the accepted proposal (challenger-02 finding 10).

## 6. Verification & Test Plan

- Unit and integration tests in `packages/devkit-spec/tests/`:
  - `integration/bundles/spec/test_role_contracts.py`: both roles in `ROLES` and `EFFORT_PRESETS`; host matrix,
    `get-context`, cited path, return fields (AC-01, AC-02, AC-04).
  - `integration/bundles/spec/test_workflows.py`: both roles projected for every agent; `validate` ok (AC-03).
  - `integration/bundles/spec/test_backlog_roles_guidance.py` (new): invocation points, Host verification, size
    guidance and definition, and the snapshot command extracted from `spec-delegate` run on a scratch repository
    (AC-04, AC-05, AC-10, AC-11).
  - `integration/features/proposals/test_size_gate.py` (new): `next` and `workflow answer` on `XL`, `xl`, absent
    and `L` drafts under `ask` and `auto`; `accept --direct --check` (AC-06, AC-07, AC-08).
  - `integration/features/delivery/test_attach.py`: `plan-` refused, `dev-` accepted (AC-09).
  - `integration/features/proposals/test_decomposition_fixture.py` (new): the Host procedure (AC-12).
  - `integration/features/proposals/test_proposal_scaffold.py`: the scaffold comment (AC-11).
- `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `uv run devkit rules check`,
  `uv run devkit sync --check`.
- AC-13: a `triage` subagent run over the open feedback from a clean worktree, recorded in the final change report.
