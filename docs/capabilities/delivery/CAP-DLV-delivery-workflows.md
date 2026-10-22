---
id: CAP-DLV-delivery-workflows
title: Delivery Workflows
summary: "Five delivery workflows define stages, gates, checks, bounded reviews and run records, verified source-feedback resolution, integration readiness, informational committed worker-result inspection, and native Codex workers with emulated boundaries and scoped approvals."
area: delivery
status: active
created_at: 2026-10-13
usecases:
  - UC-route-development-intent
  - UC-incubate-and-hand-off-a-proposal
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
  - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py
---

# [CAP-DLV-delivery-workflows] Delivery Workflows

## 1. Summary

The `spec` bundle ships one devkit workflow definition per combination of `planning-depth` and `task-kind`
(`kind = "workflow"` assets in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/`), six host-neutral role contracts
(`kind = "subagent"` assets in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/`), all in the `core` preset, and the
`devkit_agt.features.integration.readiness` provider `spec` (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py`). devkit's workflow engine
evaluates the definitions (`CAP-DLV-workflow-orchestration`);
`devkit sync` projects the roles into each agent host's subagent directory
(`CAP-DIST-agent-projections`). The
definitions are the only source of stage order, checks, gates and returns: an executor reads them, never an ad-hoc
sequence.

## 2. Scope & Boundary

- **In-Scope**: the five definitions (layout, anchor, stages, gates, entry and exit checks, returns, declared checks),
  the gate semantics of `plan-intent`, `plan-accept`, `dev-integration` and the `exception` stage, the envelope kinds
  the stages require, the `activity-effort` rules of review and reconcile, the six role contracts, and the
  `devkit_agt.features.integration.readiness` provider (`devkit_spec.features.delivery.usecases.integration.check`) for Unit and `session` tasks, and
  informational `devkit spec worker inspect` evidence for worker-result acceptance.
- **Out-of-Scope**:
  - Evaluating a definition, recording answers and envelopes, binding units: devkit's `devkit workflow` commands.
  - Creating and binding a spec bundle: `CAP-DLV-spec-bundles`.
  - Creating a proposal and the cross-layout handoff: `CAP-DLV-proposal-incubation`.
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
  - **Scope Excluded**: model selection. The model is the runtime's setting; role contracts preset only a
    model-independent reasoning effort per role (§4.6, `ADR-orchestration-workers`), independent of `activity-effort`,
    which sets only how thorough an activity's review and verification are.

## 3. Business Rules & Policies

1. **One definition per classification**: the workflow id is `sdd-<planning-depth>[-<task-kind>]`. `session` uses
   `sdd-session-feature` or `sdd-session-bugfix`, `spec` uses `sdd-spec-feature` or `sdd-spec-bugfix`, `proposal` uses
   `sdd-proposal` until handoff and then `sdd-spec-<task_kind>`. A team review is `proposal` depth plus PR policy, not
   a workflow. The task kind `overall-refactor` has no depth and one workflow, `sdd-overall-refactor`, run in `direct`
   mode only, without a Unit, proposal or spec bundle (`ADR-overall-refactor-workflow`). The axes are not stored as
   fields: the Unit's kind and the bound workflow show them.
2. **Definitions are authoritative**: an executor MUST take stage order, checks, gates and returns from
   `devkit workflow show <id>` / `devkit workflow show --unit <dir>` and `devkit workflow next --unit <dir>`. The
   Markdown body of a definition keeps only rules the schema cannot express.
3. **Shared stages are identical**: a stage id used by several definitions MUST have the same exit checks, gate,
   role, isolation, skills and artifacts in each; `devkit workflow validate` with no arguments reports a difference
   as `SHARED_STAGE_MISMATCH`. Returns are each workflow's own.
4. **Gates are named `<activity>-<decision>`**: `plan-intent`, `plan-accept` and `dev-integration`; the `exception`
   stage belongs to no activity. Numbered gate names are not used.
5. **Decision boundaries and authority**: `plan-accept`, `proposal-handoff`, and `dev-integration` independently permit
   `ask` or `auto`, default `ask`. User decisions are explicit; policy delegation is reported as policy, never fabricated
   user consent. `accept --by user|policy` records acceptance and status together; `policy` requires owning base auto
   and prospective source auto. Planning merge is an acceptance effect, not Development result acceptance. Native
   accept-and-handoff may combine included asks into one form. Verified local effects still obey readiness, exact report,
   SHA, worktree, cleanup and environment guards; publication and host permissions remain separate.
   `workflow return` voids the stage and later decision records and envelopes. Policy delegation never disables checks.
6. **`plan-intent` opens every task**: goal, scope, verification (for a bugfix, the expected behavior), `task-kind`
   and `planning-depth` describe the instructed task. An explicit task instruction supplies this intent without a repeated prompt; `auto` permits policy satisfaction. For `spec` depth the gate opens once the anchor exists and is
   recorded in inline Planning; for `proposal` depth it is the user's confirmation of the draft in Backlog, which one
   request may ask together with a direct acceptance's `plan-accept` (two explicit answers, neither inferred); a spec
   handed off from a proposal carries the proposal's `gate:plan-intent` and `gate:plan-accept` records under the same
   names (`CAP-DLV-proposal-incubation`).
7. **No Development direction gate**: Development starts from the agreed intent. Implementation choices inside it
   are made with the recommended option and recorded; a non-blocking improvement is reported as feedback (a
   follow-up draft proposal is also allowed); only a problem that cannot be solved without changing the agreed goal,
   scope or contract stops the work. At `high` the review loop also stops it (rule 15): a batch that is not minor at
   the cap round, or a recurring P1, is a problem; a P1 the implementer holds invalid and the reviewer asserts again
   after one round given the counter-evidence is a question in the run's `worker` envelope, with both positions as
   options. A P1 the user then rules invalid is closed only by a waiver citing the `answer` envelope, and a fix the
   user asks for after a cap or recurrence problem gets one further round outside the cap, named by the `resolution`
   envelope. A session reports either in the conversation and does not
   integrate; none of this is the `exception` stage. A worker records it and ends; the Host decides recovery or a
   close. There is no return from Development to Planning.
8. **`dev-integration` is per integration unit** (one pull request): it has no exit checks of its own and is asked as
   soon as `integration-approval` is current, that is once the final change report holds. Under `auto` it passes only
   after the path's required review, reconciliation and checks pass, at every `activity-effort`, `low` included.
   Docs reflection and conflict resolution within the approved intent need no re-approval.
9. **Living Spec before `dev-integration`**: the Living Spec reflection, a resolved `reconcile.md` and
   `status: completed` of the anchor MUST be complete before the gate; an optional review feedback breakpoint between
   `review-refine` and `living-spec-draft` adds no stage, check or approval file. The reflection includes `docs/glossary.md`,
   where it exists, when the change introduces or renames a domain term (`spec-sync`, first step).
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
14. **Proposal Planning ends at handoff** (`CAP-DLV-proposal-incubation`): `sdd-proposal` declares no `next`
    candidates, because devkit's `devkit workflow handoff` rebinds a unit in place and refuses a candidate with
    another anchor (`HANDOFF_LAYOUT_MISMATCH`). Once `plan-accept` holds, `next` reports the unit complete
    (`[STAGE: - complete=true]`, no `[HANDOFF]` line) and Development starts with `devkit spec proposal handoff <slug>`.
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
    change the effort, stages or required policies (`ADR-bounded-high-effort-review-loop`).
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
    fresh round outside the cap (`ADR-review-and-reconcile-verification`). A batch not minor at the cap round and a recurring P1
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
    `high`, two or more options compared, a `scout` starting from `devkit spec refs <ID> --direction in` for each
    capability and ADR the proposal touches, then `challenger` rounds of the same loop. A proposal scaffolds
    non-authoritative `planning_effort` and `dev_effort` hints (`low` | `medium` | `high`, default `medium`) in
    `proposal.md`: `planning_effort` is proposed with `plan-intent` and pre-fills Planning start, `dev_effort` is
    refined during Planning before `plan-accept` and returned by `handoff` to pre-fill Development start, while the
    confirmed `activity-effort` of each run is recorded only on its `worker-NN.yaml` envelope (with any override reason
    in `summary`). The effort is always proposed with a reason when the activity starts, and the `plan-accept`
    request shows each Planning run's effort, the refined `dev_effort` hint and the support-role envelopes present,
    naming a `challenger`, or a `scout` at `high`, that the effort required and no envelope shows, and each
    `challenger` round with the `reverify` that closes it. Gates, exit checks
    and `required` policies hold at every effort.
16. **Only the workers write to Git**: a read-only role never stages or commits (`x-git-actions: [read]`). The two
    workers (`[read, commit]`) commit on their activity branch, write their own records and never push, merge, rebase,
    reset or amend (`ADR-orchestration-workers`).

## 4. Interfaces & Data Contracts

### 4.1 Workflow Catalog

| Workflow | Classification | Layout (`work_dir` / `unit_path`) | Anchor | Gates |
| --- | --- | --- | --- | --- |
| `sdd-session-feature` | `session` × `feature` | none | none | `plan-intent`, `dev-integration` |
| `sdd-session-bugfix` | `session` × `bugfix` | none | none | `plan-intent`, `dev-integration` |
| `sdd-overall-refactor` | `overall-refactor` (no depth) | none | none | `plan-intent`, `dev-integration` |
| `sdd-spec-feature` | `spec` × `feature` | `specs` / `{date:%Y-%m}/{date:%Y%m%d}-{slug}` | `spec.md` | `plan-intent`, `dev-integration` |
| `sdd-spec-bugfix` | `spec` × `bugfix` | `specs` / `{date:%Y-%m}/{date:%Y%m%d}-{slug}` | `spec.md` | `plan-intent`, `dev-integration` |
| `sdd-proposal` | `proposal` (either kind) | `docs/proposals` / `PROP-{slug}` | `proposal.md` | `plan-intent`, `plan-accept` |

Each definition with a unit sets its own `layout`, so spec bundles and proposal bundles live where the document model
expects them and `devkit workflow list` finds both. `schema_version` is `1` in every definition.

### 4.2 Stages

`devkit workflow show <id>` is the authoritative list; in order (gate in parentheses):

- **`sdd-session-feature`**: `intent-session` (`plan-intent`), `execute-verify`, `report-session`, `approval-session`
  (`dev-integration`), `commit-session` (exit `lint-ci-clean`), `merge` (exit `merged`).
- **`sdd-session-bugfix`**: `intent-session`, `reproduce-session`, then the stages of `sdd-session-feature` from
  `execute-verify` on.
- **`sdd-overall-refactor`**: `intent-refactor` (`plan-intent`), `restructure`, `report-refactor`, `commit-refactor`
  (exit `lint-ci-clean`), `approval-refactor` (`dev-integration`), `merge` (exit `merged`).
- **`sdd-spec-feature`**: `intent` (`plan-intent`), `specify`, `build-verify`, `review-refine`, `living-spec-draft`,
  `collect-feedback`, `final-change-report`, `integration-approval` (`dev-integration`), `integrate`, `merge`.
- **`sdd-spec-bugfix`**: `intent` (`plan-intent`), `characterize`, `plan-tasks`, `reproduce`, `fix-verify`, then the
  stages of `sdd-spec-feature` from `review-refine` on.
- **`sdd-proposal`**: `intent-proposal` (`plan-intent`), `spike` (optional in the schema and never current on
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
| `plan-intent` | `intent`, `intent-session`, `intent-proposal` | task intent: `ask` or `auto` |
| `plan-accept` | `direction-handoff` | `ask` or `auto` |
| `proposal-handoff` | native Development start | `ask` or `auto` |
| `dev-integration` | `integration-approval`, `approval-session` | `dev-integration` (`ask` or `auto`) |

- A gate waiting for the user: `devkit workflow next` prints `[WAITING: human gate:<gate>]` with a
  `[REQUEST: id=gate:<gate> ...]`. A `plan-intent` answer is `devkit workflow answer --unit <dir> --request
  gate:plan-intent --action accept --by user`, a `plan-accept` acceptance `devkit spec proposal accept <slug> --by user`
  (`--direct` for a direct acceptance), and a decline of either `--action decline --by user --note "<reason>"`. A
  `dev-integration` OK is `--given dev-integration` on every later `next`, and an objection about the change takes the
  stage's return path; where a runner binds `gate:dev-integration` to PR state, the PR ready state answers it. Every
  definition with that gate declares `gates: {dev-integration: {answer: given}}`, so `next` ends its `[REQUEST]` with
  `answer=given`.
- `dev-integration = "auto"`: the gate passes by policy; its stage never stays current, so `next` lists it as
  `[GATE_PASSED: dev-integration stage=integration-approval policy=auto source=policy]` (JSON `passed_gates`), the basis
  every report cites.
- `--given <gate>` asserts a gate for one run (a runner's binding).
- The workflow definitions fix the policies each gate accepts (`gates.<gate>.policies`): `plan-intent` and
  `plan-accept`, `proposal-handoff` and `dev-integration` take `ask` or `auto`. A configured policy outside them stops every
  devkit command that evaluates the unit with `WORKFLOW_GATE_POLICY`, and `devkit spec policy` reports the same rule
  (`CAP-DLV-project-policy`).
- `plan-accept` is asked only for a proposal in review, or for a draft once a direct acceptance wrote
  `status: accepted`: the `direction-handoff` exit is `frontmatter(proposal.md status reviewing|accepted)`, so a draft
  otherwise, or a rejected proposal, gets no request. A `plan-accept` acceptance is recorded with
  `devkit spec proposal accept`.

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

One Markdown contract per role in devkit's
`CAP-DIST-agent-projections`:
`role`, `title`, `description`, an optional `skill` and a `hosts` block for `claude-code`, `codex` and `antigravity`.
Extension keys devkit does not interpret: `x-execution` (`isolated`), `x-invocation` (`optional`), `x-model-profile`
(`light-medium`, `general-high`, `high-reasoning`; never a host model name) and `x-git-actions` (`[read]` for every
role but the two workers, `[read, commit]`).

The four read-only roles preset a reasoning effort in their host blocks, with no model name
(`ADR-orchestration-workers`): `medium` for the `light-medium` profile, `high` for `general-high` and `high-reasoning`,
as `effort` under `claude-code` and `model_reasoning_effort` under a `codex` block that is not `unsupported`, at
`low`, `medium` or `high` only. Antigravity has no such key. The two workers set none, whatever their profile, so
they run at the session's effort like the Host whose work they take over. The preset is independent of
`activity-effort` and applies only when the projected agent is spawned: a role the main session runs itself uses
the session's effort. An emulated named-role projection still applies its declared preset; workers declare none. On Claude Code a per-call `effort` or
`CLAUDE_CODE_EFFORT_LEVEL` overrides the preset; on Codex the preset wins over a spawn value.
`packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` pins role, profile and preset for every contract.

| Role | Skill | Model profile | Reasoning effort | Writes | Envelope kind |
| --- | --- | --- | --- | --- | --- |
| `challenger` | none: the procedure is in the contract | `high-reasoning` | `high` | nothing | `challenger` |
| `reconcile-reviewer` | `spec-sync` | `light-medium` | `medium` | nothing: verifies the implementer's reconcile at `medium`/`high`, subject to rule 15 | `reconcile-check` |
| `code-reviewer` | `spec-review` | `general-high` | `high` | nothing: verifies implementation against requirements and checks | `review`, `reverify`, or a message for a session |
| `scout` | none: the procedure is in the contract | `light-medium` | `medium` | nothing, or the proposal's `materials/` on request | `scout` |
| `planning-worker` | none: the procedure is in `spec/references/planning.md`, which the contract cites | `general-high` | session | the proposal directory in its `plan-` worktree, committed | `worker` (its own) |
| `development-worker` | none: the procedure is in the contract | `general-high` | session | the unit's write scope in its `dev-` worktree, committed at every stage boundary | `worker` (its own) and the stage envelopes |

The contract body is the role's prompt and holds only what the role needs: purpose, input fields, return fields,
write boundaries, failure handling and, for a role whose procedure no main session runs (`challenger`, `scout`, the
`development-worker`), the procedure itself. Planning runs in a main session in `direct` mode, so its ordered steps
live in the `spec` skill's `references/planning.md`, which the `planning-worker` contract cites; the contract keeps
only the worker's own obligations (worktree, nested roles, return, write boundaries, problems)
(`ADR-orchestration-workers`). Caller guidance (per-role payload, host guarantees, the
post-run diff comparison, envelope recording, range validation) lives in `spec-delegate` (`SPEC-subagent-procedure-in-contract`).

The workers exist for `local-orchestrated` mode (`spec-orchestrate`, user-invoked per activity) and never for
`session` depth. Each is one-shot: it runs one turn of one activity in that activity's devkit worktree, using absolute
paths, an explicit absolute worktree cwd on every command and `git -C <worktree>` because initial cwd may be the
base checkout, runs its role subagents nested (Host → worker → role; Claude Code tool `Agent`, Codex
`collaboration.spawn_agent`) with absolute read/contract scopes that name the worktree's startup skill and
instruction paths (a nested role's read from another checkout is a reported boundary exception) and never ends its turn while one is still running, keeps
scratch files in an ignored path inside its worktree, writes its own records, commits at every stage boundary and,
when it stops on questions or a problem, makes an emergency commit of the unfinished work with its `worker` envelope
when record/commit access is permitted.
Planning resolves operational instructions and CLI execution in the assigned worktree. When a turn needs newer
base document IDs or CLI features, the Host incorporates the base and synchronizes that worktree's installed
instructions under existing Git and permission policy before resuming. A worker discovering that dependency returns
a problem for Host recovery; it never merges, resolves references from another branch, hides missing IDs in prose,
or fabricates unsupported records. Base advancement alone does not require a refresh.

The Planning payload names an ignored probe path inside the proposal directory and allowed write scope; the Host
verifies or prepares it before delegation. The worker removes temporary files and throwaway repositories, including
their linked worktrees, before its last commit and retains evidence in `materials/`. A probe that needs an outside
path is a boundary-expansion problem for the Host. Ignored status grants no sandbox or activity-repository Git
permissions; a temporary path under `/tmp` may not exercise repository-local sandbox conditions.

It never reverts, closes, raises the depth or narrows the scope. The `development-worker` runs from the stage
`devkit workflow next` names up to the final change report; the `planning-worker` takes a draft proposal toward
`plan-accept`, collecting its questions in one round. The Host restates either worker's questions for the user (what
each answer decides, what each option leads to) rather than relaying the worker's wording. The Host validates the cumulative committed range from the
unit's last accepted head; a range it rejects is a problem in the Host's own `worker` envelope, which blocks the unit
from review and integration without discarding anything until a resolution names it
(`ADR-orchestration-workers`, `ADR-orchestration-workers`). Host statuses: Claude Code
`native`, Codex `emulated` with `sandbox_mode: workspace-write`, Antigravity `unverified`
(`ADR-orchestration-workers`). Native Codex spawning does not enforce the worker's role/path boundary;
Git administration remains shared. Workers inherit model and reasoning effort and set no approval-policy override.

Prefer the projected named role with payload only. An unavailable role can mean projection or session-root
availability; role absence alone does not prove missing trust. Normal status/sync repairs missing or stale
projections where authorized. A generic native subagent may read the absolute effective managed/override contract
and explicitly emulate it only when host project-instruction loading is permitted; an explicit trust restriction
stops fallback and cannot be bypassed by another role, tool, path, process or host settings edit. Before starting a
worker, missing native spawning, required nested roles or necessary approval capability selects existing Host
`direct` execution when allowed, or `needs_input` for required isolation. Availability grants no future approval.

Each necessary operation beyond active sandbox access requests a separate narrowly scoped approval naming exact
operation, target and justification: sibling writes, shared Git index/commits, scope registry and verification/network
access included. No broad persistent prefix or settings change is introduced; preflight success grants no later
access. Unavailable or denied approval stops that operation and preserves its actual partial state. Do not evade
refusal through another tool, path, process or broader request. Retry another-cause failure only after cause/input
changes and authorization permits it. Failed record/emergency commit operations use only still-permitted scoped
access. Emergency `--no-verify` is limited to ordinary commit-gate refusal, never sandbox or approval denial.

When the worker record or emergency commit also cannot run, return `failed` with cause, commands tried, recovery,
actual last SHA, dirty paths and absent/uncommitted records or commit; never invent a clean committed result or final
HEAD containing it. The Host blocks failed dirty/uncommitted returns even without a worker record and owns a
subsequent recovery run and its records. Successful acceptance still requires cumulative ancestry through final HEAD,
strict allowed paths, clean worktree, unchanged base and checks. The one-shot lifecycle and stage gates remain.

Actual generic native Planning and Development runs are recorded in `MAT-codex-native-worker-evidence` for the observed
runtime. Named-role loading on a fresh host, denied approvals, failed emergency commits and wider host/version
coverage remain unverified. Deterministic contract/projection tests cover those instruction branches, not platform
enforcement; no persistent-grant or native confinement guarantee follows.

Stages delegate to `code-reviewer` (`review-refine`), `reconcile-reviewer` (`living-spec-draft`, as verifier) and `scout`
(`spike`); `challenger` has no stage of its own (its return is recorded at `spike`) and is delegated as the Planning effort asks
(at `medium` and `high`, rule 15). Implementation stages keep
`role: developer`; the orchestration mode hands their turn to a worker. `[DELEGATE: role=<role> isolation=...]` in
`next` names the role; `spec-delegate` decides between a host subagent and a main-session substitute and records the
choice. A projected role receives only the per-call payload, since the host loads the contract body as its system
prompt.

### 4.7 Executor Commands (devkit)

| Command | Use |
| --- | --- |
| `devkit workflow next --unit <dir> [--given <check>]...` | Current stage, unmet checks, `[NEXT_SKILL]`, `[WAITING]`, `[DELEGATE]`, `[SKIPPED]`. |
| `devkit workflow show <id>` / `--unit <dir>` | Render a definition. |
| `devkit workflow answer --unit <dir> --request gate:<gate> --action accept\|decline --by user` | Record a `plan-intent` decision, or decline `plan-accept`. |
| `devkit spec proposal accept <slug> --by user [--note <text>] [--direct --note <reason>] [--check]` | Record a `plan-accept` acceptance with `status: accepted` in one step; `--direct` for an eligible draft on the base (`CAP-DLV-proposal-incubation`). |
| `devkit workflow return --unit <dir> --to <stage>` | Go back within the activity; voids later approvals and earlier envelopes of those stages. |
| `devkit workflow bind --unit <dir> --workflow <id>` | Bind an unbound unit, or change its workflow. |
| `devkit workflow validate` | Validate definitions; `SHARED_STAGE_MISMATCH` across definitions. |
| `devkit workflow list` | List units of every layout. |
| `devkit workflow envelope worker\|answer\|resolution --unit <dir> ...` | A run's record (`--stage` and `--effort` always; `--questions-file`, `--problem`, `--tried`, `--recovery`), its answers (`--answers-to`, `--answers-file`, `--settle`) or a fix (`--resolves`). |
| `devkit workflow envelope check --unit <dir> [--format json]` | Malformed envelopes and the hold: `[BLOCKED]`, `[PENDING_QUESTION]`; `blocked`, `problems`, `pending_questions` in JSON. |
| `devkit worktree start <branch> [--no-worktree \| --existing-branch <branch> --unit <dir>]` | Start `plan-<slug>` or `dev-<slug>` in a worktree or the current checkout, or continue an existing branch after devkit-spec's attach check. |
| `devkit worktree finish <branch> [--merge [--local-only]]` | Land the branch on the base as a merge commit, or a fast-forward under `[worktree] merge = "ff-only"` (skipping `fetch`/`push` when `--local-only`), remove the worktree, delete the branch when `delete_branch=yes`, and run the post-finish extension. |
| `devkit worktree status --stale` | Activity branches idle beyond `[worktree] stale_after`; also warned by `devkit rules check -p hygiene`. |

### 4.8 SDD Integration Readiness Provider (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py`)

