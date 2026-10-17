# Workflow CLI and Output Contract

**Package**: `devkit.workflow` (`devkit workflow` CLI). Envelope commands: [Review Envelopes](envelopes.md); requests and decision records: [Human Interaction Contract](human-interaction.md).  
**Related**: [Workflow Engine Overview](overview.md), [Agent-First Output](../architecture/ARCH-08-1-agent-output.md).

## 1. Commands

```bash
devkit workflow new <slug> [--workflow ID] [--date YYYY-MM-DD] [--status S]   # create a unit from the layout template and bind it
devkit workflow bind --unit DIR [--anchor FILE] [--workflow ID]  # record or change the workflow binding
devkit workflow next --unit DIR [--anchor FILE] [--workflow ID] [--given NAME]... [--no-lint] [--format text|json]
devkit workflow handoff --unit DIR [--anchor FILE] [--workflow ID] [--date YYYY-MM-DD] [--by NAME] [--no-lint] [--format text|json]
devkit workflow requests --unit DIR [--anchor FILE] [--no-lint] [--format text|json]   # open human requests of a unit
devkit workflow answer --unit DIR [--anchor FILE] --request ID --action accept|decline|cancel [--value V] [--note TEXT] [--by NAME] [--no-lint] [--format text|json]
devkit workflow return --unit DIR [--anchor FILE] --to STAGE [--note TEXT] [--by NAME] [--no-lint] [--format text|json]  # go back; later approvals are asked again
devkit workflow show <ID|PATH> [--format text|json]              # a definition's stages and next candidates
devkit workflow show --unit DIR [--anchor FILE] [--format text|json]  # the unit's bound definition plus [BINDING: workflow=...]
devkit workflow checks [--format text|json]                      # registered check names, classes and parameters (plugins included)
devkit workflow validate [PATH]... [--format text|json]          # validate definitions (default: both sources, plus roles and shared stages)
devkit workflow list [--status S]... [--exclude-status S]... [--format text|json]  # discovered units across every layout
# COMMON: --unit DIR [--anchor FILE] [--stage ID] [--status S] [--summary TEXT] [--assume TEXT]... [--unverified TEXT]...
#         [--check NAME=PASS|FAIL|SKIP[ detail]]... [--base REV] [--head REV] [--effort low|medium|high] [--format text|json]
# With only --unit (and --stage) each writes the next envelopes/<kind>-NN.yaml skeleton; any other flag writes it complete.
devkit workflow envelope new --kind KIND COMMON [--findings-file PATH|-]      # any kind but the five below
devkit workflow envelope worker --stage ID COMMON [--questions-file PATH|-] [--problem CAUSE [--tried TEXT]... --recovery TEXT]
                                [--findings-file PATH|-]
devkit workflow envelope answer COMMON [--answers-to FILE --answers-file PATH|-]
devkit workflow envelope resolution COMMON [--resolves FILE]
devkit workflow envelope review COMMON [--findings-file PATH|-]
devkit workflow envelope reverify COMMON [--from latest|FILE] [--resolve N|all]... [--waive N=REASON]... [--findings-file PATH|-]
devkit workflow envelope check --unit DIR [--format text|json]   # every envelope file, contract violations and the hold
```

