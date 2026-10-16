# Human Interaction Contract

**Package**: `devkit.workflow`. Commands and error codes: [CLI and Output Contract](cli-and-output.md).  
**Related**: [Workflow Engine Overview](overview.md#3-approval-gates), [Workflow Definitions and Checks](definition-and-checks.md).

## 1. Scope

The engine stops for a person in four situations: an approval gate, a declared `human` check, the choice of the next workflow after a handoff, and a question a delegated run recorded in its `worker` envelope. This document defines the data contract between the engine and whoever answers: what a request looks like, what an answer looks like, where answers are stored and how the engine applies them. Presentation is out of scope: a terminal agent, an IDE panel, a chat bot or a web page is compliant as long as it reads requests from the engine's output and writes answers in the record format below. The engine never infers an answer from conversation.

## 2. Request Kinds

| Kind | Asked when | Answer |
| --- | --- | --- |
| `approve` | A gated stage's exit checks all hold and `approvals.<gate>` is `ask`; or a declared `human` check in the current stage is unmet. | `accept` or `decline`, with an optional note. |
| `choose` | The bound workflow is complete, it declares `next` candidates, and `approvals.handoff` is `ask` (or `auto` found no eligible candidate). Also every unanswered question of a `worker` envelope ([Review Envelopes](envelopes.md#11-questions-answers-problems-and-resolutions)). | Handoff: `accept` with one eligible option id, or `decline`. Question: an answer envelope with one option id, or `choice: null` and the answer in its decision when the question allows a note. |
| `feedback` | Never emitted by the engine. Reserved for notes a person attaches to a stage or artifact at any time. | `accept` with free text. Never blocks. |

Questions reuse the `choose` kind rather than adding one, so a terminal agent or a web page renders gate requests, handoff choices and questions with one renderer. They differ in how the answer comes back: a question's `answer` is `envelope`, its target type is `question`, and the person's choice and note are rewritten into an `answer` envelope by whoever processes them (`devkit workflow envelope new --kind answer`); `devkit workflow answer` refuses it (`DECISION_INVALID`). A question is never declined or cancelled: it stays open until an answer envelope answers it.

`cancel` is valid for every kind of decision record: the person dismissed the request without deciding. A cancelled record is kept for the audit trail and has no effect on evaluation.

Two more record kinds are written by the engine itself rather than answering a request: `return` records (section 5) and the `choose` record that `handoff --workflow <id>` writes for an explicit choice.

## 3. Request

`devkit workflow next` emits every open request of the unit, in text as one `[REQUEST: ...]` line each and in JSON as the `requests` array. `devkit workflow requests --unit DIR` prints only that list.

```json
{
  "id": "gate:integration",
  "kind": "approve",
  "title": "Approve integration",
  "prompt": "Approve gate 'integration' to finish stage 'integrate' of direct-delivery.",
  "target": {"type": "gate", "name": "integration", "stage": "integrate"},
  "options": [],
  "allow_note": true,
  "declined": null,
  "answer": "record"
}
```

| Field | Meaning |
| --- | --- |
| `id` | Deterministic identifier, unique among the unit's open requests: `gate:<gate>`, `check:<name>`, `handoff`, or `question:<worker-NN>.<question id>` (`question:worker-01.q1`). An answer references it. |
| `kind` | `approve` or `choose` (the engine never emits `feedback`). |
| `title` | Short label for a chip or button row, at most 40 characters. |
| `prompt` | One sentence a person can act on. |
| `target` | What the request decides: `{"type": "gate" \| "check" \| "handoff" \| "question", "name", "stage"}`. `stage` is the current stage id, `null` for a handoff, and the worker envelope's stage for a question, whose `name` is `<worker-NN.yaml>#<question id>`. |
| `options` | `choose` only: `[{"id", "description", "recommended", "eligible"}]`, in declaration order; for a handoff `description` lists the candidate's `when` checks with their results. Exactly one option is chosen. An ineligible option is shown but cannot be accepted. A question's options are its own, all eligible, possibly none. |
| `allow_note` | Whether a note may accompany the answer: `true`, except for a question that sets `allow_note: false`. |
| `declined` | The latest `decline` record for this request (`{"file", "note", "at"}`) when the request is still open, otherwise `null`. A declined request stays open: it may be asked again. |
| `answer` | How the answer reaches the engine: `record` (`devkit workflow answer` or a host's record), `given` (the definition's `gates.<gate>.answer`: after the person's approval the executor passes `next --given <gate>` on this and every later run and writes nothing; an objection takes a return path) or `envelope` (a question: an `answer` envelope). `record` for every other request that is not a gate. |
| `context` | A question's `context` (what it rests on), else `null`. |

Text form (free text is a JSON string literal, so it always stays on one line):

```text
[REQUEST: id=gate:integration kind=approve title="Approve integration" target=gate:integration stage=integrate note=allowed]
[REQUEST: id=gate:release kind=approve title="Approve release" target=gate:release stage=release note=allowed answer=given]
[REQUEST: id=handoff kind=choose title="Choose next workflow" options=spec-driven,hotfix,direct-delivery eligible=hotfix,direct-delivery recommended=-]
[REQUEST: id=question:worker-01.q1 kind=choose title="Storage format" target=question:worker-01.yaml#q1 stage=direction-handoff options=a,b recommended=a note=allowed answer=envelope]
[DECLINED: id=gate:integration file=decisions/01-gate-integration.yaml note="rebase first"]
```

Gate and check requests appear only for the current stage (or the pending handoff), so a unit has at most a handful open at once; questions appear whatever the stage until answered, and while any is unanswered, or a problem is unresolved, no gate request is asked ([Review Envelopes, section 4](envelopes.md#4-hold-blocked-and-waiting-for-answers)). Everything in a request is derived from the definition, the project policy and the unit's files; nothing is stored.

## 4. Answer

An answer is a decision record written to `<unit>/decisions/<NN>-<request>.yaml`, where `NN` is a sequence per unit of at least two digits and `<request>` is the request id with `:` replaced by `-`. The file is YAML with these keys:

```yaml
request: gate:integration
kind: approve
action: decline       # accept | decline | cancel
workflow: direct-delivery
stage: integrate
note: "rebase first"
by: mj                # optional: who answered
at: "2026-10-12T09:30:00Z"
```

| Key | Required | Rules |
| --- | --- | --- |
| `request` | yes | An open request id of the unit, or `feedback:<target>` for a free note. The file name must be `NN-<request with : as ->.yaml`. |
| `kind` | yes | Follows from the request id: `approve` for `gate:*` and `check:*`, `choose` for `handoff`, `feedback` for `feedback:*`, `return` for `return:*`. |
| `action` | yes | `accept`, `decline` or `cancel`. |
| `workflow` | yes | The workflow the unit was evaluated against when the answer was given. |
| `stage` | `approve` | The stage of the request (`target.stage`); other kinds may omit it. |
| `value` | `choose`/`feedback` + `accept` | `choose`: one eligible option id. `feedback`: the text. Absent for `approve` and `return`, and for every action other than `accept`. |
| `note` | no | Free text. Recommended on `decline`. |
| `by` | no | Identifier of the person or host that recorded the answer. |
| `at` | yes | ISO-8601 timestamp; a quoted string or a YAML date/timestamp. `answer` and `return` write UTC to the microsecond (`2026-10-12T09:30:00.250000Z`, the fraction omitted when it is zero); a value without a fraction stands for its whole second. |

No other key is allowed. Records are never edited or deleted by the engine. Only records of the **current workflow segment** count: those whose `workflow` is the evaluated workflow and whose sequence is above the `last_decision` of the anchor's latest `workflow_history` entry. Within the segment, the **effective** decision for a request is its latest non-`cancel` record by sequence that no later `return` record voided (section 5). A new `accept` after a `decline` supersedes it; a `cancel` changes nothing.

`devkit workflow answer --unit DIR --request ID --action ACTION [--value V] [--note TEXT] [--by NAME]` validates the answer against the open requests and writes the record with the next free sequence number. Among the records devkit writes, a sequence number belongs to one record of the unit, whatever its request: writers take an exclusive lock on the `decisions/` directory itself (waiting at most 10 seconds for another writer, then `LOCK_HELD`; `LOCK_UNSUPPORTED` where `flock` is unavailable; `PATH_UNSAFE` when `decisions/` is a symbolic link), number the record above every record file present, and write it whole: a hidden temporary file (`.<name>.<12 hex digits>.tmp`, which loaders and `lint-clean` skip) takes the record's name through a hard link that never replaces a file, or, on a file system without hard links, through a rename after checking that the name is free. Concurrent answers and returns are therefore strictly ordered, and an interrupted write leaves no partial record. The lock is on the directory rather than a lock file so that nothing but records sits in `decisions/`. A host with its own UI may write the same file directly, but it bypasses the lock: its file can take a sequence number another record also holds, or (without hard links) be replaced if it appears in the instant between the check and the rename. A host that writes records should number them above every file present and create them exclusively. The engine validates every record on read and reports a malformed record, or a handoff choice that is not an eligible candidate, as `[DECISION_ERROR: file "reason"]` without failing. In JSON each one is an entry of the result's `errors` list, the `to_dict()` of an advisory error with `code`, `message` and `file`: `DECISION_RECORD_INVALID` (`DecisionRecordError`) for a malformed record, `HANDOFF_CHOICE_IGNORED` (`HandoffChoiceIgnoredError`) for an ignored choice.

## 5. How the Engine Applies Answers

- **Approve gate.** The implicit `gate:<gate>` check is satisfied when the effective decision is `accept` (`[GATE: ... source=decision:decisions/NN-...yaml]`), or when the executor passes `--given <gate>`. The gate is asked only once the stage's exit checks hold. A `decline` leaves the stage current; `next` prints `[DECLINED: ...]` with the note next to the stage's `[RETURNS]` so the agent can take the work back.
- **Human check.** A declared `human` check behaves like a gate under the id `check:<name>`.
- **Per stage.** An `approve` record answers its request for the stage named in its `stage` field only. A gate or human check used by several stages of one workflow is asked, and answered, in each of them; an approval given in one stage never satisfies another.
- **Handoff choice.** Under `approvals.handoff = "ask"`, an `accept` whose value is an eligible candidate sets `chosen` in `[HANDOFF: ...]`; `devkit workflow handoff --unit DIR` then rebinds without `--workflow`. `handoff --workflow <id>` writes the same accepted `handoff` record before rebinding. Under `auto`, a recorded choice takes precedence over the engine's first-eligible pick. A recorded choice that is not an eligible candidate is reported as a `[DECISION_ERROR]` and ignored.
- **Returns.** When the unit goes back to an earlier stage, approvals given for that stage and later ones must be given again. `devkit workflow return --unit DIR --to STAGE [--note TEXT] [--by NAME]` records it as an accepted `return:<stage>` record; `STAGE` must be the current stage or an earlier one. `next` never records a return: when it finds the current stage earlier than a stage with a valid approval, it lists those approvals as `[STALE_APPROVAL: ... counts=yes void_with="devkit workflow return --unit DIR --to STAGE"]` and they keep counting. Whether the redone work needs fresh approval is a person's decision; run `return` to require it. An `approve` record is void once a later `return` record targets its stage or an earlier one. The same return voids the envelopes recorded before it for its target stage or a later one (their `stage` placed in the definition, their `created_at` not certainly after the record's `at`), so a stage whose exit reads an envelope (`envelope-review-passed`, `envelope-check-pass`) is satisfied again only by a new one; an envelope without a stage or a `created_at` is never voided. Each time stands for the span its precision allows: `2026-10-12T09:30:00Z` for that whole second, a time to the microsecond for that microsecond. An envelope counts only when the earliest moment its `created_at` allows is at or after the latest moment the return's `at` allows; when the order is unknown (both in the same second, written to the second) the envelope is void, since asking for it again is safer than letting one that may predate the return satisfy the stage. `envelope new` never falls into that case: it writes `created_at` to the microsecond and, when the clock has not passed the latest accepted return of the segment yet (the same instant, a clock behind a host's record), stamps it at the end of that return's span instead, so an envelope written after a return always counts ([Review Envelopes](envelopes.md#2-authoring)). Approvals need no such rule; they are ordered by sequence number.
- **Given versus recorded.** `--given` is an assertion for the current invocation only, intended for runner checks (CI evidence), scripted use and gates the definition marks `answer: given`; it is not stored. A recorded decision is the durable form and the one hosts should use for every other approval. A `given` gate trades the record for one fewer commit: its authority is the person's approval the executor reports, or the runner's binding (a PR's ready state).
- **Policy `auto` and `off`.** No request is emitted; the output records the policy that decided (`[GATE: ... source=policy]` while the stage is current, `[SKIPPED: ...]`), so a reader can tell a delegated decision from a human one.

Decision records stay in the unit through handoffs as an audit trail, but they belong to the segment they were given in: an approval or handoff choice from a finished segment never counts in the next one, even for a gate with the same name. Envelopes written by `envelope new` are scoped the same way, by their `workflow` and `segment` keys ([Review Envelopes](envelopes.md#1-file-contract)).
