---
id: CAP-HARN-agent-guidance
title: Agent Guidance Assets
summary: "Agent guidance routes task instructions through SDD and coordinator-led adaptive development with active delegation, and covers idea discovery, deep research, milestones and local-orchestrated verification."
area: harness
status: active
created_at: 2026-10-13
usecases:
  - UC-route-development-intent
  - UC-advance-an-idea
  - UC-research-an-idea-and-shape-a-roadmap
  - UC-adopt-in-an-existing-repository
  - UC-adopt-sdd-from-adaptive-development
  - UC-handle-delivery-problems-and-exceptions
  - UC-resolve-stale-activity-branches
  - UC-drive-development-to-integration
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
  - packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/SKILL.md
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md
---

# [CAP-HARN-agent-guidance] Agent Guidance Assets

## 1. Summary

The `spec` bundle (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, registered through the `devkit.bundles` entry point `spec`) is the
half of devkit-spec an agent reads: it tells every session how spec-driven delivery works, which route a request
takes and which procedure each stage runs. devkit distributes it like any content package
(`CAP-DIST-manifest-spec`): `devkit
sync` copies the assets to `.devkit/managed/spec/`, projects skills and role contracts into each agent host's native
directories and writes the guidance pointer into the root `AGENTS.md` block.

## 2. Scope & Boundary

- **In-Scope**: the bundle manifest and presets, the constitution,  the guidance pointer, the
  `spec*` skills and their references, the playbooks and proposal template; the role
  contracts as deployed assets.
- **Out-of-Scope**:
  - Workflow definitions: `CAP-DLV-delivery-workflows`; role contracts: `CAP-DLV-delivery-roles`.
  - The rule assets and their guides: `CAP-GOV-spec-rules`.
  - The commands the guidance invokes: `CAP-HARN-command-mount` and the capabilities it lists.
  - Distribution, projection, context loading and playbook search themselves: devkit.
- **Non-Goals**:
  - **Scope Excluded**: host-specific content. Skills and role contracts are written once, host-neutral; devkit
    projects them per host (`.claude/`, `.agents/`, `.codex/`).
  - **Scope Excluded** (`ADR-document-system`): seeding `docs/` by default. An existing `docs/` tree never
    receives files it did not ask for.

## 3. Business Rules & Policies

1. **Context first**: WHILE the shared development approach is SDD, an agent MUST read the constitution (`devkit get-context spec`) once per agent context before
   development work, including work started without a skill, and read each relevant instruction body before the
   action it governs. An instruction never overrides a mandatory check; a conflict is reported, not resolved by
   picking one. Every role contract under `subagents/` runs `devkit get-context spec` itself, so nested roles load
   the same lifecycle context. Before document work, SDD also loads `devkit get-context docs`; docs owns shared
   writing instructions and the steering summaries. Read relevant steering bodies when their summaries concern
   the decision (`ADR-document-system`).
2. **One pointer in `AGENTS.md`**: the bundle adds exactly one line to the root `AGENTS.md` guidance block (the
   `spec-pointer` fragment); everything else is reached through `devkit get-context spec` and the skills.
3. **Managed files are read-only**: files under `.devkit/managed/` and projected agent files are never edited;
   project changes go through `devkit override` or the project's own bundle.