`--anchor FILE` names the anchor file that identifies the unit when its directory holds several candidate anchors (`ANCHOR_AMBIGUOUS`); see [Per-Definition Layout](overview.md#per-definition-layout).

All commands accept `-w/--workspace-root`. It defaults to the devkit root of the current directory (the Git work tree's top level; outside Git, the nearest directory with a `.devkit/` folder); an explicit value that is not an existing directory, or one below the top level of a Git work tree, is `ARGUMENT_INVALID`; a `.devkit/` below the top level of a work tree whose top level has none is `DEVKIT_ROOT_NESTED`.

## 2. Exit Codes and Errors

Exit codes follow the devkit convention ([Errors, Exit Codes and Platforms](../architecture/ARCH-08-cross-cutting.md#4-exit-code-conventions)):

| Exit | When |
| --- | --- |
| `0` | The command did its job. `next` exits `0` whatever the stage, including a unit that waits for a person (`[WAITING]`, `[REQUEST]`, a recorded decline), a delegation (`[DELEGATE]`) or a handoff choice. |
| `1` | The command ran and reports a negative result: `validate` found invalid definitions or shared-stage differences (a definition file that cannot be loaded at all makes it exit `2`), `show` found problems in the definition, `envelope check` found malformed envelope files (`ENVELOPE_INVALID`). |
| `2` | The command could not do its job: a usage error from the command line parser, an argument error (`ARGUMENT_INVALID`: a `-w` or `validate` path that does not exist, a malformed `--date`, `show` given both or neither of `REF` and `--unit`, or `--anchor` without `--unit`), and every other error code below (unreadable configuration, receipt, definition or anchor, a refused input, a lint run that could not execute, an unexpected error). |

A command that collects several problems (`validate`, `envelope check`) exits with the highest exit code among them. `show` only reports, so it exits `1` when its report lists any problem, whatever the problem's own code, and `2` only when it cannot run (an unknown workflow, an unreadable definition or configuration).

In text mode errors are reported on stderr as Agent Advisory Protocol blocks from `devkit.advisory`, with a stable code and an `[ACTION]` directive, so an agent knows whether to fix input, stop for a person, or respect a guardrail. Under `--format json` stdout carries exactly one JSON object, never a bare array: the command's result, or `{"error": {...}}` when it has none. Problems a command collects rather than raises are listed in its result under `errors`, each the `to_dict()` of an advisory error (`code`, `level`, `message`, `exit_code`, `advisory`, plus `file` or `where` when the problem has one); warnings and notices are listed under `notices`. The JSON object carries every advisory, so nothing is rendered on stderr in JSON mode; in text mode warnings and notices follow the result as `[WARN]` or `[NOTICE]` blocks. A text-mode `next` or `requests` whose lint run failed prints its result and then reports the `devkit.rules` error on stderr (in JSON it is among the result's `errors`); `envelope check` reports each `ENVELOPE_INVALID` file the same way.

The library raises the same codes, one class per code. `WorkflowError` is the base: it sets the actor and retry once, and each subclass adds its code and mode. Errors of `devkit.core` (`CONFIG_INVALID`, `RECEIPT_INVALID`, `GIT_FAILED`, ...) and of `devkit.rules` (from `lint-clean`) pass through unchanged.

| Code | Class | Mode | Exit | Raised when |
| --- | --- | --- | --- | --- |
| `CONFIG_INVALID` | `devkit.core` `ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` cannot be read or parsed (passed through unchanged) |
| `WORKFLOW_CONFIG_INVALID` | `WorkflowConfigError` | `INPUT_ERROR` | `2` | the `[workflow]`, `[workflow.approvals]` or `[workflow.stages]` table is malformed (a subclass of the `devkit.core` `ConfigError`) |
| `WORKFLOW_GATE_POLICY` | `GatePolicyError` | `INPUT_ERROR` | `2` | `[workflow.approvals]` sets a gate to a policy its definition does not accept (`gates.<gate>.policies`); refused before evaluation by `next`, `requests`, `answer`, `return` and `handoff` |
| `ARGUMENT_INVALID` | `devkit.core` `ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` or a `validate` path does not exist, `--date` is not `YYYY-MM-DD`, or `show` is given both or neither of `REF` and `--unit` |
| `WORKFLOW_NOT_SELECTED`, `WORKFLOW_NOT_FOUND`, `WORKFLOW_INVALID` | `WorkflowNotSelectedError`, `WorkflowNotFoundError`, `WorkflowInvalidError` | `INPUT_ERROR` | `2` | no definition chosen (`new` without `--workflow` or `[workflow].default`; for a unit command, an unbound unit without a default, whose fix is `bind --unit <dir> --workflow <id>`), no id or file matches, or the chosen one fails validation (problems become `[DETAIL]` lines) |
| `WORKFLOW_NOT_BINDABLE` | `WorkflowNotBindableError` | `INPUT_ERROR` | `2` | `new` or `bind` was given `--workflow <path>` naming a file that is not the discovered definition of its id (outside `definitions_dir` and the receipt, or shadowed by another file with the same id); a binding records only the id, so later commands could not find the file |
| `WORKFLOW_DEFINITION_INVALID` | `DefinitionError` | `INPUT_ERROR` | `2` | a definition file cannot be read or parsed (`parse_definition`, `load_definition`), or an id is defined twice; `validate` collects it as a load error |
| `WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_CHECK_INVALID`, `ROLE_UNKNOWN` | `DefinitionProblem`, `CheckReferenceProblem`, `RoleUnknownProblem` | `INPUT_ERROR` | `1` | collected by validation with `where` (`<stage>.<field>`): a problem in a loaded definition, a check reference that does not resolve, a role outside the vocabulary |
| `SHARED_STAGE_MISMATCH` | `SharedStageMismatchError` | `INPUT_ERROR` | `1` | collected by a whole-workspace `validate`: stages that share an id but differ |
| `WORKFLOW_ASSET_MISSING` | `WorkflowAssetMissingError` | `AUTO` | `2` | collected by discovery: a receipt-listed definition is missing from disk; `[FIX]` is `devkit sync` |
| `WORKFLOW_CHECK_INVALID` | `CheckError` | `INPUT_ERROR` | `2` | a check reference is malformed, unregistered, a duplicate or colliding declaration, or a `runner`/`human` check in `next[].when` (`parse_check`, `Registry`, `validate`) |
| `LAYOUT_INVALID`, `SLUG_INVALID` | `LayoutError`, `SlugError` | `INPUT_ERROR` | `2` | a layout template, directory or anchor file name is malformed (`validate_template`, `parse_layout_spec`; inside `[workflow]` it is `WORKFLOW_CONFIG_INVALID`); a unit slug does not match `[a-z0-9][a-z0-9-]*` |
| `UNIT_NOT_FOUND`, `UNIT_EXISTS`, `ANCHOR_INVALID` | `UnitNotFoundError`, `UnitExistsError`, `AnchorInvalidError` | `INPUT_ERROR` | `2` | the unit directory has no anchor, already exists (also when a concurrent `new` created the anchor first: `new` creates it exclusively), or its frontmatter is unreadable (`list` reports the last one per unit under `error`) |
| `UNIT_DIR_NOT_EMPTY` | `UnitDirNotEmptyError` | `INPUT_ERROR` | `2` | `new` found the unit directory without an anchor but holding leftover records (`decisions/*.yaml`, `envelopes/*.yaml` or `*.yml`, listed as details and targets), which would count in the new unit (fix: another slug, or move the records out); other files such as `.gitkeep` or notes are left in place and do not refuse it |
| `ANCHOR_AMBIGUOUS`, `ANCHOR_MISMATCH` | `AnchorAmbiguousError`, `AnchorMismatchError` | `INPUT_ERROR` | `2` | several candidate anchor files exist in the unit (pass `--anchor FILE`); the selected workflow declares a different anchor than the file that identifies the unit, or than `--anchor` names |
| `GIVEN_INVALID` | `GivenInvalidError` | `INPUT_ERROR` | `2` | a `--given` name is neither a gate nor a registered runner or human check |
| `REQUEST_UNKNOWN` | `RequestUnknownError` | `INPUT_ERROR` | `2` | `answer --request` is not an open request of the unit (and not `feedback:*`); the details list the open ids |
| `DECISION_INVALID` | `DecisionInvalidError` | `INPUT_ERROR` | `2` | the `answer` action or value does not fit the request: a value on `approve` or on an action other than `accept`, a missing, unknown or ineligible option, more than one value; or the request is a `question:*` one, answered by an answer envelope (`[FIX]` is the `envelope answer` command) |
| `DECISION_RECORD_INVALID`, `HANDOFF_CHOICE_IGNORED` | `DecisionRecordError`, `HandoffChoiceIgnoredError` | `INPUT_ERROR` | `2` | collected with `file`: a decision record does not match the format (`parse_record`, `load_decisions`); a recorded handoff choice is not an eligible candidate and is ignored |
| `RETURN_INVALID` | `ReturnInvalidError` | `INPUT_ERROR` | `2` | `return --to` names no stage of the workflow, or one after the current stage |
| `HANDOFF_NOT_READY`, `HANDOFF_NONE`, `HANDOFF_OFF` | `HandoffNotReadyError`, `HandoffNoneError`, `HandoffOffError` | `INPUT_ERROR` | `2` | the unit's workflow is not complete, declares no `next`, or handoff is disabled by policy |
| `HANDOFF_CHOICE_REQUIRED` | `HandoffChoiceRequiredError` | `INTERACTION` | `2` | `handoff` under `approvals.handoff = "ask"` without a recorded choice: stop and ask the user; `[FIX]` is the `answer` command to run with their choice (details list the candidates) |
| `HANDOFF_UNDECIDED`, `HANDOFF_INVALID`, `HANDOFF_INELIGIBLE` | `HandoffUndecidedError`, `HandoffInvalidError`, `HandoffIneligibleError` | `INPUT_ERROR` | `2` | `auto` found no eligible candidate; the choice is not a candidate, or its `when` checks fail |
| `HANDOFF_LAYOUT_MISMATCH` | `HandoffLayoutMismatchError` | `INPUT_ERROR` | `2` | the chosen candidate's anchor differs from the unit's; relocate the unit, then `bind` |
| `HANDOFF_HELD` | `HandoffHeldError` | `BLOCKED` | `1` | `handoff` of a complete unit its envelopes hold: an unresolved problem, an unanswered question or a malformed worker envelope (one detail each); clear them first ([Review Envelopes, section 4](envelopes.md#4-hold-blocked-and-waiting-for-answers)) |
| `ENVELOPE_STATUS_INVALID`, `ENVELOPE_FLAG_INVALID`, `ENVELOPE_FROM_INVALID`, `ENVELOPE_FINDINGS_INVALID`, `ENVELOPE_ITEMS_INVALID`, `ENVELOPE_REFERENCE_INVALID` | `EnvelopeStatusError`, `EnvelopeFlagError`, `EnvelopeFromError`, `EnvelopeFindingsError`, `EnvelopeItemsError`, `EnvelopeReferenceError` (base `AuthoringError`) | `INPUT_ERROR` | `2` | authoring flags (`envelope new` and the kind commands) that cannot produce a valid envelope, or `envelope new` given a kind that has its own command; a `--resolve`/`--waive` number outside the carried findings, and fields or a status the kind does not allow, are `ENVELOPE_FLAG_INVALID`; a malformed `--questions-file` or `--answers-file` is `ENVELOPE_ITEMS_INVALID`; an `--answers-to` or `--resolves` that names no fitting envelope of the unit is `ENVELOPE_REFERENCE_INVALID` |
| `ENVELOPE_KIND_INVALID` | `EnvelopeKindError` | `INPUT_ERROR` | `2` | an envelope kind does not match `[a-z][a-z0-9-]*` (`write_envelope`) |
| `ENVELOPE_INVALID` | `EnvelopeFormatError` | `INPUT_ERROR` | `1` | collected with `file` by `load_envelopes`: a malformed envelope file, or an answer or resolution whose `answers_to` or `resolves` names no fitting envelope; `envelope check` reports each one with its `[TARGET]` |
| `RECEIPT_INVALID` | `devkit.core` `ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` exists but does not match its schema; restore it from version control, then run `devkit sync` |
| `GIT_FAILED` | `devkit.core` `GitError` | `MAINTENANCE` | `2` | `is_ancestor` cannot answer, or is given a non-hexadecimal revision (`INPUT_ERROR`) |
| `LOCK_HELD`, `LOCK_UNSUPPORTED`, `PATH_UNSAFE` | `devkit.core` `LockHeldError`, `LockUnsupportedError`, `UnsafePathError` | `DEFER`, `BLOCKED`, `INPUT_ERROR` | `2` | writing a decision record, an envelope or a new unit's anchor: another writer held the directory lock for 10 seconds; `flock` is unavailable on the platform or the file system; the records directory is a symbolic link ([Answer](human-interaction.md#4-answer)) |
| `WORKFLOW_OPTIONAL_STAGE_UNASKED` | `OptionalStageWarning` | `CONTINUE` (level `WARNING`) | `0` (`1` under `--strict`) | returned, never raised, by `validate` under `notices` with `where`: an optional stage's gate or `human` exit check is never requested; the definition stays valid |
| `WORKFLOW_ROLES_UNCHECKED` | `RolesUncheckedNotice` | `NOTE` (level `NOTICE`, brief) | `0` | returned, never raised, by `validate` when neither a receipt nor `[workflow] roles_dir` exists, so stage roles were not checked |

## 3. `next` Text Output

`next --format text` prints one tagged line per fact. Agents read the tags; the order is stable. Free text (details, titles, notes, `when` reasons, descriptions, error reasons) is written as a JSON string literal, so quotes and newlines are escaped and every fact stays on one line.

```text
[WORKFLOW: direct-delivery unit=.devkit/transient/work/login status=in-progress bound=yes]
[DONE: intent build-verify review]
[GATE_PASSED: intent stage=intent policy=ask source=decision:decisions/01-gate-intent.yaml]
[SKIPPED: collect-feedback reason=stages.collect-feedback=off]
[STAGE: integrate human_gate=integration role=developer isolation=none]
[UNMET: gate:integration]
[CHECK: gate:integration class=human evaluated=false detail="approval for gate 'integration' not given"]
[NEXT_SKILL: wf-integrate]
[GATE: integration policy=ask satisfied=no source=-]
[WAITING: human gate:integration]
[REQUEST: id=gate:integration kind=approve title="Approve integration" target=gate:integration stage=integrate note=allowed]
[ENVELOPE_ERROR: envelopes/review-01.yaml "missing required key status"]
```

- `[STAGE: - complete=true]` when every stage is done or skipped.
- `[BOUND_ELSEWHERE: workflow=<id>]` follows `[WORKFLOW]` when the unit is bound to another workflow than the one evaluated.
- `[SKIPPED: <id> reason=...]` names the policy entry that skipped the stage: `stages.<id>=off` or `approvals.<gate>=off`.
- `[WAITING]` appears when the current stage's gate is asked (every exit check holds), or when every unmet check is `runner` or `human`. Its class is `human` when any unmet check is human.
- `[GATE: <name> policy=P satisfied=yes|no source=S]` appears only for a gated current stage. `source` is `policy` (`auto`), `given` (`--given`), `decision:<file>` (an accepted record) or `-` while not satisfied. It ends with `held=yes` while the unit's envelopes hold the gate.
- `[BLOCKED: <file> cause="..." recovery="..."]` per unresolved problem, `[BLOCKED: <file> malformed=yes reason="..."]` per malformed worker envelope and `[PENDING_QUESTION: <file> id=<question> title="..."]` per unanswered question, whatever the stage ([Review Envelopes, section 4](envelopes.md#4-hold-blocked-and-waiting-for-answers)). While any is listed, no gate of the stage that raised it or a later stage passes, by policy, `--given` or record, and none is asked: such a gated stage whose exit checks hold reports the unmet `envelope-hold` check instead. Gates passed before stay passed, and the handoff is neither asked nor run. Unanswered questions also become `question:*` requests and set `[WAITING: human <their ids>]`.
- `[DELEGATE: role=R isolation=I]` and `[RETURNS: <to> when="..."; ...]` describe the current stage. `[DELEGATE]` carries `contract=<path>` when the role is in the project's vocabulary (receipt `subagent` asset or `roles_dir` file); otherwise the key is absent.
- `[STALE_APPROVAL: <file> request=<id> stage=<stage> counts=yes void_with="devkit workflow return --unit <dir> --to <current stage>"]` lists approvals of later stages found while an earlier stage is current. It is a read-only notice: `next` writes nothing, and those approvals keep counting until `devkit workflow return` records a `return:<stage>` decision that voids them.
- `[LINT_ERROR: "..."]` appears when `lint-clean` could not run; the command then also reports the `devkit.rules` error on stderr (text mode), unchanged (for example `RULES_RUN_FAILED`), and exits with its exit code.
- Whenever a person must act, one `[REQUEST: ...]` line per open request follows the stage block (ending with `answer=given` for a gate the definition marks so: pass `--given <gate>` after the approval instead of recording it), with `[DECLINED: ...]` for a request that was refused and is still open, and `[DECISION_ERROR: file "reason"]` for a malformed or ignored record (formats in [Human Interaction Contract](human-interaction.md#3-request)).

When the workflow is complete and declares `next` candidates (and `approvals.handoff` is not `off`), the handoff block follows:

```text
[STAGE: - complete=true]
[HANDOFF: policy=ask candidates=spec-driven hotfix direct-delivery eligible=hotfix direct-delivery recommended=- chosen=-]
[CANDIDATE: spec-driven eligible=no recommended=yes when=file-exists(spec.md)=false]
[CANDIDATE: hotfix eligible=yes recommended=no when=frontmatter(task.md kind hotfix)=true]
[CANDIDATE: direct-delivery eligible=yes recommended=no when=-]
[WAITING: human handoff]
```

- `recommended=` lists only candidates that are both recommended and eligible.
- Under `policy=auto`, `chosen=` names the first eligible candidate and no `[WAITING]` line appears; with no eligible candidate the engine falls back to waiting for a person.
- A recorded choice of the current segment (`decisions/NN-handoff.yaml`) sets `chosen=` under either policy and adds `decision=<file>`. A recorded choice that is not an eligible candidate is ignored and reported as a `[DECISION_ERROR]`.
- No `[HANDOFF]` line means the unit is finished.

## 4. JSON Output

`next --format json` emits one object:

```json
{
  "workflow": "direct-delivery",
  "unit": ".devkit/transient/work/login",
  "status": "in-progress",
  "bound": true,
  "bound_elsewhere": null,
  "done": ["intent", "build-verify"],
  "skipped": [{"id": "collect-feedback", "reason": "stages.collect-feedback=off"}],
  "stage": {"id": "review", "name": "Review loop", "human_gate": null, "role": "reviewer", "isolation": "preferred", "skills": ["wf-review"], "entry": [], "exit": [], "artifacts": [], "returns": []},
  "unmet": [{"name": "envelope-review-passed", "class": "disk", "satisfied": false, "evaluated": true, "detail": "no review envelope"}],
  "next_skill": "wf-review",
  "delegate": {"role": "reviewer", "isolation": "preferred", "contract": ".devkit/managed/team/subagents/reviewer.md"},
  "gate": null,
  "waiting": null,
  "complete": false,
  "handoff": null,
  "requests": [],
  "stale_approvals": [],
  "passed_gates": [],
  "blocked": false,
  "problems": [],
  "pending_questions": [],
  "malformed_workers": [],
  "errors": []
}
```

- `gate` is `null` for an ungated stage, else `{"name", "policy", "satisfied", "source", "decision", "held"}` (`source` is `policy`, `given`, `decision` or `null`; `decision` names the record file; `held` is `true` while the unit's envelopes keep it from passing).
- `blocked`, `problems` (`[{"file", "cause", "attempts", "recovery"}]`), `pending_questions` (`[{"file", "id", "title"}]`) and `malformed_workers` (`[{"file", "reason"}]`) report the hold of the unit's envelopes, over every segment ([Review Envelopes, section 4](envelopes.md#4-hold-blocked-and-waiting-for-answers)).
- `handoff` is `null` until the workflow is complete; then it is `{"policy", "candidates": [{"workflow", "recommended", "eligible", "checks": [...]}], "eligible": [...], "recommended": [...], "chosen", "decision"}`.
- `passed_gates` lists the gates of done stages with what passed them: `[{"stage", "name", "policy", "satisfied", "source", "decision", "held"}]`, in text one `[GATE_PASSED: <gate> stage=<id> policy=P source=policy|given|decision:<file>]` line each after `[DONE]`. A gate an `auto` policy passed is never current, so this is where a report finds the basis of every gate.
- `requests` holds the open requests ([Human Interaction Contract](human-interaction.md#3-request)); `stale_approvals` the files of approvals for stages after the current one, which still count until a `return` record voids them.
- `errors` holds every collected problem: malformed envelopes (`ENVELOPE_INVALID`) and decision records (`DECISION_RECORD_INVALID`, `HANDOFF_CHOICE_IGNORED`) with their `file`, and the `devkit.rules` error that stopped `lint-clean`.

The other commands:

- `show --format json`: the parsed document plus `layout`, the effective `anchor`, `approvals`, `stages_off`, `ok` and `errors` (the definition's problems, with `where`). `show --unit <dir>` describes the definition the unit is bound to (else `[workflow].default`), loaded unvalidated like `show <ref>` so its problems are reported, not raised, and adds `binding` (`workflow`, `workflow_history`) and, in text, a `[BINDING: workflow=W]` line after the document.
- `validate --format json`: `{"ok", "roles_checked", "definitions": [{"id", "path", "ok", "errors"}], "errors", "notices"}`. A definition's own `errors` carry `where` (`WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_CHECK_INVALID` or `ROLE_UNKNOWN`, exit `1`); the top-level `errors` hold the files that could not be loaded (`WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_ASSET_MISSING`, exit `2`) and the shared-stage differences (`SHARED_STAGE_MISMATCH`, exit `1`). `notices` hold each definition's warnings (`WORKFLOW_OPTIONAL_STAGE_UNASKED`, with `where`; they leave the definition `ok`) and `WORKFLOW_ROLES_UNCHECKED`. In text, each problem of a definition is a `[PROBLEM: <where>: <message>]` line and a shared-stage difference is `[INVALID: shared stage '<id>' differs between <a> and <b>: <field>]`; warnings and notices follow on stderr.
- `checks --format json`: `{"checks": [...]}`, the registry: primitives and the anchor aliases.
- `list --format json`: `{"units": [{"unit", "anchor", "status", "workflow", "history", "error"}]}` across every layout in use; the text form is `[UNIT: <dir> status=S workflow=W anchor=A]`, with `error="..."` for a unit whose anchor cannot be read (in JSON, the `ANCHOR_INVALID` advisory `to_dict()`). `--status <value>` keeps units whose anchor `status` equals a given value (repeatable) and `--exclude-status <value>` drops them; both are exact matches and nothing is excluded by default, so active units are `--exclude-status completed`.
- `handoff --format json`: `{"unit", "from", "to", "policy", "decision", "history"}`.
- `requests --format json`: `{"requests": [...], "errors": [...]}`, where `errors` holds the error that stopped `lint-clean`, if any; in text it is a `[LINT_ERROR: "..."]` line after the requests, and the command exits with its exit code as `next` does. `answer` and `return` emit the written record with its `file`.
- `envelope new`, `worker`, `answer`, `resolution`, `review`, `reverify` and `check`: see [Review Envelopes](envelopes.md).