Registered under the `devkit_agt.features.integration.readiness` entry point as `spec` and selected by `[integration] provider = "spec"` (`ADR-delivery-decision-boundaries`, `SPEC-hook-driven-integration-cleanup`). `check(context: IntegrationContext) -> Readiness` evaluates the committed `context.finish.source_sha` against `context.finish.target_sha` (at a build of an approved request, the build target, with the result commit as `context.result_sha`; `ADR-local-and-pull-request-integration`) inside an isolated temporary workspace materialized from Git (populating `.devkit/managed/` only when files match the committed `.devkit/installation.json` SHA-256 digests), so uncommitted worktree or base edits never influence readiness:

1. **Policy and configuration**: validates `[tool.spec]` (`read_spec_config`) and `[workflow.approvals]` (`check_approvals`, accepting ask or auto for task intent and the three main boundaries) in both the base checkout and the materialized `source_sha` snapshot.
2. **Unit tasks (`task.kind == "unit"`)**: verifies branch-to-unit correspondence through `attach_check(base, branch, unit, source_sha)` and `task.id` agreement (`<slug>`, `SPEC-<slug>` or `PROP-<slug>`), then evaluates the unit in `Workspace(..., ancestor=...)`:
   - `dev-<slug>` (`sdd-spec-feature` or `sdd-spec-bugfix`): evaluated with `given=("dev-integration",)`; requires `current_stage == "integrate"`, zero unmet checks across earlier stages (`specify`/`characterize`, `build-verify` or `reproduce`/`fix-verify`, `review-refine`, `living-spec-draft`, `collect-feedback` when enabled, `final-change-report`, `integration-approval`), no envelope hold (`blocked` or `pending_questions`), `spec.md` `status: completed`, `reconcile.md` `status: resolved`, and (when handed off from a proposal) carried `gate:plan-accept` accepted.
   - `plan-<slug>` (`sdd-proposal`): requires `proposal.md` `status: accepted`, `gate:plan-intent` and `gate:plan-accept` accepted, `collect-feedback` satisfied when enabled, `complete == True` (`current_stage is None`), and no envelope hold.
