---
id: CAP-GOV-rule-authoring
title: "Rule Authoring"
summary: "Protocols, workspace cache API, rule configuration, and custom rule development."
area: governance
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/rules/services/builtins/base.py
  - packages/devkit/src/devkit_agt/features/rules/services/testing.py
  - packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py
created_at: 2026-10-17
---

# [CAP-GOV-rule-authoring] Rule Authoring Guide and Rule Protocol

Rule contracts, the workspace API rules read through, where rules load from, and how a rule is tested.
Related: `CAP-GOV-rules-engine`, `CAP-GOV-evaluation-lifecycle`,
[Rules Reference](../../development/reference/rules.md).

## 1. Rule Protocols and Contracts

Rules implement the `typing.Protocol` contracts in `devkit_agt.features.rules.models.contracts`.

### The `Rule` Protocol

```python
from typing import Protocol, runtime_checkable
from devkit_agt.features.rules.models.contracts import RuleContext, Violation, Phase, Severity

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

`phase` is the rule's default phase; the evaluator applies project phase overrides before filtering, so a rule never inspects them (`CAP-GOV-evaluation-lifecycle`). The evaluator sets each violation's `severity` and `phase` to the rule's effective values, so a rule does not pass them.

Any object satisfying the protocol can be passed to `RuleRegistry.register`. Rule files (section 5) contribute only the `BaseRule` subclasses they define.

### Optional `promote_to`

`BaseRule` accepts an optional `promote_to` (not part of the `Rule` protocol). Declare it on a `hygiene` rule meant to become a `linter` rule once the codebase is clean:

```python
from devkit_agt.features.rules import Phase, Severity
from devkit_agt.features.rules.services.builtins import BaseRule

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

`promote_to` is only valid as `Phase.LINTER` on a `Phase.HYGIENE` rule; any other combination raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`) at construction, which makes the rule package a loading error. How the pending promotion is reported: `CAP-GOV-evaluation-lifecycle`.

### Optional `settings` and `validate_settings`

`BaseRule.settings` holds a frozen dataclass instance with the rule's defaults. Its fields may be `int`, `float`, `str`, `bool` or `list[str]`, each optionally `| None` (the only fields that accept `null`); nested tables are not supported, and any other annotation is rejected when the rule is loaded. Gate settings use the same type checker (`devkit_agt.features.rules.models.settings.check_setting_value`). A project sets the values, globally or per path, in `[rules.settings.<RULE-id>]` (`CAP-GOV-evaluation-lifecycle`). Rules read the effective instance with `ctx.settings(self, path)`; without a resolver (library callers that skip `evaluate_rules`) the defaults are returned.

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
                         settings=FileLengthSettings(), guide="guide.md")

    def validate_settings(self, settings: FileLengthSettings) -> None:
        if settings.max_lines <= 0:
            raise ValueError("max_lines must be a positive integer")

    def check(self, ctx: RuleContext) -> list[Violation]:
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=None):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            settings = ctx.settings(self, rel)
            ...
```

