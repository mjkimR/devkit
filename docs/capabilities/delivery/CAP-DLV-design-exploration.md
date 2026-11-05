---
id: CAP-DLV-design-exploration
title: General solution exploration
summary: "An opt-in user-invoked skill explores general design mechanisms and tradeoffs through optional local roles, returning conversation-first directions without implementation authority."
area: delivery
status: active
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/SKILL.md
created_at: 2026-11-05
usecases:
  - UC-explore-a-design-problem
---

# [CAP-DLV-design-exploration] General solution exploration

## 1. Summary

The design-explore catalog bundle helps choose useful mechanisms for architecture, data models, module boundaries
and processing or development workflows. `ADR-explicit-solution-exploration` records its independent entry,
skill-local roles and output authority.

## 2. Scope and Boundary

- **In-Scope**: bounded problem framing, distinct mechanisms, optional premise exploration, relevant references,
  consequential criticism and synthesis of useful directions with tradeoffs.
- **Out-of-Scope**: runtime projection (`CAP-DIST-agent-projections`), implementation and delivery authority
  (the consumer's workflow), sourced research investigations (`CAP-DLV-deep-research`) and interface improvement
  (`CAP-DLV-uiux-improvement`).
- **Scope Excluded**: mandatory documents, business brainstorming, global specialists, persistent memory,
  automatic companion invocation, fixed casts or counts, scoring, consensus and comparative-benefit experiments.

## 3. Business Rules and Policies

1. **Opt-in entry**: WHERE design-explore:core is selected, sync MUST deploy one user-only skill, three local roles
   and two references without global specialist registration or ambient design guidance.
   Test: `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py`.
2. **Explicit invocation**: The skill MUST run only on explicit user invocation.
   Review: the entry guard and user-only projection integration test.
3. **Local assignments**: WHEN delegating, the coordinator MUST pass a selected role's absolute path resolved from
   the invoked skill, with goal, premise, relevant facts, constraints, permitted actions, read/write boundaries,
   stop condition and expected return. Review: `test_optional_local_assignments_and_evidence_boundaries`.
4. **Independent first passes**: WHERE fresh children without parent inheritance are supported, the coordinator
   SHOULD withhold peer conclusions from their first-pass assignments.
   Review: `test_optional_local_assignments_and_evidence_boundaries`.
5. **Honest fallback**: IF fresh children or role returns are unavailable, THEN the coordinator MUST disclose
   shared-context passes or missing coverage without inventing independence or agreement.
   Review: `test_optional_local_assignments_and_evidence_boundaries`.
6. **Output authority**: WHEN exploration finishes, the coordinator MUST return in conversation unless a destination
   is explicitly requested. Review: `test_general_design_and_output_authority_contracts`.
7. **Retention owner**: WHERE a destination is explicitly requested, only the coordinator MUST write it under the
   consumer's existing format, permissions and project rules. Review: entry procedure and local role boundaries.
8. **Role authority**: WHEN a role runs, it MUST leave product source, retained files, settings, index and HEAD
   unchanged. Review: `test_optional_local_assignments_and_evidence_boundaries`.
9. **Exploration boundary**: The invocation MUST confer no automatic implementation, settings change, commit,
   delivery approval or publication authority. Review: `test_general_design_and_output_authority_contracts`.
10. **Preserved goal**: WHEN exploring mechanisms, the coordinator SHOULD preserve the actual goal and hard
    constraints while questioning proposed means and open preferences.
    Review only: entry procedure, exploration examples and semantic review.
11. **Useful distinction**: WHEN presenting directions, the coordinator SHOULD explain mechanisms, benefits,
    tradeoffs and decision-changing assumptions rather than count brands, names or role labels as design diversity.
    Review: `test_general_design_and_output_authority_contracts`.
12. **Optional support**: WHEN selecting useful work, the coordinator MAY keep it inline or use local explorers,
    researcher and critic without a cast, count, score, survey, prototype, consensus or benefit-proof prerequisite.
    Review: entry, researcher and critic instructions.
13. **Preserved differences**: WHEN synthesizing, the coordinator SHOULD retain plausible unconventional mechanisms
    and their benefits instead of averaging candidates into a generic feature list.
    Review: `test_general_design_and_output_authority_contracts`.
14. **Bounded uncertainty**: WHEN reporting evidence or critique, the coordinator SHOULD separate inspected support,
    inference and unknowns, permit zero criticism findings and normally use one useful refinement pass.
    Review: local researcher/critic instructions and semantic review.
15. **Refused operation**: IF access or a requested destination is refused, THEN the coordinator MUST stop that
    operation without bypassing the refusal and name the blocked work alongside the useful result.
    Review: entry procedure and local role boundaries.
16. **Independent lifecycle**: WHEN the bundle is removed or reselected, sync MUST preserve user artifacts and other
    selected bundles. Test: integration removal check and
    `packages/devkit-catalog/tests/e2e/bundles/design_explore/test_installed_consumer.py`.

Checks establish instruction and packaging consistency. They do not measure model obedience, creativity or team
superiority. Fresh context and Markdown role boundaries provide no native filesystem or permission isolation.

## 4. Interfaces and Data Contracts

Select `uv run devkit add design-explore` or design-explore:core, then explicitly invoke `/design-explore <problem>`.
Registration is `design-explore = "devkit_catalog.design_explore"`. Dist and catalog suffice without agt, docs or
spec packages. Selection starts no work and changes no development approach.

The skill routes conditional reads to `references/exploration-methods.md` and `references/orchestration.md`.
Local role files are solution-explorer, reference-researcher and design-critic; only selected bodies are loaded.
Explorers return a premise, concrete mechanism/example, benefit, tradeoff, evidence/inference and unknowns.
Researchers return supported findings with sources, transfer limits and gaps. Critics return supported findings
with evidence, failure conditions and the smallest useful refinement; zero findings is valid.
Only actual returns inform synthesis. No result schema, fixed option count or retained document kind is required.
