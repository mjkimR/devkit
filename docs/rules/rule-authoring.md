# Rule Authoring Guide and Rule Protocol

Rule contracts, the workspace API rules read through, and where rules load from.
Related: [Rule Engine Overview](overview.md), [Evaluation Lifecycle](evaluation-lifecycle.md),
[Rules Reference](reference.md).

## 1. Rule Protocols and Contracts

Rules implement the `typing.Protocol` contracts in `devkit.rules.engine.models`.

### The `Rule` Protocol

```python
from typing import Protocol, runtime_checkable
from devkit.rules.engine.models import RuleContext, Violation, Phase, Severity

@runtime_checkable
class Rule(Protocol):
    id: str
    name: str
    description: str
    phase: Phase
    severity: Severity

    def check(self, ctx: RuleContext) -> list[Violation]:
        """Inspect the workspace and return any rule violations."""
        ...
```

`phase` is the rule's default phase; the evaluator applies project phase overrides before filtering, so a rule never inspects them ([Evaluation Lifecycle, section 4](evaluation-lifecycle.md#4-phase-transitions-overrides-and-promotions)). The evaluator sets each violation's `severity` and `phase` to the rule's effective values, so a rule does not pass them.

Any object satisfying the protocol can be passed to `RuleRegistry.register`. Rule files (section 5) contribute only the `BaseRule` subclasses they define.

### Optional `promote_to`

`BaseRule` accepts an optional `promote_to` (not part of the `Rule` protocol). Declare it on a `hygiene` rule meant to become a `linter` rule once the codebase is clean:

```python
from devkit.rules import Phase, Severity
from devkit.rules.rules import BaseRule

class NoTodoRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-no-todo",
            name="no-todo",
            description="TODO markers are tracked debt.",
            phase=Phase.HYGIENE,
            severity=Severity.WARNING,
            promote_to=Phase.LINTER,
        )
```

`promote_to` is only valid as `Phase.LINTER` on a `Phase.HYGIENE` rule; any other combination raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`) at construction, which makes the rule file a loading error. How the pending promotion is reported: [Evaluation Lifecycle, section 4](evaluation-lifecycle.md#rule-promotions-promote_to).

### Optional `settings` and `validate_settings`

`BaseRule.settings` holds a frozen dataclass instance with the rule's defaults. Its fields may be `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None` (the only fields that accept `null`); nested tables are not supported, and any other annotation is rejected when the rule is loaded. Gate settings use the same type checker (`devkit.rules.engine.settings.check_setting_value`). A project sets the values, globally or per path, in `[rules.settings.<RULE-id>]` ([Evaluation Lifecycle, section 5](evaluation-lifecycle.md#5-project-policy-severity-overrides-and-typed-settings)). Rules read the effective instance with `ctx.settings(self, path)`; without a resolver (library callers that skip `evaluate_rules`) the defaults are returned.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class FileLengthSettings:
    max_lines: int = 400
    extensions: list[str] = field(default_factory=lambda: [".md"])

class FileLengthRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(id="RULE-file-length", name="file-length-check", description="...",
                         phase=Phase.HYGIENE, severity=Severity.WARNING,
                         settings=FileLengthSettings(), guide="file_length.md")

    def validate_settings(self, settings: FileLengthSettings) -> None:
        if settings.max_lines <= 0:
            raise ValueError("max_lines must be a positive integer")

    def check(self, ctx: RuleContext) -> list[Violation]:
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=None):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            settings = ctx.settings(self, rel)
            ...
```

`validate_settings` raises `ValueError` for values the field types cannot express. It runs on the defaults, the configured values and every override layer (each applied to the configured values) before any rule executes. Several overrides matching one file are combined when `ctx.settings` is first called for it, and a rejected combination raises `SettingsError` (`RULES_SETTINGS_INVALID`). Results are memoized per combination of matching overrides.

### Optional `guide`

`guide` names a Markdown file relative to the module that defines the rule class. `devkit rules explain <RULE-id>` prints it and violation output cites its path, so the full remediation need not travel in every message. Built-in guides live next to their rules (for example `rules/hygiene/file_length.md`).

### The `Autofixable` Protocol

```python
@runtime_checkable
class Autofixable(Rule, Protocol):
    def fix(self, ctx: RuleContext) -> list[str]:
        """Apply safe deterministic fixes and return modified relative file paths."""
        ...
```