3. **Session tasks (`task.kind == "session"`)**: requires a `dev-<slug>` branch with no spec unit for `<slug>`, verifies that no spec or proposal unit touched between `merge_base(target_sha, source_sha)` and `source_sha` is held or incomplete (`spec.md` must be `completed`, `proposal.md` must be `accepted`), and validates structured JSON declarations in `task.claims_json` (`task_kind` in `feature|bugfix|overall-refactor`, `effort` in `low|medium|high`, `review`, `tests`, `lint` passed, plus `reproduced: true` and `resolved: true` for `bugfix`).
4. **Cumulative CI governance rules**: runs `run_project_rules(workspace, snapshot=ci_snapshot, phase=Phase.LINTER)` on the `merge_base..source_sha` snapshot (`mode="ci"`), or with a result commit on the `build_target..result_sha` snapshot (the tree that would land), and requires zero load/evaluation errors and zero blocking violations (`CI_RULES=pass`). The unit is still evaluated from the source tree; with a result commit, a target change inside the unit directory since the merge base is a reason. Tests are not re-run on the result.
5. **Deterministic evidence**: returns `Readiness(source_sha, target_sha, evidence=..., reasons=..., result_sha=..., target_bound=("TARGET_SHA", "RESULT_SHA"), disclosure="CI rules only on the merged result; tests and review ran on the source only")` whose coded `Evidence` tuple (`TASK_KIND`, `WORKFLOW`, `UNIT`, `SOURCE_SHA`, `TARGET_SHA`, `STAGE_STATUS`, `HOLD_STATUS`, `SESSION_CLAIMS`, `CI_RULES`, `SPEC_POLICY`, and `RESULT_SHA` at a build) is deterministic from committed Git state. `SPEC_POLICY` digests the parsed `[tool.spec]` of the target and of the result (the source before a build) and is not target-bound, so a `[tool.spec]` change on the target refuses the build through `IntegrationService`'s evidence equality, which ignores only the target-bound codes.

