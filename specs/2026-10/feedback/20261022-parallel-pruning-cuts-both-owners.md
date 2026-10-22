---
id: FB-parallel-pruning-cuts-both-owners
title: Parallel pruning deletes a rule from both files that point to each other
scope: repo
kind: suggestion
category: instruction-conflict
target: packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md
skill: none
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-parallel-pruning-cuts-both-owners] Parallel pruning deletes a rule from both files that point to each other

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `agent-asset-writing` says to link background instead of retelling it and, in the
  overall-refactor pruning pass, to leave out what another asset owns. Each rewriter decides ownership from its own
  batch only.
- **Proposed Procedure**: before deleting a restatement because another asset owns it, the rewriter confirms the
  owner still states it after its own edits (`rg` the bundle for the rule's key term); in a parallel run the Host
  runs one cross-batch check of removed rules before review.
- **Expected Benefit**: no rule disappears from the bundle because two owners each assumed the other kept it.
- **Cost & Risk**: one search per deleted restatement; the Host check is a single diff pass.
- **Attempted**: observed in this session; a `code-reviewer` pass caught the cases and the Host restored them.

## Diagnostic Details

- **Reproduction**: seven parallel rewriters pruned bundle assets by ownership; batches cut the same rule from
  both the constitution and the classification reference, and from the delegate worker reference and the worker
  records reference.
- **Expected / Actual**: each rule kept by exactly one owner / the rule existed in neither file.
- **Versions**: devkit main at 45f6f810.
- **Conditions**: overall-refactor, direct mode, general subagents with disjoint write boundaries.
- **Workarounds Attempted**: an independent review of the whole diff for circular deletions; fixes restored the rules.
- **Related Assets**: `AGENTS.md.jinja`, `skills/spec/references/classification.md`,
  `skills/spec-delegate/references/worker.md`, `skills/spec/references/worker-records.md`.

## Evidence

```text
classification.md: "The axes and workflows are in the spec constitution"
AGENTS.md.jinja (pruned): "Classify work ... with the spec skill's references/classification.md"
worker-records.md (pruned): permission rules "owned by the worker contracts and spec-delegate worker.md"
worker.md (pruned): "Removed everything worker-records.md owns: ... permission failures"
```
