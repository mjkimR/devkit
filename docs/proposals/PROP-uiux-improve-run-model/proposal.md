---
id: PROP-uiux-improve-run-model
title: app-uiux-improve runs outside the repository workflow on per-task approval
summary: "Offers an explicitly approved per-task UI/UX run outside the consumer workflow while retaining product constraints, host permissions and applicable checks. The user can instead keep the consumer workflow."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/2026-11/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
    - packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/
  excludes:
    - docs/capabilities/harness/
    - packages/devkit-spec/
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit-dist/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
decomposed_from: PROP-uiux-improve-pilot-fit
workflow: sdd-proposal
---

# [PROP-uiux-improve-run-model] app-uiux-improve runs outside the repository workflow on per-task approval

## 1. Background & Hypothesis

`CAP-DLV-uiux-improvement` rule 3 (consumer authority) requires the coordinator to carry every requested change
through the consumer's existing workflow, permissions and approvals (`ADR-uiux-improvement-workflow-boundary`
clause 2, kept by `ADR-impeccable-session-authority`). The bundle installs without `devkit-spec` (rule 13), so "the
consumer's workflow" can be SDD, adaptive development, a team PR and CI process, or nothing formal.

The bundle owner's observation: running a UI/UX improvement through the repository's development workflow did not
fit, and a whole-surface overhaul is hard to carry through it. This proposal is a workflow-neutral bundle policy: it
does not add a route to any particular workflow, and it depends on no `devkit-spec` concept. Split from
~~`PROP-uiux-improve-pilot-fit`~~ (drafted in `6902170e9`, deleted in this split) with
`PROP-uiux-improve-bundle-hygiene` and `PROP-uiux-improve-impeccable-routing`. The user set the delivery order: this
proposal first, then `PROP-uiux-improve-impeccable-routing` (`depends_on` this one), then
`PROP-uiux-improve-bundle-hygiene` (`depends_on` the routing proposal).

