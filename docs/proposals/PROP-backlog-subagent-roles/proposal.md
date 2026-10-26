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
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/collaboration/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-backlog-subagent-roles] Backlog triage and decomposer subagent roles

## 1. Background & Hypothesis

Backlog work runs in the main session today. Feedback triage follows the `feedback-hygiene` playbook, and splitting a
broad draft (`decomposed_from`, `--needs-decompose`) is done by the Host by hand. Both read many files and fill the
coordinating context, and the Host judges its own grouping without a second view. `ADR-roadmap-and-milestones`
leaves the `triage` and `decomposer` roles as follow-ups, and `MS-autonomous-backlog-and-orchestration` names them
in its first exit condition.

Hypothesis: two support roles with explicit contracts can take these reads out of the main session. They return
proposals for the user's decision without writing Backlog state themselves. That keeps user ownership of
dispositions, and the Host can verify each result like a Scout or Challenger return.

## 2. Technical Spike Questions

- **Q1**: What does each role read and return, and does either role write anything? Compare a read-only return the
  Host applies with a role that writes candidate drafts or feedback dispositions in a verified path.
- **Q2**: How is provenance kept? `decomposed_from`, feedback promotion targets and dispositions must survive the
  delegation without the role inventing links.
- **Q3**: Which envelope kind and stage records the return, given that Backlog work has no spec unit? Check whether
  the existing envelope kinds cover it or a Backlog record is needed.
- **Q4**: How do `spec-next`, `spec-feedback` sweeps and the `feedback-hygiene` playbook invoke the roles, and when
  does the Host stay inline because the batch is small?
- **Q5**: Which hosts can run the roles natively, and what is the fallback when a host cannot isolate them?

## 3. Proposed Design & Impact

To be settled in Planning. The starting point is two contracts beside the existing ones in the spec bundle
`subagents/`:
- `triage` groups open feedback by target, severity and recurrence and recommends a disposition for each group.
- `decomposer` proposes a split of one draft into independently deliverable drafts with `decomposed_from` set.

Both report through the same envelope and diff checks that `spec-delegate` applies to support roles. User-owned gates
and milestone transitions stay with the user.

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
