---
id: PROP-seeded-paths-in-boundaries
title: Seeded and synced paths in proposal boundaries
summary: Lets a proposal's write scope cover the tracked files devkit sync writes because of the agreed change, such as a new seed in a selected preset, so Development does not stop on a path Planning could not name.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-27
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - delivery/
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/proposal_boundaries/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-seeded-paths-in-boundaries] Seeded and synced paths in proposal boundaries

## 1. Background & Hypothesis

A proposal's `boundaries.owns` becomes Development's write scope, and `RULE-proposal-boundaries` admits only paths
that exist at Planning (or their nearest parent). A change that adds a seed to a preset the repository selects makes
`devkit sync` write a new tracked file, such as `docs/ux/README.md` from the `docs-skeleton` seed in
`SPEC-ux-documentation`, that Planning could not name. The worker then stops on a problem until the Host admits the
path by hand. `.devkit/installation.json` and `AGENTS.md` do not hit this only because they already exist.

Hypothesis: the tracked outputs that `devkit sync` writes because of the agreed change can be derived, or at least
declared, so the handoff write scope includes them without a Host decision each time.

## Source feedback (when this proposal receives feedback)

- `FB-new-seed-sync-output-outside-boundaries`: the whole observation, a seeded path outside the handed-off write
  scope that stopped Development.

## 2. Technical Spike Questions

- **Q1**: Can Development derive the sync outputs of its own bundle change (for example from `devkit sync --check` in
  the worktree), or must Planning declare them?
- **Q2**: If declared, what does `RULE-proposal-boundaries` accept: a seeded target path the change creates, named
  with its seed source?
- **Q3**: Is a standing rule ("sync outputs that follow from the agreed change are admitted; record them in
  `_Boundary`") enough as procedure, without code?

## 3. Proposed Design & Impact

To be settled in Planning. The interim procedure is the one the Host used in this session: such a path is admitted
as Host-admitted in `_Boundary` without stopping.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr seeded-paths-in-boundaries "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept seeded-paths-in-boundaries --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff seeded-paths-in-boundaries.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
