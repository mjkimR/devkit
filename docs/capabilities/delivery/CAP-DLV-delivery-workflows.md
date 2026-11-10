---
id: CAP-DLV-delivery-workflows
title: Delivery Workflows
summary: "SDD stages retain eligibility checks and historical records without task-intent approval. Later boundaries govern delivery; workers retain scope, the Host accepts verification and git-operator executes authorized lifecycle effects."
area: delivery
status: active
created_at: 2026-10-13
usecases:
  - UC-route-development-intent
  - UC-plan-and-hand-off-a-proposal
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
  - packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py
  - packages/devkit/src/devkit_agt/features/integration/cli.py
  - packages/devkit-spec/src/devkit_spec/features/worker/cli/commands.py
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/isolated-execution.md
---

# [CAP-DLV-delivery-workflows] Delivery Workflows

## 1. Summary

The `spec` bundle ships one devkit workflow definition per combination of `planning-depth` and `task-kind`
(`kind = "workflow"` assets in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/`), ten host-neutral role contracts
(`kind = "subagent"` assets in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/`), all in the `core` preset. devkit's workflow engine
evaluates the definitions (`CAP-DLV-workflow-orchestration`);
`devkit sync` projects the roles into each agent host's subagent directory
(`CAP-DIST-agent-projections`). The
definitions are the only source of stage order, checks, gates and returns: an executor reads them, never an ad-hoc
sequence.

## 2. Scope & Boundary

- **In-Scope**: the six definitions (layout, anchor, stages, gates, entry and exit checks, returns, declared checks),
  the approval semantics of `plan-accept`, `proposal-handoff`, `dev-integration` and the `exception` stage, the envelope kinds
  the stages require, the `activity-effort` rules of review and reconcile, the optional UX review, and Host-led branch and final verification.
- **Out-of-Scope**:
  - Role contracts, delegated work boundaries and worker inspection: `CAP-DLV-delivery-roles`.
  - Evaluating a definition, recording answers and envelopes, binding units: devkit's `devkit workflow` commands.
  - Creating and binding a spec bundle: `CAP-DLV-spec-bundles`.
  - Creating a proposal and the cross-layout handoff: `CAP-DLV-proposal-planning`.
  - The effective approval, stage, Git and routing policy: `CAP-DLV-project-policy`.
  - The procedures a stage names (the `spec*` skills), classification, Backlog, depth changes and closes:
    `CAP-HARN-agent-guidance`.
- **Non-Goals**:
  - **Scope Excluded**: conditional stages. Each classification is one workflow; a change of depth adds a Unit,
    closes the work or, for a queued draft the user reclassifies as `session` at pickup, deletes the draft in Backlog
    (`ADR-delivery-classification`), never a stage switched on by content.
  - **Scope Excluded**: a Development direction gate. Choices inside the agreed intent are the executor's; a problem
    that breaks the agreement stops the work as a problem.
  - **Scope Excluded**: a runner. Dispatching stages, the integration queue, the shared-docs write lock, retry caps,
    executing merges and declaring `lint-ci-clean` and `merged` belong to an external runner, or to the executor
    declaring them with `--given` when none exists.
  - **Scope Excluded**: runtime model routing. Distribution owns opt-in subagent model levels and shared project
    overrides (`CAP-DIST-agent-projections`); `activity-effort` determines review and verification thoroughness.


## 3. Business Rules & Policies

1. **One definition per classification**: the workflow id is `sdd-<planning-depth>[-<task-kind>]`. `session` uses
   `sdd-session-feature` or `sdd-session-bugfix`, `spec` uses `sdd-spec-feature` or `sdd-spec-bugfix`, `proposal` uses
   `sdd-proposal` until handoff and then `sdd-spec-<task_kind>`. A team review is `proposal` depth plus PR policy, not
   a workflow. The task kind `overall-refactor` has no depth and one workflow, `sdd-overall-refactor`, run in `direct`
   mode only, without a Unit, proposal or spec bundle (`ADR-delivery-classification`). A behavior-preserving work
   item agreed in a review-refactor decision round whose edited source files span more than one feature or module is
   `overall-refactor` work, and a single-module one follows the feature workflows
   (`ADR-review-refactor-application`, `CAP-DLV-review-refactor`). The axes are not stored as
   fields: the Unit's kind and the bound workflow show them.
2. **Definitions are authoritative**: an executor MUST take stage order, checks, gates and returns from
   `devkit workflow show <id>` / `devkit workflow show --unit <dir>` and `devkit workflow next --unit <dir>`. The
   Markdown body of a definition keeps only rules the schema cannot express.
3. **Shared stages are identical**: a stage id used by several definitions MUST have the same exit checks, gate,
   role, isolation, skills and artifacts in each; `devkit workflow validate` with no arguments reports a difference
   as `SHARED_STAGE_MISMATCH`. Returns are each workflow's own.
4. **Gates are named `<activity>-<decision>`**: `plan-accept`, `proposal-handoff` and `dev-integration`; the `exception`
   stage belongs to no activity. Numbered gate names are not used.
5. **Decision boundaries and authority**: `plan-accept`, `proposal-handoff`, and `dev-integration` independently permit
   `ask` or `auto`, default `ask`. User decisions are explicit; policy delegation is reported as policy, never fabricated
   user consent. `accept --by user|policy` records acceptance and status together; `policy` requires the retained
   base's `plan-accept=auto` policy. Planning merge is an acceptance effect, not Development result acceptance. Under
   `ask`, the Host may combine acceptance and handoff in one conversation, then invokes the CLI. Verified local effects still obey readiness, exact report,
   SHA, worktree, cleanup and environment guards; publication and host permissions remain separate.
   `workflow return` voids the stage and later decision records and envelopes. Policy delegation never disables checks.
