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

- **Library entry points.** `workspace.py` (`Workspace`: configuration, definitions, roles, plugin checks, unit resolution, `evaluate_unit` with the drift policy), `units.py` (`create_unit`, `list_units`), `answers.py` (`record_answer`, `return_to`), `handoff.py` (`plan_handoff`, `apply_handoff`) and `envelope/` (`compose`, `write_next`).
- **Evaluation.** `evaluate.py` (pure: `Options` in, `Result` out), `results.py`, `requests.py`, `primitives.py` (the disk checks), `checks.py` (the registry), `plugins.py`, `lint.py` (the `devkit.rules` binding) and `git.py`.
- **Documents and records.** `definition.py`, `validation.py`, `discovery.py`, `decisions.py`, `binding.py`, `envelope/model.py`, `config.py`, `layout.py`, `roles.py`, `frontmatter.py` (built on `devkit.core.frontmatter`), `ids.py`, `errors.py`.
- **CLI.** `cli/` (`app.py` with the error boundary, `units.py`, `run.py`, `definitions.py`, `envelope.py`).

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

All commands accept `-w/--workspace-root`; it defaults to the devkit project containing the current directory. Exit codes follow the devkit convention ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)):

| Exit | When |
| --- | --- |
| `0` | The command did its job. `next` exits `0` whatever the stage, including a unit that waits for a person (`[WAITING]`, `[REQUEST]`), a delegation (`[DELEGATE]`) or a handoff choice. |
| `1` | The command ran and reports a negative result: `validate` found invalid definitions or shared-stage differences, `show` found problems in the definition, `envelope check` found malformed envelope files (`ENVELOPE_INVALID`), or `next` refused a unit whose bound stage schema changed (`WORKFLOW_DRIFT`). |
| `2` | The command could not do its job: a usage error from the command line parser, and every other error code below (unreadable configuration, receipt, definition or anchor, a refused input, a lint run that could not execute, an unexpected error). |

Errors are reported on stderr as Agent Advisory Protocol blocks from the `devkit.advisory` module, with a stable code and an `[ACTION]` directive, so an agent knows whether to fix input, stop for a person, or respect a guardrail. Under `--format json` stdout carries exactly one JSON document: the command's result, or `{"error": {...}}` when it has none. A `next` whose lint run failed prints its result (with `lint_error`) and reports `LINT_FAILED` on stderr only; `envelope check` does the same with `ENVELOPE_INVALID`. The library raises the same codes: `WorkflowError` and its subclasses (`ConfigError`, `DefinitionError`, `LayoutError`, `CheckError`, `PluginError`, `DriftError`, ...), plus the `devkit.core` errors it passes through unchanged (`RECEIPT_INVALID`, `GIT_FAILED`).

| Code | Mode | Exit | Raised when |
| --- | --- | --- | --- |
| `CONFIG_INVALID` | `INPUT_ERROR` | `2` | `.devkit/config.toml` cannot be parsed or its `[workflow]` tables are malformed (`ConfigError`, also a `devkit.core` `ConfigError`) |
| `WORKFLOW_NOT_SELECTED`, `WORKFLOW_NOT_FOUND`, `WORKFLOW_INVALID` | `INPUT_ERROR` | `2` | no definition chosen, none matches, or the chosen one fails validation (problems become `[DETAIL]` lines) |
| `UNIT_NOT_FOUND`, `UNIT_EXISTS`, `ANCHOR_INVALID` | `INPUT_ERROR` | `2` | the unit directory has no anchor, already exists, or its frontmatter is unreadable |
| `ANCHOR_AMBIGUOUS`, `ANCHOR_MISMATCH` | `INPUT_ERROR` | `2` | several candidate anchor files exist in the unit (pass `--workflow`); the selected workflow declares a different anchor than the file that identifies the unit |
| `HANDOFF_LAYOUT_MISMATCH` | `INPUT_ERROR` | `2` | the chosen candidate's anchor differs from the unit's; relocate the unit, then `bind` |
| `ENVELOPE_STATUS_INVALID`, `ENVELOPE_FLAG_INVALID`, `ENVELOPE_FROM_INVALID`, `ENVELOPE_FINDINGS_INVALID` | `INPUT_ERROR` | `2` | `envelope new` authoring flags that cannot produce a valid envelope (details name the flag) |
| `ENVELOPE_INVALID` | `INPUT_ERROR` | `1` | `envelope check` found malformed envelope files; `[DETAIL]` lines carry file and reason, `[TARGET]` the files. The library's `EnvelopeFormatError` (a malformed finding or list) and every collected `EnvelopeError` entry carry the same code |
| `SLUG_INVALID`, `DATE_INVALID`, `GIVEN_INVALID`, `KIND_INVALID` | `INPUT_ERROR` | `2` | a flag or argument is malformed |
| `HANDOFF_NOT_READY`, `HANDOFF_NONE`, `HANDOFF_OFF` | `INPUT_ERROR` | `2` | the unit's workflow is not complete, declares no `next`, or handoff is disabled by policy |
| `HANDOFF_CHOICE_REQUIRED`, `HANDOFF_UNDECIDED`, `HANDOFF_INVALID`, `HANDOFF_INELIGIBLE` | `INPUT_ERROR` | `2` | `ask` needs a recorded choice or `--workflow`; `auto` found no eligible candidate; the choice is not a candidate, or its `when` checks fail (details list the candidates) |
| `REQUEST_UNKNOWN`, `DECISION_INVALID` | `INPUT_ERROR` | `2` | `answer` names a request that is not open, or an action/value that does not fit it (see [Human Interaction Contract](human-interaction.md)) |
| `RETURN_INVALID` | `INPUT_ERROR` | `2` | `return --to` names no stage of the workflow, or one after the current stage |
| `WORKFLOW_DRIFT` | `BLOCKED` | `1` | the bound schema hash changed under in-flight work; `[FIX]` names the `bind` command |
| `LINT_FAILED` | `MAINTENANCE` | `2` | `devkit.rules` raised a rule loading or execution error during `lint-clean` |
| `CHECK_LOAD_FAILED` | `MAINTENANCE` | `2` | a plugin check file failed to load, declares an invalid check (`PluginError`), or a receipt `workflow-check` file is missing, unsafe or differs from its recorded hash (`[FIX]`: `devkit sync`, or `devkit override create` to keep an edit) |
| `RECEIPT_INVALID` | `MAINTENANCE` | `2` | `.devkit/installation.json` exists but does not match its schema (`devkit.core` `ReceiptError`); restore it from version control, then run `devkit sync` |

