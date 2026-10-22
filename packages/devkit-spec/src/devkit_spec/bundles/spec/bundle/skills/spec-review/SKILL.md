---
name: spec-review
description: Verify the git diff, acceptance criteria and test results before declaring a task or feature complete; detects unexplained scope drift, phantom completion and unstated requirement drift.
---

# spec-review: Pre-Completion Verification Workflow

Use this skill when all tasks in `tasks.md` are checked (`tasks-all-checked` opens the `review-refine` stage), or
before submitting a pull request.

## 1. Prerequisites & Inputs

- Feature files: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/spec.md`, `plan.md`, `tasks.md`.
- Implementation committed on the task branch (an intermediate commit), so the envelope's `--head` names the reviewed
  content.
- If the review covers uncommitted changes, say so in the envelope's `assumptions`; the cumulative check after the
  commit covers it.

## 2. Verification Workflow & Converge Invariants

- Never rewrite, delete or weaken original tests or acceptance criteria to force a failing check to pass. Record a
  technical limitation as a review finding.
- If a limitation needs a contract change outside the agreed intent, report it as a problem for the Host.
- Verify mechanically (`git diff`, build, tests, linters), not by extra LLM re-evaluation.

### Step 1: Mechanical Git Diff Inspection

- Run `git status -s` and `git diff` against the base branch.
- Check for:
  - **Scope drift**: changes outside the declared `_Boundary:` in `tasks.md` without a stated reason.
    - `_Boundary:` is expected scope; an explained extension is not a finding.
    - A delegated write scope is strict: any change outside it is a finding.
    - Implemented non-goals or unrequested features are always findings.
  - **Stray files**: leftover debug scripts, `.DS_Store`, temporary scratch files.
  - **Dead code / debug prints**: `print`/`console.log` debugging, commented-out code blocks, mock bypass flags.

### Step 2: Contract & Acceptance Criteria Validation

- Compare actual code and test outputs against every `[AC-NN]` Given/When/Then scenario in `spec.md`:
  - happy path, edge cases and boundary conditions are tested and passing;
  - error payloads and status codes match the contract.
- Non-goals: no excluded scope implemented, even partially.
- Bugfix bundles: the Red and Green envelopes exist and the regression test is kept
  (`devkit workflow envelope check --unit <dir>`).

### Step 3: Run Deterministic Verification Gates

- Follow the repository's test policy on the reviewed content (e.g., `just test-affected`); preserve selector
  fallbacks and any named frontend checks.
- Run the full suite locally only when that policy or the selector requires it.
- As a delegated reviewer, reuse valid results and rerun only missing or stale checks.
- Run the linters and formatters (e.g., `just lint`) and the spec rules: `devkit rules check --staged` for staged
  changes, `devkit rules check --ci --base <ref>` for a committed branch.
- Each check passes with exit code 0 and zero warnings and errors.

### Step 4: Capture Unstated Requirements & Drift

- Record each new requirement, API change or unexpected constraint the implementation revealed as a finding.
- If it changes the agreed contract, it is a problem for the Host; if it stays inside the contract, fix or waive it in
  the reverify round.

### Delegated execution (Reviewer role)

- Who runs this skill, by `activity-effort`:
  - medium and high: the `code-reviewer` role, in an isolated context (through `spec-delegate`; `[DELEGATE]` for this
    stage). Its first medium review is mandatory regardless of change size.
  - low: the Developer.
- Both produce the same envelope. The role's inputs, write boundaries and stale-head handling are in its contract
  (`.devkit/managed/spec/subagents/code-reviewer.md`).
- Every finding carries `evidence` (path:line), a `failure_condition` and a `severity` of `P1`, `P2` or `P3` at every
  effort (the `spec` skill's `references/review-loop.md` section 3 defines them; the implementer records the
  reviewer's level unchanged).
- Zero findings is a valid PASS; do not manufacture defects.
- After fixes, re-verify only the changed part:
  - At medium the implementer verifies fixes and later changes and decides whether to call the code-reviewer again
    (the `spec` skill's `references/effort.md`), recording who checked what in `reverify`.
  - At high the review runs in the bounded rounds of `references/review-loop.md`; each summary starts with
    `round <N>;`.

### Feedback after the review

If an external runner pauses after `review-refine` for user feedback:

- Feedback that changes implementation returns to build/reverify for the affected part; a direction change is a close
  (the `spec` skill).
- The pause replaces no stage, check or gate: Living Spec reflection still completes before `dev-integration`.

## 3. Review Report

The review envelope is the report, for a direct run and a delegated Reviewer run alike. For a spec Unit (`spec` or
`proposal` depth), record the findings as found (all open):

```bash
devkit workflow envelope review --unit <dir> --stage review-refine \
  --status completed --summary "<scenarios confirmed and by what>" \
  --check tests="PASS <command and count>" --check lint="PASS devkit rules check --staged" \
  --base <ref> --head $(git rev-parse HEAD) --findings-file - <<'EOF'
- issue: "<what was found>"
  evidence: "path:line"
  failure_condition: "<under which input or state it fails>"
  suggested_action: "<recommended next step>"
  severity: "P2"
EOF
```

- The command writes the next `envelopes/review-NN.yaml`. For a pass, omit `--findings-file`.
- After fixes, close the round with
  `devkit workflow envelope reverify --unit <dir> --stage review-refine --from latest --resolve <N> --waive <N>=<reason>`
  (`--resolve all` when every finding is fixed). It writes `reverify-NN.yaml` for `envelope-review-passed`.
- Record fixes in the reverify envelope, not inside the review file itself.
- A `session`-depth task states the same content in the final response or PR body and writes no envelope; a reviewer
  subagent returns it as a message.

## 4. Completion

- [ ] The verdict is stated to the user: PASS is `status: completed` with no open findings; REVISE is
  `status: completed` with findings; `needs_input` when verification is blocked.
- [ ] For a spec Unit with a PASS, `devkit workflow next --unit <dir>` no longer lists `envelope-review-passed` as
  unmet.
