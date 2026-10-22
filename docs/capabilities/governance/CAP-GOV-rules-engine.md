---
id: CAP-GOV-rules-engine
title: "Governance Rules Engine"
summary: "Deterministic static invariant verification, convergence checking, phases, and autofix engine."
area: governance
status: active
created_at: 2026-10-17
---

# [CAP-GOV-rules-engine] Agent Rule Engine: Architecture Overview

`devkit_agt.features.rules` (`devkit rules` CLI) is a deterministic governance engine: repository-level checks, relative Markdown link validation and repair, hygiene checks, and execution of the rules that bundles distribute for their own document models.
Related: `CAP-GOV-evaluation-lifecycle`, `CAP-GOV-rule-authoring`, [Rules Reference](../../development/reference/rules.md),
`CAP-GATE-commit-gates`, `CAP-DIST-in-repo-bundles`, `ARCH-08-2-resource-taxonomy`.

## 1. Principles

1. **Deterministic checks**: repository invariants (relative links, file sizes, committed secrets) are enforced by parsing, not by prompt instructions.
2. **No built-in document model**: the engine does not know what a specification, use case or decision record is. Identifier grammars, frontmatter schemas, target directories and cross-reference semantics belong to the bundle that defines those documents and arrive as `kind = "rule"` assets; the engine provides the cache, the Markdown file catalog, policy and execution. Built-in rules cover only what holds for any repository.
3. **Session caching**: one in-memory cache per evaluation session holds file lists, bytes, text, frontmatter and links.
4. **Convergent autofix**: one repair pass followed by one recheck, never a repair loop (`CAP-GOV-evaluation-lifecycle`).
5. **One evaluation path**: the CLI, the `rules-check` commit gate and the workflow engine's `lint-clean` check both call `run_project_rules`, so they cannot disagree on policy; target scoping lives in `evaluate_rules`, so they also agree on which rules explicit targets can affect (`CAP-GOV-evaluation-lifecycle`).

## 2. Subsystem Layout

```text
src/devkit_agt/features/rules/
├── engine/                  # Core evaluation engine & contracts
│   ├── models.py            # Violation, RuleContext, Rule, Autofixable protocols
│   ├── config.py            # [rules] section of .devkit/config.toml (phase/severity overrides, settings)
│   ├── settings.py          # Typed per-rule settings, path-scoped overrides, resolver
│   ├── discovery.py         # Rule assets recorded by devkit sync in the installation receipt
│   ├── project.py           # run_project_rules: config, registry, context and evaluation in one call
│   ├── phases.py            # Effective phase resolution, overrides, promotions
│   ├── policy.py            # validate_policy: inputs declarations, phase, severity and settings policy in one pass
│   ├── errors.py            # RulesError hierarchy: raised errors and collected RuleProblems with codes
│   ├── registry.py          # RuleRegistry & default_rule_registry (plugin packages via devkit_core.core.plugins)
│   ├── evaluator.py         # Target scoping, sequential rule evaluation, single autofix pass & convergence recheck
│   └── rule_tests.py        # rule_folder and run_rule_tests: each rule's tests/ in a pytest subprocess
├── testing.py               # load_rule, check, evaluate, opened_files: helpers for the tests in a rule's folder
├── workspace/               # Shared file caching, Markdown file catalog and Git snapshots
│   ├── cache.py             # WorkspaceCache (file discovery, bytes, text, frontmatter, links)
│   ├── catalog.py           # DocumentCatalog (paths, basenames, frontmatter id/title/status)
│   ├── markdown.py          # Fences, inline links, count_tasks (the checklist counter shared with devkit_agt.features.workflow)
│   └── snapshot.py          # Staged / CI Git trees for gate evaluation (in place or materialized)
├── rules/                   # Built-in governance rules (repository-generic only)
│   ├── base.py              # Base rule helper class (settings, guide, related, promote_to, inputs)
│   └── <name>/              # one folder per rule: rule.py, guide.md, tests/ (markdown_link, file_length,
│                            # secret_leak, clean_artifacts)
└── cli/                     # commands.py (check, fix, phases, explain, test) and output.py (text and JSON rendering)
```

Library callers import the public API from `devkit_agt.features.rules`; built-in rule classes are exported by `devkit_agt.features.rules.services.builtins`. The opt-in `authoring` bundle (size and wording rules with their tests, playbooks and the `agent-asset-writing` instruction) lives outside this module, in the data-only `devkit_agt.bundles.authoring` (`src/devkit_agt/bundles/authoring/bundle/`): its rules use only the public API and are loaded from the synchronized copies like any bundle rule, and discovering the bundle never imports the engine.

## 3. Integration with Content Wheels and devkit

- **Content wheels**: bundles ship rules as `kind = "rule"` assets; `devkit sync` records each deployed file in `.devkit/installation.json`, and `devkit rules` loads them from the receipt without any flag (`CAP-GOV-rule-authoring`).
- **Project policy**: a consumer changes a distributed rule's phase, severity or settings only through `[rules]` in `.devkit/config.toml`; managed rule files are hash-checked and never edited in place.
- **Pre-commit and CI**: the built-in `rules-check` commit gate evaluates what `devkit rules check --staged` evaluates on every commit, on by default once the hooks are installed (`CAP-GATE-commit-gates`); CI runs `devkit rules check --ci --base <ref>`. Both evaluate the exact Git tree, so the result cannot depend on unstaged or ignored files (`CAP-GOV-evaluation-lifecycle`).

## 4. Shared Foundation

`devkit_agt.features.rules` uses the shared foundation and distribution project support without reimplementing them: frontmatter is parsed with `devkit_core.core.frontmatter` (the grammar the workflow engine reads), the installation receipt with `devkit_dist.features.project.repositories.receipt`, Git commands run through `devkit_core.core.git.run_git`, snapshot paths are validated with `devkit_core.core.paths`, and rule packages are loaded with `devkit_core.core.plugins` (atomic per package, classes in module then definition order). `devkit rules test` runs each rule's tests through `devkit_agt.features.compact.run_command` (full log on disk, bounded view in the result), imported only when tests run. The CLI's default workspace root is `devkit_dist.features.project.repositories.project.find_project_root` of the current directory.
