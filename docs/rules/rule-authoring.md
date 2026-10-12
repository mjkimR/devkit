# Rule Authoring Guide and Rule Protocol

**Status**: Architecture Specification & Developer Guide  
**Package**: `devkit.rules`  
**Related Documents**:
- [Rule Engine Overview](overview.md)
- [Evaluation Lifecycle](evaluation-lifecycle.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Rule Protocols and Contracts

All governance rules in `devkit.rules` implement Python `typing.Protocol` contracts defined in `devkit.rules.engine.models`.

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

`phase` is the rule's default phase. A project may move a `linter` rule to `hygiene` through `[rules.phase_overrides]` in `.devkit/config.toml`; the evaluator applies that override before filtering, so a rule never needs to inspect it. See [Evaluation Lifecycle, section 4](evaluation-lifecycle.md#4-phase-transitions-overrides-and-promotions).

Any object satisfying the protocol can be passed to `RuleRegistry.register`. Rule files loaded from `--rules-dir` or from the installation receipt contribute only the `BaseRule` subclasses they define, instantiated without arguments; a file that fails to import or whose classes cannot be instantiated contributes no rule and is reported as a loading error.

### Optional `promote_to`

`BaseRule` accepts an optional `promote_to` field. It is not part of the `Rule` protocol, so plain classes may omit it. Declare it on a `hygiene` rule that is meant to become a `linter` rule once the codebase is clean:

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

`promote_to` is only valid as `Phase.LINTER` on a `Phase.HYGIENE` rule; any other combination raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`) at construction, which makes the rule file a loading error. `devkit rules check --phase hygiene` reports the remaining violation count for every rule declaring a promotion, and `devkit rules phases` lists the pending transition.

### Optional `settings` and `validate_settings`

`BaseRule.settings` holds a frozen dataclass instance with the rule's defaults. Its fields may be `int`, `float`, `str`, `bool` or `list[str]`; any other annotation is rejected when the rule is loaded. A project changes the values, globally or per path, in `[rules.settings.<RULE-id>]` of `.devkit/config.toml` (see [Evaluation Lifecycle, section 5](evaluation-lifecycle.md#5-project-policy-severity-overrides-and-typed-settings)). Rules read the effective instance with `ctx.settings(self, path)`; without a resolver (library callers that skip `evaluate`) the defaults are returned.

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

`validate_settings` runs on the defaults, the configured values and every override layer (each applied to the configured values) before any rule executes; raise `ValueError` for values the field types cannot express. The evaluator reports the failure with the rule ID and stops. Several overrides matching the same file are combined when `ctx.settings` is first called for it; a combination that `validate_settings` rejects raises `SettingsError` (`RULES_SETTINGS_INVALID`), which the evaluator reports as `Invalid settings (RULE-id): ...`. Results are memoized per combination of matching overrides.

### Optional `guide`

`guide` names a Markdown file relative to the module that defines the rule class. `devkit rules explain <RULE-id>` prints it and violation output cites its path, so an agent can read the full remediation without the rule carrying it in every message. Built-in guides live next to their rules (for example `rules/hygiene/file_length.md`).

### The `Autofixable` Protocol

Rules that support automated deterministic repairs implement `Autofixable`:

```python
@runtime_checkable
class Autofixable(Rule, Protocol):
    def fix(self, ctx: RuleContext) -> list[str]:
        """Apply safe deterministic fixes and return modified relative file paths."""
        ...
```

---

## 2. Rule Context and Workspace Cache

Rules inspect files using `ctx.cache` rather than direct disk I/O to maximize performance:

- `ctx.is_file_targeted(path)`: Returns `True` if the file is included in the current run targets. It is `False` for any path matched by the project's `[rules] exclude` patterns, even in a whole-workspace run, so a rule that scans with `find_files` must call it before reporting. `ctx.changed_files` already has excluded paths removed; `ctx.has_targets` says whether the run named explicit targets at all.
- `ctx.cache.find_files(root, extensions=(".md",))`: Sorted absolute paths of the regular files under `root` with one of `extensions` (`None` lists every file). Dependency and cache directories, `.devkit/managed/` and `.devkit/overrides/`, symlinks resolving outside the workspace and, inside a Git work tree, Git-ignored files that are not explicit targets are skipped (cached).
- `ctx.cache.read_text(path)` / `ctx.cache.read_bytes(path)`: File contents for a workspace-relative or absolute path (cached). `read_text` replaces undecodable bytes with U+FFFD; `read_text_strict(path)` returns `None` for a file that is not valid UTF-8, which a fixer must then leave alone.
- `ctx.cache.write_text(path, content)`: Writes exact UTF-8 bytes (no newline translation) and refreshes the cache; paths under `.devkit/managed/` and `.devkit/overrides/` are refused with `PinnedWriteError` (`RULES_PINNED_WRITE_REFUSED`).
- `ctx.cache.get_frontmatter(path)`: The YAML frontmatter mapping (`devkit.core.frontmatter` grammar) or `None`; raises `devkit.core.FrontmatterError` (`FRONTMATTER_INVALID`) for a malformed block.
- `ctx.cache.get_links(path)`: Inline Markdown links (`MarkdownLink`: `text`, `target` as written, `line`, `start`/`end` of the link and `target_start`/`target_end` of the destination on its line), skipping fenced code and code spans. `devkit.rules.extract_links(text)` does the same for a string.
- `ctx.cache.get_catalog(root)`: Returns the `DocumentCatalog`: every Markdown path, a basename index for link repair, and the frontmatter `id`, `title` and `status` of each file recorded verbatim (with duplicate `id`s listed). A file whose frontmatter cannot be parsed is listed in `frontmatter_errors` instead of failing the run. It applies no identifier grammar and extracts no references; a rule that needs those parses the body itself.
- `ctx.settings(rule, path)`: The rule's effective settings for a workspace-relative or absolute path inside the workspace.
- `devkit.rules.count_tasks(text)`: Returns `(checked, total)` Markdown checklist items, ignoring YAML frontmatter and fenced code. `devkit.workflow` uses the same function for its `tasks-checked` check, so a rule about task completion and a workflow gate never disagree.

---

## 3. Implementing a Custom Rule Example

Here is an example rule checking that Markdown files under `docs/` begin with a level 1 heading. It subclasses `BaseRule`, so the same file works with `--rules-dir` and as a bundle's `kind = "rule"` asset (the loaders instantiate `BaseRule` subclasses without arguments):

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

Saved as `rules/doc_heading.py`, it runs with `devkit rules check --rules-dir rules`. The evaluator sets each violation's `severity` and `phase` to the rule's effective values, so a rule does not need to pass them.

---

## 4. Built-in Rule Modules

The built-in rules reside in `devkit.rules.rules`:

| Module | Rules | Phase | Description |
| --- | --- | --- | --- |
| `rules.markdown` | `RULE-markdown-link` | linter | Verifies that relative links in Markdown point to existing files and fixes broken relative links. |
| `rules.hygiene` | `RULE-file-length` | hygiene | Warns on excessive line counts; `max_lines` and `extensions` are typed settings. |
| `rules.safety` | `RULE-secret-leak`, `RULE-clean-artifacts` | linter | Flags credentials and generated artifacts among explicit targets, chiefly in `check --staged` / `--ci` gates. |

Built-in rules are deliberately limited to invariants that hold for any repository. Rules about a particular documentation model (frontmatter schemas, identifier grammars, directory layouts, cross-references between documents) are authored in the bundle that owns that model and distributed as `kind = "rule"` assets, as described in the next section.

---

## 5. Registering and Executing Custom Rules

```python
from pathlib import Path
from devkit.rules import RuleContext, RuleRegistry, evaluate, resolve_managed_rules

registry = RuleRegistry()
registry.register(DocHeadingRule())
managed = resolve_managed_rules(Path("."))                   # rules synchronized by devkit
registry.discover_from_files(managed.paths)                   # managed.errors: RuleLoadError per malformed receipt or missing entry

ctx = RuleContext(workspace_root=Path("."))
result = evaluate(ctx, registry.get_all())

print(f"Total findings: {len(result.violations)}")
```

`RuleContext` takes every argument by keyword; only `workspace_root` is required. Pass `cache=WorkspaceCache(root)` to share one cache across several evaluations; without it the context creates its own, so `ctx.cache` is always a `WorkspaceCache`. A cache built for another root is refused.

To run a project the way `devkit rules check` does (project policy, receipt rules and `--rules-dir` together), call `run_project_rules(Path("."), rules_dir=...)` instead; see the [reference](reference.md#library-and-custom-rules).

Rules distributed in a bundle (`kind = "rule"`) are plain Python files like the one above. `devkit sync` deploys them under `.devkit/managed/<bundle>/` and lists each file in the installation receipt; `devkit rules` loads them from there, and a project configures them through `[rules]` in `.devkit/config.toml` rather than by editing the managed copy.
