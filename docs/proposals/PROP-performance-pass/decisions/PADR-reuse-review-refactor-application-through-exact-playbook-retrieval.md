---
id: PADR-reuse-review-refactor-application-through-exact-playbook-retrieval
title: Reuse review-refactor application through exact playbook retrieval
summary: For applying agreed performance changes, we resolve review-refactor by exact playbook retrieval and cite its application and evidence sections by heading, always co-deploying it, to keep one application procedure that follows overrides, accepting a preset constraint and a heading test.
proposal: PROP-performance-pass
status: draft
created_at: 2026-10-27
---

# [PADR-reuse-review-refactor-application-through-exact-playbook-retrieval] Reuse review-refactor application through exact playbook retrieval

- **Status**: Draft
- **Date**: 2026-10-27

---

## 1. Context & Problem Statement

A performance pass applies agreed changes exactly as `review-refactor` does: one work item on its own branch, edit
tasks in disjoint scopes, one commit per change with verification before and after, differential old/new comparison,
a fresh adversarial review, report and integration. Copying those steps creates two copies that drift. A playbook's
relative body resources resolve against the parent of the effective `source.path` that exact retrieval returns, which
is an override path when the user overrode the playbook (`CAP-DIST-context-and-playbooks`). A file of another
playbook exists only when a selected preset deploys that playbook.

## 2. Decision Drivers

- One application and evidence procedure for both playbooks.
- The reference follows the user's override of `review-refactor`.
- A missing or renamed target is caught before release, not during a run.
- No playbook requires running another.

## 3. Considered Options

- **Exact retrieval plus cited headings, co-deployed** (selected): one procedure; adds a preset constraint and a test.
- **Relative link into the sibling directory**: no constraint; ignores overrides and breaks silently when
  `review-refactor` is not deployed.
- **Copy the shared steps**: self-contained; two copies drift, against the settled reuse by reference.

## 4. Decision Outcome

- `performance-pass`'s `SKILL.md`, before the decision round, tells the agent to run `devkit playbook get
  maintenance/review-refactor` and read `references/applying.md` and `references/criteria.md` next to the returned
  `source.path`, falling back to the managed copy when an override directory lacks the file.
- Citations name the file and the heading text without its number, in one form a test parses (for example
  `review-refactor references/applying.md "Commits and verification"`).
- Reading that text is reference reading, not an invocation: no intake, batch or decision round of `review-refactor`
  starts. `CAP-DIST-context-and-playbooks` states this for co-deployed playbooks.
- Every preset that deploys `performance-pass` also deploys `review-refactor`.
- Not followed: `review-refactor`'s "Work items and route"; the run's behavior-preserving work item follows the
  repository's feature workflow at its own depth, for one module or several (`user`), because the direct-mode
  overall-refactor route is granted to `review-refactor` runs only. Also not followed: its
  "approved behavior change" inside the behavior-preserving work item (every found difference is a contract change,
  `PADR-classify-performance-changes-by-observable-behavior`).
- `performance-pass` states only what it adds or overrides: measurement per change on a quiet machine, its
  preservation criteria, the reviewer brief additions and its report fields.

## 5. Consequences

- Positive: one procedure; improvements to `review-refactor` application apply to both.
- Negative: a `performance` preset also deploys `review-refactor`; a heading rename in `review-refactor` needs a
  matching edit here.
- Risk: a user override of `review-refactor` that drops a cited heading leaves the reference without a target; the
  playbook tells the agent to stop and report the missing section rather than improvise.

## 6. Confirmation

A `devkit-catalog` bundle test asserts that every preset containing `performance-pass` contains `review-refactor` and
that each citation in `performance-pass` (parsed from the fixed form) names a heading, number removed, that exists
in the named `review-refactor` file.
