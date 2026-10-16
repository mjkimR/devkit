# Review Envelopes

**Package**: `devkit.workflow`. The file contract that delegated roles and reviews write, the envelope checks read, and the gates and the integration guard are held by.  
**Related**: [Workflow Definitions and Checks](definition-and-checks.md#primitives), [CLI and Output Contract](cli-and-output.md).

## 1. File Contract

Delegated roles and reviews return a YAML envelope written to `<unit>/envelopes/<kind>-<NN>.yaml`. `kind` matches `[a-z][a-z0-9-]*`; `NN` is a sequence per kind of at least two digits (`01` ... `99`, `100`, ...). The highest sequence is current and earlier files are history. Files are never overwritten; `devkit workflow envelope new` writes the next number under the same directory lock as decision records, and writes the file whole (a hidden temporary file that takes its name without replacing a file, [Answer](human-interaction.md#4-answer)), so an interrupted write leaves no partial envelope. Files named `.<name>.<12 hex digits>.tmp` are such temporary files and are never loaded.

```yaml
kind: review
stage: review
workflow: direct-delivery    # the workflow the unit was bound to when written (envelope new records it)
segment: 0                   # finished segments in the anchor's workflow_history when written
created_at: 2026-10-12T10:00:00.250000Z   # UTC; to the second is also valid
status: completed            # completed | needs_input | failed
summary: "1-3 line judgment"
findings:
  - issue: "What was found"
    evidence: "path:line"
    failure_condition: "Under which input it fails"
    suggested_action: "Recommended next step"
    resolution: open         # open | resolved | waived (default open)
    waiver: "why it is accepted"   # waived findings only
assumptions: ["what the judgment rests on"]        # optional
unverified_areas: ["what was not checked"]        # optional
checks:                      # free-form keys; a value starting with PASS satisfies envelope-check-pass
  tests: "PASS 14/14"
diff_scope: { base: "main", head: "<sha>" }
review: review-01.yaml       # reverify only: the review round it closes
```

- `kind` and `status` are required; `kind` must match the file name and `status` must be `completed`, `needs_input` or `failed`.
- A `reverify` envelope must name the `review-NN.yaml` it closes. The deciding review state is the latest review round, or the last reverify that references it. Envelopes a later `devkit workflow return` re-opened are left out first ([Returns](human-interaction.md)).
- `workflow` (a workflow id) and `segment` (a non-negative integer) scope the envelope to one [workflow segment](overview.md#the-handoff-gate), like decision records: the checks of a workflow count only envelopes whose `workflow` is that workflow and whose `segment` is the number of entries in the anchor's `workflow_history` (`0` before the first handoff). After a handoff the next workflow therefore does not see the previous segment's reviews, and a workflow re-entered later (`a` to `b` to `a`) does not see those of its earlier segment. An envelope without `workflow` counts in every segment; one with `workflow` but no `segment` counts in every segment of that workflow. A `workflow` that is not an id, or a `segment` that is not a non-negative integer, makes the envelope malformed.
- `completed` with no findings is a valid pass. `needs_input` and `failed` never satisfy a check.
- `assumptions` and `unverified_areas` are lists of strings; `checks` is a mapping; `findings` is a list of mappings with only the finding keys shown above. `activity_effort`, on any kind, is `low`, `medium` or `high`: the effort the run applied. The kinds of delegated work carry the fields of [section 1.1](#11-questions-answers-problems-and-resolutions); on any other kind those fields make the envelope malformed. Other top-level keys are ignored.
- Malformed envelopes are reported as `[ENVELOPE_ERROR: file "reason"]` (in JSON, an `ENVELOPE_INVALID` entry of `errors` with its `file`) and are not loaded; evaluation continues.

### 1.1 Questions, Answers, Problems and Resolutions

Four kinds record delegated work that a person or another run picks up. A question waiting for answers and an execution problem are different states: a question is answered, a problem is resolved, and neither is inferred from `needs_input` alone.

```yaml
# envelopes/question-01.yaml: what to ask a person, gathered in one round
kind: question
stage: direction-handoff
status: needs_input          # always needs_input
summary: "Storage format and migration scope"
questions:
  - id: q1                   # [a-z][a-z0-9-]*, unique in the envelope
    title: "Storage format"  # 40 characters at most, like a request title
    prompt: "Which format should settings use?"
    context: "proposal.md section 3, materials/bench.md"   # optional
    options:                 # optional; ids unique, at most one recommended
      - { id: a, description: "Keep TOML", recommended: true }
      - { id: b, description: "Switch to JSON" }
    allow_note: true         # default true; a question without options must allow a note
```

```yaml
# envelopes/answer-01.yaml: the answers, rewritten, written by whoever processes them
kind: answer
status: completed            # always completed
summary: "q1 decided"
answers_to: question-01.yaml # the question envelope it answers
answers:
  - question: q1             # a question of answers_to, one answer per question
    choice: a                # one of its options, or null for an answer outside them
    decision: "Keep TOML and only tidy key names"   # one sentence
    constraints: ["Old keys only warn for one release"]   # optional: constraints the answer adds
```

```yaml
# envelopes/worker-02.yaml: one run that stopped on an execution problem
kind: worker
status: failed               # failed requires problem; needs_input carries it only for an execution problem
summary: "Build stopped"
activity_effort: medium
problem:
  cause: "The integration fixture no longer starts"
  attempts: ["Reinstalled the environment"]   # optional
  recovery: "Repair the fixture, then rerun the build stage"
```

```yaml
# envelopes/resolution-01.yaml: written by whoever actually resolved the problem, with the fix
kind: resolution
status: completed            # always completed
summary: "Fixture repaired in tests/conftest.py; the build stage passes"   # what was done and why it resolves it
resolves: worker-02.yaml     # the envelope whose problem it resolves
```

| Kind | Fields | Rules |
| --- | --- | --- |
| `question` | `questions` (required, non-empty) | Status `needs_input`. Each question is shaped like a `choose` request ([Human Interaction Contract](human-interaction.md#3-request)). |
| `answer` | `answers_to`, `answers` (both required) | Status `completed`. `answers_to` names a well-formed `question-NN.yaml` of the unit; each answer names one of its questions and, unless `choice` is `null`, one of that question's options. |
| `worker` | `problem` (optional; no other kind carries it) | `failed` requires `problem`; `completed` refuses it. A `needs_input` worker envelope without `problem` waits for the questions of a question envelope, which carries them; a worker envelope carries no `questions`. |
| `resolution` | `resolves` (required) | Status `completed` and a non-empty `summary`. `resolves` names a well-formed envelope of the unit that carries a `problem`. |

`problem` (`cause` and `recovery` required, `attempts` a list of strings) is carried only by a `worker` envelope, never with status `completed`: an execution problem is reported by the run that hit it, in one envelope kind. An answer or resolution whose reference names no fitting envelope is malformed: it answers or resolves nothing. References are file names in the same `envelopes/` directory, checked over every envelope of the unit whatever its segment.

## 2. Authoring

`devkit workflow envelope new --unit DIR [--anchor FILE] --kind KIND [--stage ID]` locates the unit's anchor like every unit command (`--anchor` names the anchor when the directory holds several, `ANCHOR_AMBIGUOUS`), records the bound workflow's id (or the configured default's for an unbound unit, `WORKFLOW_NOT_SELECTED` without one) and the current segment in `workflow` and `segment`, and with no other flag writes a `needs_input` skeleton for the author to fill in. It reads only the anchor's binding, never the plugin checks, and the workflow definition only when `[workflow].default` names it by a `.md` path, for its `id` (unvalidated; evaluation scopes envelopes by that id, so the path itself would never count), so a review can be recorded while the definition is invalid, or missing when the unit is bound or the default is an id. `created_at` is the current UTC time to the microsecond, or the end of the latest accepted `return` of the segment when the clock has not passed it, so a `return` followed at once by `envelope new` never voids the new envelope ([Returns](human-interaction.md#5-how-the-engine-applies-answers)). Any further flag switches to authoring, where the file is written complete so that no agent edits YAML by hand:

| Flag | Effect |
| --- | --- |
| `--status` | `completed` (default when authoring), `needs_input` or `failed`. |
| `--summary TEXT` | The judgment. |
| `--assume TEXT`, `--unverified TEXT` | Repeatable; fill `assumptions` and `unverified_areas`. |
| `--check NAME=VERDICT[ detail]` | Repeatable; `VERDICT` is `PASS`, `FAIL` or `SKIP` and may carry a detail such as `PASS 14/14`. |
| `--base REV`, `--head REV` | `diff_scope`; `--head` is what `revision-ancestor` compares and must be a hexadecimal commit id (`--head $(git rev-parse HEAD)`). |
| `--findings-file PATH` (or `-` for stdin) | A YAML list of findings with `issue` and `evidence` (required) and optionally `failure_condition`, `suggested_action`, `resolution` (default `open`) and `waiver`; other keys are refused. A `review` records findings as found, so a resolution other than `open` is refused. |
| `--from latest` (or a review/reverify file) | Carries the findings of the round being closed into a `reverify` and sets its `review`. `latest` is the deciding review state among the envelopes of the current segment. Refused for `review`; required for `reverify`. |
| `--resolve N` (repeatable) or `--resolve all` | Marks carried finding `N` (1-based) resolved; `all` resolves every open one. A number outside the carried findings is `ENVELOPE_FLAG_INVALID`. |
| `--waive N=REASON` (repeatable) | Marks carried finding `N` waived and records the reason as its `waiver`; `suggested_action` is kept. |
| `--questions-file PATH` (or `-`) | `question` only: a YAML list of questions ([section 1.1](#11-questions-answers-problems-and-resolutions)). A malformed list is `ENVELOPE_ITEMS_INVALID`. |
| `--answers-to FILE`, `--answers-file PATH` (or `-`) | `answer` only: the question envelope answered (a file name, or a path whose last part is one) and a YAML list of answers. A malformed list is `ENVELOPE_ITEMS_INVALID`; a reference that does not fit is `ENVELOPE_REFERENCE_INVALID`. |
| `--problem CAUSE`, `--tried TEXT` (repeatable), `--recovery TEXT` | An execution problem; `--tried` and `--recovery` need `--problem`. |
| `--resolves FILE` | `resolution` only: the envelope whose problem it resolves (`ENVELOPE_REFERENCE_INVALID` when it carries none). |
| `--effort low\|medium\|high` | `activity_effort`. |

The status defaults to `needs_input` for a question, `failed` with `--problem`, and `completed` otherwise. Before writing, `envelope new` refuses an envelope its loader would report malformed: fields or a status the kind does not allow (`ENVELOPE_FLAG_INVALID`) or a reference that does not fit. Only one of `--findings-file`, `--questions-file` and `--answers-file` may read stdin. A bare skeleton of these kinds (no authoring flag) lists their fields with placeholders and, like a reverify skeleton, stays malformed until it is filled in.

Findings from `--findings-file` are appended after any carried findings. The written key order is `kind, stage, workflow, segment, created_at, status, review, summary, findings, assumptions, unverified_areas, checks, diff_scope, questions, answers_to, answers, problem, resolves, activity_effort`, omitting empty optional keys. The kind must match `[a-z][a-z0-9-]*` (`ENVELOPE_KIND_INVALID`). The sequence follows the highest `<kind>-NN` file present, malformed files included. The confirmation line is `[ENVELOPE: <file> kind=K seq=NN status=S open_findings=N]`; `--format json` emits `{"file", "kind", "seq", "status", "open_findings"}`.

## 3. Checking

`devkit workflow envelope check --unit DIR` loads every file under `envelopes/`, prints one `[ENVELOPE: file kind seq status open_findings]` line per valid file (ending with `problem=yes` when it carries a problem), the hold of [section 4](#4-hold-blocked-and-waiting-for-answers) as `[BLOCKED: ...]` and `[PENDING_QUESTION: ...]` lines, one `[ENVELOPE_ERROR: file "reason"]` per malformed one, then `[OK: N envelopes]` when nothing is malformed. The hold does not change the exit code. Each malformed file is also reported on stderr as an `ENVELOPE_INVALID` advisory whose `[TARGET]` is the file, and the command exits `1`. `envelope check` lists every envelope whatever its segment; each JSON entry carries `workflow` and `segment` (`null` when absent). `--format json` emits `{"envelopes": [...], "blocked", "problems", "pending_questions", "errors": [...]}` as the only output, each error the `to_dict()` of the advisory (`code`, `message`, `exit_code`, `advisory` with the file as `target_files`, `file`); nothing goes to stderr.

## 4. Hold: Blocked and Waiting for Answers

A unit's envelopes hold it in two cases, read over every envelope of the unit whatever its workflow segment, and not cleared by a `return`:

- **Blocked**: an envelope carries a `problem` that no `resolution` names in `resolves`. Later commits or successful runs do not clear it; only a resolution written by whoever actually fixed it does. Comments or a request to rerun do not.
- **Waiting for answers**: a question of a `question` envelope that no `answer` envelope answers. The answers to one question envelope may be spread over several answer envelopes. Whether an answer was reflected in the documents is the author's responsibility; the engine checks that it was recorded.

While a unit is held:

- **No gate passes.** `devkit workflow next` reports the gate as not satisfied (`held=yes`) whatever would satisfy it (policy `auto`, `--given`, an accepted record), asks no gate request, and a gated stage whose exit checks hold shows the unmet `envelope-hold` check (class `disk`) naming the blocking files and the number of unanswered questions. Stages without a gate, and the runs that resolve a problem or answer questions, go on.
- **Unanswered questions are requests.** Each becomes a `choose` request `question:<question-NN>.<id>` answered by an answer envelope (`answer: envelope`), not by `devkit workflow answer` ([Human Interaction Contract](human-interaction.md#2-request-kinds)), and the unit waits for them (`[WAITING: human ...]`).
- **Integration is refused.** `devkit worktree finish --merge` calls the `devkit.finish_guard` extensions before its first change; devkit-agt registers one (`devkit.workflow.integration:finish_guard`) that reads every unit whose `envelopes/` files the branch changed (between the merge base and the branch tip), at the committed tip, and refuses the merge with `WORKTREE_BLOCKED` listing one line per unresolved problem and unanswered question ([Task Worktrees](../worktree/overview.md)). Uncommitted envelopes neither block nor clear it. Other integrators (a pull request service) apply the same rule by reading the envelopes at the head they merge: `envelope check --format json` reports `blocked`, `problems` and `pending_questions`.
