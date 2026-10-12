# Agent Rule Engine: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-rule-engine` (`agent-rules` CLI)  
**Related Documents**:
- [Evaluation Lifecycle](evaluation-lifecycle.md)
- [Rule Authoring Guide](rule-authoring.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Overview and Objectives

`agent-rule-engine` is a fast, deterministic governance and specification verification engine designed for AI-collaborative codebases. It automates repository-level consistency checks, Markdown relative link validation, specification metadata invariants, and code hygiene.

### Core Principles

1. **Deterministic Verification over LLM Hallucinations**: Enforce repository invariants (e.g., relative links, frontmatter syntax, document references, file sizes) using AST and deterministic parsing rather than unreliable natural language prompts.
2. **Session Caching & Fast Iteration**: Maintain an in-memory session cache of file lists, bytes, text, frontmatter metadata, and lightweight link structures to keep verification times sub-second.
3. **Safe, Convergent Autofixes**: Provide automated repairs that run in a single pass followed by a convergence recheck, ensuring fixes never enter infinite repair loops or leave partial broken states uninspected.
4. **Decoupled CLI & Library Integration**: Available both as a standalone command-line tool (`agent-rules`) and as an importable Python library with custom rule registries.

---

## 2. Subsystem Layout

The rule engine is implemented in `packages/agent-rule-engine/src/agent_rule_engine/`:

```text
src/agent_rule_engine/
├── engine/                  # Core evaluation engine & contracts
│   ├── models.py            # Violation, RuleContext, Rule, Autofixable protocols
│   ├── config.py            # [rules] section of .devkit/config.toml (phase overrides)
│   ├── phases.py            # Effective phase resolution, overrides, promotions
│   ├── registry.py          # RuleRegistry & default_registry
│   └── evaluator.py         # Sequential rule evaluation & convergence recheck
├── workspace/               # Shared file caching & document catalog
│   ├── cache.py             # WorkspaceCache (bytes, text, YAML frontmatter, links)
│   └── catalog.py           # WorkspaceCatalog (specs & docs indexes, references)
├── rules/                   # Built-in governance rules
│   ├── base.py              # Base rule helper class
│   ├── specification/       # Metadata, document IDs, and reference checks
│   ├── markdown/            # Relative link validation & repair
│   └── hygiene/             # File length & formatting checks
└── cli/                     # CLI entry point
    └── commands.py          # Click commands: check, fix and phases
```

---

## 3. Integration with Content Wheels and devkit-distribution

`agent-rule-engine` works hand-in-hand with `devkit-distribution`:
- **Content Wheels**: Rule packages can be bundled into Python content wheels and installed via `uv`.
- **Pre-commit & CI**: Workspaces run `just rules-check` or `just rules-fix` in CI pipelines and pre-commit hooks to guarantee repository integrity before merges.
