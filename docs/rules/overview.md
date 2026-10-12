# Agent Rule Engine: Architecture Overview

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit.rules` (`devkit rules` CLI)  
**Related Documents**:
- [Evaluation Lifecycle](evaluation-lifecycle.md)
- [Rule Authoring Guide](rule-authoring.md)
- [Rules Reference](reference.md)
- [Commit Gate Overview](../gate/overview.md)
- [In-Repository Bundles](../distribution/in-repo-bundles.md)
- [Resource Taxonomy](../architecture/resource-taxonomy.md)
- [Architecture Overview](../architecture/overview.md)

---

## 1. Overview and Objectives

`devkit.rules` is a fast, deterministic governance verification engine designed for AI-collaborative codebases. It automates repository-level consistency checks, Markdown relative link validation, and code hygiene, and it executes the rules that bundles distribute for their own document models.

### Core Principles

1. **Deterministic Verification over LLM Hallucinations**: Enforce repository invariants (e.g., relative links, file sizes, committed secrets) with deterministic parsing rather than unreliable natural language prompts.
2. **No Built-in Document Model**: The engine does not know what a specification, a story or a decision record is. Identifier grammars, frontmatter schemas, target directories and cross-reference semantics belong to the bundle that defines those documents and arrive as `kind = "rule"` assets; the engine provides the cache, the Markdown file catalog, policy and execution.
3. **Session Caching & Fast Iteration**: Maintain an in-memory session cache of file lists, bytes, text, frontmatter metadata, and lightweight link structures to keep verification times sub-second.
4. **Safe, Convergent Autofixes**: Provide automated repairs that run in a single pass followed by a convergence recheck, ensuring fixes never enter infinite repair loops or leave partial broken states uninspected.
5. **Decoupled CLI & Library Integration**: Available both as a standalone command-line tool (`devkit rules`) and as an importable Python library with custom rule registries.

---

## 2. Subsystem Layout

The rule engine is implemented in `packages/devkit/src/devkit/rules/`:

```text
src/devkit/rules/
├── engine/                  # Core evaluation engine & contracts
│   ├── models.py            # Violation, RuleContext, Rule, Autofixable protocols
│   ├── config.py            # [rules] section of .devkit/config.toml (phase/severity overrides, settings)
│   ├── settings.py          # Typed per-rule settings, path-scoped overrides, resolver
│   ├── discovery.py         # Rule assets recorded by devkit sync in the installation receipt
│   ├── project.py           # run_project_rules: config, registry, context and evaluation in one call
│   ├── phases.py            # Effective phase resolution, overrides, promotions
│   ├── policy.py            # validate_policy: phase, severity and settings policy in one pass
│   ├── errors.py            # RulesError hierarchy: raised errors and collected RuleProblems with codes
│   ├── registry.py          # RuleRegistry & default_registry (plugin files via devkit.core.plugins)
│   └── evaluator.py         # Sequential rule evaluation, single autofix pass & convergence recheck
├── workspace/               # Shared file caching, Markdown file catalog and Git snapshots
│   ├── cache.py             # WorkspaceCache (file discovery, bytes, text, frontmatter, links)
│   ├── catalog.py           # DocumentCatalog (paths, basenames, frontmatter id/title/status)
│   ├── markdown.py          # Fences, inline links, count_tasks (the checklist counter shared with devkit.workflow)
│   └── snapshot.py          # Staged / CI Git trees materialized for gate evaluation
├── rules/                   # Built-in governance rules (repository-generic only)
│   ├── base.py              # Base rule helper class (settings, guide, promote_to)
│   ├── markdown/            # Relative link validation & repair
│   ├── hygiene/             # File length checks (typed settings, guide)
│   └── safety/              # Secret leak and generated artifact checks for snapshot gates
└── cli/                     # CLI entry point
    ├── commands.py          # Click commands: check, fix, phases and explain
    └── output.py            # Text and JSON rendering
```

---

## 3. Integration with Content Wheels and devkit

`devkit.rules` works hand-in-hand with `devkit`:
- **Content Wheels**: Rule packages can be bundled into Python content wheels (`kind = "rule"` assets) and installed via `uv`. `devkit sync` records each deployed rule file in `.devkit/installation.json`, and `devkit rules` loads them from the receipt without any flag.
- **Project Policy**: A consumer changes a distributed rule's phase, severity or settings only through `[rules]` in `.devkit/config.toml`; managed rule files are hash-checked and never edited in place.
- **Pre-commit & CI**: `devkit gate install` adds the built-in `rules-staged` pre-commit gate, which runs the same staged-tree evaluation as `devkit rules check --staged` through the library ([Commit Gate Overview](../gate/overview.md#2a-built-in-gates)); CI runs `devkit rules check --ci --base <ref>`. Both evaluate the exact Git tree, not the working directory, so the gate result cannot depend on unstaged or ignored files.

---

## 4. Shared Foundation

`devkit.rules` builds on `devkit.core` and never re-implements it: frontmatter is parsed with `devkit.core.frontmatter` (the same grammar the workflow engine reads), the installation receipt with `devkit.core.receipt`, Git commands run through `devkit.core.git.run_git`, snapshot paths are validated with `devkit.core.paths`, and custom rule files are loaded with `devkit.core.plugins` (atomic per file, classes in definition order). The CLI's default workspace root is `devkit.core.find_project_root` of the current directory.
