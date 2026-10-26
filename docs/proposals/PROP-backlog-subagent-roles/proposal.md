---
id: PROP-backlog-subagent-roles
title: Backlog triage and decomposer subagent roles
summary: Adds isolated triage and decomposer support roles so Backlog feedback triage and draft decomposition can be delegated with verified write boundaries and preserved provenance, and gates XL drafts to decomposition before Planning.
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-backlog-subagent-roles
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/proposal.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/seed/docs/proposals/README.md
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/tests/
    - .devkit/installation.json
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    - docs/usecases/delivery/
  excludes:
    - docs/decisions/
    - packages/devkit/
    - packages/devkit-dist/
    - packages/devkit-viewer/
    - handbook/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-backlog-subagent-roles] Backlog triage and decomposer subagent roles

## 1. Background & Hypothesis

Backlog work runs in the main session today. Feedback triage follows the `feedback-hygiene` playbook, and splitting a
broad draft (`decomposed_from`, `needs_decompose`) is done by the Host by hand. Both read many files and fill the
coordinating context, and the Host judges its own grouping without a second view. `ADR-roadmap-and-milestones`
leaves the `triage` and `decomposer` roles as follow-ups, and `MS-backlog-subagent-roles` names them in its exit
condition.

Proposals are the main intake, and a rough draft stays allowed in Backlog. Nothing today keeps a rough `size: XL`
draft from entering Planning as one unit: `XL` reads "major overhaul", which nobody can check, and only a Planning run
that notices the breadth returns `needs_decompose`.

Hypothesis: two support roles with explicit contracts can take these reads out of the main session. They return
recommendations for the user's decision without writing Backlog state themselves. That keeps user ownership of
dispositions, and the Host can verify each result like a Scout or Challenger return. A judgeable `XL` and a
deterministic gate before Planning send every XL draft to the `decomposer` first.

Present workload (`materials/spike-findings.md` F5): 3 open feedback items, 86 dispositioned ones in the tree, no live
document carrying `decomposed_from` and no live `XL` proposal. The value is in larger hygiene batches, the first real
decompositions and the drafts to come, not in today's queue.

## 2. Technical Spike Questions

- **Q1 (read and return)**: Settled by the `user` (answer-01 q1): both roles are read-only.
- **Q2 (provenance)**: Settled below (Host application): the Host writes every link with existing commands, after an
  ID check that distinguishes existing IDs from proposed child slugs; open feedback of a decomposed parent keeps the
  retirement move.
- **Q3 (record)**: Settled by the `user` (answer-01 q2): no envelope; the Backlog commit body names the role used.
- **Q4 (invocation)**: Settled by the `user` (answer-01 q3, q4): `triage` is delegated above 5 open items on a native
  host; the `decomposer` runs from Backlog only, now also for an `XL` draft (answer-01 q4 constraints).
- **Q5 (hosts)**: Settled by policy below.
- **Q6 (XL gate placement)**: Settled by the `user` (answer-02 q5): devkit-spec only. Spike F7: a workflow exit
  condition blocks the gate, `devkit workflow next` and plan-intent recording, and devkit-spec's own commands carry the
  decompose text; `next` and `answer` print no directive of their own, which `FB-workflow-exit-check-without-directive`
  keeps open as a separate suggestion.
- **Q7 (XL definition)**: Settled by the `user` (answer-02 q6): "different nature" means work that would need separate
  specs or a different `task_kind`.

## 3. Proposed Design & Impact

### Roles

Two contracts in the spec bundle `subagents/`, registered in `bundle.toml` (an asset entry and `presets.core`) beside
the existing roles. Both have `x-execution: isolated`, `x-invocation: optional` and `x-git-actions: [read]`, start by
running `uv run devkit get-context spec` (the `code-reviewer` pattern that `SPEC-foundation-documents` extends to every
role), decide nothing and write nothing (`user`, answer-01 q1).

Each contract cites the procedure it applies by managed path instead of restating it (challenger-01 finding 5;
`CAP-DLV-delivery-workflows` section 4.6: a main session runs both procedures), and keeps only its inputs, return
fields, write boundaries and failure handling.

- **`triage`** applies `feedback-hygiene` Steps 1 and 2 (`.devkit/managed/spec/playbooks/feedback-hygiene/SKILL.md`)
  to the open feedback the Host names (by default `devkit spec list feedback --status open --all-namespaces -n 0`),
  reading each item's target and evidence. It returns, per group: the FB IDs, the confirmed ownership, a recommended
  destination from the Step 2 table with its reason, possible duplicates of another open item and dismissal
  candidates. It never proposes a status change itself; Step 3 stays with the Host after the user's decision.