## Source feedback at completion

`ADR-feedback-lifecycle` defines promoted and resolved as terminal routes: promotion transfers tracking to
identified follow-up work; resolution closes a direct verified fix without promotion. Only open feedback needs action.
Task entry preserves source FB IDs and scope through handoff and drafting. Terminal references require no completion
disposition or re-verification and do not implicitly authorize source writes. Completion of follow-up work never
converts promoted sources to resolved.

At `living-spec-draft`, review only explicit open direct-fix sources against implementation and verification and
record outcomes in `reconcile.md`. At `report-session`, do the same before committing and report outcomes without
a new artifact. Record outcome and evidence for resolutions; incomplete or unverified direct fixes stay open.
Include source files needing updates in task/delegation boundaries; otherwise the Host applies their dispositions.
Recheck only resolutions newly made by this task if later changes invalidate evidence. This obligation is independent
of capture settings and collect-feedback policy and grants no integration authority or additional workflow gate.

Native local Development starts may use `spec_handoff` (`CAP-DLV-proposal-incubation`): its confirmation form shows
the accepted plan and lets the user override the `dev_effort` hint before the worktree and spec handoff are created.
The returned `activity_effort` is the run input and is recorded on that run's worker envelope. This supplies the
local user interaction otherwise provided by an external runner; final integration retains its separate approval.

