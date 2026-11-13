---
id: PROP-uiux-improve-bundle-hygiene
title: app-uiux-improve pilot hygiene fixes
summary: "Fixes app-uiux-improve pilot instruction gaps in branch-build verification, brief scope, craft-rule precedence, change acceptance, computed contrast, local context paths and plugin-enablement troubleshooting."
status: accepted                     # draft | reviewing | accepted | rejected
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
`PROP-uiux-improve-impeccable-routing` (question and load routing) and `SPEC-uiux-improve-run-model` (the run model).
All three touch the bundle's `SKILL.md` and `CAP-DLV-uiux-improvement`. The user set the delivery order:
`SPEC-uiux-improve-run-model` first, then `PROP-uiux-improve-impeccable-routing`, then this proposal, which
`depends_on` the routing proposal and builds on both.

Hypothesis: with these gaps closed, a coordinator verifies the branch it changed, keeps a task focus from turning into
a prohibition, tells an Impeccable session which rule wins, catches an in-list but out-of-scope change and measures
contrast instead of estimating it.

## 2. Technical Spike Questions

Planning settled wording and test placement against source HEAD `aa6c51dc3148efba121bc54c8e582a59aacd11d1`.
No business question remains; acceptance and Development handoff stay with the Host.

- **Q1 resolved**: clarify `CAP-DLV-uiux-improvement` rules 4 (focus versus constraint), 11 (branch-build and
  measured-color verification), 16 (brief precedence and read-only absolute context paths), 17 (goal-scope acceptance)
  and 18 (retention report). Rule 13 remains unchanged. Computed contrast extends rule 11's verification obligation;
  it needs no separate authority rule or ADR.
- **Q2 resolved**: extend the existing integration instruction assertions and add focused assertions for measured
  contrast and workflow-neutral wording. Use representative instruction walkthroughs for actual behavior; static
  assertions establish only that the required instructions are present. Details are in `target-docs.md`.

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

Impact: `CAP-DLV-uiux-improvement` rules 4, 11, 16, 17 and 18; `UC-improve-an-interface-and-user-flow` inspection,
acceptance and coverage examples; the bundle's `SKILL.md`, `references/orchestration.md`,
`references/design-guidance.md`, `roles/designer.md`, `roles/unconventional-designer.md`, human README and
`test_app_uiux_improve.py`. `target-docs.md` maps the wording and acceptance checks. No ADR, workflow, runtime API,
package dependency or distribution change is required.

### Planning decisions and constraints

- Keep `planning_effort: low` because direction is settled; retain `dev_effort: medium` for instruction review and
  bundle checks. No scout or challenger pass is required at this Planning effort.
- Preserve delivery order: `SPEC-uiux-improve-run-model`, then `PROP-uiux-improve-impeccable-routing`, then this
  proposal. Rebase is not worker work: the Host refreshes this Planning branch or the Development input when those
  predecessors land. Recheck the affected rule numbers and wording then; no sibling decision is treated as settled
  by this plan.
- Preserve the consumer's chosen workflow and Impeccable route as the predecessors settle them. This proposal adds
  no run mode, question relay, plugin-load fallback, setup authority or context-file write authority.
- Apply workflow neutrality to agent-read skill, reference and role bodies. General references to a branch,
  worktree or the consumer workflow are allowed; concrete devkit-spec policy keys, values, CLI gates and lifecycle
  records are not instruction dependencies. The human README keeps its installation command.
- Apply brief precedence within existing authority: user-authorized goals, explicit constraints and the current
  consumer specification control craft defaults. If those sources conflict with one another, return the conflict
  for a decision instead of choosing new authority.
- Compare the changed branch build before and after with the same representative task and data. If a live backend
  is unsuitable, use a repeatable mock against that branch build and report mocked coverage. No performance or
  real-user improvement claim follows from this instruction change.
- No concrete work is deferred by this proposal beyond the policy and routing changes already owned by the two
  named predecessor proposals.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: the Host uses `devkit spec proposal accept-plan uiux-improve-bundle-hygiene` after reviewing the
  committed Planning result and obtaining the required approval. Development handoff follows the predecessor order
  on `dev-uiux-improve-bundle-hygiene` with `dev_effort: medium`. The proposal retires there and
  `MAT-uiux-improve-pilot` moves to `docs/materials/`, retaining its ID and sibling citations.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal. Before that deletion, move `MAT-uiux-improve-pilot` to a live sibling.
