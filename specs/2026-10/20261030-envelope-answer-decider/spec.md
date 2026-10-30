---
id: SPEC-envelope-answer-decider
title: Record the decider of each answer and guard reverify closures
summary: Give answer envelopes an optional per-answer decider (user, host or policy) and refuse a reverify that resolves or waives a finding its source envelope already closed.
status: in-progress
created: 2026-10-30
related_capabilities: [CAP-DLV-workflow-envelopes, CAP-DLV-cli-and-output]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-envelope-answer-decider] Record the decider of each answer and guard reverify closures

## 1. Problem Statement & Motivation

Two envelope authoring gaps make records lose or misstate a decision.

- An `answer` envelope entry holds only `question`, `choice`, `decision` and `constraints`. When one envelope records
  both the user's decisions and the Host's own sequencing decision, the two differ only in prose, although the spec
  constitution says records name `user` or `policy`. Host payloads ask workers to record answers "with `--by user`", a
  flag `devkit workflow envelope answer` does not have (`FB-answer-envelope-has-no-decider`).
- `devkit workflow envelope reverify --from <round> --resolve N` accepts a number naming a finding the source envelope
  already closed. A waived finding is rewritten as `resolution: resolved` while it keeps its `waiver`, no notice is
  printed, and the finding the author meant stays open (`FB-reverify-resolve-overwrites-waiver`).

## 2. User Stories

- **US-1**: As a Host or worker recording answers, I want each answer entry to name who decided it, so that a later
  reader can tell the user's decisions from the Host's and policy's without parsing prose.
- **US-2**: As an agent closing a review or challenger round across turns, I want a reverify that names an
  already-closed finding refused with the finding numbers, so that a wrong number never rewrites an earlier closure.

## 3. Non-Goals

1. **Scope Excluded**: no `--by` flag on `devkit workflow envelope answer` (the decider is per answer, in the answers
   file); no decider on `settles` items; no change to `devkit workflow answer`, decision records or how answers hold
   and release gates; no change to `--resolve all`, which already closes only open findings; no reopening of a closed
   finding through `reverify`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] An answer entry records its decider
- **Given** a worker envelope `worker-01.yaml` with question `q1` (options `a`, `b`) and question `q2`
- **When** `devkit workflow envelope answer --answers-to worker-01.yaml --answers-file -` reads
  `- { question: q1, choice: a, decision: Keep TOML., by: user }` and `- { question: q2, choice: null, decision: Ship
  first., by: host }`
- **Then** it exits `0`, and `answer-01.yaml` has `by: user` on the `q1` entry and `by: host` on the `q2` entry, each
  after `decision` (and after `constraints` when present)

### [AC-02] An answer without a decider stays valid
- **Given** the worker envelope of AC-01
- **When** the answers file has an entry without `by`, or a hand-written `answer-01.yaml` has entries without `by`
- **Then** the command exits `0` and writes no `by` key for that entry, and `envelope check` loads the file with no
  `ENVELOPE_INVALID` error

### [AC-03] An unknown decider is refused before writing
- **Given** the worker envelope of AC-01
- **When** the answers file has an entry with `by: person`
- **Then** the command exits `2` with `ENVELOPE_ITEMS_INVALID`, `[TARGET] --answers-file`, a message naming
  `user, host, policy`, and no envelope file is written

### [AC-04] A loaded answer with an unknown decider is malformed
- **Given** a hand-written `answer-01.yaml` whose entry has `by: person`
- **When** `devkit workflow envelope check` loads the unit
- **Then** it reports `envelopes/answer-01.yaml` as `ENVELOPE_INVALID` and exits `1`, and the question stays unanswered

### [AC-05] Detailed envelope output shows the decider
- **Given** the `answer-01.yaml` written by AC-01
- **When** `devkit workflow envelope check --details --format json` runs
- **Then** the `answers` of `envelopes/answer-01.yaml` carry `"by": "user"` and `"by": "host"`; an entry without a
  decider carries no `by` key

### [AC-06] Resolving or waiving an already-closed finding is refused
- **Given** `challenger-01.yaml` with three findings and `reverify-01.yaml` (`review: challenger-01.yaml`) that resolved
  finding 1 and waived finding 2
- **When** `devkit workflow envelope reverify --from envelopes/challenger-01.yaml --resolve 2 --waive "1=kept" --resolve
  3` runs
- **Then** it exits `2` with `ENVELOPE_FINDING_CLOSED`, `[TARGET] --resolve 2, --waive 1`, one `[DETAIL]` line
  `N: <resolution> "<issue>"` per carried finding, and no envelope file is written

### [AC-07] Open findings still close
- **Given** the state of AC-06
- **When** `devkit workflow envelope reverify --from envelopes/challenger-01.yaml --resolve 3` runs
- **Then** it exits `0`, prints `open_findings=0`, and finding 2 stays `waived` with its waiver

### [AC-08] Guidance names the decider per answer
- **Given** the spec bundle's worker-records reference §2 and the `spec-delegate` payload and worker references
- **When** a Host or worker reads how to record or hand over answers
- **Then** the `envelope answer` example carries `by`, worker records §2 defines `user`, `host` and `policy`, and the
  payload and worker references say the rewritten answers name `by` per answer

## 5. Source feedback

- `FB-answer-envelope-has-no-decider`: fully in scope (the optional per-answer `by` field, its validation and output,
  and the guidance); resolve it when the implementation is verified.
- `FB-reverify-resolve-overwrites-waiver`: fully in scope (the refusal of a closed finding named by `--resolve` or
  `--waive`); resolve it when the implementation is verified.

## 6. Assumptions

- `by: null` in a hand-written file reads as absent, like other optional keys; an empty string or any value other than
  `user`, `host` or `policy` is refused.
- "Shown where answers are printed" is the YAML the command writes and the `--details --format json` bodies of
  `envelope check`; no text line prints answer entries today, so none is added.
- The refusal of a closed finding gets a code of its own, `ENVELOPE_FINDING_CLOSED` (`INPUT_ERROR`, exit `2`), so an
  agent can branch on it apart from an out-of-range number (`ENVELOPE_FLAG_INVALID`). Its `[TARGET]` entries are the
  flag and number to drop (`--resolve 2`), so they name both the finding number and the flag to correct.
- A number outside the carried findings is still checked first and keeps `ENVELOPE_FLAG_INVALID`; a finding named by
  both `--resolve` and `--waive` in one call keeps its current behavior (the waiver wins).
