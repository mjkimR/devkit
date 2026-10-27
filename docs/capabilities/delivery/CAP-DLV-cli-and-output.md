---
id: CAP-DLV-cli-and-output
title: "Workflow CLI and Output"
summary: "Commands, exit codes, text sentinels, and JSON payload contracts for workflows."
area: delivery
status: active
created_at: 2026-10-17
---

# [CAP-DLV-cli-and-output] Workflow CLI and Output Contract

**Package**: `devkit_agt.features.workflow` (`devkit workflow` CLI). Envelope commands: `CAP-DLV-workflow-envelopes`; requests and decision records: `CAP-DLV-human-interaction`.
**Related**: `CAP-DLV-workflow-orchestration`, `ARCH-08-1-agent-output`.

## 1. Commands

The default group help focuses on operating existing units. Authoring commands `new`, `bind`, `checks`, `validate` and `envelope new` remain callable with their own `--help` but are hidden from their parent help.

```bash
devkit workflow new <slug> [--workflow ID] [--date YYYY-MM-DD] [--status S]   # create a unit from the layout template and bind it
devkit workflow bind --unit DIR [--anchor FILE] [--workflow ID]  # record or change the workflow binding
devkit workflow next --unit DIR [--anchor FILE] [--workflow ID] [--given NAME]... [--no-lint] [--format text|json]
devkit workflow handoff --unit DIR [--anchor FILE] [--workflow ID] [--date YYYY-MM-DD] [--by NAME] [--given NAME]... [--no-lint] [--format text|json]
devkit workflow next --view requests --unit DIR [--anchor FILE] [--no-lint] [--format text|json]   # requests-only view, using the same evaluation and error status as next
devkit workflow answer --unit DIR [--anchor FILE] --request ID --action accept|decline|cancel [--value V] [--note TEXT] [--by NAME] [--given NAME]... [--no-lint] [--format text|json]
devkit workflow return --unit DIR [--anchor FILE] --to STAGE [--note TEXT] [--by NAME] [--given NAME]... [--no-lint] [--format text|json]  # go back; later approvals are asked again
devkit workflow show <ID|PATH> [--format text|json]              # a definition's stages and next candidates
devkit workflow show --unit DIR [--anchor FILE] [--format text|json]  # the unit's bound definition plus [BINDING: workflow=...]
devkit workflow checks [--format text|json]                      # registered check names, classes and parameters (plugins included)
devkit workflow validate [PATH]... [--format text|json]          # validate definitions (default: both sources, plus roles and shared stages)
devkit workflow list [--status S]... [--exclude-status S]... [--format text|json]  # discovered units across every layout
# COMMON: --unit DIR [--anchor FILE] [--stage ID] [--summary TEXT] [--assume TEXT]... [--unverified TEXT]...
#         [--effort low|medium|high] [--format text|json]
# VERIFY: [--status S] [--check NAME=PASS|FAIL|SKIP[ detail]]... [--base REV] [--head REV]   (not on answer or resolution)
# With only --unit (and --stage) each writes the next envelopes/<kind>-NN.yaml skeleton; any other flag writes it complete.
devkit workflow envelope new --kind KIND COMMON VERIFY [--findings-file PATH|-]      # any kind but the five below
devkit workflow envelope worker --stage ID COMMON VERIFY [--questions-file PATH|-] [--problem CAUSE [--tried TEXT]... --recovery TEXT]
                                [--findings-file PATH|-]
devkit workflow envelope answer COMMON [--answers-to FILE] [--answers-file PATH|-] [--settle N=DECISION]...
devkit workflow envelope resolution COMMON [--resolves FILE]
devkit workflow envelope review COMMON VERIFY [--findings-file PATH|-]
devkit workflow envelope reverify COMMON VERIFY [--from latest|FILE] [--resolve N|all]... [--waive N=REASON]... [--findings-file PATH|-]
devkit workflow envelope check --unit DIR [--details] [--format text|json]   # every envelope file, contract violations and the hold
```

`--anchor FILE` names the anchor file that identifies the unit when its directory holds several candidate anchors (`ANCHOR_AMBIGUOUS`); see `CAP-DLV-workflow-orchestration`.

