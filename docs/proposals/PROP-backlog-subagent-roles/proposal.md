---
id: PROP-backlog-subagent-roles
title: Backlog triage and decomposer subagent roles
summary: Adds isolated triage and decomposer support roles so Backlog feedback triage and draft decomposition can be delegated with verified write boundaries and preserved provenance.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-autonomous-backlog-and-orchestration
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/
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
    - handbook/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-backlog-subagent-roles] Backlog triage and decomposer subagent roles

## 1. Background & Hypothesis

Backlog work runs in the main session today. Feedback triage follows the `feedback-hygiene` playbook, and splitting a
broad draft (`decomposed_from`, `needs_decompose`) is done by the Host by hand. Both read many files and fill the
coordinating context, and the Host judges its own grouping without a second view. `ADR-roadmap-and-milestones`
leaves the `triage` and `decomposer` roles as follow-ups, and `MS-autonomous-backlog-and-orchestration` names them
in its first exit condition.

Hypothesis: two support roles with explicit contracts can take these reads out of the main session. They return
proposals for the user's decision without writing Backlog state themselves. That keeps user ownership of
dispositions, and the Host can verify each result like a Scout or Challenger return.

Present workload (`materials/spike-findings.md` F5): 3 open feedback items, 86 dispositioned ones in the tree, and no
live document carrying `decomposed_from` yet. The value is in larger hygiene batches and in the first real
decompositions, not in today's queue.

## 2. Technical Spike Questions

- **Q1 (read and return)**: What does each role read and return, and does either role write? Spike: neither needs to
  write; a read-only return the Host applies keeps the support-role diff check as the write-boundary verification.
  Pending: user question `q1`.
- **Q2 (provenance)**: How do `decomposed_from`, feedback promotion targets and dispositions survive delegation?
  Settled below (Host application): the Host writes every link with existing commands, after an ID check that
  distinguishes existing IDs from proposed child slugs; open feedback of a decomposed parent keeps the retirement move.
- **Q3 (record)**: Which envelope records the return when Backlog has no unit? Spike F2: `envelope new` requires a
  unit, triage has none and a decomposition deletes its parent. Pending: user question `q2`.
- **Q4 (invocation)**: Who calls the roles and when does the Host stay inline? Spike F3: no workflow stage; the
  `feedback-hygiene` playbook, the Backlog reference and `spec-next` call them. Pending: user questions `q3` and `q4`.
- **Q5 (hosts)**: Which hosts run the roles natively, and the fallback? Settled by policy below.

## 3. Proposed Design & Impact

Lines marked *(provisional: qN)* follow the recommended answer of that question and are rewritten if the user chooses
another option.

### Roles

Two contracts in the spec bundle `subagents/`, registered in `bundle.toml` (an asset entry and `presets.core`) beside
the existing roles. Both have `x-execution: isolated` and `x-invocation: optional`, start by running
`uv run devkit get-context spec` (the `code-reviewer` pattern that `PROP-foundation-documents` extends to every role)
and decide nothing. *(provisional: q1)* Both have `x-git-actions: [read]` and write nothing.

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
  returns a split into independently deliverable children: per child a proposed slug, title, summary, scope, effort
  hints chosen afresh, boundaries by nearest existing parent, the inherited `milestone` and edges among the children;
  the proposed disposition of each incoming `depends_on` edge; and per child the parent PADRs, answers and materials it
  inherits, or none. It does not assign the parent's open feedback to a child: those files take the retirement move
  (`feedback-retirement.md`, `CAP-DLV-proposal-incubation` section 3.1); it may name a child an open item is relevant
  to, as input for a later hygiene pass. It returns `needs_input` when the draft does not divide into independently
  deliverable parts.

Each return carries the support-role envelope fields (`status`, `summary`, `findings` with `evidence`, `assumptions`,
`unverified_areas`, and `diff_scope.head`, the base HEAD the role read); a finding's `failure_condition` states what
goes wrong if the recommendation is applied blindly.

| Role | Model profile | Reasoning effort | Reason (`policy`) |
| --- | --- | --- | --- |
| `triage` | `light-medium` | `medium` | Classification by the playbook's fixed table, like `scout` |
| `decomposer` | `general-high` | `high` | A design split whose second view is the point of the role |

### Host application and verification

- **Before delegating**: the checkout is clean (`git status --porcelain` empty), so the post-run comparison sees any
  write; on a dirty checkout the Host delegates from a clean task worktree or stays inline. For the decomposer,
  `devkit spec proposal check <slug>` passes on the base and a Planning return for decomposition is merged first
  (Backlog reference, Return from Planning); the payload's `diff_scope.head` is the base HEAD.
- **After the return**: `git status --porcelain` is still empty (spec-delegate step 4). Before applying a split, the
  Host confirms `git diff <head> -- docs/proposals/PROP-<slug>` is empty and re-runs `devkit spec refs PROP-<slug>
  --direction in -n 0`; a change in either sends the draft back to the role or to inline work.
