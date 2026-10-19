---
id: PADR-answer-envelopes-settle-worker-assumptions
title: Answer envelopes settle worker assumptions
summary: Adds an optional settles list to answer envelopes, each item naming a worker assumption by its position and the user's decision on it, written with a repeatable --settle flag.
proposal: PROP-envelope-record-gaps
status: draft
created_at: 2026-10-19
---

# [PADR-answer-envelopes-settle-worker-assumptions] Answer envelopes settle worker assumptions

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

When the user's answers also settle assumptions a worker recorded (its `worker` envelope's `assumptions`), the
`answer` envelope has no place for them: its items are `{question, choice, decision, constraints}`, each tied to a
question. A run recorded them as `constraints` prefixed "Settled by the user in the same round:"
(`FB-answer-envelope-no-slot-for-settled-assumptions`), which stretches `constraints` ("only for what the answer
adds", `references/worker-records.md` section 2). Evidence: `materials/spike-evidence.md`.

## 2. Decision Drivers

- The plan-intent fixed a slot in the answer envelope; a pure convention is out.
- Worker envelopes are never overwritten, so a position in their `assumptions` list is stable.
- Consistency with `reverify --resolve N` / `--waive N=REASON`, which address findings by 1-based position.
- Settling an assumption holds nothing and releases nothing: no change to the hold of section 4.

## 3. Considered Options

- **A. `settles` items by position**: `settles: [{assumption: 2, decision: "..."}]`, the 1-based position in the
  `answers_to` worker's `assumptions`.
- **B. `settles` items by text**: the assumption string copied exactly.
- **C. Assumption ids**: give worker assumptions ids (`{id, text}`), referenced by `settles`.

## 4. Decision Outcome

- **Option A.** An `answer` envelope may carry `settles`, a list of `{assumption, decision}`: `assumption` a
  1-based position into the `assumptions` of the `answers_to` worker envelope, each at most once, `decision` one
  sentence. Positions outside that list make the envelope malformed (a reference that does not fit,
  `ENVELOPE_REFERENCE_INVALID` when authoring).
- `answers` stays required when `settles` is absent; an answer with `settles` may have no `answers`, and then
  `answers_to` must name a well-formed worker envelope with assumptions instead of questions.
- Authoring: `devkit workflow envelope answer --settle N=DECISION` (repeatable), like `--waive`.
- Only `answer` carries `settles`; it affects no hold, check or exit code.
- `references/worker-records.md` section 2 says a decision that settles a worker assumption goes into `settles`,
  never into `constraints`.

## 5. Consequences

- Engine: the `Answer`/envelope model, `_check_kind_fields`, reference validation and the `answer` command;
  `envelope check --format json` entries carry `settles`. Tests for valid, out-of-range, duplicate and
  settles-only answers.
- Contract: `CAP-DLV-workflow-envelopes` section 1.1 (table and example) and section 2 (flag table, key order).
- Option C would change every worker envelope's schema; rejected.
