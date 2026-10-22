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

A rules run re-parses and re-walks every Python file even when almost none changed since the last run; the Python
rules dominate `devkit rules check` (about 2.9 s, Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files)). `SPEC-document-index-cache` showed that a content-keyed
on-disk memo of per-file parse results cuts a full load to about 17 % with identical results
(`ADR-content-keyed-document-parse-memo`).

Hypothesis: if a rule separates a per-file facts function (pure in the file's text) from its cross-file judgment, the
facts can persist between runs under a content digest and a rule version, so a run parses and walks only changed files.

## 2. Technical Spike Questions

- **Q1**: Which rules split cleanly into per-file facts and a cross-file judgment (`RULE-architecture` imports,
  `RULE-advisory-unique-code` code declarations, `RULE-usecase-boundaries`), and what does the rule contract add
  (a `facts` hook, a facts schema version)?
- **Q2**: Key, fingerprint, location, format and failure policy: reuse the document memo's decisions where they fit,
  and decide what invalidates facts when a rule's code changes.

## 3. Proposed Design & Impact

- An opt-in rule contract for per-file facts, persisted under `.devkit/transient/` with content-digest keys and a
  rule fingerprint; undeclared rules are unchanged.
- Results identical to a run without the cache under edits, renames, deletions, branch switches and rule changes.
- Measured against main after `PROP-shared-python-node-index`; Planning decides whether the remaining time justifies
  the contract change.

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
