---
id: SPEC-high-effort-review-loop
title: Bounded high-effort review procedure
summary: "Bounds the high activity-effort procedure of the devkit-spec bundle: whole-batch review rounds that end on no finding or all-minor fixes, hand-over of persistent, recurring or contested P1s, P1-P3 severity, mandatory high Planning scout and session reclassification advice."
status: planned
created: 2026-10-19
related_capabilities:
  - CAP-DLV-delivery-workflows
  - CAP-DLV-workflow-envelopes
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-high-effort-review-loop] Bounded high-effort review procedure

## 1. Problem Statement & Motivation

Handed off from proposal PROP-high-effort-review-loop on 2026-10-19. The decision is
`ADR-bounded-high-effort-review-loop`, which supersedes `ADR-medium-review-delegation`: it carries the `medium` and
`low` rules over unchanged and replaces the `high` clause ("code re-review after fixes and independent reconcile
verification") with the design in section 5.

- **Unbounded re-review.** At `high`, every path says only "re-review after the fixes": nothing states a round's scope,
  its inputs, when the loop ends, or what happens when it does not converge.
- **No priority among findings.** A finding's `severity` is an optional free label (`CAP-DLV-workflow-envelopes`);
  the envelope reference's example value is `medium`.
- **Every fix costs a subagent round.** `high` leaves no room to close a typo or a fix the reviewer itself prescribed
  without another isolated review.
- **High Planning lacks evidence by rule.** `scout` runs only "when the direction needs evidence", also at `high`.
- **High session work.** Nothing advises raising the depth when `high` is proposed for work that is not `session`
  depth.

The change is prose in the `devkit-spec` bundle (the `spec` skill's effort references, `spec-review`, `spec-delegate`,
the role contracts and the workflow bodies), the tests that assert that prose, and the Living Spec. Envelope schemas,
stage ids, checks and gates stay as they are.

### 1.1 Assumptions

Premises of the proposal checked against base `8ca289b`, and the choices made inside the agreed scope:

- **High triggers changed after Planning.** Commit `a37add2` narrowed when `high` is proposed (an effect that cannot
  be undone locally, or unresolved P1s, a return or a close for a defect in earlier work of the same task); the
  proposal's problem statement and §3.5 were written against the earlier triggers (reversing a decision, a new
  contract or document kind, several packages). The reclassification advice is therefore stated by what the
  `session` task does, not by trigger name: creating or changing a contract (one with external consumers included) or
  a document kind proposes `spec` depth, reversing an accepted decision proposes `proposal` depth, and anything else
  gives no depth advice. This keeps the agreed mapping and covers the current triggers. The mandatory `scout` of
  `high` Planning does not depend on the triggers.
- **The procedure lives in one reference.** The full `high` loop goes into a new `spec` skill reference,
  `references/review-loop.md`, linked from `references/effort.md`; effort.md keeps the table and one rule per level
  and stays under the bundle's 12288-byte skill document budget (`test_bundle_budgets.py`). The other bundle files
  name the level and cite the reference instead of restating the loop, which applies the direction of
  FB-effort-procedure-restated to the files this change has to touch anyway. That feedback stays open.
- **Severity scope.** "Required on every finding at every effort" applies to the three review kinds the scale is
  defined for: `review` (and the findings a `reverify` carries), `reconcile-check` and `challenger`, a `low`
  self-review and self-check included. `scout` findings are evidence, not defects, and `worker` findings list open
  items; neither takes a level. The envelope engine (`devkit.workflow`, outside this change) keeps accepting any
  non-empty string: the levels are a procedure, not a schema rule.
- **`plan-accept` gap report.** The request content is defined in the `sdd-proposal` body, the `spec-orchestrate`
  skill and rule 15 of `CAP-DLV-delivery-workflows`; the missing-`scout` gap is added there.
  `CAP-DLV-proposal-incubation` defines no request content and needs no change.
- **Superseded ADR frontmatter.** Setting `status: superseded` and `superseded_by` on `ADR-medium-review-delegation`
  is outside this Development turn's write scope; it is left to the Host as an open item of the final report.
