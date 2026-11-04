---
id: PLAN-rejection-reason-rewritten
spec: SPEC-rejection-reason-rewritten
---

# Technical Plan: `SPEC-rejection-reason-rewritten` Rejection records carry a rewritten decision, not a quote

## 1. Constitution & Invariant Review

- The spec constitution's records rule (decisions, never quotes or paraphrases) is the invariant this change
  restores; no ADR is needed, because no decision changes: the rejection still changes the status only and the
  hygiene pass still writes the ADR and deletes the proposal (`ADR-proposal-acceptance`, `CAP-DLV-proposal-planning`
  rule 9).
- Editing `ADR-reject-ux-rules-path-exclusion` replaces a quote with the same decision in sentence form: a wording
  repair the constitution permits without a new ADR.

## 2. Architecture Overview & Impact

- Target Area: the `spec` bundle of `devkit-spec` (workflow and playbook sources), the proposal scaffold text in
  `devkit_spec.features.proposals.usecases.scaffold`, and `CAP-DLV-proposal-planning` in `docs/capabilities/delivery/`.
- `workflows/sdd-proposal.md` Gate rules: the rejection sentence names the form (decision and reason, rewritten as one
  English decision sentence, `user` as decider, no quote).
- `playbooks/feedback-hygiene/SKILL.md` Step 4: "quoting the reason from the rejection commit" becomes "stating the
  decision and reason recorded in the rejection commit".
- `scaffold.py` Lifecycle comment: the same form in one line.
- `CAP-DLV-proposal-planning` rule 9: names the form, written at `living-spec-draft` and listed in `reconcile.md`
  together with the ADR repair and the feedback resolution.
- Tests: one guidance test in `packages/devkit-spec/tests/integration/bundles/spec/test_workflows.py` (or a sibling
  guidance module) asserting AC-01 and AC-02 with `assert_rule` and the negative phrases.
- `devkit sync` regenerates `.devkit/managed/spec/` and `.devkit/installation.json`.

## 3. Verification & Test Plan

| Check | Command |
| --- | --- |
| Guidance and scaffold tests | `just test-affected` (fallback `just test devkit-spec tests/integration/bundles/spec tests/integration/features/proposals`) |
| Wording hygiene | `uv run devkit rules check --phase hygiene` on the two bundle sources |
| No quote request left | the `rg` command of AC-07 |
| Document rules | `uv run devkit rules check --staged`; `--ci --base <ref>` on the committed head |
| Lint and types | `just lint-check devkit-spec`, `just check devkit-spec` |