6. **Explicit task authorization**: an explicit instruction MUST authorize the task's goal, scope, verification,
   `task-kind` and `planning-depth` before work starts. SDD workflows MUST NOT declare an intent approval gate or
   create intent approval records. Intent stage IDs, non-gate checks and return targets remain stable. Existing
   valid intent decisions remain inert history without migration. A handed-off spec retains only plan-accept as
   an acceptance audit record (`ADR-remove-plan-intent-gate`, `CAP-DLV-proposal-planning` rule 12).
7. **No Development direction gate**: Development starts from the agreed intent. Implementation choices inside it
   are made with the recommended option and recorded; a non-blocking improvement is reported as feedback (a
   follow-up draft proposal is also allowed); only a problem that cannot be solved without changing the agreed goal,
   scope or contract stops the work. At `high` the review loop also stops it (rule 15,
   `ADR-review-loop`): a batch that is not minor at the cap round, a recurring P1, and a P1 the
   implementer holds invalid that the reviewer asserts again after one more round given the counter-evidence are each
   a `problem` in the run's `worker` envelope (the contested one with the disagreement and the evidence). The Host
   owns the recovery within the authorized goal, scope and constraints, and recovery adds no user approval gate; it
   closes a contested P1 only with evidence that its failure condition does not apply under the agreed contract, and
   changing an acceptance criterion or waiving an agreed constraint needs the user's decision. A Host-directed
   recovery gets one further fresh round outside the cap, named by its `resolution` envelope. A session reports a cap
   or recurrence hand-over in the conversation and does not integrate, and the Host resolves a contested P1 against
   the agreed contract; none of this is the `exception` stage. A worker records it and ends; the Host decides
   recovery or a close. There is no return from Development to Planning.
8. **`dev-integration` is per integration unit** (one pull request): it has no exit checks of its own and is asked as
   soon as `integration-approval` is current, that is once the final change report holds. Under `auto` it passes only
   after the path's required review, reconciliation and checks pass, at every `activity-effort`, `low` included.
   Docs reflection and conflict resolution within the approved intent need no re-approval.
9. **Living Spec before `dev-integration`**: the Living Spec reflection, a resolved `reconcile.md` and
   `status: completed` of the anchor MUST be complete before the gate; an optional review feedback breakpoint between
   `review-refine` and `living-spec-draft` adds no stage, check or approval file. The reflection includes the owning root or namespace `steering/glossary.md`,
   where it exists, when the change introduces or renames a domain term (`spec-sync`, first step), and, when `spec.md`
   has a Screens section, each drafted screen written to `docs/ux/`, its step citations in the use cases and its
   register rows in the owning root or namespace `steering/ux-objects.md`, each a `reconcile.md` target (`ADR-ux-screens`).
   Per-feature `spec-sync` reflects the core contract delta. The separately invoked maintenance playbook in
   `CAP-DLV-drift-reconciliation` reviews accumulated drift in a bounded batch; it adds no delivery stage or
   scheduler. Each mismatch needs the user's explicit disposition before corrections enter this workflow.
10. **Integration is a stage, not a persona**: its code authority is limited to conflict resolution and the
    verification that needs; its docs authority is the reflection the approved change requires. It re-verifies only
    what conflict resolution and docs reflection changed and does not restart code review.
11. **Exception stage**: every workflow has the out-of-band `exception` stage, entered on `exception-raised` and left
    on `exception-handled`, both `human` checks, without a gate. It distinguishes three failure kinds: retry cap
    exceeded, execution or tool failure, unresolved semantic conflict. A problem the Host handles itself never goes
    through it.
12. **Bugfix evidence order**: a reproduction precedes the fix. In `sdd-spec-bugfix` a `red` envelope
    (`checks.reproduced`) precedes a `green` envelope (`checks.resolved`, `checks.preserved`); in `sdd-session-bugfix`
    a failing reproduction test (`reproduce-session`) precedes the fix and the Red then Green evidence is in the
    session report. A compile, environment or test-setup failure unrelated to the defect is not reproduction evidence.
13. **A session has no unit and no artifacts**: `sdd-session-*` declare no layout and no stage or exit check that
    requires a Unit, envelope, spec, reconcile document or gate record file, at every `activity-effort`. They are not
    evaluated by `devkit workflow next`; the executor follows their stages from `devkit workflow show <id>` and reports
    the change, effort, review result, verification and remaining constraints in the final response or PR body. A
    lasting design record, contract change or Living Spec change raises the depth to `spec`.
14. **Proposal Planning ends at handoff** (`CAP-DLV-proposal-planning`): `sdd-proposal` declares no `next`
    candidates, because devkit's `devkit workflow handoff` rebinds a unit in place and refuses a candidate with
    another anchor (`HANDOFF_LAYOUT_MISMATCH`). Once `plan-accept` holds, `next` reports the unit complete
    (`[STAGE: - complete=yes]`, no `[HANDOFF]` line) and Development starts with `devkit spec proposal handoff <slug>`.
    An eligible draft may skip Planning by a **direct acceptance** (`ADR-proposal-acceptance`):
    Backlog work on the base checkout, under every pull-request policy, where the Host sweeps its own acceptance
    session at `collect-feedback` and records `plan-accept` with `devkit spec proposal accept <slug> --by user
    --direct --note "<reason>"`, without `reviewing`. It has no Planning branch, run, `activity-effort` or `worker` envelope; the
    stage schema is unchanged, and the request shows "Planning: skipped (direct acceptance)" where a Planning
    acceptance shows its effort record.