All commands accept `-w/--workspace-root`. It defaults to the devkit root of the current directory (the Git work tree's top level; outside Git, the nearest directory with a `.devkit/` folder); an explicit value that is not an existing directory, or one below the top level of a Git work tree, is `ARGUMENT_INVALID`; a `.devkit/` below the top level of a work tree whose top level has none is `DEVKIT_ROOT_NESTED`.

## 2. Exit Codes and Errors

Exit codes follow the devkit convention (`ARCH-08-cross-cutting`):

| Exit | When |
| --- | --- |
| `0` | The command did its job. `next` exits `0` whatever the stage, including a unit that waits for a person (`[WAITING]`, `[REQUEST]`, a recorded decline), a delegation (`[DELEGATE]`) or a handoff choice. |
| `1` | The command ran and reports a negative result: `validate` found invalid definitions or shared-stage differences (a definition file that cannot be loaded at all makes it exit `2`), `show` found problems in the definition, `envelope check` found malformed envelope files (`ENVELOPE_INVALID`), `handoff` found the unit held by its envelopes (`HANDOFF_HELD`). |
| `2` | The command could not do its job: a usage error from the command line parser, an argument error (`ARGUMENT_INVALID`: a `-w` or `validate` path that does not exist, a malformed `--date`, `show` given both or neither of `REF` and `--unit`, or `--anchor` without `--unit`), and every other error code below whose exit is `2` (unreadable configuration, receipt, definition or anchor, a refused input, a lint run that could not execute, an unexpected error). |

A command that collects several problems (`validate`, `envelope check`) exits with the highest exit code among them. `show` only reports, so it exits `1` when its report lists any problem, whatever the problem's own code, and `2` only when it cannot run (an unknown workflow, an unreadable definition or configuration).

In text mode errors are reported on stderr as Agent Advisory Protocol blocks from `devkit.advisory`, with a stable code and an `[ACTION]` directive, so an agent knows whether to fix input, stop for a person, or respect a guardrail. Under `--format json` stdout carries exactly one JSON object, never a bare array: the command's result, or `{"error": {...}}` when it has none. Problems a command collects rather than raises are listed in its result under `errors`, each the `to_dict()` of an advisory error (`code`, `level`, `message`, `exit_code`, `advisory`, plus `file` or `where` when the problem has one); warnings and notices are listed under `notices`. The JSON object carries every advisory, so nothing is rendered on stderr in JSON mode; in text mode warnings and notices follow the result as `[WARN]` or `[NOTICE]` blocks.

Each advisory reaches the agent once (`ARCH-08-1-agent-output` section 1). A text-mode `next` (including its `--view requests` view) whose lint run failed prints its result, in which the `lint-clean` check names only the error's code (`[CHECK: lint-clean ... detail="lint failed: RULES_RUN_FAILED"]`), and then reports the `devkit_agt.features.rules` error on stderr, unchanged; in JSON it is among the result's `errors`. `envelope check` reports each `ENVELOPE_INVALID` file only on stderr, with no stdout line for it. `next` reports a malformed envelope or decision record only as an `[ENVELOPE_ERROR]` or `[DECISION_ERROR]` line, never also on stderr.

**Fixes and targets.** Every `[FIX]` is runnable as written (`CAP-ADV-agent-advisory-protocol` section 8): a command with the unit and every other value filled in, through the agent-facing invocation `uv run devkit ...`, or an edit naming what to change; it never contains a placeholder such as `<id>` or names an option the command lacks. When several candidates fit, `[FIX]` is the command that lists them (or the command for a single candidate) and `[DETAIL]` gives one exact command or option per candidate: `ANCHOR_AMBIGUOUS` repeats the invoked command with each `--anchor`, `HANDOFF_CHOICE_REQUIRED` and `HANDOFF_CHOICE_IGNORED` give one `answer --unit DIR --request handoff --action accept --value <candidate>` per eligible candidate, `WORKFLOW_NOT_SELECTED` and `ANCHOR_MISMATCH` one `bind --unit DIR --workflow <id>` per fitting workflow, and the envelope refusals the `--from`, `--answers-to`, `--resolves` or finding numbers that fit (`CAP-DLV-workflow-envelopes`). Every `INPUT_ERROR` caused by an option has that option as its `[TARGET]` (`--request`, `--value`, `--action`, `--to`, `--given`, `--anchor`, `--workflow`, `--from`, `--settle`, ...); one caused by a file names the file.

The library raises the same codes, one class per code. `WorkflowError` is the base: it sets the actor and retry once, and each subclass adds its code and mode. Foundation and project errors (`CONFIG_INVALID`, `RECEIPT_INVALID`, `GIT_FAILED`, ...) and of `devkit_agt.features.rules` (from `lint-clean`) pass through unchanged.

| Code | Class | Mode | Exit | Raised when |
| --- | --- | --- | --- | --- |
| `CONFIG_INVALID` | `devkit_dist.base.errors` `ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` cannot be read or parsed (passed through unchanged) |
| `WORKFLOW_CONFIG_INVALID` | `WorkflowConfigError` | `INPUT_ERROR` | `2` | the `[workflow]`, `[workflow.approvals]` or `[workflow.stages]` table is malformed (a subclass of the `devkit_dist.base.errors` `ConfigError`) |
| `WORKFLOW_GATE_POLICY` | `GatePolicyError` | `INPUT_ERROR` | `2` | `[workflow.approvals]` sets a gate to a policy its definition does not accept (`gates.<gate>.policies`); refused before evaluation by `next`, `answer`, `return` and `handoff` |
| `ARGUMENT_INVALID` | `devkit_core.base.errors` `ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` or a `validate` path does not exist, `--date` is not `YYYY-MM-DD`, or `show` is given both or neither of `REF` and `--unit` |
| `WORKFLOW_NOT_SELECTED`, `WORKFLOW_NOT_FOUND`, `WORKFLOW_INVALID` | `WorkflowNotSelectedError`, `WorkflowNotFoundError`, `WorkflowInvalidError` | `INPUT_ERROR` | `2` | no definition chosen (`new` without `--workflow` or `[workflow].default`; for a unit command, an unbound unit without a default, with one `[DETAIL]` `bind --unit DIR --workflow <id>` per discovered workflow, the `[FIX]` itself when there is one), no id or file matches (the `[FIX]` names the discovered ids), or the chosen one fails validation (problems become `[DETAIL]` lines) |
| `WORKFLOW_NOT_BINDABLE` | `WorkflowNotBindableError` | `INPUT_ERROR` | `2` | `new` or `bind` was given `--workflow <path>` naming a file that is not the discovered definition of its id (outside `definitions_dir` and the receipt, or shadowed by another file with the same id); a binding records only the id, so later commands could not find the file |
| `WORKFLOW_DEFINITION_INVALID` | `DefinitionError` | `INPUT_ERROR` | `2` | a definition file cannot be read or parsed (`parse_definition`, `load_definition`), or an id is defined twice; `validate` collects it as a load error |
| `WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_CHECK_INVALID`, `ROLE_UNKNOWN` | `DefinitionProblem`, `CheckReferenceProblem`, `RoleUnknownProblem` | `INPUT_ERROR` | `1` | collected by validation with `where` (`<stage>.<field>`): a problem in a loaded definition, a check reference that does not resolve, a role outside the vocabulary |
| `SHARED_STAGE_MISMATCH` | `SharedStageMismatchError` | `INPUT_ERROR` | `1` | collected by a whole-workspace `validate`: stages that share an id but differ |
| `WORKFLOW_ASSET_MISSING` | `WorkflowAssetMissingError` | `AUTO` | `2` | collected by discovery: a receipt-listed definition is missing from disk; `[FIX]` is `devkit sync` |
| `WORKFLOW_CHECK_INVALID` | `CheckError` | `INPUT_ERROR` | `2` | a check reference is malformed, unregistered, a duplicate or colliding declaration, or a `runner`/`human` check in `next[].when` (`parse_check`, `Registry`, `validate`) |
| `LAYOUT_INVALID`, `SLUG_INVALID` | `LayoutError`, `SlugError` | `INPUT_ERROR` | `2` | a layout template, directory or anchor file name is malformed (`validate_template`, `parse_layout_spec`; inside `[workflow]` it is `WORKFLOW_CONFIG_INVALID`); a unit slug does not match `[a-z0-9][a-z0-9-]*` |
| `UNIT_NOT_FOUND`, `UNIT_EXISTS`, `ANCHOR_INVALID` | `UnitNotFoundError`, `UnitExistsError`, `AnchorInvalidError` | `INPUT_ERROR` | `2` | the unit directory has no anchor (`[FIX]` names `list`; with `--anchor`, `[TARGET] --anchor` and the anchors the unit holds), already exists (also when a concurrent `new` created the anchor first: `new` creates it exclusively), or its frontmatter is unreadable (`list` collects the last one per unit) |
| `UNIT_DIR_NOT_EMPTY` | `UnitDirNotEmptyError` | `INPUT_ERROR` | `2` | `new` found the unit directory without an anchor but holding leftover records (`decisions/*.yaml`, `envelopes/*.yaml` or `*.yml`, listed as details and targets), which would count in the new unit (fix: another slug, or move the records out); other files such as `.gitkeep` or notes are left in place and do not refuse it |
| `ANCHOR_AMBIGUOUS`, `ANCHOR_MISMATCH` | `AnchorAmbiguousError`, `AnchorMismatchError` | `INPUT_ERROR` | `2` | several candidate anchor files exist in the unit (`[TARGET] --anchor`; one `[DETAIL]` per candidate: the invoked command with `--anchor FILE` added); the selected workflow declares a different anchor than the file that identifies the unit, or than `--anchor` names |
| `GIVEN_INVALID` | `GivenInvalidError` | `INPUT_ERROR` | `2` | a `--given` name is neither a gate nor a registered runner or human check (`[TARGET] --given`) |
| `REQUEST_UNKNOWN` | `RequestUnknownError` | `INPUT_ERROR` | `2` | `answer --request` is not an open request of the unit (and not `feedback:*`); the details list the open ids and `[FIX]` is `next --view requests --unit DIR` |
| `DECISION_INVALID` | `DecisionInvalidError` | `INPUT_ERROR` | `2` | the `answer` action or value does not fit the request: a value on `approve` or on an action other than `accept`, a missing, unknown or ineligible option, more than one value (`[TARGET] --value` or `--action`); or the request is a `question:*` one, answered by an answer envelope (`[TARGET] --request`; `[FIX]` is `envelope answer --unit DIR --answers-to <worker file> --answers-file -`, the message says what stdin holds) |
| `DECISION_RECORD_INVALID`, `HANDOFF_CHOICE_IGNORED` | `DecisionRecordError`, `HandoffChoiceIgnoredError` | `INPUT_ERROR` | `2` | collected with `file`: a decision record does not match the format (`parse_record`, `load_decisions`); a recorded handoff choice is not an eligible candidate and is ignored |
| `RETURN_INVALID` | `ReturnInvalidError` | `INPUT_ERROR` | `2` | `return --to` names no stage of the workflow, or one after the current stage (`[TARGET] --to`) |
| `HANDOFF_NOT_READY` | `HandoffNotReadyError` | `INTERACTION` | `2` | the unit's workflow is not complete: whether to finish the current stage first is the user's call; `[REPORT]` names the stage and `[FIX]` is `next --unit DIR` |
| `HANDOFF_NONE`, `HANDOFF_OFF` | `HandoffNoneError`, `HandoffOffError` | `INPUT_ERROR` | `2` | the unit's workflow declares no `next`, or handoff is disabled by policy |
| `HANDOFF_CHOICE_REQUIRED` | `HandoffChoiceRequiredError` | `INTERACTION` | `2` | `handoff` under `approvals.handoff = "ask"` without a recorded choice: stop and ask the user (`[REPORT]` names the eligible and recommended candidates); one `[DETAIL]` `answer --unit DIR --request handoff --action accept --value <candidate>` per eligible candidate, `[FIX]` the single one or `next --unit DIR`; the message names the `handoff` to run after the answer |
| `HANDOFF_UNDECIDED`, `HANDOFF_INVALID`, `HANDOFF_INELIGIBLE` | `HandoffUndecidedError`, `HandoffInvalidError`, `HandoffIneligibleError` | `INPUT_ERROR` | `2` | `auto` found no eligible candidate (details give each candidate's `when` checks; `[FIX]` reruns `handoff --unit DIR` once one holds); the choice is not a candidate, or its `when` checks fail (`[TARGET] --workflow`) |
| `HANDOFF_LAYOUT_MISMATCH` | `HandoffLayoutMismatchError` | `INPUT_ERROR` | `2` | the chosen candidate's anchor differs from the unit's; relocate the unit, then `bind` |
| `HANDOFF_HELD` | `HandoffHeldError` | `INTERACTION` | `1` | `handoff` of a complete unit its envelopes hold: an unresolved problem, an unanswered question or a malformed worker envelope (one detail each); the answers and recovery decisions come from the user, so the agent stops and asks; `[FIX]` is `envelope check --unit DIR` (`CAP-DLV-workflow-envelopes`) |
| `ENVELOPE_STATUS_INVALID`, `ENVELOPE_FLAG_INVALID`, `ENVELOPE_FROM_INVALID`, `ENVELOPE_FINDINGS_INVALID`, `ENVELOPE_ITEMS_INVALID`, `ENVELOPE_REFERENCE_INVALID` | `EnvelopeStatusError`, `EnvelopeFlagError`, `EnvelopeFromError`, `EnvelopeFindingsError`, `EnvelopeItemsError`, `EnvelopeReferenceError` (base `AuthoringError`) | `INPUT_ERROR` | `2` | authoring flags (`envelope new` and the kind commands) that cannot produce a valid envelope, or `envelope new` given a kind that has its own command; a `--resolve`/`--waive` number outside the carried findings, a malformed or repeated `--settle`, a `challenger` or `review` finding recorded as not `open`, and fields or a status the kind does not allow, are `ENVELOPE_FLAG_INVALID`; a malformed `--questions-file` or `--answers-file` is `ENVELOPE_ITEMS_INVALID`; an `--answers-to` or `--resolves` that names no fitting envelope of the unit, or a `--settle` position beyond its `assumptions`, is `ENVELOPE_REFERENCE_INVALID` |
| `ENVELOPE_KIND_INVALID` | `EnvelopeKindError` | `INPUT_ERROR` | `2` | an envelope kind does not match `[a-z][a-z0-9-]*` (`write_envelope`) |
| `ENVELOPE_INVALID` | `EnvelopeFormatError` | `INPUT_ERROR` | `1` | collected with the unit-relative `file` by `load_envelopes`: a malformed envelope file, or an answer or resolution whose `answers_to` or `resolves` names no fitting envelope; `next` and `envelope check` set its `[TARGET]` to the workspace-relative file and its `[FIX]` to fixing or removing it, then `envelope check --unit DIR` |
| `RECEIPT_INVALID` | `devkit_dist.base.errors` `ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` exists but does not match its schema; restore it from version control, then run `devkit sync` |
| `GIT_FAILED` | `devkit_core.base.errors` `GitError` | `MAINTENANCE` | `2` | `is_ancestor` cannot answer, or is given a non-hexadecimal revision (`INPUT_ERROR`) |
| `LOCK_HELD`, `LOCK_UNSUPPORTED`, `PATH_UNSAFE` | `devkit_core.base.errors` `LockHeldError`, `LockUnsupportedError`, `UnsafePathError` | `DEFER`, `BLOCKED`, `INPUT_ERROR` | `2` | writing a decision record, an envelope or a new unit's anchor: another writer held the directory lock for 10 seconds; `flock` is unavailable on the platform or the file system; the records directory is a symbolic link (`CAP-DLV-human-interaction`) |
| `WORKFLOW_OPTIONAL_STAGE_UNASKED` | `OptionalStageWarning` | `CONTINUE` (level `WARNING`) | `0` (`1` under `--strict`) | returned, never raised, by `validate` under `notices` with `where`: an optional stage's gate or `human` exit check is never requested; the definition stays valid |
| `WORKFLOW_ROLES_UNCHECKED` | `RolesUncheckedNotice` | `NOTE` (level `NOTICE`, brief) | `0` | returned, never raised, by `validate` when neither a receipt nor `[workflow] roles_dir` exists, so stage roles were not checked |

## 3. `next` Text Output

`next --format text` prints one tagged line per fact (`ARCH-08-1-agent-output` section 3). Agents read the tags; the order is stable. A value without spaces is bare, a boolean is `yes` or `no`, an empty value is `-`, and free text (details, titles, notes, `when` reasons, descriptions, error reasons, a `when` summary that contains a space) is written as a JSON string literal, so quotes and newlines are escaped and every fact stays on one line. Lists documented as space-separated (`[DONE]`, `[UNMET]`, `[HANDOFF]`'s `candidates`, `eligible`, `recommended`) and comma-separated (`[REQUEST]`'s `options`, `eligible`, `recommended`) hold ids only.

```text
[WORKFLOW: direct-delivery unit=.devkit/transient/work/login status=in-progress bound=yes]
[DONE: intent build-verify review]
[GATE_PASSED: intent stage=intent policy=ask source=decision:decisions/01-gate-intent.yaml]
[SKIPPED: collect-feedback reason=stages.collect-feedback=off]
[STAGE: integrate human_gate=integration role=developer isolation=none]
[UNMET: gate:integration]
[NEXT_SKILL: wf-integrate]
[GATE: integration policy=ask satisfied=no source=-]
[WAITING: human gate:integration]
[REQUEST: id=gate:integration kind=approve title="Approve integration" target=gate:integration stage=integrate note=allowed]
[ENVELOPE_ERROR: envelopes/review-01.yaml "missing required key status"]
```

Every line `next` prints, in this order (a line whose condition does not hold is absent):

| Line | When and what |
| --- | --- |
| `[WORKFLOW: <id> unit=<dir> status=<anchor status>\|- bound=yes\|no]` | Always first. `unit` is workspace-relative. |
| `[BOUND_ELSEWHERE: workflow=<id>]` | The unit is bound to another workflow than the one evaluated (`--workflow`). |
| `[DONE: <stage>...\|-]` | Always: the stages done, space-separated. |
| `[GATE_PASSED: <gate> stage=<id> policy=P source=policy\|given\|decision:<file>]` | One per gate of a done stage, with what passed it. |
| `[SKIPPED: <id> reason=stages.<id>=off\|approvals.<gate>=off]` | One per stage skipped by policy. |
| `[STAGE: <id> human_gate=<gate>\|- role=<role>\|- isolation=<isolation>\|-]` | The current stage. |
| `[STAGE: - complete=yes]` | Instead, when every stage is done or skipped; the handoff block below may follow. |
| `[UNMET: <check>...\|-]` | The current stage's unmet exit checks, space-separated. |
| `[CHECK: <check> class=<class> evaluated=yes\|no detail="..."]` | One per unmet check, except the current gate's `gate:<gate>`, which the `[GATE]` line reports. `evaluated=no` means the check could not be evaluated (a runner or human check without `--given`, Git unable to answer). A `lint-clean` whose rules could not run reads `detail="lint failed: <CODE>"`; the error itself is on stderr. |
| `[NEXT_SKILL: <skill>\|-]` | The skill that performs the current stage. |
| `[DELEGATE: role=R isolation=I contract=<path>]` | The current stage asks for a subagent; `contract` only when the role is in the project's vocabulary (receipt `subagent` asset or `roles_dir` file). |
| `[RETURNS: <to> when="..."; ...]` | The stages the current one may return to. |
| `[GATE: <gate> policy=P satisfied=yes\|no source=policy\|given\|decision:<file>\|- held=yes]` | The current stage is gated. `satisfied` reports the gate's approval only (an `auto` policy, `--given` or an accepted record), not the stage: an `auto` gate reads `satisfied=yes` while other exit checks are still unmet, and the stage passes only when `[UNMET]` is empty. `held=yes` only while the unit's envelopes hold the gate. |
| `[WAITING: human\|runner <check>...]` | The stage waits for a person or a runner: its gate is asked (every exit check holds), or every unmet check is `runner` or `human` (class `human` when any is). Also for unanswered questions (their request ids) and a handoff choice (`handoff`). |
| `[STALE_APPROVAL: <file> request=<id> stage=<stage> counts=yes void_with="uv run devkit workflow return --unit <dir> --to <current stage>"]` | One per approval of a later stage found while an earlier stage is current. A read-only fact: `next` writes nothing, and those approvals keep counting until `devkit workflow return` records a `return:<stage>` decision that voids them. |
| `[BLOCKED: <file> cause="..." recovery="..."]` | One per unresolved problem, whatever the stage (`CAP-DLV-workflow-envelopes`). |
| `[PENDING_QUESTION: <file> id=<question> title="..."]` | One per unanswered question. |
| `[BLOCKED: <file> malformed=yes reason="..."]` | One per malformed worker envelope. |
| `[REQUEST: ...]`, `[DECLINED: id=<id> file=<file> note="..."]` | One `[REQUEST]` per open request (formats in `CAP-DLV-human-interaction`; a gate the definition marks `answer: given` ends with `answer=given`: pass `--given <gate>` after the approval instead of recording it), each followed by `[DECLINED]` when it was refused and is still open. |
| `[ENVELOPE_ERROR: <file> "reason"]` | One per malformed envelope, `<file>` unit-relative; this line is its only report in text. |
| `[DECISION_ERROR: <file> "reason"]` | One per malformed decision record or ignored handoff choice; its only report in text. |

While any `[BLOCKED]` or `[PENDING_QUESTION]` is listed, no gate of the stage that raised it or a later stage passes, by policy, `--given` or record, and none is asked: such a gated stage whose exit checks hold reports the unmet `envelope-hold` check instead. Gates passed before stay passed, and the handoff is neither asked nor run. Unanswered questions also become `question:*` requests and set `[WAITING: human <their ids>]`.

When the workflow is complete and declares `next` candidates (and `approvals.handoff` is not `off`), the handoff block follows `[STAGE: - complete=yes]`:

```text
[STAGE: - complete=yes]
[HANDOFF: policy=ask candidates=spec-driven hotfix direct-delivery eligible=hotfix direct-delivery recommended=- chosen=-]
[CANDIDATE: spec-driven eligible=no recommended=yes when=file-exists(spec.md)=no]
[CANDIDATE: hotfix eligible=yes recommended=no when="frontmatter(task.md kind hotfix)=yes"]
[CANDIDATE: direct-delivery eligible=yes recommended=no when=-]
[WAITING: human handoff]
[REQUEST: id=handoff kind=choose title="Choose next workflow" options=spec-driven,hotfix,direct-delivery eligible=hotfix,direct-delivery recommended=-]
```

| Line | When and what |
| --- | --- |
| `[HANDOFF: policy=ask\|auto candidates=<ids> eligible=<ids>\|- recommended=<ids>\|- chosen=<id>\|- decision=<file>]` | The candidates of a complete unit. `recommended` lists only candidates that are both recommended and eligible. Under `policy=auto`, `chosen` names the first eligible candidate and no `[WAITING]` line appears; with no eligible candidate the engine falls back to waiting for a person. A recorded choice of the current segment (`decisions/NN-handoff.yaml`) sets `chosen` under either policy and adds `decision=<file>`; a recorded choice that is not an eligible candidate is ignored and reported as a `[DECISION_ERROR]`. |
| `[CANDIDATE: <id> eligible=yes\|no recommended=yes\|no when=<check>=yes\|no ...\|-]` | One per candidate, with the result of each of its `when` checks (quoted when a check contains a space). |

No `[HANDOFF]` line after `[STAGE: - complete=yes]` means the unit is finished. `[HANDOFF]` is `next`'s report of the candidates only; the `handoff` command reports the rebinding it did as `[HANDED_OFF]` (section 4).

## 4. Other Commands and JSON Output

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

- `unmet` lists every unmet check, the current gate's `gate:<gate>` included (text leaves its `[CHECK]` line out).
- `gate` is `null` for an ungated stage, else `{"name", "policy", "satisfied", "source", "decision", "held"}` (`source` is `policy`, `given`, `decision` or `null`; `decision` names the record file; `held` is `true` while the unit's envelopes keep it from passing).
- `blocked`, `problems` (`[{"file", "cause", "attempts", "recovery"}]`), `pending_questions` (`[{"file", "id", "title"}]`) and `malformed_workers` (`[{"file", "reason"}]`) report the hold of the unit's envelopes, over every segment (`CAP-DLV-workflow-envelopes`).
- `handoff` is `null` until the workflow is complete; then it is `{"policy", "candidates": [{"workflow", "recommended", "eligible", "checks": [...]}], "eligible": [...], "recommended": [...], "chosen", "decision"}`.
- `passed_gates` lists the gates of done stages with what passed them: `[{"stage", "name", "policy", "satisfied", "source", "decision", "held"}]`. A gate an `auto` policy passed is never current, so this is where a report finds the basis of every gate.
- `requests` holds the open requests (`CAP-DLV-human-interaction`); `stale_approvals` the files of approvals for stages after the current one, which still count until a `return` record voids them.
- `errors` holds every collected problem: malformed envelopes (`ENVELOPE_INVALID`) and decision records (`DECISION_RECORD_INVALID`, `HANDOFF_CHOICE_IGNORED`) with their unit-relative `file`, and the `devkit_agt.features.rules` error that stopped `lint-clean`.

The other commands print, in text:

| Command | Lines |
| --- | --- |
| `next --view requests` | The `[REQUEST]` and `[DECLINED]` lines of `next`, or `[OK: no open requests]`. A lint error is reported on stderr and sets the exit code, as for `next`. |
| `answer` | `[DECISION: <file> request=<id> kind=approve\|choose\|feedback action=accept\|decline\|cancel]`, the record written (`<file>` unit-relative). |
| `return` | `[RETURNED: <file> to=<stage>]`, the `return:<stage>` record written. |
| `handoff` | `[HANDED_OFF: from=<workflow> to=<workflow> policy=ask\|auto decision=<file>]` (`decision` only when a recorded or explicit choice was used), then `[HISTORY: <workflow>...]`, the finished segments in order. |
| `new` | `[UNIT: <dir> workflow=<id> anchor=<file>]`. |
| `bind` | `[BOUND: <id>]`. |
| `list` | One `[UNIT: <dir> status=<status>\|- workflow=<id>\|- anchor=<file> error="..."]` per unit (`error` only for an anchor that cannot be read: the first line of the reason), or `[OK: no units dirs=<work dirs>]` (comma-separated, quoted when they contain a space). |
| `show` | The document lines below, then `[BINDING: workflow=<id>\|-]` with `--unit`, then one `[PROBLEM: <where>: <message>]` per problem of the definition. |
| `checks` | One `[CHECK: <name>(<params>) class=<class> alias=<alias> description="..."]` per registered check (`alias` only for an alias): the registry, not an evaluation. |
| `validate` | `[VALID: <path> id=<id>]` or `[INVALID: <path> id=<id> problems=N]` with one `[PROBLEM: <where>: <message>]` each, `[INVALID: <load error>]` per file that cannot be loaded and per shared-stage difference (`[INVALID: shared stage '<id>' differs between <a> and <b>: <field>]`), or `[VALID: no definitions under <dir>]`; warnings and notices follow on stderr. |
| `envelope ...` | `CAP-DLV-workflow-envelopes` sections 2 and 3. |

`show`'s document lines describe the definition, not a unit's evaluation:

| Line | What |
| --- | --- |
| `[WORKFLOW: <id> title="..." status=<status>\|- stages=N]` | First. |
| `[LAYOUT: work_dir=<dir>\|- unit_path=<template>\|- anchor=<file>\|-]` | The definition declares a layout. |
| `[DECLARED_CHECK: <name> class=<class> description="..."]` | One per check the definition declares. |
| `[STAGE: <id> name="..." human_gate=<gate>\|- role=<role>\|- isolation=<isolation>\|- optional=yes\|no exception=yes\|no]` | One per stage, followed by the lines of that stage: |
| `[SKIPPED: <id> reason=stages.<id>=off]` | The project switches the stage off (the same line `next` prints). |
| `[GATE: <gate> policy=<policy> answer=given policies=<a,b>]` | The stage is gated; `answer=given` and `policies` only when the definition sets them. |
| `[ENTRY: <check>...\|-]`, `[EXIT: <check>...\|-]`, `[ARTIFACTS: <path>...\|-]`, `[SKILLS: <skill>...\|-]` | The stage's lists, space-separated. |
| `[RETURNS: <to> when="..."; ...]` | The stage declares returns. |
| `[NEXT: <workflow> recommended=yes\|no when=<checks>\|-]` | After the stages, one per handoff candidate (`when` quoted when it contains a space). |

The JSON forms:

- `show --format json`: the parsed document plus `layout`, the effective `anchor`, `approvals`, `stages_off`, `ok` and `errors` (the definition's problems, with `where`). `show --unit <dir>` describes the definition the unit is bound to (else `[workflow].default`), loaded unvalidated like `show <ref>` so its problems are reported, not raised, and adds `binding` (`workflow`, `workflow_history`).
- `validate --format json`: `{"ok", "roles_checked", "definitions": [{"id", "path", "ok", "errors"}], "errors", "notices"}`. A definition's own `errors` carry `where` (`WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_CHECK_INVALID` or `ROLE_UNKNOWN`, exit `1`); the top-level `errors` hold the files that could not be loaded (`WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_ASSET_MISSING`, exit `2`) and the shared-stage differences (`SHARED_STAGE_MISMATCH`, exit `1`). `notices` hold each definition's warnings (`WORKFLOW_OPTIONAL_STAGE_UNASKED`, with `where`; they leave the definition `ok`) and `WORKFLOW_ROLES_UNCHECKED`.
- `checks --format json`: `{"checks": [...]}`, the registry: primitives and the anchor aliases.
- `list --format json`: `{"units": [{"unit", "anchor", "status", "workflow", "history", "error"}], "errors": [...]}` across every layout in use. A unit whose anchor cannot be read keeps its row with the `ANCHOR_INVALID` advisory `to_dict()` (the parser's full report) under `error`, and the same advisory is collected in the top-level `errors`; `list` still exits `0`. `--status <value>` keeps units whose anchor `status` equals a given value (repeatable) and `--exclude-status <value>` drops them; both are exact matches and nothing is excluded by default, so active units are `--exclude-status completed`.
- `handoff --format json`: `{"unit", "from", "to", "policy", "decision", "history"}`.
- `next --view requests --format json`: `{"requests": [...], "errors": [...]}`, where `errors` holds the error that stopped `lint-clean`, if any; the command exits with its exit code as `next` does. `answer` and `return` emit the written record with its `file`.
- `envelope new`, `worker`, `answer`, `resolution`, `review`, `reverify` and `check`: see `CAP-DLV-workflow-envelopes`.