- **Round count across returns.** A `devkit workflow return` leaves earlier envelopes out of the checks but keeps the
  files; their `round <N>;` markers still count toward the cap within the segment.

## 2. User Stories

- **US-1**: As an implementer running an activity at `high`, I want a review loop with a defined round scope, end and
  hand-over, so that the loop terminates without leaving a non-minor fix unreviewed.
- **US-2**: As a reviewer role, I want the earlier findings, the round's diff scope and the effort as input and a fixed
  severity scale, so that I can mark recurrences and priorities the implementer records unchanged.
- **US-3**: As a user, I want persistent, recurring or contested P1s handed to me through the existing `worker`
  problem and question records, so that I decide only what the loop cannot.

## 3. Non-Goals

1. **Scope Excluded**: a plan-review role (`plan-reviewer`) before implementation.
   - **When to Reconsider**: feedback records design-level P1s from `high` code review in two or more units.
2. **Scope Excluded**: model and reasoning settings; `activity-effort` stays independent of them.
3. **Scope Excluded**: envelope schema changes: no new finding key, envelope kind, stage, check or gate, and no
   validation of severity values by `devkit.workflow`.
4. **Scope Excluded**: changing the `medium` and `low` procedures, including a definition of "cross-component impact"
   in the medium reconcile exception (FB-reconcile-self-check-cross-component stays open).
5. **Scope Excluded**: closing challenger findings with `reverify` or hiding their open counts
   (FB-challenger-findings-stay-open); a `high` Planning round states what the previous round's findings became in its
   summary.

## 4. Acceptance Criteria & Behavioral Contracts

Bundle paths are relative to `packages/devkit-spec/src/devkit_spec/bundle/`. Each scenario except AC-09 is checked by
`packages/devkit-spec/tests/test_effort_procedure.py`, which reads the shipped text.

### [AC-01] The high loop defines round, fixing, next round, end and round count
- **Given** `skills/spec/references/review-loop.md`
- **When** the test reads it
- **Then** it states that each round is a fresh reviewer instance, that round 1 reviews the whole change and each
  later round every fix since the previous round, never a subset; that the implementer fixes every finding of a round
  together and closes the round (`reverify` for code, a new `reconcile-check` for reconcile, the next `challenger-NN`
  summary or the `worker` summary for Planning); that the loop ends when a round returns no finding or every fix of the
  batch meets the minor-fix conditions and is self-verified; that each round's summary starts with `round <N>;` (a
  closing reconcile check also with `closes reconcile-check-<NN>;`); that the cap is 3 rounds after the initial
  review; and that a `devkit workflow return` does not reset the count

### [AC-02] Minor-fix self-verification has four conditions per review kind
- **Given** `skills/spec/references/review-loop.md`
- **When** the test reads its minor-fix table
- **Then** the table has the rows Location, Nature, Contract and Evidence and the columns Code review, Reconcile and
  Planning; the text states that uncertainty on any condition sends the whole batch to the next round, that the
  self-verification is recorded with reason and evidence (in `reverify`, the new `reconcile-check`, or the `worker`
  summary), that a recurring finding cannot be closed by self-verification, and that the initial `code-reviewer`,
  `reconcile-reviewer` and `challenger` calls stay mandatory at `high`

### [AC-03] Hand-over uses worker problems and questions
- **Given** `skills/spec/references/review-loop.md` and `subagents/development-worker.md`
- **When** the test reads them
- **Then** the reference names three causes: a batch that fails the minor-fix conditions at the cap round, a P1 that
  recurs after its fix (`recurs: <envelope> #<n>;` at the start of `issue`), and a P1 the implementer holds invalid
  that is asserted again after one round given the counter-evidence; the first two are a `problem` in the `worker`
  envelope and the third a `questions` entry with both positions as options; a session reports them in the
  conversation and does not integrate; a P1 the user rules invalid is closed only by a waiver citing the `answer`
  envelope; a fix the user asks for after a cap or recurrence problem gets one further round outside the cap; and the
  development worker contract names the `high` hand-over as a reason to stop and a contested P1 as a question

