# Agent Workflow Engine: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-workflow-engine` (`agent-workflow` CLI)  
**Related Documents**:
- [Workflow Definitions and Checks](definition-and-checks.md)
- [Rule Engine Overview](../rule-engine/overview.md)
- [Context Loading and Playbook Discovery](../distribution/context-and-playbooks.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Problem Statement

A multi-stage delivery procedure (intent, specify, build, review, reconcile, integrate) has to be followed the same way by every coding agent a repository uses, today Claude Code and Codex, occasionally Antigravity. Two delivery models were compared:

1. **Procedure inside agent skills.** Each stage is a `SKILL.md`; the agent reads the prose and decides for itself which stage it is in by looking at files. This needs no CLI, but stage detection is prose, so hosts diverge, a changed procedure cannot be detected on in-flight work, and approval gates hold only as well as the host follows long instructions.
2. **Procedure as data, stage computed by a CLI, skills as thin entry points.** Stages, their exit conditions and their gates are declared in a workflow definition file. A CLI evaluates the conditions against the files of a work unit and prints the current stage, what is unmet and what to do next. Skills only route the agent to that output.

`devkit` implements the second model. It is the model `specrig` converged on, and it is the only one in which Claude Code and Codex receive the same answer from the same state. One per-agent entry skill remains necessary, because no host invokes a CLI on its own.

### Core Principles

1. **Procedure is data.** A workflow is a Markdown file whose frontmatter declares `stages[]`. The body carries prose gate rules for humans and agents; the engine never parses it.
2. **The CLI decides the stage.** `agent-workflow next` evaluates every stage's exit checks in order and reports the first unmet stage. Agents treat `[STAGE]` as the diagnosed stage rather than re-deriving it.
3. **Gates are enforced by policy, not prose.** A stage marked `human_gate` cannot be passed without an explicit `--given <gate>` under the `ask` policy. The project lowers a gate to `auto` or `off` in configuration, never by editing the workflow.
4. **Drift is detected.** A work unit records the hash of the stage schema it was bound to. When the definition changes under in-flight work, `next` refuses until the unit is rebound.
5. **Layout is a template, not a convention.** Where work units live and how their directories are named is a configured path template. The engine assumes only "a directory containing an anchor file".
6. **Agent-neutral by construction.** Definitions, CLI output and entry skills are identical bytes for every host. Only subagent role projection differs per host, and `devkit-distribution` already owns that.

---

## 2. Subsystem Layout

```text
packages/agent-workflow-engine/src/agent_workflow_engine/
├── config.py        # [workflow] and [workflow.approvals] from .devkit/config.toml
├── layout.py        # Layout protocol + TemplateLayout (unit_path template, discovery glob)
├── frontmatter.py   # Frontmatter split/read/update preserving every other byte
├── definition.py    # Workflow document parsing, validation, schema hash
├── checks.py        # Check registry: syntax, classes, primitives, aliases
├── envelope.py      # envelopes/<kind>-NN.yaml loading and review/reverify state
├── evaluate.py      # Stage evaluation: checks, gates, --given, delegate, waiting
├── binding.py       # workflow / workflow_hash recorded in the anchor file
├── render.py        # Sentinel text lines and JSON
├── git.py           # merge-base ancestry for revision checks
└── cli/commands.py  # agent-workflow: new, bind, next, show, checks, validate, list, envelope
```

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

- `unit_path` is a Python `str.format` template. Placeholders are `{slug}` and `{date}`; `{date}` accepts a `strftime` spec, for example `{date:%Y%m%d}`. No other syntax is introduced.
- `{slug}` is mandatory. Absolute paths, `..`, and backslashes are rejected.
- Discovery replaces each placeholder with `*`, globs under `work_dir`, and keeps directories that contain the anchor file. Nothing is parsed back out of a path; identity lives in the anchor's frontmatter.
- The `specrig` layout is expressed as `work_dir = "specs"`, `unit_path = "{date:%Y-%m}/{date:%Y%m%d}-{slug}"`, `anchor = "spec.md"`.
- The default `work_dir` is under `.devkit/transient/`, which consumer repositories are expected to ignore in Git. Choose a tracked path instead when review envelopes and approval evidence must travel with pull requests and across machines.

The layout is a two-method protocol (`new_unit`, `discover`) with `TemplateLayout` as its only implementation. A Python plugin layout, loaded like custom rules, fits behind the same protocol and is deferred until a template cannot express a required structure.

### The Anchor File

The anchor is Markdown with YAML frontmatter. `agent-workflow new` writes:

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

`status` is read by frontmatter checks and reported by `next`. `workflow` and `workflow_hash` are the binding. Every other frontmatter line and the whole body are preserved by binding updates.

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
| `ask` (default) | The gate is an implicit human check. The stage stays current with `[WAITING: human gate:<gate>]` until the executor runs `next --given <gate>` after obtaining the user's approval. |
| `auto` | The gate is satisfied by policy. The stage passes once its other exit checks hold, and the output records `[GATE: <gate> policy=auto]` so the delegation is visible. |
| `off` | The stage is skipped and reported as `[SKIPPED: <id> policy=approvals.<gate>=off]`. |

`--given` is the only way to assert a human or runner check. The CLI never writes an approval file and never infers approval from conversation. Raising a gate later is a configuration change back to `ask`; lowering it is a change to `auto` or `off`. The workflow definition does not change in either case.

### The `handoff` Gate

Workflows are segments: a definition's `next` list names the workflows that may continue a completed unit ([Definitions, Handoff Candidates](definition-and-checks.md#handoff-candidates)). The reserved gate name `handoff` governs who picks:

| Policy | Behavior |
| --- | --- |
| `ask` (default) | `next` lists every candidate with its eligibility and recommendation and reports `[WAITING: human handoff]`. The executor presents them, and after the user's choice runs `handoff --unit DIR --workflow <id>`; the choice must be an eligible candidate. |
| `auto` | The first candidate whose `when` checks all hold is `chosen=`; `handoff --unit DIR` rebinds to it without a choice. With no eligible candidate the engine waits for a person, and `handoff` without `--workflow` fails with `HANDOFF_UNDECIDED`. |
| `off` | No handoff is offered; the unit is finished when its workflow completes. |

`handoff` records the finished segment in the anchor's `workflow_history` and binds the unit to the chosen workflow, whose stages are then evaluated from the start against the same unit directory.

---

## 5. CLI Surface

```bash
agent-workflow new <slug> [--workflow ID] [--date YYYY-MM-DD]   # create a unit from the layout template and bind it
agent-workflow bind --unit DIR [--workflow ID]                  # record or refresh the binding (accepts drift)
agent-workflow next --unit DIR [--given NAME]... [--no-lint] [--format text|json]
agent-workflow handoff --unit DIR [--workflow ID] [--date YYYY-MM-DD]  # continue a completed unit with a next candidate
agent-workflow show <ID|PATH> [--format text|json]              # print a definition's stages, hash and next candidates
agent-workflow checks [--format text|json]                      # registered check names, classes and parameters
agent-workflow validate [PATH]...                               # validate definitions (default: definitions_dir)
agent-workflow list [--format text|json]                        # discovered units with status and binding
agent-workflow envelope new --unit DIR --kind KIND              # write the next envelopes/<kind>-NN.yaml skeleton
```

All commands accept `-w/--workspace-root`. Exit codes: `0` success, `1` any error. `next` exits `0` whether or not the unit is complete; the stage is in the output.

Errors are reported on stderr as Agent Advisory Protocol blocks from the `agent-advisory` package, with a stable code and an `[ACTION]` directive, so an agent knows whether to fix input, stop for a person, or respect a guardrail. Under `--format json` the same error is also emitted on stdout as `{"error": {...}}`.

| Code | Mode | Raised when |
| --- | --- | --- |
| `CONFIG_INVALID` | `INPUT_ERROR` | the `[workflow]` table is malformed |
| `WORKFLOW_NOT_SELECTED`, `WORKFLOW_NOT_FOUND`, `WORKFLOW_INVALID` | `INPUT_ERROR` | no definition chosen, none matches, or the chosen one fails validation (problems become `[DETAIL]` lines) |
| `UNIT_NOT_FOUND`, `UNIT_EXISTS`, `ANCHOR_INVALID` | `INPUT_ERROR` | the unit directory has no anchor, already exists, or its frontmatter is unreadable |
| `SLUG_INVALID`, `DATE_INVALID`, `GIVEN_INVALID`, `KIND_INVALID` | `INPUT_ERROR` | a flag or argument is malformed |
| `HANDOFF_NOT_READY`, `HANDOFF_NONE`, `HANDOFF_OFF` | `INPUT_ERROR` | the unit's workflow is not complete, declares no `next`, or handoff is disabled by policy |
| `HANDOFF_CHOICE_REQUIRED`, `HANDOFF_UNDECIDED`, `HANDOFF_INVALID`, `HANDOFF_INELIGIBLE` | `INPUT_ERROR` | `ask` needs `--workflow`; `auto` found no eligible candidate; the choice is not a candidate, or its `when` checks fail (details list the candidates) |
| `WORKFLOW_DRIFT` | `BLOCKED` | the bound schema hash changed under in-flight work; `[FIX]` names the `bind` command |
| `LINT_FAILED` | `MAINTENANCE` | `agent-rule-engine` raised a rule execution error during `lint-clean` |

Output contracts are specified in [Workflow Definitions and Checks, section 5](definition-and-checks.md#5-output-signals).

---

## 6. Integration with the Rule Engine and Distribution

- **Lint check.** The `lint-clean` check runs `agent-rule-engine` in the `linter` phase on the files of the work unit, honoring the project's `[rules]` policy (phase and severity overrides, typed settings) and loading the rules that `devkit sync` recorded in the installation receipt. Violations are reported in the check detail; a rule execution or loading error fails the command.
- **Workflow definitions as assets.** A bundle declares `kind = "workflow"` assets (one Markdown definition each). `devkit sync` places them under `.devkit/managed/<bundle>/` and records their paths in the installation receipt under `entrypoints`. The engine discovers definitions from two sources: the project's `definitions_dir`, and every workflow asset in `.devkit/installation.json`. A project definition with the same `id` shadows the synchronized one, so a repository can adapt a distributed workflow without editing managed files. `agent-workflow validate` with no arguments covers both sources.
- **Entry skill.** When at least one workflow asset is synchronized, `devkit sync` generates the shared `devkit-workflow` skill and projects it into every selected agent's skill directory, exactly as it does for `devkit-playbook`. The skill tells the agent to run `agent-workflow next --unit <dir>`, treat `[STAGE]` as the diagnosed stage, open the skill named by `[NEXT_SKILL]`, never pass `--given` for an approval it did not receive, and on `[HANDOFF]` present the candidates and run `handoff` only after the user's choice (or immediately under `policy=auto`). It is identical for every host; Codex gets `allow_implicit_invocation: true` because the agent should pick it up whenever a task follows a workflow. Repositories that use no workflow never see the skill.
- **Subagent delegation.** `[DELEGATE: role=<role> isolation=<level>]` names a role; the host's projected subagent file for that role is the contract. A bundle ships the role as a `kind = "subagent"` asset, either as native files per agent or as one host-neutral role contract that `devkit sync` renders for each selected agent (see [Agent Projections](../distribution/agent-projections.md)). The engine does not resolve host paths.

---

## 7. Relationship to specrig

The stage schema, check classes, evaluation loop, binding hash, envelope file contract and sentinel output are ported from `specrig`'s `cli/internal/workflow` package. Four things were generalized:

| specrig | devkit |
| --- | --- |
| `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/spec.md` hard-coded | `[workflow]` layout template and anchor name |
| `lint-clean` bound to the specrig rule engine | bound to `agent-rule-engine` |
| `feedback.sweep=off` as the only policy skip | gate policy `off` skips any gated stage |
| `human_gate: true` interpreted by skill prose | `[workflow.approvals]` enforced by the CLI with `ask`, `auto`, `off` |

Proposal handoff, worktree commands, the scope registry and the feedback counter are specrig methodology and are not part of this engine.
