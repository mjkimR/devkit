---
id: PLAN-review-refactor-lessons
spec: SPEC-review-refactor-lessons
---

# Technical Plan: `SPEC-review-refactor-lessons` Review-refactor playbook: parallel application and preservation lessons

## 1. Architecture Overview & Impact

- Target area: the `maintenance` catalog bundle's `review-refactor` playbook (guidance only, no code) and its Living
  Spec: `CAP-DLV-review-refactor`, `UC-review-and-refactor-accumulated-slop` and the application ADR.
- The repository does not select the `maintenance` bundle, so no managed copy changes; the bundle's packaging tests
  cover the asset.

## 2. Component Breakdown & Interface Contracts

| Component | Change | ACs |
| --- | --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/applying.md` | §3 subagent edits: parallel isolated checkouts by default for disjoint scopes, preparation like a fresh checkout, uncommitted results moved and committed one at a time, sequential for overlaps and dependencies, no governance relaxation; §4 removal sweep; §5 adversarial reviewer brief; §6/§7 report outcome after integration | 01, 02, 03, 06, 07, 08 |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/criteria.md` | §4 differential comparison for changes with a definable input domain, side-by-side old code without stashing; divergence list for consolidations | 04, 05 |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/SKILL.md` | decision round lists behavior differences; report adds behavior changes and the integration state after integration | 05, 08 |
| `CAP-DLV-review-refactor` | change contract items 3, 6, 7, 8 and report interface | all |
| `UC-review-and-refactor-accumulated-slop` | scenario and extensions for parallel application and the reviewer | 01, 02, 07 |
| a new ADR, slug `apply-review-refactor-changes-in-parallel-checkouts` | supersedes `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`, restating its decision with parallel application | 01, 02, 03 |

The playbook must stay self-contained for repositories without the `spec` bundle: "isolated checkout" names a Git
worktree or any separate checkout, and preparation names the repository's own setup.

## 3. Verification & Test Plan

- `uv run devkit rules check` on every changed document (document size for the playbook, references, IDs, links).
- `just test devkit-catalog` (bundle packaging and asset tests) and `just rules-check`.
- Review: a fresh reviewer maps each AC to the playbook sections and checks the CAP, UC and ADR agree with them.
