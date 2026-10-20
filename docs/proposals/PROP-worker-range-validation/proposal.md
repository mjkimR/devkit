---
id: PROP-worker-range-validation
title: One-command worker result inspection for orchestrated units
summary: "Bundles existing worker-result checks and reviewer diff information into one command that derives its unit, range, write scope and base checkout from the worktree and committed records, leaving interpretation to the agent without adding an approval gate."
status: reviewing                      # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: delivery/
priority: critical                      # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: high                        # low | medium | high (hint for Development)
boundaries:
  owns:
    - delivery/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-worker-range-validation] One-command worker result inspection for orchestrated units

## 1. Background & Hypothesis

- **Observed on 2026-10-19**: the first sustained local-orchestrated run (three Development units and two Planning
  units in parallel) worked, but the Host repeated the same checks by hand for every returned range: ancestry from
  the last accepted head, every changed path inside the write scope, a clean worktree, the cumulative rules check
  and `devkit workflow next`. The write scope exists only in the delegation payload, so each scope check was a
  hand-written pattern.
- **Reviewer input**: `FB-reconcile-reviewer-no-diff-list` identifies missing changed-file information in the
  read-only reviewer's payload. The same Git inspection can supply it.
- **Hypothesis**: A small command that collects existing checks and diff information saves repeated shell work. It
  provides evidence for the main agent; it does not become another approval gate or coordination system.

## 2. Planning Scope

Implement a thin wrapper in `devkit-spec` around the checks the Host already performs:
`devkit spec worker inspect [--unit <dir>] [--base <accepted>] [--head <returned>] [--scope <prefix>... |
--scope-file <path>] [--base-checkout <path>]`. Run in a unit's worktree, the command infers every input it can from
the worktree and the unit's committed records; an explicit flag only overrides the derived value (user decision at
the `plan-accept` review, superseding the earlier explicit-input design):

- **Unit**: the unit bound to the worktree's activity branch.
- **Returned head**: the commit that added the unit's latest `worker` envelope, which is the worker's `final_head`
  by definition.
- **Base** (the last accepted head): derived from the unit's `worker` envelopes and their blocked state, or the
  branch's merge base with its base branch when no earlier `worker` envelope exists.
- **Write scope**: derived from committed documents: for Planning the proposal directory; for Development the unit
  directory, the tasks' `_Boundary:` paths, the unit's materials directory, the Living Spec documents `reconcile.md`
  targets and the linked source feedback the spec names. `--scope` or `--scope-file` replaces it.
- **Base checkout**: the worktree's registered base checkout, reported as information only.

When the records do not determine an input, the command reports it as could-not-run (exit `2`) with a stable code
whose action is to pass that flag; it never guesses. The output names every input's value and where it came from,
including each scope entry's source. The command does not use the scope registry, workers author no new mandatory
committed scope record and the envelope schema is not extended.

Planning settles the CLI arguments, the derivation rules, concise result fields and reuse of existing check APIs.
Prefer existing conventions (the branch/unit binding, the `_Boundary:` and `reconcile.md` parsers, the worktree's
base-checkout lookup) without introducing a separate scope authority or validation lifecycle.

## 3. Proposed Design & Impact

- One invocation reports ancestry, changed paths, paths outside the scope, worktree status, existing envelope
  validation, cumulative rules results and `devkit workflow next`, plus the base checkout's HEAD and dirty paths as
  information. Include the compared heads and changed paths in information the agent can pass to a read-only
  reviewer.
- Default output carries the result and actionable findings; structured output is one JSON object. Preserve the
  stable codes and actions of existing checks and report checks that could not run distinctly from negative results.
- Scope mismatches and worktree observations are information for the main agent to assess. The command MUST NOT
  add an approval request, workflow gate, integration refusal, mandatory scope registration or an option that
  overrides findings. Existing rules, delegation write boundaries and approval gates retain their current meaning;
  the helper neither weakens them nor adds a new blocking prerequisite to accepting a worker result. The derived
  scope is what the committed documents declare and never wider; the Host's payload scope stays authoritative and
  can be passed with `--scope` when it differs.
- The agent decides how to act on findings and runs any corrective commands. The helper does not modify files,
  merge the base, refresh environments, run `devkit sync`, retry operations or automatically enlarge write scope.
- Affected: a small `devkit spec worker` command group, `spec-delegate` and `spec-orchestrate` guidance, reviewer
  payload guidance, and `CAP-DLV-delivery-workflows`. No new worker envelope fields are required.

- Settled design (command name, derivation rules and their could-not-run codes, per-check `pass`/`fail`/`not-run`
  results, exit codes, reviewer fields, no writes): `PADR-informational-range-inspection-reuses-existing-checks`.

**Non-Goals**: automatic scope expansion (the command never widens what the committed documents declare),
link-repair ownership inference, base-drift detection or merging, worktree environment refresh, new approval gates,
and automatic enforcement of helper findings.

**Separate feedback**: `FB-worker-scope-misses-link-repairs` and `FB-handoff-premise-drift-unreported` remain open for
scope construction and handoff drift respectively. Neither is required for this command and neither is implemented
by this proposal.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr worker-range-validation "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff worker-range-validation`.
- On rejection: `status: rejected` with the user's reason in the commit message.
