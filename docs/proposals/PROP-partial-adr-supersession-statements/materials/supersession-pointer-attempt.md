# Partial supersession pointers: findings from the closed pointer-check attempt

## 1. Identity and Boundary

- Source: the `spec`-depth attempt with the slug `supersession-pointer-summary-check` on
  `dev-supersession-pointer-summary-check`, started from `main` at `39cf1c39` (plan-intent commit `280626ea`). It
  stopped at `specify` with an uncommitted `spec.md` draft and was closed by depth escalation into this proposal; its
  branch was discarded unmerged, so no spec document with that slug exists.
- Inspected on: 2026-11-10.
- Scope: `docs/decisions/`, `RULE-decision-supersession`, the rules evaluator, the `adr-consolidation` playbook and the
  `spec-next` post-handoff reference in this repository.

## 2. What the attempt tried

The attempt planned to extend `RULE-decision-supersession` with a finding for a "Superseded in part by" pointer whose
text after the successor ID repeats the successor ADR's `summary` (whitespace normalized, trailing sentence mark
ignored). Its draft acceptance criteria:

1. A partial pointer that repeats the successor summary is reported once, naming the line and the successor ID.
2. A pointer whose text differs from the summary is not reported.
3. The handoff commit, which writes the summary pointer, is not refused by `devkit rules check --staged`.
4. `just rules-check` on the current `docs/decisions/` still exits 0, and each existing summary copy is reported
   without being rewritten.

Its non-goals excluded interpreting which clauses a replacement covers, rewriting existing pointers, changing the
handoff API, and the handoff docstring alignment of `FB-handoff-pointer-owner-docstring-mismatch` (deferred by the
user).

## 3. Why it stopped

- The rules evaluator gives every finding its rule's effective severity: `_check_rules` in
  `packages/devkit/src/devkit_agt/features/rules/services/evaluator.py` (line 175) assigns
  `effective_severity(rule, ...)` to each finding. `RULE-decision-supersession` is an error rule, so the new finding
  would be an error.
- Six existing ADRs carry a pointer equal to the successor's normalized summary, so an error finding fails
  `just rules-check` on `main` (criterion 4) and the handoff commit gate (criterion 3):
  - `ADR-proposal-acceptance`, `ADR-delivery-approval-and-lifecycle-authority`,
    `ADR-local-and-pull-request-integration` and `ADR-test-selection-and-ci`, each for `ADR-post-merge-verification`;
  - `ADR-orchestration-workers`, for `ADR-recorded-adjacent-path-extensions-for-development-workers`;
  - `ADR-steering-documents`, for `ADR-namespace-steering-directories`.
- The in-scope routes considered were a companion warning-severity rule, per-finding severity in the devkit-agt rules
  engine, or an error finding skipped in `--staged` runs after repairing the six pointers. Each widened the scope, and
  the user redirected the work to the ADR model itself.

## 4. Observations that inform this proposal

- The superseding ADRs already state their replaced scope in prose. `ADR-post-merge-verification` has one
  "This replaces `ADR-<target>` …" sentence per target in its Decision Outcome; `ADR-namespace-steering-directories`
  has "Replaces in `ADR-steering-documents`: …". The wording is free-form, so no rule or tool can extract it.
- `adr-consolidation` Step 2 reads the replaced scope from the earlier ADR's pointer ("a clause a 'Superseded in part
  by' line names is not in effect"), which is why the pointer text has to be clarified after handoff.
- `devkit docs refs <ID> --direction in` lists supersession references mixed with every other incoming reference
  (`ADR-test-selection-and-ci` returns plans, reconcile records and ADRs together); no command or viewer page shows a
  decision's partial replacements.
- 17 of the 65 ADRs carry at least one "Superseded in part by" line and none is wholly superseded, so partial
  supersession is the common path.
- `SPEC-partial-adr-supersession` (2026-10-30) introduced the current accepted-plus-pointer model and listed a
  structured field (`superseded_in_part_by`, `status: amended`) as a non-goal; Planning should read its reasons
  before choosing a structured form.
