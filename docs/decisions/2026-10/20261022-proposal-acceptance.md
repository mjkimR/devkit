---
id: ADR-proposal-acceptance
title: Proposal acceptance, review reports and proposal records
summary: "For proposal acceptance, we use one validated accept command with an eligibility-checked direct path, a handoff guard, source-bound review reports with native approval, checked boundary paths and proposal-local feedback, to bind acceptance to exact reviewed sources, accepting more modules."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-planning-feedback-in-proposal
  - ADR-direct-acceptance-command-and-handoff-guard
  - ADR-eligibility-for-direct-acceptance
  - ADR-proposal-boundaries-name-existing-paths
  - ADR-source-bound-review-reports-and-explicit-lifecycle-approval
---

# [ADR-proposal-acceptance] Proposal acceptance, review reports and proposal records

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: not recorded in the members
- **Involved Components/Capabilities**: `CAP-DLV-proposal-incubation`, `CAP-DLV-delivery-workflows`,
  `CAP-GOV-spec-rules`, `CAP-GOV-rule-authoring`

---

## 1. Context & Problem Statement

A direct acceptance must reach the same end state a Planning acceptance reaches: `status: accepted` and an accepted
`gate:plan-accept`, which the handoff carries. The engine fixes the order
([engine evidence](../../materials/2026-10/20261020-draft-direct-acceptance/engine-evidence.md)): `plan-intent` while
the proposal is a draft, a passing `collect-feedback` sweep, `status: accepted` on disk, then `plan-accept`; anything
else is `REQUEST_UNKNOWN`. The handoff checked the status but not the gate record, and the `plan-<slug>` readiness
check ran only on the MCP integration path. Every executor edited the `status:` line by hand; 01 §10 already planned
one writer for it, shared by the local Host and autohub. Where a direct acceptance is committed is compared in
[options](../../materials/2026-10/20261020-draft-direct-acceptance/options-comparison.md); the user chose A2, Backlog
acceptance on the base under every policy, and allowed one request to ask both gates (`answer-01.yaml`).

Every request not started now is a draft proposal (`SPEC-backlog-roadmap-and-issues`), so many drafts carry a
direction that is already settled: a piece split off a larger request, a follow-up promoted from feedback, a request
whose contract is clear. Direct acceptance needs a rule for which drafts qualify, split into what a tool can check and
what only the Host and the user can judge.

`SPEC-proposal-review-and-approval` needs a readable design briefing without embedding full English source in a
native form. Approval must still bind the actual plan, effects and configured guards. Shared reports expire and
Git/worktree operations cannot form a cross-process transaction.

`target_area` and `boundaries.owns` in `proposal.md` were free text, unchecked at creation, at `plan-intent` or at
handoff, which copies them into the spec's carried notes and task boundary (`proposals/handoff.py`,
`proposals/specs.py`). A proposal declared `capabilities/core/`, an area that does not exist
(`FB-proposal-boundaries-unchecked`). `devkit spec proposal new` without `--target-area` writes the placeholder
`capabilities/<area>/` into both fields. Evidence:
`docs/materials/2026-10/20261020-envelope-record-gaps/spike-evidence.md`.

Planning workers write only inside their proposal. Global feedback would require expanding every worker's write
allowance. Proposal-local feedback fits that boundary, but generic handoff moved extra files into historical
materials, and a rejected or decomposed proposal can be deleted without handoff.

---

## 2. Decision Drivers

- One validated step instead of an order an agent must get right by hand, and one writer for every acceptance.
- Never infer an approval: an explicit acceptance is recorded through devkit's `record_answer`, exactly as
  `devkit workflow answer` does.
- Keep the `sdd-proposal` schema: `collect-feedback` is shared with Development and must stay required for Planning.
- Depth is not size (01 §2.2): small work can need its direction decided, large work can be clear.
- A draft whose existence means the direction is open must never skip Planning: a supersede reverses an earlier
  `plan-accept`, and a depth escalation exists because the direction must be decided first (`classification.md` §4).
- The user's explicit `plan-accept` is the safeguard; the rule must not pretend a tool can judge a direction.
- Exact review identity, explicit user authority, local MCP priority, bounded retry, existing integration ownership,
  and a read-only viewer outweigh automatic regeneration or invisible recovery.
