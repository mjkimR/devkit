---
name: performance-pass
description: Manually run a performance pass over user-selected slow commands or operations that measures them unprofiled, attributes their cost and applies only agreed behavior-preserving speedups with measured before/after and differential evidence, stopping at one decision round.
---

# Performance pass

Run only when the user invoked or confirmed this playbook (`devkit-playbook`, `devkit playbook get
maintenance/performance-pass` or a confirmed intake offer); selection never executes it. The outcome is a measured
speedup of the operations the user selected, with each saving shown unprofiled against the previous revision.
Invocation, an external runner naming this playbook and a clean measurement authorize no change. Only the user's
decision round does: an unattended run stops at the decision round with nothing applied.

## Constraints for every run

- Apply no change before the decision round approved it.
- Keep every observable behavior of the targets; a speedup that changes one is a contract change with its own work
  item.
- Report savings from unprofiled measurement on this machine in this session, never from a profile or from another
  session's numbers; those are context only.
- Never edit receipt-owned files (`.devkit/managed/`, agent projections): read them as evidence and send a change
  against them to the source bundle, an upstream follow-up or `devkit override`.
- If you find a correctness defect on the way, record it as a follow-up; never fix it in the pass.
- Never stash or switch the working checkout; run an older revision from an extracted copy or a separate checkout.

## 1. Intake

1. Record the run ID, a credential-free repository identity, HEAD, dirty paths, prior reports and the report
   destination: the owning work unit's materials, else the repository's materials location, as an ordinary local
   file.
2. Record the environment: machine, operating system, runtime versions and the load at intake.
3. Have the user select the targets. Record each as an exact argument list with its working directory and
   environment, the metric (wall time, subprocess count, peak memory) and the goal when the user has one.
4. Clarify missing scope before any timed run.
5. Select the mode with the user:

| Mode | Entry | Read | Ends |
| --- | --- | --- | --- |
| `survey` | The user names candidate operations and wants a ranked list | measurement, profiling, candidates | Decision round with nothing applied. An approved change turns the run `targeted`; record the switch in the report |
| `targeted` | The user names operations to speed up | Every reference in phase order | Report with measured before/after per change |

## 2. Measure and attribute

1. In every mode, read `references/measurement.md` before the first timed run, and record a baseline per target by
   its protocol.
2. When the measurement does not already name the cost (a composite whose components do not explain the total, or
   one opaque process), read `references/profiling.md` and attribute the cost by it.
3. Before the decision round, read `references/candidates.md` and record each candidate by it.

## 3. Resolve review-refactor

The application procedure and the preservation evidence are `review-refactor`'s, cited by file and heading. Resolve
them before the decision round:

1. Run `devkit playbook get maintenance/review-refactor`.
2. For each cited file, read `references/<file>` next to the returned `source.path`. When that path is an override
   directory without the file, read the managed copy; files missing from an override directory are read from
   upstream.
3. Reading that text is reference reading, not an invocation: none of `review-refactor`'s intake, batches or decision
   round starts.
4. If a cited heading is missing from the file you read, stop the run and report the missing section; never
   improvise the procedure.

A citation names the file, then the heading without its number, for example
`review-refactor references/applying.md "Commits and verification"`.

## 4. Decision round

Present all candidates of the run together, each with its record, classification and proposed disposition, and for
changes the route and the edited paths. Record each decision with its reason and provenance.

| Disposition | Record and next action |
| --- | --- |
| Apply with behavior preserved | Joins the run's work item; measured before/after and differential evidence per change. |
| Contract change | Its own work item through the repository's normal development workflow. |
| Defer | Reason, follow-up destination (existing or newly created) and restart condition. |
| Keep | The reason the cost is accepted. |

- Route: the run's agreed behavior-preserving changes form one work item that follows the repository's feature
  workflow at the depth its own classification gives (with the `spec` bundle, `session` when no contract or
  specification text changes), whether it edits one module or several. Never split or merge the work item to change
  its route.
- Do not follow `review-refactor references/applying.md "Work items and route"`: its direct-mode overall-refactor
  route belongs to `review-refactor` runs, and this route replaces it.
- State the route and the edited paths in the round; the edited paths, following edits included, are the write
  scope.
- Leave an unanswered candidate pending; nothing is applied for it.
- The user's approval in the round is the recorded intent (goal, scope and non-goals) of the routed work item. It
  never supplies the work item's integration approval.
- In an exercise, label decisions as simulated; they change only the fixture.

## 5. Apply agreed changes

When the round approved changes, read `references/changes.md` and follow it. If HEAD or a relevant dirty path moved
since intake, re-run the baseline and revalidate the evidence first, and take a change whose intent shifts back to
the decision round.

## 6. Report and completion

Recheck HEAD and dirty paths, then write the report:

- Intake and environment, mode (and a switch to `targeted`), targets and the baseline record per target.
- Coverage: operations measured, components attributed, candidates dropped below the noise floor, coverage gaps.
- Candidates and changes as separate records. Each change names its candidate, classification, differential inputs
  and their count, verification, measured before/after and commit.
- Decisions with provenance, follow-ups, and counts: candidates, applied, contract work items, deferred, kept,
  pending.
- The final interleaved measurement of every target against the intake revision.
- Outcome: `stopped at decision round`, `applied` or `partially applied`, with the work items' integration state.
  Update it once each work item integrates or stops.

Claim the run complete only with no pending decision, every agreed change committed or routed and the final
measurement recorded. A `survey` run that applied nothing is complete with its decisions recorded and its outcome
`stopped at decision round`.
