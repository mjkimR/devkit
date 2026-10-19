---
id: PROP-high-effort-review-loop
title: Bounded high-effort review procedure
summary: 'Redefines the high activity-effort procedure: P1-driven review rounds that end on no P1 or on stalled progress, a strict self-verification exception for minor fixes in code and reconcile re-review, severity levels, mandatory scout in high Planning, and reclassification advice for high session work.'
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-high-effort-review-loop] Bounded high-effort review procedure

- **Origin**: `ADR-medium-review-delegation` defined `medium` in detail and kept `high` as it was: "High retains code
  re-review after fixes and independent reconcile verification". `high` was never designed on its own.
- **Decided in Backlog**: the direction in §3 (loop rule, minor-fix exception for code and reconcile, severity
  levels, mandatory `scout`, session reclassification advice). Out of scope: a plan-review role and model or reasoning
  settings (see §3.6).
- **Related**: `ADR-medium-review-delegation`, `ADR-reconcile-check-envelope`, `CAP-DLV-delivery-workflows`,
  `CAP-DLV-workflow-envelopes`, `PROP-role-reasoning-effort-presets`.

## 1. Background & Hypothesis

### 1.1 Problem

- **Unbounded re-review.** At `high`, every path says only "re-review after the fixes" (`effort.md`, the
  `sdd-session-*` and `sdd-spec-*` workflow bodies, `spec-review` §61, `CAP-DLV-delivery-workflows`). Nothing states
  the scope of a re-review round, who runs it, when the loop ends, or what happens when it does not converge.
- **No priority among findings.** A finding's `severity` is an optional free label with no effect on open-finding
  counts or checks (`CAP-DLV-workflow-envelopes`). A loop cannot be driven by "serious findings" when nothing says
  which findings are serious.
- **Every fix costs a subagent round.** `medium` lets the implementer verify fixes; `high` leaves no room to close a
  typo or a fix the reviewer itself prescribed without another isolated review.
- **High Planning lacks evidence by rule.** `high` is proposed for work that reverses an accepted decision, creates a
  contract or document kind, or spans packages, yet `scout` runs only "when the direction needs evidence".
- **High session work.** The `high` triggers mostly describe work whose contract must be fixed first, which is not
  `session` depth; nothing points that out.

### 1.2 Hypothesis

A `high` loop that runs isolated review rounds until no P1 finding remains, hands over to the user only when progress
stalls, and lets strictly minor fixes be self-verified with recorded evidence gives `high` a defined end and a
higher bar than `medium` without spending a subagent round on every trivial fix.

## 2. Technical Spike Questions

- **Q1. Severity scale.** Exact definitions of P1, P2 and P3 for `spec-review` and `challenger` findings, and whether
  `severity` becomes required only at `high` or at every effort. Envelope code stays unchanged either way: the
  stage exit keeps counting every open finding regardless of severity.
- **Q2. Stall detection.** How "the same P1 recurs" and "fixes keep producing P1s" are identified across rounds
  (matching by `evidence` and `issue`, or an explicit `recurs:` reference written by the implementer in `reverify`),
  and the value of the safety cap (proposed: 5 rounds).
- **Q3. Out-of-scope P1.** A re-review round is limited to the fix diff and its impact; a P1 found outside it is fixed
  but marked. Whether such findings count toward the stall rule.
- **Q4. Planning loop.** Whether the same loop and minor-fix exception apply to `challenger` re-review in `high`
  Planning, with `Decision needed:` findings excluded from the loop (they go to `plan-accept`).
- **Q5. Session reclassification.** Whether the advice is a SHOULD in the `spec` skill only, or also a notice from
  any command.

## 3. Proposed Design & Impact

### 3.1 Review loop at `high` (code review and reconcile verification)

| Item | Rule |
| --- | --- |
| Reviewer | Each round starts a fresh `code-reviewer` (or `reconcile-reviewer`) with the earlier findings and the fix diff as input. |
| Scope | The fix diff and what it affects. A P1 outside that scope is still fixed, marked as out of scope. |
| Loop trigger | Only open P1 findings start another round. P2 and P3 are fixed or waived with a reason by the implementer in the same round and closed in `reverify`. |
| End | A fresh round returns no P1. |
| Hand over to the user | The same P1 recurs after its fix; fixing P1s keeps producing new P1s; the implementer and the reviewer disagree on a finding's validity; or the safety cap (Q2) is reached. Recorded as a problem. |

### 3.2 Minor-fix self-verification at `high`

The initial `code-reviewer` and `reconcile-reviewer` calls stay mandatory. After them, a fix MAY be self-verified
instead of starting a new round only when all of these hold:

| Condition | Code review | Reconcile |
| --- | --- | --- |
| Location | Only the location the finding's `evidence` names | Only the document or entry the finding names |
| Nature | Typo, comment, formatting, in-scope rename, test-only addition, or the finding's `suggested_action` applied as written | Wording only, or the finding's `suggested_action` applied as written |
| Contract | No public API, schema, error code, CLI output or other package touched | The contract's meaning is unchanged |
| Evidence | A test or check reproducing the `failure_condition` passes (for a P1, it failed before the fix) | The edited text and the actual diff are shown to agree |

- Uncertainty on any condition requires the reviewer.
- Recorded as self-verification with the reason and evidence: in `reverify` for code, in a new `reconcile-check` for
  reconcile.
- A later reviewer round includes every self-verified fix in its scope.
- A finding that recurs can no longer be closed by self-verification.

### 3.3 Severity levels

- **P1**: violates an acceptance criterion or contract, a correctness defect, data loss or a security issue.
- **P2**: a defect with a workaround.
- **P3**: an improvement.

`spec-review` and the reviewer contracts define them; `high` requires `severity` on every finding (Q1).

### 3.4 Mandatory `scout` in `high` Planning

`high` Planning runs `scout` to collect the accepted decisions, capabilities and contracts the proposal touches,
cited in the `challenger` input.

### 3.5 Reclassification advice for `high` session work

When `high` is proposed for a `session` task, the agent first proposes `spec` depth. If the user keeps `session`,
the work runs at `high` as defined.

### 3.6 Out of scope

- **Plan review role.** A separate `plan-reviewer` before implementation. Reconsider when `high` code reviews
  repeatedly return design-level P1s (record them as feedback).
- **Model and reasoning settings.** `activity-effort` stays independent of them; static per-role presets are
  `PROP-role-reasoning-effort-presets`.

### 3.7 Impact

- A new ADR supplementing `ADR-medium-review-delegation` for `high` (the accepted ADR is not edited).
- `devkit-spec` bundle: `skills/spec/references/effort.md`, `skills/spec-review/SKILL.md`,
  `skills/spec-delegate/SKILL.md`, the `code-reviewer`, `reconcile-reviewer` and `challenger` contracts, and the
  `sdd-session-*`, `sdd-spec-*` and `sdd-proposal` workflow bodies. Stage ids, checks and gates are unchanged.
- Living Spec: `CAP-DLV-delivery-workflows` (effort rules), `CAP-DLV-workflow-envelopes` (severity meaning, no
  schema change).

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions are recorded as PADRs in `decisions/`; research goes in `materials/`.
- On acceptance (`plan-accept`): record `gate:plan-accept`, set `status: accepted` and merge the Planning branch;
  Development starts with `devkit spec proposal handoff high-effort-review-loop`.
- On rejection: change only `status: rejected`, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