### [AC-04] Severity is P1, P2 or P3 on every review finding
- **Given** `skills/spec/references/review-loop.md`, `skills/spec/references/envelope.md`, `skills/spec-review/SKILL.md`
  and the contracts `subagents/code-reviewer.md`, `subagents/reconcile-reviewer.md` and `subagents/challenger.md`
- **When** the test reads them
- **Then** the reference defines `P1`, `P2` and `P3` for code review, reconcile and Planning; envelope.md's example
  severity is a P-level, never `medium`, and it states that a `review`, `reconcile-check` or `challenger` finding
  carries one at every effort, that the implementer records it unchanged and that it has no effect on checks; the
  `spec-review` report example carries `severity`; and each of the three contracts returns `severity` on every finding

### [AC-05] High Planning runs scout and the plan-accept request reports its absence
- **Given** `skills/spec/references/effort.md`, `skills/spec/references/review-loop.md`, `workflows/sdd-proposal.md`
  and `skills/spec-orchestrate/SKILL.md`
- **When** the test reads them
- **Then** effort.md's Planning row requires `scout` at `high`; the reference starts that `scout` from
  `devkit spec refs <ID> --direction in` for each capability and ADR the proposal touches; and the `sdd-proposal` body
  and the `spec-orchestrate` accept step state that the `plan-accept` request names a missing `scout` envelope at
  `high` as it does a missing `challenger`

### [AC-06] High session work gets reclassification advice
- **Given** `skills/spec/references/effort.md`
- **When** the test reads it
- **Then** it states, as a SHOULD, that when `high` is proposed for a `session` task, work that creates or changes a
  contract or a document kind proposes `spec` depth, work that reverses an accepted decision proposes `proposal`
  depth, and other work gets no depth advice, and that a `session` the user keeps runs at `high` as defined

### [AC-07] No bundle file restates an unbounded high re-review
- **Given** every Markdown file under `skills/`, `subagents/` and `workflows/`
- **When** the test searches them
- **Then** none contains `re-review after`, `High retains` or `re-review at high`, and `skills/spec-review/SKILL.md`,
  `skills/spec-delegate/SKILL.md`, both worker contracts and the five workflow bodies each cite `review-loop.md` for
  `high`

### [AC-08] Reviewer payloads carry the round inputs
- **Given** `skills/spec-delegate/references/payload.md`
- **When** the test reads the rows for `code-reviewer`, `reconcile-reviewer` and `challenger`
- **Then** each row names the earlier rounds' findings, the round's diff scope and the `activity-effort`

### [AC-09] Stages, checks and gates are unchanged
- **Given** the five workflow definitions after the change
- **When** `devkit workflow validate` and the existing `test_workflows.py` run
- **Then** the command exits 0, the tests pass, and `git diff 8ca289b -- packages/devkit-spec/src/devkit_spec/bundle/workflows/`
  changes no line inside a definition's YAML frontmatter

## 5. Design

Carried from the proposal and numbered as `ADR-bounded-high-effort-review-loop` cites it (§3.1 to §3.5). The
normative text ships in `skills/spec/references/review-loop.md` and `skills/spec/references/effort.md`.

### 3.1 Review loop at `high`

Applies to code review (`code-reviewer`), reconcile verification (`reconcile-reviewer`) and `high` Planning
(`challenger`). A round hands the reviewer the whole batch of work since the previous round; the implementer then
handles every finding of that round together, whatever its severity.

