---
name: spec-tasks
description: Decompose the technical plan into independently verifiable tasks in tasks.md, each with its expected file scope (_Boundary:) and the acceptance criteria it serves (_Requirements:).
---

# spec-tasks: Task Breakdown Workflow

Use this skill once `spec.md` and `plan.md` exist, to write a short list of tasks that each produce a verifiable result:

- the `specify` stage of workflow `sdd-spec-feature`;
- the `plan-tasks` stage of workflow `sdd-spec-bugfix`.

## 1. Prerequisites & Inputs

- `spec.md` and `plan.md` in `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`, and the skeleton `tasks.md` beside them (written by
  `devkit spec new` or `devkit spec proposal handoff`).
- If the bundle is a bugfix from `devkit spec new` (no `tasks.md`): write `tasks.md` with the frontmatter
  `id: TASKS-<slug>`, `spec: SPEC-<slug>` and `plan: PLAN-<slug>`, then the tasks.

## 2. Work Breakdown Principles

- **One verifiable result per task**: a task can be implemented and checked on its own.
  - Keep the code and its tests in the same task when they change together.
  - Split when one part can be verified without the other.
- **Expected scope (`_Boundary:`)**: every task names the paths it is expected to touch.
  - A long list may wrap onto lines indented deeper than the label line, its entries still separated by commas. A
    blank line, a list item or any line not indented deeper ends it.
  - It is a scope estimate, not a lock: if a change turns out to need another path, make it and explain it in the
    report.
  - If a `development-worker` builds the task, also name the `docs/` paths its checks require (such as a code-table
    row), because the `spec-delegate` write scope is strict and the worker writes no `docs/` path outside the
    boundaries and the reconcile targets.
- **Acceptance links (`_Requirements:`)** (`RULE-task-coverage`):
  - Every task links the scenarios it serves on a direct child line indented two spaces,
    `- _Requirements: AC-01, AC-02_`.
  - Every `[AC-NN]` in `spec.md` is covered by at least one task; a task cites only IDs the spec defines.
  - A `_Requirements:_` line in a table, prose or under a non-task item covers nothing.
- **Optional markers**: a `**Verification**` command when the check is not obvious from the boundary; phase headings
  for a long list.

Do not write task counts: progress is computed from the checkboxes (`devkit spec list spec` shows
`tasks=<checked>/<total>`; `devkit workflow next --unit <dir>` evaluates `tasks-all-checked`).

Tasks hold implementation and verification work only:

- Review (`spec-review`), Living Spec sync (`spec-sync`) and a bugfix's Red and Green envelopes are stage evidence,
  not tasks (`tasks-all-checked` opens `review-refine`).
- The reproduction test itself is a task.

## 3. Tasks Output Standard

Read the skeleton `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/tasks.md`, then rewrite it, keeping its `id`, `spec` and `plan`
frontmatter:

```markdown
---
id: TASKS-<feature-slug>
spec: SPEC-<feature-slug>
plan: PLAN-<feature-slug>
---

# Task Breakdown: `SPEC-<feature-slug>` <Feature Title>

- [ ] **Task 1**: Domain types and validation, with unit tests
  - **_Boundary**: `src/app/domain/types.py`, `tests/domain/test_types.py`
  - _Requirements: AC-01_
- [ ] **Task 2**: CLI command wiring and its error output
  - **_Boundary**: `src/app/cli/run.py`, `tests/cli/test_run.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test tests/cli/test_run.py`
```

## 4. Definition of Done

- [ ] Every acceptance scenario is covered: `devkit rules check <dir>` reports no `RULE-task-coverage` violation.
- [ ] In a registered task worktree, `devkit spec scope update --spec <dir>` gave the registry the task boundaries
  (on `SPEC_SCOPE_TOKEN_MISSING` the worktree is not registered: skip it). `[SCOPE_ACK]` overlaps inform the
  orchestrator; they are not a gate.
- [ ] The skeleton marker line `<!-- devkit:skeleton -->` is removed from `tasks.md`, and
  `devkit workflow next --unit <dir>` shows the exit of `specify` (or `plan-tasks`) met; otherwise it names what is
  still unmet.