4. **Classification**: WHILE the approach is SDD, the `spec` skill MUST classify work on `task-kind`, then `planning-depth`, then per activity
   the mode and `activity-effort`, after reading `devkit spec policy`, propose the classification for the user to
   state at intake (for `proposal` depth, scaffolding `planning_effort` and provisional `dev_effort` hints on
   `proposal.md`, refining `dev_effort` before `plan-accept`, and using `dev_effort` from `handoff` as the default
   Development start hint while recording confirmed run effort only on `worker-NN.yaml` envelopes), and drive the one
   workflow `sdd-<planning-depth>[-<task-kind>]` (`CAP-DLV-delivery-workflows`). `planning-depth` follows what must be
   settled before implementation, not size.
   Unit depths write `spec.md`, `plan.md` and `tasks.md` before production code; a `session` task writes no Unit,
   envelope, gate record file or reconcile document. The Host raises the depth on its own judgment (`[tool.spec]
   depth_escalation = "ask"`: after the user's confirmation), never lowers it except through a proposal's handoff or,
   on the user's explicit decision at pickup, the session reclassification of a queued draft
   (`ADR-delivery-classification`), and a `session` → `spec` raise keeps
   the work by adding a spec Unit; Development never returns to Planning, and a wrong direction is a close (depth
   escalation, supersede or abandon) under a new slug. The mode is chosen per activity: `direct` by default,
   `local-orchestrated` and `cloud-pr` only on the user's instruction. Explicit user instructions take precedence.
5. **Progressive disclosure**: a skill loads only the instructions and references of the current phase; a reference
   names the moment to read it ("Read this before ...").
6. **No session hijacking**: agents MUST NOT unilaterally terminate the user's session or stop active work without
   user direction.
7. **Playbooks offered at intake, run on confirmation**: playbooks are occasional procedures, not part of routine
   delivery. The `spec` skill runs one `devkit playbook search "<English query>" --limit 3 --max-bytes 4096` as the
   first step of a new task intake, before classification (`ADR-decision-ledger`). Intake is a
   `/spec <intent>` or a user's own message outside the agreed scope of the current task; continuations, same-task
   follow-ups, explicit entries, steps inside a selected playbook and information-only questions skip it, and so does
   every later intake once the user declines playbooks for the conversation; a declined candidate is not offered
   again. A candidate is offered, in at most one line with the classification statement, only when its description
   names the operation the request asks for (never a topic match), covers the main operation and fits the requested
   scope; scores never decide. Nothing of it runs before the user confirms, and the confirmation is its explicit
   invocation; the intake reply ends with the offer and waits for the answer before a Unit, branch or edit is created. No match and search errors stay silent. The post-selection procedure is the `spec` reference
   `references/playbooks.md`, read only on a match; no `spec-playbook` skill exists. Explicit invocation through
   `devkit-playbook` and failing-rule remediation stay available.
8. **Templates by path**: shared documents start from `.devkit/managed/docs/templates/<kind>.md`; the proposal template stays under spec; seeded files are
   written once where absent and are project-owned afterwards.
9. **Skill names**: every skill of the bundle is named `spec` or `spec-<procedure>`. Rationale:
   `ADR-document-system`.

## 4. Interfaces & Data Contracts

### 4.1 Manifest and Presets

`bundle.toml`: `schema = 1`, `name = "spec"`, `version`, `default_preset = "core"`, `auto_select = true`.

| Preset | Selection | Assets |
| --- | --- | --- |
| `core` | Automatic on `devkit sync` (`auto_select`) | Lifecycle guidance, five lifecycle rules, proposal template, skills, workflows, role contracts and playbooks. |

The devkit-docs wheel auto-selects docs:core for shared document guidance. Its optional `docs:docs-skeleton`
preset seeds absent document files. The supported SDD setup selects both core bundles.

A project opts out of the bundle with `[presets] spec = false` in `.devkit/config.toml`. The constitution
(`AGENTS.md` at the bundle root) is deployed to `.devkit/managed/spec/AGENTS.md` whatever the presets.

| Asset kind | Assets |
| --- | --- |
| `instruction` | Shared instructions belong to docs:core (`CAP-DOCS-document-model`); spec declares none. |
| `guidance` | `spec-pointer` |
| `rule` | `task-coverage`, `spec-lifecycle`, `spec-progress`, `reconcile-contract`, `proposal-boundaries` (`CAP-GOV-spec-rules`) |
| `skill` | the 15 skills of 4.4 |
| `workflow` | `sdd-session-feature`, `sdd-session-bugfix`, `sdd-overall-refactor`, `sdd-spec-feature`, `sdd-spec-bugfix`, `sdd-proposal` |
| `subagent` | `challenger`, `reconcile-reviewer`, `code-reviewer`, `ux-reviewer`, `scout`, `triage`, `decomposer`, `planning-worker`, `development-worker` |
| `playbook` | `brownfield-adoption`, `sdd-baseline`, `feedback-hygiene`, `adr-consolidation`, `feedback-consolidation` |
| `document` | `templates` holds the proposal template. docs owns the shared templates and optional skeleton. |

### 4.2 Constitution

`devkit get-context spec` returns `{"bundle": "spec", "constitution": <text>, "instructions": [],
"documents": [], "documents_elsewhere": [], "notices": []}` (the result keys of `CAP-DIST-context-and-playbooks` 2;
the spec bundle declares no context directory). Shared instructions and steering summaries are returned by
`devkit get-context docs`.
The constitution's sections:

1. **Context**: read it once per agent context and each relevant instruction before the action it governs; a
   mandatory check wins over an instruction.
2. **Living Spec and Scope**: `docs/` holds the current contract; feature specs are `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/`;
   shared document context loaded through docs; namespaces under
   `docs/packages/<name>/`; references by full ID; Non-Goals and `_Boundary:` are the expected scope.
3. **Classification and Authority**: the three axes, the `sdd-<planning-depth>[-<task-kind>]` workflow names, raising
   and lowering the depth, the approval boundaries `plan-accept`, `proposal-handoff` and `dev-integration` with
   `ask|auto`, task scope authorized by an explicit instruction, and policy read through `devkit spec policy`.
4. **Verification and Completion**: compare diff, requirements, check results and Living Spec impact before
   reporting completion; a `session` task reports in its final response or PR body.
5. **Managed Files**: template paths, policy read through `devkit spec policy`, managed files changed only by override.

### 4.3 Shared Instructions and Guidance Pointers

Agents SHOULD read the global glossary and UX object register together with the selected registered namespace's
`docs/packages/<name>/steering/glossary.md` and `ux-objects.md` when they exist. Local glossary definitions apply
only to that namespace. Shared object rows stay global, local rows stay in that namespace, and registers are created
only when their rows are needed; global content is never copied into every namespace (`ADR-namespace-steering-registers`).
Agents SHOULD check object representations and calls to action against both registers during UX review; the link
and coverage rules do not parse those registers or enforce their vocabulary semantics.

The following instructions belong to docs:core. SDD decision supersession, completed-spec preservation and
Planning-only UX timing belong to the spec constitution.

| Asset | Read before |
| --- | --- |
| `contract-authoring` | Authoring or reviewing specifications, acceptance criteria, policies, instructions, rules or workflows: RFC 2119 wording, measurable contracts, Non-Goals, examples (policy exceptions are in the spec constitution). |
| `living-spec-writing` | Authoring, editing or reviewing `docs/` or `specs/`: current-state writing, approach-owned retention boundaries, traceability, summaries, ID references, and terminology and the global-plus-selected-namespace steering glossary: six domain-neutral naming rules in its Glossary section (`ADR-writing-and-terminology-guidance`) that inform naming, enforce nothing and do not authorize renaming code, APIs or schemas. |
| `document-writing` | Writing or editing any document: the sentence-level baseline (one directive or claim per sentence, condition first, prohibitions with their alternative, one-clause reasons with background by ID, no hedges or emphatic capitals, one default, concrete examples); the per-kind instructions add to it. |
| `decision-writing` | Writing an ADR or PADR: the admission criteria both share (costly to reverse, cross-area, weighed options, a changed contract; other choices stay in proposal or spec records), Y-statement `summary`, context, drivers, options, a Decision Outcome of declarative clauses where a restated clause ends with its trace (`→ <ID> <section or rule> (<keyword>)`; the restating document stays authoritative), consequences and the `Confirmation` section naming the check, test, review or restating IDs. |
| `capability-writing` | Writing a capability: EARS business rules (`WHEN`, `WHILE`, `IF ... THEN`, `WHERE`) with RFC 2119 keywords and their enforcing rule or test, scope owners, exact interfaces. |
| `usecase-writing` | Writing a use case: goal, main success scenario, extensions keyed to its steps, postconditions, Example Mapping to Given/When/Then scenarios, UX step citations (the screen a step happens on, `off screen: <reason>`, long-running activities and system judgements cited by perceived outcome). |
| `ux-writing` | Writing a UX document (`docs/ux/`) or a Screens draft: one screen, modal or panel per document, purpose, content tree without character-cell layouts, states, interactions naming the served step, criteria for surfaces beyond pages and forms (element choice, continuous input in prose with `global:` rows, modes as states, transitions, task-less surfaces, mismatch recorded as feedback; `SPEC-ux-writing-non-page-surfaces`), contrasting candidates, root and selected namespace `steering/ux-objects.md` registers created only for needed shared/local rows, style and medium left to the project (`ADR-ux-screens`). |
| `architecture-writing` | Writing `docs/architecture/`: arc42 placement, C4 diagram scope, constraints with their enforcing check (fitness function) or "review only", quality-attribute scenarios. |

- **Instruction headers**: every writing instruction of the docs bundle and the `authoring` bundle's
  `agent-asset-writing` MUST have a `description` that starts with `Read before` and stays within 300 characters.
  Check: `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` (docs bundle) and
  `packages/devkit/tests/integration/bundles/authoring/test_bundle.py` (the `Read before` prefix only).
- **One owner per writing rule**: a writing rule MUST be stated in only one writing instruction of the docs bundle;
  the per-kind instructions add to `document-writing` instead of restating it. Rationale:
  `ADR-writing-and-terminology-guidance`.

The `authoring` bundle's `agent-asset-writing` instruction applies to skills, playbooks, instructions and
subagents. Authors SHOULD load role-specific placement, delegation and path-resolution guidance from the
skill-authoring playbook's `references/roles.md` only when authoring delegated work or role-file paths. The common
instruction SHOULD retain only a conditional route to that reference; the playbook SHOULD link it at the
applicable step (`ADR-role-authoring-reference`). Authors SHOULD keep a role used only within one skill in that skill's `roles/<role>.md`, unless
independent selection or required role-specific host settings justify registering a subagent. Authors SHOULD
separate procedural instructions from native settings and state that Markdown does not enforce tool or sandbox
permissions. The skill-authoring playbook retains its skill/playbook authoring trigger without expanding into
native subagent configuration authoring.

For skill-local delegation, authors SHOULD route the child to its assigned absolute role path and first read,
with a goal, relevant sources, read/write boundaries, permitted actions, stop condition and expected return.
Authors SHOULD name the subagent type per role or assignment: `role-worker` by default
(`CAP-DIST-agent-projections`), the host's general subagent (`general-purpose` on Claude Code) for a role that needs
a capability outside the `role-worker` tool list, and the skill's own delegation for a child that holds commit
authority or worktree ownership, such as adaptive-dev's builder role. A missing `role-worker` stops that delegation
with its cause reported, never a runtime fallback (`ADR-role-worker-subagent`). Test:
`packages/devkit/tests/integration/bundles/authoring/test_bundle.py`.
Authors SHOULD specify fresh context without parent conversation inheritance where supported and report the
limitation otherwise. Unavailable delegation or permissions leave explicit missing coverage. Review checks these
semantic criteria; authoring bundle tests check distribution, self-containment and size.

The `spec-pointer` line in the root `AGENTS.md` block: run `uv run devkit get-context spec` once per agent context
before development work; start work with `/spec <intent>`, each new task intake running its intake step first (so
the rule survives a lost skill body), orient with `/spec-next`; `docs/` is the current-state
Living Spec and `specs/` holds feature specs.

### 4.4 Skills

| Skill | Purpose | Commands it runs (under `devkit spec`; `docs ...` under `devkit docs`) |
| --- | --- | --- |
| `spec` | Entry router: classify the work, run Backlog (direct acceptance and session reclassification of a draft included) and inline Planning, raise the depth and close, drive the workflow; first runs intake playbook discovery with devkit's `devkit playbook search` (principle 7). | `policy`, `new`, `proposal new`, `proposal check`, `proposal accept`, `proposal handoff` |
| `spec-next` | Orientation: diagnose work under way; when idle, filter queued drafts by direct prerequisites on one local base snapshot, then rank by repository milestone, priority and size, offering Planning, a direct acceptance or a session reclassification. | `policy`, `docs list spec\|proposal\|feedback`, `proposal padr`, `proposal accept --check`, `proposal accept-plan`, `proposal handoff` |
| `spec-specify` | Write `spec.md` (feature or bugfix reference); creates the bundle with `devkit spec new`. | `new`, `docs list`, `docs refs`, `docs search`, `policy` |
| `spec-plan` | Write `plan.md`: design, interfaces, verification plan. | `docs list`, `docs refs`, `docs search` |
| `spec-tasks` | Write `tasks.md` with `_Boundary:` and `_Requirements:`. | `docs list spec` |
| `spec-review` | Verify the change against the spec, the diff and the checks before completion. | |
| `spec-ux-review` | Run by the `ux-reviewer`: walk each linked use case through drafted screens and score each screen on six rubric items with evidence, before code, without severity, at most two rounds (`ADR-ux-screens`). | |
| `spec-sync` | Reconcile the change into the Living Spec and resolve `reconcile.md`. | `docs list`, `docs refs`, `docs search`, `proposal new` |
| `spec-integrate` | Prepare integration: conflicts, re-verification, reconcile confirmation and cumulative check; obtain Host conversational approval, then run `devkit integration integrate` and recover from observed Git or PR state; clean up. | `policy`, `scope sweep`, `proposal prune` |
| `spec-delegate` | Delegate to a role contract as the `activity-effort` asks, compare working-tree snapshots taken before and after a support role, record its envelope (none for a Backlog role), validate a worker's committed range and handle its questions and problems. | |
| `spec-review-proposal` | Review a committed proposal and all PADRs; preserve exclusive Planning ownership during refinement, commit/review changes and present findings for approval. | `proposal report`, `proposal accept-plan` (local), `proposal accept` (other environments), `proposal handoff` |
| `spec-orchestrate` | User-invoked `local-orchestrated` mode per activity: one-shot Planning and Development workers in their own worktrees, the Host keeping preparation, validation, questions, problems and integration; a plain instruction returns to `direct`. | `new`, `proposal accept-plan`, `scope collect` |
| `spec-rule` | Author or tune a project rule for `devkit rules` in the project's own bundle. | |
| `spec-feedback` | Record and sweep feedback observations (`specs/<YYYY-MM>/feedback/`), after looking up existing feedback of every status. | `docs search`, `docs list feedback`, `docs resolve`, `policy` |
| `spec-entrypoints` | Derive capability and use case entrypoints from spec bundles, review and apply them. | `entrypoints derive`, `docs list capability` |

Skill references, each read at the moment it names: `spec/references/completion.md` (completion classification,
policy, Host conversational approval and CLI execution, reconciliation evidence),
`spec/references/depth-and-close.md` (raising the depth and closing without a merge),
`spec/references/source-feedback.md` (tasks that address named feedback), `spec/references/playbooks.md` (offer, records and
use of a playbook intake discovery found, read only on a match), `spec/references/envelope.md` (return
envelope, final change report, integration result), `spec/references/git-policy.md` (worktree, pull request and branch cleanup levels), `spec/references/worktree.md` (task worktree start, work, Host-approved CLI integration and observed-state recovery, leftovers),
`spec-next/references/post-handoff.md` (follow-up of `[REWRITTEN]` and `[UNRESOLVED_LINK]` lines),
`spec-next/references/workflow-signals.md` (`devkit workflow next` lines and advisories),
`spec-delegate/references/hosts.md` (spawning a role on each host), `spec-delegate/references/payload.md` (payload
fields and rows per role), `spec-specify/references/feature.md` and
`bugfix.md`, `spec-specify/references/screens.md` and `spec-sync/references/screens.md` (drafting and writing
screens), `spec-review/references/scope-extension.md` (reviewing a grown `_Boundary:`),
`spec-integrate/references/recovery.md` (base merge after a Git refusal, unknown or partial results, remote deletion
failure), `spec-orchestrate/references/recovery.md` (context loss, returning to `direct`),
`spec-feedback/references/sweep.md` and `template.md`, `spec-rule/references/config.md` and
`templates.md`, `spec-entrypoints/references/backfill.md`.

### Delegation evidence and integration responsibilities

The Host payload names necessary official-documentation reads separately from external-service mutations; it grants
no blanket network or sandbox exception. When workers cannot read the sources, the Host provides verified evidence.
Design-critical facts that remain unverified are exposed as problems or questions, not settled design.

For intended moves or deletions, the Host checks ID references and path links before delegation and grants exact
link-repair-only document paths. Unexpected repair targets require narrow boundary expansion before editing.
Workers retain their strict write boundaries.

For changed bundle sources, the Host runs `devkit sync` in the source worktree and commits tracked outputs before
approval. A local conflict-free moved target needs no source base merge; Git conflicts or `ff-only`/PR ancestry
refusals require source preparation and re-verification. Generated conflicts may be seeded and disclosed.
After landing, the Host synchronizes dependencies in a fresh process, synchronizes bundles, regenerates stale
tracked artifacts and commits before final checks (`ADR-post-merge-verification`).

### Host scope observation

Task writing, reconciliation and worker acceptance carry no scope publication, registration or ACK obligation.
Creation retains best-effort automatic linked-worktree registration. Before scheduling or reconstructing parallel
work, the Host uses `devkit spec scope collect`, which reads creation snapshots, `plan-*`/`dev-*` refs and accessible
worktrees in one run. Fetch is explicit and separate from observation. The Host reads evidence by horizon: units whose `current`
evidence overlaps run sequentially, while a pair with only `future` evidence (a Planning unit's declared or candidate
paths) does not serialize Planning runs. Before a handoff the Host treats a unit's `future` evidence as `current`,
so units whose `future` evidence overlaps are handed off and integrated sequentially. Partial coverage and unknown
attribution inform both choices, never prove independence, and grant or refuse no write. Other-PC dirty/unpushed work is invisible; PRs improve published-change
visibility. Future cloud snapshot sharing is a direction only. `workflow next` has no collection side effect.

The contract is CAP-COLL-work-scope-registry; the rationale is ADR-host-owned-scope-observation and
`ADR-collect-only-scope-observation`. Source assets are
`spec-tasks`, `spec-sync`, `spec-delegate/references/worker.md` and `spec-orchestrate`.

### Repository verification policy

`spec-plan`, `spec-review` and `spec-integrate` follow the consumer repository's required checks. Reviewers reuse
valid results and run missing or stale checks. WHEN Git effects land, the Host MUST run final verification with
the landed runtime before reporting delivery complete. It saves the target SHA before the first merge and uses
that SHA for affected selection, preserving full fallback and frontend checks. It never compares main to itself.
After synchronization, `devkit generated check` and required regeneration/commits precede final tests, lint/types
and governance checks. A local-orchestrated batch MAY verify once after selected merges and repairs; all landed
units stay pending until the combined HEAD passes. A failed check requires in-scope target repair and recheck;
feedback alone does not complete the work. Setup/import failures are unfinished verification. Automatic rollback
and merge replay are prohibited. The report names the checked HEAD, commands and results; a moved HEAD invalidates
the current-head claim until affected checks are refreshed. Nightly/release CI remains a backstop.
This is Host procedure, not CLI enforcement (`ADR-post-merge-verification`). Guidance verification:
`packages/devkit-spec/tests/integration/bundles/spec/test_moved_target_guidance.py`.

### Feedback capture policy

`spec-feedback` reads `FEEDBACK_POLICY` from `devkit spec policy` (`CAP-DLV-project-policy`). Repository-owned
rules, skills, instructions, playbooks, workflows, roles, script/CLI tools, templates, overrides and Living Spec
documents are the base targets. `coverage=repo-and-upstream` additionally covers upstream tools used in the
session, including devkit and devkit-spec. Users describe the observation; agents never require tool ownership
classification or frontmatter from them.

- `capture=observed` records concrete observations autonomously; `requested-only` records only explicit requests.
  Enabled workflow sweeps under requested-only write a passing policy-skip envelope without recording observations;
  A `session` task reports the skip without an envelope. Stages switched off produce no sweep envelope.
- Explicit observation and session sweep requests override autonomous capture, coverage and stage restrictions;
  requested sweeps write no envelope.
- `detail=brief` keeps context, observed result or proposed change, assessment and Evidence; `standard` fills the
  kind-specific template. `detailed` adds reproduction, expected/actual results, versions, conditions, attempted
  workarounds and related assets. Missing information is `unknown`; facts are never invented. Detailed capture
  is not constrained by the brief/standard one-minute writing budget.
- `reminder=contextual` suggests an optional sweep when reusable observations warrant it; `off` disables optional
  reminders without changing required stages.

Planning feedback lives at `docs/proposals/PROP-<slug>/feedback/<name>.md`, inside the existing worker boundary;
Development uses its spec's `feedback/<name>.md`, and work without a Unit uses the month-level backlog.
Under observed capture, direct executors and both workers record concrete observations before each run's last work
commit, including runs ending on questions or problems. Capture does not depend on the sweep stage being on.

Before each Planning return to the user, an enabled sweep covers that run plus committed accumulated records,
looks up every candidate in the feedback of every status and writes fresh feedback evidence before its single worker
record. A prior PASS
does not cover later work. Requested-only writes policy-skip PASS, zero observations passes, stage-off writes no sweep
envelope and incomplete coverage records FAIL with its gap. Explicit user sweeps write no envelope. Rejection uses
recorded coverage/skip/gap and starts no new worker/Cloud Agent; it claims no sweep of a later conversation.

Handoff carries only `status: open` files into the spec and settled files into materials
(`CAP-DLV-proposal-planning`). Rejected/decomposition-return feedback stays with the proposal until deletion.
The Host then preserves open files in the month-level backlog in the deletion commit, updates links and historical
references with Git context, validates current references, and keeps the proposal on invalid input, collision or an
unresolved live dependency. Capture and relocation never change feedback status. The procedure is
`spec/references/feedback-retirement.md`; the category table is in `spec-feedback/references/template.md`.

Feedback uses `scope: repo | upstream | unknown`, determined by ownership rather than product name. An asset
developed in this repository is `repo`, even if it is shipped to other repositories; an installed upstream copy
is `upstream`. Uncertain ownership or cross-tool causes use `unknown` and stay eligible for recording. The
observed `target` is separate from the eventual resolution destination.

Before writing, every recording, direct or in a sweep, MUST look up existing feedback of every status with
`devkit docs search "<symptom and asset words>" --kind feedback --history -n 5` (a sweep adds `--all-namespaces`) and
act on the matched status (`ADR-feedback-lifecycle-ledger`). The recorder judges a hit
the same observation when it describes the same symptom of the same asset or behavior, whatever its `target` wording;
no search score decides. A consolidated record hit is decided by its entry that matches the observation. `open` records
nothing and names the existing ID (new evidence goes into that file inside the write scope, otherwise into the
report); `dismissed` records nothing unless evidence contradicts the recorded reason; `resolved` records a fresh observation, citing an existing resolved ID with `recurring: true` when available; `promoted` and `forwarded` record nothing while the destination is live and a new
item citing the ID once it ended or no longer resolves. This lookup replaced the sweep's equal-`target`
deduplication against open items; a sweep reports the matched IDs as duplicates. Source guidance checks:
`packages/devkit-spec/tests/integration/bundles/spec/test_feedback_lookup_guidance.py`.

Hygiene determines ownership and proposes local fixes or upstream report drafts; one observation may link several
resolution destinations. External submission requires explicit authorization, and `forwarded` requires an actual
report location. Pending ownership or submission leaves feedback open. Capture never changes feedback status.

Under `ADR-feedback-lifecycle-ledger`, promoted and resolved feedback are terminal. Promotion hands tracking to
follow-up work; resolution records a direct verified fix without promotion, in a session or spec. Only open feedback
needs action. Preserve source FB IDs and received scope for traceability through handoff and drafting. Terminal
sources require no completion disposition or re-verification, and follow-up completion never converts them to resolved.

The common completion procedure checks only explicit open direct-fix sources against implementation and verification:
spec work records outcomes in reconciliation, session work updates source files before its commit and reports them
without a new artifact. Resolutions name the destination, outcome and evidence; partial/deferred/unverified direct
fixes stay open with remaining scope reported. Include only source files needing these updates in task/delegation
boundaries, or have the Host apply dispositions. Recheck this task's new resolutions if later changes invalidate
evidence; do not revisit pre-existing terminal feedback. Unrelated capture stays open. Direct-fix completion applies
even under requested-only capture or a disabled collect-feedback stage, without a separate hygiene invocation.

### 4.5 Playbooks

| Playbook | Procedure |
| --- | --- |
| `brownfield-adoption` | Adopt spec-driven delivery in a repository that already has code and docs: install, take the baseline, contain legacy Markdown under `docs/materials/_legacy/` and record any deferral as a commented `.devkit/config.toml` entry the user decided, then migrate legacy content through normal work. |
| `sdd-baseline` | Verify the user-selected retained adaptive-development product through current documents, implementation and actual checks, then activate SDD under an exact-effects user decision; package selection is preparation, not activation (`CAP-DLV-sdd-baseline-adoption`). |
| `feedback-hygiene` | Triage open feedback in one batch: group by target, order by severity and recurrence, promote to rules, playbooks, decisions or spec work, or dismiss or forward, with the user's decision; above 5 open items, on a host that runs it natively, the read-only `triage` role groups and recommends from a clean checkout. |
| `adr-consolidation` | Consolidate related approved ADRs into replacement ADRs that keep the retired IDs as aliases, without changing any decision (`ADR-decision-ledger`). |
| `feedback-consolidation` | When invoked or confirmed by the user, delete eligible resolved feedback, including resolved consolidated records and aliases. Consolidate promoted, dismissed and forwarded feedback into per-area, same-status records with aliases. Protect current references, incomplete work, unmerged branches, invalid files and materials. Verify status and fidelity for consolidated outcomes (`ADR-feedback-lifecycle-ledger`). |

### 4.6 Templates

`.devkit/managed/docs/templates/{capability,usecase,ux,decision,milestone}.md` and
`.devkit/managed/spec/templates/proposal.md`: frontmatter with a required English
`summary`, the H1 `# [<ID>] <Title>` convention and the section skeleton of each document kind (`devkit spec proposal
new` and `padr` write the proposal and PADR shapes themselves; `CAP-DLV-proposal-planning`).

### 4.7 Docs Skeleton

The docs bundle's `docs-skeleton` asset seeds `docs/`, each file written once where absent and then project-owned:

```text
docs/
├── README.md                                  # entry
├── steering/glossary.md, glossary.yaml        # steering documents: terms, search synonyms
├── architecture/                              # README.md and arc42 chapters ARCH-01, 03, 05-1, 05-2, 06, 07, 08
├── capabilities/README.md, usecases/README.md, decisions/README.md, materials/README.md, ux/README.md
└── development/setup.md, workflow.md, ci-cd.md
```

The directory READMEs describe document authoring without SDD entry obligations. SDD proposal and roadmap catalog
guidance stays in the spec skill references. Existing seeded bytes stay project-owned.

The seeded `steering/glossary.md` (steering frontmatter `title` and `summary`) table is `Term | Definition | Owner | Avoid | Code identifiers` (`ADR-writing-and-terminology-guidance`):
the definition also states what a term excludes, `Owner` is the defining document ID or owning component, `Avoid` lists
rejected synonyms (also synonyms of the term's cluster in `glossary.yaml`) and `Code identifiers` the matching fields,
types and paths. Its "Avoided Generic Nouns" section holds the project's additions to the `living-spec-writing` default
list and its accepted exceptions, and the file points to that instruction. A project-owned glossary with older columns
is not migrated; the instruction's fallback records the same fields in its existing cells.

Every seeded ID-bearing document MUST parse without document-index problems and resolve by its declared ID.
The package regression test verifies all seeded architecture IDs and preservation of customized content. The
consumer wheel smoke installs devkit-spec after the base-only checks, verifies its command mount, and checks
opt-in docs seeding and discovery in the installed package.

### Host-approved CLI integration

After checks, review, reconcile and the final report, the agent asks the Host for conversational approval and then
runs `devkit integration integrate`. The CLI revalidates Git identities and retained approval policy and derives automatic
authority only from that base's policy. The Host runs branch checks with the source runtime and final checks after
synchronizing the landed runtime in fresh processes. It does not accept an approval token or persist a lifecycle request. Local
and pull-request routes are explicit; after interruption, inspect Git or remote PR state and rerun only against
the observed state. Approval is never inferred from a successful prepare or a prior process result.

### Repository Backlog and next work

The spec classification reference routes Backlog to its repository-only procedure (`ADR-roadmap-and-milestones-ledger`). Immediate session/spec requests use inline Planning; every request not starting now and every decomposition result is a draft proposal. Decomposed_from and supersedes preserve request origin through handoff. Backlog reviews feedback, places drafts in milestones and prepares explicit user decisions for milestone activation, closing and dropping. On the user's explicit `plan-accept`, Backlog may accept an eligible draft directly on the base checkout, after `devkit spec proposal accept --direct --check`, the Host's judgment that the direction leaves nothing to compare and its sweep of the acceptance session, with no Planning branch, run, effort or worker envelope (`ADR-proposal-acceptance`); this ends the earlier interim rule that small drafts run Planning at `low`. On the user's explicit decision at pickup, a queued draft without PADRs whose work is `session` depth may be deleted in one base commit that preserves its open feedback and done as a session under a new slug (`ADR-delivery-classification`). Backlog may delegate a split to the read-only `decomposer` role, only for a merged `needs_decompose` return, the user's request or an `XL` draft; `size: XL` means the work would need two or more specs or a different `task_kind`, and such a draft cannot start Planning (`CAP-DLV-proposal-planning`): the agent decomposes it (split or promote to a milestone) and never edits the size to pass. The Host judges `size` against that definition and shows it at intake. Before and after a Backlog role run the checkout is clean; the Host resolves every cited ID, requires proposed slugs to be unused, applies only what the user decides and names the role in the Backlog commit body, with no envelope. Session reclassification also requires no `size: XL`. No issue field, tracker intake/closing or autohub dependency applies.

Milestones are MS documents at the global or a registered namespace's roadmap root (`ADR-namespace-milestone-roots`) with goal, exit condition and non-goals, never copied work lists. User and agent jointly review the theme and decompose it into direct PROP members. Only proposal anchors declare membership; handoff omits milestone metadata and historical SPEC metadata is ignored. Milestones are loosely managed themes that bind nothing: proposal Planning concretizes and settles scope and requirements, and guidance never uses a milestone's goal, exit condition or non-goals as constraints on design options. Prefer a multi-unit phase, release or architectural theme advancing `ARCH-01-introduction-and-goals`, with observable phase-level outcomes and capability boundaries, over a milestone that only sequences one proposal; a theme may begin with one proposal while broader intended scope is not authored. CLI flags, branch names, file layouts and scenario tests belong in proposals/specs. Activation shows unmet dependencies but permits an explicit out-of-order decision. Close planned/active milestones through one current Backlog candidate: sufficient decomposition, direct proposal work delivered or explicitly excluded/moved, and the exit condition met for the resulting agreed scope. Inspect all direct PROP members across namespaces, the selected local base (report its commit without claiming remote freshness) and relevant known Planning/Development activity; focused code/Git inspection resolves missing proposals without reconstructing delivery lineage. Handoff, deletion, rejection, reassignment and empty membership alone never prove delivery. Outstanding in-scope work, an unmet exit condition or inconclusive required evidence keeps the milestone open with the remaining check named; missing confirmation is a separate gap. The user confirms both plain body assertions and status done together in one Backlog commit, without a third approval. Recheck scope, membership and relevant evidence immediately before writing; unchanged authorization survives interruption or context compaction, while material changes or an unestablishable approved candidate/evidence require reconfirmation. Actual semantic scope changes (new required work, exclusion or moving scope elsewhere) reset both assertions to pending in the authorized scope edit. Normal handoff/mechanical identity relocation does not change scope/decomposition and requires no milestone review, reset or reconfirmation. No pre-handoff or integration hook is added; relevant completion evidence is checked at close. Pure wording/format corrections preserving meaning do not invalidate. Extending done scope requires user-owned reopen to active with pending assertions or another milestone. Unchanged done writes nothing, dropped is not a close candidate, and existing done assertions remain unchanged during approved content-preserving relocation. Drop prepares member reassignment/clearing/rejection and shows successor dependencies. Done/dropped records remain hidden history unless merged: on the user's Backlog decision, small milestones of any status MAY merge into a broader theme milestone that lists their IDs in `aliases` with both assertions pending, in one commit that deletes the merged files, runs `devkit rules fix` and removes `depends_on` edges between them; remaining scope moves to draft proposals in the theme, which stays planned or active while scope remains and closes only through both confirmations. A merge is not an in-place extension (`ADR-roadmap-and-milestones-ledger`).

Milestone storage follows `ADR-roadmap-and-milestones-ledger` and `ADR-namespace-milestone-roots`: planned/active at the
milestone's roadmap root (global or a registered namespace's), done/dropped in that root's flat `_archive/`. Close commits done, both confirmed assertions and movement together.
Drop commits the agreed member/dependency disposition, dropped and movement together without creating completion
assertions. Reopen commits active, both assertions pending and movement to the root together. These effects belong
to the existing concrete user decision; no extra archive-only gate applies. Repeating unchanged archived close/drop
writes nothing. Destination collisions stop without overwriting. Exact existing-history batches require concrete
authority and passing readers, preserve source bytes and never retrofit missing assertions. Merges work from
either location and retain aliases; the theme status selects its location. Check: rendered milestone guidance and
`test_milestone_archive_guidance.py` with labelled simulated decisions and actual Git states.


Spec-next treats a slug with a plan-/dev- branch, a reviewing/accepted proposal or an incomplete spec as in progress; queued drafts do not suppress idle recommendations. After the unit prerequisite filter below, eligible draft order is critical first, milestone rank (active, ready planned, no milestone), milestone created_at/ID, priority, size, draft created_at/ID. Unready/finished milestone, needs_decompose and XL drafts are Backlog actions (the latter two name the decomposer); unit-ready critical drafts still rank first; milestone exceptions never bypass unit prerequisites. The skill supplies deterministic ties/defaults; the CLI adds no sorting. It recommends intent confirmation when absent, offers Planning, a direct acceptance or a session reclassification for the draft, and mentions open feedback hygiene.


Proposal acceptance and handoff run through Host-authorized CLI operations (`ADR-delivery-approval-and-lifecycle-authority`).
The Host reviews the proposal, every PADR and the envelopes at the final committed `plan-<slug>` source, presents
the findings and effects, and invokes `devkit spec proposal accept-plan` only after the user's decision under `ask`.
`devkit spec proposal report` renders an optional briefing; acceptance requires no published report, while shared
proposal-review artifacts remain available for publication (`CAP-DLV-proposal-planning`,
`CAP-COLL-shared-artifacts`). A report never carries approval or permissions. Refinement requires exclusive
Planning ownership, committed changes and a fresh review of the committed source; accepted plans use follow-up
workflows.


### Direct unit prerequisites and lifecycle decisions

Backlog/spec-next and explicit proposal pickup or direct-spec intake inspect optional depends_on without a new
CLI or gate. Select one local base ref and resolve its commit once; report both and read all candidates and direct
target anchors from that snapshot across namespaces, including history. Never substitute active branch completion,
fetch implicitly or claim remote freshness. Only one uniquely resolved SPEC anchor with status completed satisfies
an edge for scheduling; do not recursively reopen that SPEC's prerequisites. This is a status signal, not task,
reconcile, approval or coverage certification. No dependencies means unit-ready. Report each blocked draft's exact
ID and reason: unfinished proposal, rejected proposal, unfinished spec, or invalid/unknown target. Missing,
malformed, ambiguous or unreadable base evidence requires Backlog repair. Filter ordinary and critical candidates
before existing milestone/priority ordering. Explicit user pickup may override order, recording unsatisfied IDs
and reasons in proposal Planning decisions or `spec.md`; it cannot waive malformed references or cycle diagnostics.

Before decompose, supersede, reject, delete or session reclassification, inspect incoming depends_on references
across all namespaces, retaining only live direct unit edges. Review each edge with the user and replace it with
the required child/successor set, or remove it only for an explicit prerequisite waiver. Apply the disposition in
the same authorized change. Stop the lifecycle mutation when dependent edits exceed the allowed scope and ask the
Host to coordinate; never edit another worker's checkout. Retained rejected PROP anchors resolve but remain
blocked. Missing targets never mean ready. Do not rewrite completed history, infer successors through provenance
or store a lineage graph. On-demand code/Git inspection can answer downstream milestone outcome questions;
proposal disappearance is not completion evidence.


## Approach-aware SDD entry

The installed spec pointer, constitution and router inspect `devkit config show` before selecting SDD routing.
For `sdd`, existing intake/classification/stage/Git/approval rules apply. For `adaptive-dev`, they direct ordinary work
to the project's adaptive-development guidance and independent checks without implicit SDD Units, per-change envelopes or
immutable iteration history. Existing explicitly bound SDD artifacts keep their checks. Installing or selecting spec
assets never switches the approach. The `adaptive-dev` bundle's entry, roles and context are separately delivered; this policy supplies no
product discovery coordinator.

An explicit `/discovery` invocation is not development intake: the spec router runs no playbook discovery,
classification or Unit creation. It follows `CAP-DLV-idea-discovery`; later implementation starts as ordinary intake.

An explicit `/deep-research` invocation is not development intake: the spec router runs no playbook discovery,
classifies it into no depth and creates no Unit for it, and work the research later informs starts as ordinary
intake. A proposal, spec or ADR cites research retained outside it by its `MAT-<slug>` ID in a code span and never
copies it into a proposal's `materials/` (`ADR-adaptive-development-and-research`).

## Adaptive development entry and current context

The opt-in `adaptive-dev:core` bundle supplies `/adaptive-dev`, conditional references, the adaptive-dev pointer, three
optional support contracts and a current-context template (`CAP-DLV-adaptive-development`). Install devkit-adaptive, which brings the document system and harness, and select `adaptive-dev` explicitly; devkit-spec is not required. The entry inspects common
`configuration.development.approach` before product work and stops on SDD or invalid policy rather than switching
approach implicitly. Independent document/project checks and retained SDD artifact protections remain applicable.

The coordinator adapts clarification, research, implementation and actual-usage verification to the next useful
action, actively delegates useful separable work and retains coordination, integration and final validation.
Product-clarifier, product-researcher and usage-reviewer provide support where useful; no action requires all roles.
Their role contracts preserve source/index/HEAD authority and distinguish emulated boundaries from native
confinement. `/adaptive-dev` neither invokes nor suggests a research entry and links a retained research material by its
`MAT-<slug>` ID. The coordinator owns mutable project context at
`.devkit/adaptive-dev.md`, including current goal/choices, source-specific run/check evidence, uncertainty and next
action. Sync owns its pristine template and preserves the project-owned file. Explicit adoption requests route to
the separately available baseline procedure; this entry does not activate SDD or reconstruct experiment history.

## Deep research entry

The opt-in `deep-research:core` catalog bundle supplies `/deep-research` with conditional orchestration, workspace
and synthesis references and four optional skill-local role documents (direction-explorer, discovery-critic, discovery-planner,
research-investigator), with no global research subagent registration or guidance asset (`CAP-DLV-deep-research`). It installs with devkit-docs and
devkit-catalog under either approach without devkit-spec, and shares no role with and depends on no other bundle.
The entry runs only on explicit user invocation: native projection disables implicit invocation and the skill body
opens with the explicit-only guard; no skill, pointer, guide or role suggests it. It inspects no approach, writes only
its transient run directory and one indexed material under `docs/materials/`, and never commits: its report directs
the commit through the project's Git policy.

## Local-orchestrated verification

The local-orchestrated Host MUST own post-integration asynchronous launch, collection, cleanup and final
integrated coverage. Development workers MUST run required native checks synchronously in their assigned
worktree, including necessary selective E2E, and return source-specific evidence. Worker payloads MUST NOT
inherit the Host exec lifecycle; common completion guidance routes to it only for the Host after landing.
Direct/session work retains native verification. Actor and task select responsibility, not directory location;
the executor CLI has no role or cwd restriction. Rendered local/cloud and worker-projection regression tests in
`packages/devkit-spec/tests/integration/bundles/spec/test_isolated_execution_guidance.py` check instruction routing;
actual agent compliance is Review only. `ADR-verification-execution-ownership` records this boundary.

Before choosing asynchronous verification, the Host inspects repository documentation, scripts, runner configuration and CI for actual required commands and coverage. It establishes independently runnable groups and verifies what the retained synchronous command excludes and what the asynchronous command covers, preserving all existing required coverage. Directory names and test labels establish neither E2E existence, cost nor independent runnability. If verification is unseparated, unclear or has no independently runnable subset, the Host keeps the existing required commands synchronously. Consumers need no E2E tier; guidance neither manufactures empty coverage nor automatically restructures verification. Overlapping broad commands do not establish reduced blocking by adding a duplicate E2E run. Devkit's selector commands are its own adoption example.

Where independent required groups are established, the source local-orch skill SHOULD start with one outstanding isolated E2E run after the project's established synchronous verification group and preserve its existing full fallback. It launches native argv at fixed A, backgrounds one `exec wait --clean` through the tool, continues independent work and collects its result. Tool notification limits, default retention and separate execution/cleanup outcomes remain explicit (`CAP-HARN-isolated-execution`).

WHILE main advances, the Host MUST retain the earliest uncovered interval, including generated repairs, and MUST NOT label A's result as testing descendant C. Before completion, current landed HEAD needs required synchronous results and passing required E2E there or an explicit empty E2E selection across the complete uncovered interval. At the next failed/unknown result check, hold further merges and prioritize repair without merge replay or automatic rollback. Git-operator remains a Git executor. Source guidance tests cover launch/work/collection ordering; actual Host compliance is Review only (`ADR-isolated-test-runs`).
