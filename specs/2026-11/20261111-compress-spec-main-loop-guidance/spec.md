---
id: SPEC-compress-spec-main-loop-guidance
title: Compress the spec guidance of the main development loop
summary: Shortens the spec guidance every development run reads (constitution, spec skill, sdd-spec-feature, worker contract and core references) conservatively, keeping each rule at one owner, after the peripheral pass shows which compression patterns hold.
status: completed
created: 2026-11-11
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-compress-spec-main-loop-guidance] Compress the spec guidance of the main development loop

## 1. Problem Statement & Motivation

Handed off from proposal PROP-compress-spec-main-loop-guidance on 2026-11-11.

### 1. Background & Hypothesis

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
1. Shrink guidance that restates a check a devkit command or rule enforces deterministically, refusing before any
   effect with an actionable code and `[FIX]`. When knowing the rule before acting avoids rework (the refusal would
   come only after the work is done), keep a one-line essence and drop only the detail the refusal covers. Drop the
   rule completely only when the refusal comes early and cheap and its fix is obvious.
2. Move rare-case branches (recovery, unusual errors, exception paths, seldom-used modes) out of the entry
   documents into on-demand references, linked one level deep.

Removing procedures or rules, or relaxing pinned tests, stays out of scope.

A second peripheral pass tried both policies on the same groups:
- Policy 1 dropped or reduced 5 sentences in all.
- Policy 2 moved 5 rare branches, cutting entry documents by up to 558 bytes (spec-rule) and adding as much to
  references.
- Most candidates stayed. Many checks fire only after the work is done (linters, `assignment verify`, document
  rules, commit gates). Others were authority or judgment rules, or already one-line triggers.
- Expect the main loop to yield more only where its rules are refused early by the CLI. Measure that before committing
  to the proposal's size goal.

## 2. User Stories

- **US-1**: As an agent running the main development loop, I want the spec guidance I read on every run to carry
  only what I need on the common path, so that my attention stays on the rules that change my next step.

## 3. Non-Goals

1. **Procedures and rules stay**: no procedure, rule, authority or approval boundary is removed, relaxed or
   tightened; no new rule is added.
2. **Pinned tests stay as strong**: a pinned guidance test changes only to follow a kept rule's new location or
   wording.
3. **No code, CLI or version change**: devkit commands, codes, `[FIX]` text and package versions stay unchanged.
4. **No behavior evaluation**: regressions surface as feedback and the affected commit is reverted or repaired.
5. **Outside scope**: documents other than the 16 listed in AC-01, `docs/decisions/` and projections.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Only the two policies change the scoped documents
- **Given** the 16 scoped sources of the spec bundle: the constitution (`AGENTS.md.jinja`), the `spec` skill and its
  envelope, worker-records and completion references, `sdd-spec-feature`, the development-worker contract, the
  specify, plan, tasks, review, sync, delegate, orchestrate and integrate skills, and `isolated-execution`
- **When** the pass edits them
- **Then** each removed or reduced sentence either restates a check a devkit command or rule refuses before any
  effect, with a stable code and an actionable `[FIX]` (Policy 1), or is a rare branch moved to a reference of the
  same skill linked directly from its entry document (Policy 2); wording changes are incidental
- **And** authority, approval, irreversible or outward effects, judgment criteria and rules detected only after
  effects stay in the guidance; a late-refused rule keeps at least a one-line essence

### [AC-02] Every change is traceable and revertable alone
- **Given** an edited document
- **When** its change is committed
- **Then** it lands in its own commit (a moved branch together with the reference that receives it)
- **And** the change report lists bytes before and after per document and, per removed or reduced sentence, the
  enforcing code path and code (Policy 1) or the receiving reference and trigger line (Policy 2)
- **And** rejected candidates are listed with their reason

### [AC-03] Checks stay green
- **Given** the finished branch
- **When** `devkit rules check --ci --base <base>`, `just test-affected --base <base>` and `devkit sync --check`
  run
- **Then** they pass, with headings, anchors and section numbers other files cite still resolving, Jinja branches
  intact and explicit-only guards kept

## 5. Carried Proposal Notes

- Q1 (second peripheral pass yield) is answered in §1; Q2 and Q3 are answered per document by the change report
  (AC-02).
