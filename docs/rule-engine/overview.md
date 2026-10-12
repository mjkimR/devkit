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

`agent-rule-engine` is a fast, deterministic governance verification engine designed for AI-collaborative codebases. It automates repository-level consistency checks, Markdown relative link validation, and code hygiene, and it executes the rules that bundles distribute for their own document models.

### Core Principles

1. **Deterministic Verification over LLM Hallucinations**: Enforce repository invariants (e.g., relative links, frontmatter syntax, file sizes) using AST and deterministic parsing rather than unreliable natural language prompts.
2. **No Built-in Document Model**: The engine does not know what a specification, a story or a decision record is. Identifier grammars, frontmatter schemas, target directories and cross-reference semantics belong to the bundle that defines those documents and arrive as `kind = "rule"` assets; the engine provides the cache, the Markdown file catalog, policy and execution.
3. **Session Caching & Fast Iteration**: Maintain an in-memory session cache of file lists, bytes, text, frontmatter metadata, and lightweight link structures to keep verification times sub-second.
4. **Safe, Convergent Autofixes**: Provide automated repairs that run in a single pass followed by a convergence recheck, ensuring fixes never enter infinite repair loops or leave partial broken states uninspected.
5. **Decoupled CLI & Library Integration**: Available both as a standalone command-line tool (`agent-rules`) and as an importable Python library with custom rule registries.

---

## 2. Subsystem Layout

The rule engine is implemented in `packages/agent-rule-engine/src/agent_rule_engine/`:

```text
src/agent_rule_engine/
├── engine/                  # Core evaluation engine & contracts
│   ├── models.py            # Violation, RuleContext, Rule, Autofixable protocols
│   ├── config.py            # [rules] section of .devkit/config.toml (phase/severity overrides, settings)
│   ├── settings.py          # Typed per-rule settings, path-scoped overrides, resolver
│   ├── discovery.py         # Rule assets recorded by devkit sync in the installation receipt
│   ├── phases.py            # Effective phase resolution, overrides, promotions
│   ├── registry.py          # RuleRegistry & default_registry
│   └── evaluator.py         # Policy validation, sequential rule evaluation & convergence recheck
├── workspace/               # Shared file caching, Markdown file catalog and Git snapshots
│   ├── cache.py             # WorkspaceCache (bytes, text, YAML frontmatter, links)
│   ├── catalog.py           # DocumentCatalog (paths, basenames, frontmatter id/title/status)
│   ├── markdown.py          # count_tasks: the checklist counter shared with agent-workflow-engine
│   └── snapshot.py          # Staged / CI Git trees materialized for gate evaluation
├── rules/                   # Built-in governance rules (repository-generic only)
│   ├── base.py              # Base rule helper class (settings, guide, promote_to)
│   ├── markdown/            # Relative link validation & repair
│   ├── hygiene/             # File length checks (typed settings, guide)
│   └── safety/              # Secret leak and generated artifact checks for snapshot gates
└── cli/                     # CLI entry point
    └── commands.py          # Click commands: check, fix, phases and explain
```

---

## 3. Integration with Content Wheels and devkit-distribution

`agent-rule-engine` works hand-in-hand with `devkit-distribution`:
- **Content Wheels**: Rule packages can be bundled into Python content wheels (`kind = "rule"` assets) and installed via `uv`. `devkit sync` records each deployed rule file in `.devkit/installation.json`, and `agent-rules` loads them from the receipt without any flag.
- **Project Policy**: A consumer changes a distributed rule's phase, severity or settings only through `[rules]` in `.devkit/config.toml`; managed rule files are hash-checked and never edited in place.
- **Pre-commit & CI**: Workspaces run `agent-rules check --staged` in pre-commit hooks and `agent-rules check --ci --base <ref>` in CI pipelines. Both evaluate the exact Git tree, not the working directory, so the gate result cannot depend on unstaged or ignored files.
