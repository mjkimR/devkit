---
id: CAP-GOV-rules-engine
title: "Governance Rules Engine"
summary: "Deterministic static verification, nonblocking change-scoped considerations, explicit changed-file context, convergence rechecks and rule-owned extraction reuse."
area: governance
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/rules/__init__.py
  - packages/devkit/src/devkit_agt/features/rules/usecases/project.py
  - packages/devkit/src/devkit_agt/features/rules/usecases/context.py
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

6. **Persistent extraction**: rule-owned per-file Python facts reuse syntax extraction across processes; discovery, current configuration and cross-file judgments run on every evaluation (`ADR-rules-run-workspace-cache`).

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
- **Command help**: `devkit rules --help` lists the operating commands `check`, `fix`, `context` and `explain`. The authoring commands `phases` (`CAP-GOV-evaluation-lifecycle`) and `test` (`CAP-GOV-rule-authoring`) stay callable with their own `--help` but are hidden from the group help, as the workflow authoring commands are (`CAP-DLV-cli-and-output`).
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
   an existing `.devkit/transient/`, on the safe memo path shared with the document parse memo
   (`devkit_core.core.memo`): no symbolic link, non-directory or directory that resolves elsewhere at any component
   from `.devkit/` down, and a regular file or none at the memo path. Readers refuse the same paths.
   `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`.
4. **Persistence authority**: WHERE a project runs working-tree checks or fixes without dry run, the project use case
   MUST flush derived facts only after evaluation and rechecks finish without execution problems.
   `packages/devkit/tests/integration/features/rules/engine/test_project.py`.
5. **Bounded pruning**: WHEN a full untargeted working-tree evaluation flushes, it MUST prune only descriptors with
   an explicit complete logical path set. Partial runs and caught source failures preserve unseen entries.
   `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/tests/test_rule.py`.

The memo format is exactly `version`, `fingerprint` and `entries` (a memo with any other top-level key is discarded);
each logical path maps to `digest`, canonical `context` and rule-codec `payload`. The memo is trusted local derived state, not authenticated execution state.
Unchanged serialized bytes cause no replacement. Concurrent writers use last atomic replacement; lost entries cause
later misses. Stores remain loaded separately from computed judgments across invalidations.
`ADR-rules-run-workspace-cache` owns the storage and writer policy.


## Explicit rule omissions

A rule MAY expose `omission(ctx) -> RuleOmission | None` through the optional applicability contract. Existing rules
without the hook execute unchanged. `RuleOmission(rule_id, code, reason)` identifies a deliberate omission, distinct
from target-scope `skipped` IDs and successful execution. The evaluator calls the hook for check and convergence
recheck candidates; fix writes and failed-fix unknown writes retain existing all-active rescoping behavior. A finding
of a rule the convergence recheck omits is reported as found, never `fixed`.

WHEN omissions exist, rules JSON MUST include `omissions: [{rule_id, code, reason}]` and text MUST emit one
`[RULE_OMITTED: <id> code=<code> reason=<reason>]` per omission, each value one sentinel field. Without omissions the
optional omissions field is absent. An omission does not suppress document rules or independent project checks.
Applicability errors, including a code that is not `UPPER_SNAKE`, are rule-execution errors, not omissions. `packages/devkit/tests/unit/features/rules/engine/test_scoping.py` enforces rescoping.


## Rule finding severity and explicit read context

1. **Nonblocking consideration**: WHEN an effective finding has `Severity.NOTICE`, the engine MUST retain it as a
   `Violation` with wire value `notice` without blocking ordinary, strict, commit-gate or workflow lint-clean checks.
   Existing `INFO = "info"`, warning and error behavior remains unchanged.
   Test: `packages/devkit/tests/integration/features/rules/engine/test_change_notices.py`.
2. **No repair obligation**: WHEN NOTICE findings render, text MUST use `status=consider` and summaries MUST include
   the separate `notices` count. NOTICE findings MUST NOT request or claim repair, enter remaining/promotion counts
   or invoke fixers at effective NOTICE severity. Invalid metadata is `RULES_EXECUTION_FAILED`.
   Tests: rules change-notice unit and integration tests.
3. **Explicit read companion**: WHEN `devkit rules context FILE` runs, it MUST return working-versus-HEAD change
   status, source identities and bounded old/new hunk evidence even without matching rules or findings. It evaluates
   only applicable change-scoped NOTICE rules. Unknown/outside/pinned targets are `RULES_TARGET_INVALID`;
   excluded files return `status=excluded` with no source excerpts or findings.
   Test: rules change-notice integration tests.
4. **Bounded excerpts**: WHEN read context contains changed text, it MUST return at most 20 hunks, 20 lines per side
   per hunk and 8192 UTF-8 source bytes, with omitted hunk/line/byte counts. JSON is one object with `file`, `change`,
   `hunks`, `findings`, `suppressed`, `omitted` and advisory `notices`; text uses `RULE_CONTEXT`, `CHANGE_HUNK`,
   `VIOLATION` and `SUMMARY` sentinels. Test: rules change-notice unit tests.
5. **Transient reminder suppression**: WHERE `--session TOKEN` is supplied, read context MUST suppress repeated
   delivered fingerprints only within the caller's token and never suppress hunk evidence. Fingerprints use the
   executing rule/settings, logical path and relevant construct/change bytes. An unrelated edit does not reissue the
   consideration; a relevant edit does. Ordinary checks and tokenless reads remain complete.
   Test: rules change-notice integration tests.
6. **Bounded memo failure**: WHEN a session reaches 24 hours or 2048 fingerprints, it MUST return unsuppressed
   findings with `RULE_READ_SESSION_EXPIRED`. IF safe memo read/lock/write fails, THEN it MUST return unsuppressed
   findings with `RULE_READ_SESSION_UNAVAILABLE`. The existing project lock serializes atomic memo writes under
   `.devkit/transient/rules/read-notices/`; memos retain only hashed token/fingerprints and delivery metadata.
   Test: rules change-notice integration tests.

Rule NOTICE findings and the result's advisory `notices` array are distinct. Rule warning/INFO findings remain
stdout results unaffected by `--strict`; advisory warnings preserve their existing strict behavior. Native file
reads do not invoke this companion. A crash after memo update and before host display can suppress a retry;
exactly-once model delivery is not claimed. `ADR-change-scoped-rule-notices` records this trade-off.