- **`decomposer`** applies the Backlog reference's decomposition and prerequisite disposition
  (`.devkit/managed/spec/skills/spec/references/backlog.md`) to one draft the Host names, reading its PADRs, answer
  envelopes, materials and the live units that depend on it (`devkit spec refs PROP-<slug> --direction in -n 0`). It
  returns a split into independently deliverable children: per child a proposed slug, title, summary, scope, a size
  below `XL`, effort hints chosen afresh, boundaries by nearest existing parent, and edges among the children; the
  proposed disposition of each incoming `depends_on` edge; per child the parent PADRs, answers and materials it
  inherits, or none; and the exit it recommends (below). It does not assign the parent's open feedback to a child:
  those files take the retirement move (`feedback-retirement.md`, `CAP-DLV-proposal-incubation` section 3.1); it may
  name a child an open item is relevant to, as input for a later hygiene pass. It returns `needs_input` when the draft
  does not divide into independently deliverable parts.

Each return carries the support-role envelope fields (`status`, `summary`, `findings` with `evidence`, `assumptions`,
`unverified_areas`, and `diff_scope.head`, the base HEAD the role read); a finding's `failure_condition` states what
goes wrong if the recommendation is applied blindly.

| Role | Model profile | Reasoning effort | Reason (`policy`) |
| --- | --- | --- | --- |
| `triage` | `light-medium` | `medium` | Classification by the playbook's fixed table, like `scout` |
| `decomposer` | `general-high` | `high` | A design split whose second view is the point of the role |

### Invocation (`user`, answer-01 q3, q4)

- **`triage`**: in `feedback-hygiene` Step 1, the Host delegates when the open-feedback listing has more than 5 items
  and the host runs the role natively; otherwise it runs Step 1 inline.
- **`decomposer`**: from Backlog only, never self-initiated, for (1) a `needs_decompose` draft once its Planning return
  is merged, (2) the user's request to split a draft, and (3) an `XL` draft that the size gate below stopped. A
  mis-sized draft (declared `M` or `L`, actually broad) is still caught by Planning's existing `needs_decompose`
  return, which leads to (1).
- `spec-next` names the decomposer in its Backlog actions for `needs_decompose` and `XL` drafts.

### XL size gate

- **Definition** (`user`): `size: XL` means the work would produce two or more specs, or bundles deliverables of
  different nature, that is, work that would need separate specs or a different `task_kind` (`user`, answer-02 q6).
  The proposal template and `CAP-DLV-proposal-incubation` give one example of each side:
  - `XL`: a new CLI command together with a viewer redesign it does not need (two specs), or a parser bugfix bundled
    with a new search feature (`bugfix` and `feature`);
  - not `XL`: two agent contracts and the command checks that route work to them, delivered by one `feature` spec.
- **Values**: `S`, `M`, `L` and `XL` stay; the wording changes in the proposal template, the scaffold comment,
  `CAP-DLV-proposal-incubation` (the field table and the `target-docs.md` recommendation), the seed
  `docs/proposals/README.md`, `CAP-HARN-agent-guidance` and `UC-route-development-intent` where they describe sizes. Rough `XL` drafts stay valid
  in Backlog: no rule refuses `size: XL` on a draft.
- **Judging**: the `spec` skill's plan-intent step has the Host judge `size` against the definition and show it in the
  plan-intent request, as it shows `planning_effort`, because the scaffold writes `size: M` for every draft
  (challenger-02 finding 5).
- **One predicate** (challenger-02 finding 4): a proposal passes when `size` is absent or exactly `S`, `M` or `L`;
  any other value (`XL`, `xl`, a typo) is refused, and the refusal names the allowed values. Every check below uses it.
- **Gate** (`user`: an error, not a warning): an `XL` draft cannot pass plan-intent and cannot start Planning.
  Placement, devkit-spec only (`user`, answer-02 q5; spike F7 options A and B, corrected by challenger-02 finding 1):
  - `sdd-proposal.md`: the `intent-proposal` exit adds `frontmatter(proposal.md size S|M|L|)`. The gate request stays
    closed under `ask` and `auto`, so `devkit workflow next` shows the stage unmet with `detail="size=XL"` at exit 0,
    and `devkit workflow answer --request gate:plan-intent` refuses with `REQUEST_UNKNOWN`.
  - `devkit spec proposal accept --direct` adds the blocking line "size: XL (decompose first: split with
    --decomposed-from or promote to a milestone)" under `SPEC_PROPOSAL_NOT_ELIGIBLE`, beside the `needs_decompose`
    line; no new error class.
  - The `plan-` attach check (`devkit worktree start --existing-branch`) adds a reason naming both exits under
    `WORKTREE_ATTACH_REFUSED`, only for `plan-` branches, so a `dev-` attach or the unit integration readiness of an
    accepted proposal is never refused for size (challenger-02 finding 10).
  - `planning.md` step 1: a Planning run on a proposal whose size fails the predicate returns it as for decomposition
    (`status: draft`, `needs_decompose: true`), which covers a new `plan-` branch that no attach check sees
    (challenger-02 finding 3).
  - The `spec` skill's plan-intent step, `spec-next` and the `sdd-proposal` notes read the unmet size check as the
    directive "decompose first, never edit the size to pass", so an agent acts on it although `next` carries no code.
  - The Backlog reference's session reclassification adds "no `size: XL`" to its conditions (challenger-02 finding 9).
