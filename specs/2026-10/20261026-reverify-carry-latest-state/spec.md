---
id: SPEC-reverify-carry-latest-state
title: Reverify carries the latest closing state
summary: A reverify that names a challenger or review round carries the findings from that round's latest closing reverify, so a second closure never reopens findings an earlier reverify resolved.
status: in-progress
created: 2026-10-26
related_capabilities: [CAP-DLV-workflow-envelopes]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-reverify-carry-latest-state] Reverify carries the latest closing state

## 1. Problem Statement & Motivation

`devkit workflow envelope reverify --from envelopes/challenger-NN.yaml` copies the findings from the named challenger
envelope itself. When an earlier reverify already closed some findings of the same round, a second closure resets them
to `open` unless the author restates every earlier `--resolve` and `--waive`. Three Planning workers hit this on
2026-10-26 while closing one challenger round across two turns (`FB-reverify-reopens-earlier-resolutions`).

## 2. User Stories

- **US-1**: As an agent closing a challenger or review round across several turns, I want a reverify that names the
  round to start from the round's latest closing state, so that I pass only the findings this turn closes.

## 3. Non-Goals

1. **Scope Excluded**: `--from latest` and `--from envelopes/reverify-NN.yaml` keep their behavior; the deciding-state
   rules of `envelope check` and workflow evaluation, the envelope schema and the `--resolve`/`--waive` syntax do not
   change.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A second closure of a challenger round keeps earlier resolutions
- **Given** `challenger-01.yaml` with three findings and `reverify-01.yaml` (`review: challenger-01.yaml`) that resolved
  finding 1 and waived finding 2 with reason `kept`
- **When** `devkit workflow envelope reverify --from envelopes/challenger-01.yaml --resolve 3` runs
- **Then** it exits `0`, prints `open_findings=0`, and `reverify-02.yaml` has `review: challenger-01.yaml` and
  resolutions `resolved`, `waived` (waiver `kept`), `resolved`

### [AC-02] Naming a review round carries its latest closing reverify
- **Given** `review-01.yaml` with two findings and `reverify-01.yaml` (`review: review-01.yaml`) that resolved finding 1
- **When** `devkit workflow envelope reverify --from envelopes/review-01.yaml` runs with no `--resolve`
- **Then** it exits `0`, prints `open_findings=1`, and `reverify-02.yaml` keeps finding 1 `resolved` and finding 2 `open`

### [AC-03] Without a closing reverify the round file is carried
- **Given** `challenger-01.yaml` with two findings and no reverify naming it, or only a reverify of another round or of
  another segment
- **When** `devkit workflow envelope reverify --from envelopes/challenger-01.yaml --resolve 1` runs
- **Then** it exits `0`, prints `open_findings=1`, and finding 2 is `open`

### [AC-04] Numbering stays over the carried list
- **Given** the state of AC-01 before its command
- **When** `devkit workflow envelope reverify --from envelopes/challenger-01.yaml --resolve 4` runs
- **Then** it exits `2` with `ENVELOPE_FLAG_INVALID` naming `finding numbers are 1..3`, and no envelope is written

## 5. Source feedback

- `FB-reverify-reopens-earlier-resolutions`: fully in scope; resolve it when the implementation is verified.

## 6. Assumptions

- The closing state of a named round is the last reverify among the current segment's envelopes whose `review` names
  the round's file, the same segment scope `--from latest` uses.
- The round is matched by file name, so `--from` with an absolute path to the round file behaves the same way.