Library calls that the CLI wraps with a more specific code raise these directly; their messages name the offending key or file:

| Code | Class | Raised when |
| --- | --- | --- |
| `DEFINITION_INVALID` | `DefinitionError` | a definition file cannot be read or parsed (`parse`, `load`); `resolve`/`find` name no or several definitions (the CLI reports `WORKFLOW_NOT_FOUND`) |
| `LAYOUT_INVALID` | `LayoutError` | a layout template, slug, directory or anchor file name is malformed (`validate_template`, `parse_layout_spec`, `TemplateLayout.new_unit`); the CLI reports `SLUG_INVALID` or `CONFIG_INVALID` |
| `CHECK_INVALID` | `CheckError` | a check reference is malformed, unregistered or collides (`parse_check`, `Registry`); validation reports it as a problem |
| `ROLE_UNKNOWN`, `SHARED_STAGE_MISMATCH`, `WORKFLOW_ASSET_MISSING` | collected entries | validation `Problem` for a role outside the vocabulary; `WorkflowProblem` for stages that share an id but differ, and for a receipt-listed definition missing from disk |
| `DECISION_RECORD_INVALID` | `DecisionRecordError` | a decision record file does not match the format (`parse_record`); `load_decisions` collects it as a `DecisionError` entry with this code |
| `GIT_FAILED` | `devkit.core` `GitError` | `is_ancestor` cannot answer, or is given a non-hexadecimal revision (`INPUT_ERROR`) |

Output contracts are specified in [Workflow Definitions and Checks, section 5](definition-and-checks.md#5-output-signals); the request and decision formats in [Human Interaction Contract](human-interaction.md).

---

## 6. Integration with the Rule Engine and Distribution

- **Lint check.** The `lint-clean` check runs `devkit.rules` in the `linter` phase on the files of the work unit, honoring the project's `[rules]` policy (phase and severity overrides, typed settings, `exclude`) through `run_project_rules`, the entry point `devkit rules check` uses, and loading the rules that `devkit sync` recorded in the installation receipt. Violations are reported in the check detail; a rule execution or loading error fails the command.
- **Workflow definitions as assets.** A bundle declares `kind = "workflow"` assets (one Markdown definition each). `devkit sync` places them under `.devkit/managed/<bundle>/` and records their paths in the installation receipt under `entrypoints`. The engine discovers definitions from two sources: the project's `definitions_dir`, and every workflow asset in `.devkit/installation.json`. A project definition with the same `id` shadows the synchronized one, so a repository can adapt a distributed workflow without editing managed files. `devkit workflow validate` with no arguments covers both sources.
- **Entry skill.** When at least one workflow asset is synchronized, `devkit sync` generates the shared `devkit-workflow` skill and projects it into every selected agent's skill directory, exactly as it does for `devkit-playbook`. The skill tells the agent to run `devkit workflow next --unit <dir>`, treat `[STAGE]` as the diagnosed stage, open the skill named by `[NEXT_SKILL]`, record an approval with `devkit workflow answer` only after the user's explicit answer, take a `[RETURNS]` path with `devkit workflow return`, and on `[HANDOFF]` present the candidates and run `handoff` only after the user's choice (or immediately under `policy=auto`). It is identical for every host; Codex gets `allow_implicit_invocation: true` because the agent should pick it up whenever a task follows a workflow. Repositories that use no workflow never see the skill.
- **Subagent delegation.** `[DELEGATE: role=<role> isolation=<level> contract=<path>]` names a role and the contract that defines it. A bundle ships the role as a `kind = "subagent"` asset, either as native files per agent or as one host-neutral role contract that `devkit sync` renders for each selected agent (see [Agent Projections](../distribution/agent-projections.md)). The engine reads the receipt's `subagent` assets (asset id, plus the `role` a managed contract declares) and the project's `[workflow] roles_dir` (`<role>.md`, shadowing the receipt) as the role vocabulary: `validate` rejects a stage role outside it, and `[DELEGATE]` cites the managed or overridden contract, else the first projected file. With no receipt and no `roles_dir` the check is skipped with a `[NOTE]`.
- **Plugin checks.** A bundle may ship check evaluators as Python files under a `kind = "workflow-check"` asset. The project may also drop files under `[workflow] checks_dir`. Each file defines `BaseCheck` subclasses with `name`, `description`, `params` and `evaluate(ctx)`; they register with class `plugin` and are referenced from definitions like primitives. See [Workflow Definitions and Checks, Plugin Checks](definition-and-checks.md#plugin-checks).

---

## 7. Relationship to specrig

The stage schema, check classes, evaluation loop, binding hash, envelope file contract and sentinel output are ported from `specrig`'s `cli/internal/workflow` package. specrig embeds the engine through the `devkit.workflow` library (`Workspace`, `evaluate_unit`, the structured `Result`) rather than parsing CLI output. These things were generalized:

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