- **Two exits**, both through the `decomposer`, applied by the Host on the user's decision:
  - (a) **split**: `devkit spec proposal new <child> --decomposed-from PROP-<parent>` for each child, keeping the
    parent's `milestone`;
  - (b) **promote**: create `docs/roadmap/MS-<slug>.md` from the milestone template and place the children in it, when
    there are three or more children or the theme is long-running. The decomposer's return names the parent's
    milestone, if any, and a proposed relation to the new one (the parent milestone `depends_on` it, or its scope
    narrowed); the Host applies it on the user's decision, with the reset of that milestone's completion review the
    template requires for a scope change (challenger-02 finding 8). Creating a milestone is the user's decision on a
    concrete candidate; its status changes stay user-owned.
  The decomposer recommends (a) or (b) by that criterion; the user chooses.
- **No split possible**: a decomposer `needs_input` return on an `XL` draft means the draft was mis-sized; the Host
  shows the user a size correction with the decomposer's reason, and only the user's decision changes the size
  (challenger-02 finding 7).
- A proposal already past plan-intent whose size is edited to `XL` shows `intent-proposal` unmet again; its Planning
  run returns it with `needs_decompose: true` (step 1 above), as for a mis-sized draft.

### Host application and verification

- **Before delegating**: the checkout is clean (`git status --porcelain` empty), so the post-run comparison sees any
  write; on a dirty checkout the Host delegates from a clean task worktree or stays inline. For the decomposer,
  `devkit spec proposal check <slug>` passes on the base, and a Planning return for decomposition is merged first
  (Backlog reference, Return from Planning) when the draft has a Planning return; the payload's `diff_scope.head` is
  the base HEAD.
- **After the return**: `git status --porcelain` is still empty (spec-delegate step 4). Before applying a split, the
  Host confirms `git diff <head> -- docs/proposals/PROP-<slug>` is empty and re-runs `devkit spec refs PROP-<slug>
  --direction in -n 0`; a change in either sends the draft back to the role or to inline work.
- **IDs**: every existing ID a return cites (FB, the parent PROP, dependents, MS) resolves with `devkit spec resolve`,
  or it is dropped and reported. A proposed child slug or milestone slug must not resolve; `devkit spec proposal new`
  refuses a collision. Edges to children are written after the children exist, in the same Backlog commit.
- **Application**: the Host presents the groups or the split, and applies only what the user decides, with the existing
  procedures: `feedback-hygiene` Steps 2 and 3; `devkit spec proposal new <child> --decomposed-from PROP-<parent>`
  (with `--milestone` for the kept or promoted milestone), `devkit spec proposal padr` and a materials copy for each
  inherited item the user keeps, the prerequisite disposition and the feedback retirement of the Backlog reference.
- **Record** (`user`, answer-01 q2): no envelope; the role returns a message, and the Backlog commit body names the role
  that was used.
- User-owned gates (`plan-intent`, `plan-accept`) and milestone transitions stay with the user; neither role changes a
  milestone status.

### Hosts (`policy`)

The `challenger` matrix, since neither role writes even `materials/` (challenger-01 finding 3): Claude Code `native`
(`Read`, `Grep`, `Glob`, `Bash`, with `disallowedTools: [Write, Edit]`; `Bash` runs the `devkit spec` queries), Codex
`emulated` (`sandbox_mode: read-only`), Antigravity `native` (sandboxed commands). Where a host cannot isolate a role,
`spec-delegate`'s substitute route applies, which here means running the cited playbook or Backlog procedure inline.

### Acceptance (`policy`)

- Tests pin both contracts like the others (`test_role_contracts.py`: role, profile, preset, host matrix with
  `disallowedTools`, payload row, the cited procedure path, `get-context`).
- A fixture decomposition test drives the Host procedure on a temporary repository: children carry `decomposed_from`,
  a rewired incoming edge points at a created child, the parent's open feedback is moved by retirement and not copied
  into a child, and a proposed slug that collides is refused.
- Size gate tests: an `XL` and an `xl` draft leave `intent-proposal` unmet at `next` (`detail="size=XL"`) under `ask`
  and `auto`; `workflow answer --request gate:plan-intent` is refused; `accept --direct --check` lists the size
  blocking line under `SPEC_PROPOSAL_NOT_ELIGIBLE`; a `plan-` attach is refused with the decompose reason and a `dev-`
  attach of an accepted `XL` proposal is not; a draft without `size` and an `L` draft still pass; guidance tests cover
  the `planning.md` step 1 return and the reclassification condition; `devkit workflow validate` accepts the
  definition.
