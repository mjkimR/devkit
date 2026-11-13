---
id: CAP-DLV-idea-discovery
title: Idea discovery
summary: "An explicitly invoked discovery skill refines half-formed ideas with a minimum useful interview, bounded independent exploration, concrete proposals and uncertainty-driven routing without delivery authority."
area: delivery
status: active
created_at: 2026-11-13
usecases:
  - UC-discover-and-refine-an-idea
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/discovery/SKILL.md
---

# [CAP-DLV-idea-discovery] Idea discovery

## 1. Summary

The opt-in deep-research core preset supplies `/discovery` beside the separately invoked research entry.
The coordinator turns a half-formed idea into concrete proposals and a useful next decision. External research
supports the choice when needed. The result stays in conversation unless retention is requested.

## 2. Scope and Boundary

- **In-Scope**: minimum useful interviewing, distinct candidate premises, optional local exploration/research/critique,
  proposal synthesis, uncertainty-driven routing and explicitly requested result retention.
- **Out-of-Scope**: mandatory sourced investigations and their existing retention contract (`CAP-DLV-deep-research`),
  design mechanisms for an already supplied problem (`CAP-DLV-design-exploration`), delivery intake
  (`CAP-HARN-agent-guidance`) and generic projection (`CAP-DIST-agent-projections`).
- **Scope Excluded**: automatic implementation, a runtime or CLI, approach changes, delivery records, mandatory
  reports, fixed role/option counts, external-service execution and persistent decision tracking.

## 3. Business Rules and Policies

1. **Explicit entry**: WHERE deep-research:core is selected, sync MUST deploy discovery and research with user-only
   invocation policy and no registered discovery subagents. Test:
   `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`.
2. **Context before questions**: WHEN framing discovery, the coordinator SHOULD recover the desired change,
   audience/use scene, consequential constraints and session outcome from supplied context before asking.
3. **Minimum interview**: WHEN an unanswered user-only choice changes the first proposals or avoids substantial
   wasted exploration, the coordinator SHOULD ask it with the consequence; deferrable choices stay assumptions or
   alternative premises rather than delaying the first proposals until every branch is settled.
4. **Facts versus decisions**: WHEN missing information is inspectable, the coordinator SHOULD find it itself;
   user decisions MUST remain distinct from assumptions, recommendations and team agreement.
5. **Bounded first wave**: BEFORE autonomous work, the coordinator SHOULD state its question, observable effort
   bound and stop condition; a small inquiry MAY stay inline without roles or external research.
6. **Local delegation**: WHEN assigning a role, the coordinator MUST pass its verified absolute installed role path
   to a role-worker with goal, exact sources, absolute boundaries, permitted actions, expected return and stop
   condition. Roles MUST leave product files, retained results, settings, index and HEAD unchanged.
7. **Independence**: WHERE fresh contexts are supported, explorers SHOULD receive common facts and constraints
   without peer conclusions or a preferred winner until their independent first returns.
8. **Honest fallback**: IF delegation or evidence is unavailable, THEN the coordinator MUST report missing coverage;
   useful inline work MUST NOT be claimed as independent role execution.
9. **Concrete proposals**: WHEN presenting a direction, the coordinator SHOULD supply a usage example, benefit,
   adoption/operating cost, support, unresolved assumptions and a condition that rules it out without an option quota.
10. **Critique timing**: AFTER developing candidates, the coordinator MAY assign a challenger to consequential
    premises, evidence and output usefulness; zero supported findings is valid and consensus is not required.
11. **Uncertainty routing**: WHEN selecting a next step, the coordinator SHOULD route user-only choices to focused
    questions, factual gaps to bounded research, experiential gaps to examples or proposed experiments, failed
    premises to reframing/hold/rejection, and sufficient clarity to a concise brief.
12. **Further work**: BEFORE another autonomous round, the coordinator SHOULD name the question and what result
    changes the recommendation; it MUST stop at the agreed bound and preserve surviving uncertainty.
13. **Execution authority**: WHEN proposing an experiment or delivery handoff, the coordinator MUST obtain separate
    write/execution authority before acting; discovery alone creates no implementation, Unit, approval, envelope,
    settings change, staging, commit or publication.
14. **Conversation default**: WHEN no destination is requested, the coordinator MUST return in conversation without
    requiring a retained material; only the coordinator writes an explicitly requested result.
15. **Scratch boundary**: WHEN scratch is needed, the coordinator MUST allocate collision-free run/task directories
    under `.devkit/transient/deep-research/` and verify ignored/untracked paths before Git-backed scratch writes.
    Unproven ignore state stops allocation; absent Git is disclosed.
16. **Refused access**: IF access or authorization is refused or ambiguous, THEN the coordinator and roles MUST stop
    that resource without bypass and report its missing coverage while continuing unrelated permitted work.
17. **Discovery outcome**: WHEN discovery ends, the coordinator MUST report clarified, validation-needed, held or
    rejected with reasons, actual evidence limits and the next decision; a rejected idea is a valid result.
18. **Requested retention**: WHERE a material is requested, the coordinator MUST follow the material identity,
    collision, partial-resume, complete-material immutability and citation conventions in `CAP-DLV-deep-research`,
    leaving it uncommitted and reporting its coverage status separately from the discovery outcome.
19. **Upgrade compatibility**: WHEN the core preset is upgraded, removed or reselected, sync MUST preserve existing
    research overrides and retained materials. Tests: the integration upgrade case and
    `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`.

Distribution checks enforce deployment and upgrade boundaries. Interview quality, proposal usefulness, role
independence and routing are semantic agent contracts verified through behavioral exercise and review.

## 4. Interfaces and Data Contracts

Select with `uv run devkit add deep-research`, then explicitly invoke `/discovery <idea, request or decision>`.
No bundle rename, dependency or change to the existing research skill paths is required. Both entries declare
user-only invocation; Codex and Claude Code use native settings, while Antigravity follows the explicit skill-body
guard. An invocation starts no SDD intake; subsequent implementation uses ordinary intake.

Local roles: idea-explorer develops one premise, evidence-researcher answers one factual question, idea-challenger
checks developed proposals. Returns carry completed/needs_input/failed status, exact source/artifact identity,
findings/support and failure conditions, assumptions, missing coverage and actual scratch paths. Only the
coordinator writes a requested retained result. No role document supplies native sandbox or tool enforcement.

The conversational result contains the problem/use scene, concrete proposals, justified recommendation, actual
user decisions, assumptions, inspected support/limits, discovery outcome and next route proportionately.
A requested material keeps its complete/partial investigation status separate from that outcome.
