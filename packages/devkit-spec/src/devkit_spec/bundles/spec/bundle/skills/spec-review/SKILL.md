---
name: spec-review
description: Verify the git diff, acceptance criteria and test results before declaring a task or feature complete; detects unexplained scope drift, phantom completion and unstated requirement drift.
---

# spec-review: Pre-Completion Verification Workflow

Use this skill when all tasks in `tasks.md` are checked (`tasks-all-checked` opens the `review-refine` stage), or before submitting a pull request.

---

## 1. Prerequisites & Inputs

- Feature files: `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/spec.md`, `plan.md`, `tasks.md`.
- Implementation committed on the task branch (an intermediate commit), so the envelope's `--head` names the reviewed content. A review of uncommitted changes says so in the envelope's `assumptions`; the cumulative check after the commit covers it.

---

## 2. Verification Workflow & Converge Invariants

- **NEVER rewrite, delete or weaken original tests or acceptance criteria** to force a failing check to pass. A technical limitation is a review finding; one that needs a contract change outside the agreed intent is reported as a problem for the Host.
- Verify mechanically (`git diff`, build, tests, linters), not by extra LLM re-evaluation.

### Step 1: Mechanical Git Diff Inspection
- Run `git status -s` and `git diff` against the base branch.
- Check for:
  - **Scope drift**: changes outside the declared `_Boundary:` in `tasks.md` without a stated reason. `_Boundary:` is expected scope; an explained extension is not a finding. A delegated write scope is strict: any change outside it is a finding. Implemented non-goals or unrequested features are always findings.
  - **Stray files**: leftover debug scripts, `.DS_Store`, temporary scratch files.
  - **Dead code / debug prints**: `print`/`console.log` debugging, commented-out code blocks, mock bypass flags.

### Step 2: Contract & Acceptance Criteria Validation
- Compare actual code and test outputs against every `[AC-NN]` Given/When/Then scenario in `spec.md`: happy path, edge cases and boundary conditions tested and passing; error payloads and status codes match the contract.
- Non-goals: no excluded scope implemented, even partially.
- Bugfix bundles: the Red and Green envelopes exist and the regression test is kept (`devkit workflow envelope check --unit <dir>`).

### Step 3: Run Deterministic Verification Gates
- Follow the repository's test policy on the reviewed content (e.g., `just test-affected`); preserve selector fallbacks and any named frontend checks. Run the full suite locally only when that policy or the selector requires it. A delegated reviewer reuses valid results and reruns only missing or stale checks.
- Run the linters and formatters (e.g., `just lint`) and the spec rules: `devkit rules check --staged` for staged changes, `devkit rules check --ci --base <ref>` for a committed branch.
- Exit code 0 with zero warnings and errors.

### Step 4: Capture Unstated Requirements & Drift
- Record each new requirement, API change or unexpected constraint the implementation revealed as a finding. One that changes the agreed contract is a problem for the Host; one inside it is fixed or waived in the reverify round.

---

### Delegated execution (Reviewer role)
- At medium and high the `code-reviewer` role runs this skill in an isolated context (through `spec-delegate`; `[DELEGATE]` for this stage), its first medium review mandatory regardless of change size; at low the Developer runs it. Both produce the same envelope. Its inputs, write boundaries and stale-head handling are in its contract (`.devkit/managed/spec/subagents/code-reviewer.md`).
- Every finding carries `evidence` (path:line), a `failure_condition` and a `severity` of `P1`, `P2` or `P3` at every effort (the `spec` skill's `references/review-loop.md` section 3 defines them; the implementer records the reviewer's level unchanged). Zero findings is a valid PASS; do not manufacture defects.
- After fixes, re-verify only the changed part. At medium the implementer verifies fixes and later changes and decides whether to call the code-reviewer again (the `spec` skill's `references/effort.md`), recording who checked what in `reverify`. At high the review runs in the bounded rounds of `references/review-loop.md`; each summary starts with `round <N>;`.

### Optional feedback breakpoint

After `review-refine` passes and before `living-spec-draft`, an executor may pause for user feedback or proceed automatically. An external runner owns that option and its wait/resume state; it adds no stage, check or approval file. Feedback that changes implementation returns to build/reverify for the affected part; a direction change is a close (the `spec` skill). It does not replace the `dev-integration` gate, and Living Spec reflection still completes before `dev-integration`.

## 3. Review Report

The review envelope is the report, for a direct run and a delegated Reviewer run alike. For a spec Unit (`spec` or `proposal` depth), record the findings as found (all open):

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

This writes the next `envelopes/review-NN.yaml`; omit `--findings-file` for a pass. After fixes, close the round with `devkit workflow envelope reverify --unit <dir> --stage review-refine --from latest --resolve <N> --waive <N>=<reason>` (`--resolve all` when every finding is fixed), which writes `reverify-NN.yaml` for `envelope-review-passed`. Do not record fixes inside the review file itself. A `session`-depth task states the same content in the final response or PR body and writes no envelope; a reviewer subagent returns it as a message.

- PASS is `status: completed` with no open findings; REVISE is `status: completed` with findings; `needs_input` when verification is blocked. Give the user a clear verdict.
