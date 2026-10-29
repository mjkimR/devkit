---
name: spec-tasks
description: Decompose the technical plan into independently verifiable tasks in tasks.md, each with its expected file scope (_Boundary:) and the acceptance criteria it serves (_Requirements:).
---

# spec-tasks: Task Breakdown Workflow

Rewrite the skeleton `tasks.md` beside `spec.md` and `plan.md` (stage `specify` of `sdd-spec-feature`, `plan-tasks`
of `sdd-spec-bugfix`), keeping its frontmatter. A bugfix bundle has none yet: create it with `id: TASKS-<slug>`,
`spec: SPEC-<slug>` and `plan: PLAN-<slug>`.

## Rules

- Each task yields one result that can be verified on its own; keep code and its tests in one task.
- `_Boundary:` estimates the paths the task touches; a needed extra path is made and explained in the report. A task
  a `development-worker` builds also names the `docs/` paths its checks require, because its `spec-delegate` write
  scope is strict.
- `_Requirements: AC-01, AC-02_` on a child line indented two spaces links the scenarios the task serves; a task
  covers every `[AC-NN]`.
- Tasks hold implementation and verification only. Review, Living Spec sync and a bugfix's envelopes are stage
  evidence; the reproduction test is a task.
- Write no task counts; progress comes from the checkboxes.

```markdown
- [ ] **Task 1**: Domain types and validation, with unit tests
  - **_Boundary**: `src/app/domain/types.py`, `tests/domain/test_types.py`
  - _Requirements: AC-01_
  - **Verification**: `just test tests/domain/test_types.py`
```

## Completion

- [ ] `devkit rules check <dir>` reports no `RULE-task-coverage` violation, and `<!-- devkit:skeleton -->` is gone.
- [ ] `devkit workflow next --unit <dir>` shows the stage exit met.
