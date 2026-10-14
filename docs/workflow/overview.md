# Agent Workflow Engine: Architecture Overview

**Package**: `devkit.workflow` (`devkit workflow` CLI). Commands, exit codes, error codes and output: [CLI and Output Contract](cli-and-output.md).  
**Related**: [Workflow Definitions and Checks](definition-and-checks.md), [Rule Engine Overview](../rules/overview.md), [Context Loading and Playbook Discovery](../distribution/context-and-playbooks.md).

## 1. Delivery Model

A multi-stage delivery procedure (intent, specify, build, review, reconcile, integrate) must be followed the same way by every coding agent a repository uses. `devkit` keeps the procedure as data, computes the stage with a CLI and leaves skills as thin entry points: stages, exit conditions and gates are declared in a workflow definition, and the CLI evaluates them against the files of a work unit and prints the current stage, what is unmet and what to do next. Procedure written into skill prose leaves stage detection to each host, cannot detect a changed procedure on in-flight work, and holds gates only as well as the host follows long instructions. One per-agent entry skill remains necessary, because no host invokes a CLI on its own.

1. **Procedure is data.** A workflow is a Markdown file whose frontmatter declares `stages[]`. The body carries prose gate rules; the engine never parses it.
2. **The CLI decides the stage.** `devkit workflow next` evaluates every stage's exit checks in order and reports the first unmet stage. Agents treat `[STAGE]` as the diagnosed stage rather than re-deriving it.
3. **Gates are enforced by policy, not prose.** Under `ask` a gated stage passes only with a recorded approval or an explicit `--given <gate>` for one run. The project lowers a gate in configuration, never by editing the workflow.
4. **Drift is detected.** A work unit records the hash of the stage schema it was bound to; when the definition changes while a stage is still current, `next` refuses until the unit is rebound.
5. **Layout is a template.** Where work units live and how their directories are named is a configured path template; the engine assumes only "a directory containing an anchor file".
6. **Agent-neutral.** Definitions, CLI output and entry skills are identical bytes for every host. Only subagent role projection differs per host, and `devkit.distribution` owns that.

