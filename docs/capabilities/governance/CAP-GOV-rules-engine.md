---
id: CAP-GOV-rules-engine
title: "Governance Rules Engine"
summary: "Deterministic static invariant verification, convergence checking and rule-owned per-file extraction reuse."
area: governance
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/rules/__init__.py
  - packages/devkit/src/devkit_agt/features/rules/usecases/project.py
created_at: 2026-10-17
---

# [CAP-GOV-rules-engine] Agent Rule Engine: Architecture Overview

`devkit_agt.features.rules` (`devkit rules` CLI) is a deterministic governance engine: repository-level checks, relative Markdown link validation and repair, hygiene checks, and execution of the rules that bundles distribute for their own document models.
Related: `CAP-GOV-evaluation-lifecycle`, `CAP-GOV-rule-authoring`, [Rules Reference](../../development/reference/rules.md),
`CAP-GATE-commit-gates`, `CAP-DIST-in-repo-bundles`, `ARCH-08-2-resource-taxonomy`.

## 1. Principles

1. **Deterministic checks**: repository invariants (relative links, file sizes, committed secrets) are enforced by parsing, not by prompt instructions.
2. **No built-in document model**: the engine does not know what a specification, use case or decision record is. Identifier grammars, frontmatter schemas, target directories and cross-reference semantics belong to the bundle that defines those documents and arrive as `kind = "rule"` assets; the engine provides the cache, the Markdown file catalog, policy and execution. Built-in rules cover only what holds for any repository.
3. **Session caching**: one in-memory cache per evaluation session holds file lists, bytes, text, frontmatter, links, parsed Python (one shared, read-only tree or remembered parse error per file) and indexed AST nodes by type, arbitrary computed run-scoped objects (`get_or_compute`), and resolves each path argument once until an invalidation.
4. **Convergent autofix**: one repair pass followed by one recheck, never a repair loop (`CAP-GOV-evaluation-lifecycle`).
5. **One evaluation path**: the CLI, the `rules-check` commit gate and the workflow engine's `lint-clean` check both call `run_project_rules`, so they cannot disagree on policy; target scoping lives in `evaluate_rules`, so they also agree on which rules explicit targets and snapshot diffs can affect (`CAP-GOV-evaluation-lifecycle`).

6. **Persistent extraction**: rule-owned per-file Python facts reuse syntax extraction across processes; discovery, current configuration and cross-file judgments run on every evaluation (`ADR-pull-per-file-python-facts`).

## 2. Subsystem Layout

```text
src/devkit_agt/features/rules/
├── models/                  # Rule/context contracts, settings, phases, snapshots and facts descriptors
├── repositories/
│   ├── config.py            # Project rules policy
│   ├── discovery.py         # Receipt-verified rule assets
│   └── workspace/
│       ├── cache.py         # Shared file/AST/node cache and public facts pull API
│       ├── file_facts.py    # Run-local facts identity and invalidation
│       ├── facts.py         # Source provenance and per-rule JSON stores
│       ├── catalog.py       # Markdown paths and frontmatter
│       ├── markdown.py      # Markdown links and task counting
│       └── snapshot.py      # Staged and CI Git trees
├── services/                # Evaluator, registry, rule-test helpers and built-in rules
├── usecases/                # Project assembly, snapshot capture and rule operations
└── cli/                     # Command adapters and text/JSON output
```

Library callers import the public API from `devkit_agt.features.rules`; built-in rule classes are exported by `devkit_agt.features.rules.services.builtins`. The opt-in `authoring` bundle (size and wording rules with their tests, playbooks and the `agent-asset-writing` instruction) lives outside this module, in the data-only `devkit_agt.bundles.authoring` (`src/devkit_agt/bundles/authoring/bundle/`): its rules use only the public API and are loaded from the synchronized copies like any bundle rule, and discovering the bundle never imports the engine.

## 3. Integration with Content Wheels and devkit

- **Content wheels**: bundles ship rules as `kind = "rule"` assets; `devkit sync` records each deployed file in `.devkit/installation.json`, and `devkit rules` loads them from the receipt without any flag (`CAP-GOV-rule-authoring`).
- **Project policy**: a consumer changes a distributed rule's phase, severity or settings only through `[rules]` in `.devkit/config.toml`; managed rule files are hash-checked and never edited in place.
- **Command help**: `devkit rules --help` lists the operating commands `check`, `fix` and `explain`. The authoring commands `phases` (`CAP-GOV-evaluation-lifecycle`) and `test` (`CAP-GOV-rule-authoring`) stay callable with their own `--help` but are hidden from the group help, as the workflow authoring commands are (`CAP-DLV-cli-and-output`).
- **Pre-commit and CI**: the built-in `rules-check` commit gate evaluates what `devkit rules check --staged` evaluates on every commit, on by default once the hooks are installed (`CAP-GATE-commit-gates`); CI runs `devkit rules check --ci --base <ref>`. Both evaluate the exact Git tree, so the result cannot depend on unstaged or ignored files (`CAP-GOV-evaluation-lifecycle`).

## 4. Shared Foundation

`devkit_agt.features.rules` uses the shared foundation and distribution project support without reimplementing them: frontmatter is parsed with `devkit_core.core.frontmatter` (the grammar the workflow engine reads), the installation receipt with `devkit_dist.features.project.repositories.receipt`, Git commands run through `devkit_core.core.git.run_git`, snapshot paths are validated with `devkit_core.core.paths`, and rule packages are loaded with `devkit_core.core.plugins` (atomic per package, classes in module then definition order). `devkit rules test` runs each rule's tests through `devkit_agt.features.compact.run_command` (full log on disk, bounded view in the result), imported only when tests run. The CLI's default workspace root is `devkit_dist.features.project.repositories.project.find_project_root` of the current directory.

## 5. Per-file Rule Facts

1. **Fresh judgment**: WHEN a rule pulls per-file facts, the engine MUST key persistent reuse by logical relative
   POSIX path, digest of the exact cached source bytes, canonical extraction context and executing-source fingerprint.
   `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`.
2. **Derived state**: IF a memo is absent, malformed, incompatible or inaccessible, THEN the engine MUST compute
   facts without adding advisories or changing findings, their order or exit status. Extractor programming failures
   retain normal rule execution semantics. `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`.
3. **Safe memo paths**: WHEN an explicitly enabled writer flushes, it MUST use atomic per-rule JSON replacement under
   an existing safe `.devkit/transient/`, rejecting symlinks and non-regular memo components.
   `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`.
4. **Persistence authority**: WHERE a project runs working-tree checks or fixes without dry run, the project use case
   MUST flush derived facts only after evaluation and rechecks finish without execution problems.
   `packages/devkit/tests/integration/features/rules/engine/test_project.py`.
5. **Bounded pruning**: WHEN a full untargeted working-tree evaluation flushes, it MUST prune only descriptors with
   an explicit complete logical path set. Partial runs and caught source failures preserve unseen entries.
   `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/tests/test_rule.py`.

The memo format is `version`, `fingerprint` and `entries`; each logical path maps to `digest`, canonical `context`
and rule-codec `payload`. The memo is trusted local derived state, not authenticated execution state.
Unchanged serialized bytes cause no replacement. Concurrent writers use last atomic replacement; lost entries cause
later misses. Stores remain loaded separately from computed judgments across invalidations.
`ADR-persist-python-facts-and-reuse-in-snapshots` owns the storage and writer policy.
