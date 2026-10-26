---
id: SPEC-backlog-subagent-roles
title: Backlog triage and decomposer subagent roles
summary: Adds isolated triage and decomposer support roles so Backlog feedback triage and draft decomposition can be delegated with verified write boundaries and preserved provenance, and gates XL drafts to decomposition before Planning.
status: completed
created: 2026-10-26
related_capabilities: [CAP-DLV-delivery-workflows, CAP-DLV-proposal-incubation, CAP-HARN-agent-guidance]
related_usecases: [UC-route-development-intent, UC-incubate-and-hand-off-a-proposal]
workflow: sdd-spec-feature
---

# [SPEC-backlog-subagent-roles] Backlog triage and decomposer subagent roles

## 1. Problem Statement & Motivation

Handed off from proposal PROP-backlog-subagent-roles on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-backlog-subagent-roles`

Backlog work runs in the main session today. Feedback triage follows the `feedback-hygiene` playbook, and splitting a
broad draft (`decomposed_from`, `needs_decompose`) is done by the Host by hand. Both read many files and fill the
coordinating context, and the Host judges its own grouping without a second view. `ADR-roadmap-and-milestones`
leaves the `triage` and `decomposer` roles as follow-ups, and `MS-backlog-subagent-roles` names them in its exit
condition.

Nothing keeps a rough `size: XL` draft from entering Planning as one unit: `XL` reads "major overhaul", which nobody
can check, and only a Planning run that notices the breadth returns `needs_decompose`.

Two read-only support roles return recommendations; the Host verifies them like a Scout or Challenger return and
applies only what the user decides. A judgeable `XL` and a deterministic gate before Planning send every `XL` draft to
decomposition first. The support-role diff check of `spec-delegate` also misses a role writing to an already-modified
file, which these Backlog delegations would inherit; the check moves to a content snapshot.

Present workload (`docs/materials/2026-10/20261026-backlog-subagent-roles/spike-findings.md` F5): few open feedback
items and no live decomposition; the value is in larger hygiene batches and the first real decompositions.

## 2. Use Cases and User Stories

- **US-1**: As the Host in a hygiene session with more than 5 open feedback items, I want a `triage` role to group and
  route them from a fresh context, so that my context stays free and the user decides on a second view.
- **US-2**: As the Host splitting a draft in Backlog, I want a `decomposer` role to propose independently deliverable
  children with their provenance, so that the split and its edges are judged before I apply them.
- **US-3**: As the user, I want an `XL` draft stopped before Planning with a directive to decompose, so that no
  multi-spec draft is planned as one unit.
- **US-4**: As the Host delegating any support role, I want the post-run check to detect every write, also to a file
  that was already modified, so that a role's boundary holds on a dirty checkout.

`UC-route-development-intent` changes: its feedback-triage route gains the optional `triage` delegation, and its
orientation reports an `XL` draft as a decomposition action.

## 3. Non-Goals

1. **Scope Excluded**: a role that writes anything, sets a feedback status, deletes a proposal or creates or changes a
   milestone.
2. **Scope Excluded**: a workflow, stage or unit for Backlog work, and a Backlog envelope location; a role's return is
   a message, recorded in no envelope.
3. **Scope Excluded**: a rule that refuses `size: XL` on a draft, or any size check other than the one predicate below.
4. **Scope Excluded**: a change to `devkit-agt` or `devkit-dist`, including a coded directive on an unmet workflow
   exit check (`FB-workflow-exit-check-without-directive`, dismissed in Planning).
5. **Scope Excluded**: automatic milestone placement or status changes; replacing any user-owned gate; external
   tracker intake or synchronization; multi-unit orchestration hardening.

## 4. Acceptance Criteria & Behavioral Contracts

The size predicate: a proposal passes when `size` is absent or exactly `S`, `M` or `L`; any other value (`XL`, `xl`, a
typo) fails, and every refusal devkit-spec prints names the allowed values.

### [AC-01] The triage contract is an isolated read-only role that cites the playbook
- **Given** the spec bundle source
- **When** `subagents/triage.md` is read
- **Then** its frontmatter has `role: triage`, `x-execution: isolated`, `x-invocation: optional`, `x-git-actions:
  [read]`, `x-model-profile: light-medium`, `claude-code` `native` with tools `[Read, Grep, Glob, Bash]`,
  `disallowedTools: [Write, Edit]` and `effort: medium`, `codex` `emulated` with `sandbox_mode: read-only` and
  `model_reasoning_effort: medium`, and `antigravity` `native` with `commandExecutionPolicy: sandbox`; its body runs
  `uv run devkit get-context spec`, cites `.devkit/managed/spec/playbooks/feedback-hygiene/SKILL.md` Steps 1 and 2,
  returns groups (FB IDs, ownership, destination with reason, duplicates, dismissal candidates) and proposes no
  status change

### [AC-02] The decomposer contract is an isolated read-only role that cites the Backlog reference
- **Given** the spec bundle source
- **When** `subagents/decomposer.md` is read
- **Then** its frontmatter matches AC-01's host matrix with `x-model-profile: general-high` and effort `high`; its body
  runs `uv run devkit get-context spec`, cites `.devkit/managed/spec/skills/spec/references/backlog.md`, returns per
  child a slug, title, summary, scope, a size below `XL`, effort hints, boundaries, edges and the inherited PADRs,
  answers and materials, the disposition of each incoming `depends_on` edge and the recommended exit (split or
  promote), assigns no open feedback to a child, and returns `needs_input` when the draft does not divide

### [AC-03] Both roles are registered, projected and validated
- **Given** a fresh repository after `devkit sync`
- **When** `devkit workflow validate --format json` runs
- **Then** it exits `0` with `ok: true` and `roles_checked: true`; `.devkit/managed/spec/subagents/triage.md` and
  `decomposer.md` exist, each role is projected to `.claude/agents/<role>.md`, `.codex/agents/<role>.toml` and
  `.agents/agents/<role>.md`, and `bundle.toml` lists both as assets and in `presets.core`

### [AC-04] Delegation guidance names the invocation points
- **Given** the bundle text
- **When** the caller guidance is read
- **Then** `spec-delegate`'s payload table has a `triage` and a `decomposer` row; `feedback-hygiene` Step 1 delegates
  `triage` when the listing has more than 5 items and the host runs it natively, and otherwise runs Step 1 inline; the
  Backlog reference delegates the `decomposer` only from Backlog, for a merged `needs_decompose` return, the user's
  request to split or an `XL` draft, requires a clean checkout before and after a Backlog role run, resolves every
  cited existing ID, requires every proposed slug to be unused and names the role in the Backlog commit body;
  `spec-next` names the decomposer in its Backlog actions for `needs_decompose` and `XL` drafts

### [AC-05] The support-role diff check sees a write to an already-modified file
- **Given** a checkout where `f` is already modified and `new.txt` untracked
- **When** a support role appends to `f` and `new.txt`, leaving `git status --short` unchanged
- **Then** the `spec-delegate` snapshot (`git read-tree HEAD`, `git add -A` and `git write-tree` under a temporary
  `GIT_INDEX_FILE`) differs before and after, `git diff --name-only <before> <after>` lists exactly `f` and `new.txt`,
  and taking the snapshot leaves the real index and `git status --short` unchanged

### [AC-06] An XL draft leaves plan-intent unmet at next
- **Given** a draft proposal bound to `sdd-proposal` with `size: XL`, or `size: xl`, under `plan-intent` `ask` and
  under `auto`
- **When** `devkit workflow next --unit docs/proposals/PROP-<slug>` runs
- **Then** it exits `0`, shows stage `intent-proposal` with the size check under `[UNMET: ...]` and `detail="size=XL"`
  (`size=xl`), and prints no `[GATE: plan-intent ...]` request; a draft without `size` and one with `size: L` show
  the request open

### [AC-07] plan-intent cannot be recorded for an XL draft
- **Given** the `XL` draft of AC-06
- **When** `devkit workflow answer --unit <dir> --request gate:plan-intent --action accept --by user` runs
- **Then** it is refused with `REQUEST_UNKNOWN` and writes no decision record

### [AC-08] A direct acceptance check names the size blocker
- **Given** an `XL` draft otherwise eligible for direct acceptance
- **When** `devkit spec proposal accept <slug> --by user --direct --check --note "x"` runs
- **Then** it fails with `SPEC_PROPOSAL_NOT_ELIGIBLE` and a `blocking:` detail starting `size: XL (decompose first:
  split with --decomposed-from or promote to a milestone` that names the allowed values; a `size: L` draft has no size
  detail

### [AC-09] Only a Planning attach is refused for size
- **Given** a draft proposal with `size: XL` bound to `sdd-proposal`, and an accepted proposal with `size: XL`
- **When** `attach_check` runs for `plan-<slug>` on the draft and for `dev-<slug>` on the accepted proposal
- **Then** the `plan-` attach returns a reason naming the size, the allowed values and both exits (split, promote), and
  the `dev-` attach returns no reason

### [AC-10] Guidance covers the Planning return, judging, reclassification and the directive
- **Given** the bundle text
- **When** the guidance is read
- **Then** `planning.md` step 1 returns a proposal whose size fails the predicate as for decomposition
  (`status: draft`, `needs_decompose: true`); the `spec` skill has the Host judge `size` against the definition and
  show it in the plan-intent request; the session reclassification conditions include no `size: XL`; the `spec`
  skill, `spec-next` and `sdd-proposal.md` read the unmet size check as "decompose first, never edit the size to pass"

### [AC-11] XL has a judgeable definition with an example of each side
- **Given** the proposal template, the scaffold comment, the seed `docs/proposals/README.md` and
  `CAP-DLV-proposal-incubation`
- **When** each describes `size`
- **Then** `XL` is defined as work that would produce two or more specs or bundle deliverables of a different
  `task_kind`; the template and the capability give one `XL` example (a new CLI command with a viewer redesign it does
  not need, or a parser bugfix with a new search feature) and one non-`XL` example (two agent contracts and their
  command checks in one `feature` spec); "major overhaul" appears in none of them

### [AC-12] A fixture decomposition preserves provenance and feedback
- **Given** a temporary repository with a draft parent that has an open feedback file and an incoming `depends_on`
  edge from another draft, and an existing proposal whose slug a proposed child reuses
- **When** the Host procedure runs: `devkit spec proposal new <child> --decomposed-from PROP-<parent>` per child, the
  edge rewired to a created child, the feedback retirement move and the parent's deletion
- **Then** each child carries `decomposed_from: PROP-<parent>`, the dependent's `depends_on` names a created child,
  the open feedback file sits under `specs/<YYYY-MM>/feedback/` with its ID and status and in no child, and
  `proposal new` on the colliding slug exits `2` with `SPEC_PROPOSAL_EXISTS` and writes nothing

### [AC-13] A dogfood triage run is recorded
- **Given** the open feedback at Development time and a clean checkout
- **When** the `triage` role runs on it
- **Then** the final change report records its return and the before and after `git status --porcelain`, both empty

## 5. Source feedback

- `FB-support-role-diff-check-on-dirty-tree` (`specs/2026-10/20261026-backlog-subagent-roles/feedback/`): resolved
  directly by AC-05; the `user` added it to the scope at Development start.

## 6. Assumptions

- The snapshot replaces the status-code comparison for every support role, not only the Backlog ones: one uniform
  check covers a clean and a dirty tree and forces no clean worktree on a caller that delegates mid-edit (the
  feedback's cost note). The Backlog roles still require a clean checkout, as the proposal agreed, because the Host
  applies their result in the same checkout.
- `xl` shows its own spelling in `detail`, since the engine prints the value it read.
- The fixture decomposition test drives the existing commands and the file moves directly; no command is added.
