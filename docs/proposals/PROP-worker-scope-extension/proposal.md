---
id: PROP-worker-scope-extension
title: Tiered write boundaries for delegated workers
summary: Splits a delegated worker's write boundary into an extensible estimate and a hard deny list, so a worker records and justifies an adjacent-path extension instead of stopping or having its whole result rejected, in local and cloud runs alike.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-tasks/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md
    - packages/devkit-spec/src/devkit_spec/features/worker/
    - docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    - docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
  excludes:
    - docs/decisions/
    - .devkit/managed/
    - packages/devkit-spec/src/devkit_spec/features/workflow/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-worker-scope-extension] Tiered write boundaries for delegated workers

## 1. Background & Hypothesis

A delegated `development-worker` may write only the write scope its payload names: the unit directory, the tasks'
`_Boundary:` paths and the reconcile targets. The contract says "one path outside the write scope rejects the whole
result", and the Host's acceptance procedure (`spec-delegate/references/worker.md`) blocks the range, records a
`problem` envelope and sends a recovery request. In practice `_Boundary:` is an estimate written before any code
exists, and a task that needs one more file (a sibling module, a test helper, a fixture, a docs page a check demands)
is common. Each such case costs a full round trip: block, re-delegate or widen, re-validate.

Three shipped documents already disagree on how strict that boundary is:

- `spec-tasks` calls `_Boundary:` an estimate: "a needed extra path is made and explained in the report".
- The `development-worker` contract denies "everything else" and rejects the whole result on one outside path.
- `spec-review` reports "changes outside `_Boundary:` without a stated reason" for a Developer's own work, but
  "any change outside a delegated write scope" for a worker.

Locally the gap is invisible because the Host (a main session) reads the situation and re-spawns with a wider
scope. In an autohub cloud run there is no Host: the worker is the top-level agent, Hub verifies envelopes and
holds the run on a `problem` or an unanswered question, and only the operator can move it. So in the cloud the strict
reading turns every boundary miss into an operator intervention or a silently rejected result.

Two existing mechanisms show the shape of the answer:

- The `(sync output)` rule (`CAP-DLV-delivery-workflows`): a worker may add paths the payload did not list to the
  owning task's `_Boundary:`, annotated `(sync output)`, and the Host accepts them against stated criteria rather
  than blocking.
- `devkit spec worker inspect` derives its scope from `_Boundary:` at the returned head (`derive_scope` in
  `features/worker/usecases/inputs.py`), so a `tasks.md` amendment already passes the scope check. The contract
  forbids what the tool permits.

Hypothesis: the boundary should be three tiers, not one line. The declared `_Boundary:` is free; an adjacent path is
an extension the worker makes itself, annotates in `_Boundary:` and records in its `worker` envelope, and the
reviewer judges; a short deny list is the only hard line, and crossing it is the only case that stops the run. The
judgment moves from the Host to the worker, the verification to the `code-reviewer` round and the inspect tool, and
the final say to the gate the operator already holds. The same rule applies locally, so the Host stops being the
mechanism that papers over the inconsistency.

## 2. Technical Spike Questions

- **Q1**: What is the adjacent class a worker may extend into without stopping? Candidate definition: paths under
  the same source ownership root as a declared `_Boundary:` path (the package, feature or `tests/` mirror
  `ARCH-05-2-components` ties to it), the `docs/` paths a declared check reads, and project-level generated or lock
  files the declared change forces. Planning decides whether the class is stated as prose, as a derivation rule
  `derive_scope` can compute from the declared paths, or as a project setting in `.devkit/config.toml`.
- **Q2**: What stays on the deny list? Starting point: the current Denied list (other spec bundles, `.devkit/` apart
  from sync outputs, governance rules, weakening a test) plus architecture declarations and new feature edges, CI and
  release configuration, and anything outside the repository. Planning confirms whether the deny list is the
  contract's prose or a checkable pattern list, and whether a project may add to it.
- **Q3**: How is an extension recorded so that every verifier reads the same evidence? Candidate: the path is
  appended to the owning task's `_Boundary:` with `(scope extension: <reason>)`, mirroring `(sync output)`, and the
  `worker` envelope gains a `scope_extensions` list (`path`, `task`, `reason`, `requirements`). Planning decides
  whether `inspect` reports extensions as a distinct `scope` sub-result (`declared`, `extended`, `outside`) and
  whether an undeclared extension is `fail` or a reviewer finding.