## Worker result inspection

`devkit spec worker inspect [--unit <dir>] [--base <accepted>] [--head <returned>]
[--scope <prefix>... | --scope-file <file>] [--base-checkout <path>] [--details]` collects evidence in the activity worktree.
It derives its inputs from committed HEAD records and reports each value's source; explicit flags replace only
that input. Scope-file is UTF-8, one nonempty literal repository-relative prefix per line; a scope override
replaces the entire derived scope. Literal paths match themselves and descendants at path-component boundaries.

- Unit: the branch's `devkitUnit` marker, else its activity-branch correspondence. A Development spec takes
  precedence over its accepted pre-handoff proposal; ambiguous or absent correspondence is unresolved.
- Head: the unique commit adding the highest-numbered worker envelope. Base: the commit adding the previous
  worker envelope when its state is unblocked, otherwise the common `diff_scope.base` of its unresolved problems.
  With no previous worker, use the single merge base with `devkitBase`, or the registered base checkout's branch.
- Scope: a Planning proposal directory; for Development, the unit directory, literal task boundaries, materials
  directory, reconciliation targets and explicitly linked Source feedback files whose committed status is `open`.
  Terminal or unknown statuses add no implicit source scope; explicit task boundaries remain independent. Entries retain their source,
  task number or feedback ID. Missing or invalid scope records leave the scope check not-run.