| Item | Rule |
| --- | --- |
| Round | A fresh reviewer instance. Round 1 reviews the whole change; each later round reviews every fix made since the previous round and what it affects. Input: the earlier rounds' findings, the round's diff scope and the effort. |
| Fixing | The implementer fixes every finding of the round, P1, P2 and P3 together (a P2 or P3 may be waived with a reason), and closes the round: `reverify` for code; for reconcile, a new `reconcile-check`; for Planning, the next `challenger-NN` summary or the `worker` envelope's summary. |
| Next round | Runs when any fix of the batch fails the minor-fix conditions (§3.2). The whole batch goes to the next round, never a subset. |
| End | The round returns no finding, or every fix of the batch meets §3.2 and is self-verified. |
| Round count | The implementer starts each round's envelope summary with `round <N>;` (and `closes reconcile-check-<NN>;` for a closing reconcile check), so counts are read from summaries, never from new fields. Counted across `devkit workflow return` within one segment. |

Hand-over to the user:

| Cause | Unit path (worker or Host) | Session |
| --- | --- | --- |
| At the cap round (the third after the initial review), the batch does not meet §3.2 | `problem` in the `worker` envelope; recovery names the open findings | Reported in the conversation; not integrated |
| The same P1 recurs after its fix (marked `recurs:`) | Same | Same |
| A P1 the implementer holds invalid, still asserted after one more round given the implementer's counter-evidence (tests or output) | `questions` entry with the reviewer's and the implementer's positions as options | Asked in the conversation |

The cap only limits further rounds: at the cap round a batch that fully meets §3.2 ends the loop whatever its
severity; any batch that would need another round is handed over, P2 and P3 included unless each is waived with a
reason. After a hand-over, a P1 the user rules invalid is closed with `reverify --waive <N>=<reason>` citing the
`answer` envelope (the only waiver a P1 may carry; for reconcile and Planning the same goes into the new
`reconcile-check` or the `worker` summary), and a fix the user asks for after a cap or recurrence problem gets one
further fresh round outside the cap, named by the `resolution` envelope. This is not the `exception` stage.

### 3.2 Minor-fix self-verification at `high`

The initial `code-reviewer`, `reconcile-reviewer` and `high` Planning `challenger` calls stay mandatory. After a
round, its batch MAY be self-verified instead of starting the next round only when every fix in it meets all of:

| Condition | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| Location | Only the location the finding's `evidence` names | Only the document or entry the finding names | Only the proposal section the finding names |
| Nature | Typo, comment, formatting, in-scope rename, test-only addition, or the `suggested_action` applied as written when it names a concrete edit | Wording only, or a concrete `suggested_action` applied as written | Wording only, or a concrete `suggested_action` applied as written |
| Contract | No public API, schema, error code, CLI output or other package touched | The contract's meaning is unchanged | No decision changed |
| Evidence | Behavior fixes: a test or check reproducing the `failure_condition` passes (for a P1, it failed before the fix). Text-only kinds: the diff is limited to the named location | The edited text and the actual diff are shown to agree | The edited text is shown to agree with the finding |

Uncertainty on any condition, for any fix, requires the next round for the whole batch. The self-verification is
recorded with reason and evidence; a recurring finding can no longer be closed by it.

### 3.3 Severity levels

| Level | Code review | Reconcile | Planning |
| --- | --- | --- | --- |
| P1 | Violates an acceptance criterion or contract; a correctness defect, data loss or a security issue | A missing target for a changed behavior or contract, or a reflection that contradicts the implementation or contract | The design fails, or conflicts with an accepted ADR or capability |
| P2 | A defect with a workaround | An incomplete or imprecise reflection with no contradiction | A defect in how a decision is specified, with a workaround |
| P3 | An improvement | An improvement | An improvement |

Severity is the reviewer's; the implementer records it as returned and never relabels it. It has no effect on checks.

### 3.4 Mandatory `scout` in `high` Planning

`high` Planning runs `scout`, starting from `devkit spec refs <ID> --direction in` for each capability and ADR the
proposal touches, so its output is a list the `challenger` input cites. The `plan-accept` request reports a missing
`scout` envelope at `high` as it does a missing `challenger`.

### 3.5 Reclassification advice for `high` session work

When `high` is proposed for a `session` task, the advice follows what the work does (section 1.1): a contract or
document kind proposes `spec` depth, reversing an accepted decision proposes `proposal` depth, anything else gives no
advice. If the user keeps `session`, the work runs at `high` as defined.