`validate_settings` (or the settings dataclass's `__post_init__`) raises `ValueError` for values the field types cannot express; every field must be an `init` field. Rejected project values are `RULES_SETTINGS_INVALID` as an `INPUT_ERROR`; rejected defaults, unresolvable field annotations and any other exception are the same code as `MAINTENANCE`, attributed to the rule. Validation runs on the defaults, the configured values and every override layer (each applied to the configured values) before any rule executes. Several overrides matching one file are combined when `ctx.settings` is first called for it, and a rejected combination raises `SettingsError` (`RULES_SETTINGS_INVALID`). Results are memoized per combination of matching overrides.

### Optional `guide`

`guide` names a Markdown file relative to the module that defines the rule class. `devkit rules explain <RULE-id>` prints it and violation output cites its path, so the full remediation need not travel in every message. Every rule, built in or distributed, is one directory: `rule.py` defines the class, `guide.md` beside it is the guide (`guide="guide.md"`) and `tests/` holds its tests (section 6), for example `devkit_agt/features/rules/services/builtins/file_length/`; a plugin rule's guide lives in its package directory, next to the module defining the class.

### Optional `related`

A guide explains a violation; the judgment or procedure behind the rule usually lives elsewhere: an instruction (the
policy the rule checks part of) or a playbook (the procedure that resolves its violations). `related` names them as
`<bundle>:<asset-id>`, and `devkit rules explain` prints each as
`[RELATED: <ref> kind=instruction|playbook path=<file>]`, the path being the file agents read (the project override,
else the managed copy, from the installation receipt). An entry that is not deployed is printed with `kind=- path=-`,
one of another kind or without a Markdown file with its `kind` and `path=-`, each with a `RULES_RELATED_UNRESOLVED`
notice; a receipt that cannot be read leaves every entry `kind=- path=-` with one such notice naming the receipt's
problem and fix. A malformed entry is `RULES_DEFINITION_INVALID` when the rule
loads. The guide then says when to read them instead of repeating them, and the instruction names the rule by ID
without repeating its checks.

```python
super().__init__(id="RULE-skill-document-size", ..., guide="guide.md", related=("authoring:skill-authoring",))
```

### Optional `inputs`

A rule that reads files beyond its targets, such as one that scans the whole workspace or reads a configuration file,
declares `inputs`: the workspace-relative patterns, in the `**` grammar of `[rules] exclude` (`match_path`), of every
file whose content can change its findings. A run with explicit working-tree targets skips the rule when no target
matches one of them (`CAP-GOV-evaluation-lifecycle`); whole-workspace runs and the Git snapshot gates always evaluate
it. `None`, the default, means any file can affect the rule: it runs in every run. A rule that reports only its
targets leaves `inputs` unset.

```python
super().__init__(id="RULE-architecture", ..., inputs=("**/*.py", "**/pyproject.toml", "**/bundle.toml",
                                                       ".devkit/architecture.toml"))
```

`inputs` is not part of the `Rule` protocol; the engine reads it with `getattr`. On `BaseRule` it must be `None` or a
non-empty tuple of patterns `validate_pattern` accepts; anything else (an empty tuple, a list, a string, an invalid
pattern) raises `RuleDefinitionError` (`RULES_DEFINITION_INVALID`) at construction, which makes the rule package a
loading error. A rule that satisfies the protocol without subclassing `BaseRule` and carries such a value fails policy
validation with the same code and its rule ID before any rule runs. A declaration that omits a file the rule reads
hides its findings from targeted runs on that file, so the rule's tests check it is complete (section 6).
`devkit rules explain` prints the declaration.

### Guide Format

A guide is what `devkit rules explain <RULE-id>` prints and what a violation cites, so an agent that hits a violation
reads it to decide what to do. Every guide, built in or distributed, uses the same sections:

```markdown
# [RULE-<id>] <Title>

## 1. Overview          what the rule guarantees and why; phase and severity; which files it checks and which not
## 2. Cause of Violation each condition reported, with its message
## 3. Remediation       the autofix, if any, what to do by hand, and when to read the `related` assets
## 4. Configuration     settings (type, default, meaning), path overrides; "no settings" when there are none
## 5. Exceptions        how a justified exception is recorded (path overrides, `[rules] exclude`, severity overrides)
## 6. Examples          optional
```

The built-in guides (`devkit_agt/features/rules/services/builtins/*/guide.md`) follow it.

### The `Autofixable` Protocol

```python
@runtime_checkable
class Autofixable(Rule, Protocol):
    def fix(self, ctx: RuleContext) -> list[str]:
        """Apply safe deterministic fixes and return modified relative file paths."""
        ...
```

`fix` returns every workspace-relative path it modified; the evaluator invalidates those paths and rechecks (`CAP-GOV-evaluation-lifecycle`). Fixers write through `ctx.cache.write_text` and leave alone files `read_text_strict` rejects.

## 2. Rule Context and Workspace Cache

Rules read files through `ctx.cache`, not direct disk I/O:

- `ctx.is_file_targeted(path)`: `True` if the file is in the current run's targets. It is `False` for any path matched by `[rules] exclude`, even in a whole-workspace run, so a rule that scans with `find_files` must call it before reporting. `ctx.changed_files` already has excluded paths removed; `ctx.has_targets` says whether the run named explicit targets, and `ctx.targets` holds them workspace-relative before exclusions. `ctx.relative_path(path)` gives the workspace-relative POSIX form of a relative or absolute path, `None` outside the workspace.
- `ctx.snapshot`: the Git snapshot a `check --staged` or `--ci` run evaluates (`devkit_agt.features.rules.Snapshot`: `mode` `staged` or `ci`, `base`, `changed` and `deleted` paths, the repository `root`), `None` for a working-tree run. Rules about diff evidence read it: a record that claims a file changed can be checked against `changed`, and a declaration naming a deleted path against `deleted`, even when the declaring file itself is not in the diff.
- `ctx.cache.find_files(root, extensions=(".md",))`: Sorted absolute paths of the regular files under `root` with one of `extensions` (`None` lists every file), with the target discovery of `CAP-GOV-evaluation-lifecycle` (cached).
- `ctx.cache.read_text(path)` / `ctx.cache.read_bytes(path)`: Contents of a workspace-relative or absolute path (cached). `read_text` replaces undecodable bytes with U+FFFD; `read_text_strict(path)` returns `None` for a file that is not valid UTF-8, which a fixer must then leave alone.
- `ctx.cache.write_text(path, content)`: Writes exact UTF-8 bytes (no newline translation), replacing the file atomically with its permission bits kept, and refreshes the cache; a path that resolves (symlinks followed) outside the workspace root is refused with `UnsafePathError` (`PATH_UNSAFE`), and paths under `.devkit/managed/` and `.devkit/overrides/` with `PinnedWriteError` (`RULES_PINNED_WRITE_REFUSED`).
- `ctx.cache.get_python_ast(path)`: The parsed `ast.Module` of a Python file, parsed once per run from its bytes as CPython reads source (a BOM and a PEP 263 coding cookie honoured), under its workspace-relative name (the resolved absolute path for a file outside the workspace). Every rule that asks receives the same tree, so a rule MUST NOT modify it; a rule that needs a changed tree parses its own copy (`ADR-share-one-read-only-parsed-tree-per-python-file`). A file that does not parse raises a fresh `SyntaxError` (or `ValueError`) of the same type and arguments on every call from one parse, and a missing file raises `FileNotFoundError`; each rule decides whether to report or skip it. A rule that reads Python source parses it through this accessor, not with `ast.parse` of its own (`ADR-parse-cached-bytes-once-and-memoize-the-outcome`).
- `ctx.cache.get_python_nodes(path, *types)`: Nodes of the requested `ast.AST` types from a Python file, in document traversal order, built once per file on first request from `get_python_ast(path)`. Callers receive a shared immutable tuple of matching nodes and MUST NOT modify them (`ADR-index-python-ast-nodes-by-type-in-workspacecache`). Raises `ValueError` when no types are passed, and re-raises any syntax error from `get_python_ast`. A rule that queries specific node types calls this accessor instead of walking the tree itself.
- `ctx.cache.get_frontmatter(path)`: The YAML frontmatter mapping (`devkit_core.core.frontmatter` grammar) or `None`; raises `devkit_core.base.errors.FrontmatterError` (`FRONTMATTER_INVALID`) for a malformed block.
- `ctx.cache.get_links(path)`: Inline Markdown links (`MarkdownLink`: `text`, `target` as written, `line`, `start`/`end` of the link and `target_start`/`target_end` of the destination on its line), skipping fenced code and code spans. `devkit_agt.features.rules.extract_links(text)` does the same for a string.
- `ctx.cache.get_catalog(root)`: The `DocumentCatalog`: every Markdown path, a basename index for link repair, and the frontmatter `id`, `title` and `status` of each file recorded verbatim (with duplicate `id`s listed). A file whose frontmatter cannot be parsed is listed in `frontmatter_errors` instead of failing the run. It applies no identifier grammar and extracts no references; a rule that needs those parses the body itself.
- `ctx.settings(rule, path)`: The rule's effective settings for a workspace-relative or absolute path inside the workspace.
- `devkit_agt.features.rules.count_tasks(text)`: `(checked, total)` Markdown checklist items, ignoring YAML frontmatter and fenced code. `devkit_agt.features.workflow`'s `tasks-checked` check uses the same function, so a rule and a workflow gate never disagree.

## 3. Implementing a Custom Rule Example

A custom rule is a **plugin package**: a directory holding the rule module, any helper modules, the rule's guide, resources and tests. The same directory works with `--rules-dir` and as a bundle's `kind = "rule"` asset:

```text
rules/
  doc_heading/
    __init__.py          # optional: runs first as the package module when present
    rule.py              # the rule class
    headings.py          # helper module, imported relatively
    guide.md             # the guide (guide="guide.md")
    tests/
      test_rule.py       # tests beside the code; never imported by devkit's loaders (section 6)
```

Every `.py` file of the directory, recursively, is a module of one package, except files under a `tests` directory, `test_*.py` and `*_test.py` files, `__pycache__` and hidden entries. Modules import each other relatively (`from .headings import starts_with_h1`, `from .sub import x`), also lazily inside functions at run time; they cannot import a file that is not part of the package. Any other installed package (such as `devkit` itself) is imported absolutely.

This rule requires Markdown files under `docs/` to begin with a level 1 heading. The helper module `headings.py`:

```python
def starts_with_h1(text: str) -> bool:
    """Whether the first non-blank line of ``text`` is a level 1 heading."""
    lines = text.strip().splitlines()
    return bool(lines) and lines[0].startswith("# ")
```

The rule module `rule.py`:

```python
from devkit_agt.features.rules import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.services.builtins import BaseRule

from .headings import starts_with_h1


class DocHeadingRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-doc-heading",
            name="doc-heading",
            description="Markdown files under docs/ must begin with an H1 heading.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            guide="guide.md",
        )

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root / "docs", extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            if not starts_with_h1(ctx.cache.read_text(path)):
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

Saved as `rules/doc_heading/`, it runs with `devkit rules check --rules-dir rules`, and its tests with `devkit rules test RULE-doc-heading --rules-dir rules` (section 6).

## 4. Built-in Rules

Built-in rules (`devkit_agt.features.rules.services.builtins`, catalog in the [Rules Reference](../../development/reference/rules.md#built-in-rules)) are limited to invariants that hold for any repository. Rules about a particular documentation model (frontmatter schemas, identifier grammars, directory layouts, cross-references) ship in the bundle that owns that model, together with the guides and templates they cite, as `kind = "rule"` assets.

## 5. Rule Sources and Registration

`devkit rules` and `run_project_rules` load rules from three sources, in order; a rule with the same ID as an earlier one replaces it:

1. The built-in registry.
2. Every `kind = "rule"` asset recorded by `devkit sync` in `.devkit/installation.json`, each one plugin package. A bundle declares the asset's `source` as the package directory (`BUNDLE_INVALID` for a file); `devkit sync` deploys it under `.devkit/managed/<bundle>/`, and a project override under `.devkit/overrides/<bundle>/` replaces the managed copy of each file it overrides, so one package may mix overridden and managed modules. Every module file listed under the asset's `paths` (whatever its name, test files excepted) is verified as commit gate files are (`devkit_dist.features.project.repositories.receipt.verified_asset_packages`), in a plain run and in a Git snapshot alike: a file with a `files` entry in the receipt must match its SHA-256, and only a project override under `.devkit/overrides/` may lack one and is then loaded as it is. A listed file that does not exist, cannot be read, resolves outside the project, has no recorded hash outside `.devkit/overrides/` or differs from its hash is a loading error (`RULES_LOAD_FAILED`, exit code 2), not a silent skip, and its package is not loaded: `devkit sync` restores the managed copy, and `devkit override create <bundle>:<asset>` keeps a deliberate edit as a project override. A project configures these rules only through `[rules]` in `.devkit/config.toml`.
3. `--rules-dir` (`rules_dir`): each immediate subdirectory is one plugin package, in sorted order; subdirectories whose name starts with `_` or `.`, and a `tests` directory, are skipped. A `.py` file directly in the directory is a loading error (`RULES_LOAD_FAILED`) whose fix moves it into `<rules-dir>/<name>/`.

Rule packages are loaded with `devkit_core.core.plugins`: every module of the package is imported (the package module first, then its submodules in sorted order), and every concrete `BaseRule` subclass defined in one of them is instantiated without arguments, in module then definition order; classes imported from elsewhere are ignored and a class re-exported by another module of the package counts once. Loading is atomic per package: a package any module of which fails to import, or whose rule classes cannot be instantiated, contributes no rule and is one loading error naming the package. Rule packages are executable Python and should come from a trusted source.

Registering and evaluating by hand:

```python
from pathlib import Path
from devkit_agt.features.rules import RuleContext, RuleRegistry, evaluate_rules, resolve_managed_rules

registry = RuleRegistry()
managed = resolve_managed_rules(Path("."))                    # rules synchronized by devkit
registry.discover_from_packages(managed.packages)              # managed.errors: RuleLoadError per malformed receipt or unusable file
registry.discover_from_dir(Path("rules"))                      # registry.errors: RuleLoadError per package that fails to load

ctx = RuleContext(workspace_root=Path("."))
result = evaluate_rules(ctx, registry.get_all())

print(f"Total findings: {len(result.violations)}")
```

`RuleContext` takes every argument by keyword; only `workspace_root` is required. Pass `cache=WorkspaceCache(root)` to share one cache across several evaluations; without it the context creates its own. A cache built for another root is refused. To run a project as `devkit rules check` does (policy, receipt rules and `rules_dir` together), call `run_project_rules` instead ([Rules Reference, Library](../../development/reference/rules-library.md)).

## 6. Testing a Rule

A rule's tests live in its folder, `<rule folder>/tests/`, so they travel with the rule: a bundle's `kind = "rule"`
asset deploys them with the code (`devkit sync` records them in the receipt), and the plugin loader never imports
anything under `tests/` or named `test_*.py`/`*_test.py`. Leave `tests/` without an `__init__.py`; pytest imports the
files by path (`--import-mode=importlib`). The built-in rules follow the same layout
(`devkit_agt/features/rules/services/builtins/<name>/tests/test_rule.py`), as do the `authoring` bundle's rules.

`devkit_agt.features.rules.services.testing` loads and evaluates a rule as devkit does ([Rules Reference, Rule tests](../../development/reference/rules-library.md#rule-tests)):

- `load_rule(__file__)` loads the folder above `tests/` as a plugin package, exactly as a deployed copy is loaded, and
  returns its rule (`load_rule(__file__, "RULE-x")` when the package defines several). The tests of a deployed copy
  therefore test the rule devkit runs: the managed copy with each module file of a project override
  (`.devkit/overrides/<bundle>/...`) in place of the managed one, whether the tests sit in the managed copy or in the
  override. With an installation receipt only the module files it lists for the rule are loaded, verified against
  their hashes as `devkit rules check` verifies them, so a stray file in either folder is never imported and a
  drifted managed copy fails to load (`RULES_LOAD_FAILED`, fix: `devkit sync`). An override that holds no `tests/` keeps the managed copy's, and they run against the overridden modules.
  A built-in rule is an importable module: its tests construct it directly.
- `check(rule, root, files, ...)` writes `files` under `root` (pytest's `tmp_path`), evaluates the rule alone with
  `evaluate_rules` and returns its violations; `targets`, `fix`, `dry_run`, `phase`, `settings` (the
  `[rules.settings.<RULE-id>]` values, path overrides under `"overrides"`) and `exclude` (`[rules] exclude`)
  match a project run. A run that reports
  problems (settings that do not type-check, a rule that raises) raises `RulesRunError` with them; `evaluate` returns
  the whole `EvaluationResult` instead, to assert on those problems and on `skipped`.
- `opened_files(root)` records the workspace files opened while it is active. A rule declaring `inputs` tests that a
  documentation-only target set skips it, that a target matching each pattern reports a seeded violation, and that
  every file a whole-workspace check opens matches one of its patterns.

```python
# rules/doc_heading/tests/test_rule.py
from devkit_agt.features.rules.services.testing import check, load_rule

RULE = load_rule(__file__)


def test_a_document_without_a_heading_is_reported(tmp_path):
    found = check(RULE, tmp_path, {"docs/a.md": "text\n", "docs/b.md": "# B\n", "README.md": "text\n"})
    assert [(v.file, v.line) for v in found] == [("docs/a.md", 1)]


def test_only_targets_are_checked(tmp_path):
    files = {"docs/a.md": "text\n", "docs/c.md": "text\n"}
    assert [v.file for v in check(RULE, tmp_path, files, targets=["docs/c.md"])] == ["docs/c.md"]
```

`devkit rules test [RULE-id]...` runs the tests of the named rules (every rule when none is named), resolved as for
`devkit rules explain`: built in, synchronized (the managed copy, or a project override's copy when the rule class is
defined there) and `--rules-dir`. Each tests directory runs in a pytest subprocess from the workspace root, writing
neither bytecode nor a pytest cache next to the tests; arguments after `--` go to pytest
(`devkit rules test RULE-doc-heading --rules-dir rules -- -k heading -x`). pytest must be importable by the interpreter
running devkit (`RULES_TEST_UNAVAILABLE` otherwise: `uv add --dev pytest`). Output and exit codes:
[Rules Reference](../../development/reference/rules.md#cli-usage).
