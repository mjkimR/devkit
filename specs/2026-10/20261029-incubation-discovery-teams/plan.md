---
id: PLAN-incubation-discovery-teams
spec: SPEC-incubation-discovery-teams
---

# Technical Plan for SPEC-incubation-discovery-teams

## 1. Constitution and Invariants

The two accepted discovery ADRs extend incubation while retaining content-only catalog ownership, shared approach
inspection, optional roles and mutable Host-owned context. No dependency, runtime or component-layer change.
Preserve `CAP-DLV-idea-incubation` and `ARCH-05-2-components` boundaries. No new invariant conflict.

## 2. Architecture Overview and Impact

Add one user-invoked skill and three read-only role contracts to the existing incubation core preset.
Use existing manifest `invocation = "user"` to project native settings; sources contain no native policy fields.
The invoking Host coordinates optional assignments and saves retained synthesis. Existing researcher experiment
writes stay limited to explicit payload authority. Retain all existing role IDs and default inheritance.

## 3. Components and Interfaces

- `skills/incubate-research/SKILL.md`: explicit trigger, approach/context checks, conditional orchestration and
  synthesis references, return criteria; research completion does not start implementation.
- `references/orchestration.md`: adaptive assignments, independent premises, evidence comparison, optional
  critic/direct communication, unavailable-role handling and bounded partial results.
- `references/synthesis.md`: proportionate notes, claim/source support, provisional versus user decisions,
  conditional roadmap, useful alternatives and resume facts.
- `subagents/direction-explorer.md`, `discovery-critic.md`, `discovery-planner.md`: one bounded goal and structured
  evidence/draft returns; no source/context/index/HEAD writes.
- Existing entry/discovery/delegation/context guidance: research is suggested only, invoked by the user; add
  research role routing and retained alternatives without forcing broad work for small tasks.
- Existing researcher: permit native web tools where supported and record current source claims with limits.
- `bundle.toml`, catalog README and Living Spec: expose the entry/roles and honest consumer behavior.

Return convention remains status, summary, source/artifact identity, evidence and failure conditions,
recommendation/draft, assumptions and unverified areas. Actual context writes stay with the Host.

## 4. State and Edges

Selection seeds neither context nor discovery documents. Reuse existing document locations; default new research
notes to project-owned `docs/materials/`. Notes label proposed scope and conditional roadmap, with links from
`.devkit/incubation.md`. No parser or new lifecycle is added. Role absence, policy errors, unsupported sources and
budget exhaustion yield bounded reports with explicit gaps. No network/permissions or publication fallback.

## 5. Verification Plan

- Extend catalog integration tests to load the actual manifest and synchronize all hosts, checking native
  explicit-invocation projection, six role contracts and removal/reselection preservation.
- Extend installed-consumer e2e to build wheels and verify research assets without devkit-spec.
- Use skill-creator validation for frontmatter/reference readiness, repository wording/rules and self-containment.
- Run matched isolated baseline/candidate exercises on fixed raw sources; inspect real artifacts and delegation.
  Add an independent fresh-context resume and source-backed research assignment. Retain concise evidence under
  this spec; keep throwaway consumer workspaces outside tracked content.
- Run `just lint-check devkit-catalog`, `just check devkit-catalog`, `just test-affected`, the changed installed
  consumer e2e, `devkit sync` and cumulative rules. Reuse checks for unchanged content.
- Independent code review covers the cumulative change; reconcile review verifies retained contracts and evidence.
