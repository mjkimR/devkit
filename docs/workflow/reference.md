# devkit.workflow

A data-driven delivery workflow engine for coding agents. A workflow is a
Markdown file whose frontmatter declares stages with exit checks and approval
gates. The `devkit workflow` CLI checks those against the files of a work
unit and tells the agent which stage it is in, what is unmet and which skill
to open next. Claude Code, Codex and Antigravity read the same output. The
engine is part of the `devkit` distribution and requires Python 3.12 or later.
The CLI is a thin layer over the `devkit.workflow` library (see
[Library](#library)).

## Structure

```text
src/devkit/workflow/
├── workspace.py     # Workspace: configuration, definitions, roles, plugins, unit resolution, evaluate_unit (drift policy)
├── units.py         # create_unit, list_units
├── answers.py       # record_answer, validate_answer, return_to
├── handoff.py       # candidate evaluation, plan_handoff, apply_handoff
├── evaluate.py      # pure stage evaluation (Options -> Result)
├── results.py       # Result, Gate, Delegate, Waiting, Drift, Skipped
├── requests.py      # Request, Option, Target and how requests are built
├── primitives.py    # evaluators of the disk primitives
├── definition.py    # workflow document model, parsing and the schema hash
├── validation.py    # validate, shared_stage_problems, validate_workspace
├── discovery.py     # definitions_dir plus synchronized workflow assets; find, resolve
├── checks.py        # check registry: syntax, classes, primitives, aliases, plugin registration
├── plugins.py       # plugin checks from receipt workflow-check assets and checks_dir
├── roles.py         # subagent role vocabulary from receipt subagent assets and roles_dir
├── decisions.py     # decisions/NN-<request>.yaml records, scoped to a workflow segment
├── envelope/        # model.py (envelopes/<kind>-NN.yaml, review state), authoring.py (envelope new)
├── binding.py       # workflow / workflow_hash / workflow_history in the anchor file
├── config.py        # [workflow], [workflow.approvals] and [workflow.stages]
├── layout.py        # unit_path template, discovery, per-definition layout spec
├── frontmatter.py   # anchor frontmatter on devkit.core.frontmatter; in-place key updates
├── render.py        # sentinel text lines
├── lint.py          # the lint-clean binding to devkit.rules
├── git.py           # merge-base ancestry for revision checks
├── ids.py           # the shared [a-z][a-z0-9-]* identifier grammar
├── errors.py        # WorkflowError and its coded subclasses
└── cli/             # app.py (group, options, error boundary), units.py, run.py, definitions.py, envelope.py
```

## CLI usage

From this monorepo, run `just init`, then:

```bash
just workflow checks                                  # registered checks, plugin checks included
just workflow validate                                # definitions under definitions_dir, roles, shared stages
just workflow new login-flow                          # create and bind a unit
just workflow next --unit .devkit/transient/work/login-flow
just workflow next --unit <dir> --given integration   # assert a gate for this run only
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
just workflow envelope check --unit <dir>             # every envelope file and any contract violation
```

Every command takes `-w/--workspace-root`. Without it the workspace is the
devkit project that contains the current directory: the nearest directory
with a `.devkit/` folder, else the Git work tree's top level.

To install directly in another project:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit workflow next --unit <dir>
```

Exit codes follow the devkit convention
([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)):
`0` the command did its job, `1` it reports a negative result, `2` it could
not do its job. `next` exits `0` whatever the stage, including a unit waiting
for a person or a delegation. `1` comes from `validate` (invalid definitions),
`show` (a definition with problems), `envelope check` (`ENVELOPE_INVALID`) and
`next` refusing a drifted unit (`WORKFLOW_DRIFT`). Everything else that fails,
from a usage error to `UNIT_NOT_FOUND`, `CONFIG_INVALID` or `RECEIPT_INVALID`,
exits `2`. Errors are Agent Advisory Protocol blocks on stderr
(`devkit.advisory`) with a stable code and an `[ACTION]` directive; the codes
are listed in [Overview, section 5](overview.md#5-cli-surface). Under
`--format json` stdout carries exactly one JSON document: the result, or
`{"error": {...}}` when there is none.

## Configuration

Everything is optional and lives in the Git-tracked `.devkit/config.toml`:

```toml
[workflow]
work_dir = ".devkit/transient/work"   # root of work units
unit_path = "{slug}"                  # str.format template; {slug} and {date:<strftime>} only
anchor = "task.md"                    # file that identifies a unit and carries the binding
definitions_dir = ".devkit/workflows" # workflow definition files
roles_dir = ".devkit/roles"           # project-authored subagent contracts, <role>.md
checks_dir = ".devkit/workflow-checks" # project-authored plugin checks, *.py
default = "direct-delivery"           # used by `new` and by unbound units

[workflow.approvals]
direction = "auto"                    # ask (default) | auto | off
integration = "ask"
handoff = "ask"                       # reserved: who picks the next workflow of a completed unit

[workflow.stages]
collect-feedback = "off"              # on (default) | off: skip this stage id in every workflow
```

`ask` keeps a gated stage current and, once the stage's own exit checks hold,
emits an `approve` request. The answer is a decision record under
`<unit>/decisions/`, written by `devkit workflow answer` or by a host UI;
`next --given <gate>` remains as an assertion for one run that is not stored.
`auto` passes the gate by policy, and `[GATE: ... source=policy]` says so
while the stage is current. `off` skips the stage. Lowering or raising a gate
later is a change to this table only. The request and record formats are the
[Human Interaction Contract](human-interaction.md).

`[workflow.stages]` turns a stage off by id whether or not it has a gate.
`next` reports it as `[SKIPPED: <id> reason=stages.<id>=off]` and the stage
never blocks completion or handoff. Ids that no selected workflow uses are
allowed, since stage ids are shared across definitions.

Workflows chain. A definition's `next` list names candidate workflows with
`when` preconditions (check syntax) and a `recommended` flag. Once a unit
completes its workflow, `next` prints `[HANDOFF]` and one `[CANDIDATE]` line
per candidate with its eligibility, plus a `choose` request. Under
`handoff = "ask"` the person's choice is recorded with `answer --request
handoff --action accept --value <id>`, or passed as `handoff --workflow <id>`,
which records the same decision. Under `"auto"` the first eligible candidate
is chosen. `handoff --unit <dir>` then rebinds the unit and records the
finished segment in the anchor's `workflow_history`. Decisions of a finished
segment never count in the next one.

## Workflow definitions

Definitions are discovered from the project's `definitions_dir` and from every
`kind = "workflow"` asset that `devkit sync` recorded in
`.devkit/installation.json`; a project definition shadows a synchronized one
with the same id. A recorded definition missing from disk is reported as
`WORKFLOW_ASSET_MISSING` (run `devkit sync`), and a malformed receipt is `RECEIPT_INVALID` (restore it
from version control, then run `devkit sync`). Bundles that
ship a workflow also get the generated `devkit-workflow` entry skill, so an
agent knows to run `next`.

`validate` with no arguments checks every discovered definition and, across
them, that a stage id used by several definitions is the same stage: equal
`exit`, `human_gate`, `role`, `isolation`, `skills` and `artifacts`. A
difference is reported as `[INVALID: shared stage '<id>' differs between <a>
and <b>: <field>]`, because skills, runners and people recognize a stage by
its id. `validate --format json` emits `{"valid", "roles_checked",
"definitions": [{"id", "path", "valid", "hash", "problems"}], "errors",
"shared"}`. Every problem is a coded entry: `problems` hold
`{"code", "where", "message"}` (`code` is `DEFINITION_INVALID`,
`CHECK_INVALID` or `ROLE_UNKNOWN`), and `errors` (files that could not be
loaded) and `shared` (`SHARED_STAGE_MISMATCH`) hold `{"code", "message",
"target", "fix"}`. `show --format json` reports its `problems` the same way.

## Roles and plugin checks

A stage `role` other than `developer` or `-` must name a subagent the project
has: a `kind = "subagent"` asset recorded in the receipt (its asset id, plus
the `role` its contract declares), or a project-authored `<roles_dir>/<role>.md`,
which shadows the receipt entry. `validate`, `show`, `next` and `bind` report
`unknown role '<role>' (no subagent contract found)` otherwise. When neither
the receipt nor `roles_dir` exists, the check is skipped and `validate` says so
with a `[NOTE]`, so definitions can be authored before any bundle is synced.
`[DELEGATE: role=<role> isolation=<level> contract=<path>]` then cites the
contract that defines the role.

Checks are extensible. A Python file under `checks_dir`, or recorded in the
receipt under a `kind = "workflow-check"` asset, defines `BaseCheck` subclasses:

```python
from devkit.workflow import BaseCheck, CheckContext, CheckResult


class MaterialsPresent(BaseCheck):
    name = "materials-present"
    description = "the unit has at least one file under materials/"
    params = ()

    def evaluate(self, ctx: CheckContext) -> CheckResult:
        found = any((ctx.unit_dir / "materials").glob("*"))
        return ctx.passed() if found else ctx.failed("materials/ is empty or missing")
```

Loaded checks appear in `devkit workflow checks` with class `plugin` and are
referenced from definitions like primitives (`name` or `name(arg ...)` with the
declared `params`). A name that collides with a built-in is an error. Loading
is atomic per file: a file that fails to import, declares an invalid check or
redefines a name contributes nothing and is `CHECK_LOAD_FAILED`. Every
receipt-listed file is first checked with `devkit.core.receipt.verified_asset_file`,
exactly as rules and gates are: a file that is missing, resolves outside the
project or differs from the SHA-256 the receipt records is `CHECK_LOAD_FAILED`
too, with the fix `devkit sync` (restore) or `devkit override create
<bundle>:<asset>` (keep the edit); a file without a record (a project
override) loads as it is. A check that raises is an unsatisfied,
evaluated result with the exception in its detail. Plugin files are executable
Python and must come from a trusted source.

A definition declares `id`, `schema_version: 1`, optional `checks` (runner or
human checks it introduces), ordered `stages`, each with `exit` checks,
`skills`, `role`, `isolation`, `human_gate` and `returns`, an optional
`next` list of handoff candidates, and an optional `layout` that overrides
`work_dir`, `unit_path` or `anchor` for the units of that workflow, so one
repository can keep, for example, proposal bundles under `docs/proposals/`
and spec bundles under `specs/` as units of different workflows. Unknown keys
are rejected at every level. Checks are `name` or `name(arg ...)` from
`devkit workflow checks`; aliases such as `anchor-exists`, `tasks-all-checked`
and `envelope-review-passed` resolve against the configured anchor.
`lint-clean` runs `devkit.rules` on the unit's files. See
[Workflow Definitions and Checks](definition-and-checks.md) for the schema,
the check table, the envelope contract and the output signals.

## Library

`Workspace` is the entry point. It applies the same configuration, plugin
checks, roles, lint binding and drift guard as the CLI. Every failure is an
`AdvisoryError` with a stable `code`: a `WorkflowError` (or one of its
subclasses such as `ConfigError`, `DefinitionError`, `LayoutError`,
`CheckError` or `DriftError`), or a `devkit.core` error passed through
unchanged (`RECEIPT_INVALID`, `GIT_FAILED`). Branch on `exc.code`, never on the
message. Problems the library collects rather than raises are typed entries
with a `code`: `EnvelopeError`, `DecisionError`, validation `Problem`s
(`stage`, `field`, `message`, `code`) and `WorkflowProblem`s (`message`,
`code`, `target`, `fix`) for definition and plugin check files that could not
be loaded (`Workspace.discovery_errors`, `load_plugin_checks`,
`ValidationReport.load_errors`) and for shared-stage differences
(`shared_stage_problems`).

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
| `Workspace(root=None, *, lint=rules_lint, ancestor=is_ancestor)` | Load `[workflow]` configuration; definitions, roles and plugins load lazily, once. |
| `ws.resolve_unit(unit, workflow=None) -> UnitRef` | Unit directory, anchor, binding and the workflow to evaluate against. |
| `ws.evaluate_unit(unit, *, given=(), lint=True, enforce_drift=True) -> Result` | Evaluate with the project's policies; raises `DriftError`; never writes a file. Approvals of later stages are listed in `Result.stale_approvals` and count until `record_return(unit, stage)` voids them. |
| `ws.definition(ref=None, binding=None)`, `ws.load_definition(ref)` | A validated (or raw) definition by id or path relative to the root. |
| `ws.validate_definitions(paths=()) -> ValidationReport` | What `validate` reports. |
| `ws.describe(doc, binding=None) -> dict` | What `show --format json` emits. |
| `create_unit(ws, slug, *, workflow=None, when=None, status="planned") -> UnitRef` | `new`. |
| `list_units(ws, *, statuses=(), excluded=()) -> list[UnitInfo]` | `list`. |
| `record_answer(ws, unit, request_id, action, values=(), *, note="", by="", lint=True) -> Decision` | `answer`. |
| `return_to(ws, unit, stage, *, note="", by="", lint=True) -> Decision` | `return`. |
| `plan_handoff(ws, unit, result, choice=None) -> HandoffPlan`, `apply_handoff(plan, *, when=None, by="", note="") -> HandoffOutcome` | `handoff`. |
| `compose(...) -> Envelope`, `render_envelope(envelope, created_at)`, `write_next(unit_dir, kind, body)` | `envelope new`. |
| `evaluate(doc, Options) -> Result` | Pure evaluation without policies or writes. |

## Current limits

Only `TemplateLayout` exists. A handoff to a workflow whose anchor differs
from the unit's is refused (`HANDOFF_LAYOUT_MISMATCH`); moving a unit between
layouts is the caller's job, followed by `bind`. Subagent delegation names a
role, its isolation level and the contract path; the host projection of that
role belongs to `devkit.distribution`. `entry` checks are informational: they
appear in `show` and in the JSON `stage` object and are never evaluated.

## Architectural Specifications & Deep-Dives

- [Workflow Engine Overview](overview.md): delivery model, layout template, approval gates, CLI surface and the relationship to specrig.
- [Workflow Definitions and Checks](definition-and-checks.md): document schema, check registry, envelopes, binding and drift, output signals.
- [Human Interaction Contract](human-interaction.md): request kinds, decision records, how answers are applied.
