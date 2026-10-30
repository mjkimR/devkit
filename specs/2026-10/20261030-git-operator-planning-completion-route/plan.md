---
id: PLAN-git-operator-planning-completion-route
spec: SPEC-git-operator-planning-completion-route
---

# Technical Plan: `SPEC-git-operator-planning-completion-route` Planning completion and acceptance execution route for git-operator

## 1. Constitution & Invariant Review

None. The change adds no operator effect, so `ADR-reusable-lifecycle-resource-manager` and the git-operator contract
stay as they are; the composed acceptance's behavior (`ADR-proposal-acceptance`, `ADR-host-cli-lifecycle-authority`,
`ADR-moved-target-merge`) is unchanged; the workflow engine in `packages/devkit/` is not touched. The reworded
refusal stays a Click usage error with exit `2`, as `ARCH-08-1-agent-output` allows for argument misuse.

## 2. Architecture Overview & Impact

Target area: `capabilities/delivery/`. Three independent edits, no new dependency:

- **Acceptance route (AC-01, AC-02, AC-03, AC-07)**: spec bundle guidance only.
  - `skills/spec-orchestrate/references/git-operator-operations.md`: one line after the table: Planning acceptance is
    no operator job; the Host runs the composed command, which already integrates and cleans up.
  - `skills/spec-orchestrate/references/git-operator-dispatch.md`: the same in one line beside "Normal integration
    already includes cleanup".
  - `skills/spec-orchestrate/SKILL.md.jinja` loop step 4: the Host runs the composed command itself after the review.
  - `skills/spec-review-proposal/SKILL.md.jinja` local step 4: name `--by user|policy`, and replace "After a partial
    result, inspect ..." with the preparation/post-commit refusal rule.
- **Return stage (AC-04, AC-05)**: `skills/spec/references/worker-records.md` §1 (`--stage` bullet) and
  `skills/spec/references/planning.md` step 6 name `direction-handoff` for the `[STAGE: - complete=yes]` while
  `reviewing` case. No engine change: the existing hold of an open question at `direction-handoff` already makes the
  composed acceptance refuse in its preview (`_Acceptance.preview`, `hold:` conditions).
- **Dry run (AC-06)**: `features/delivery/cli/proposals.py` `accept_cmd`: split the composed-form refusal into
  `--direct` (unchanged meaning) and `--check` (new text). The text uses `devkit_command` for the project's invocation
  form and `proposal_unit(slug)` for the unit directory.

After the bundle sources change, `devkit sync` refreshes the projection; its tracked outputs are committed as sync
outputs.

## 3. Component & Interface Design

The `--check` usage error (normative wording to the extent AC-06 pins it):

```text
Error: composed acceptance has no --check: its readiness refusals in preparation come before the first write, and a
later failure returns needs_recovery with completed_steps; for read-only material run `uv run devkit spec proposal
report <slug>` and `uv run devkit workflow envelope check --unit docs/proposals/PROP-<slug>`
```

The `--direct` usage error: `composed acceptance cannot use --direct`. `--direct` is checked first.

## 5. Error Handling & Edge Cases

- Both `--direct` and `--check` with `--mode`: the `--direct` error.
- An invalid slug with `--mode --check`: the usage error fires before the slug is validated, as today; the named
  commands then refuse the slug themselves.

## 6. Verification & Test Plan

- AC-01, AC-02, AC-04: wording tests in `packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py`
  (operating references, skills) and a new `test_planning_return_stage_guidance.py` beside it (worker records,
  planning).
- AC-05: a behavior test in `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_cli.py` on the
  existing `pending` fixture under `plan-accept = "auto"`.
- AC-06: a CLI test in the same file.
- AC-03, AC-07: the existing tests, unchanged.
- Commands: `just lint-check devkit-spec`, `just check devkit-spec`, `just test-affected` (its `mode=full` fallback),
  `just rules-check`, `uv run devkit sync --check`.
