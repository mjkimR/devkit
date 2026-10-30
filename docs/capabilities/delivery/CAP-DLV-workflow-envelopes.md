---
id: CAP-DLV-workflow-envelopes
title: "Workflow Envelopes"
summary: "Workflow envelopes retain immutable stage evidence and review rounds. Authoring stays write-only; an explicit command commits one authored new record with deterministic identity, ordinary hooks, bounded Git checks and same-file recovery."
area: delivery
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py
  - packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py
  - packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py
created_at: 2026-10-17
usecases:
  - UC-drive-development-to-integration
  - UC-handle-delivery-problems-and-exceptions
---

# [CAP-DLV-workflow-envelopes] Review Envelopes

**Package**: `devkit_agt.features.workflow`. The file contract that delegated roles and reviews write, the envelope checks read, and the gates and the integration guard are held by.
**Related**: `CAP-DLV-workflow-definitions`, `CAP-DLV-cli-and-output`.

## 1. File Contract

Delegated roles and reviews return a YAML envelope written to `<unit>/envelopes/<kind>-<NN>.yaml`. `kind` matches `[a-z][a-z0-9-]*`; `NN` is a sequence per kind of at least two digits (`01` ... `99`, `100`, ...). The highest sequence is current and earlier files are history. Files are never overwritten; the authoring commands ([Authoring](#2-authoring)) write the next number under the same directory lock as decision records, and writes the file whole (a hidden temporary file that takes its name without replacing a file, `CAP-DLV-human-interaction`), so an interrupted write leaves no partial envelope. Files named `.<name>.<12 hex digits>.tmp` are such temporary files and are never loaded.

Envelope and workflow-decision YAML syntax is parsed through the shared `devkit_core.core.yaml` LibYAML safe boundary. The owning envelope or decision format continues to validate its own schema, fields and empty-document behavior. If the PyYAML C binding is unavailable, the read fails with `YAML_BINDING_UNAVAILABLE` and exit `2` before format validation; malformed YAML continues through the owning format's existing malformed-input behavior.

```yaml
kind: review
stage: review
workflow: direct-delivery    # the workflow the unit was bound to when written (the authoring commands record it)
segment: 0                   # finished segments in the anchor's workflow_history when written
created_at: 2026-10-12T10:00:00.250000Z   # UTC; to the second is also valid
status: completed            # completed | needs_input | failed
summary: "1-3 line judgment"
findings:
  - issue: "What was found"
    evidence: "path:line"
    failure_condition: "Under which input it fails"
    suggested_action: "Recommended next step"
    severity: "P2"           # optional non-empty string; descriptive metadata
    resolution: open         # open | resolved | waived (default open)
    waiver: "why it is accepted"   # waived findings only
assumptions: ["what the judgment rests on"]        # optional
unverified_areas: ["what was not checked"]        # optional
checks:                      # free-form keys; a value starting with PASS satisfies envelope-check-pass
  tests: "PASS 14/14"
diff_scope: { base: "<base-sha>", head: "<head-sha>" }
review: review-01.yaml       # reverify only: the review-NN.yaml or challenger-NN.yaml round it closes
```

- `kind` and `status` are required; `kind` must match the file name and `status` must be `completed`, `needs_input` or `failed`.
- A `reverify` envelope must name the `review-NN.yaml` or `challenger-NN.yaml` round it closes; any other value makes it malformed (`ADR-review-and-reconcile-verification`). The deciding state of `review` and of `challenger` is the latest round of that kind, or the last reverify that references it, so a reverify of a challenger round never counts for the review state; every other kind is decided by its latest envelope. Envelopes a later `devkit workflow return` re-opened are left out first (`CAP-DLV-human-interaction`).
- `workflow` (a workflow id) and `segment` (a non-negative integer) scope the envelope to one `CAP-DLV-workflow-orchestration`, like decision records: the checks of a workflow count only envelopes whose `workflow` is that workflow and whose `segment` is the number of entries in the anchor's `workflow_history` (`0` before the first handoff). After a handoff the next workflow therefore does not see the previous segment's reviews, and a workflow re-entered later (`a` to `b` to `a`) does not see those of its earlier segment. An envelope without `workflow` counts in every segment; one with `workflow` but no `segment` counts in every segment of that workflow. A `workflow` that is not an id, or a `segment` that is not a non-negative integer, makes the envelope malformed.
- `completed` with no findings is a valid pass. `needs_input` and `failed` never satisfy a check.
- `assumptions` and `unverified_areas` are lists of strings; `checks` is a mapping; `findings` is a list of mappings with only the finding keys shown above. `activity_effort`, on any kind, is `low`, `medium` or `high`: the effort the run applied. The kinds of delegated work carry the fields of [section 1.1](#11-questions-answers-problems-and-resolutions); on any other kind those fields make the envelope malformed. Other top-level keys are ignored.
- Finding `severity`, when supplied, is a non-empty string label. Empty, whitespace-only and non-string values are malformed. It is preserved in loading, serialization and reverify carry-forward; omission stays omitted. It has no effect on open-finding counts, check satisfaction or exit codes. The engine validates nothing beyond that: the `spec` bundle's review procedures require `P1`, `P2` or `P3` on every finding of a `review`, `reconcile-check` or `challenger` envelope and define the levels (`CAP-DLV-delivery-workflows` rule 15).
- Malformed envelopes are not loaded; evaluation continues. Each is reported once: by `devkit workflow next` as an `[ENVELOPE_ERROR: file "reason"]` line, by `envelope check` as an `ENVELOPE_INVALID` advisory on stderr ([section 3](#3-checking)), and in JSON as an `ENVELOPE_INVALID` entry of `errors` with its unit-relative `file`. Its `[TARGET]` is the workspace-relative file and its `[FIX]` names the `envelope check --unit DIR` to rerun once it is fixed.

### 1.1 Questions, Answers, Problems and Resolutions

A run of delegated work leaves one `worker` envelope: what it did, the questions it puts to a person (`questions`) and an execution problem it stopped on (`problem`). What another actor does later is a separate envelope that references that run: an `answer` records the rewritten answers to its questions and the assumptions of the run the user settled, a `resolution` closes its problem. A question waiting for answers and an execution problem are different states: a question is answered, a problem is resolved, and neither is inferred from `needs_input` alone.

User direction that neither answers a recorded question nor settles a recorded worker assumption is incorporated
into the proposal/PADR (or spec/plan) and summarized in the subsequent worker record. It requires no fabricated
question or new envelope kind. Existing pending questions and settles-only answers retain their normal procedure.

```yaml
# envelopes/worker-01.yaml: one run that stopped to ask, gathering its questions in one round
kind: worker
stage: direction-handoff
status: needs_input          # a worker envelope with questions has status needs_input
summary: "Storage format and migration scope need a decision"
activity_effort: medium
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
answers_to: worker-01.yaml   # the run whose questions it answers
answers:
  - question: q1             # a question of answers_to, one answer per question
    choice: a                # one of its options, or null for an answer outside them
    decision: "Keep TOML and only tidy key names"   # one sentence
    constraints: ["Old keys only warn for one release"]   # optional: constraints the answer adds
settles:                     # optional: assumptions of answers_to the user settled
  - assumption: 2            # 1-based position in the assumptions of answers_to, each at most once
    decision: "Keep the TOML layout"   # one sentence
```

```yaml
# envelopes/worker-02.yaml: one run that stopped on an execution problem
kind: worker
stage: build
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
resolves: worker-02.yaml     # the run whose problem it resolves
```

| Kind | Fields | Rules |
| --- | --- | --- |
| `worker` | `questions`, `problem` (both optional; no other kind carries them) | One per run, naming the `stage` `devkit workflow next` names when it is written, after the run's other records (a worker envelope without one is malformed; `envelope worker` requires `--stage`). `needs_input` asks questions or reports a problem (an empty one is malformed). With `questions` the status is `needs_input`; each question is shaped like a `choose` request (`CAP-DLV-human-interaction`). `failed` requires `problem`; `completed` refuses it. A run that both asks and hit a problem records both, with status `needs_input`. |
| `answer` | `answers_to` (required), `answers`, `settles` (at least one of the two) | Status `completed`. `answers_to` names a well-formed `worker-NN.yaml` of the unit, with questions when `answers` is not empty; each answer names one of them and, unless `choice` is `null`, one of that question's options. Each `settles` item names a position of that envelope's `assumptions` (`ADR-orchestration-workers`); settles hold and release nothing. |
| `resolution` | `resolves` (required) | Status `completed` and a non-empty `summary`. `resolves` names a well-formed `worker-NN.yaml` of the unit that carries a `problem`. |

`problem` has `cause` and `recovery` (required) and `attempts` (a list of strings). A `settles` item has exactly `assumption` (an integer from `1`) and `decision` (a non-empty string); a repeated position, another key or a position beyond the referenced envelope's `assumptions` makes the answer malformed, so its answers stop counting. An answer's `choice: null` answers outside the options; it is also how whoever ends a Planning (a rejection, a return for decomposition) closes the questions still open, with the reason as the decision. A question's `allow_note` is a hint for the person's input, not a restriction on answers. An answer or resolution whose reference names no fitting envelope is malformed: it answers or resolves nothing. References are file names in the same `envelopes/` directory, checked over every envelope of the unit whatever its segment.

## 2. Authoring

Five kinds have a command of their own that takes the options of their fields: `devkit workflow envelope worker`, `answer`, `resolution`, `review` and `reverify`. Every other kind is written with `devkit workflow envelope new --kind KIND`, which refuses those five with `ENVELOPE_FLAG_INVALID` and a `[FIX]` naming the command. Each command takes `--unit DIR [--anchor FILE] [--stage ID]` (`envelope worker` requires `--stage`), locates the unit's anchor like every unit command (`--anchor` names the anchor when the directory holds several, `ANCHOR_AMBIGUOUS`), records the bound workflow's id (or the configured default's for an unbound unit, `WORKFLOW_NOT_SELECTED` without one) and the current segment in `workflow` and `segment`, and with no other flag writes a `needs_input` skeleton for the author to fill in. `envelope worker` also loads the bound definition to check `--stage`, because an envelope with a stage its workflow does not declare holds every gate: a stage the definition does not declare (`-` included) is refused before anything is written, the bare skeleton included, with `ENVELOPE_FLAG_INVALID`, `[TARGET] --stage` and a `[FIX]` naming the `uv run devkit workflow next --unit DIR` command, the declared stage the run worked in when that command names none (`complete=yes`), and the declared stages; when the definition cannot be loaded, or its id is not the workflow the envelope records, the stage is not checked, so a run can still be recorded on a missing or broken definition. Apart from that check, each command reads only the anchor's binding, and the workflow definition only when `[workflow].default` names it by a `.md` path, for its `id` (unvalidated; evaluation scopes envelopes by that id, so the path itself would never count), so a review can be recorded while the definition is invalid, or missing when the unit is bound or the default is an id. `created_at` is the current UTC time to the microsecond, or the end of the latest accepted `return` of the segment when the clock has not passed it, so a `return` followed at once by an authoring command never voids the new envelope (`CAP-DLV-human-interaction`). Any further flag switches to authoring, where the file is written complete so that no agent edits YAML by hand. The flags of the table's first part are common to every command, except that `envelope answer` and `envelope resolution` take no `--status`, `--check`, `--base` or `--head`: an answer or a resolution records a decision or a fix, is always `completed` and carries no verification of its own. The rest belong to the commands named:

| Flag | Effect |
| --- | --- |
| `--status` | `completed` (default when authoring), `needs_input` or `failed`. |
| `--summary TEXT` | The judgment. |
| `--assume TEXT`, `--unverified TEXT` | Repeatable; fill `assumptions` and `unverified_areas`. |
| `--check NAME=VERDICT[ detail]` | Repeatable; `VERDICT` is `PASS`, `FAIL` or `SKIP` and may carry a detail such as `PASS 14/14`. |
| `--base REV`, `--head REV` | `diff_scope`; `--head` is what `revision-ancestor` compares and must be a hexadecimal commit id (`--head $(git rev-parse HEAD)`). In Git workspaces each supplied revision must resolve to a commit and is stored as its full commit ID. Unknown and non-commit revisions are refused with `ENVELOPE_FLAG_INVALID` (exit `2`) before writing an envelope. |
| `--effort low\|medium\|high` | `activity_effort`. |
| `--findings-file PATH` (or `-` for stdin) | `new`, `worker`, `review` and `reverify`: a YAML list of findings with `issue` and `evidence` (required) and optionally `failure_condition`, `suggested_action`, `severity` (a non-empty string label), `resolution` (default `open`) and `waiver`; other keys are refused. A `review` or `challenger` records findings as found, so a resolution other than `open` is refused (`ENVELOPE_FLAG_INVALID`); its round is closed by a `reverify`. |
| `--from latest` (or a review, challenger or reverify file) | `reverify` only, and required by its contract: carries the findings of the round being closed and sets its `review`. `latest` is the deciding review state among the envelopes of the current segment that count, read as evaluation does: a round a later `devkit workflow return` re-opened is left out (`CAP-DLV-human-interaction`; when the bound definition cannot be loaded, nothing is left out); without a review round it is `ENVELOPE_FROM_INVALID`, with one `[DETAIL]` line `--from envelopes/<file>` per review, challenger and reverify file of the segment (so a challenger round is named exactly). A `review-NN.yaml` or `challenger-NN.yaml` closes that round and carries its closing state: the findings of the last reverify among the current segment's envelopes whose `review` names the file, or the file's own findings when none does, so earlier resolutions and waivers persist. A `reverify-NN.yaml` carries its own findings and `review`. A file of any other kind, or one that cannot be read, is `ENVELOPE_FROM_INVALID` with the same `[DETAIL]` lines, and for a `reconcile-check` file its `[FIX]` names the reconcile route: a new `reconcile-check` envelope (`envelope new --unit DIR --kind reconcile-check --stage <its stage>`) or another reconcile-reviewer call. Every refusal of `--from` has `[TARGET] --from`. |
| `--resolve N` (repeatable) or `--resolve all` | `reverify` only: marks carried finding `N` (1-based) resolved; `all` resolves every open one. A number outside the carried findings is `ENVELOPE_FLAG_INVALID` (`[TARGET] --resolve` or `--waive`) with one `[DETAIL]` line `N: <resolution> "<issue>"` per carried finding, so the valid numbers are in the refusal itself. |
| `--waive N=REASON` (repeatable) | `reverify` only: marks carried finding `N` waived and records the reason as its `waiver`; `suggested_action` is kept. |
| `--questions-file PATH` (or `-`) | `worker`: a YAML list of the questions the run asks ([section 1.1](#11-questions-answers-problems-and-resolutions)). A malformed list is `ENVELOPE_ITEMS_INVALID`. |
| `--answers-to FILE`, `--answers-file PATH` (or `-`) | `answer`: the worker envelope whose questions are answered (a file name, or a path whose last part is one) and a YAML list of answers. A malformed list is `ENVELOPE_ITEMS_INVALID`; a reference that does not fit is `ENVELOPE_REFERENCE_INVALID` with `[TARGET] --answers-to` and one `[DETAIL]` line `--answers-to <file>` per worker envelope that fits. |
| `--settle N=DECISION` (repeatable) | `answer`: a `settles` item for assumption `N` (1-based) of the `--answers-to` envelope; with it `--answers-file` may be omitted. A value that is not `N=DECISION` with `N` from `1`, or a repeated `N`, is `ENVELOPE_FLAG_INVALID`; a position beyond that envelope's assumptions is `ENVELOPE_REFERENCE_INVALID` (`[TARGET] --settle`). |
| `--problem CAUSE`, `--tried TEXT` (repeatable), `--recovery TEXT` | `worker`: an execution problem; `--tried` and `--recovery` need `--problem`. |
| `--resolves FILE` | `resolution`: the worker envelope whose problem it resolves (`ENVELOPE_REFERENCE_INVALID` when it carries none, with `[TARGET] --resolves` and one `[DETAIL]` line `--resolves <file>` per worker envelope with a problem). |

The status defaults to `needs_input` with `--questions-file`, `failed` with only `--problem`, and `completed` otherwise. Before writing, every authoring command refuses an envelope its loader would report malformed: fields or a status the kind does not allow (`ENVELOPE_FLAG_INVALID`) or a reference that does not fit. Only one of `--findings-file`, `--questions-file` and `--answers-file` may read stdin, and an empty stdin is refused (`ENVELOPE_FLAG_INVALID`, `[TARGET]` the flag) before anything is written, so a failed pipe never records an empty review. Every authoring refusal is an `INPUT_ERROR` whose `[TARGET]` is the flag to correct. A bare skeleton of these kinds (no authoring flag) lists their fields with placeholders and, like a reverify skeleton, stays malformed until it is filled in.

Revision resolution applies to CLI authoring commands, including kind-specific commands. Outside Git, authoring retains supplied scope values and the hexadecimal head syntax check. Pure library composition and historical loading remain independent of repository history; they do not resolve revisions.

Findings from `--findings-file` are appended after any carried findings. The written key order is `kind, stage, workflow, segment, created_at, status, review, summary, findings, assumptions, unverified_areas, checks, diff_scope, questions, answers_to, answers, settles, problem, resolves, activity_effort`, omitting empty optional keys. The kind must match `[a-z][a-z0-9-]*` (`ENVELOPE_KIND_INVALID`). The sequence follows the highest `<kind>-NN` file present, malformed files included. The confirmation line is `[ENVELOPE: <file> kind=K seq=NN status=S open_findings=N]`, where `<file>` is relative to the unit directory (`envelopes/review-01.yaml`), as in `envelope check` and `next`. A bare skeleton ends with `skeleton=yes` instead of `open_findings`; a `worker`, `answer` or `resolution` line carries `open_findings` only when it is not `0`. `--format json` emits `{"unit", "file", "kind", "seq", "status", "skeleton", "open_findings"}`, with `unit` the workspace-relative unit directory and `file` unit-relative.

## 3. Checking

`devkit workflow envelope check --unit DIR` loads every file under `envelopes/` and prints, in text:

| Line | When |
| --- | --- |
| `[ENVELOPE: <file> kind=K seq=NN status=S open_findings=N problem=yes review=<file>]` | One per valid file, `<file>` unit-relative. `open_findings` is left out of a `worker`, `answer` or `resolution` line when it is `0`; `problem=yes` only when the file carries a problem; `review=` only on a reverify, naming the round it closes. |
| `[BLOCKED: ...]`, `[PENDING_QUESTION: ...]` | The hold of [section 4](#4-hold-blocked-and-waiting-for-answers), in the formats of `CAP-DLV-cli-and-output`. |
| `[OK: N envelopes]` | Last, when nothing is malformed. |

The hold does not change the exit code. Each malformed file is reported once, on stderr, as an `ENVELOPE_INVALID` advisory whose `[TARGET]` is the workspace-relative file and whose `[FIX]` reruns this check; stdout carries no line for it, and the command exits `1`. `envelope check` lists every envelope whatever its segment; each default JSON entry carries only `file`, `seq`, `kind`, `status`, `stage`, `workflow`, `segment`, `review` and `open_findings`, plus open `findings` for the deciding envelope of each kind (review and challenger rounds use their latest closing reverify). Historical bodies, closed findings, checks, answers and assumptions are omitted. `--details --format json` restores complete envelope bodies, including `settles`. Every file is validated in both modes; the hold, errors and exit code are unchanged. `--format json` emits `{"envelopes": [...], "blocked", "problems", "pending_questions", "malformed_workers", "errors": [...]}` as the only output (`problems` is `[{"file", "cause", "attempts", "recovery"}]`, `pending_questions` `[{"file", "id", "title"}]`, `malformed_workers` `[{"file", "reason"}]`), each error the `to_dict()` of the advisory (`code`, `message`, `exit_code`, `advisory` with the workspace-relative file as `target_files`, and the unit-relative `file`); nothing goes to stderr.

## 4. Hold: Blocked and Waiting for Answers

A unit's envelopes hold it in three cases, read over every envelope of the unit whatever its workflow segment, and not cleared by a `return`:

- **Blocked**: an envelope carries a `problem` that no `resolution` names in `resolves`. Later commits or successful runs do not clear it; only a resolution written by whoever actually fixed it does. Comments or a request to rerun do not.
- **Waiting for answers**: a question of a `worker` envelope that no `answer` envelope answers. The answers to one run's questions may be spread over several answer envelopes. Whether an answer was reflected in the documents is the author's responsibility; the engine checks that it was recorded.
- **Malformed worker envelope**: a `worker-NN.yaml` that does not satisfy the contract. Whether it reports a problem or questions cannot be known, so it holds as a problem does (fail closed) until it is fixed, from the stage (and workflow) its YAML still states, else every gate: `[BLOCKED: <file> malformed=yes ...]`, counted in `blocked` and listed under `malformed_workers`.

While a unit is held:

- **No gate from the hold on passes.** The hold applies to the gate of the stage the holding worker envelope was written in (its `stage`) and of every later stage; gates passed before stay passed, so a run that resolves the problem goes on from where the unit is. A malformed worker envelope holds from the stage it still states. An envelope of another workflow or without a stage of this one holds every gate. `devkit workflow next` reports a held gate as not satisfied (`held=yes`) whatever would satisfy it (policy `auto`, `--given`, an accepted record), asks no gate request, and a gated stage whose exit checks hold shows the unmet `envelope-hold` check (class `disk`) naming the blocking files and the number of unanswered questions. Stages without a gate, and the runs that resolve a problem or answer questions, go on. A stage skipped by policy `off` is skipped as before.
- **No handoff.** A complete unit asks no handoff choice, and `devkit workflow handoff` refuses with `HANDOFF_HELD`.
- **Unanswered questions are requests.** Each becomes a `choose` request `question:<worker-NN>.<id>` answered by an answer envelope (`answer: envelope`), not by `devkit workflow answer` (`CAP-DLV-human-interaction`), and the unit waits for them (`[WAITING: human ...]`).
- **Integration is refused.** `devkit worktree finish --merge` calls the `devkit.finish_guard` extensions before its first change; devkit-agt registers one (`devkit_agt.features.workflow.usecases.integration:finish_guard`) that reads every unit whose `envelopes/` files the branch changed (between the merge base and the branch tip), at the committed tip, and refuses the merge with `WORKTREE_BLOCKED` listing one line per unresolved problem, unanswered question and malformed worker envelope (`CAP-WT-task-worktrees`). Uncommitted envelopes neither block nor clear it. Envelope files are never removed one by one, so a file the branch deleted from a unit it kept still counts, read at the merge base; a unit the branch removed whole (a handoff, a close) holds nothing. A Git failure while reading propagates, and the merge is refused (`WORKTREE_GUARD_FAILED`). Other integrators (a pull request service) apply the same rule by reading the envelopes at the head they merge: `envelope check --format json` reports `blocked`, `problems` and `pending_questions`.


## 5. Explicit Single-Envelope Commit

`devkit workflow envelope commit --unit DIR --file envelopes/NAME.yaml` commits one existing new authored envelope. `ADR-explicit-envelope-commits` records the decision. `CAP-DLV-cli-and-output` owns output fields and error codes. Tests: `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py` and `packages/devkit/tests/unit/features/workflow/test_envelope_commit_policy.py`.

1. **Opt-in boundary**: WHEN explicit commit is invoked, the operation MUST avoid rewriting authored envelope bytes, sequence and `diff_scope`. Authoring and its library operation remain write-only, including outside Git; `next`, `check` and `show` remain read-only.
2. **Tracked identity**: WHERE explicit commit is used, the Unit MUST have a tracked regular bound anchor inside the current Git worktree and an existing HEAD. Its tracked ID is `SPEC-<slug>` or `PROP-<slug>`, with slug matching `[a-z0-9][a-z0-9-]*`. The command derives `chore(workflow): record <slug> <kind>-<NN>` from that anchor and the selected record, with workflow, segment and stage in the body; branch names do not determine the message.
3. **Authored file**: IF the literal Unit-relative file is not an immediate valid envelope under its real `envelopes/` directory, is ignored, crosses a symlink or escapes the worktree, THEN the command MUST refuse before mutation. A valid record has a nonempty summary, a declared stage and exactly the bound workflow/current segment. Authored `completed`, `failed` and `needs_input` records are eligible; committing a record does not make it pass a gate.
4. **Index and dirty scope**: IF another Git-visible staged, unstaged or untracked path is dirty, or the selected path is modified tracked history or partially staged, THEN the command MUST refuse before staging. A new selected file may already be staged only when index bytes equal worktree bytes. One active writer per worktree is required; no global lock service is provided.
5. **Supported Git state**: IF Git is unavailable, HEAD is unborn/detached, an operation is in progress, the index is locked/unmerged, or `GIT_INDEX_FILE` is supplied, THEN the command MUST refuse before mutation. The operation rechecks repository identity, HEAD including its symbolic branch, selected bytes and scope before mutation.
6. **Ordinary commit**: WHEN an eligible new record is committed, Git MUST stage only its literal path and run ordinary commit hooks, identity and configured signing without bypass flags. A successful result requires one commit parented by captured HEAD, exactly that added path with expected blob, the same symbolic branch and clean index/worktree. Metadata-rewriting hooks are eligible; the reported SHA is final HEAD observed after hooks.
7. **Failure recovery**: WHEN Git/hook/signing rejects and unchanged HEAD/reference plus retained record/index can be established, the operation MUST report `ENVELOPE_COMMIT_FAILED` with staging state, before/after HEAD, exact retained path and a retry command for the same file. Retry allocates no envelope. Unknown completion, unexpected content/reference effects or failed postconditions report `ENVELOPE_COMMIT_UNCERTAIN` and require HEAD/index/worktree inspection before further mutation. Neither outcome resets, amends, deletes or automatically retries observed resources.
8. **Idempotent repeat**: WHEN selected bytes already exist unchanged in HEAD and the checkout is clean, the command MUST return `already_committed` without making a commit and with null subject. It makes no claim about the existing commit message.

This operation adds no gate, approval, push or merge authority. Combined source/document changes, multiple records, decision/acceptance transactions and emergency commits retain their manual commit procedures (`CAP-DLV-delivery-workflows`). Integration preparation follows the final record commit because its source HEAD changes.
