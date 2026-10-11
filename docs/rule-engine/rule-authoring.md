# Rule Authoring Guide and Rule Protocol

**Status**: Architecture Specification & Developer Guide  
**Package**: `agent-rule-engine`  
**Related Documents**:
- [Rule Engine Overview](overview.md)
- [Evaluation Lifecycle](evaluation-lifecycle.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)

---

## 1. Rule Protocols and Contracts

All governance rules in `agent-rule-engine` implement Python `typing.Protocol` contracts defined in `agent_rule_engine.engine.models`.

### The `Rule` Protocol

```python
from typing import Protocol, runtime_checkable
from agent_rule_engine.engine.models import RuleContext, Violation, Phase, Severity

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

- `ctx.is_file_targeted(path)`: Returns `True` if the file is included in the current run targets.
- `ctx.cache.list_files(pattern)`: Scans repository files matching a glob pattern (cached).
- `ctx.cache.get_text(path)`: Returns the string content of a relative file path.
- `ctx.cache.get_lines(path)`: Returns lines of text with newline characters preserved.
- `ctx.cache.get_frontmatter(path)`: Parses and caches YAML frontmatter dictionaries.
- `ctx.cache.get_markdown_links(path)`: Extracts and returns parsed Markdown relative links.
- `ctx.cache.catalog`: Accesses indexed specification document IDs and cross-references.

---

## 3. Implementing a Custom Rule Example

Here is an example rule checking that markdown files under `docs/` have a level 1 heading:

```python
from pathlib import Path
from agent_rule_engine.engine.models import (
    RuleContext,
    Violation,
    Phase,
    Severity,
)

class DocHeadingRule:
    id = "DOC-001"
    name = "Document Title Heading"
    description = "Markdown documentation files must begin with an H1 heading."
    phase = Phase.LINTER
    severity = Severity.ERROR

    def check(self, ctx: RuleContext) -> list[Violation]:
        violations: list[Violation] = []
        for file_path in ctx.cache.list_files("docs/**/*.md"):
            if not ctx.is_file_targeted(file_path):
                continue

            text = ctx.cache.get_text(file_path)
            lines = text.strip().splitlines()
            if not lines or not lines[0].startswith("# "):
                violations.append(
                    Violation(
                        rule_id=self.id,
                        file=file_path,
                        line=1,
                        message="File must start with an '# <Title>' heading.",
                        remediation="Add an '# <Title>' heading to the first line.",
                        severity=self.severity,
                        phase=self.phase,
                    )
                )
        return violations
```

---

## 4. Built-in Rule Modules

The built-in rules reside in `agent_rule_engine.rules`:

| Module | Rule ID Prefix | Description |
| --- | --- | --- |
| `rules.specification` | `SPEC-*` | Verifies YAML frontmatter metadata, unique document IDs, and valid document cross-references. |
| `rules.markdown` | `MD-*` | Verifies that relative links in Markdown point to valid target files/anchors and fixes broken relative links. |
| `rules.hygiene` | `HYG-*` | Warns on excessive file line counts or unstructured scratch files. |

---

## 5. Registering and Executing Custom Rules

```python
from pathlib import Path
from agent_rule_engine import RuleContext, RuleRegistry, evaluate

registry = RuleRegistry()
registry.register(DocHeadingRule())

ctx = RuleContext(workspace_root=Path("."))
result = evaluate(ctx, registry=registry)

print(f"Total findings: {len(result.violations)}")
```