The engine is a library with a thin CLI on top and imports only `devkit.core`, `devkit.advisory` and `devkit.rules`; the module map is in [the reference](reference.md#structure).

## 2. Work Units and Layout

A **work unit** is one directory holding the artifacts of one piece of work: the anchor file, optional `tasks.md`, review envelopes under `envelopes/`, decision records under `decisions/`, and whatever else the bound workflow names in `artifacts`. One path template in the project configuration both creates a unit directory from a slug and a date and discovers existing ones:

```toml
# .devkit/config.toml
[workflow]
work_dir = ".devkit/transient/work"   # root of all work units, workspace-relative
unit_path = "{slug}"                  # directory of one unit under work_dir
anchor = "task.md"                    # file that identifies a unit and carries its binding
definitions_dir = ".devkit/workflows" # where workflow definition files live
default = "direct-delivery"           # workflow id used by `new` when --workflow is omitted, and for unbound units
```

- `unit_path` is a Python `str.format` template with the placeholders `{slug}` and `{date}`; `{date}` accepts a `strftime` spec such as `{date:%Y%m%d}`, and a `/` inside the spec (`{date:%Y/%m}`) creates directory levels. `{slug}` is mandatory. Absolute paths, `..` and backslashes are rejected, also when a `{date}` spec would render them (`{date:/abs/%Y}`); `new` refuses a unit directory that resolves outside `work_dir` through a symbolic link (`LAYOUT_INVALID`).
- Discovery replaces each placeholder with `*` (one per directory level it renders), globs under `work_dir` and keeps directories that contain the anchor file. Nothing is parsed back out of a path; identity lives in the anchor's frontmatter.
- specrig's layout, for example, is `work_dir = "specs"`, `unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"`, `anchor = "spec.md"`.
- The default `work_dir` is under `.devkit/transient/`, which consumer repositories are expected to ignore in Git. Choose a tracked path when review envelopes and approval evidence must travel with pull requests and across machines.

`TemplateLayout` (`new_unit`, `discover`) is the only layout; plugin layouts are not supported.

### Per-Definition Layout

A workflow definition may override any of `work_dir`, `unit_path` and `anchor` in its frontmatter `layout` mapping, so the units of different workflows (proposal bundles under `docs/proposals/`, spec bundles under `specs/`) live in different places and are identified by different anchor files:

```yaml
# .devkit/workflows/incubate.md
layout:
  work_dir: docs/proposals
  unit_path: "{slug}"
  anchor: proposal.md
```

- `new --workflow incubate` creates the unit under the definition's layout and writes its anchor; `[UNIT: ...]` names the anchor.
- `list` discovers units under every distinct layout in use (the project default plus each discovered definition's) and prints the anchor per row.
- `next`, `bind`, `handoff`, `requests`, `answer`, `return`, `show --unit` and `envelope` take a unit directory. With `--workflow` (`next`, `bind`), that definition's anchor must exist there. Without it, the engine looks for the project anchor and then every anchor a discovered definition declares: exactly one must be present. None is `UNIT_NOT_FOUND`; more than one is `ANCHOR_AMBIGUOUS`, resolved by passing `--anchor FILE` (every command above except `envelope check`, which only needs some anchor to be present). The binding (or the configured default) then selects the workflow, whose anchor must be the file that was found; otherwise `ANCHOR_MISMATCH` names both, and its fix is renaming the anchor or `bind --workflow <id>` with a workflow whose anchor is the found file.
- Aliases such as `anchor-exists` resolve against the definition's own anchor, in validation and in evaluation. Changing a layout never causes drift.
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

`status` is read by frontmatter checks and reported by `next`. `workflow` and `workflow_hash` are the binding ([Binding and Drift](definition-and-checks.md#3-binding-and-drift)).

## 3. Approval Gates

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

Under `ask` the answer is a decision record under `<unit>/decisions/`, written by `devkit workflow answer` or by a host UI; `--given` is an assertion for the current invocation and is not stored. The CLI never infers approval from conversation. An approval belongs to the workflow segment and the stage it was given in (a gate shared by two stages is asked in each), and a `return` to an earlier stage voids the approvals of that stage and later ones ([Human Interaction Contract](human-interaction.md#5-how-the-engine-applies-answers)). Raising or lowering a gate is a change to this table only; the workflow definition does not change.

### Stage Policy

A stage, gated or not, can be switched off by the project by stage id:

```toml
[workflow.stages]
collect-feedback = "off"   # on (default) | off
```

The stage policy is applied before any check or gate is evaluated, so `stages.<id>=off` wins over `approvals.<gate>`. `next` reports `[SKIPPED: <id> reason=stages.<id>=off]`, and a skipped stage never blocks completion or handoff. Stage ids match `[a-z][a-z0-9-]*` and are shared across definitions, so an id that no selected workflow uses is accepted. `show` marks the affected stages with `[SKIP: <id> reason=stages.<id>=off]` and lists them under `stages_off` in JSON.

### The `handoff` Gate

Workflows are segments: a definition's `next` list names the workflows that may continue a completed unit ([Handoff Candidates](definition-and-checks.md#handoff-candidates)). The reserved gate name `handoff` governs who picks:

| Policy | Behavior |
| --- | --- |
| `ask` (default) | `next` lists every candidate with its eligibility and recommendation, emits a `choose` request (`id=handoff`) and reports `[WAITING: human handoff]`. The person's choice is recorded with `answer --request handoff --action accept --value <id>`, or passed as `handoff --workflow <id>`, which records the same decision; the choice must be an eligible candidate. |
| `auto` | The first candidate whose `when` checks all hold is `chosen=`; `handoff --unit DIR` rebinds to it without a choice. With no eligible candidate the engine waits for a person, and `handoff` without `--workflow` fails with `HANDOFF_UNDECIDED`. |
| `off` | No handoff is offered; the unit is finished when its workflow completes. |

`handoff` records the finished segment in the anchor's `workflow_history` and binds the unit to the chosen workflow, whose stages are then evaluated from the start against the same unit directory. Decision records and envelopes of finished segments never count again.

## 4. Integration with the Rule Engine and Distribution

- **Lint check.** `lint-clean` runs `devkit.rules` in the `linter` phase on the files of the work unit through `run_project_rules` (the entry point of `devkit rules check`), honoring the project's `[rules]` policy (phase and severity overrides, typed settings, `exclude`) and the rules `devkit sync` recorded in the installation receipt. Violations are reported in the check detail; a rule execution or loading error fails the command.
- **Definitions as assets.** A bundle declares `kind = "workflow"` assets (one Markdown definition each); `devkit sync` places them under `.devkit/managed/<bundle>/` and records them in the receipt under `entrypoints`. Definitions are discovered from the project's `definitions_dir` and from every workflow asset in `.devkit/installation.json`; a project definition with the same `id` shadows the synchronized one, so a repository adapts a distributed workflow without editing managed files. A recorded definition missing from disk is `WORKFLOW_ASSET_MISSING` (run `devkit sync`); a malformed receipt is `RECEIPT_INVALID`.
- **Entry skill.** When at least one workflow asset is synchronized, `devkit sync` generates the shared `devkit-workflow` skill and projects it into every selected agent's skill directory, as it does `devkit-playbook`. The skill tells the agent to run `devkit workflow next --unit <dir>`, treat `[STAGE]` as the diagnosed stage, open the skill named by `[NEXT_SKILL]`, record an approval with `devkit workflow answer` only after the user's explicit answer, take a `[RETURNS]` path with `devkit workflow return`, and on `[HANDOFF]` present the candidates and run `handoff` only after the user's choice (immediately under `policy=auto`). It is identical for every host; Codex gets `allow_implicit_invocation: true`. Repositories that use no workflow never see the skill.
- **Subagent roles.** A stage `role` other than `developer` or `-` must be in the project's role vocabulary: the receipt's `kind = "subagent"` assets (asset id, plus the `role` a managed contract declares) and the project's `[workflow] roles_dir` (`<role>.md`, shadowing the receipt). A bundle ships a role as native files per agent or as one host-neutral contract that `devkit sync` renders for each selected agent ([Agent Projections](../distribution/agent-projections.md)). `validate`, `show`, `next` and `bind` report `unknown role '<role>' (no subagent contract found)` for a role outside it. `[DELEGATE: role=<role> isolation=<level> contract=<path>]` cites the managed or overridden contract, else the first projected file. With neither a receipt nor `roles_dir`, roles are not checked and `validate` returns a `WORKFLOW_ROLES_UNCHECKED` notice (`roles_checked: false`), so definitions can be authored before any bundle is synced.
- **Plugin checks.** Python check evaluators ship as `kind = "workflow-check"` assets or live under `[workflow] checks_dir`; see [Plugin Checks](definition-and-checks.md#plugin-checks).

## 5. Relationship to specrig

The engine was ported from specrig's `cli/internal/workflow` package and generalized: a configurable layout instead of hard-coded `specs/` paths, `lint-clean` bound to `devkit.rules`, gate and stage policies instead of skill prose, plugin checks instead of compiled-in evaluators, and a role vocabulary from the receipt. specrig embeds the engine through the library (`Workspace`, `evaluate_unit`, the structured `UnitEvaluation`) rather than parsing CLI output. Proposal relocation (moving a bundle from `docs/proposals/` to `specs/` with link rewriting), the scope registry and the feedback counter are specrig methodology and stay out of the engine, which provides the layout, binding, role, plugin-check and skip primitives such a layer needs. The task worktree lifecycle is generic and lives in [`devkit.worktree`](../worktree/overview.md); which routes use a worktree stays specrig's.
