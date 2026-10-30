# devkit_agt.features.workflow

A data-driven delivery workflow engine for coding agents. A workflow is a Markdown file whose frontmatter declares stages with exit checks and approval gates; `devkit workflow` checks them against the files of a work unit and tells the agent which stage it is in, what is unmet and which skill to open next. The CLI is a thin layer over the library ([Library](#library)). Requires Python 3.12 or later.

## Structure

```text
src/devkit_agt/features/workflow/
├── models/              # definitions, layouts, bindings, decisions and evaluation results
│   ├── definition.py    # WorkflowDocument and pure parse_definition
│   └── layout.py        # TemplateLayout path rendering and discovery_glob
├── repositories/        # configuration, workflow sources, Git and unit records
│   ├── definitions.py   # load_definition, discover_definitions
│   ├── layout.py        # discover_units: real filesystem discovery from a layout
│   ├── project/         # workflow configuration and role vocabulary
│   └── unit/            # bindings, frontmatter, immutable records and decisions
├── services/            # definition validation, primitive evaluation and envelope policy
├── usecases/            # workspace, units, evaluation, answers, handoff and envelopes
└── cli/                 # app, definitions, units, run, envelope and rendering adapters
```

Everything public is exported from `devkit_agt.features.workflow`; import from there
rather than from the subpackages.

## CLI usage

From this monorepo, run `just init`, then:

```bash
just workflow checks                                  # registered checks: primitives and aliases
just workflow validate                                # definitions under definitions_dir, roles, shared stages
just workflow new login-flow                          # create and bind a unit
just workflow next --unit .devkit/transient/work/login-flow
just workflow next --unit <dir> --given integration   # assert a gate for this run only (every run for an answer=given gate)
just workflow next --unit <dir> --format json
just workflow next --view requests --unit <dir>                   # open human requests (approvals, choices)
just workflow answer --unit <dir> --request gate:integration --action accept
just workflow return --unit <dir> --to build-verify   # take the unit back; later approvals are asked again
just workflow handoff --unit <dir>                    # continue a completed unit with the recorded or auto choice
just workflow show direct-delivery
just workflow show --unit <dir>                       # the unit's bound workflow plus its binding
just workflow list                                    # units across every layout in use
just workflow list --exclude-status completed         # active units; --status <value> keeps exact matches
just workflow envelope review --unit <dir>            # needs_input skeleton to fill in
just workflow envelope review --unit <dir> --summary "..." --findings-file findings.yaml --check tests="PASS 3/3"
just workflow envelope reverify --unit <dir> --from latest --resolve 1 --waive "2=accepted cost"  # open findings only
just workflow envelope worker --unit <dir> --stage <stage> --summary "..." --questions-file questions.yaml
just workflow envelope answer --unit <dir> --summary "..." --answers-to worker-01.yaml --answers-file answers.yaml  # each answer may name by: user|host|policy
just workflow envelope worker --unit <dir> --stage <stage> --summary "..." --problem "<cause>" --tried "<attempt>" --recovery "<step>"
just workflow envelope resolution --unit <dir> --summary "<what was done>" --resolves worker-02.yaml
just workflow envelope new --unit <dir> --kind final-report --check tests="PASS 3/3"  # any other kind
just workflow envelope check --unit <dir>             # every envelope file and any contract violation
```

Every command takes `-w/--workspace-root` (default: the devkit project containing the current directory). To install directly in another project:

```bash
uv add "devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit workflow next --unit <dir>
```

Exit codes: `0` the command did its job (`next` whatever the stage), `1` a negative result (`validate`, `show`, `envelope check`), `2` it could not run. The full command synopsis, exit and error codes, sentinels and JSON shapes are in the `CAP-DLV-cli-and-output`.

## Configuration

Everything is optional and lives in the Git-tracked `.devkit/config.toml`:

```toml
[workflow]
work_dir = ".devkit/transient/work"   # root of work units
unit_path = "{slug}"                  # str.format template; {slug} and {date:<strftime>} only
anchor = "task.md"                    # file that identifies a unit and carries the binding
definitions_dir = ".devkit/workflows" # workflow definition files
roles_dir = ".devkit/roles"           # project-authored subagent contracts, <role>.md
default = "direct-delivery"           # used by `new` and by unbound units

[workflow.approvals]
integration = "auto"                  # ask (default) | auto | off
handoff = "ask"                       # reserved: who picks the next workflow of a completed unit

[workflow.stages]
collect-feedback = "off"              # on (default) | off: skip this stage id in every workflow
```

Layout template: `CAP-DLV-workflow-orchestration`. Gate, stage and handoff policies: `CAP-DLV-workflow-orchestration`. Role vocabulary: `CAP-DLV-workflow-orchestration`.

## Library

`Workspace` is the entry point. It applies the same configuration, roles,
lint binding as the CLI, and loads the receipt, the discovered
definitions and roles once for every call. Every
failure is an `AdvisoryError` with a stable `code`, one class per code: a
`WorkflowError` subclass (`WorkflowConfigError`, `DefinitionError`,
`LayoutError`, `CheckError`, `HandoffChoiceRequiredError`, ...),
or a foundation, project or `devkit_agt.features.rules` error passed through unchanged
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

from devkit_agt.features.workflow import Workspace

ws = Workspace(Path("."))  # Workspace() uses the project containing the current directory
unit = ws.resolve_unit(".devkit/transient/work/login")
result = ws.evaluate_unit(unit, lint=False)
print(result.stage.id if result.stage else "complete")
for request in result.requests:
    print(request.id, request.kind, request.target.stage)
```

The main calls:

| Call | Purpose |
| --- | --- |
| `Workspace(root=None, *, lint=lint_with_rules, ancestor=is_ancestor, invocation=None)` | Load `[workflow]` configuration; the receipt, definitions, roles and plugins load lazily, once. `invocation` (the CLI passes the arguments after `devkit workflow`) lets `ANCHOR_AMBIGUOUS` list the exact command to rerun per candidate anchor. |
| `ws.resolve_unit(unit, workflow=None, *, anchor=None) -> UnitRef` | Unit directory, anchor, binding and the workflow to evaluate against; `anchor` resolves `ANCHOR_AMBIGUOUS`. |
| `ws.unit_scope(unit, *, anchor=None) -> UnitScope` | Unit directory, anchor, binding and the bound (else default) workflow id, without loading the definition, except to read the id of a default given as a `.md` path (what the envelope authoring commands use). |
| `ws.bind_unit(unit, workflow=None, *, anchor=None) -> UnitRef` | `bind`: record the workflow ID in the anchor, keeping the history. A `workflow` path that is not the discovered definition of its id raises `WorkflowNotBindableError` (also from `create_unit`). |
| `ws.evaluate_unit(unit, *, given=(), lint=True) -> UnitEvaluation` | Evaluate with the project's policies; never writes a file. Approvals of later stages are listed in `UnitEvaluation.stale_approvals` and count until `return_to` voids them. |
| `ws.definition(ref=None, binding=None)`, `ws.load_definition(ref)` | A validated (or raw) definition by id or path relative to the root, from the cached definitions. |
| `ws.validate_definition(doc)`, `ws.validate_definitions(paths=()) -> ValidationReport` | One definition's problems; what `validate` reports (each `DefinitionReport.warnings`, and `ValidationReport.notices`, hold the non-fatal `OptionalStageWarning`s of `definition_warnings`). |
| `ws.describe(doc, binding=None) -> DefinitionDescription`, `ws.describe_unit(unit, *, anchor=None)` | What `show` and `show --unit` report (`to_dict()` is its JSON, `ok` its success). |
| `create_unit(ws, slug, *, workflow=None, when=None, status="planned") -> UnitRef` | `new`: creates the anchor exclusively (`UnitExistsError`); refuses a directory without one that holds leftover decision records or envelopes (`UnitDirNotEmptyError`). |
| `list_units(ws, *, statuses=(), excluded=()) -> list[UnitInfo]` | `list`. |
| `record_answer(ws, unit, request_id, action, values=(), *, note="", by="", lint=True) -> Decision` | `answer`. |
| `return_to(ws, unit, stage, *, note="", by="", lint=True) -> Decision` | `return`. |
| `plan_handoff(ws, unit, result, choice=None) -> HandoffPlan`, `apply_handoff(plan, *, when=None, by="") -> HandoffOutcome` | `handoff`. |
| `compose_envelope(...) -> Envelope`, `envelope_timestamp(unit_dir, workflow, segment_start)`, `render_envelope(envelope, created_at)`, `write_envelope(unit_dir, kind, body)` | The envelope authoring commands; pass `workflow=scope.workflow, segment=scope.binding.segment` (from `ws.unit_scope`) to scope the envelope, `load_envelopes(dir).scoped(workflow, segment)` as `envelopes`, `unit=scope.rel` so the refusals name runnable commands, and `envelope_timestamp(dir, workflow, scope.binding.segment_start)` as `created_at` so no earlier return voids it. |
| `load_envelopes(dir).hold() -> Hold` | Unresolved problems and unanswered questions over every segment (`blocked`, `problems`, `questions`, `reasons()`); `UnitEvaluation.hold` carries the same. |
| `evaluate_definition(doc, Options) -> UnitEvaluation` | Pure evaluation without policies or writes. |

## Specifications

- `CAP-DLV-workflow-orchestration`: delivery model, layout template, approval, stage and handoff policies, integration with rules and distribution.
- `CAP-DLV-workflow-definitions`: document schema, shared stages, handoff candidates, check registry, binding.
- `CAP-DLV-workflow-envelopes`: envelope file contract (worker questions and problems, answers, resolutions), authoring flags, `envelope check`, the hold on gates and integration.
- `CAP-DLV-human-interaction`: request kinds, decision records, how answers are applied.
- `CAP-DLV-cli-and-output`: commands, exit and error codes, text sentinels and JSON shapes.
