---
id: PROP-response-style-survey
title: Survey reply-style practice to refine response-style
summary: Surveys reply-style guidance across agent tooling repositories and writing guides, measures candidate rules with a small benchmark, and folds the results into the response-style bundle, including whether its always-on guidance needs more than the 300-byte fragment.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: distribution/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - distribution/
    - packages/devkit-catalog/src/devkit_catalog/response_style/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-response-style-survey] Survey reply-style practice to refine response-style

## 1. Background & Hypothesis

- **Problem**: The `response-style` bundle was rewritten once from one external project's ideas (an AGPL output-style
  plugin, used for principles only). A single source gives one author's taste, not a tested practice, and nothing
  measures whether the rules change replies at all.
- **Constraint found in that rewrite**: a `guidance` fragment is limited to 300 UTF-8 bytes
  (`CAP-DIST-manifest-spec`), so only one core sentence is always loaded; the rest lives in the skill, which an agent
  reads once per context and which fades in long sessions. The user allows relaxing the limit if the evidence needs it.
- **Hypothesis**: Rules drawn from several independent sources and kept only when a small benchmark shows an effect
  give replies that are shorter, answer-first and loss-free on every host, without model-specific wording.

## 2. Technical Spike Questions

- **Q1 (Sources)**: Which repositories and guides to survey: agent output styles and system prompts published by tool
  vendors, open agent harnesses (Claude Code plugins, Codex `AGENTS.md` collections, Cursor and Windsurf rules),
  technical writing guides (English and Korean product writing guides), and what each claims with evidence.
- **Q2 (Licensing)**: How survey notes record each source's license, and the rule that only ideas, never wording,
  examples or structure, move into the bundle from copyleft sources.
- **Q3 (Measurement)**: A small benchmark (about ten to fifteen prompts: focused question, broad survey, depth
  request, acknowledgment, artifact request, blocking question, a Korean subset) run headless per host with no style,
  the current style and a candidate. Metrics: answer in the first sentence, length, wrapper-free artifacts, kept
  numbers and scope conditions. Where it lives (`materials/` scripts or a repository script) and how it stays cheap.
- **Q4 (Always-on budget)**: Whether the benchmark shows a gain from more always-loaded text than one 300-byte
  fragment, and if so: raise the limit for all bundles, allow a per-bundle exception, or allow several fragments.
  This is a `CAP-DIST-manifest-spec` contract change in `devkit-dist`.
- **Q5 (Variants)**: Whether the bundle should offer presets (for example a terse heads-down variant and a fuller
  status variant) or stay one style with variables.
- **Q6 (Precedence)**: How the "content versus form" rule interacts with the spec bundle's report formats, and whether
  those formats should shrink instead.

## 3. Proposed Design & Impact

- Planning: a survey note per source in `materials/` with its license, claims and evidence; a benchmark design; PADRs
  for the source policy, the measurement and the always-on budget.
- Development: the revised skill and guidance in `devkit-catalog`, the benchmark and its first results, and the
  manifest contract change only if Q4 decides one.
- Affected: the `response-style` bundle, its tests and smoke assertions, `CAP-DIST-content-packages`, and
  `CAP-DIST-manifest-spec` plus guidance validation in `devkit-dist` only under Q4.

## 4. Lifecycle & Retirement Criteria

- Preliminary decisions: `devkit spec proposal padr response-style-survey "<title>"`.
- On acceptance (`plan-accept`): hand off with `devkit spec proposal handoff response-style-survey`.
- On rejection: `status: rejected` with the user's reason in the commit message.
