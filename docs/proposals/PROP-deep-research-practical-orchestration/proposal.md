---
id: PROP-deep-research-practical-orchestration
title: Make deep-research deliverable-driven and proportionate
summary: "Align deep-research assignments and criticism with the requested deliverable, reduce duplicate verification and distinguish recoverable retrieval failures from permission refusals."
status: accepted
created_at: 2026-11-05
target_area: capabilities/delivery/
priority: medium
size: M
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/
    - packages/devkit-catalog/tests/integration/bundles/test_deep_research.py
    - packages/devkit-catalog/tests/e2e/bundles/deep_research/
    - docs/capabilities/delivery/CAP-DLV-deep-research.md
    - docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
    - docs/decisions/
  excludes:
    - packages/devkit/src/
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
    - .devkit/managed/
    - .agents/skills/
task_kind: feature
planning_effort: low
dev_effort: medium
workflow: sdd-proposal
---

# [PROP-deep-research-practical-orchestration] Make deep-research deliverable-driven and proportionate

## 1. Background & Hypothesis

A user invoked deep-research both to pilot its operation and to find reusable agent-team configurations for
UI/UX improvement and unconventional ideation. The first response emphasized empirical team-performance
literature and recommended a same-task comparison before adopting a configuration. Concrete repository and
file references arrived only after the user asked again. The user explicitly rejected the cost of comparative
validation and preferred adapting existing role instructions, then refining them during ordinary use.

The pilot successfully dispatched three fresh-context investigators, collected their actual returns, used a
subsequent critic and retained a material. The following observations identify improvements to that operation:

- The requested practical output was not sufficiently represented in the first assignments and final answer.
- The critic found no consequential evidence problems in the supplied qualified proposal, but did not catch
  that the proposed next step imposed unwanted work. It reviewed the supplied proposal, not the final material.
- The coordinator reopened several sources already inspected by investigators. Some verification was useful;
  repeated broad coverage also duplicated investigation effort. No token or latency saving was measured.
- One role stopped fulltext verification after timeout, 404 and unreadable-page results. Its partial return was
  truthful, but the role boundary used the same stop-and-no-reroute wording for refused and unavailable operations.
  That wording can cause ordinary retrieval failures to be treated as authorization refusals.

Hypothesis: small changes to intake framing, delegation, criticism and retrieval recovery can make the existing
research team produce more directly useful results at proportionate effort. No new runtime or role is needed.
The current contracts in `CAP-DLV-deep-research` and `UC-research-an-idea-and-shape-a-roadmap` remain the foundation.

### User constraints and evidence status

The requested work proceeds through Planning of this bounded improvement. Plan acceptance and Development
handoff remain separate Host decisions. Keep the explicitly invoked skill with skill-local Markdown roles and optional delegation.
Do not require same-task comparisons, blind scoring or proof of team benefit before adopting a useful pattern.

The observations above come from the pilot conversation and returned assignments retained in
`MAT-agent-team-design-pilot`. This proposal needs no access to the transient run directory.

## 2. Planning Decisions

Planning used `low` activity-effort: the direction is already concrete and needs no additional research or critic
pass. No essential user question remains. Development remains `medium` because agent-facing instructions and
retained behavior contracts need independent review.

| Question | Settled direction | Consequence |
| --- | --- | --- |
| Brief and assignment | Put requested deliverable, intended use, known constraints and an observable stop condition in the existing brief; each assignment names its contribution and expected return. | Infer the fields from supplied context; add no mandatory intake form or universal output template. |
| Usefulness check | Keep a coordinator-owned final check before retention; give the same criteria to discovery-critic only when it is invoked. | Check the requested artifact, next action and unwanted prerequisites without a compulsory reviewer call. |
| Retrieval classification | A definite refusal stops access to that resource. An ordinary technical retrieval failure permits bounded authorized recovery. Ambiguous authorization stops that resource while unrelated permitted work can continue. | Failed retrieval and actual replacement evidence remain visible; recovery consumes the original assignment bound. |
| Verification | Retain installation and authority checks; use concrete semantic review examples for instruction behavior. | No test claims to measure creativity, usefulness or cost superiority, and no comparison experiment is required. |

`PADR-deliverable-driven-research` records the lasting instruction choice and tradeoffs. `target-docs.md` identifies
the exact expected source and Living Spec reflection. No new package, runtime behavior or feature edge is needed.

## 3. Proposed Design & Impact

### 3.1 Frame the requested output before allocating research