`fix` returns every workspace-relative path it modified; the evaluator invalidates those paths and rechecks ([Evaluation Lifecycle](evaluation-lifecycle.md#2-autofix-and-convergence)). Fixers write through `ctx.cache.write_text` and leave alone files `read_text_strict` rejects.

## 2. Rule Context and Workspace Cache

Rules read files through `ctx.cache`, not direct disk I/O:

- `ctx.is_file_targeted(path)`: `True` if the file is in the current run's targets. It is `False` for any path matched by `[rules] exclude`, even in a whole-workspace run, so a rule that scans with `find_files` must call it before reporting. `ctx.changed_files` already has excluded paths removed; `ctx.has_targets` says whether the run named explicit targets.
- `ctx.cache.find_files(root, extensions=(".md",))`: Sorted absolute paths of the regular files under `root` with one of `extensions` (`None` lists every file), with the target discovery of [Evaluation Lifecycle, section 3](evaluation-lifecycle.md#3-cli-execution-and-phases) (cached).
- `ctx.cache.read_text(path)` / `ctx.cache.read_bytes(path)`: Contents of a workspace-relative or absolute path (cached). `read_text` replaces undecodable bytes with U+FFFD; `read_text_strict(path)` returns `None` for a file that is not valid UTF-8, which a fixer must then leave alone.
- `ctx.cache.write_text(path, content)`: Writes exact UTF-8 bytes (no newline translation) and refreshes the cache; paths under `.devkit/managed/` and `.devkit/overrides/` are refused with `PinnedWriteError` (`RULES_PINNED_WRITE_REFUSED`).
- `ctx.cache.get_frontmatter(path)`: The YAML frontmatter mapping (`devkit.core.frontmatter` grammar) or `None`; raises `devkit.core.FrontmatterError` (`FRONTMATTER_INVALID`) for a malformed block.
- `ctx.cache.get_links(path)`: Inline Markdown links (`MarkdownLink`: `text`, `target` as written, `line`, `start`/`end` of the link and `target_start`/`target_end` of the destination on its line), skipping fenced code and code spans. `devkit.rules.extract_links(text)` does the same for a string.
- `ctx.cache.get_catalog(root)`: The `DocumentCatalog`: every Markdown path, a basename index for link repair, and the frontmatter `id`, `title` and `status` of each file recorded verbatim (with duplicate `id`s listed). A file whose frontmatter cannot be parsed is listed in `frontmatter_errors` instead of failing the run. It applies no identifier grammar and extracts no references; a rule that needs those parses the body itself.
- `ctx.settings(rule, path)`: The rule's effective settings for a workspace-relative or absolute path inside the workspace.
- `devkit.rules.count_tasks(text)`: `(checked, total)` Markdown checklist items, ignoring YAML frontmatter and fenced code. `devkit.workflow`'s `tasks-checked` check uses the same function, so a rule and a workflow gate never disagree.

## 3. Implementing a Custom Rule Example

This rule requires Markdown files under `docs/` to begin with a level 1 heading. As a `BaseRule` subclass it works both with `--rules-dir` and as a bundle's `kind = "rule"` asset:

```python
from devkit.rules import Phase, RuleContext, Severity, Violation
from devkit.rules.rules import BaseRule


class DocHeadingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-doc-heading",
            name="doc-heading",
            description="Markdown files under docs/ must begin with an H1 heading.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root / "docs", extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            lines = ctx.cache.read_text(path).strip().splitlines()
            if not lines or not lines[0].startswith("# "):
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=rel,
                        line=1,
                        message="File must start with an '# <Title>' heading.",
                        remediation="Add an '# <Title>' heading to the first line.",
                    )
                )
        return violations
```

Saved as `rules/doc_heading.py`, it runs with `devkit rules check --rules-dir rules`.

## 4. Built-in Rules

Built-in rules (`devkit.rules.rules`, catalog in the [Rules Reference](reference.md#built-in-rules)) are limited to invariants that hold for any repository. Rules about a particular documentation model (frontmatter schemas, identifier grammars, directory layouts, cross-references) ship in the bundle that owns that model, together with the guides and templates they cite, as `kind = "rule"` assets.

## 5. Rule Sources and Registration

`devkit rules` and `run_project_rules` load rules from three sources, in order; a rule with the same ID as an earlier one replaces it:

1. The built-in registry.
2. Every `.py` file listed under the `entrypoints` and `paths` of a `kind = "rule"` asset recorded by `devkit sync` in `.devkit/installation.json`, whatever its name; `devkit sync` deploys them under `.devkit/managed/<bundle>/`, and an override under `.devkit/overrides/` replaces the managed copy. Each file is verified as commit gate files are (`devkit.core.verified_asset_files`), in a plain run and in a Git snapshot alike: a file with a `files` entry in the receipt must match its SHA-256, and only a project override under `.devkit/overrides/` may lack one and is then loaded as it is. A listed file that does not exist, cannot be read, resolves outside the project, has no recorded hash outside `.devkit/overrides/` or differs from its hash is a loading error (`RULES_LOAD_FAILED`, exit code 2), not a silent skip: `devkit sync` restores the managed copy, and `devkit override create <bundle>:<asset>` keeps a deliberate edit as a project override. A project configures these rules only through `[rules]` in `.devkit/config.toml`.
3. `--rules-dir` (`rules_dir`): the Python files under it, in sorted path order; files and directories whose name starts with `_` or `.` are skipped (only this scan skips them).

Rule files are loaded with `devkit.core.plugins`: classes in definition order, imported classes ignored, every `BaseRule` subclass instantiated without arguments. A file that fails to import, or whose rule classes cannot be instantiated, contributes no rule and is a loading error. Rule files are executable Python and should come from a trusted source.

Registering and evaluating by hand:

```python
from pathlib import Path
from devkit.rules import RuleContext, RuleRegistry, evaluate_rules, resolve_managed_rules

registry = RuleRegistry()
registry.register(DocHeadingRule())
managed = resolve_managed_rules(Path("."))                   # rules synchronized by devkit
registry.discover_from_files(managed.paths)                   # managed.errors: RuleLoadError per malformed receipt or missing entry

ctx = RuleContext(workspace_root=Path("."))
result = evaluate_rules(ctx, registry.get_all())

print(f"Total findings: {len(result.violations)}")
```

`RuleContext` takes every argument by keyword; only `workspace_root` is required. Pass `cache=WorkspaceCache(root)` to share one cache across several evaluations; without it the context creates its own. A cache built for another root is refused. To run a project as `devkit rules check` does (policy, receipt rules and `rules_dir` together), call `run_project_rules` instead ([Rules Reference, Library](reference.md#library)).
