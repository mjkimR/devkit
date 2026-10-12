# agent-rule-engine

A sequential Python rule engine for specification documents and repository governance.
Requires Python 3.12 or later; runtime dependencies are `click` and `pyyaml`.

## Structure

```text
src/agent_rule_engine/
├── engine/                  # Rule contracts, registry, config, settings, phases, evaluation and autofix recheck
│   ├── discovery.py         # Rule assets recorded by devkit sync in .devkit/installation.json
│   └── settings.py          # Typed per-rule settings with path-scoped overrides
├── workspace/               # Shared file cache, parsing, document catalog and Git snapshots
├── cli/                     # Click commands and output formatting
└── rules/
    ├── base.py              # Common rule implementation (settings, guide, promote_to)
    ├── specification/       # Frontmatter, identifiers and document references
    ├── markdown/            # Relative link validation and repair
    ├── hygiene/             # File length checks
    └── safety/              # Secrets and generated artifacts in the files under check
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
just rules-check --staged                      # the exact staged tree (pre-commit gate)
just rules-check --ci --base origin/main       # HEAD against its merge base (CI gate)
just rules-fix --dry-run
just rules-fix
just rules-check --phase hygiene
just rules-phases
just rules-explain RULE-file-length
```

To install directly in another project:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/agent-rule-engine"
uv run agent-rules check --workspace-root .
```

`check` never writes files. `fix --dry-run` returns the initial fixable findings
without writes. `hygiene` includes linter rules as well as hygiene checks.
`phases` prints each rule's default and effective phase without evaluating.
`explain <RULE-id>` prints a rule's phase, severity, effective settings and its
guide document. Exit code 1 indicates unresolved error violations, rule
execution failures, custom rule loading failures, or invalid project policy.
Warnings alone do not fail the command. `--format json` emits an array of
violations to stdout; execution and loading errors are reported separately to
stderr.

File arguments are exact workspace-relative paths or absolute paths inside the
workspace. An empty list checks the whole workspace. Relationship checks still
build the full `docs/` and `specs/` catalog, even when checking selected files.

## Git snapshot gates

`check --staged` evaluates the Git index (what a commit would contain) and
`check --ci --base <ref>` evaluates `HEAD` against its merge base with `<ref>`.
Both read the tree from Git, materialize it into a temporary directory and run
the linter phase there, with the changed files of the diff as targets. Unstaged
edits, untracked files and local-only configuration cannot change the result:
`.devkit/config.toml`, the installation receipt and synchronized rules are all
taken from the snapshot. Snapshot gates refuse file arguments, `--phase hygiene`
and `fix`. A snapshot with no changed files passes without evaluating. The text
output starts with a `[SNAPSHOT: mode=... changed=N deleted=M]` line.

Two built-in linter rules exist for these gates and inspect explicit targets
only: `RULE-secret-leak` (credential files and private key, AWS, GitHub and
`sk-` token patterns) and `RULE-clean-artifacts` (compiled binaries, database
files, logs above 1 MiB). A run without targets reports nothing for them.

## Project configuration

Everything lives in the Git-tracked `.devkit/config.toml` under `[rules]`:

```toml
[rules.phase_overrides]
RULE-markdown-link = "hygiene"          # only "hygiene": park a linter rule while debt is cleared

[rules.severity_overrides]
RULE-file-length = "error"              # error | warning | info

[rules.settings.RULE-file-length]       # typed settings declared by the rule
max_lines = 300
extensions = [".md"]

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"               # workspace-relative; ** matches zero or more segments
max_lines = 800
```

Entries for unknown rules, redundant overrides, unknown settings keys, wrong
types and invalid patterns fail the run before any rule executes, with the rule
ID in the message. Later matching overrides win and omitted keys inherit the
earlier value. Because managed files are hash-checked by `devkit sync`, this
table is the only place a project changes a distributed rule's behavior.

### Phase overrides and promotions

The `linter` phase is the gate for hooks and CI. To adopt a rule against a
codebase that already violates it, park it in `hygiene` while the debt is
cleared, then return it once `check --phase hygiene` reports `remaining=0`:

- A project moves a built-in or custom `linter` rule to `hygiene` through
  `[rules.phase_overrides]`. Only `"hygiene"` is accepted.
- A rule author declares a new `hygiene` rule with `promote_to=Phase.LINTER`
  to record that it becomes a linter rule once clean.

`check --phase hygiene` prints a `[PHASE_OVERRIDE: ...]` or `[PROMOTION: ...]`
line per pending transition with its remaining count. `agent-rules phases`
lists the full plan, and `--format json` emits one object per rule. Details are
in [Evaluation Lifecycle](../../docs/rule-engine/evaluation-lifecycle.md).

## Synchronized rules

Rules shipped by a bundle (`kind = "rule"`) are recorded by `devkit sync` in
`.devkit/installation.json`. `agent-rules` loads every `.py` file listed under
such an asset (an override under `.devkit/overrides/` replaces the managed
copy) after the built-in rules and before `--rules-dir`, so no flag is needed.
A rule with the same ID as an earlier one replaces it.

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

```python
from dataclasses import dataclass, field

from agent_rule_engine import RuleContext, Violation
from agent_rule_engine.rules import BaseRule


@dataclass(frozen=True)
class BannedWordsSettings:
    banned: list[str] = field(default_factory=lambda: ["TODO"])


class BannedWordsRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-banned-words",
            name="banned-words",
            description="Banned markers in documentation",
            settings=BannedWordsSettings(),
            guide="banned_words.md",
        )

    def validate_settings(self, settings: BannedWordsSettings) -> None:
        if not settings.banned:
            raise ValueError("banned must list at least one word")

    def check(self, ctx: RuleContext) -> list[Violation]:
        out = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: BannedWordsSettings = ctx.settings(self, rel)
            if any(word in ctx.cache.read_text(path) for word in settings.banned):
                out.append(Violation(self.id, rel, 1, "banned marker"))
        return out
```

`settings` is a frozen dataclass instance carrying the defaults; its fields may
be `int`, `float`, `str`, `bool` or `list[str]`. `ctx.settings(rule, path)`
returns the effective instance for a file after project overrides.
`validate_settings` rejects values the types alone cannot express. `guide` names
a Markdown file next to the rule module that `explain` prints and violations
cite.

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
Settings fields are scalars and string lists; nested tables are not supported.
Snapshot gates materialize the whole tree, which is proportional to repository
size. Phase overrides can only move a rule to `hygiene`; promoting a rule to
`linter` is done by editing its declared phase. Parallel workers are future work.

## Architectural Specifications & Deep-Dives

Detailed technical designs and protocols are documented in `docs/rule-engine/`:

- [Rule Engine Architecture Overview](../../docs/rule-engine/overview.md): Core subsystems, workspace cache, and document catalog.
- [Evaluation Lifecycle & Convergence](../../docs/rule-engine/evaluation-lifecycle.md): Phased checks, project policy, snapshot gates, single-pass autofix, and convergence verification.
- [Rule Authoring Guide](../../docs/rule-engine/rule-authoring.md): Protocols, settings, guides, finding models, cache APIs, and custom rule implementation.
- [Resource Taxonomy](../../docs/architecture/resource-taxonomy.md): Governance rules within the multi-tier agent asset taxonomy.
