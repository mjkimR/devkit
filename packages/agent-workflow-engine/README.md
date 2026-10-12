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
├── config.py        # [workflow] and [workflow.approvals] from .devkit/config.toml
├── layout.py        # Work unit layout: unit_path template, discovery
├── frontmatter.py   # Frontmatter read/update preserving other bytes
├── definition.py    # Workflow document parsing, validation, schema hash
├── checks.py        # Check registry: syntax, classes, primitives, aliases
├── envelope.py      # envelopes/<kind>-NN.yaml loading and review state
├── evaluate.py      # Stage evaluation, gates, --given, delegate, waiting
├── binding.py       # workflow / workflow_hash in the anchor file
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
just workflow show direct-delivery
just workflow list
just workflow envelope new --unit <dir> --kind review
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
```

`ask` keeps a gated stage current until `next --given <gate>` is passed after
the user's approval. `auto` passes the gate by policy and records it in the
output. `off` skips the stage. Lowering or raising a gate later is a change to
this table only.

## Workflow definitions

A definition declares `id`, `schema_version: 1`, optional `checks` (runner or
human checks it introduces) and ordered `stages`, each with `exit` checks,
`skills`, `role`, `isolation`, `human_gate` and `returns`. Checks are
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
protocol but is not loaded from a directory yet. Workflow definitions are read
from `definitions_dir`; shipping them as a distributed bundle asset kind is
planned. Subagent delegation names a role and isolation level only; the host
projection of that role belongs to `devkit-distribution`. `entry` checks are
reported, not evaluated.

## Architectural Specifications & Deep-Dives

- [Workflow Engine Overview](../../docs/workflow/overview.md): delivery model, layout template, approval gates, CLI surface and the relationship to specrig.
- [Workflow Definitions and Checks](../../docs/workflow/definition-and-checks.md): document schema, check registry, envelopes, binding and drift, output signals.
