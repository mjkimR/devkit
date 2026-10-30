---
id: MAT-git-operator-handoff-commit-evidence
title: Handoff transaction commit planning evidence
summary: "Record the devkit repository's 2026-10-30 Host handoff commits, the composed handoff's write-only code path and the options for who commits the handoff transaction, as Planning evidence for the result readiness proposal."
created_at: 2026-10-30
---

# [MAT-git-operator-handoff-commit-evidence] Handoff transaction commit planning evidence

## Evidence boundary

Repository: devkit, `main` at `fdba6646` (2026-10-30). This material holds Planning observations of this repository
only. `MAT-git-operator-consumer-pilot` keeps the resource-indexer pilot record unchanged.

## Observed Host handoff commits

Each composed handoff on 2026-10-30 exited 0 and left its transaction uncommitted in the new `dev-<slug>` worktree.
The Host committed it with one commit of the same shape before any worker started.

| Commit | Subject | Content besides the spec bundle, promoted ADRs and moved materials |
| --- | --- | --- |
| `a65f0a5d` | `feat(spec): hand off local orchestration resource manager` | none |
| `c29602db` | `docs(spec): hand off workflow record auto-commit Development` | none |
| `e2349f78` | `spec: hand off deep-research bundle split to Development` | `M docs/proposals/PROP-rename-incubation-to-adaptive-dev/proposal.md`: the sibling draft edit of `FB-handoff-rewrite-edits-sibling-draft` |
| `0debf74f` | `spec: hand off incubation to adaptive-dev rename to Development` | `M docs/decisions/2026-10/20261030-split-deep-research-bundle.md`: an accepted ADR reference rewrite |

The Host commit added no judgment: it staged every path the handoff changed. Its subject varied by Host.

## Code path

- `HandoffUseCase._execute` (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_handoff.py`)
  verifies the new worktree is clean at the reviewed base head, runs `handoff_and_register` and returns
  `status: handed_off` with no commit step.
- The composed acceptance (`native_plan_accept.py`) already commits its exact service-created delta
  (`spec: accept proposal <slug>`), checks the parent and changed paths after the commit, and on a commit-gate
  refusal withdraws its own writes and reports `SPEC_PROPOSAL_ACCEPT_COMMIT_REFUSED`.
- `CAP-DLV-proposal-planning` states that the plain handoff does not create a commit; the composed handoff
  contract names its effects without one.
- `spec-delegate`'s worker reference starts a worker's range at "the worktree's HEAD when you spawn the worker,
  after your own commits": the Host commit step is implied, not named.
- The shared Git hooks run a commit gate; a post-commit hook in this repository rewrites the commit
  (`[cgate] Commit rewritten: <old> -> <new>`), so a tool reports HEAD after hooks, as
  `ADR-explicit-envelope-commits` requires for `devkit workflow envelope commit`.

## Options for the handoff transaction

| Option | Host step | Worker input | Cost | Risk |
| --- | --- | --- | --- | --- |
| A. Composed handoff commits its transaction | removed | clean, committed, HEAD reported | one commit step plus gate-refusal handling in `native_handoff.py`, mirroring acceptance | a gate refusal leaves the transaction uncommitted; reported as a stopped handoff |
| B. Keep write-only; the result reports dirty paths and the next actor | kept, now named | clean only after the Host commit | contract text only | the Host commit stays a manual, unnamed-message step on every handoff |
| C. Commit in every handoff, plain included | removed | clean | as A, plus the plain handoff in a checkout that may hold other work | commits unrelated work or refuses in a dirty `dev-<slug>` checkout |

Planning recommends A: the composed handoff runs only in a worktree it verified clean, so its delta is exactly its
own, the same condition under which the composed acceptance already commits.
