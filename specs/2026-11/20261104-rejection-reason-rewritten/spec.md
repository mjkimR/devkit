---
id: SPEC-rejection-reason-rewritten
title: Rejection records carry a rewritten decision, not a quote
summary: "Aligns the proposal rejection path with the records rule: the rejection commit, the rejection ADR and the contract state the user's decision and reason as a rewritten decision sentence instead of a verbatim conversation quote."
status: planned
created: 2026-11-04
related_capabilities: [CAP-DLV-proposal-planning]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-rejection-reason-rewritten] Rejection records carry a rewritten decision, not a quote

## 1. Problem Statement & Motivation

The spec constitution's records rule says records "carry decisions, never conversation quotes, paraphrases or
dates", and the feedback template says "Never quote or paraphrase the user". The proposal rejection path is the one
place that asks for the opposite: the `sdd-proposal` workflow's Gate rules put "the user's reason, unrewritten" into
the rejection commit, and the `feedback-hygiene` playbook writes the rejection ADR "quoting the reason from the
rejection commit". `CAP-DLV-proposal-planning` rule 9 says only "with the user's reason", which an executor reads
either way. The result is a verbatim conversation fragment, in the conversation's language, inside a commit message
and an accepted English ADR (`ADR-reject-ux-rules-path-exclusion` carries one), where every other record holds a
rewritten decision. A quote adds nothing a decision sentence does not: the rejection commit stays in Git either way,
and the ADR already states the rejected direction and the chosen alternative. The user decided that no rejection
needs the verbatim form.

## Source feedback

- `FB-rejection-reason-quoted-verbatim` (repo, change-request): the three passages above and the proposed rewrite;
  this spec fixes it directly.

## 2. User Stories

- **US-1**: As the executor that receives a rejection, I want the workflow, the contract and the proposal scaffold to
  ask for the user's decision and reason as a decision sentence, so that the rejection commit follows the same records
  rule as every other record.
- **US-2**: As the Host running the `feedback-hygiene` playbook, I want the rejection ADR to state the recorded
  decision and reason in English, so that an agent that never saw the conversation reads an ADR, not a transcript.

## 3. Non-Goals

1. **Scope Excluded**: rewriting past rejection commits; Git history keeps the one existing verbatim commit
   (aa67659f) unchanged.
2. **Scope Excluded**: changing the records rule itself, the `answer` envelope grammar or the hygiene warning's code
   and message; only the wording that asks for a quote changes.
3. **Scope Excluded**: the release handbook and consumer repositories' installed copies; `devkit sync` carries the
   bundle change.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The workflow asks for a decision sentence
- **Given** the `sdd-proposal` workflow source (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md`)
- **When** its Gate rules describe a rejection
- **Then** one block states that the rejection commit carries the user's decision and its reason rewritten as one
  English decision sentence naming `user` as the decider, never a conversation quote, and the word `unrewritten`
  does not occur in the file; the spec bundle guidance tests assert both.

### [AC-02] The playbook states, not quotes
- **Given** the `feedback-hygiene` playbook source Step 4
- **When** it describes the rejection ADR
- **Then** one block states that the ADR states the decision and reason recorded in the rejection commit, found with
  the `git log -1 --format='%H %B' -S'status: rejected' -- <proposal.md>` command, and the phrase `quoting the reason`
  does not occur; the guidance tests assert both.

### [AC-03] The contract names the form
- **Given** `CAP-DLV-proposal-planning` rule 9
- **When** it describes the rejection commit
- **Then** it states that the commit carries the user's decision and reason as a decision sentence, never a quote,
  and that the hygiene ADR restates that decision; `devkit rules check` passes on the file.

### [AC-04] The proposal scaffold hint agrees
- **Given** the proposal scaffold template text in `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`
- **When** a new proposal is scaffolded
- **Then** its Lifecycle comment says the rejection commit carries the user's decision and reason as a decision
  sentence; `just test devkit-spec tests/integration/features/proposals` passes.

### [AC-05] The existing rejection ADR follows the rule
- **Given** `ADR-reject-ux-rules-path-exclusion`
- **When** its Decision Outcome is read
- **Then** it states the user's decision and reason as an English decision sentence citing the rejection commit, with
  no quoted conversation text, and `devkit rules check` passes on the file.

### [AC-06] The source feedback is resolved
- **Given** `FB-rejection-reason-quoted-verbatim`
- **When** this change lands
- **Then** its status is `resolved` with a Disposition line naming this spec and the verification, and
  `devkit rules check` passes on the file.

### [AC-07] No bundle asks for a quote
- **Given** the repository's bundle sources
- **When** `rg -n -i "unrewritten|quoting the reason" packages/*/src/*/bundles` runs
- **Then** it prints nothing.

## 5. Assumptions

- The records rule's wording ("never conversation quotes, paraphrases or dates") stays as it is; the rejection
  passages are aligned to it rather than the rule gaining an exception.
- The hygiene warning's `[FIX]` text ("find the rejection commit and its reason ... write a rejection ADR") asks for
  no quote and is unchanged.
