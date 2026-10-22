---
id: FB-decomposed-from-refused-during-planning
title: Planning cannot split with --decomposed-from while its plan branch exists
scope: repo
kind: friction
category: instruction-conflict
target: devkit spec proposal new --decomposed-from (devkit_spec/proposals/backlog.py check_backlog_editable)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-19
---

# [FB-decomposed-from-refused-during-planning] Planning cannot split with --decomposed-from while its plan branch exists

## 1. Friction / Question (friction, question)

- **Context**: A `high` Planning run of PROP-integration-follow-ups, after the user chose to split it: narrow the
  proposal to base advances and create child drafts for two extensions with
  `devkit spec proposal new ... --decomposed-from PROP-integration-follow-ups`.
- **Expectation**: The proposal's own lifecycle section ("If Planning splits the work: decompose into child drafts
  with `--decomposed-from`") and the split option of the Planning question say Planning can create decomposed
  children of the proposal it is planning.
- **Actual**: The command refuses with `SPEC_PROPOSAL_IN_PLANNING`: the source must be a `draft` with no
  `plan-<slug>` branch, so a proposal in Planning (on its own plan branch, `status: reviewing`) can never be the
  `--decomposed-from` source. The `[FIX]` says "Change it on plan-<slug> as part of its Planning", which is where the
  command ran. Only the Backlog route (return to `needs_decompose`) records `decomposed_from`.
- **Workaround (or Interpretation Chosen)**: Created the children with plain `devkit spec proposal new` (the
  planning worker may write "a new draft proposal for a follow-up") and named the parent in each body; no
  `decomposed_from` frontmatter was hand-written.
- **Suggestion**: Either allow `--decomposed-from` when run on the source's own plan branch (the source stays and
  is narrowed, not deleted), or add a provenance field for a split that keeps its parent (such as `split_from`), and
  fix the proposal template and the `[FIX]` text to match.

## Evidence

```text
$ devkit spec proposal new integration-pull-request-cleanup --decomposed-from PROP-integration-follow-ups
[ERROR] (SPEC_PROPOSAL_IN_PLANNING) PROP-integration-follow-ups is in Planning on plan-integration-follow-ups;
        Backlog does not edit, split or delete it
[FIX]   Change it on plan-integration-follow-ups as part of its Planning, or wait until that branch is merged and removed
check_backlog_editable: refuses while planning_branches() has the slug, and when status != "draft"
proposal.md section 4 (scaffold): "If Planning splits the work: decompose into child drafts with --decomposed-from"
```

## Disposition

Directly addressed by `SPEC-feedback-planning-and-glossary` without promotion. The decomposition guard keeps its draft/no-Planning-branch restriction and supplies Host-managed return advice. Planning/Backlog guidance preserves evidence, closes questions, commits the draft return and names authorized CLI/PR integration and branch cleanup before rechecking editability. Local/fetched branch and non-draft refusal tests verify no mutation, the useful directive and successful creation once editable; independent medium code review confirmed the guidance. The affected suite passed 1,111 tests. This resolution does not assert integration.
