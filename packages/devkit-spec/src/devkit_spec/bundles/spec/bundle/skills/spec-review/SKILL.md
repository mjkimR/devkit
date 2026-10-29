---
name: spec-review
description: Verify the git diff, acceptance criteria and test results before declaring a task or feature complete; detects unexplained scope drift, phantom completion and unstated requirement drift.
---

# spec-review: Pre-Completion Verification Workflow

Use at the `review-refine` stage (all tasks checked) or before submitting a pull request. Review committed content
so the envelope's `--head` names it; state any included uncommitted changes in `assumptions`.

## Constraints

- Never weaken, delete or rewrite tests or acceptance criteria to make a check pass; record the limitation as a
  finding, and a needed contract change as a problem for the Host.
- At `activity-effort` medium and high the `code-reviewer` role runs this skill through `spec-delegate`; at low, the
  Developer does. Each finding carries `evidence`, a `failure_condition` and a `severity` of `P1`, `P2` or `P3` at every
  effort. Rounds and re-verification: the `spec` skill's `references/effort.md` and `references/review-loop.md`.
- Zero findings is a valid PASS.

## Steps

### Step 1: Diff

`git diff` against the base. Findings: changes outside `_Boundary:` without a stated reason (any change outside a
delegated write scope), implemented non-goals or unrequested features, stray files, debug leftovers.

### Step 2: Acceptance criteria

Every `[AC-NN]` scenario in `spec.md`, edge and error cases included, is tested and passing; no non-goal is
implemented. A bugfix has its Red and Green envelopes and keeps the regression test.

### Step 3: Checks

Run the repository's test policy on the reviewed content (e.g. `just test-affected`, keeping selector fallbacks and
named frontend checks), the linters, and `devkit rules check --staged` (staged) or
`devkit rules check --ci --base <ref>` (committed branch). A delegated reviewer reruns only missing or stale checks.

### Step 4: Drift

Each requirement, API change or constraint the implementation revealed is a finding; one that changes the agreed
contract is a problem for the Host.

## Report

For a spec Unit, record all findings as open:

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

- For a pass, omit `--findings-file`. After fixes, close the round with
  `devkit workflow envelope reverify --unit <dir> --stage review-refine --from latest --resolve <N|all> --waive <N>=<reason>`.
- A `session`-depth task gives the same content in the final response or PR body.
- Feedback after a passed review that changes the implementation returns to build/reverify; a direction change is a
  close.
- After `devkit workflow return`, the earlier review no longer passes `review-refine`: a `reverify` of it closes its
  findings only, and the stage needs a fresh independent review envelope of the fixed range.

## Completion

- [ ] The user has the verdict: PASS (no open findings), REVISE (findings) or `needs_input` (verification blocked).
- [ ] For a spec Unit with a PASS, `devkit workflow next --unit <dir>` no longer lists `envelope-review-passed` as
  unmet.
