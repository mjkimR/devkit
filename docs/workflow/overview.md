# Agent Workflow Engine: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit.workflow` (`devkit workflow` CLI)  
**Related Documents**:
- [Workflow Definitions and Checks](definition-and-checks.md)
- [Rule Engine Overview](../rules/overview.md)
- [Context Loading and Playbook Discovery](../distribution/context-and-playbooks.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Problem Statement

A multi-stage delivery procedure (intent, specify, build, review, reconcile, integrate) has to be followed the same way by every coding agent a repository uses, today Claude Code and Codex, occasionally Antigravity. Two delivery models were compared:

1. **Procedure inside agent skills.** Each stage is a `SKILL.md`; the agent reads the prose and decides for itself which stage it is in by looking at files. This needs no CLI, but stage detection is prose, so hosts diverge, a changed procedure cannot be detected on in-flight work, and approval gates hold only as well as the host follows long instructions.
2. **Procedure as data, stage computed by a CLI, skills as thin entry points.** Stages, their exit conditions and their gates are declared in a workflow definition file. A CLI evaluates the conditions against the files of a work unit and prints the current stage, what is unmet and what to do next. Skills only route the agent to that output.

`devkit` implements the second model. It is the only one in which Claude Code and Codex receive the same answer from the same state. One per-agent entry skill remains necessary, because no host invokes a CLI on its own.

### Core Principles

1. **Procedure is data.** A workflow is a Markdown file whose frontmatter declares `stages[]`. The body carries prose gate rules for humans and agents; the engine never parses it.
2. **The CLI decides the stage.** `devkit workflow next` evaluates every stage's exit checks in order and reports the first unmet stage. Agents treat `[STAGE]` as the diagnosed stage rather than re-deriving it.
3. **Gates are enforced by policy, not prose.** Under the `ask` policy a stage marked `human_gate` passes only with a recorded approval (a decision record written by `devkit workflow answer` or a host UI) or an explicit `--given <gate>` for one run. The project lowers a gate to `auto` or `off` in configuration, never by editing the workflow.
4. **Drift is detected.** A work unit records the hash of the stage schema it was bound to. When the definition changes while a stage is still current, `next` refuses until the unit is rebound.
5. **Layout is a template, not a convention.** Where work units live and how their directories are named is a configured path template. The engine assumes only "a directory containing an anchor file".
6. **Agent-neutral by construction.** Definitions, CLI output and entry skills are identical bytes for every host. Only subagent role projection differs per host, and `devkit` already owns that.

---

## 2. Subsystem Layout

`devkit.workflow` is a library with a thin CLI on top. Layers, from the entry point down:

- **Library entry points** (top level). `workspace.py` (`Workspace`: configuration, definitions, roles and plugin checks loaded once and reused, unit resolution, `bind_unit`, `evaluate_unit` with the drift policy), `answers.py` (`record_answer`, `return_to`), `handoff.py` (`plan_handoff`, `apply_handoff`), `render.py` (the sentinel text lines; public library functions the CLI prints) and `errors.py` (one class per error code).
- **`definition/`.** The workflow document: `definition.py`, `validation.py`, `discovery.py`, `checks.py` (the check registry) and `ids.py`.
- **`project/`.** The project's setup: `config.py`, `layout.py`, `roles.py`, `plugins.py`.
- **`unit/`.** A work unit on disk: `units.py` (`create_unit`, `list_units`), `binding.py`, `frontmatter.py` (built on `devkit.core.frontmatter`), `decisions.py`, `records.py` (shared helpers of the numbered decision and envelope files) and `envelope/` (`model.py`, `authoring.py` with `compose_envelope`, `write_envelope`).
- **`evaluation/`.** `evaluate.py` (pure: `evaluate_definition`, `Options` in, `UnitEvaluation` out), `results.py`, `requests.py`, `primitives.py` (the disk checks), `git.py` and `lint.py` (the `devkit.rules` binding).
- **`cli/`.** `app.py` (the group and shared options), `units.py`, `run.py`, `definitions.py`, `envelope.py`.

The module map is in [the reference](reference.md#structure). The engine imports only `devkit.core`, `devkit.advisory` and `devkit.rules`.

---

## 3. Work Units and Layout

A **work unit** is one directory holding the artifacts of one piece of work: the anchor file, optional `tasks.md`, review envelopes under `envelopes/`, and whatever else the bound workflow names in `artifacts`. The engine needs two operations from a layout:

- **Create**: given a slug and a date, produce the unit directory path.
- **Discover**: list existing unit directories, identified by the presence of the anchor file.

Both come from one path template in the project configuration:

```toml
# .devkit/config.toml
[workflow]
work_dir = ".devkit/transient/work"   # root of all work units, workspace-relative
unit_path = "{slug}"                  # directory of one unit under work_dir
anchor = "task.md"                    # file that identifies a unit and carries its binding
definitions_dir = ".devkit/workflows" # where workflow definition files live
default = "direct-delivery"           # workflow id used by `new` when --workflow is omitted
```

- `unit_path` is a Python `str.format` template. Placeholders are `{slug}` and `{date}`; `{date}` accepts a `strftime` spec, for example `{date:%Y%m%d}`. A `/` inside the spec (`{date:%Y/%m}`) creates directory levels. No other syntax is introduced.
- `{slug}` is mandatory. Absolute paths, `..`, and backslashes are rejected.
- Discovery replaces each placeholder with `*` (one `*` per directory level it renders), globs under `work_dir`, and keeps directories that contain the anchor file. Nothing is parsed back out of a path; identity lives in the anchor's frontmatter.
- The `specrig` layout is expressed as `work_dir = "specs"`, `unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"`, `anchor = "spec.md"`.
- The default `work_dir` is under `.devkit/transient/`, which consumer repositories are expected to ignore in Git. Choose a tracked path instead when review envelopes and approval evidence must travel with pull requests and across machines.

`TemplateLayout` implements both operations (`new_unit`, `discover`). Plugin layouts are not supported; a template expresses every structure in use.

### Per-Definition Layout

The `[workflow]` table is the project default. A workflow definition may override any of `work_dir`, `unit_path` and `anchor` in its frontmatter `layout` mapping, so the units of different workflows can live in different places and be identified by different anchor files:

```yaml
# .devkit/workflows/incubate.md
layout:
  work_dir: docs/proposals
  unit_path: "{slug}"
  anchor: proposal.md
```

- `new --workflow incubate` creates the unit under the definition's layout and writes its anchor; `[UNIT: ...]` names the anchor.
- `list` discovers units under every distinct layout in use (the project default plus each discovered definition's) and prints the anchor per row.
- `next`, `bind`, `handoff`, `requests`, `answer`, `return` and `envelope` take a unit directory. With `--workflow`, that definition's anchor must exist there. Without it, the engine looks for the project anchor first and then every anchor a discovered definition declares: exactly one must be present. None is `UNIT_NOT_FOUND`; more than one is `ANCHOR_AMBIGUOUS`, resolved by passing `--workflow`. The binding (or the configured default) then selects the workflow, whose anchor must be the file that was found; otherwise `ANCHOR_MISMATCH` names both.
- Aliases such as `anchor-exists` resolve against the definition's own anchor, in validation and in evaluation.
- The schema hash covers stages only; changing a layout never causes drift.
- `handoff` refuses a candidate whose anchor differs from the unit's (`HANDOFF_LAYOUT_MISMATCH`). Moving a unit into another layout and renaming its anchor is the caller's job (a methodology layer such as specrig's proposal handoff); `bind --workflow <id>` then records the new binding.

### The Anchor File

The anchor is Markdown with YAML frontmatter. `devkit workflow new` writes:

```markdown
---
id: <slug>
status: planned
created: 2026-10-12
workflow: direct-delivery
workflow_hash: sha256:...
---
# <slug>
```

`status` is read by frontmatter checks and reported by `next`. `workflow` and `workflow_hash` are the binding. Binding updates replace those keys (including every line of a block-style value) and preserve every other frontmatter line and the whole body.

---

## 4. Approval Gates

A stage declares `human_gate: true` (gate named after the stage id) or `human_gate: "<gate>"` (a shared gate name such as `direction` or `integration`). Each gate is governed by project policy:

```toml
[workflow.approvals]
direction = "auto"
integration = "ask"
```

| Policy | Behavior in `next` |
| --- | --- |
| `ask` (default) | The gate is an implicit human check, asked once the stage's own exit checks hold. The stage then stays current with `[WAITING: human gate:<gate>]` and an `approve` request until the approval is recorded (or `next --given <gate>` asserts it for one run). |
| `auto` | The gate is satisfied by policy. The stage passes once its other exit checks hold; while it is current, `[GATE: <gate> policy=auto satisfied=yes source=policy]` makes the delegation visible. |
| `off` | The stage is skipped and reported as `[SKIPPED: <id> reason=approvals.<gate>=off]`. |

Under `ask`, `next` emits an `approve` request (`[REQUEST: id=gate:<gate> ...]`) and the answer is a decision record under `<unit>/decisions/` written by `devkit workflow answer` or by a host UI; `--given` remains as an assertion for the current invocation that is not stored. The CLI never infers approval from conversation. An approval belongs to the workflow segment it was given in: it does not carry over a handoff, and when `devkit workflow return` takes the unit back to an earlier stage, the approvals of that stage and later ones must be given again. `next` and the other read commands never write files: when they find an earlier stage current again, they list the approvals of later stages as `[STALE_APPROVAL: ...]` (JSON `stale_approvals`) and those approvals keep counting until a `return` is recorded. Raising a gate later is a configuration change back to `ask`; lowering it is a change to `auto` or `off`. The workflow definition does not change in either case. The request and answer formats are specified in [Human Interaction Contract](human-interaction.md).

### Stage Policy

A stage that has no gate can still be switched off by the project, by stage id:

```toml
[workflow.stages]
collect-feedback = "off"   # on (default) | off
```

`next` skips it exactly like a gated stage under `off`, reporting `[SKIPPED: <id> reason=stages.<id>=off]`, and a skipped stage never blocks completion or handoff. The stage policy is applied before the gate policy, so `stages.<id>=off` wins over `approvals.<gate>`. Stage ids match `[a-z][a-z0-9-]*` and are shared across definitions, so an id that no selected workflow uses is accepted. `show` marks the affected stages with `[SKIP: <id> reason=stages.<id>=off]` and lists them under `stages_off` in JSON.

### The `handoff` Gate

Workflows are segments: a definition's `next` list names the workflows that may continue a completed unit ([Definitions, Handoff Candidates](definition-and-checks.md#handoff-candidates)). The reserved gate name `handoff` governs who picks:

| Policy | Behavior |
| --- | --- |
| `ask` (default) | `next` lists every candidate with its eligibility and recommendation, emits a `choose` request (`id=handoff`) and reports `[WAITING: human handoff]`. The person's choice is recorded with `answer --request handoff --action accept --value <id>`, or passed as `handoff --workflow <id>`, which records the same decision; the choice must be an eligible candidate. |
| `auto` | The first candidate whose `when` checks all hold is `chosen=`; `handoff --unit DIR` rebinds to it without a choice. With no eligible candidate the engine waits for a person, and `handoff` without `--workflow` fails with `HANDOFF_UNDECIDED`. |
| `off` | No handoff is offered; the unit is finished when its workflow completes. |

`handoff` records the finished segment in the anchor's `workflow_history` (with the highest decision sequence number at that moment) and binds the unit to the chosen workflow, whose stages are then evaluated from the start against the same unit directory. Decision records of finished segments never count again.

---

## 5. CLI Surface

```bash
devkit workflow new <slug> [--workflow ID] [--date YYYY-MM-DD] [--status S]   # create a unit from the layout template and bind it
devkit workflow bind --unit DIR [--workflow ID]                  # record or refresh the binding (accepts drift)
devkit workflow next --unit DIR [--workflow ID] [--given NAME]... [--no-lint] [--format text|json]
devkit workflow handoff --unit DIR [--workflow ID] [--date YYYY-MM-DD] [--by NAME] [--no-lint] [--format text|json]
devkit workflow requests --unit DIR [--no-lint] [--format text|json]   # open human requests of a unit
devkit workflow answer --unit DIR --request ID --action ACTION [--value V] [--note TEXT] [--by NAME] [--no-lint] [--format text|json]
devkit workflow return --unit DIR --to STAGE [--note TEXT] [--by NAME] [--no-lint] [--format text|json]  # go back; later approvals are asked again
devkit workflow show <ID|PATH> [--format text|json]              # print a definition's stages, hash and next candidates
devkit workflow show --unit DIR [--format text|json]             # the unit's bound definition plus [BINDING: ... drift=bool]
devkit workflow checks [--format text|json]                      # registered check names, classes and parameters (plugins included)
devkit workflow validate [PATH]... [--format text|json]          # validate definitions (default: both sources, plus roles and shared stages)
devkit workflow list [--status S]... [--exclude-status S]... [--format text|json]  # discovered units across every layout
devkit workflow envelope new --unit DIR --kind KIND [--stage ID] [--format text|json]  # write the next envelopes/<kind>-NN.yaml skeleton
devkit workflow envelope new --unit DIR --kind KIND [--status S] [--summary TEXT] [--assume TEXT]... [--unverified TEXT]...
                            [--check NAME=PASS|FAIL|SKIP[ detail]]... [--base REV] [--head REV] [--findings-file PATH|-]
                            [--from latest|FILE] [--resolve N|all]... [--waive N=REASON]...   # write it complete
devkit workflow envelope check --unit DIR [--format text|json]   # every envelope file and any contract violation
```

All commands accept `-w/--workspace-root`; it defaults to the devkit project containing the current directory, and an explicit value that is not an existing directory is `ARGUMENT_INVALID`. Exit codes follow the devkit convention ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)):

| Exit | When |
| --- | --- |
| `0` | The command did its job. `next` exits `0` whatever the stage, including a unit that waits for a person (`[WAITING]`, `[REQUEST]`), a delegation (`[DELEGATE]`) or a handoff choice. |
| `1` | The command ran and reports a negative result: `validate` found invalid definitions or shared-stage differences (a definition file that cannot be loaded at all makes it exit `2`), `show` found problems in the definition, `envelope check` found malformed envelope files (`ENVELOPE_INVALID`), or `next` refused a unit whose bound stage schema changed (`WORKFLOW_DRIFT`). |
| `2` | The command could not do its job: a usage error from the command line parser, an argument error (`ARGUMENT_INVALID`: a `-w` or `validate` path that does not exist, a malformed `--date`, `show` given both or neither of `REF` and `--unit`), and every other error code below (unreadable configuration, receipt, definition or anchor, a refused input, a lint run that could not execute, an unexpected error). |

A command that collects several problems (`validate`, `envelope check`) exits with the highest exit code among them. `show` only reports, so it exits `1` when its report lists any problem, whatever the problem's own code, and `2` only when it cannot run (an unknown workflow, an unreadable definition or configuration).

Errors are reported on stderr as Agent Advisory Protocol blocks from the `devkit.advisory` module, with a stable code and an `[ACTION]` directive, so an agent knows whether to fix input, stop for a person, or respect a guardrail. Under `--format json` stdout carries exactly one JSON object, never a bare array: the command's result (`list` as `{"units": [...]}`, `checks` as `{"checks": [...]}`, `requests` as `{"requests": [...]}`), or `{"error": {...}}` when it has none. Problems a command collects rather than raises are listed in its result under `errors`, each the `to_dict()` of an advisory error (`code`, `message`, `exit_code`, `advisory`, plus `file` or `where` when the problem has one). A `next` whose lint run failed prints its result (the `devkit.rules` error among its `errors`) and reports that same error on stderr; `envelope check` reports each `ENVELOPE_INVALID` file the same way.

The library raises the same codes, one class per code. `WorkflowError` is the base: it sets the actor and retry once, and each subclass adds its code and mode. Errors of `devkit.core` (`CONFIG_INVALID`, `RECEIPT_INVALID`, `GIT_FAILED`, ...) and of `devkit.rules` (from `lint-clean`) pass through unchanged.

| Code | Class | Mode | Exit | Raised when |
| --- | --- | --- | --- | --- |
| `CONFIG_INVALID` | `devkit.core` `ConfigError` | `INPUT_ERROR` | `2` | `.devkit/config.toml` cannot be read or parsed (passed through unchanged) |
| `WORKFLOW_CONFIG_INVALID` | `WorkflowConfigError` | `INPUT_ERROR` | `2` | the `[workflow]`, `[workflow.approvals]` or `[workflow.stages]` table is malformed (a subclass of the `devkit.core` `ConfigError`) |
| `ARGUMENT_INVALID` | `devkit.core` `ArgumentError` | `INPUT_ERROR` | `2` | `-w/--workspace-root` or a `validate` path does not exist, `--date` is not `YYYY-MM-DD`, or `show` is given both or neither of `REF` and `--unit` |
| `WORKFLOW_NOT_SELECTED`, `WORKFLOW_NOT_FOUND`, `WORKFLOW_INVALID` | `WorkflowNotSelectedError`, `WorkflowNotFoundError`, `WorkflowInvalidError` | `INPUT_ERROR` | `2` | no definition chosen, no id or file matches, or the chosen one fails validation (problems become `[DETAIL]` lines) |
| `WORKFLOW_DEFINITION_INVALID` | `DefinitionError` | `INPUT_ERROR` | `2` | a definition file cannot be read or parsed (`parse_definition`, `load_definition`), or an id is defined twice; `validate` collects it as a load error |
| `WORKFLOW_DEFINITION_INVALID`, `WORKFLOW_CHECK_INVALID`, `ROLE_UNKNOWN` | `DefinitionProblem`, `CheckReferenceProblem`, `RoleUnknownProblem` | `INPUT_ERROR` | `1` | collected by validation with `where` (`<stage>.<field>`): a problem in a loaded definition, a check reference that does not resolve, a role outside the vocabulary |
| `SHARED_STAGE_MISMATCH` | `SharedStageMismatchError` | `INPUT_ERROR` | `1` | collected by a whole-workspace `validate`: stages that share an id but differ |
| `WORKFLOW_ASSET_MISSING` | `WorkflowAssetMissingError` | `AUTO` | `2` | collected by discovery: a receipt-listed definition is missing from disk; `[FIX]` is `devkit sync` |
| `WORKFLOW_CHECK_INVALID` | `CheckError` | `INPUT_ERROR` | `2` | a check reference is malformed, unregistered or collides (`parse_check`, `Registry`) |
| `WORKFLOW_CHECK_LOAD_FAILED` | `PluginError` | `MAINTENANCE` | `2` | a plugin check file failed to load, declares an invalid check, or a receipt `workflow-check` file is missing, unsafe or differs from its recorded hash (`[FIX]`: `devkit sync`, or `devkit override create` to keep an edit) |
| `LAYOUT_INVALID`, `SLUG_INVALID` | `LayoutError`, `SlugError` | `INPUT_ERROR` | `2` | a layout template, directory or anchor file name is malformed (`validate_template`, `parse_layout_spec`; inside `[workflow]` it is `WORKFLOW_CONFIG_INVALID`); a unit slug does not match `[a-z0-9][a-z0-9-]*` |
| `UNIT_NOT_FOUND`, `UNIT_EXISTS`, `ANCHOR_INVALID` | `UnitNotFoundError`, `UnitExistsError`, `AnchorInvalidError` | `INPUT_ERROR` | `2` | the unit directory has no anchor, already exists, or its frontmatter is unreadable (`list` reports the last one per unit under `error`) |
| `ANCHOR_AMBIGUOUS`, `ANCHOR_MISMATCH` | `AnchorAmbiguousError`, `AnchorMismatchError` | `INPUT_ERROR` | `2` | several candidate anchor files exist in the unit (pass `--workflow`); the selected workflow declares a different anchor than the file that identifies the unit |
| `GIVEN_INVALID` | `GivenInvalidError` | `INPUT_ERROR` | `2` | a `--given` name is neither a gate nor a registered runner or human check |
| `WORKFLOW_DRIFT` | `DriftError` | `BLOCKED` | `1` | the bound schema hash changed under in-flight work; `[FIX]` names the `bind` command |
| `REQUEST_UNKNOWN`, `DECISION_INVALID` | `RequestUnknownError`, `DecisionInvalidError` | `INPUT_ERROR` | `2` | `answer` names a request that is not open, or an action/value that does not fit it (see [Human Interaction Contract](human-interaction.md)) |
| `DECISION_RECORD_INVALID`, `HANDOFF_CHOICE_IGNORED` | `DecisionRecordError`, `HandoffChoiceIgnoredError` | `INPUT_ERROR` | `2` | collected with `file`: a decision record does not match the format (`parse_record`, `load_decisions`); a recorded handoff choice is not an eligible candidate and is ignored |
| `RETURN_INVALID` | `ReturnInvalidError` | `INPUT_ERROR` | `2` | `return --to` names no stage of the workflow, or one after the current stage |
| `HANDOFF_NOT_READY`, `HANDOFF_NONE`, `HANDOFF_OFF` | `HandoffNotReadyError`, `HandoffNoneError`, `HandoffOffError` | `INPUT_ERROR` | `2` | the unit's workflow is not complete, declares no `next`, or handoff is disabled by policy |
| `HANDOFF_CHOICE_REQUIRED` | `HandoffChoiceRequiredError` | `INTERACTION` | `2` | under `ask` a person must choose the next workflow; `[FIX]` is the `answer` command to run once they have (details list the candidates) |
| `HANDOFF_UNDECIDED`, `HANDOFF_INVALID`, `HANDOFF_INELIGIBLE` | `HandoffUndecidedError`, `HandoffInvalidError`, `HandoffIneligibleError` | `INPUT_ERROR` | `2` | `auto` found no eligible candidate; the choice is not a candidate, or its `when` checks fail |
| `HANDOFF_LAYOUT_MISMATCH` | `HandoffLayoutMismatchError` | `INPUT_ERROR` | `2` | the chosen candidate's anchor differs from the unit's; relocate the unit, then `bind` |
| `ENVELOPE_STATUS_INVALID`, `ENVELOPE_FLAG_INVALID`, `ENVELOPE_FROM_INVALID`, `ENVELOPE_FINDINGS_INVALID` | `EnvelopeStatusError`, `EnvelopeFlagError`, `EnvelopeFromError`, `EnvelopeFindingsError` (base `AuthoringError`) | `INPUT_ERROR` | `2` | `envelope new` authoring flags that cannot produce a valid envelope; a `--resolve`/`--waive` number outside the carried findings is `ENVELOPE_FLAG_INVALID` |
| `ENVELOPE_KIND_INVALID` | `EnvelopeKindError` | `INPUT_ERROR` | `2` | an envelope kind does not match `[a-z][a-z0-9-]*` (`write_envelope`) |
| `ENVELOPE_INVALID` | `EnvelopeFormatError` | `INPUT_ERROR` | `1` | collected with `file` by `load_envelopes`: a malformed envelope file; `envelope check` reports each one with its `[TARGET]` |
| `RECEIPT_INVALID` | `devkit.core` `ReceiptError` | `MAINTENANCE` | `2` | `.devkit/installation.json` exists but does not match its schema; restore it from version control, then run `devkit sync` |
| `GIT_FAILED` | `devkit.core` `GitError` | `MAINTENANCE` | `2` | `is_ancestor` cannot answer, or is given a non-hexadecimal revision (`INPUT_ERROR`) |

Output contracts are specified in [Workflow Definitions and Checks, section 5](definition-and-checks.md#5-output-signals); the request and decision formats in [Human Interaction Contract](human-interaction.md).

---

## 6. Integration with the Rule Engine and Distribution

- **Lint check.** The `lint-clean` check runs `devkit.rules` in the `linter` phase on the files of the work unit, honoring the project's `[rules]` policy (phase and severity overrides, typed settings, `exclude`) through `run_project_rules`, the entry point `devkit rules check` uses, and loading the rules that `devkit sync` recorded in the installation receipt. Violations are reported in the check detail; a rule execution or loading error fails the command.
- **Workflow definitions as assets.** A bundle declares `kind = "workflow"` assets (one Markdown definition each). `devkit sync` places them under `.devkit/managed/<bundle>/` and records their paths in the installation receipt under `entrypoints`. The engine discovers definitions from two sources: the project's `definitions_dir`, and every workflow asset in `.devkit/installation.json`. A project definition with the same `id` shadows the synchronized one, so a repository can adapt a distributed workflow without editing managed files. `devkit workflow validate` with no arguments covers both sources.
- **Entry skill.** When at least one workflow asset is synchronized, `devkit sync` generates the shared `devkit-workflow` skill and projects it into every selected agent's skill directory, exactly as it does for `devkit-playbook`. The skill tells the agent to run `devkit workflow next --unit <dir>`, treat `[STAGE]` as the diagnosed stage, open the skill named by `[NEXT_SKILL]`, record an approval with `devkit workflow answer` only after the user's explicit answer, take a `[RETURNS]` path with `devkit workflow return`, and on `[HANDOFF]` present the candidates and run `handoff` only after the user's choice (or immediately under `policy=auto`). It is identical for every host; Codex gets `allow_implicit_invocation: true` because the agent should pick it up whenever a task follows a workflow. Repositories that use no workflow never see the skill.
- **Subagent delegation.** `[DELEGATE: role=<role> isolation=<level> contract=<path>]` names a role and the contract that defines it. A bundle ships the role as a `kind = "subagent"` asset, either as native files per agent or as one host-neutral role contract that `devkit sync` renders for each selected agent (see [Agent Projections](../distribution/agent-projections.md)). The engine reads the receipt's `subagent` assets (asset id, plus the `role` a managed contract declares) and the project's `[workflow] roles_dir` (`<role>.md`, shadowing the receipt) as the role vocabulary: `validate` rejects a stage role outside it, and `[DELEGATE]` cites the managed or overridden contract, else the first projected file. With no receipt and no `roles_dir` the check is skipped with a `[NOTICE]`.
- **Plugin checks.** A bundle may ship check evaluators as Python files under a `kind = "workflow-check"` asset. The project may also drop files under `[workflow] checks_dir`. Each file defines `BaseCheck` subclasses with `name`, `description`, `params` and `evaluate(ctx)`; they register with class `plugin` and are referenced from definitions like primitives. See [Workflow Definitions and Checks, Plugin Checks](definition-and-checks.md#plugin-checks).

---

## 7. Relationship to specrig

The stage schema, check classes, evaluation loop, binding hash, envelope file contract and sentinel output are ported from `specrig`'s `cli/internal/workflow` package. specrig embeds the engine through the `devkit.workflow` library (`Workspace`, `evaluate_unit`, the structured `UnitEvaluation`) rather than parsing CLI output. These things were generalized:

| specrig | devkit |
| --- | --- |
| `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/spec.md` hard-coded; proposals under `docs/proposals/` handled by separate commands | `[workflow]` layout template and anchor name as the default, overridable per definition (`layout`), so proposal and spec bundles are units of different workflows in one repository |
| `lint-clean` bound to the specrig rule engine | bound to `devkit.rules` |
| `feedback.sweep=off` as the only policy skip | gate policy `off` skips any gated stage; `[workflow.stages]` turns any stage off by id |
| `human_gate: true` interpreted by skill prose | `[workflow.approvals]` enforced by the CLI with `ask`, `auto`, `off` |
| `workflow envelope new` with authoring flags and `envelope check` | same flag surface (`--status`, `--summary`, `--assume`, `--unverified`, `--check`, `--base`, `--head`, `--findings-file`, `--from`, `--resolve`, `--waive`) and `envelope check`; plain `envelope new` still writes a `needs_input` skeleton |
| role vocabulary validated against `.specrig/subagents/<role>.md`; `[DELEGATE]` prints the contract path | validated against receipt `subagent` assets plus `[workflow] roles_dir`; `[DELEGATE]` prints `contract=` |
| own evaluators (`materials-present`, `envelope-final-report-present`) compiled into the Go binary | plugin checks loaded from `kind = "workflow-check"` assets or `checks_dir` |
| `RULE-workflow-shared-stage` lint rule | `validate` reports differing shared stages across definitions |
| `workflow show --spec <dir>` | `show --unit <dir>` with `[BINDING]` |
| `list spec` excludes completed specs by default | `list --exclude-status completed` (exact-match filters, no default exclusion) |

Proposal handoff as relocation (moving a bundle from `docs/proposals/` to `specs/` with link rewriting), worktree commands, the scope registry and the feedback counter are specrig methodology and are not part of this engine. The engine provides the layout, binding, role, plugin-check and skip primitives such a layer needs.
