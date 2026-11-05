---
id: PROP-cloud-research-handoff
title: Cloud research request and result handoff
summary: "Extend deep research with user-mediated cloud research requests, resumable result intake and evidence-aware synthesis without adding a research runtime."
status: draft
created_at: 2026-11-05
target_area: docs/capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/deep_research/
    - packages/devkit-catalog/tests/integration/bundles/test_deep_research.py
    - packages/devkit-catalog/tests/e2e/bundles/deep_research/
    - docs/capabilities/delivery/
    - docs/usecases/delivery/
    - docs/decisions/
    - guides/install/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-cloud-research-handoff] Cloud research request and result handoff

## 1. Background & Hypothesis

`CAP-DLV-deep-research` supports optional local research roles, evidence-aware synthesis and resumable partial
materials. It does not define a request-and-return procedure for research performed by a user in ChatGPT or Gemini.

A copyable research brief and explicit result intake could let a user employ cloud research alongside local work
without introducing a provider runtime. The useful outcome is the incorporated evidence, not merely a prompt.

## 2. Technical Spike Questions

- **Q1 — Request quality:** What minimum brief captures the decision, research questions, constraints, useful
  sources, expected evidence and desired output without demanding repository-specific knowledge from the provider?
- **Q2 — Resume:** How are pending requests and returned reports identified across sessions using the existing
  transient workspace and partial material conventions, including loss of transient files?
- **Q3 — Evidence:** Which consequential claims require source inspection, and how are inaccessible citations,
  contradictory reports and unverified provider conclusions represented?
- **Q4 — Handoff convenience:** Is copying a brief and returning an exported report sufficient, or is an optional
  handoff artifact useful? Compare available host capabilities without making browser automation mandatory.
- **Q5 — Later automation:** Under what demonstrated need would API execution justify credentials, cost controls,
  background task management and a revision of the no-runtime boundary?

## 3. Proposed Design & Impact

Recommended starting direction, subject to Planning:

1. During an explicitly invoked investigation, prepare a provider-neutral request containing the question,
   intended decision, known facts, constraints, source expectations and output format.
2. Separate information suitable for external disclosure from private repository context. Make the proposed
   outbound content inspectable; do not include secrets or upload repository contents implicitly.
3. Give the user a copyable prompt, any deliberately selected attachments and instructions for returning a report
   with citations. Track that the request is awaiting a user-provided result rather than claiming execution.
4. Continue independent local work when useful. If the investigation pauses, retain the minimum resumable context
   through the existing partial material convention; do not make a transient-only pointer the sole resume input.
5. On return, record provider/report identity, date, the actual supplied content and inspection limits. Check the
   consequential evidence and integrate it with local findings, preserving conflicts and missing coverage.
6. Preserve the existing explicit invocation, approach neutrality and coordinator-owned material boundary.

Relevant official documentation inspected on 2026-11-05 provides optional future execution paths:

- [Gemini Deep Research](https://aistudio.google.com/docs/deep-research) describes preview access through the
  Interactions API and asynchronous execution.
- [OpenAI longer web research](https://developers.openai.com/api/docs/guides/tools-web-search#run-longer-web-research)
  describes Responses API web research with background execution for long-running tasks.

These API paths are not evidence of parity with the consumer applications or of access through the user's current
subscription. Provider availability and execution costs must be rechecked if API work is proposed.

Expected changes belong to the deep-research skill and supporting references, its capability/use case and installed
consumer checks. No new feature dependency or shared subagent role is proposed.

**Scope excluded:** API clients, research schedulers, automatic browser submission, credential handling, automatic
uploads, and automatic acceptance of external reports as verified facts. Reconsider API integration only as a
separately authorized scope after the manual round trip demonstrates a concrete automation need.

## 4. Lifecycle & Retirement Criteria

This is a queued draft with `medium` Planning and Development effort and estimated size `M`. It has no prerequisite
proposal. Planning must settle request content, disclosure boundaries, return formats and durable resume behavior.

Candidate Development acceptance checks:

- **AC1:** Given a bounded investigation, the user receives a self-contained copyable request and knows what result
  to return; generating it is not reported as a completed cloud investigation.
- **AC2:** Given a pending request and a later session with its named partial material, the coordinator resumes the
  investigation without depending on vanished transient files or duplicating a request silently.
- **AC3:** Given an imported report with valid, missing and conflicting evidence, the synthesis distinguishes
  inspected support from external claims and retains the gaps that can change the decision.
- **AC4:** Given no returned report, local findings can remain useful and the retained result stays explicitly
  partial where external evidence is necessary.

Acceptance and handoff follow the existing proposal lifecycle. Reject or narrow the draft if a reusable request
and intake procedure adds no meaningful convenience over the existing investigation brief.
