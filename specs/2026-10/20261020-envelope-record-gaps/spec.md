---
id: SPEC-envelope-record-gaps
title: 'Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries'
summary: "Lets a reverify close a challenger round, gives answer envelopes a settles list for worker assumptions the user decided, and adds a warning rule that proposal boundaries name existing paths, so Planning records match what actually happened."
status: planned
created: 2026-10-20
related_capabilities:
  - CAP-DLV-workflow-envelopes
  - CAP-DLV-delivery-workflows
  - CAP-DLV-proposal-incubation
  - CAP-GOV-spec-rules
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-envelope-record-gaps] Close gaps in Planning records: folded challenger findings, settled assumptions, proposal boundaries

## 1. Problem Statement & Motivation

Handed off from proposal PROP-envelope-record-gaps on 2026-10-20.
- **Preserved Materials**: `docs/materials/2026-10/20261020-envelope-record-gaps`

- **Folded challenger findings stay open** (`FB-challenger-findings-stay-open`): a planning worker folds every
  `challenger` finding into the proposal, but the envelope keeps them `open`, because only a `reverify` closes findings
  and it must name a `review-NN.yaml`. Both high-effort Planning units of 2026-10-19 reported fixed findings as open
  and counted earlier unmarked challenger rounds toward the review-loop cap, so the record no longer showed the real
  state of the review.
- **Settled assumptions have no slot** (`FB-answer-envelope-no-slot-for-settled-assumptions`): when the user's answer
  also settles a worker assumption, the answer envelope can only carry it as free text in a constraint.
- **Proposal boundaries are unchecked** (`FB-proposal-boundaries-unchecked`): `boundaries.owns` may name a capability
  area that does not exist (`capabilities/core/`), and no rule reports it.

The decisions are accepted: `ADR-reverify-closes-challenger-rounds`, `ADR-answer-envelopes-settle-worker-assumptions`
and `ADR-proposal-boundaries-name-existing-paths`. This spec implements them without changing any gate or policy.

### Source feedback

- `FB-review-loop-round-count-across-procedure-change` and `FB-review-round-count-before-markers`: the round count of
  earlier unmarked high-effort rounds and the treatment of a fold of the user's answers (Q1,
  `ADR-reverify-closes-challenger-rounds`). Their resolution is verified once the review-loop text ships.
- `FB-challenger-findings-stay-open` (Q1), `FB-answer-envelope-no-slot-for-settled-assumptions` (Q2) and
  `FB-proposal-boundaries-unchecked` (Q3): reproductions cited by the ADRs.

## 2. User Stories

- **US-1**: As a Planning executor, I want to close a folded `challenger` round in its own record, so that the
  `plan-accept` request shows each finding as resolved, waived or open as it really is.
- **US-2**: As whoever records the user's answers, I want a field for the worker assumptions the user settled, so that
  `constraints` carry only what an answer adds.
- **US-3**: As a Planning executor, I want a warning when a proposal's `target_area` or `boundaries.owns` names no
  existing path, so that the boundary handed to Development names real paths by `plan-accept`.

## 3. Non-Goals

1. **Scope Excluded**: any gate, policy or workflow-check change; no check of `sdd-proposal` starts reading
   `challenger` findings or `reverify` envelopes.
2. **Scope Excluded**: renaming the `reverify` key `review` or back-filling a closing `reverify` for existing
   `challenger` envelopes.
3. **Scope Excluded**: assumption IDs on `worker` envelopes; `settles` holds and releases nothing.
4. **Scope Excluded**: checking `boundaries.excludes`, rescanning proposals for deleted paths, a fix for
   `RULE-proposal-boundaries`, and any change of `devkit spec proposal new` or `devkit spec proposal handoff`.
5. **Scope Excluded**: deploying the new rule into this repository's `.devkit/` installation (`devkit sync` is the
   Host's step after integration).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A reverify closes a challenger round
- **Given** a unit with `envelopes/challenger-01.yaml` holding two open findings and no `review` envelope
- **When** `devkit workflow envelope reverify --unit <dir> --from envelopes/challenger-01.yaml --resolve 1 --waive "2=kept as designed"` runs
- **Then** it exits `0` and writes `reverify-01.yaml` with `review: challenger-01.yaml`, finding 1 `resolved`, finding 2
  `waived` with that `waiver`, and prints `open_findings=0`; `devkit workflow envelope check --unit <dir>` prints that
  reverify's line ending in `review=challenger-01.yaml]`, and its `--format json` entry carries
  `"review": "challenger-01.yaml"`

### [AC-02] The challenger state follows its last reverify and the review state ignores it
- **Given** a unit with `review-01.yaml` (one open finding), `challenger-01.yaml` (one open finding) and a reverify
  naming `challenger-01.yaml` that resolves its finding
- **When** the checks `envelope-check-pass(challenger)` and `envelope-check-pass(review)` are evaluated
- **Then** the challenger check is met (the reverify decides) and the review check is unmet (the review state is still
  `review-01.yaml`, no reverify of a challenger round counts for it)

### [AC-03] `--from` refusals name the challenger form
- **Given** a unit without any `review` envelope
- **When** `envelope reverify --from latest --resolve all` runs, or `--from` names a `scout-01.yaml`
- **Then** it exits `2` with `ENVELOPE_FROM_INVALID`, writes no file, and the `[FIX]` names
  `--from envelopes/challenger-NN.yaml`