15. **`activity-effort` sets the review, never the floor**: Development of a spec unit reviews at `low` by the author
    (stated as self-review in the envelope), at `medium` with one mandatory initial `code-reviewer` pass regardless
    of size and a separate `reconcile-reviewer` check, at `high` with both reviewers in the bounded review loop below.
    Only medium permits omitting the initial reconcile reviewer when all affected contracts and documents are
    identified, agreement with the actual diff is directly demonstrated, and no unresolved contract interpretation or
    cross-component impact remains (behavior or agent-facing text changed in more than one package, in more than one
    capability area, or in a package and the repository tooling; the change's own Living Spec reflection and
    references updated elsewhere do not count). The implementer then records a self-check, omission reason and
    verification evidence in `reconcile-check`; small size alone is insufficient. At medium the implementer verifies
    fixes and subsequent changes and decides repeat calls, considering expanded scope, uncertain correctness and
    contract interpretation. A failed or stale initial call is not required-review evidence. These choices do not
    change the effort, stages or required policies (`ADR-review-loop`).
    The implementer always writes, fixes and resolves the Living Spec reflection and `reconcile.md`; the
    verification at every effort is a `reconcile-check` envelope the `living-spec-draft` exit reads, so its findings
    are fixed in the reconcile and never reopen `review-refine`.
    At `high`, code review, reconcile verification and Planning criticism run in rounds. Each round is a fresh
    reviewer given the earlier rounds' findings, the round's diff scope and the effort: round 1 covers the whole
    change, each later round every fix since the previous round, never a subset. The implementer fixes every finding
    of a round together (a `P2` or `P3` may be waived with a reason) and closes the round with `reverify` (for
    Planning, a reverify of the `challenger-NN` round, written after each fold at `medium` too) or a new
    `reconcile-check`; a P1 the implementer holds invalid stays open
    there with its counter-evidence and sends the batch to the next round. The loop ends when a round finds nothing, or
    when every fix of the batch is minor (confined to the named location, a text-only or prescribed edit, no contract
    change, shown by a test or by the diff) and is self-verified with its reason and evidence; the initial reviewer
    calls, the first reconcile verification included, are never replaced by a self-check, and a recurring finding is
    never self-verified. Each round's summary starts with `round <N>;`; the cap is 3 rounds after the initial one and
    is not reset by `devkit workflow return` within a segment. Each loop counts its own kind; a round without the
    marker counts, in sequence order, only before the loop's first marked round and only when a `worker` envelope of
    the segment written before that marker records `activity_effort: high`; the higher number holds when a marker
    disagrees with that count, a `reverify` is never a round, and a fold of the user's answers is a new batch of the same loop that gets at most one
    fresh round outside the cap (`ADR-review-loop`). A batch not minor at the cap round and a recurring P1
    (`recurs:` at the start of the reviewer's `issue`) stop the work (rule 7). Recurrence means the same failure
    condition remains after an attempted fix, including an incomplete fix, or returns; the reviewer names the earlier
    finding and explains the shared failure condition. A distinct defect introduced by a fix is a new finding:
    sharing a file, topic or cause alone is insufficient, and a different remedy does not reclassify an unresolved
    earlier failure. Existing severity, minor-fix and round-cap conditions apply to both. A finding whose `evidence` path is not
    in the round's diff file list is out of scope: it is fixed with the batch and never counts as a recurrence; a
    `challenger` finding whose `suggested_action` starts with `Decision needed:` stays out of the loop and goes to
    `plan-accept`. The procedure ships in the `spec`
    skill's `references/review-loop.md`.
    Every finding of a `review`, `reconcile-check` or `challenger` envelope carries `severity` `P1`, `P2` or `P3` at
    every effort, with one `P1` definition per review kind (a contract or acceptance-criterion violation, a missing or
    contradicting reflection, a failing or conflicting design); the reviewer sets it, the implementer records it
    unchanged, and it affects no check (`CAP-DLV-workflow-envelopes`).
    A session reviews at the same levels but its reviewer returns a message and nothing is written; when `high` is
    proposed for a session, the proposal advises `spec` depth for work that creates or changes a contract or a
    document kind and `proposal` depth for work that reverses an accepted decision. Proposal Planning runs
    questions only at `low`, one `challenger` pass at `medium` (a `scout` when the direction needs evidence) and, at
    `high`, two or more options compared, a `scout` starting from `devkit docs refs <ID> --direction in` for each
    capability and ADR the proposal touches, then `challenger` rounds of the same loop. A proposal scaffolds
    non-authoritative `planning_effort` and `dev_effort` hints (`low` | `medium` | `high`, default `medium`) in
    `proposal.md`: `planning_effort` is stated at intake and pre-fills Planning start, `dev_effort` is
    refined during Planning before `plan-accept` and returned by `handoff` to pre-fill Development start, while the
    confirmed `activity-effort` of each run is recorded only on its `worker-NN.yaml` envelope (with any override reason
    in `summary`). The effort is always proposed with a reason when the activity starts, and the `plan-accept`
    request shows each Planning run's effort, the refined `dev_effort` hint and the support-role envelopes present,
    naming a `challenger`, or a `scout` at `high`, that the effort required and no envelope shows, and each
    `challenger` round with the `reverify` that closes it, and each `ux-review` round with its open findings, which
    the user decides there. Gates, exit checks and `required` policies hold at every effort.
    The UX review (`ADR-ux-screens`) is an optional delegation before code, never a stage or a gate: the
    isolated, read-only `ux-reviewer` runs `spec-ux-review` on drafted screens (`ADR-ux-screens`) in
    Planning (recorded at `spike`) or, at spec depth, after the Screens section of `spec.md` is written and before the
    plan (inside `specify` before `spec-plan`, or `characterize` before `plan-tasks` for a bugfix, recorded at that
    stage). It walks each linked use case's main scenario and extensions through the screens and scores each screen
    0, 1 or 2 on six rubric items with evidence for every score below 2; it checks the link-rule items on the drafts
    by hand as its own judgment, outside the rubric. Its findings carry no severity and stay out of the review loop;
    a unit has at most two rounds. In Development the implementer closes the last round with a further `ux-review`
    envelope marking each finding `resolved` or `waived` with a reason. The effort table recommends one round at
    `medium` and `high` when screens change; a `session` task applies the `ux-writing` instruction and runs none.
16. **Only the workers write to Git**: a read-only role never stages or commits (`x-git-actions: [read]`). The two
    workers (`[read, commit]`) commit on their activity branch, write their own records and never push, merge, rebase,
    reset or amend (`ADR-orchestration-workers`).

17. **Stage commits and record-only opt-in**: WHEN a stage boundary is reached, the executor MUST persist its changes with ordinary Git hooks. For one fully authored envelope as the sole pending file, it MAY use `devkit workflow envelope commit --unit DIR --file envelopes/NAME.yaml` (`CAP-DLV-workflow-envelopes`). Review/reverify, final-report and feedback with no findings are eligible after their associated work is committed. Accompanying source/document changes, multiple records, Planning returns, acceptance/decision transactions and problem/emergency work keep their required combined manual commits. Evidence SHAs remain unchanged. Integration preparation follows record commit; changed HEAD invalidates older preparation. A known Git/hook/signing failure uses same-file retry after fixing the cause, while uncertain effects require inspection. This adds no approval, push or merge authority. Source guidance checks: `packages/devkit-spec/tests/integration/bundles/spec/test_envelope_commit_guidance.py`.

## 4. Interfaces & Data Contracts

### 4.1 Workflow Catalog

| Workflow | Classification | Layout (`work_dir` / `unit_path`) | Anchor | Gates |
| --- | --- | --- | --- | --- |
| `sdd-session-feature` | `session` × `feature` | none | none | `dev-integration` |
| `sdd-session-bugfix` | `session` × `bugfix` | none | none | `dev-integration` |
| `sdd-overall-refactor` | `overall-refactor` (no depth) | none | none | `dev-integration` |
| `sdd-spec-feature` | `spec` × `feature` | `specs` / `{date:%Y-%m}/{date:%Y%m%d}-{slug}` | `spec.md` | `dev-integration` |
| `sdd-spec-bugfix` | `spec` × `bugfix` | `specs` / `{date:%Y-%m}/{date:%Y%m%d}-{slug}` | `spec.md` | `dev-integration` |
| `sdd-proposal` | `proposal` (either kind) | `docs/proposals` / `PROP-{slug}` | `proposal.md` | `plan-accept` |

Each definition with a unit sets its own `layout`, so spec bundles and proposal bundles live where the document model
expects them and `devkit workflow list` finds both. `schema_version` is `1` in every definition.

### 4.2 Stages

`devkit workflow show <id>` is the authoritative list; in order (gate in parentheses):

- **`sdd-session-feature`**: `intent-session`, `execute-verify`, `report-session`, `approval-session`
  (`dev-integration`), `commit-session` (exit `lint-ci-clean`), `merge` (exit `merged`).
- **`sdd-session-bugfix`**: `intent-session`, `reproduce-session`, then the stages of `sdd-session-feature` from
  `execute-verify` on.
- **`sdd-overall-refactor`**: `intent-refactor`, `restructure`, `report-refactor`, `commit-refactor`
  (exit `lint-ci-clean`), `approval-refactor` (`dev-integration`), `merge` (exit `merged`).
- **`sdd-spec-feature`**: `intent`, `specify`, `build-verify`, `review-refine`, `living-spec-draft`,
  `collect-feedback`, `final-change-report`, `integration-approval` (`dev-integration`), `integrate`, `merge`.
- **`sdd-spec-bugfix`**: `intent`, `characterize`, `plan-tasks`, `reproduce`, `fix-verify`, then the
  stages of `sdd-spec-feature` from `review-refine` on.
- **`sdd-proposal`**: `intent-proposal` (its exit requires `size` absent or exactly `S`, `M` or
  `L`, `frontmatter(proposal.md size S|M|L|)`, so an `XL` draft shows it unmet and opens no request), `spike` (optional in the schema and never current on
  its own, but run whenever the Planning effort requires a `challenger`, rule 15, or the direction needs evidence;
  having no exit check, it may show under `[DONE]` before any review ran, which is not Planning evidence: the
  support-role envelopes recorded at `spike` are),
  `collect-feedback`, `direction-handoff` (`plan-accept`), `handoff` (no exit check, no return:
  Development never returns to Planning).

Every workflow also has `exception`. Stage details of the spec-bundle workflows:

| Stage | Entry | Exit | Role / isolation | Skills |
| --- | --- | --- | --- | --- |
| `intent` | | `anchor-exists` | developer / none | `spec` |
| `specify` | `anchor-exists` | `file-exists(plan.md)`, `tasks-exists`, `not-skeleton(spec.md)`, `not-skeleton(plan.md)`, `not-skeleton(tasks.md)`, `lint-clean` | developer / none | `spec-specify`, `spec-plan`, `spec-tasks` |
| `characterize` (bugfix) | `anchor-exists` | `not-skeleton(spec.md)`, `lint-clean` | developer / none | `spec-specify` |
| `plan-tasks` (bugfix) | `not-skeleton(spec.md)` | `file-exists(plan.md)`, `tasks-exists`, `not-skeleton(plan.md)`, `not-skeleton(tasks.md)`, `lint-clean` | developer / none | `spec-plan`, `spec-tasks` |
| `reproduce` (bugfix) | `tasks-exists` | `envelope-check-pass(red reproduced)` | developer / none | `spec-specify` |
| `fix-verify` (bugfix) | `envelope-check-pass(red reproduced)` | `tasks-all-checked`, `envelope-check-pass(green resolved)`, `envelope-check-pass(green preserved)`, `lint-clean` | developer / none | |
| `build-verify` | `tasks-exists` | `tasks-all-checked`, `lint-clean` | developer / none | |
| `review-refine` | `tasks-all-checked` | `envelope-review-passed` | code-reviewer / preferred | `spec-review`, `spec-delegate` |
| `living-spec-draft` | `envelope-review-passed` | `frontmatter(reconcile.md status resolved)`, `envelope-completed(reconcile-check)`, `anchor-status-completed` | reconcile-reviewer / preferred (verification only; implementer writes) | `spec-sync`, `spec-delegate` |
| `collect-feedback` | `frontmatter(reconcile.md status resolved)` | `envelope-check-pass(feedback swept)` | developer / none | `spec-feedback` |
| `final-change-report` | `envelope-check-pass(feedback swept)` | `envelope-check-pass(final-report tests)`, `envelope-check-pass(final-report build)`, `envelope-check-pass(final-report lint)` | developer / none | `spec` |
| `integration-approval` | the three final-report checks | none | developer / none | `spec` |
| `integrate` | the three final-report checks | `frontmatter(reconcile.md status resolved)`, `anchor-status-completed`, `lint-ci-clean` | developer / none | `spec-integrate` |
| `merge` | `lint-ci-clean` | `merged` | `-` / none | |
| `exception` | `exception-raised` | `exception-handled` | developer / none | `spec` |

For a proposal, `collect-feedback` has entry `anchor-exists` and the same exit, gate, role, isolation,
skills and artifacts as the Development stage. Feedback files and sweep envelopes live in the proposal, without
requiring a spec or reconcile record. Before every Planning return (including questions), the executor writes fresh
sweep evidence, then its single worker record. Latest-envelope checks do not enforce run freshness mechanically;
the executor validates coverage. Stage-off writes no envelope, requested-only writes policy-skip PASS, zero
observations passes, and incomplete coverage records FAIL with its gap. Rejection starts no new agent and uses the
last recorded coverage/skip/gap. A rejected proposal may show an unmet collect-feedback check; it is ended work, not
an instruction to start another sweep. A direct acceptance has no Planning run: the Host's sweep covers the acceptance
session, under the same policy, before `devkit spec proposal accept --direct`; a draft deleted for a session
reclassification preserves its open feedback like a rejection's cleanup. Handoff drops Planning envelopes; Development
runs its own sweep.

The `spike` stage of `sdd-proposal` delegates to the `scout` role (isolation `preferred`, skill `spec-delegate`) and
writes into the proposal's `materials/`; `scout` and `challenger` returns are recorded as envelopes at
`spike`. The `report-session` stage of a session runs `spec-review` and, unless
`collect-feedback` is switched off, `spec-feedback`; it runs no `spec-sync`, because a session has no reconcile record.

### 4.3 Gates

| Gate | Stage(s) | Approval key (`[workflow.approvals]`) |
| --- | --- | --- |
| `plan-accept` | `direction-handoff` | `ask` or `auto` |
| `proposal-handoff` | none: `devkit spec proposal accept --mode accept_and_handoff` and `devkit spec proposal handoff --effort` read it | `ask` or `auto` |
| `dev-integration` | `integration-approval`, `approval-session` | `dev-integration` (`ask` or `auto`) |

- A gate waiting for the user: `devkit workflow next` prints `[WAITING: human gate:<gate>]` with a
  `[REQUEST: id=gate:<gate> ...]`. A `plan-accept` acceptance is `devkit spec proposal accept <slug> --by user`
  (`--direct` for a direct acceptance), and a decline of plan-accept `--action decline --by user --note "<reason>"`. A
  `dev-integration` OK is `--given dev-integration` on every later `next`, and an objection about the change takes the
  stage's return path; where a runner binds `gate:dev-integration` to PR state, the PR ready state answers it. Every
  definition with that gate declares `gates: {dev-integration: {answer: given}}`, so `next` ends its `[REQUEST]` with
  `answer=given`.
- `dev-integration = "auto"`: the gate passes by policy; its stage never stays current, so `next` lists it as
  `[GATE_PASSED: dev-integration stage=integration-approval policy=auto source=policy]` (JSON `passed_gates`), the basis
  every report cites.
- `--given <gate>` asserts a gate for one run (a runner's binding).
- The workflow definitions fix the policies each stage gate accepts (`gates.<gate>.policies`):
  `plan-accept` and `dev-integration` take `ask` or `auto`. A configured policy outside them stops every devkit workflow
  command that evaluates the unit with `WORKFLOW_GATE_POLICY`. `proposal-handoff` is declared by no stage, so workflow
  commands never check it. `devkit spec policy` and the spec commands that read an approval policy refuse any of the
  three boundaries outside `ask` or `auto` with `SPEC_CONFIG_INVALID` (`CAP-DLV-project-policy`).
- `plan-accept` is asked only for a proposal in review, or for a draft once a direct acceptance wrote
  `status: accepted`: the `direction-handoff` exit is `frontmatter(proposal.md status reviewing|accepted)`, so a draft
  otherwise, or a rejected proposal, gets no request. A `plan-accept` acceptance is recorded with
  `devkit spec proposal accept`. Under `plan-accept = "auto"` the gate passes by policy and `handoff` has no exit,
  so once feedback is swept `next` prints `[STAGE: - complete=yes]` for a `reviewing` proposal before any
  acceptance ran. A Planning run in that state records its `worker` envelope at `direction-handoff`, never
  `handoff` or `-` (the `spec` skill's `worker-records.md`): open questions recorded there hold `plan-accept`, so
  the composed acceptance refuses with `SPEC_PROPOSAL_APPROVAL_NOT_READY`, and the run records no acceptance or
  handoff effect.

### 4.4 Checks

| Check | Class | Meaning |
| --- | --- | --- |
| `anchor-exists` | devkit | `file-exists(spec.md)` under the spec layout, `file-exists(proposal.md)` under the proposal layout. |
| `file-exists(plan.md)` | devkit | The bundle has `plan.md`. |
| `tasks-exists`, `tasks-all-checked` | devkit | `tasks.md` exists / every task is checked. |
| `not-skeleton(<file>)` | devkit | The file no longer carries `<!-- devkit:skeleton -->` (`CAP-DLV-spec-bundles`). |
| `lint-clean` | devkit | `devkit rules` (linter phase) passes on the unit's files. |
| `frontmatter(<file> <key> <value>)` | devkit | A frontmatter value, e.g. `frontmatter(reconcile.md status resolved)`. |
| `anchor-status-completed` | devkit | The anchor has `status: completed`. |
| `envelope-review-passed` | devkit | The latest review round passed (review, then reverify). |
| `envelope-check-pass(<kind> <key>)` | devkit | The latest envelope of the kind has `checks.<key>` starting with `PASS`. |
| `lint-ci-clean` | declared `runner` | `devkit rules check --ci --base <ref>` passes on the committed head; the Developer runs it after the commit and CI re-runs it. |
| `merged` | declared `runner` | The integration unit is merged into the base branch. |
| `exception-raised`, `exception-handled` | declared `human` | A retry cap, tool failure or unresolved semantic conflict was raised / its cause was handled by the user. |

Runner checks are never evaluated by `next`; they are declared with `--given lint-ci-clean` / `--given merged` once
CI and the merge (or, without a runner, the local cumulative check) report. `revision-ancestor(red green)` is
available to a project that wants stricter bugfix ordering.

### 4.5 Envelopes

Envelopes are devkit envelope files under a unit's `envelopes/`, written with
`devkit workflow envelope new --unit <dir> --kind <kind> [--stage <id>] --summary "..." [--check <key>="PASS ..."]
[--base <ref>] [--head <sha>] [--assume ...] [--unverified ...]` (kinds `review`, `reverify`, `worker`, `answer` and
`resolution` through `devkit workflow envelope <kind>` instead, which takes the same flags and those of the kind) and validated with
`devkit workflow envelope check --unit <dir>`; a malformed envelope never satisfies a check. A session writes none.

| Kind | File | Written by |
| --- | --- | --- |
| `review`, `reverify` | `envelopes/review-NN.yaml`, `envelopes/reverify-NN.yaml` | the reviewing executor; reverify closes the review round, and in Planning the executor's reverify (`--from envelopes/challenger-NN.yaml`, `review: challenger-NN.yaml`) closes a `challenger` round |
| `red` | `envelopes/red-NN.yaml` (`checks.reproduced`) | the implementer |
| `green` | `envelopes/green-NN.yaml` (`checks.resolved`, `checks.preserved`) | the implementer |
| `feedback` | `envelopes/feedback-NN.yaml` (`checks.swept`), in the proposal or spec Unit | the executor; each Planning run supplies fresh coverage |
| `final-report` | `envelopes/final-report-NN.yaml` (`checks.tests`, `build`, `lint`) | the implementer |
| `challenger`, `scout` | role returns | the caller, from the role's fields; a `challenger` round is closed by a `reverify` |
| `ux-review` | `envelopes/ux-review-NN.yaml`, the `ux-reviewer`'s round outside the review loop (no severity, at most two rounds), recorded at `spike`, `specify` or `characterize`; read by no check | the caller, from the role's fields; in Development the implementer closes the last round with a further `ux-review` marking each finding `resolved` or `waived` |
| `reconcile-check` | the reconcile verification at `living-spec-draft`, read by its exit (`envelope-completed(reconcile-check)`) | the implementer: self-check at `low`, reconcile-reviewer's returned fields at `medium`/`high`, medium self-verification of the initial check or `high` self-verification of a minor-fix batch under rule 15; identify verifier, evidence, any initial omission reason and, at `high`, the `round <N>;` marker |
| `worker` | one run's result, exactly one per run: the applied `activity-effort`, the run's `questions` (status `needs_input`) and its `problem` (`cause`, `attempts`, `recovery`; `failed` requires it) | the run itself: a worker, the Host in `direct`, or the Host for a range it blocks |
| `answer` | the rewritten answers to a run's questions (`answers_to: worker-NN.yaml`), one decision per question, and the run's `assumptions` the user settled (`settles`, by 1-based position; an answer may hold settles alone) | the run that processes them, first, in a commit of its own |
| `resolution` | the fix of a run's problem (`resolves: worker-NN.yaml`, `summary`) | whoever actually fixed it, with the fix |

A unit is held while a `worker` envelope's problem has no `resolution` naming it (blocked) or a question has no
`answer` (waiting): devkit passes no gate, by any source, and `devkit worktree finish --merge` refuses the branch
(`WORKTREE_BLOCKED`); a pull request merges only while `devkit workflow envelope check --format json` reports
`"blocked": false` and no `pending_questions`. Unanswered questions are `choose` requests
(`question:worker-NN.<id>`, `answer=envelope`) that `devkit workflow answer` refuses. Formats and roles:
`ADR-orchestration-workers`.

A role returns `status` (`completed`, `needs_input`, `failed`), `summary`, `findings` (`issue`, `evidence`,
`failure_condition`, `suggested_action`, and `severity` `P1`, `P2` or `P3` on every `review`, `reconcile-check` and
`challenger` finding, rule 15), `assumptions`, `unverified_areas`, `checks` and `diff_scope`. Docs impact
has no envelope key: it lives in `reconcile.md`.

### 4.6 Role Contracts

`CAP-DLV-delivery-roles` owns the ten role contracts (§4.1), reusable lifecycle executor (§4.1.1), one-shot activity
workers (§4.1.2) and worker-result inspection (§4.2). Stage assignments and review effort remain defined here.

### 4.6.1 Reusable lifecycle execution

`CAP-DLV-delivery-roles` §4.1.1 defines reusable git-operator dispatch, authority and effect checks.

### 4.6.2 One-shot activity workers

`CAP-DLV-delivery-roles` §4.1.2 defines activity-worker execution, write admission and acceptance boundaries.

### 4.7 Executor Commands (devkit)

| Command | Use |
| --- | --- |
| `devkit workflow next --unit <dir> [--given <check>]...` | Current stage, unmet checks, `[NEXT_SKILL]`, `[WAITING]`, `[DELEGATE]`, `[SKIPPED]`. |
| `devkit workflow show <id>` / `--unit <dir>` | Render a definition. |
| `devkit workflow answer --unit <dir> --request gate:<gate> --action accept\|decline --by user` | Record a custom gate decision, or decline `plan-accept`. |
| `devkit spec proposal accept <slug> --by user [--note <text>] [--direct --note <reason>] [--check]` | Record a `plan-accept` acceptance with `status: accepted` in one step; `--direct` for an eligible draft on the base (`CAP-DLV-proposal-planning`). |
| `devkit workflow return --unit <dir> --to <stage>` | Go back within the activity; voids later approvals and earlier envelopes of those stages. |
| `devkit workflow bind --unit <dir> --workflow <id>` | Bind an unbound unit, or change its workflow. |
| `devkit workflow validate` | Validate definitions; `SHARED_STAGE_MISMATCH` across definitions. |
| `devkit workflow list` | List units of every layout. |
| `devkit workflow envelope worker\|answer\|resolution --unit <dir> ...` | A run's record (`--stage` and `--effort` always; `--questions-file`, `--problem`, `--tried`, `--recovery`), its answers (`--answers-to`, `--answers-file`, `--settle`) or a fix (`--resolves`). |
| `devkit workflow envelope check --unit <dir> [--format json]` | Malformed envelopes and the hold: `[BLOCKED]`, `[PENDING_QUESTION]`; `blocked`, `problems`, `pending_questions` in JSON. |
| `devkit worktree start <branch> [--no-worktree \| --existing-branch <branch> --unit <dir>]` | Start `plan-<slug>` or `dev-<slug>` in a worktree or the current checkout, or continue an existing branch after devkit-spec's attach check (a `plan-` attach refuses a rejected or `needs_decompose` proposal and one not `accepted` whose `size` is not absent or `S`, `M` or `L`). |
| `devkit worktree finish <branch> [--merge [--local-only]]` | Land the branch on the base as a merge commit, or a fast-forward under `[worktree] merge = "ff-only"` (skipping `fetch`/`push` when `--local-only`), remove the worktree, delete the branch when `delete_branch=yes`, and run the post-finish extension. |
| `devkit worktree status --stale` | Activity branches idle beyond `[worktree] stale_after`; also warned by `devkit rules check -p hygiene`. |

### 4.8 Branch verification and final landed verification

1. **Branch checks.** Before approval, the Host MUST run the source runtime's required tests, lint/types, rules and
   workflow/envelope checks. Unresolved problems, pending questions and incomplete stage evidence hold integration
   at this Host boundary. Generic integration parses none of those source records.
2. **Final verification.** After confirmed Git landing and its scoped cleanup, the Host MUST synchronize the target
   environment from landed dependency declarations and invoke fresh processes. It synchronizes bundles, regenerates
   stale tracked artifacts and commits regeneration before running required final checks against the resulting HEAD.
3. **Completion evidence.** The Host MUST report checked HEAD, commands and outcomes before reporting delivery
   complete. The merge CLI's `verification=pending` and successful exit are not proof of external checks. A moved
   HEAD requires inspecting the added changes and refreshing affected checks.
4. **Recovery.** IF setup, imports or final checks fail, THEN delivery MUST remain unfinished. The Host repairs the
   target within agreed scope and rechecks without merge replay or automatic rollback. Direct project test commands
   may diagnose a broken wrapper; required rule/workflow checks still require repairing the tool.
5. **Batching.** The Host MUST save the target SHA before the first merge and use it for final affected-test selection,
   preserving full fallback and required frontend checks. A local-orchestrated batch MAY run final checks once after
   all selected merges and in-scope repairs. Every landed unit remains pending until the combined HEAD passes.
6. **Acceptance.** Proposal acceptance retains direction eligibility and explicit authority, but composed acceptance
   yields before handoff. The Host verifies the accepted landing and invokes handoff in a fresh process with the
   unchanged authorized scope, mode and effort (`CAP-DLV-proposal-planning`).

The local-orchestrated Host MUST own post-integration asynchronous launch, collection, cleanup and final
integrated coverage. Development workers MUST run required native checks synchronously in their assigned
worktree, including necessary selective E2E, and return source-specific evidence. Worker payloads MUST NOT
inherit the Host exec lifecycle; common completion guidance routes to it only for the Host after landing.
Direct/session work retains native verification. Actor and task select responsibility, not directory location;
the executor CLI has no role or cwd restriction. Rendered local/cloud and worker-projection regression tests in
`packages/devkit-spec/tests/integration/bundles/spec/test_isolated_execution_guidance.py` check instruction routing;
actual agent compliance is Review only. `ADR-verification-execution-ownership` records this boundary.

Before choosing asynchronous verification, the Host inspects repository documentation, scripts, runner configuration and CI for actual required commands and coverage. It establishes independently runnable groups and verifies what the retained synchronous command excludes and what the asynchronous command covers, preserving all existing required coverage. Directory names and test labels establish neither E2E existence, cost nor independent runnability. If verification is unseparated, unclear or has no independently runnable subset, the Host keeps the existing required commands synchronously. Consumers need no E2E tier; guidance neither manufactures empty coverage nor automatically restructures verification. Overlapping broad commands do not establish reduced blocking by adding a duplicate E2E run. Devkit's selector commands are its own adoption example.

Where independent required groups are established, local-orchestrated use keeps the project's known synchronous group synchronous and selected required E2E MAY run through `CAP-HARN-isolated-execution` while independent work continues. The Host records baseline B, tested SHA A and outstanding coverage; an ancestor pass never attests a later HEAD. Required final E2E passes at current landed HEAD or an explicit empty selection covers its complete uncovered interval, including generated repairs. At the next failed/unknown result check, hold further merges and prioritize repair. Background `wait --clean` composes observation and eligible cleanup, while execution tools own notification delivery and the Host owns acceptance. One outstanding run is the starting recommendation, not an executor policy.

`ADR-post-merge-verification` records this boundary. Guidance regressions in
`packages/devkit-spec/tests/integration/bundles/spec/test_moved_target_guidance.py` check the sequence; the Host's
execution of external project checks is review-only, not enforced by the merge CLI.

## Source feedback at completion

`ADR-feedback-lifecycle-ledger` defines promoted and resolved as terminal routes: promotion transfers tracking to
identified follow-up work; resolution closes a direct verified fix without promotion. Only open feedback needs action.
Task entry preserves source FB IDs and scope through handoff and drafting. Terminal references require no completion
disposition or re-verification and do not implicitly authorize source writes. Completion of follow-up work never
converts promoted sources to resolved.

Before recording feedback, search existing feedback of every status and act on matching results. The user-invoked `feedback-consolidation` playbook deletes eligible resolved feedback and its aliases, while retaining other terminal outcomes in consolidated records with aliases. Active references and incomplete or unmerged work protect feedback from deletion. A recurrence after deletion is recorded as a fresh observation; Git history retains the originals (`ADR-feedback-lifecycle-ledger`, `CAP-HARN-agent-guidance`).

At `living-spec-draft`, review only explicit open direct-fix sources against implementation and verification and
record outcomes in `reconcile.md`. At `report-session`, do the same before committing and report outcomes without
a new artifact. Record outcome and evidence for resolutions; incomplete or unverified direct fixes stay open.
Include source files needing updates in task/delegation boundaries; otherwise the Host applies their dispositions.
Recheck only resolutions newly made by this task if later changes invalidate evidence. This obligation is independent
of capture settings and collect-feedback policy and grants no integration authority or additional workflow gate.

Local Development starts use `devkit spec proposal handoff` after the Host presents the accepted proposal, current
report and worktree/setup effects and receives conversational approval under `ask`. The command returns the selected
effort as the run input; the worker envelope records that effort. Under `auto`, the command reads the policy from the
retained base and uses the proposal's declared `dev_effort`. Final integration retains its separate gate.

## Worker result inspection

`CAP-DLV-delivery-roles` §4.2 specifies `devkit spec worker inspect`, its inputs, scope evidence, result schema and
read-only limits. The Host's acceptance authority remains independent of that informational helper.

## Shared document context

SDD guidance MUST load `devkit get-context docs` before using document contracts. The docs bundle owns shared
authoring instructions and templates; spec retains lifecycle gates, immutable decision supersession and completed
spec preservation. Installing devkit-spec auto-selects both core bundles. Explicitly removing docs requires
`devkit add docs` to restore the supported SDD selection (`ADR-document-system`).


## Adaptive development applicability

WHILE the common approach is `adaptive-dev`, SDD spec/proposal creation, proposal acceptance and handoff MUST refuse
before mutation with `SPEC_LIFECYCLE_INACTIVE` (exit 2). The action points to shared policy inspection and an explicit
SDD choice; it does not suggest bypassing checks. Both direct public operations and composed worktree/acceptance
operations enforce the boundary. Generic workflows, read-only policy/scope/worker inspection and document lookup
remain usable. `packages/devkit-spec/tests/integration/features/policy/test_adaptive_dev.py` covers these refusals.

The installed attachment extension leaves generic non-SDD Units to generic validation in adaptive development and preserves
its SDD checks for explicitly SDD-bound Units. Scoped cleanup retains its no-bundle default; adaptive development may retain
cleanup for concretely recorded SDD ownership. Mode changes grant no broader cleanup authority.
