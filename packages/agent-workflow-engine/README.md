# agent-workflow-engine

A data-driven delivery workflow engine for coding agents. A workflow is a
Markdown file whose frontmatter declares stages with exit checks and approval
gates; the `agent-workflow` CLI evaluates those checks against the files of a
work unit and tells the agent which stage it is in, what is unmet and which
skill to open next. Claude Code, Codex and Antigravity read the same output.
Requires Python 3.12 or later; runtime dependencies are `agent-advisory`,
`agent-rule-engine`, `click` and `pyyaml`.

## Structure

```text
src/agent_workflow_engine/
├── config.py        # [workflow], [workflow.approvals] and [workflow.stages] from .devkit/config.toml
├── layout.py        # Work unit layout: unit_path template, discovery, per-definition layout spec
├── frontmatter.py   # Frontmatter read/update preserving other bytes
├── definition.py    # Workflow document parsing, validation, schema hash
├── checks.py        # Check registry: syntax, classes, primitives, aliases
├── envelope.py      # envelopes/<kind>-NN.yaml loading, review state and authoring
├── evaluate.py      # Stage evaluation, gates, --given, delegate, waiting
├── binding.py       # workflow / workflow_hash / workflow_history in the anchor file
├── decisions.py     # decisions/NN-<request>.yaml records answering human requests
├── render.py        # Sentinel text output
├── git.py           # merge-base ancestry for revision checks
└── cli/             # agent-workflow commands
```

## CLI usage

From this monorepo, run `just init`, then:

```bash
just workflow checks                                  # registered checks
just workflow validate                                # definitions under definitions_dir
just workflow new login-flow                          # create and bind a unit
just workflow next --unit .devkit/transient/work/login-flow
just workflow next --unit <dir> --given integration   # assert a gate after the user's OK
just workflow next --unit <dir> --format json
just workflow requests --unit <dir>                   # open human requests (approvals, choices)
just workflow answer --unit <dir> --request gate:integration --action accept
just workflow handoff --unit <dir>                    # continue a completed unit with the recorded or auto choice
just workflow show direct-delivery
just workflow list                                    # units across every layout in use
just workflow envelope new --unit <dir> --kind review # needs_input skeleton to fill in
just workflow envelope new --unit <dir> --kind review --summary "..." --findings-file findings.yaml --check tests="PASS 3/3"
just workflow envelope new --unit <dir> --kind reverify --from latest --resolve 1 --waive "2=accepted cost"
just workflow envelope check --unit <dir>             # every envelope file and any contract violation
```

To install directly in another project:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/agent-workflow-engine"
uv run agent-workflow next --unit <dir>
```

Exit codes: `0` success, `1` any error. Errors are Agent Advisory Protocol
blocks on stderr (`agent-advisory`) with a stable code such as
`WORKFLOW_DRIFT`, `UNIT_NOT_FOUND` or `CONFIG_INVALID` and an `[ACTION]`
directive; `--format json` also emits them on stdout. `next` exits `0` whether
or not the unit is complete.

## Configuration

Everything is optional and lives in the Git-tracked `.devkit/config.toml`:

```toml
[workflow]
work_dir = ".devkit/transient/work"   # root of work units
unit_path = "{slug}"                  # str.format template; {slug} and {date:%Y%m%d} only
anchor = "task.md"                    # file that identifies a unit and carries the binding
definitions_dir = ".devkit/workflows" # workflow definition files
default = "direct-delivery"           # used by `new` and by unbound units

[workflow.approvals]
direction = "auto"                    # ask (default) | auto | off
integration = "ask"
handoff = "ask"                       # reserved: who picks the next workflow of a completed unit

[workflow.stages]
collect-feedback = "off"              # on (default) | off: skip this stage id in every workflow
```

`ask` keeps a gated stage current and emits an `approve` request; the answer is
a decision record under `<unit>/decisions/` written by `agent-workflow answer`
(or by a host UI), while `next --given <gate>` remains as a non-persisted
assertion. `auto` passes the gate by policy and records it in the output.
`off` skips the stage. Lowering or raising a gate later is a change to this
table only. The request and record formats are the
[Human Interaction Contract](../../docs/workflow/human-interaction.md).

`[workflow.stages]` turns a stage off by id whether or not it has a gate.
`next` reports it as `[SKIPPED: <id> reason=stages.<id>=off]` and the stage
never blocks completion or handoff. Ids that no selected workflow uses are
allowed, since stage ids are shared across definitions.

Workflows chain. A definition's `next` list names candidate workflows with
`when` preconditions (check syntax) and a `recommended` flag. Once a unit
completes its workflow, `next` prints `[HANDOFF]` and one `[CANDIDATE]` line
per candidate with its eligibility, plus a `choose` request. Under
`handoff = "ask"` the person's choice is recorded with `answer --request
handoff --action accept --value <id>` (or passed as `handoff --workflow <id>`);
under `"auto"` the first eligible candidate is chosen. `handoff --unit <dir>`
then rebinds the unit, recording the finished segment in the anchor's
`workflow_history`.

## Workflow definitions

Definitions are discovered from the project's `definitions_dir` and from every
`kind = "workflow"` asset that `devkit sync` recorded in
`.devkit/installation.json`; a project definition shadows a synchronized one
with the same id. Bundles that ship a workflow also get the generated
`devkit-workflow` entry skill, so an agent knows to run `next`.

A definition declares `id`, `schema_version: 1`, optional `checks` (runner or
human checks it introduces), ordered `stages`, each with `exit` checks,
`skills`, `role`, `isolation`, `human_gate` and `returns`, an optional
`next` list of handoff candidates, and an optional `layout` that overrides
`work_dir`, `unit_path` or `anchor` for the units of that workflow, so one
repository can keep, for example, proposal bundles under `docs/proposals/`
and spec bundles under `specs/` as units of different workflows. Checks are
`name` or `name(arg ...)` from `agent-workflow checks`; aliases such as
`anchor-exists`, `tasks-all-checked` and `envelope-review-passed` resolve
against the configured anchor. `lint-clean` runs `agent-rule-engine` on the
unit's files. See [Workflow Definitions and Checks](../../docs/workflow/definition-and-checks.md)
for the schema, the check table, the envelope contract and the output signals.

## Library

```python
from pathlib import Path
from agent_workflow_engine import Options, evaluate, resolve

doc = resolve(Path(".devkit/workflows"), "direct-delivery")
result = evaluate(doc, Options(workspace_root=Path("."), unit_dir=Path("work/login").resolve(), anchor="task.md"))
print(result.stage.id if result.stage else "complete")
```

## Current limits

Only `TemplateLayout` exists; a plugin layout fits behind the `Layout`
protocol but is not loaded from a directory yet. A handoff to a workflow
whose anchor differs from the unit's is refused (`HANDOFF_LAYOUT_MISMATCH`);
moving a unit between layouts is the caller's job, followed by `bind`.
Subagent delegation names a role and isolation level only; the host
projection of that role belongs to `devkit-distribution`. `entry` checks are
reported, not evaluated.

## Architectural Specifications & Deep-Dives

- [Workflow Engine Overview](../../docs/workflow/overview.md): delivery model, layout template, approval gates, CLI surface and the relationship to specrig.
- [Workflow Definitions and Checks](../../docs/workflow/definition-and-checks.md): document schema, check registry, envelopes, binding and drift, output signals.
- [Human Interaction Contract](../../docs/workflow/human-interaction.md): request kinds, decision records, how answers are applied.
