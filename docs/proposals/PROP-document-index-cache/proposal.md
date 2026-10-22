---
id: PROP-document-index-cache
title: Reuse the document index between commands
summary: "Caches the Living Spec document index on disk, keyed by each file's identity, so lookups such as devkit spec resolve and list stop re-reading every document on each call."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: documents/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/documents/
    - docs/capabilities/documents/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-document-index-cache] Reuse the document index between commands

## 1. Background & Hypothesis

`devkit spec resolve <ID>` takes about 430 ms and `devkit spec list feedback` about 530 ms (Measured on main at 4dbf9c4b (macOS, Python 3.12, this repository: about 820 tracked Python files and 850 Markdown files)). Both build the
full `DocumentIndex` (`features/documents/repositories/index.py`) on each call, reading and parsing the frontmatter
of every document (about 710 files) even to resolve one ID. Agents call these lookups many times per task.

Hypothesis: an on-disk index cache keyed by each document's identity (path, size and mtime, or a content hash)
lets a call re-read only changed documents and makes the common case a cache load.

## 2. Technical Spike Questions

- **Q1**: Which key is safe across checkouts, worktrees, branch switches and clock skew (mtime+size versus content
  hash), and where does the cache live (an ignored path inside the workspace, per worktree)?
- **Q2**: What happens on a corrupt, stale or concurrently written cache, and how does the index guarantee results
  identical to a fresh build?

## 3. Proposed Design & Impact

- The index loads a cache, revalidates entries against the keys, re-parses only changed or new documents, drops
  removed ones and writes the cache atomically. A corrupt cache is rebuilt silently (a diagnostic under `-v`).
- Results of `list`, `search`, `resolve` and `refs` stay identical to a fresh build; tests cover edits, renames,
  deletions, alias changes and branch switches. Timings are measured again.
- Rules that build the same catalog (`WorkspaceCache.get_catalog`) may reuse it if the Planning finds that safe.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr document-index-cache "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept document-index-cache --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff document-index-cache.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
