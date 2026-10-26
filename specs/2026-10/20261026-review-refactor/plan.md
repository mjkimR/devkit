---
id: PLAN-review-refactor
spec: SPEC-review-refactor
---

# Technical Plan: `SPEC-review-refactor` Maintenance review and refactoring playbook

## 1. Constitution & Invariant Review

None. The four accepted ADRs (`ADR-bound-review-refactor-runs-by-surface-batch`,
`ADR-apply-approved-contract-removals-as-separate-work-items`,
`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`,
`ADR-require-reachability-evidence-and-layered-placement`) settle the run model; the direct-mode ADR refines the
applicability of `ADR-overall-refactor-workflow` for these runs. Invocation follows `ADR-external-playbook-execution`
and `ADR-spec-intake-playbook-discovery` unchanged. The `all` preset stays implicit (`CAP-DIST-manifest-spec`), no
version changes (shared release version), and the bundle stays content-only with no runtime dependency
(`CAP-DIST-content-packages`). The playbook cites no repository ID, as bundle self-containment requires.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/bundle.toml` | Asset `review-refactor` (directory source), `upkeep` gains it, new preset `refactoring` |
| `.../maintenance/bundle/playbooks/review-refactor/SKILL.md` | Entry condition, intake, batches, review with subagents, findings, decision round, completion and report |
| `.../review-refactor/references/criteria.md` | Review questions per surface, dispositions, reduction grounds, preservation evidence, helper placement (read at the review and evidence steps) |
| `.../review-refactor/references/applying.md` | Route and single-module test, write scope, direct mode, subagent edits, commits, verification, review, report and integration, contract-removal work items (read when a decision round approved changes) |
| `packages/devkit-catalog/tests/integration/bundles/test_bundles.py` | Preset matrix with `refactoring`, directory-form file set, manifest presets, entry condition, self-containment, size and reference links |
| `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md` | Preset table row and maintenance section; recommendation row |
| `docs/capabilities/distribution/CAP-DIST-content-packages.md` §6 | The third playbook and both presets |
| `docs/capabilities/delivery/CAP-DLV-review-refactor.md` (new) | The playbook's contract, entrypoint `SKILL.md` |
| `docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md` (new) | The developer's goal, scenario, extensions and acceptance scenarios |

No new dependency. Choice: directory form over one file, because the agreed rules exceed the 12288-byte budget
without trimming required constraints; the split follows when each part is needed (every run; review and evidence;
application after approval), so an unattended run that stops at the decision round never reads `applying.md`.

## 3. Component & Interface Design

Manifest fragment:

```toml
[[assets]]
id = "review-refactor"
kind = "playbook"
source = "playbooks/review-refactor"

[presets.upkeep]
assets = ["drift-reconciliation", "review-refactor"]

[presets.refactoring]
assets = ["review-refactor"]
```

Playbook header: `name: review-refactor`, `description` naming one operation (a review and refactoring pass that
consolidates and reduces code, agent guidance and CLI commands) and its scope (user-selected surfaces and roots).

`SKILL.md` sections: entry condition; 1 Intake and batches; 2 Review a batch (subagent review rules, tool output as
candidates); 3 Record findings; 4 Decision round; 5 Apply agreed changes (pointer to `references/applying.md`);
6 Report and completion; exercise rule. `references/criteria.md`: code, guidance and CLI review questions; the named
cost rule; dispositions; reduction grounds; preservation evidence; helper placement; recurrence prevention.
`references/applying.md`: route and single-module test, write scope, direct mode and branch, subagent edits, commits
and verification, review, report and integration, contract removals.

## 5. Error Handling & Edge Cases

- Missing scope: clarified before inspection. Unselected landing surface: deferred unless the user adds the surface.
- Host without subagents: the same steps in the playbook's agent; review falls back to a recorded self-review.
- HEAD or dirty paths move between intake and application: evidence revalidated, changed intent re-decided.
- Receipt-owned files: read-only evidence; findings go to the source bundle or `devkit override`.

## 6. Verification & Test Plan

| Scenario | Verification |
| --- | --- |
| AC-01, AC-02, AC-03, AC-04 | `just test devkit-catalog` (bundle integration tests); `uv run devkit rules check --phase hygiene <pb>` |
| AC-05 | `materials/checklist.md` checked by the code reviewer against `<pb>` |
| AC-06 | `uv run devkit rules check` (references, use case and capability links), reviewer reading |
| AC-07 | `materials/sweep.md` and the feedback files (manual evidence) |
| AC-08 | `materials/fixture-exercise.md` with fixture patches, commits and command output (manual evidence) |

Repository checks: `just lint devkit-catalog`, `just check devkit-catalog`, `just test-affected`, `just rules-check`.
