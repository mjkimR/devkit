# Human Interaction Contract

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-workflow-engine`  
**Related Documents**:
- [Workflow Engine Overview](overview.md)
- [Workflow Definitions and Checks](definition-and-checks.md)

---

## 1. Scope

The workflow engine stops for a person in three situations: an approval gate, a declared `human` check, and the choice of the next workflow after a handoff. This document defines the data contract between the engine and whoever answers: what a request looks like, what an answer looks like, where answers are stored and how the engine applies them.

It deliberately defines nothing about presentation. A terminal agent, an IDE panel, a chat bot or a web page may render requests however it likes; it is compliant as long as it reads requests from the engine's output and writes answers in the record format below. The engine never infers an answer from conversation.

The contract borrows the parts that several agent frameworks agree on:

- flat, JSON-serializable requests with a small set of primitive fields (MCP elicitation, LangGraph interrupts);
- a three-way answer, `accept` / `decline` / `cancel`, that separates an explicit refusal from a dismissed dialog (MCP elicitation);
- the engine, not the UI, supplies the set of options and the recommendation (Codex `availableDecisions`, Claude Code `AskUserQuestion`);
- every request has an identifier and an answer always carries it, because several requests can be open at once (LangGraph interrupt ids, OpenAI Agents SDK interruptions);
- answers are durable records so that a run can stop, wait as long as it needs, and resume idempotently (Claude Agent SDK `defer`, LangGraph checkpoints);
- a refusal carries a note that flows back into the work (HumanLayer, Claude Agent SDK `deny(message)`).

---

## 2. Request Kinds

| Kind | Asked when | Answer |
| --- | --- | --- |
| `approve` | A gated stage is otherwise done and `approvals.<gate>` is `ask`; or a declared `human` check in the current stage is unmet. | `accept` or `decline`, with an optional note. |
| `choose` | The bound workflow is complete, it declares `next` candidates, and `approvals.handoff` is `ask` (or `auto` found no eligible candidate). | `accept` with one option id (or several when `multi`, or free text when `allow_other`), or `decline`. |
| `feedback` | Never emitted by the engine. Reserved for notes a person attaches to a stage or artifact at any time. | `accept` with free text. Never blocks. |

`cancel` is valid for every kind: the person dismissed the request without deciding. A cancelled record is kept for the audit trail and has no effect on evaluation.

---

## 3. Request

`agent-workflow next` emits every open request of the unit, in text as one `[REQUEST: ...]` line each and in JSON as the `requests` array. `agent-workflow requests --unit DIR` prints only that list.

```json
{
  "id": "gate:integration",
  "kind": "approve",
  "title": "Approve integration",
  "prompt": "Approve gate 'integration' to finish stage 'integrate' of direct-delivery.",
  "target": {"type": "gate", "name": "integration", "stage": "integrate"},
  "options": [],
  "multi": false,
  "allow_other": false,
  "allow_note": true,
  "declined": null
}
```

| Field | Meaning |
| --- | --- |
| `id` | Deterministic identifier, unique among the unit's open requests: `gate:<gate>`, `check:<name>` or `handoff`. An answer references it. |
| `kind` | `approve` or `choose` (the engine never emits `feedback`). |
| `title` | Short label for a chip or button row, at most 40 characters. |
| `prompt` | One sentence a person can act on. |
| `target` | What the request decides: `{"type": "gate" \| "check" \| "handoff", "name", "stage"}`. `stage` is the current stage id, or `null` for a handoff. |
| `options` | `choose` only: `[{"id", "label", "description", "recommended", "eligible"}]`, in declaration order. An ineligible option is shown but cannot be accepted. |
| `multi` | `choose` only: whether several option ids may be accepted at once. Handoff is single-select. |
| `allow_other` | `choose` only: whether free text is accepted instead of an option id. Handoff does not allow it. |
| `allow_note` | Whether a note may accompany the answer. Always `true` today. |
| `declined` | The latest `decline` record for this request (`{"file", "note", "at"}`) when the request is still open, otherwise `null`. A declined request stays open: it may be asked again. |

Text form:

```text
[REQUEST: id=gate:integration kind=approve title="Approve integration" target=gate:integration stage=integrate note=allowed]
[REQUEST: id=handoff kind=choose title="Choose next workflow" options=spec-driven,hotfix,direct-delivery eligible=hotfix,direct-delivery recommended=- multi=no other=no]
[DECLINED: id=gate:integration file=decisions/01-gate-integration.yaml note="rebase first"]
```

Requests appear only for the current stage (or the pending handoff), so a unit has at most a handful open at once. Everything in a request is derived from the definition, the project policy and the unit's files; nothing is stored.

---

## 4. Answer

An answer is a decision record written to `<unit>/decisions/<NN>-<request>.yaml`, where `NN` is a two-digit sequence per unit and `<request>` is the request id with `:` replaced by `-`. The file is YAML with these keys:

```yaml
request: handoff
kind: choose
action: accept        # accept | decline | cancel
value: hotfix         # choose: option id, list of ids when multi, or free text when allow_other
note: "spec is not needed for a one-line fix"
by: mj                # optional: who answered
at: "2026-10-12T09:30:00Z"
```

| Key | Required | Rules |
| --- | --- | --- |
| `request` | yes | An open request id of the unit, or `feedback:<target>` for a free note. |
| `kind` | yes | Must equal the request's kind (`feedback` for `feedback:*`). |
| `action` | yes | `accept`, `decline` or `cancel`. |
| `value` | `choose` + `accept` | An eligible option id; a list of them when `multi`; free text only when `allow_other`. Absent for `approve`. |
| `note` | no | Free text. Recommended on `decline`. |
| `by` | no | Identifier of the person or host that recorded the answer. |
| `at` | yes | ISO-8601 UTC timestamp. |

Records are never edited or deleted by the engine. The **effective** decision for a request is its latest non-`cancel` record by sequence. A new `accept` after a `decline` supersedes it; a `cancel` changes nothing.

`agent-workflow answer --unit DIR --request ID --action ACTION [--value V]... [--note TEXT] [--by NAME]` validates the answer against the open requests and writes the record. A host with its own UI may write the same file directly; the engine validates on read and reports a malformed or stale record as `[DECISION_ERROR: ...]` without failing.

---

## 5. How the Engine Applies Answers

- **Approve gate.** The implicit `gate:<gate>` check is satisfied when the effective decision is `accept` (detail `accepted by decisions/NN-...yaml`), or when the executor passes `--given <gate>`. A `decline` leaves the stage current; `next` prints `[DECLINED: ...]` with the note next to the stage's `[RETURNS]` so the agent can take the work back.
- **Human check.** A declared `human` check behaves exactly like a gate under the id `check:<name>`.
- **Handoff choice.** Under `approvals.handoff = "ask"`, an `accept` whose value is an eligible candidate sets `chosen` in `[HANDOFF: ...]`; `agent-workflow handoff --unit DIR` then rebinds without `--workflow`. Under `auto`, a recorded choice takes precedence over the engine's first-eligible pick. A choice that is no longer eligible is reported and ignored.
- **Given versus recorded.** `--given` is an assertion for the current invocation only, intended for runner checks (CI evidence) and scripted use; it is not stored. A recorded decision is the durable form and the one hosts should use for approvals.
- **Policy `auto` and `off`.** No request is emitted; the output records the policy that decided (`[GATE: ... policy=auto]`, `[SKIPPED: ...]`), so a reader can tell a delegated decision from a human one.

Decisions belong to the unit and travel with it through handoffs; the request ids of a finished workflow segment simply stop being open.

---

## 6. CLI Summary

```bash
agent-workflow requests --unit DIR [--format text|json]                     # open requests only
agent-workflow answer --unit DIR --request ID --action accept|decline|cancel \
    [--value V]... [--note TEXT] [--by NAME] [--format text|json]            # write a decision record
agent-workflow next --unit DIR                                              # requests are part of the output
```

| Code | Mode | Raised when |
| --- | --- | --- |
| `REQUEST_UNKNOWN` | `INPUT_ERROR` | `--request` is not an open request of the unit (and not `feedback:*`); the details list the open ids |
| `DECISION_INVALID` | `INPUT_ERROR` | the action or value does not fit the request: a value on `approve`, a missing or ineligible option, several values without `multi`, free text without `allow_other` |
