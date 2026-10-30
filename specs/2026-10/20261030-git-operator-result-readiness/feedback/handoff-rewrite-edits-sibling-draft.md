---
id: FB-handoff-rewrite-edits-sibling-draft
title: Handoff reference rewrite edits a sibling draft on the dev branch
scope: repo
kind: friction
category: tool-error
target: devkit spec proposal handoff
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-30
---

# [FB-handoff-rewrite-edits-sibling-draft] Handoff reference rewrite edits a sibling draft on the dev branch

## 1. Friction / Question (friction, question)

- **Context**: `devkit spec proposal accept deep-research-bundle --mode accept_and_handoff` while a sibling proposal
  that cites it, `SPEC-rename-incubation-to-adaptive-dev`, was in Planning on its own `plan-` branch.
- **Expectation**: The handoff rewrites references inside the handed-off Unit and its promoted ADRs; a sibling draft
  owned by another Planning branch is left to that branch, or the rewrite is reported for the Host to schedule.
- **Actual**: The rewrite also edited the sibling's `proposal.md` (its base-branch draft version) in the new
  `dev-deep-research-bundle` worktree, uncommitted (`SPEC_PROPOSAL_REFS_REWRITTEN` listed it among its targets). After
  the sibling's Planning merged into `main`, merging `main` into the dev branch conflicted on that file.
- **Workaround (or Interpretation Chosen)**: The Host took the accepted version from `main` and ran `devkit rules fix`
  on the sibling proposal, which rewrote the four citations to `SPEC-deep-research-bundle`.
- **Suggestion**: Leave proposals owned by an active `plan-` branch out of the handoff rewrite and report them as
  pending rewrites, or rewrite them only through `devkit rules fix` once their Planning merges.

## Diagnostic Details

- **Reproduction**: Two related drafts in parallel Planning; accept and hand off the cited one first while the citing
  one is still in Planning; later integrate the citing one and merge `main` into the dev branch.
- **Expected / Actual**: Expected no edit to a Planning-owned sibling; observed a one-line edit and a later conflict.
- **Versions**: devkit workspace at `fb9b549a`..`b2711684`.
- **Conditions**: `local-orchestrated`, `worktree = "required"`, `plan-accept = ask`.
- **Workarounds Attempted**: Accepted version plus `devkit rules fix`; succeeded.
- **Related Assets**: `devkit spec proposal handoff`, `devkit spec proposal accept --mode accept_and_handoff`,
  `SPEC_PROPOSAL_REFS_REWRITTEN`, `CAP-DLV-proposal-planning`.

## Evidence

```text
[NOTICE] (SPEC_PROPOSAL_REFS_REWRITTEN) 10 ID reference(s) to PROP-deep-research-bundle or its PADRs now name the spec or the ADRs
[TARGET] ..., docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md, ...
CONFLICT (content): Merge conflict in docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md
```

## Resolution

- **Disposition**: Resolved directly by `SPEC-git-operator-result-readiness` with the Planning decision kept: the
  handoff still rewrites a sibling draft's `depends_on` and ID references (a skipped `depends_on` dangles once the
  dev branch lands), and the guidance names the resolution of the later base-merge conflict. The `spec-next`
  post-handoff reference (section "Sibling drafts"), `CAP-DLV-proposal-planning` section 4.7 and
  `UC-plan-and-hand-off-a-proposal` extension 8a tell the Host to take the base version of the conflicting file under
  `docs/proposals/PROP-<other>/` and run `devkit rules fix` on it, which rewrites the citation to `SPEC-<slug>`.
- **Verification**: `packages/devkit-spec/tests/integration/bundles/spec/test_post_handoff_guidance.py` checks the
  guidance; `tests/integration/features/proposals/test_unit_dependencies.py::test_carry_rewrite_namespaced_and_preserve_history`
  keeps the sibling `depends_on` rewrite; `RULE-document-reference` reports and fixes `PROP-<slug> was handed off`
  (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`). Medium
  code review (`envelopes/review-01.yaml`, closed by `envelopes/reverify-01.yaml`) confirmed AC-08.