- A dogfood `triage` run over the open feedback at Development time, with its return and the before and after
  `git status --porcelain`, is recorded in the final change report.

### Living Spec impact

- `CAP-DLV-delivery-workflows` section 4.6: two role rows (skill: the cited procedure; profile and effort above; writes
  nothing; envelope kind: none, a message); the `sdd-proposal` intent-proposal exit where the capability lists it,
  and the `plan-` attach reason in integration readiness.
- `CAP-DLV-proposal-incubation`: the `XL` definition, the size gate and its two exits, and decomposition that may
  delegate the split to `decomposer`; feedback retirement unchanged.
- `CAP-HARN-agent-guidance`: the subagent asset list, the size wording and the feedback-hygiene and Backlog guidance.
- `ARCH-04-1-ecosystem-boundaries`: the Subagent Roles row.
- `UC-route-development-intent`: the optional `triage` delegation and the size wording.
- Bundle text: both contracts, `bundle.toml`, the `spec-delegate` payload table, `feedback-hygiene` Step 1, the Backlog
  reference's decomposition and reclassification paragraphs, the `spec` skill's plan-intent step, `planning.md`
  step 1, `spec-next`'s Backlog actions, `sdd-proposal.md`, the proposal template and the seed README.
- Code: the `devkit spec proposal accept --direct` conditions, the `plan-` attach check, the scaffold comment and their
  tests. No change to `devkit-agt` or `devkit-dist` (answer-02 q5); the viewer's size filter
  keeps the same values; `handbook/` is a release snapshot outside this work.

### Order with parallel work

`SPEC-foundation-documents` (accepted and handed off to a spec on `dev-foundation-documents`, not yet on `main`)
rewrites the other role contracts and adds a test that every role contract loads the spec context. The new contracts
load it from the start, so whichever lands first the other passes; the shared role tests are a textual overlap the
later branch resolves. No `depends_on` is set, because nothing here needs that spec's behavior; the Host starts this
Development after that spec integrates, as the user directed.

### Non-goals

- Multi-unit orchestration hardening across `local-orchestrated` and `cloud-pr`: dropped from the roadmap by the
  `user`, with no follow-up proposal.
- A role that writes anything, sets a feedback status, deletes a proposal or creates or changes a milestone.
- A workflow, stage or unit for Backlog work, and a Backlog envelope location.
- A rule that refuses `size: XL` on a draft, or any size check other than `XL`.
- Automatic milestone placement or milestone status changes; replacing any user-owned gate.
- External tracker intake or synchronization (`ADR-roadmap-and-milestones`).

### Planning decisions

- `policy` (scout-01): boundaries fixed from spike F1 and F4; `devkit_spec/features/` (then not needed) and
  `docs/capabilities/collaboration/` dropped; `packages/devkit/`, `packages/devkit-dist/` and `handbook/` excluded.
- `policy` (challenger-01 findings 1-7, 9): no per-child feedback assignment; split ID check; clean-tree delegation and
  the `challenger` host matrix; model profiles; cited procedures; pinned decomposer input; inherited PADRs, answers and
  materials; the acceptance tests.
- `user` (answer-01): q1 read-only roles; q2 no envelope; q3 `triage` above 5 open items; q4 the decomposer from Backlog
  only. Added scope: the judgeable `XL`, the size gate as an error before Planning and its two exits; multi-unit
  orchestration hardening is a non-goal with no follow-up.
- `policy` (scout-02): boundaries add `sdd-proposal.md`, the template, the seed README, `features/proposals/` and
  `features/delivery/`; the viewer is excluded because the size values do not change.
- `policy` (challenger-02 findings 1, 3-5, 7-11): restated command refusals (a blocking line and an attach reason, no
  new error class), the `planning.md` return, one size predicate, size judged at plan-intent, the mis-sized exit, the
  promote milestone relation, the reclassification condition, `plan-`-only attach and the conditional precondition.
- `user` (answer-02): q5 the gate stays devkit-spec only, `size: M` and `dev_effort: medium` hold, and
  `FB-workflow-exit-check-without-directive` stays open as a separate suggestion; q6 "different nature" means separate
  specs or a different `task_kind`, with one example of each side in the template and `CAP-DLV-proposal-incubation`.
- `policy`: by that definition this proposal is `M`, not `XL`: one spec of `task_kind: feature`, two agent contracts and
  small command checks serving one Backlog decomposition theme.
- `policy`: host matrix and fallback (Q5); no `depends_on` on `SPEC-foundation-documents`; sequencing is the Host's.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr backlog-subagent-roles "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept backlog-subagent-roles --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff backlog-subagent-roles.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
