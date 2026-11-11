---
id: PROP-compress-spec-main-loop-guidance
title: Compress the spec guidance of the main development loop
summary: Shortens the spec guidance every development run reads (constitution, spec skill, sdd-spec-feature, worker contract and core references) conservatively, keeping each rule at one owner, after the peripheral pass shows which compression patterns hold.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/delivery/
priority: medium                       # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/delivery/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-compress-spec-main-loop-guidance] Compress the spec guidance of the main development loop

## 1. Background & Hypothesis

A context-size check on 2026-11-11 measured the spec guidance an agent reads:
- Always loaded, about 3.4K tokens: root guide, skill and agent descriptions.
- `get-context` for every installed bundle, about 4K tokens.
- The documents of one development-worker pass, about 74KB (about 18K tokens).
- The Host orchestration set, about 68KB (about 17K tokens).

The main-loop set (about 105KB) is read on every development run and reread after compaction. Every file is within
the official Claude limits (`SKILL.md` under 500 lines; root guide under 200 lines). The risk is diluted attention
and the reread cost, not overflow. The guidance and CLI review-refactor run removed only duplicated and obsolete
text; it did not rewrite needed content shorter.

The peripheral pass of the same day measured what wording compression alone yields. Each group was rewritten for
density, with every rule kept:

| Group | Change |
| --- | --- |
| spec references | -3.6% |
| spec side skills | -1.1% |
| spec playbooks | -3.9% |
| catalog maintenance | -7.5% |
| other catalog bundles | -4% |
| adaptive bundle | -4% |

The documents were already one directive per line, and pinned guidance tests fix many phrases. Wording compression
of the main loop would likely yield a similar few percent.

Hypothesis: two policies reduce the main-loop load without removing a procedure:
1. Drop or shrink to a pointer the guidance that restates a check a devkit command or rule enforces
   deterministically, refusing before any effect with an actionable code and `[FIX]`.
2. Move rare-case branches (recovery, unusual errors, exception paths, seldom-used modes) out of the entry
   documents into on-demand references, linked one level deep.

Removing procedures or rules, or relaxing pinned tests, stays out of scope.

## 2. Technical Spike Questions

- **Q1**: What did the second peripheral pass (the two policies above, same date) yield per document? Which
  candidates did it reject, and why?
- **Q2**: For each main-loop rule, does a command or rule enforce it before effects, with a code and `[FIX]` that
  give the correct action? Authority, approval, irreversible or outward effects, judgment and post-effect
  detection always stay in the guidance.
- **Q3**: Which rare branches of the main-loop entry documents (constitution, `spec` skill, `sdd-spec-feature`,
  development-worker contract, integrate and orchestrate skills) can move to references without hiding a rule
  the common path needs?

## 3. Proposed Design & Impact

- Scope: the spec constitution, the `spec` skill, `sdd-spec-feature`, the development-worker contract,
  envelope/worker-records/completion references, specify/plan/tasks/review/sync, delegate/orchestrate/integrate,
  and isolated-execution.
- Apply Policy 1 and Policy 2 only. Wording compression is incidental.
- Conservative mode:
  - one document per commit, so each can be reverted alone;
  - a retained-constraint map for every removed or merged sentence;
  - no new or relaxed rules;
  - a pinned test changes only after its rule is confirmed kept.
- No pre-built behavior evaluation: problems surface as feedback and the affected commit is reverted or repaired.
  Package versions stay unchanged.
- Report sizes before and after for each document.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr compress-spec-main-loop-guidance "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept compress-spec-main-loop-guidance --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff compress-spec-main-loop-guidance.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
