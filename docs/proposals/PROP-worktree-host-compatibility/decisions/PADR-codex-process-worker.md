---
id: PADR-codex-process-worker
title: Codex worker as a separate process rooted in its worktree
summary: Offers a Codex worker turn as a codex exec process rooted in its worktree with both git dirs granted, only once one bounded live Development turn run by the user meets the Passes criterion; otherwise, or if not run, the Codex main session keeps running the activity in direct.
proposal: PROP-worktree-host-compatibility
status: draft
created_at: 2026-10-19
---

# [PADR-codex-process-worker] Codex worker as a separate process rooted in its worktree

- **Status**: Draft
- **Date**: 2026-10-19
- **Chosen by**: the user's answers in `envelopes/answer-01.yaml` (`codex-worker-scope` = `process-worker`,
  `codex-live-turn` = `user-codex-host`).
- **Answers**: Q3 and Q5 of `PROP-worktree-host-compatibility`; option O3. Evidence: `MAT-worktree-host-spike-evidence`
  §2.2, `envelopes/scout-02.yaml`; reviewed in `envelopes/challenger-01.yaml` to `envelopes/challenger-05.yaml`.

---

## 1. Context & Problem Statement

On Codex the worker roles are `unsupported`, so the main session runs every activity in `direct`. The reason is
structural, not the worktree's location: `spawn_agent` keeps the parent's cwd, approval policy and permission profile,
a custom agent cannot override `sandbox_mode`, and `.git` plus the linked worktree's own git dir are read-only inside
every writable root unless named exactly. A process rooted in the worktree with both git dirs granted can commit there
(verified with `codex sandbox`); a subagent of a base-rooted session cannot.

## 2. Decision Drivers

- Worker delegation on Codex without weakening the Host's committed-range check.
- No host settings written by devkit (`PADR-worktree-access-preconditions`).
- No new projection status or allowlisted key in `devkit.distribution`; the change stays in devkit-spec assets.
- Codex sandboxes the Host's own commands: inside `:workspace` a nested sandbox cannot be applied, `~/.codex` is not
  writable and the network is off, so the Host cannot start the process inside its sandbox.
- What is shipped stays true whichever way the live verification ends.

## 3. Considered Options

- **Keep Codex `unsupported`; the main session runs each activity in `direct`.** Pros: no new procedure. Cons: no
  orchestration on Codex; `direct` in a sibling worktree already needs the Host's escalated writes.
- **A Codex session started by the user per worktree with the grants (O1 per run).** Cons: the user starts a session
  per activity and turn by hand; it is a second Host, not a worker the Host coordinates.
- **A `codex exec` process per worker turn, rooted in the worktree (selected).** Pros: the worker's cwd is its
  worktree; projected roles and skills are read from it (Q5). Cons: a separate model session and one escalated launch
  per turn; approval `never` inside `exec`, so any other blocked action fails; nested roles, trust for the linked
  worktree, the gate's tooling and the Host's command timeout are unverified until the live turn.

## 4. Decision Outcome

- When the live verification below passes, the worker contracts declare the process launch with the top-level
  extension key `x-process-hosts: [codex]` (a list of host ids), and their Codex block stays `status: unsupported`
  (no `.codex/agents/<worker>.toml`, no `model_reasoning_effort`). An `x-` key passes contract validation unrendered
  (`packages/devkit-dist/src/devkit/distribution/bundles/subagents.py`); `CAP-DLV-delivery-workflows` adds it to its
  list of extension keys.
