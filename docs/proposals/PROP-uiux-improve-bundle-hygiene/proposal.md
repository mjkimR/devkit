---
id: PROP-uiux-improve-bundle-hygiene
title: app-uiux-improve pilot hygiene fixes
summary: 'Fixes app-uiux-improve instruction gaps a consumer pilot exposed: branch-build verification, brief and non-goal hygiene, craft-rule precedence, scope-aware acceptance, computed contrast, workflow-neutral wording and a plugin-enablement note.'
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
depends_on: [PROP-uiux-improve-impeccable-routing]
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
  excludes:
    - docs/decisions/
    - packages/devkit-dist/
    - packages/devkit-spec/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-uiux-improve-pilot-fit
workflow: sdd-proposal
---

# [PROP-uiux-improve-bundle-hygiene] app-uiux-improve pilot hygiene fixes

## 1. Background & Hypothesis

`app-uiux-improve` 0.1.6 ran in a consumer repository for a whole-surface color-system refresh with the
user-selected Impeccable track. `MAT-uiux-improve-pilot` (held in this bundle) records the run; finding IDs below
refer to it. This proposal takes the findings that are instruction gaps inside the bundle's current contract: each
one needs clearer wording, a missing step or a test, and none changes who holds authority. It needs no ADR.

Split from ~~`PROP-uiux-improve-pilot-fit`~~ (drafted in `6902170e9`, deleted in this split) with
`PROP-uiux-improve-impeccable-routing` (question and load routing) and `PROP-uiux-improve-run-model` (the run model).
All three touch the bundle's `SKILL.md` and `CAP-DLV-uiux-improvement`. The user set the delivery order:
`PROP-uiux-improve-run-model` first, then `PROP-uiux-improve-impeccable-routing`, then this proposal, which
`depends_on` the routing proposal and builds on both.

Hypothesis: with these gaps closed, a coordinator verifies the branch it changed, keeps a task focus from turning into
a prohibition, tells an Impeccable session which rule wins, catches an in-list but out-of-scope change and measures
contrast instead of estimating it.

## 2. Technical Spike Questions

The direction is settled; Planning confirms wording and test placement only.

- **Q1**: Which `CAP-DLV-uiux-improvement` rules change (expected: 11 verification, 16 brief, 17 acceptance, 18
  context files) and which statements need a new rule, for example a computed contrast check?
- **Q2**: Which statements get a test assertion in `test_app_uiux_improve.py` and which stay review-only?

## 3. Proposed Design & Impact

1. Verification target (A3). SKILL step 2 and step 8 inspect and verify the branch build running locally. When the
   backend is costly or shared, stub it (for example API mocking in the browser driver) and keep a re-runnable
   before/after capture. A deployed environment is at most a baseline. Under rule 11, the report labels mocked
   coverage as mocked, not as an end-to-end check.
2. Brief and spec hygiene (A4a to A4c).
   - Non-goals carry only user-stated constraints or explicit deferrals; a task focus ("color first") orders the
     work and is not a prohibition.
   - The brief states precedence when an Impeccable craft default conflicts with the brief or the spec.
   - Acceptance compares the accepted change with the spec's or request's goal scope as well as the edit list, and
     reports an in-list but out-of-scope change.
3. Contrast (A7). `design-guidance.md` and the designer roles call for a computed contrast check (color-space
   conversion, not an approximation) for color work and report the measured ratio for each key pair.
4. Untracked context files (A5), neutral line only. When `PRODUCT.md` or `DESIGN.md` is untracked or excluded and the
   session runs elsewhere, the brief passes their absolute paths read-only. The coordinator reports them under
   rule 18 with upstream's retention guidance and does not override that guidance. Choosing an in-place branch or a
   worktree stays with the consumer's own per-task settings.
5. Workflow-neutral wording. The skill and its references name no `devkit-spec` policy key (for example `worktree`
   or `pull_request` values), in line with rule 13; a test asserts the absence.
6. Plugin visibility note (A2, corrected). The README troubleshooting table says a plugin skill is visible only
   where the plugin is enabled, so a child or session in a project without that enablement cannot load it. Reading
   `SKILL.md` from the plugin cache is recorded as an observed, undocumented workaround, not a route the skill names;
   routing decisions belong to `PROP-uiux-improve-impeccable-routing`.

Impact: `CAP-DLV-uiux-improvement`, possibly `UC-improve-an-interface-and-user-flow` acceptance examples, the bundle's
`SKILL.md`, `references/orchestration.md`, `references/design-guidance.md`, designer roles, README and
`test_app_uiux_improve.py`. No ADR, no workflow or distribution change.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` (after Planning, or `--direct` if the direction is
  confirmed settled); handed off to `sdd-spec-feature` on `dev-uiux-improve-bundle-hygiene`. The proposal is deleted
  there and `MAT-uiux-improve-pilot` moves to `docs/materials/`, where the sibling proposals keep citing it by ID.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal. Before that deletion, move `MAT-uiux-improve-pilot` to a live sibling.