- **Q4**: Who verifies in the cloud? Hub does not run `devkit spec worker inspect` today (no reference in
  `autohub/modules/hub/app` or `autohub/docs`); scope is enforced by the worker's own contract and the nested
  `code-reviewer`. Planning decides whether the proposal only needs `spec-review` to verify each recorded extension
  (reason present, path in the adjacent class, not on the deny list; otherwise a P2 finding) or whether autohub should
  also run inspect on the returned head. The latter is an autohub change outside this proposal and would be recorded
  as a follow-up.
- **Q5**: Does `_Boundary:` itself get looser? `spec-tasks` could allow directory or glob entries where
  `CAP-COLL-work-scope-registry` and `CAP-TRACE-code-entrypoints` already parse them, lowering the extension rate.
  Planning checks what `parse_boundaries` and the work-scope registry accept and whether a glob entry breaks either.

## 3. Proposed Design & Impact

- **Tier A, declared**: the payload's write scope as today. No change in behaviour.
- **Tier B, extension**: the worker may write an adjacent path (Q1) when a task needs it. Before the commit that
  touches it, the worker appends the path to the owning task's `_Boundary:` with `(scope extension: <reason>)` and
  commits `tasks.md` in the same commit. Its `worker` envelope lists the extension. `spec-review` Step 1 verifies each
  recorded extension (reason, class, deny list) and reports an unjustified one as P2 and an unrecorded outside path
  as P1; the Host's and Hub's acceptance rules treat a recorded, reviewed extension as inside scope.
- **Tier C, denied**: the deny list (Q2). A task that cannot be completed without a denied path is a `problem` with
  `--status needs_input` and a question that names the path, the reason and the options; this is the only boundary
  case that stops the run, locally or in the cloud.
- **Contracts**: `development-worker.md.jinja` "Write boundaries" and "On a problem" sections state the three tiers;
  `spec-tasks` keeps `_Boundary:` as an estimate and names the extension annotation; `spec-review` Step 1 replaces the
  two-rule sentence with the tiered check; `spec-delegate/references/worker.md` "Validate" accepts recorded extensions
  and names the deny list as the blocking condition; `worker-records.md` documents the envelope field.
  `CAP-DLV-delivery-workflows` (role table row and the write-scope paragraph next to the `(sync output)` rule) and
  `CAP-DLV-workflow-envelopes` (envelope schema) carry the normative clauses.
- **Tooling**: `devkit spec worker inspect` reports `scope` as `declared`, `extended` and `outside` entries and fails
  only on `outside` or on a deny-list hit; `devkit workflow envelope worker` accepts the extension list. Both are in
  `features/worker/`; the envelope schema change is in the envelope feature only if Planning finds no way to carry it
  as an existing structured field.
- **Local and cloud parity**: the Host follows the same acceptance rule as Hub, so an extension that passes review
  passes in both environments. No autohub change is required for the proposal to hold (Q4); an inspect step in Hub
  is recorded as a follow-up for autohub.
- **Observability**: extensions are visible in `tasks.md` and the envelope, so a later pass can count them per
  project and tune the adjacent class or widen `_Boundary:` guidance where extensions are routine.

Expected affected contracts: `CAP-DLV-delivery-workflows`, `CAP-DLV-workflow-envelopes`. The gate names, the
`problem`/`resolution` mechanism, `(sync output)` handling and the git rules of the worker are unchanged.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q5 and records the tier definitions as a PADR; acceptance and handoff create one feature spec.
Completion requires: the three contracts and two skills updated; `inspect` fixtures for a recorded extension (pass),
an unrecorded outside path (fail) and a deny-list hit (fail); a `spec-review` fixture that reports an unjustified
extension; and the role-contract test still passing.

Non-goals: giving workers general freedom outside the unit; changing autohub's run or question model; a worker
widening another task's or another unit's scope; removing `_Boundary:` from `tasks.md`; the `(sync output)` rule,
which stays as the special case it is.

<!--
- Preliminary decisions: devkit spec proposal padr worker-scope-extension "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept worker-scope-extension --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff worker-scope-extension.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
