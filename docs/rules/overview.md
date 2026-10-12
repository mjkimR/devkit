# Agent Rule Engine: Architecture Overview

`devkit.rules` (`devkit rules` CLI) is a deterministic governance engine: repository-level checks, relative Markdown link validation and repair, hygiene checks, and execution of the rules that bundles distribute for their own document models.
Related: [Evaluation Lifecycle](evaluation-lifecycle.md), [Rule Authoring Guide](rule-authoring.md), [Rules Reference](reference.md),
[Commit Gate Overview](../gate/overview.md), [In-Repository Bundles](../distribution/in-repo-bundles.md), [Resource Taxonomy](../architecture/resource-taxonomy.md).

## 1. Principles

1. **Deterministic checks**: repository invariants (relative links, file sizes, committed secrets) are enforced by parsing, not by prompt instructions.
2. **No built-in document model**: the engine does not know what a specification, story or decision record is. Identifier grammars, frontmatter schemas, target directories and cross-reference semantics belong to the bundle that defines those documents and arrive as `kind = "rule"` assets; the engine provides the cache, the Markdown file catalog, policy and execution. Built-in rules cover only what holds for any repository.
3. **Session caching**: one in-memory cache per evaluation session holds file lists, bytes, text, frontmatter and links.
4. **Convergent autofix**: one repair pass followed by one recheck, never a repair loop ([Evaluation Lifecycle, section 2](evaluation-lifecycle.md#2-autofix-and-convergence)).
5. **One evaluation path**: the CLI, the `rules-staged` commit gate and the workflow engine's `lint-clean` check all call `run_project_rules`, so they cannot disagree on policy.

## 2. Subsystem Layout

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
│   ├── registry.py          # RuleRegistry & default_rule_registry (plugin files via devkit.core.plugins)
│   └── evaluator.py         # Sequential rule evaluation, single autofix pass & convergence recheck
├── workspace/               # Shared file caching, Markdown file catalog and Git snapshots
│   ├── cache.py             # WorkspaceCache (file discovery, bytes, text, frontmatter, links)
│   ├── catalog.py           # DocumentCatalog (paths, basenames, frontmatter id/title/status)
│   ├── markdown.py          # Fences, inline links, count_tasks (the checklist counter shared with devkit.workflow)
│   └── snapshot.py          # Staged / CI Git trees materialized for gate evaluation
├── rules/                   # Built-in governance rules (repository-generic only)
│   ├── base.py              # Base rule helper class (settings, guide, promote_to)
│   ├── markdown/            # Relative link validation & repair
│   ├── hygiene/             # File length checks
│   └── safety/              # Secret leak and generated artifact checks for snapshot gates
├── authoring/bundle/        # The opt-in `authoring` bundle (size rules and playbooks)
└── cli/                     # commands.py (check, fix, phases, explain) and output.py (text and JSON rendering)
```

Library callers import the public API from `devkit.rules`; built-in rule classes are exported by `devkit.rules.rules`.

## 3. Integration with Content Wheels and devkit

- **Content wheels**: bundles ship rules as `kind = "rule"` assets; `devkit sync` records each deployed file in `.devkit/installation.json`, and `devkit rules` loads them from the receipt without any flag ([Rule sources](rule-authoring.md#5-rule-sources-and-registration)).
- **Project policy**: a consumer changes a distributed rule's phase, severity or settings only through `[rules]` in `.devkit/config.toml`; managed rule files are hash-checked and never edited in place.
- **Pre-commit and CI**: the built-in `rules-staged` pre-commit gate ([Commit Gate Overview](../gate/overview.md#2a-built-in-gates)) runs the same staged-tree evaluation as `devkit rules check --staged`; CI runs `devkit rules check --ci --base <ref>`. Both evaluate the exact Git tree, so the result cannot depend on unstaged or ignored files ([Evaluation Lifecycle, section 6](evaluation-lifecycle.md#6-git-snapshot-gates)).

## 4. Shared Foundation

`devkit.rules` builds on `devkit.core` and never re-implements it: frontmatter is parsed with `devkit.core.frontmatter` (the grammar the workflow engine reads), the installation receipt with `devkit.core.receipt`, Git commands run through `devkit.core.git.run_git`, snapshot paths are validated with `devkit.core.paths`, and rule files are loaded with `devkit.core.plugins` (atomic per file, classes in definition order). The CLI's default workspace root is `devkit.core.find_project_root` of the current directory.
