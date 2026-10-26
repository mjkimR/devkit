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
  write; a read-only return the Host applies keeps the existing support-role diff check (`git status --short`
  unchanged) as the whole write-boundary verification. Pending: user question `q1`.
- **Q2 (provenance)**: How do `decomposed_from`, feedback promotion targets and dispositions survive delegation?
  Spike: the Host writes every link with existing commands (`devkit spec proposal new --decomposed-from`, the
  disposition line, `Source feedback`), and only for IDs the role cites that `devkit spec resolve` finds; the role
  never invents an ID it did not read. No new rule.
- **Q3 (record)**: Which envelope records the return when Backlog has no unit? Spike F2: `envelope new` requires a
  unit, triage has none and a decomposition deletes its parent. Pending: user question `q2`.
- **Q4 (invocation)**: Who calls the roles and when does the Host stay inline? Spike F3: no workflow stage; the
  `feedback-hygiene` playbook, the Backlog reference and `spec-next` call them. Pending: user questions `q3` and `q4`.
- **Q5 (hosts)**: Which hosts run the roles natively, and the fallback? Settled by policy below: the `scout` host
  matrix, and `spec-delegate`'s existing substitute route.

## 3. Proposed Design & Impact

### Roles

Two contracts in the spec bundle `subagents/`, registered in `bundle.toml` (an asset entry and `presets.core`) beside
the existing roles. Both have `x-execution: isolated`, `x-invocation: optional` and `x-git-actions: [read]`, start by
running `uv run devkit get-context spec` (the `code-reviewer` pattern that `PROP-foundation-documents` extends to every
role), decide nothing and write nothing.

- **`triage`** reads the open feedback the Host names (by default `devkit spec list feedback --status open
  --all-namespaces -n 0`) and each item's target and evidence. It returns groups by `target`, ordered as
  `feedback-hygiene` Step 1 orders them (`critical`, then `recurring`, then `blocked`, `workaround`, `noise`), and per
  group: the FB IDs, the confirmed ownership (`repo`, `upstream`, `unknown`), a recommended destination from the Step 2
  table with its reason, possible duplicates of another open item, and dismissal candidates (no observed Evidence).
- **`decomposer`** reads one draft proposal the Host names, its PADRs, materials, feedback and the live units that
  depend on it (`devkit spec refs PROP-<slug> --direction in -n 0`). It returns a split into independently deliverable
  children: per child a slug, title, summary, scope, effort hints chosen afresh, boundaries by nearest existing
  parent, the inherited `milestone`, edges among the children; plus the proposed disposition of each incoming
  `depends_on` edge and which child receives each open feedback file (never duplicated across children). It reports
  `needs_input` when the draft does not divide into independently deliverable parts.

Each return uses the support-role envelope fields (`status`, `summary`, `findings` with `evidence`, `assumptions`,
`unverified_areas`); a finding's `failure_condition` states what goes wrong if the recommendation is applied blindly.

### Host application and verification

- The Host checks `git status --short` is unchanged after the role (spec-delegate step 4), presents the groups or the
  split to the user, and applies only what the user decides, with the existing commands and procedures: the
  `feedback-hygiene` steps 2 and 3, `devkit spec proposal new <child> --decomposed-from PROP-<parent>`, the prerequisite
  disposition and feedback retirement of the Backlog reference.
- Every FB, PROP, SPEC or MS ID in a return is resolved (`devkit spec resolve`) before it is written into a document;
  an ID that does not resolve is dropped and reported.
- User-owned gates (`plan-intent`, `plan-accept`) and milestone transitions stay with the user; neither role proposes
  a milestone status change.

### Hosts (`policy`)

The `scout` matrix: Claude Code `native` (`Read`, `Grep`, `Glob`, `Bash`; `Bash` runs the `devkit spec` queries),
Codex `emulated` (`sandbox_mode: read-only`), Antigravity `native` (sandboxed commands). Where a host cannot isolate the
role, `spec-delegate`'s substitute route applies: the Host follows the contract body in the main session.

### Living Spec impact

- `CAP-DLV-delivery-workflows` section 4.6: two role rows.
- `CAP-DLV-proposal-incubation`: decomposition may delegate the split proposal to `decomposer`.
- `CAP-HARN-agent-guidance`: the subagent asset list and the feedback-hygiene and Backlog guidance.
- `ARCH-04-1-ecosystem-boundaries`: the Subagent Roles row.
- `UC-route-development-intent`: the feedback-triage extension names the optional `triage` delegation.
- Bundle text: both contracts, `bundle.toml`, the `spec-delegate` payload table, `feedback-hygiene` Step 1, the Backlog
  reference's decomposition paragraphs and `spec-next`'s Backlog actions; tests extend the role-set assertions
  (`test_role_contracts.py`, `test_workflows.py`).
- No change to `devkit-agt` or `devkit-dist` code (spike F1), and `handbook/` is a release snapshot outside this work.

### Order with parallel work

`PROP-foundation-documents` (accepted and handed off to a spec on `dev-foundation-documents`, not yet on `main`) rewrites the other role contracts and adds a
test that every role contract loads the spec context. The new contracts load it from the start, so whichever lands
first the other passes; the shared role tests are a textual overlap the later branch resolves. No `depends_on` is set,
because nothing here needs that spec's behavior; the Host starts this Development after that spec integrates, as the
user directed.

### Non-goals

- Multi-unit orchestration hardening across `local-orchestrated` and `cloud-pr` (the milestone's second exit
  condition). It follows as a separate proposal in `MS-autonomous-backlog-and-orchestration`.
- A role that writes Backlog state, sets a feedback status or creates proposals.
- A workflow, stage or unit for Backlog work, a new envelope location or engine code.
- Automatic milestone placement or milestone status changes; replacing any user-owned gate.
- External tracker intake or synchronization (`ADR-roadmap-and-milestones`).

### Follow-ups

- A draft proposal for multi-unit orchestration hardening (the milestone's second exit condition), created in Backlog
  by the Host.

### Planning decisions

- `policy` (scout-01): boundaries fixed from spike F1 and F4; `devkit_spec/features/` and
  `docs/capabilities/collaboration/` dropped, `bundle.toml`, the named skills, `CAP-HARN-agent-guidance`, `ARCH-04-1-ecosystem-boundaries`,
  `docs/usecases/delivery/` and the receipt added; `packages/devkit/`, `packages/devkit-dist/` and `handbook/` excluded.
- `policy`: host matrix and fallback follow `scout` and `spec-delegate` (Q5).
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