- Base checkout: the worktree's registered common-directory checkout; absent when run in the base itself. Its
  HEAD and dirty paths are observations for the Host's comparison with its saved state, not checks.

Checks report `pass`, `fail` or `not-run`: base ancestry, worktree HEAD equality, changed paths and outside-scope
paths, worktree cleanliness, committed envelope validation (including unresolved problems and pending questions),
cumulative `devkit rules check --ci --base` and `devkit workflow next`. Both old and new paths of renames are
included. Rules run only when worktree HEAD equals returned head. Workflow evaluation is not-run in a dirty
worktree because the existing command reads disk; this prevents uncommitted records from changing its result.
Wrapped results retain their codes and actions.

`--format json` emits one object containing `inputs` (value/source), `scope` entries, `base`, `head`, `changed_paths`,
optional `outside_scope` and `base_checkout`, `checks`, `notices` and `exit_code`. Text output emits inspection,
input, scope, changed-path and check sentinels. The compared commits and changed paths are reviewer payload
information. Default JSON keeps each check status, actionable findings, violations, notices, errors, unresolved problems, pending questions and recovery evidence; envelope entries contain metadata and current open findings rather than historical bodies. Successful wrapped check bodies are omitted. Workflow output retains the next action and approval evidence, with only stage identity, role, isolation and returns instead of the full stage definition. Unknown failed check payloads and diagnostic stdout/stderr remain intact. `--details --format json` includes all original wrapped results and envelope bodies. Both modes run every check and derive the same verdict from complete evidence. Exit 0 means no failed check, 1 means at least one failed check, and 2 means invalid invocation,
invalid Git inputs or unresolved required unit/head/base. A not-run check alone is a notice, not exit 1.

| Code | Meaning and action |
| --- | --- |
| `WORKER_UNIT_UNRESOLVED` | Supply `--unit` with the committed unit directory. |
| `WORKER_HEAD_UNRESOLVED` | Supply `--head` when there is no uniquely added latest worker envelope. |
| `WORKER_BASE_UNRESOLVED` | Supply `--base` when previous blocked records or base branch do not determine it. |
| `WORKER_SCOPE_UNRESOLVED` | Supply complete literal paths with `--scope` or `--scope-file`. |
| `WORKER_CHECK_NOT_RUN` | Inspect the reported cause and rerun the named check after correcting it. |

The helper MUST NOT write records, modify files, repair, retry, synchronize, merge or widen scope. It adds no
approval request, workflow gate, integration refusal or scope registration. The Host's delegation payload remains
authoritative, and the Host decides acceptance under the existing procedure.