- **Launch** (verified branch): in `local-orchestrated` mode on a host named in `x-process-hosts`, the Host runs each
  `planning-worker` or `development-worker` turn as one
  `codex exec -C <worktree> -s workspace-write --add-dir <repo>/.git --add-dir <repo>/.git/worktrees/<name>`
  process. The Host adds only these two grants, the sandbox mode and, when it knows its own session's reasoning
  effort, `-c model_reasoning_effort=<that effort>` (the role effort presets decision integrated on `main`: a worker
  runs at the session's effort); otherwise the process runs at the user's configured default and `CAP-DLV-delivery-workflows` says so.
  Grants the user's own Codex configuration holds stay the user's. The prompt is the effective contract body in the worktree
  (`<worktree>/.devkit/overrides/spec/subagents/<role>.md` when it exists, else
  `<worktree>/.devkit/managed/spec/subagents/<role>.md`), whose frontmatter also decides the launch, followed by the
  payload `spec-delegate` defines.
- **Launch preconditions**, stated in the hosts reference: the worktree was synced by `devkit worktree start`
  without `WORKTREE_SYNC_FAILED` (the projections a nested role needs are gitignored and exist only through that
  sync), and the worktree path is trusted in the user's Codex configuration, which loads project-scoped `.codex/`
  files only for a trusted project or worktree.
- The worker's first step is the access probe every worker runs (`PADR-worktree-access-preconditions`), so it tests
  the process's own sandbox; a refused probe ends the turn with nothing written.
- The Host starts the process outside its own sandbox (an escalated command approved by the user or the configured
  auto review); its accept step (`devkit spec scope update`, which writes the shared `.git`) and any blocking
  envelope commit need the same escalation. When escalation is unavailable or declined, the Host reports to the user
  and stops; it does not fall back to `direct`, which needs the same escalated writes. The committed `worker`
  envelope and the final head are the return, validated exactly as for a subagent worker (`references/worker.md`);
  the process's last message is not trusted beyond them.
- `spec-delegate` Step 3 and `spec-orchestrate` (its nested-subagent precondition and its rule that an `unsupported`
  worker means `direct`) MUST name the process launch as the path for a host listed in `x-process-hosts`;
  `spec-delegate/SKILL.md` stays within its tested budget (`BUDGET - 512` = 11776 bytes,
  `packages/devkit-spec/tests/test_bundle_budgets.py`; 7778 bytes on `main` at this Planning).
- **Live verification** (Development): one bounded `development-worker` turn of this proposal's spec, in its own
  `dev-` worktree, launched through this launch by a Codex Host the user runs.
  - The development-worker contract and its payload row accept a bounded `task_goal` that names spec tasks: such a
    turn does only those tasks and the support roles the `task_goal` names, leaves any hold `devkit workflow next`
    shows on the unit as it is (no `answer` or `resolution`), ends after them with `completed` and the next stage in
    its summary. The development-worker Return, `CAP-DLV-delivery-workflows` §4.6 and `spec-orchestrate` step 2 state
    the Host side: a Host may pass a bounded `task_goal`, and on its `completed` return validates the range and
    continues with a new turn or itself. This stays whatever the outcome; a contract test asserts it.
  - **This spec's Development runs in `direct` mode** on its Host. A Host rooted in the base checkout would load
    main's worker contracts and `spec-delegate`, which lack the probe, the bounded turn and the launch; in `direct`
    the Host does the work itself and never spawns from those texts. The spec's `plan.md` and its verification task
    state this; a Host asked to orchestrate this unit tells the user the conflict before it spawns.
- The live turn itself:
  - Development writes the key, the bounded turn and the launch text on its branch and re-syncs its `dev-` worktree,
    so the worktree's `.devkit/managed` and projected roles match the branch. At the verification task the Host
    first commits all its work and ends its run with a `completed` `worker` envelope at the current stage whose
    summary names the pending verification task (a `direct` Host writes one whenever it stops for the user; with no
    question and no problem `completed` is the well-formed status, and no gate reads it). That run's final head is
    the head named in the request and the start of both range checks. The pause is a step of the accepted plan (the
    `codex-live-turn` answer), not a stop on a problem; the user's report starts a new Host run.
  - The Host then asks the user in the conversation to run the turn, naming: the unit and the worktree; the head the
    Codex Host must find as the last accepted head, and the write scope and `activity-effort` for its payload; the
    bounded `task_goal` (the probe, one small task of `tasks.md` through the commit gate, its affected tests and one
    named nested support role whose return is recorded as a check of the live turn's `worker` envelope); the
    contract to launch, `<worktree>/.devkit/managed/spec/subagents/development-worker.md` (or its override in the
    worktree), whose frontmatter carries the key; the branch's `spec-delegate` text in the worktree as the Codex
    Host's procedure; the Codex Host's escalated steps (launch, rerunning the affected tests in the worktree, scope
    update, any blocking envelope commit); the fields to report; and that the base checkout and the worktree stay
    untouched outside the turn. The Development Host never runs `codex exec` itself.
  - The user starts a Codex session in the base checkout, which acts as Host for that one turn: it builds the payload,
    starts the process escalated, validates the return as the branch's `references/worker.md` defines and reports
    the fields and its final head; the user passes the report to the Development Host, or says the turn was not run.
  - The Development Host validates the live turn's commits from the head it named in the request up to the reported
    final head: that head is an ancestor of the final head, the worktree's HEAD equals the final head, every changed
    path is in the write scope it named, `git status --short` is empty, and the affected tests pass when rerun in the
    worktree. A failure is its own blocking `worker` envelope, as `references/worker.md` blocks a range, and the turn
    Fails. Then it records the evidence in the verification task of the spec's `tasks.md`: the command line, the
    codex version, the configuration mode (legacy `sandbox_mode` or a profile), the reasoning effort, the Codex trust
    status of the worktree, the worktree sync result, the base and final head, both Hosts' range-check results, the
    commit gate's result, the affected tests, the nested role spawned and the turn's duration against the Codex
    Host's command timeout. The live turn's own `worker` envelope carries its in-process
    checks.
  - **Passes** when all hold: the probe and a commit through the real commit gate succeed inside the process, the
    Codex Host's range check passes, the affected tests run and pass inside the process, a nested role is spawned
    and returns, the turn ends within the Codex Host's command timeout, the launch runs under the user's own
    configuration mode, and the Development Host's validation passes. Then the key, the launch text in
    `spec-delegate` and `spec-orchestrate`, and `CAP-DLV-delivery-workflows` ship as above.
  - **Fails** (including a test or gate failure caused only by the process's sandbox, and a turn the user did not
    run, recorded with its reason): the Development Host first commits or removes what the live turn left
    uncommitted, reverts or finishes the live turn's unfinished commits, and commits that with a `resolution` naming
    each problem envelope of the live turn (its own blocking one included); Development removes the key and the
    launch text from its branch, so nothing of the launch ships; the hosts reference and the contract comments
    record the failed condition, and Codex keeps the main session running the activity in `direct`. The bounded turn stays.

## 5. Consequences

- Changes `spec-delegate` (`SKILL.md` Step 3, `references/hosts.md`, `references/payload.md`), `spec-orchestrate`,
  the two worker contracts and their tests, `.devkit/installation.json` (managed hashes) and
  `CAP-DLV-delivery-workflows`; no devkit package change.
- Each Codex worker turn costs a separate model session and an approval.
- Development runs in `direct` and pauses once for the user's live turn, ending a Host run with a `completed`
  `worker` envelope; the result decides what ships, and either
  outcome completes Development.
- Unverified until the live turn: that legacy `-s workspace-write --add-dir` lifts the git-dir protection as a profile
  rule does (the probes used `codex sandbox -P`), how `-s` combines with a user's permission profile, whether
  `codex exec` can spawn a nested role, and whether Codex maps a linked worktree to the main repository's trust.
- The two grants give the process the same shared `.git` access a Claude Code worker has through its session; the
  range check does not see it on either host (`PADR-worktree-access-preconditions` §5).
- Claude Code keeps the native subagent; a `claude -p` launch can be added later by listing `claude-code`.
- Draft proposals touching the same files (the worker range validation proposal on `main`: `spec-delegate`,
  `spec-orchestrate` and the worker contracts; `PROP-direct-planning-procedure`: the `planning-worker` steps; `PROP-integration-follow-ups`)
  rebase onto this change when accepted after it.