Proposed default (the bundle owner's): before starting, the skill tells the user that this procedure proceeds without
following the repository's development workflow and guidelines, and proceeds only after the user approves (or hears
the user's preference). The user may instead choose to follow the repository workflow, and the skill then keeps
rule 3 as it is today.

### Evidence

Two runs in one SDD consumer; `MAT-uiux-improve-pilot` holds the first and `MAT-uiux-improve-second-pilot` (held in
this bundle) the second, the commit attribution and the measurement plan.

- First run, through the workflow (`spec` depth): 18 branch commits, of which 4 touched product code, tests or the UI
  README. By cause (challenger attribution, kept as found): 8 commits record only an envelope (tooling
  granularity, recorded as separate tooling feedback); 2 of those are optional UX-review rounds and 2 are
  finding-driven re-checks; contract amendments during the build came partly from scope creep that the contract
  correctly surfaced; an invented non-goal was a coordinator error (fixed by `PROP-uiux-improve-bundle-hygiene`).
  The residue that SDD structure alone explains is the spec, plan and task authoring, three lifecycle commits,
  `reconcile.md` and the mandatory check envelopes. The workflow also caught real defects: a semantic defect (UX
  review), a test gap (code review) and stale UX documents (reconcile).
- Second run, outside the workflow on the user's explicit per-task instruction: about three product commits and one
  merge, one question round; no independent code or UX review and no documentation reconcile; the edit-list rule
  caught an unwanted dependency bump. Confounds: a narrower task, a coordinator that had learned from the first run,
  and no independent check to show what it missed.

The evidence supports "much less bookkeeping"; it does not yet show "no loss of caught defects". The measurement plan
in `MAT-uiux-improve-second-pilot` tracks that.

### Governance objection and how this proposal answers it

A challenger review objected that a catalog skill defaulting outside a configured approach contradicts rule 3,
`ADR-uiux-improvement-workflow-boundary` clause 2, `CAP-HARN-agent-guidance` ("installing or selecting spec assets
never switches the approach"), `CAP-DLV-adaptive-development` rule 4 and the spec constitution. This proposal keeps
those boundaries:

- The skill never leaves the workflow on its own. It only announces and asks; the departure rests on the user's
  explicit per-task approval. The spec constitution already honors that ("Explicit user instructions take
  precedence"), and the second run used exactly that route.
- Selecting or installing the bundle changes nothing. `CAP-HARN-agent-guidance` and the capability's closing line
  ("Selection changes neither the development approach nor the consumer's execution authority") stay intact; only the
  user's per-task approval does, and only for that task.
- The wording is workflow-neutral: it names no `devkit-spec` policy key or stage, so it reads the same for a team
  process with no devkit workflow.

Hypothesis: announcing and asking per task gives the user the light route when it fits, keeps every departure
attributable to a user decision, and loses no defect-catching value if the loop keeps the independent checks the user
wants.

## 2. Technical Spike Questions

Planning recommendations below settle Q1 to Q6 for `plan-accept`; they are not an acceptance record.
`MAT-uiux-run-model-planning` records the option comparison, source SHA, incoming-reference inventory and limitations.
`PADR-uiux-task-approved-run` records the lasting decision and precise partial supersession.

- **Q1 — Entry and approval**: retain the owner's announced outside-workflow option. At entry, identify the task and
  say that this procedure runs outside the repository's development workflow and its process guidelines. Ask
  whether to continue for this task or follow that workflow instead, before product edits or a write-capable
  delegation. Reuse an explicit instruction already given for this task; do not ask twice. Without an answer or an
  approval channel, preserve useful read-only inspection and wait before dependent edits. Silence never selects a
  route. A review-only request still ends with findings and no product edits.
- **Q2 — Git authority**: reuse any current authorization for the task's exact effects. Otherwise present the verified
  changes and ask once for the remaining concrete Git effects before performing them. A question can cover a named
  commit and local integration together; include publication only if the user requests it. An outside-workflow
  choice alone grants none of them. Host permission checks still apply separately.
- **Q3 — Stale documents**: retain the report-only boundary. Name each consumer OOUX or UX document made stale, the
  affected statement and a concrete next action through the consumer's documentation process, where one exists.
  With no such process, propose a separate documentation task. Create no task or record and edit no such document
  during this run without a separate user request.
- **Q4 — Scope growth**: ask again before implementing a new surface or behavior beyond the approved goal, or
  changing a user constraint. A new file or an in-goal implementation choice does not by itself expand the goal.
  Pause only dependent work; keep authorized independent work moving.
- **Q5 — Checks**: on both routes, keep applicable project checks and before/after interface verification, fixing
  in-scope defects and repeating the affected check. The bundle adds no mandatory independent UX or code review;
  every review required by the selected consumer workflow remains required. Otherwise recommend the useful optional check with its purpose when structure or
  implementation risk warrants it, and report whether it ran.
  Missing tools and declined optional checks remain explicit coverage limits. No role count, mandatory review
  round or defect-parity claim is introduced.
- **Q6 — Decision scope**: partially supersede only unconditional consumer-workflow continuation and the corresponding
  pre-implementation, user-requested-action and stale-document update-routing clauses. Keep selection-neutral
  installation, product constraints, host restrictions, explicit Impeccable selection, context-file ownership, local-role limits and no implicit Git
  authority. Question/load routing stays with `PROP-uiux-improve-impeccable-routing`.

## 3. Proposed Design & Impact

### Options and recommendation

| Option | Benefit | Cost or risk | Disposition |
| --- | --- | --- | --- |
| Keep the consumer workflow for every run | Reuses existing checks, records and approval steps | Retains the reported bookkeeping cost | Supported user choice |
| Announce an outside-workflow run and obtain explicit task approval | Preserves the owner's preferred light route and makes the departure attributable | Independent review remains optional; stale documents need a follow-up | Recommended |
| Ask neutrally for either route with no announced preference | Gives both routes equal presentation | Does not express the owner's requested default; still requires a no-answer rule | Not selected |

The proposed announcement is: “This procedure runs outside the repository's development workflow and its process
guidelines. Continue for this task, or follow that workflow instead? Product constraints, host permissions and
applicable project checks still apply.” This is illustrative wording; the content and approval boundary are the
contract. “Outside” concerns workflow steps and workflow-specific records, not host controls, secrets, product
constraints or permission to publish.

### Execution and authority

- Outside the workflow, the coordinator uses the existing improvement loop: inspect, proportionate framing, useful
  independent perspectives, user choices, inline implementation or a selected Impeccable session, applicable
  project checks, before/after verification and a qualified result. It creates no competing workflow or new
  required retained record.
- Following the workflow, complete its pre-implementation, review and delivery steps as before. The chosen route
  applies equally to inline changes, accepted Impeccable changes and explicitly requested setup or cleanup.
- Choosing a route changes no configured approach or policy file. Selecting or invoking the bundle alone changes
  neither approach nor authority. Host refusals stop the operation without another access route.
- Product and design-system constraints remain in force. A departure from a constraint needs the user's explicit
  change to that constraint; a generic route approval does not supply it.
- Keep the Impeccable brief's recorded base, edit list, no concurrent coordinator edits, unchanged index/HEAD and
  acceptance checks. This proposal changes no interactive-command or skill-load route.

### Target documents and implementation

`PROP-uiux-improve-run-model-target` contains prospective capability rules, use-case branches and acceptance cases.
Development updates the capability summary and rules 3, 11, 12, 16, 17 and 19 as needed, adds bounded entry, scope and
Git-authority rules, promotes the PADR and adds exact partial-supersession pointers to the two existing ADRs. Keep
both old ADRs accepted because their other clauses remain in force.

Update the bundle's `SKILL.md`, `references/orchestration.md` and human README coherently. Apply `agent-asset-writing`
after loading authoring context before those edits. Keep all agent wording workflow-neutral: name no
`devkit-spec` policy key, workflow command or required delivery record. Extend the existing integration tests for
entry/authority, delegation and requested setup, and the installed-consumer test for independent installation.
No new runtime, package, feature dependency edge, distribution behavior or global workflow policy is in scope.

### Verification plan

| Check | Observable outcome |
| --- | --- |
| Entry contract assertions | Announcement, both choices, explicit per-task approval and prior-authorization reuse appear before product edits and write-capable delegation |
| Authority scenarios | No answer/non-interactive without prior approval causes no dependent edit; a route choice grants no Git/publication authority |
| Both-mode scenarios | Workflow choice retains its steps; outside choice keeps project checks, before/after verification and host restrictions |
| Scope and documentation scenarios | Out-of-goal surface/behavior requires a new decision; stale consumer documents are named with a follow-up and remain unedited |
| Delegation and setup assertions | Selected route applies to Impeccable and requested setup/cleanup without changing question/load routing or file permissions |
| Installed-consumer E2E | Bundle still installs without delivery packages, selection leaves the configured approach unchanged and no delivery records are created |
| Repository verification | Relevant lint/type checks and `just test-affected` with full fallback; include the existing app-uiux-improve installed-consumer E2E |

Empirical consumer and host trials are best effort for this personal project. Unavailable live runs are reported
as unverified coverage rather than an acceptance gate; deterministic document/rule checks and the required review
procedure still apply.

These are instruction and distribution checks. They do not prove model obedience, design quality, lower latency or
equal defect detection. The two recorded pilots are confounded; no comparative performance gate is proposed.

## 4. Lifecycle & Retirement Criteria

- Before acceptance: present this committed proposal, its PADR, target draft, Scout/Challenger findings and unverified
  areas. Existing Living Spec contracts stay in force throughout Planning.
- On acceptance: the Host uses `devkit spec proposal accept-plan` under the exact current approval policy. Development
  handoff and integration remain separate effects with their own authority. On handoff the decision becomes an ADR,
  this proposal retires and `MAT-uiux-improve-second-pilot` plus `MAT-uiux-run-model-planning` move with their IDs.
- Delivery order remains this proposal, `PROP-uiux-improve-impeccable-routing`, then
  `PROP-uiux-improve-bundle-hygiene`. Overlapping Development and handoff run sequentially.
- On rejection: retain `status: rejected` with the user's reason in the commit message; follow the normal rejection
  and feedback-retirement procedure before deletion.
