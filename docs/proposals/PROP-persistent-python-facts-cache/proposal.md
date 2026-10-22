---
id: PROP-persistent-python-facts-cache
title: Persist per-file rule facts between runs
summary: "Lets Python-source rules declare a per-file facts function whose results persist between runs keyed by content digest, so a rules run parses and walks only changed files."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-persistent-python-facts-cache] Persist per-file rule facts between runs

## 1. Background & Hypothesis

While `SPEC-rule-shared-python-ast` and `SPEC-shared-python-node-index` eliminated redundant AST parsing and walking
within a single run (`WorkspaceCache._ast_cache` and `_nodes_cache`), every new CLI invocation (`devkit rules check`,
commit gates, workflow steps) is an independent process that starts cold. On `main` at `ae108957` (CPython 3.12, 826
tracked Python files, 539 parsed AST modules), initial AST parsing and type-indexed node collection take ~2,498 ms
(~2.5 s), accounting for ~41 % of the total ~6.0 s rule evaluation time (`docs/materials/2026-10/20261022-persistent-python-facts-cache/measurements.md`).
`SPEC-document-index-cache` showed that a content-keyed on-disk memo of per-file parse results cuts a full load to
about 17 % with identical results (`ADR-content-keyed-document-parse-memo`).

Hypothesis: if a rule separates a per-file facts function (pure in the file's text) from its cross-file judgment, the
facts can persist between runs under a content digest and a rule version, so a run parses and walks only changed files
and loads pre-extracted facts in < 1 ms.

## 2. Technical Spike Questions

- **Q1**: Which rules split cleanly into per-file facts and a cross-file judgment (`RULE-architecture` imports,
  `RULE-advisory-unique-code` code declarations, `RULE-usecase-boundaries`), and what does the rule contract add
  (a lifecycle `extract_file_facts` hook vs a `ctx.cache.get_file_facts` pull accessor, facts schema version)?
- **Q2**: Key, fingerprint, location, format and failure policy: reuse the document memo's decisions
  (`ADR-content-keyed-document-parse-memo`, `ADR-parse-memo-location-and-format`) where they fit, storing per-rule files
  at `.devkit/transient/rules/facts/<rule-id>.json`, and decide what invalidates facts when a rule's code changes
  (rule module source bytes hash + devkit version fingerprint).
- **Q3**: Interaction with Git snapshot runs (`dev-snapshot-scoped-rules`): can temporary snapshot directories
  (`/tmp/devkit-rules-snapshot-...`) safely read the host repository's transient facts cache in read-only mode using
  content-addressed digests to avoid cold re-parsing in commit gates?

## 3. Proposed Design & Impact

- An opt-in rule contract for per-file facts, persisted under `.devkit/transient/rules/facts/` with content-digest
  keys and a rule fingerprint; undeclared rules are unchanged.
- Results identical to a run without the cache under edits, renames, deletions, branch switches and rule changes.
- In-memory retention during evaluation via `ctx.cache.get_or_compute("rules.facts.<rule_id>", ...)` so subsequent passes
  and rechecks never re-read disk facts.
- Measured baseline on `main` confirms that cold AST parsing and node traversal cost ~2.5 s per fresh run; loading
  pre-extracted JSON facts takes ~0.84 ms (< 1 ms), cutting `devkit rules check` from ~6.0 s to ~1.8-2.0 s on an
  unchanged workspace and justifying the contract change.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr persistent-python-facts-cache "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept persistent-python-facts-cache --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff persistent-python-facts-cache.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
