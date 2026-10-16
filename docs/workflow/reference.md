# devkit.workflow

A data-driven delivery workflow engine for coding agents. A workflow is a Markdown file whose frontmatter declares stages with exit checks and approval gates; `devkit workflow` checks them against the files of a work unit and tells the agent which stage it is in, what is unmet and which skill to open next. The CLI is a thin layer over the library ([Library](#library)). Requires Python 3.12 or later.

## Structure

```text
src/devkit/workflow/
├── workspace.py         # Workspace: cached sources, unit resolution, bind_unit, evaluate_unit (drift policy), describe
├── answers.py           # record_answer, validate_answer, return_to
├── handoff.py           # candidate evaluation, plan_handoff, apply_handoff
├── render.py            # sentinel text lines (public render_* functions, used by the CLI)
├── errors.py            # WorkflowError and one subclass per error code
├── definition/
│   ├── definition.py    # workflow document model (StageDefinition, ...), parse_definition, load_definition, schema hash
│   ├── validation.py    # validate_definition, compare_shared_stages, validate_definitions
│   ├── discovery.py     # definitions_dir plus synchronized workflow assets; discover_definitions, resolve_definition
│   ├── checks.py        # check registry: syntax, classes, primitives, aliases, plugin registration
│   └── ids.py           # the shared [a-z][a-z0-9-]* identifier grammar
├── project/
│   ├── config.py        # [workflow], [workflow.approvals] and [workflow.stages]
│   ├── layout.py        # unit_path template, discovery, per-definition layout spec
│   ├── roles.py         # subagent role vocabulary from receipt subagent assets and roles_dir
│   └── plugins.py       # plugin checks from receipt workflow-check assets and checks_dir
├── unit/
│   ├── units.py         # create_unit, list_units
│   ├── binding.py       # workflow / workflow_hash / workflow_history in the anchor file
│   ├── frontmatter.py   # anchor frontmatter on devkit.core.frontmatter; in-place key updates
│   ├── decisions.py     # decisions/NN-<request>.yaml records, scoped to a workflow segment
│   ├── records.py       # record files: directory lock, unique sequences, whole, never replaced; temporary names
│   └── envelope/        # model.py (envelopes/<kind>-NN.yaml, review state, hold, write_envelope), authoring.py (compose_envelope)
├── evaluation/
│   ├── evaluate.py      # pure stage evaluation: evaluate_definition (Options -> UnitEvaluation)
│   ├── results.py       # UnitEvaluation, GateStatus, Delegate, Waiting, Drift, Skipped
│   ├── requests.py      # Request, Option, Target and how requests are built
│   ├── primitives.py    # evaluators of the disk primitives
│   ├── git.py           # merge-base ancestry for revision checks
│   └── lint.py          # the lint-clean binding to devkit.rules
├── integration.py       # finish_guard: the devkit.finish_guard extension refusing a held branch
└── cli/                 # app.py (group, options, error boundary), units.py, run.py, definitions.py, envelope.py
```

Everything public is exported from `devkit.workflow`; import from there
rather than from the subpackages.

## CLI usage

From this monorepo, run `just init`, then:

```bash
just workflow checks                                  # registered checks, plugin checks included
just workflow validate                                # definitions under definitions_dir, roles, shared stages
just workflow new login-flow                          # create and bind a unit
just workflow next --unit .devkit/transient/work/login-flow
just workflow next --unit <dir> --given integration   # assert a gate for this run only (every run for an answer=given gate)
just workflow next --unit <dir> --format json
just workflow requests --unit <dir>                   # open human requests (approvals, choices)
just workflow answer --unit <dir> --request gate:integration --action accept
just workflow return --unit <dir> --to build-verify   # take the unit back; later approvals are asked again
just workflow handoff --unit <dir>                    # continue a completed unit with the recorded or auto choice
just workflow show direct-delivery
just workflow show --unit <dir>                       # the unit's bound workflow plus its binding and drift
just workflow list                                    # units across every layout in use
just workflow list --exclude-status completed         # active units; --status <value> keeps exact matches
just workflow envelope new --unit <dir> --kind review # needs_input skeleton to fill in
just workflow envelope new --unit <dir> --kind review --summary "..." --findings-file findings.yaml --check tests="PASS 3/3"
just workflow envelope new --unit <dir> --kind reverify --from latest --resolve 1 --waive "2=accepted cost"
just workflow envelope new --unit <dir> --kind question --summary "..." --questions-file questions.yaml
just workflow envelope new --unit <dir> --kind answer --summary "..." --answers-to question-01.yaml --answers-file answers.yaml
just workflow envelope new --unit <dir> --kind worker --summary "..." --problem "<cause>" --tried "<attempt>" --recovery "<step>"
just workflow envelope new --unit <dir> --kind resolution --summary "<what was done>" --resolves worker-02.yaml
just workflow envelope check --unit <dir>             # every envelope file and any contract violation
```

Every command takes `-w/--workspace-root` (default: the devkit project containing the current directory). To install directly in another project:

```bash
uv add "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit workflow next --unit <dir>
```

Exit codes: `0` the command did its job (`next` whatever the stage), `1` a negative result (`validate`, `show`, `envelope check`, a drifted unit), `2` it could not run. The full command synopsis, exit and error codes, sentinels and JSON shapes are in the [CLI and Output Contract](cli-and-output.md).

## Configuration

Everything is optional and lives in the Git-tracked `.devkit/config.toml`:

```toml
[workflow]
work_dir = ".devkit/transient/work"   # root of work units
unit_path = "{slug}"                  # str.format template; {slug} and {date:<strftime>} only
anchor = "task.md"                    # file that identifies a unit and carries the binding
definitions_dir = ".devkit/workflows" # workflow definition files
roles_dir = ".devkit/roles"           # project-authored subagent contracts, <role>.md
checks_dir = ".devkit/workflow-checks" # project-authored plugin checks, one package directory each
default = "direct-delivery"           # used by `new` and by unbound units

[workflow.approvals]
direction = "auto"                    # ask (default) | auto | off
integration = "ask"
handoff = "ask"                       # reserved: who picks the next workflow of a completed unit

[workflow.stages]
collect-feedback = "off"              # on (default) | off: skip this stage id in every workflow
```

Layout template: [Overview, Work Units and Layout](overview.md#2-work-units-and-layout). Gate, stage and handoff policies: [Overview, Approval Gates](overview.md#3-approval-gates). Role vocabulary: [Overview, Integration](overview.md#4-integration-with-the-rule-engine-and-distribution). Plugin checks: [Plugin Checks](definition-and-checks.md#plugin-checks).

## Library

`Workspace` is the entry point. It applies the same configuration, plugin
checks, roles, lint binding and drift guard as the CLI, and loads the receipt,
the discovered definitions, roles and plugin checks once for every call. Every
failure is an `AdvisoryError` with a stable `code`, one class per code: a
`WorkflowError` subclass (`WorkflowConfigError`, `DefinitionError`,
`LayoutError`, `CheckError`, `DriftError`, `HandoffChoiceRequiredError`, ...),
or a `devkit.core` or `devkit.rules` error passed through unchanged
(`RECEIPT_INVALID`, `GIT_FAILED`, the error that stopped `lint-clean`). Branch
on `exc.code` or the class, never on the message. Problems the library
collects rather than raises are instances of the same classes:
`EnvelopeFormatError` and `DecisionRecordError` (with the unit-relative
`file`), validation's `DefinitionProblem`s (with `where`), and the
`DefinitionError`, `WorkflowAssetMissingError`, `PluginError` and
`SharedStageMismatchError` entries of `Workspace.discovery_errors`,
`load_plugin_checks` and `ValidationReport`. Their `to_dict()` is the JSON
form the CLI prints under `errors`.

```python
from pathlib import Path

from devkit.workflow import DriftError, Workspace

ws = Workspace(Path("."))  # Workspace() uses the project containing the current directory
unit = ws.resolve_unit(".devkit/transient/work/login")
try:
    result = ws.evaluate_unit(unit, lint=False)
except DriftError as exc:  # exc.code == "WORKFLOW_DRIFT": the definition changed under in-flight work
    raise SystemExit(exc.message) from exc
print(result.stage.id if result.stage else "complete")
for request in result.requests:
    print(request.id, request.kind, request.target.stage)
```

The main calls:

| Call | Purpose |
| --- | --- |
| `Workspace(root=None, *, lint=lint_with_rules, ancestor=is_ancestor)` | Load `[workflow]` configuration; the receipt, definitions, roles and plugins load lazily, once. |
| `ws.resolve_unit(unit, workflow=None, *, anchor=None) -> UnitRef` | Unit directory, anchor, binding and the workflow to evaluate against; `anchor` resolves `ANCHOR_AMBIGUOUS`. |
| `ws.unit_scope(unit, *, anchor=None) -> UnitScope` | Unit directory, anchor, binding and the bound (else default) workflow id, without loading the definition, except to read the id of a default given as a `.md` path (what `envelope new` uses). |
| `ws.bind_unit(unit, workflow=None, *, anchor=None) -> UnitRef` | `bind`: record the workflow and its schema hash in the anchor, keeping the history. A `workflow` path that is not the discovered definition of its id raises `WorkflowNotBindableError` (also from `create_unit`). |
| `ws.evaluate_unit(unit, *, given=(), lint=True, enforce_drift=True) -> UnitEvaluation` | Evaluate with the project's policies; raises `DriftError`; never writes a file. Approvals of later stages are listed in `UnitEvaluation.stale_approvals` and count until `return_to` voids them. |
| `ws.definition(ref=None, binding=None)`, `ws.load_definition(ref)` | A validated (or raw) definition by id or path relative to the root, from the cached definitions. |
| `ws.validate_definition(doc)`, `ws.validate_definitions(paths=()) -> ValidationReport` | One definition's problems; what `validate` reports (each `DefinitionReport.warnings`, and `ValidationReport.notices`, hold the non-fatal `OptionalStageWarning`s of `definition_warnings`). |
| `ws.describe(doc, binding=None) -> DefinitionDescription`, `ws.describe_unit(unit, *, anchor=None)` | What `show` and `show --unit` report (`to_dict()` is its JSON, `ok` its success). |
| `create_unit(ws, slug, *, workflow=None, when=None, status="planned") -> UnitRef` | `new`: creates the anchor exclusively (`UnitExistsError`); refuses a directory without one that holds leftover decision records or envelopes (`UnitDirNotEmptyError`). |
| `list_units(ws, *, statuses=(), excluded=()) -> list[UnitInfo]` | `list`. |
| `record_answer(ws, unit, request_id, action, values=(), *, note="", by="", lint=True) -> Decision` | `answer`. |
| `return_to(ws, unit, stage, *, note="", by="", lint=True) -> Decision` | `return`. |
| `plan_handoff(ws, unit, result, choice=None) -> HandoffPlan`, `apply_handoff(plan, *, when=None, by="", note="") -> HandoffOutcome` | `handoff`. |
| `compose_envelope(...) -> Envelope`, `envelope_timestamp(unit_dir, workflow, segment_start)`, `render_envelope(envelope, created_at)`, `write_envelope(unit_dir, kind, body)` | `envelope new`; pass `workflow=scope.workflow, segment=scope.binding.segment` (from `ws.unit_scope`) to scope the envelope, `load_envelopes(dir).scoped(workflow, segment)` as `envelopes`, and `envelope_timestamp(dir, workflow, scope.binding.segment_start)` as `created_at` so no earlier return voids it. |
| `load_envelopes(dir).hold() -> Hold` | Unresolved problems and unanswered questions over every segment (`blocked`, `problems`, `questions`, `reasons()`); `UnitEvaluation.hold` carries the same. |
| `evaluate_definition(doc, Options) -> UnitEvaluation` | Pure evaluation without policies or writes. |

## Specifications

- [Workflow Engine Overview](overview.md): delivery model, layout template, approval, stage and handoff policies, integration with rules and distribution.
- [Workflow Definitions and Checks](definition-and-checks.md): document schema, shared stages, handoff candidates, check registry and plugin checks, binding and drift.
- [Review Envelopes](envelopes.md): envelope file contract (questions, answers, problems, resolutions), authoring flags, `envelope check`, the hold on gates and integration.
- [Human Interaction Contract](human-interaction.md): request kinds, decision records, how answers are applied.
- [CLI and Output Contract](cli-and-output.md): commands, exit and error codes, text sentinels and JSON shapes.