- The current proposals use three boundary forms (a bare area `delivery/`, a docs-root path `capabilities/delivery/`
  or `stories/delivery/`, a repository path `packages/...` or `docs/glossary.md`); all resolve and none should need
  rewriting.
- A Backlog draft keeps the placeholder until Planning settles the area, and the first Planning commit (`status:
  reviewing`) comes before the spike; neither may be refused.
- The boundary carried into Development must name real paths by `plan-accept`.
- The rules engine applies one severity per rule: the evaluator overwrites each violation's severity with the rule's
  effective severity (`packages/devkit/src/devkit/rules/engine/evaluator.py`, `CAP-GOV-rule-authoring`).
- An accepted proposal is never edited; a premise that no longer holds is a problem and a close
  (`CAP-DLV-delivery-workflows`). A rule is not a gate or a policy.
- Planning feedback stays within the Planning worker's existing write boundary.

---

## 3. Considered Options

### Proposal-local feedback with explicit retirement (Selected by `ADR-planning-feedback-in-proposal`)
- **Advantage**: one activity directory and one commit stream; open work follows the spec.
- **Cost**: needs path-rule support, handoff routing and preservation before deletion.

### Global month-level backlog (Rejected by `ADR-planning-feedback-in-proposal`)
- **Advantage**: survives every proposal ending without relocation. **Cost**: adds a second write root to Planning.

### Proposal-local feedback, generic materials move (Rejected by `ADR-planning-feedback-in-proposal`)
- **Advantage**: reuses handoff unchanged. **Cost**: open feedback becomes historical material rather than actionable
  spec feedback.

### The planned `accept` command with a direct variant, plus a handoff guard (Selected by `ADR-direct-acceptance-command-and-handoff-guard`)

### A direct-only command (Rejected by `ADR-direct-acceptance-command-and-handoff-guard`)
- `accept --direct` with a fixed `by`: it ships a second shape beside the planned shared writer, which the later
  general command would have to break.

### A skill procedure over existing commands (Rejected by `ADR-direct-acceptance-command-and-handoff-guard`)
- Edit the status, `devkit workflow answer`: no code, but the order is easy to get wrong, eligibility is unchecked and
  a partial state hands off without the gate.

### Make `collect-feedback` optional in `sdd-proposal`, or add a skip token (Rejected by `ADR-direct-acceptance-command-and-handoff-guard`)
- The first drops the sweep from normal Planning, the second records a sweep that did not happen.

### A mode of `devkit spec proposal check` (Rejected by `ADR-direct-acceptance-command-and-handoff-guard`)
- `check` is a read-only Backlog guard that refuses any status other than `draft`.

### Mechanical checks plus the Host's judgment, no size limit (Selected by `ADR-eligibility-for-direct-acceptance`)

### Add a size limit (`S` or `M`) (Rejected by `ADR-eligibility-for-direct-acceptance`)
- It mixes size into a depth decision and blocks large but clear work, which 01 §2.2 classifies as `spec`.

### A frontmatter marker set in Backlog, for example `direction: settled` (Rejected by `ADR-eligibility-for-direct-acceptance`)
- It is a stored depth axis in disguise (the axes are not stored, `ADR-delivery-classification`) and would be set when
  the request is filed, not when it is accepted.

### A. A new rule `RULE-proposal-boundaries` with severity S1, warning (Selected by `ADR-proposal-boundaries-name-existing-paths`)

### B. More checks in `RULE-spec-format` (Rejected by `ADR-proposal-boundaries-name-existing-paths`)
- It already validates the effort hints and `namespace` of proposal anchors; it is an error rule, so the new reports
  would refuse draft commits.

### C. A check in `devkit spec proposal handoff` only (Rejected by `ADR-proposal-boundaries-name-existing-paths`)
- Too late, after `plan-accept`.

### Severity S2 or S3 (Rejected by `ADR-proposal-boundaries-name-existing-paths`)
- **S2** error on `accepted` proposals only refuses the acceptance commit the Host writes after the user accepted and
  turns a later path move into an error on an unchangeable proposal; **S3** two rules (placeholder error, missing path
  warning) still refuses the first Planning commit of a placeholder draft.

