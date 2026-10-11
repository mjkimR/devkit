# agent-rule-engine

A sequential Python rule engine for specification documents and repository governance.
Requires Python 3.12 or later; runtime dependencies are `click` and `pyyaml`.

## Structure

```text
src/agent_rule_engine/
├── engine/                  # Rule contracts, registry, evaluation and autofix recheck
├── workspace/               # Shared file cache, parsing and document catalog
├── cli/                     # Click commands and output formatting
└── rules/
    ├── base.py              # Common rule implementation
    ├── specification/       # Frontmatter, identifiers and document references
    ├── markdown/            # Relative link validation and repair
    └── hygiene/             # File length checks
```

Tests live in `tests/` with the same feature groups. Library callers import the
public API from `agent_rule_engine`; built-in rule classes are exported by
`agent_rule_engine.rules`. Implementation modules live under the folders above.

## CLI usage

From this monorepo, run `just init`, then:

```bash
just rules-check
just rules-check --format json
just rules-check docs/stories/US-login.md
just rules-fix --dry-run
just rules-fix
just rules-check --phase hygiene
```

To install directly in another project:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/agent-rule-engine"
uv run agent-rules check --workspace-root .
```

`check` never writes files. `fix --dry-run` returns the initial fixable findings
without writes. `hygiene` includes linter rules as well as hygiene checks.
Exit code 1 indicates unresolved error violations, rule execution failures, or
custom rule loading failures. Warnings alone do not fail the command.
`--format json` emits an array of violations to stdout; execution and loading
errors are reported separately to stderr.

File arguments are exact workspace-relative paths or absolute paths inside the
workspace. An empty list checks the whole workspace. Relationship checks still
build the full `docs/` and `specs/` catalog, even when checking selected files.

## Library and custom rules

```python
from pathlib import Path
from agent_rule_engine import RuleContext, default_registry, evaluate

context = RuleContext(workspace_root=Path("."))
result = evaluate(context, default_registry().get_all())
```

Use `--rules-dir path/to/rules` to load Python files defining `BaseRule`
subclasses. Files load in sorted path order; imported classes are ignored.
Custom rules are executable Python and should come from a trusted source.
A custom rule with the same ID replaces a previously registered rule.

```python
from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


class ExampleRule(BaseRule):
    def __init__(self):
        super().__init__(id="RULE-example", name="example", description="Example check")

    def check(self, ctx: RuleContext) -> list[Violation]:
        return []
```

Autofix rules also implement `fix(ctx) -> list[str]`, returning every modified
workspace-relative file path. Use `ctx.cache` for shared reads and writes.
The evaluator invalidates returned paths after each fix and rechecks all active
rules once. A failed fix clears the cache and rechecks disk contents; it does
not roll back writes. Malformed frontmatter causes an execution error and
prevents the initial autofix pass from starting.

## Current limits

Caches live for one evaluation session. File discovery is cached and ignores
common dependency/cache directories. Markdown links use a lightweight regex
extractor with fenced/inline code skipping, not a full Markdown AST parser.
The runner checks working-tree files; Git snapshot evaluation, Go CLI IPC,
`rule.yaml` metadata and parallel workers are future work. Performance claims
require measurement; see the architecture notes for the experiment plan.