Record the requested deliverable, intended use, known constraints and research stopping point in the run brief.
Infer these from the request where possible; ask only when a missing choice changes the research target.
Each delegated question should explain which part of that output it supplies.

For a request for reusable configurations, the output should include repository/file references, what to borrow,
what to omit and a recommended starting composition. Empirical evidence can qualify that recommendation without
becoming a separate effectiveness study. For a factual research question, use the appropriate factual output;
repository discovery is not a universal requirement.

### 3.2 Review usefulness as well as factual support

Before retaining the result, the coordinator should check whether the requested artifact is present, whether the
recommendation supports the user's intended next action and whether it introduces unnecessary prerequisites.
When discovery-critic is useful, its payload should include those criteria and the user's cost constraints.

A finding should name the missing or burdensome output, the relevant user constraint and a concrete repair.
Zero supported findings remains valid. Do not mandate criticism, consensus, a fixed issue count or extra rounds.
Do not add an independent reviewer to every research run.

### 3.3 Verify consequential claims selectively

Investigators should return the inspected source identity, the relevant location or finding and its limitations.
The coordinator should inspect those returns and selectively reopen sources where a claim changes the
recommendation, provenance is missing, sources conflict or the returned evidence is otherwise suspect.

A clear, adequately sourced return should not trigger a complete repeat of its investigation by default.
Selective verification does not mean accepting every role claim without review. Keep observation, vendor claim,
inference and unavailable evidence distinct in the retained result.

### 3.4 Separate retrieval recovery from authorization refusal

Preserve the prohibition on bypassing an actual permission or sandbox refusal. Do not use another tool, path,
process, identity or setting to obtain access to the same denied resource.

For an ordinary timeout, broken public link or unreadable result without an authorization refusal, allow a
bounded retry or another legitimately accessible primary source within the existing research assignment.
An author-hosted manuscript or another relevant public source can be a valid alternative. Do not route around
an access control or paywall. If another source does not support the same claim, retain that claim as unverified.
If classification is ambiguous, report the uncertainty and stop access to that resource; unrelated permitted
research may continue. The return should identify the failed retrieval and what was actually inspected instead.

Use the role's existing observable research bound; no new automatic retry engine or expanding budget is proposed.

### 3.5 Keep follow-up work proportional

Separate optional investigations from prerequisites. A roadmap should connect directly to the user's intended
use and avoid turning every unknown into more research. When the user declines comparative validation, keep
uncertain benefits explicit while recommending a usable starting point without a comparison gate.

Retain the existing fresh-context dispatch, one-question assignments, source qualification, coordinator-owned
material and explicit separation between behavioral instructions and host enforcement. Adjust the existing
skill and references rather than adding personas, a framework or a fixed team size.

### Expected scope

Edit the source bundle's entry, orchestration/synthesis references and affected role wording. Reconcile the
changed behavior into the capability and use case. Update existing bundle checks only where the instruction
contract changes. Managed and projected copies remain generated through normal synchronization.
No new cross-feature dependency or package edge is in scope.

### Acceptance examples for Development

- A practical-reference request produces concrete repositories/files and reuse guidance in its first retained
  answer, rather than only research about whether the approach works.
- A proposed next step that conflicts with a supplied cost constraint is revised or identified as optional
  before retention; it is not silently made an adoption prerequisite.
- A source-supported return is reviewed without automatically repeating its whole investigation; a decisive
  unsupported claim still receives targeted verification or remains unverified.
- An ordinary public-source timeout or 404 can lead to a bounded authorized recovery. A permission refusal
  never authorizes alternate access to the denied resource. Missing coverage remains visible.
- A simple request can complete without discovery-critic or additional roles. Criticism can return zero findings.

### Scope excluded

- A new UI/UX or ideation-team skill, installation of referenced repositories or copying their entire workflows.
- Benchmarks, same-task A/B/C comparisons, blind human scoring or validation until team superiority is proved.
- A research runtime, new tool permissions, automated retry service, scheduler or persistent role memory.
- Changes to Git/worktree lifecycle, research material immutability, citation policy or publication authority.
- Implementation during Planning, or mandatory additional research/review rounds.

## 4. Lifecycle & Retirement Criteria

This proposal remains `reviewing` for the Host's committed-source review and `plan-accept` decision. Planning
has settled the direction; it claims neither acceptance nor a Development handoff.

On acceptance, hand off one bounded source-bundle/documentation change at `medium` Development effort. Include the
promoted decision in the declared Development scope. Retirement follows the normal handoff lifecycle. On rejection,
record the decision and follow the normal rejection lifecycle. No comparative-benefit study gates either adoption
or completion of the implementation checks.