### Immutable shared report plus scoped native composition (Selected by `ADR-source-bound-review-reports-and-explicit-lifecycle-approval`)
- Concise review, exact source, one decision; requires explicit TTL refresh and partial-state recovery.

### Rejected by `ADR-source-bound-review-reports-and-explicit-lifecycle-approval`
- **Keep raw proposal in every form**: repeats full English source, loses PADR focus.
- **Commit localized reports**: pollutes tracked English documentation and creates report/source commit recursion.
- **Generic approval token or synthesized confirmation callback**: expands authority across tools and restarts.
- **Full atomic merge/setup rollback**: cannot undo arbitrary setup or safely delete user changes.
- **Viewer performs approval and regeneration**: violates read-only and existing approval ownership.

---

## 4. Decision Outcome

- **Accept command**: `devkit spec proposal accept <slug> --by <actor> [--note <text>] [--direct] [--check]` is the
  one writer for every acceptance. Without `--direct` it accepts a proposal in review (`status: reviewing`) on its
  `plan-<slug>`: the Planning acceptance in one step. With `--direct` it accepts a draft: it checks the eligibility,
  including the path's conditions, and refuses a draft without `--direct`. It writes `status: accepted` and records
  `gate:plan-accept` through `record_answer`, with the note (for a direct acceptance "direct acceptance, Planning
  skipped: <reason>; task_kind <kind> confirmed"), so the engine decides whether `collect-feedback` holds, is switched
  off or is skipped by policy; on refusal it restores the status and reports the evaluation's unmet checks and hold
  reasons, never a guessed cause. `--check` runs every check read-only and writes nothing; the command never records
  `plan-intent`, never commits, merges or runs the handoff. `reject` stays the follow-up 01 §10 plans.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Acceptance authority**: the command runs after an explicit acceptance (`--by user`; autohub records the user's UI
  acceptance the same way); the original human-only restriction is replaced by policy delegation of `plan-accept`
  (`ADR-delivery-decision-boundaries`), while this writer and its carry guards remain in force.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Repair**: with `--direct` the command also repairs a proposal already `accepted` that has no effective
  `gate:plan-accept` and no `worker` envelope (no Planning ran), applying every direct-acceptance check except the
  status, on the base like a direct acceptance; a repair, like every acceptance, follows an explicit acceptance of a
  full request. There is no repair of a Planning acceptance (a `worker` envelope exists): the guard's refusal stands
  and the plain form keeps its precondition (in review, on `plan-<slug>`). The recovery, on the user's decision
  (`answer-02.yaml`, `planning-acceptance-without-record`), is to revert the whole Planning merge on the base, which
  returns the proposal to `draft`, and run Planning again; a refused `--direct` repair is undone the same way, by
  reverting its `draft`->`accepted` edit. No command path is added for either.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Where a direct acceptance runs (A2)**: a direct acceptance is Backlog work under every policy, committed on the
  base checkout only. The command checks it positively (`answer-02.yaml`, `base-checkout-definition`): the current
  worktree is the main worktree and its branch equals the integration base (the `origin/HEAD` target when it resolves,
  as the integration resolves it); anything else is refused, a linked worktree, a detached `HEAD` and any other branch
  (`plan-*`, `dev-*`, a hand-made one) included. When `origin/HEAD` does not resolve (no remote), the main worktree's
  branch is the base, as `devkit worktree` treats it, and a detached `HEAD` or a `plan-*` or `dev-*` branch is still
  refused. Before proposing it the Host settles that it can push to the base (or that there is no remote); a protected
  base means Planning instead, and a stranded acceptance commit is undone with `git revert`, never a reset. The Host
  runs `--check`, sweeps its own acceptance session only once the user has accepted, just before the command (under
  the project's sweep policy: a new `feedback` envelope at `collect-feedback`, where zero observations is a valid PASS;
  with the stage off, none; under requested-only capture, the policy-skip PASS), runs the command and commits the
  result on the base. Under `pull_request = required` the request states that the direction gets no PR review, and the
  user may choose Planning for that draft instead. (ADR-direct-acceptance-command-and-handoff-guard)
- **Both gates in one request**: for an eligible draft without a recorded `plan-intent`, one request may ask both
  decisions, each named in full (the intent with goal, scope, verification, `task_kind`, depth and the effort hints;
  the acceptance with "Planning: skipped" and the eligibility reason), and the user answers each explicitly; neither is
  inferred from the other. The Host then records `plan-intent` with `devkit workflow answer --by user`, sweeps, runs
  `accept --direct` and commits all of it in one Backlog commit. If the user accepts only the intent, the Host does not
  sweep and the commit holds the draft with its intent record, which Planning starts from; if the command refuses
  after the sweep, the sweep envelope is removed before that commit, so Planning sweeps for itself.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **No run**: a direct acceptance has no Planning run, no `activity-effort` and no `worker` envelope; its sweep covers
  the acceptance session, and freshness stays an executor procedure as for every Planning run.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Handoff guard**: for a bundle bound to `sdd-proposal`, `devkit spec proposal handoff` also requires the effective
  accepted `gate:plan-accept` record, refusing with `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` (`INTERACTION`): its
  directive is to stop and ask the user, never to record an acceptance unasked. For a proposal without a `worker`
  envelope, on the user's explicit acceptance the Host repairs it on the base with `accept --direct`, merges the base
  into `dev-<slug>` and reruns the handoff; with a `worker` envelope it reports the refusal to the user (no repair
  command) and, on the user's decision, reverts the whole Planning merge on the base back to `draft` for Planning to
  run again; a worker or Cloud Agent reports it as a problem instead. A single-file or unbound proposal, which can
  carry no gate record, keeps the status-only rule. (ADR-direct-acceptance-command-and-handoff-guard)
- **The note survives the handoff**: carried gate records keep the proposal's note after `PROP-<slug>`
  (`PROP-<slug>: <note>`) instead of replacing it, so a spec shows that its direction was accepted without Planning.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Visibility**: the acceptance request shows "Planning: skipped (direct acceptance)" where a Planning acceptance
  shows the applied effort and support roles, together with `task_kind` (which `plan-accept` confirms) and its reason,
  the recorded `planning_effort` hint, the eligibility reason, the PADRs the handoff will promote and the `dev_effort`
  hint, which the Host reviews against the settled direction as a Planning executor would. The `sdd-proposal` stage
  schema is unchanged; its body and `CAP-DLV-delivery-workflows` describe the direct path.
  (ADR-direct-acceptance-command-and-handoff-guard)
- **Eligibility checked by the tool**, all at the moment of acceptance: `status: draft`; an effective accepted
  `gate:plan-intent`; no `needs_decompose: true`; no `supersedes`; no local or fetched `plan-<slug>`; `task_kind` is
  `feature` or `bugfix`; no envelope hold (an unresolved problem, a pending question or a malformed envelope); and the
  A2 path conditions above. The same checks run read-only first, so a refusal leaves nothing behind; a missing
  `plan-intent` is reported there as a pending condition, separate from the blocking ones, because one request may ask
  for both decisions (`gates-in-one-exchange`); the accept command itself still requires it recorded.
  (ADR-eligibility-for-direct-acceptance)
- **Eligibility judged by the Host and shown to the user**: the direction leaves nothing to compare (no option to
  weigh, no question to ask), the body has no open spike question, and the draft is not a depth escalation carrying a
  failed attempt's material. The request names the recorded `planning_effort` hint, which the user confirmed at
  `plan-intent`; when it is not `low`, the Host states why Planning is skipped anyway. PADRs already in the draft are
  listed, because the handoff promotes them to accepted ADRs. No size limit applies.
  (ADR-eligibility-for-direct-acceptance)
- **Source-bound review reports**: use the proposal's report identity and exact-source validation contract. The agent
  authors a language-specific briefing; deterministic services validate its structure and references and store it
  through the shared adapter. The Host owns semantic comparison. Storage and presentation confer no approval. Publish
  after the final worker commit to avoid a report/commit cycle. TTL regeneration occurs outside a pending form and
  always requires fresh review. (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
- **Native lifecycle approval**: a native `spec_plan_accept` form explicitly authorizes acceptance commit, checked
  local merge, disclosed cleanup and optional handoff. `accept_only` and `accept_and_handoff` have distinct effects.
  Holds are nonmutating, not rejection. Existing integration owns readiness/policy and exposes only a typed in-process
  composition seam; no public token, forged form reply or generic bypass is added. Use exact base equality, narrower
  than general integration's permitted moving-target behavior. Required-PR remains on the separately approved existing
  flow. (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
- **Partial failure**: return truthful step progress after partial failure. A partial return/restart grants no
  remaining authority; fresh inspection and approval describe only remaining effects. No rollback removes user
  changes. Standalone handoff uses an exact accepted-base report and remains explicitly approved.
  (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
- **Viewer exception**: a narrowly scoped supersession of `ADR-read-only-local-server-over-git-refs` permits only
  registered-local-adapter, exact-generation `proposal-review` artifact reads outside Git. Git-only ordinary
  endpoints, loopback/Host/no-CORS protections, sanitization, no write/approval endpoints and no server regeneration
  are retained. No arbitrary filesystem or remote URL lookup is permitted. The viewer remains optional and never
  auto-starts. (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
- **Proposal boundary rule**: a new rule `RULE-proposal-boundaries` in the devkit-spec bundle, linter phase, severity
  warning, with its guide and tests in its folder. It reads every proposal anchor
  (`docs/proposals/PROP-<slug>/proposal.md` and single-file proposals) whose `status` is `draft`, `reviewing` or
  `accepted`; `rejected` proposals are skipped. It reports on the anchor, the line of the entry. A run reports a
  proposal when the anchor is in the run's targets or in a whole-workspace run; there is no deleted-path rescan, and a
  run targeting `.devkit/config.toml` does not recheck proposals. Not fixable: the rule cannot know the intended area.
  (ADR-proposal-boundaries-name-existing-paths)
- **Checked entries**: `target_area` (a string, optional; absent is not reported) and every `boundaries.owns` item. A
  non-list `owns` or a non-string item is reported as malformed. `boundaries.excludes` is not checked.
  (ADR-proposal-boundaries-name-existing-paths)
- **Resolution**: an entry is normalized with `devkit_spec.entrypoints.normalize` (absolute paths, `..` and glob
  characters are reported as invalid) and resolves when it names an existing path, with the snapshot semantics of
  `devkit_spec.entrypoints` existence checks, tried in this order: relative to the repository root; relative to the
  proposal's namespace docs root (`docs/packages/<name>/`, when `namespace` names a registered namespace), then to
  `docs/`; as a capability area under `<namespace docs root>/capabilities/`, then `docs/capabilities/`. A trailing `/`
  requires a directory. A bare entry that matches a repository directory resolves there; the guide says so.
  (ADR-proposal-boundaries-name-existing-paths)
- **Placeholder**: an entry containing `<...>` (the template's `capabilities/<area>/`) is reported as a placeholder,
  with its own message and fix (name the area), not as a missing path. (ADR-proposal-boundaries-name-existing-paths)
- **Boundary procedure**: before the `plan-accept` request the Planning executor runs `devkit rules check` on the
  proposal and clears every `RULE-proposal-boundaries` report (`workflows/sdd-proposal.md` gate rules, next to the
  `dev_effort` review). An accepted proposal whose owned path later moves keeps its warning; Development treats a
  boundary that no longer holds as a problem and a close, never an edit of the proposal.
  (ADR-proposal-boundaries-name-existing-paths)
- **Paths Development will create** (the user's answer `new-boundary-paths`, historical Git
  `5551f9f4fc2920b973276aa43a2b0e36778c2f7a:docs/proposals/PROP-envelope-record-gaps/envelopes/answer-01.yaml`): the
  proposal names the nearest existing parent directory in `target_area` or `boundaries.owns` (for example
  `packages/devkit-spec/src/devkit_spec/bundle/rules/` for a new rule folder) and names the new path itself in the
  proposal text. No new frontmatter key or entry marker; handoff copies the boundary unchanged. The rule's guide and
  the proposal template comment state this form. (ADR-proposal-boundaries-name-existing-paths)
- **Planning feedback storage**: Planning writes feedback at `docs/proposals/PROP-<slug>/feedback/<name>.md`, with
  `FB-<name>` and existing feedback frontmatter. Planning's worker write boundary stays unchanged. At handoff,
  `status: open` files move to the new spec's `feedback/`; files with `promoted`, `dismissed` or `forwarded` status
  follow the existing preserved-materials path. No status is changed. (ADR-planning-feedback-in-proposal)
- **Feedback retirement without handoff**: on rejection or return for decomposition, keep the feedback in the proposal
  until it would be deleted. The Host performing deletion moves open observations to
  `specs/<current-month>/feedback/<today>-<name>.md` first, in the same commit. Do not duplicate observations across
  decomposed children. Settled records remain available in Git history. Invalid input, collision or an unsafe path
  prevents relocation and deletion; never guess that malformed feedback is settled. Before deleting a proposal without
  handoff, preserve source Git revision/path context and convert only historical evidence mentions of retired
  proposal/PADR/settled-feedback IDs to the existing strikethrough convention. Update relative links for moved
  feedback and validate current document references. An unresolved live dependency prevents deletion; it is not
  reclassified as historical evidence. Handoff relocation participates in its existing validation, rewrite and
  rollback guarantees. (ADR-planning-feedback-in-proposal)

---

## 5. Consequences

- **Positive**:
  - A partial direct acceptance cannot be handed off and can be repaired; a bound Planning acceptance whose gate record
    is missing is caught too, goes to the user and is recovered by reverting the Planning merge to `draft`.
    (ADR-direct-acceptance-command-and-handoff-guard)
  - A draft that fails a mechanical check runs Planning; the refusal names the failed condition. A draft that passes
    but that the Host judges unsettled is proposed for Planning, with the reason; the Host never proposes direct
    acceptance silently, and the user may still choose Planning for an eligible draft.
    (ADR-eligibility-for-direct-acceptance)
  - Feedback IDs, statuses and observation dates survive moves; names are selected unused across the repository.
    (ADR-planning-feedback-in-proposal)
- **Negative / Risks**:
  - Depth escalation has no frontmatter marker, so that exclusion stays a judgment; a marker is not added for it.
    (ADR-eligibility-for-direct-acceptance)
  - More modules participate in review and approval, but responsibilities stay in their domain packages. Host-specific
    URI clickability and native form rendering need separate live evidence. Local missing MCP tools pause dependent
    work and request connection. Cloud CLI and MCP-invisible template work stay separate.
    (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
  - Warnings do not refuse commits (`GATE_RULES_WARNINGS`); a draft or a reviewing proposal with a placeholder
    commits. A project can raise the rule to error with its own severity override.
    (ADR-proposal-boundaries-name-existing-paths)
- **Follow-ups**:
  - Every party that records an acceptance (the Host locally, autohub) stops editing the `status:` line by hand; the
    `sdd-proposal` gate rules and the `spec` skill name the command. Tests that hand off a bound proposal with only
    `status: accepted` must record the gate; tests of the carried note change.
    (ADR-direct-acceptance-command-and-handoff-guard)
  - Direct acceptance extends `ADR-roadmap-in-repository`, whose interim rule ("until a direct-acceptance path exists,
    a small draft runs Planning at `low`") it ends, and qualifies `ADR-run-records-and-activity-branches` (every
    proposal activity on `plan-<slug>` or `dev-<slug>`): a direct acceptance is Backlog work, and the proposal has no
    Planning activity. (ADR-direct-acceptance-command-and-handoff-guard)
  - The shared adapter proposal must be accepted and implemented first; source-bound review changes no current
    authority until accepted, implemented and reconciled.
    (ADR-source-bound-review-reports-and-explicit-lifecycle-approval)
  - devkit-spec: the rule, its guide and tests, its registration, the proposal template comment (the accepted forms),
    `CAP-DLV-proposal-incubation` (proposal frontmatter), `CAP-GOV-spec-rules` (the rule catalog with its warning
    severity) and the `plan-accept` rule of `workflows/sdd-proposal.md`. (ADR-proposal-boundaries-name-existing-paths)
  - Feedback discovery/deduplication includes live proposal-local feedback, including rejected proposals awaiting
    cleanup. Path validation and relevant guides expand; no new document kind, status, general storage root or
    permission is added. Strategy 01 §6.2 is updated; capture/sweep timing is specified by
    `SPEC-planning-feedback-capture`, and this record decides storage and retirement only.
    (ADR-planning-feedback-in-proposal)

---

## 6. Confirmation

- `RULE-proposal-boundaries` and its tests in its rule folder.
- `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` is raised by `devkit spec proposal handoff` for a bound proposal without an
  effective accepted `gate:plan-accept`.
- Otherwise review only.