### [AC-04] A challenger envelope records findings as found
- **Given** a findings file whose finding carries `resolution: resolved`
- **When** `devkit workflow envelope new --kind challenger --findings-file <file>` runs
- **Then** it exits `2` with `ENVELOPE_FLAG_INVALID` and writes no file, as `envelope review` does

### [AC-05] A reverify must name a review or challenger round
- **Given** a `reverify-01.yaml` whose `review` is `scout-01.yaml`, and one whose `review` is `challenger-01.yaml`
- **When** `envelope check` loads them
- **Then** the first is reported as `[ENVELOPE_ERROR: ...]` naming `review-NN.yaml` or `challenger-NN.yaml`, the
  command exits `1`, and the second loads

### [AC-06] An answer settles worker assumptions by position
- **Given** `worker-01.yaml` with a question `q1` and three assumptions
- **When** `envelope answer --answers-to worker-01.yaml --answers-file <q1 answer> --settle "2=Keep the TOML layout"` runs,
  and separately an answer with only `--settle 3=...` and no `--answers-file`
- **Then** both exit `0`; the first file holds `settles: [{assumption: 2, decision: "Keep the TOML layout"}]` written
  after `answers`, the second holds `settles` and no `answers`; `envelope check --format json` entries carry `settles`;
  after only the settles-only answer `q1` is still reported as `[PENDING_QUESTION: ...]`

### [AC-07] Settles that do not fit are refused or malformed
- **Given** `worker-01.yaml` with two assumptions
- **When** `envelope answer` runs with `--settle 3=...` (out of range), with `--settle 1=a --settle 1=b`
  (duplicate), or with `--settle x` (no `N=`); and when an `answer-NN.yaml` with `settles: [{assumption: 5, ...}]` is
  loaded
- **Then** the out-of-range command exits `2` with `ENVELOPE_REFERENCE_INVALID`, the duplicate and the malformed flag
  exit `2` with `ENVELOPE_FLAG_INVALID`, no file is written; the loaded file is an `[ENVELOPE_ERROR: ...]` and the
  questions it answers are pending again

### [AC-08] Proposal boundary entries that resolve pass
- **Given** a `reviewing` proposal whose `target_area` and `boundaries.owns` entries are a repository path
  (`packages/a/`), a docs-root path (`capabilities/delivery/`), a bare capability area (`delivery/`), a file
  (`docs/glossary.md`) and, for a proposal with `namespace: api`, an area under `docs/packages/api/capabilities/`
- **When** `devkit rules check` runs `RULE-proposal-boundaries` over the workspace
- **Then** it reports no violation

### [AC-09] Missing, placeholder, invalid and malformed entries are reported as warnings
- **Given** a `draft` proposal with `target_area: capabilities/<area>/` and `boundaries.owns` entries `core/`
  (no such area), `/abs`, `src/*`, `docs/glossary.md/` (a file named as a directory) and the item `42`, and a
  proposal whose `owns` is a string
- **When** the rule runs
- **Then** each is one `severity=warning` violation on its entry's line (the placeholder with its own message naming
  the area, the missing paths "names no existing path", the invalid ones "not a literal repository-relative path",
  the non-string item and the string `owns` as malformed), and `boundaries.excludes` entries are never reported

### [AC-10] Only current proposals in the run's targets are checked
- **Given** a `rejected` proposal and an `accepted` proposal, both owning `missing/`, and a capability that is not a
  proposal
- **When** the rule runs over the whole workspace, and then targeting only the capability file
- **Then** the whole-workspace run reports the accepted proposal only, and the targeted run reports nothing

### [AC-11] The procedures describe the new records and checks
- **Given** the `spec` bundle text
- **When** `references/review-loop.md`, `references/planning.md`, `references/worker-records.md`,
  `workflows/sdd-proposal.md` and the proposal template are read
- **Then** they state: the closing `reverify --from envelopes/challenger-NN.yaml` after each Planning fold at
  `medium` and `high`; the round count of unmarked rounds (counted in sequence order only before the loop's first
  marker when a `worker` envelope of the segment records `activity_effort: high`, else a `high` loop starts at
  round 1; the higher number holds; a `reverify` is never a round); a fold of the user's answers as a new batch of the
  same loop with one fresh round outside the cap; `settles` in place of `constraints` for a settled assumption; that
  the Planning executor clears `RULE-proposal-boundaries` reports before the `plan-accept` request; and the accepted
  boundary forms with the nearest-existing-parent form for a path Development will create

## 5. Assumptions

- The planning-worker contract no longer holds the ordered Planning steps (`SPEC-direct-planning-procedure`); the
  challenger-reverify step goes into `references/planning.md` step 3 instead of the contract's step 4, as the carried
  coordination note says.
- A malformed `--settle` flag and duplicate positions are refused with `ENVELOPE_FLAG_INVALID` (the code `--waive`
  uses); an out-of-range position with `ENVELOPE_REFERENCE_INVALID` (the ADR's code for a reference that does not fit).
- A settles-only answer still requires `answers_to` to name a well-formed `worker` envelope, but not one with questions.
- The rule reports a non-mapping `boundaries` and a non-string `target_area` as malformed, like a non-list `owns`.
- The rule reads proposal anchors whatever their `historical` state: an accepted proposal is checked when targeted or
  in a whole-workspace run, as the ADR decides.
- The rule ships in the bundle and in `CAP-HARN-agent-guidance`'s rule asset list; this repository's deployed copy
  follows on the next `devkit sync`.
