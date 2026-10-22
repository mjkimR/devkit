# spec-specify reference: bugfix characterization and evidence

Read when the bundle is bound to workflow `sdd-spec-bugfix`.

- Characterization is Development work; the expected behavior was agreed at `plan-intent`.
- `characterize` writes `spec.md`, `reproduce` the Red envelope, `fix-verify` the Green envelope.
- The shared contracts (non-goals, AC format, references, clarification rule, self-validation, DoD) are in
  `SKILL.md` §4 and §5.

## Step 1: Characterize the defect (stage `characterize`)

Fill the skeleton's `Defect Characterization` section with the first four items below. Write no feature-style user
story: the bound workflow is the only bugfix record; there is no `kind` field.

- **Current behavior**: the trigger conditions, environment and the observed wrong result, with evidence (log, failing command, test name).
- **Expected behavior and its basis**: the result the existing contract requires, citing the capability, story, ADR
  or test that defines it by ID. If the agreed expected behavior cannot be kept (it is disputed, or a design decision
  rather than a defect), stop and raise it as a problem for the Host.
- **Behavior to preserve**: the call paths, input boundaries and related contracts around the change point that must keep working. Name the existing tests that cover them and the gap that needs a new check.
- **Reproduction conditions**: the exact command, data and environment that reproduce the defect, or, when automation is impossible, the observation conditions and expected results that will serve as alternative evidence.
- **Scope**: what is excluded from this fix (unrelated cleanup, a contract or structure change), written as Non-Goals.
- **Acceptance criteria**: at least one `[AC-NN]` scenario for the resolved behavior and one for each preserved behavior, written so the Green envelope can cite them.

The `characterize` exit also runs `lint-clean` over `spec.md`. `RULE-task-coverage` has nothing to match until
`plan-tasks` writes `plan.md` and `tasks.md` (`spec-plan`, `spec-tasks`).

## Step 2: Reproduce before fixing (stage `reproduce`)

- Default to an automated reproduction: a test that fails on the characterized defect before any fix. Keep it as the
  regression test.
- A compile, environment or test-setup failure unrelated to the defect is not reproduction evidence. A build failure
  that is the defect is.
- Record the Red envelope:

```bash
devkit workflow envelope new --unit <dir> --kind red --stage reproduce \
  --summary "<defect reproduced as characterized>" \
  --check reproduced="PASS <test or command> fails as characterized" \
  --base <ref> --head $(git rev-parse HEAD)
```

- `checks.reproduced` starts with `PASS` only when the failure is the characterized one.
- Otherwise record `--check reproduced="FAIL ..."` and return to `characterize`
  (`devkit workflow return --unit <dir> --to characterize`).
- `--head` is the commit the reproduction ran on. If the reproduction ran on uncommitted work, omit `--head` and say
  so with `--assume`.

## Step 3: Fix and verify (stage `fix-verify`)

- Implement within the task's `_Boundary:`; explain any path beyond it in the report.
- Keep unrelated changes out of the fix.
- Verify resolution under the same reproduction conditions and preservation over the declared paths.
- Record the Green envelope:

```bash
devkit workflow envelope new --unit <dir> --kind green --stage fix-verify \
  --summary "<resolved and preserved>" \
  --check resolved="PASS <same conditions now give the expected result>" \
  --check preserved="PASS <preserved behaviors and the tests run>" \
  --base <ref> --head $(git rev-parse HEAD)
```

- `revision-ancestor(red green)` is available for a stricter project workflow (it needs `--head` on both envelopes);
  the bundled `sdd-spec-bugfix` workflow does not require it.
- `devkit workflow envelope check --unit <dir>` reports a malformed envelope; a malformed file never satisfies a check.

## Step 4: Alternative evidence

For external outages, environment-dependent or non-deterministic defects:

1. Fix the observation conditions and expected results in `spec.md` first (Step 1).
2. Report in the Green envelope whether resolution was confirmed and what uncertainty remains.
3. One non-occurrence is not resolution; say so with `--unverified "<what remains unconfirmed>"`.

## Step 5: Route changes

- If a fix needs a contract change or a design choice outside the agreed intent, raise it as a problem for the Host.
  Development never returns to Planning; a close is the `spec` skill's `references/classification.md`.
- Say which evidence stays valid: state whether the reproduction evidence still holds, and re-examine the AC and
  preserved-behavior lists.

## Output standard

Fill in the skeleton `devkit spec new --workflow sdd-spec-bugfix` and `devkit spec proposal handoff` write. Keep its
section order and frontmatter lines (`id`, `summary`, `workflow`).

```markdown
---
id: SPEC-<defect-slug>
title: <Defect Title>
summary: <one English sentence>     # written by `devkit spec new --summary`; RULE-document-summary requires it
status: planned # planned | in-progress | completed
created: <YYYY-MM-DD>
related_capabilities:
  - CAP-<AREA>-<slug>
related_stories:
  - US-<slug>
workflow: sdd-spec-bugfix            # written by `devkit spec new --workflow sdd-spec-bugfix` or `devkit spec proposal handoff`
---

# [SPEC-<defect-slug>] <Defect Title>

## 1. Problem Statement & Motivation
<What breaks, for whom, and why it matters now.>

## 2. Defect Characterization
- **Current behavior**: <trigger, environment, observed result, evidence>
- **Expected behavior and its basis**: <required result and the contract that defines it, by ID>
- **Behavior to preserve**: <paths, boundaries, existing tests, gaps>
- **Reproduction conditions**: <command, data, environment, or alternative observation conditions>

## 3. Non-Goals
1. **Scope Excluded**: <Item>
   - **Rationale**: <Why, when it helps>
   - **When to Reconsider**: <Trigger, when one exists>

## 4. Acceptance Criteria & Behavioral Contracts
### Scenario 1: [AC-01] <Resolved behavior>
- **Given** <reproduction conditions>
- **When** <the trigger>
- **Then** <expected result>

### Scenario 2: [AC-02] <Preserved behavior>
- **Given** <neighboring path>
- **When** <its normal input>
- **Then** <unchanged result>
```
