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

- `performance-pass` tells the agent to run `devkit playbook get maintenance/review-refactor` and read
  `references/applying.md` and `references/criteria.md` relative to the returned `source.path`, naming the sections
  it applies by their headings, not by number.
- It reads them as the application procedure; it does not run `review-refactor` (no intake, batches or decision round
  of that playbook).
- Every preset that deploys `performance-pass` also deploys `review-refactor`.
- `performance-pass` states only what it adds: measurement per change, its preservation criteria, the reviewer brief
  additions and its report fields.

## 5. Consequences

- Positive: one procedure; improvements to `review-refactor` application apply to both.
- Negative: a `performance` preset also deploys `review-refactor`; a heading rename in `review-refactor` needs a
  matching edit here.
- Risk: a user override of `review-refactor` that drops a cited section leaves the reference without a target; the
  playbook tells the agent to stop and report a missing section rather than improvise.

## 6. Confirmation

A `devkit-catalog` bundle test asserts that every preset containing `performance-pass` contains `review-refactor` and
that each heading `performance-pass` cites exists in the named `review-refactor` file.