- **IDs**: every existing ID a return cites (FB, the parent PROP, dependents, MS) resolves with `devkit spec resolve`,
  or it is dropped and reported. A proposed child slug must not resolve; `devkit spec proposal new` refuses a
  collision. Edges to children are written after the children exist, in the same Backlog commit.
- **Application**: the Host presents the groups or the split, and applies only what the user decides, with the existing
  procedures: `feedback-hygiene` Steps 2 and 3; `devkit spec proposal new <child> --decomposed-from PROP-<parent>`,
  `devkit spec proposal padr` and a materials copy for each inherited item the user keeps, the prerequisite disposition
  and the feedback retirement of the Backlog reference.
- User-owned gates (`plan-intent`, `plan-accept`) and milestone transitions stay with the user; neither role proposes
  a milestone status change.

### Hosts (`policy`)

The `challenger` matrix, since neither role writes even `materials/` (challenger-01 finding 3): Claude Code `native`
(`Read`, `Grep`, `Glob`, `Bash`, with `disallowedTools: [Write, Edit]`; `Bash` runs the `devkit spec` queries), Codex
`emulated` (`sandbox_mode: read-only`), Antigravity `native` (sandboxed commands). Where a host cannot isolate a role,
`spec-delegate`'s substitute route applies, which here means running the cited playbook or Backlog procedure inline.

### Acceptance (`policy`)

The milestone's first exit condition needs more than contract text (challenger-01 finding 9):

- Tests pin both contracts like the others (`test_role_contracts.py`: role, profile, preset, host matrix with
  `disallowedTools`, payload row, the cited procedure path, `get-context`).
- A fixture decomposition test drives the Host procedure on a temporary repository: children carry `decomposed_from`,
  a rewired incoming edge points at a created child, the parent's open feedback is moved by retirement and not copied
  into a child, and a proposed slug that collides is refused.
- A dogfood `triage` run over the open feedback at Development time, with its return and the before and after
  `git status --porcelain`, is recorded in the final change report.

### Living Spec impact

- `CAP-DLV-delivery-workflows` section 4.6: two role rows (skill: the cited procedure; profile and effort above; writes
  nothing; envelope kind per `q2`).
- `CAP-DLV-proposal-incubation`: decomposition may delegate the split proposal to `decomposer`; feedback retirement
  unchanged.
- `CAP-HARN-agent-guidance`: the subagent asset list and the feedback-hygiene and Backlog guidance.
- `ARCH-04-1-ecosystem-boundaries`: the Subagent Roles row.
- `UC-route-development-intent`: the feedback-triage extension names the optional `triage` delegation.
- Bundle text: both contracts, `bundle.toml`, the `spec-delegate` payload table, `feedback-hygiene` Step 1, the Backlog
  reference's decomposition paragraphs and `spec-next`'s Backlog actions; tests extend the role-set assertions
  (`test_role_contracts.py`, `test_workflows.py`).
- No change to `devkit-agt` or `devkit-dist` code (spike F1) *(provisional: q2)*, and `handbook/` is a release snapshot
  outside this work.

### Order with parallel work

`PROP-foundation-documents` (accepted and handed off to a spec on `dev-foundation-documents`, not yet on `main`)
rewrites the other role contracts and adds a test that every role contract loads the spec context. The new contracts
load it from the start, so whichever lands first the other passes; the shared role tests are a textual overlap the
later branch resolves. No `depends_on` is set, because nothing here needs that spec's behavior; the Host starts this
Development after that spec integrates, as the user directed.

### Non-goals

- Multi-unit orchestration hardening across `local-orchestrated` and `cloud-pr` (the milestone's second exit
  condition). It follows as a separate proposal in `MS-autonomous-backlog-and-orchestration`.
- A role that sets a feedback status, deletes a proposal or changes a milestone *(provisional: q1 for any write)*.
- A workflow or stage for Backlog work, and engine code *(provisional: q2 for a Backlog record location)*.
- Automatic milestone placement or milestone status changes; replacing any user-owned gate.
- External tracker intake or synchronization (`ADR-roadmap-and-milestones`).

### Follow-ups

- A draft proposal for multi-unit orchestration hardening (the milestone's second exit condition), created in Backlog
  by the Host.

### Planning decisions

- `policy` (scout-01): boundaries fixed from spike F1 and F4; `devkit_spec/features/` and
  `docs/capabilities/collaboration/` dropped, `bundle.toml`, the named skills, `CAP-HARN-agent-guidance`,
  `ARCH-04-1-ecosystem-boundaries`, `docs/usecases/delivery/` and the receipt added; `packages/devkit/`,
  `packages/devkit-dist/` and `handbook/` excluded.
- `policy` (challenger-01 findings 1-7, 9): no per-child feedback assignment; split ID check; clean-tree delegation
  and the `challenger` host matrix; model profiles; cited procedures; pinned decomposer input; inherited PADRs,
  answers and materials; the acceptance above.
- `policy`: host matrix and fallback (Q5).
- `policy`: no `depends_on` on `PROP-foundation-documents`; sequencing is the Host's.

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
