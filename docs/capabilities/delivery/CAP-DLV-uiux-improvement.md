---
id: CAP-DLV-uiux-improvement
title: UI/UX improvement
summary: "An opt-in user-invoked skill improves interfaces and user flows through optional local design perspectives, requested implementation under the consumer workflow and qualified usage verification."
area: delivery
status: active
created_at: 2026-11-05
usecases:
  - UC-improve-an-interface-and-user-flow
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md
---

# [CAP-DLV-uiux-improvement] UI/UX improvement

## 1. Summary

The `uiux-improve` catalog bundle supplies an explicitly invoked entry for overall interface and experience
improvement. The coordinator selects useful design perspectives and carries requested changes through the
consumer's existing workflow. Alternatives, research and criticism are optional means, not a required final report.
`ADR-uiux-improvement-workflow-boundary` records the local-role and delivery-authority decision.

## 2. Scope and Boundary

- **In-Scope**: focused task/interface inspection, coherent flow and visual design, optional independent perspectives,
  requested implementation, representative usage checks and qualified reporting.
- **Out-of-Scope**: runtime tools and native projections (`CAP-DIST-agent-projections`), consumer workflow/policy
  authority (the consuming project), general solution ideation and sourced research entry behavior (other skills).
- **Scope Excluded**: global specialists, always-loaded design instruction, persistent role memory, automatic
  companion skill invocation, new delivery records or mandatory research, scores, comparisons and debate rounds.

## 3. Business Rules and Policies

1. **Opt-in distribution**: WHERE uiux-improve:core is selected, sync MUST deploy one skill and four local role files
   without registered specialist subagents. Test: `packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py`.
2. **Explicit invocation**: The bundle MUST declare `invocation = "user"` and an explicit-only entry guard.
   Tests: `test_explicit_selection_projects_local_roles_and_user_only_entry` and `CAP-DIST-agent-projections`.
3. **Consumer authority**: WHEN requested changes are implemented, the coordinator MUST follow the consumer's
   existing workflow, permissions and approvals. Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
4. **Goal-driven improvement**: WHEN the entry runs, the coordinator SHOULD select flow, interaction and visual work
   serving the supplied goal, constraints and inspected artifacts rather than require an exhaustive audit.
   Review only: representative instruction scenarios.
5. **Narrower request**: WHERE the request is review-only, the coordinator MUST finish with findings and no product edits.
   Test: `test_entry_preserves_improvement_scope_and_consumer_authority`.
6. **Optional perspectives**: WHEN selecting work, the coordinator MAY keep a small request inline or select useful
   local roles without a fixed cast, alternative count, numeric score or proof-of-benefit experiment.
   Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
7. **Role packet**: WHEN delegating, the coordinator MUST pass the resolved absolute local role path, goal, relevant
   facts/artifacts, hard constraints, permitted actions, stop condition and expected return to a general child.
   Review only: orchestration instruction and representative payload.
8. **Independent context**: WHERE the host supports fresh children, the coordinator SHOULD use fresh context without
   parent conversation inheritance and withhold peer conclusions from independent first passes.
   Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
9. **Role authority**: WHEN a role runs, it MUST return suggestions or evidence while leaving product source,
   retained files, index and HEAD unchanged. Review: local role text and `test_entry_preserves_improvement_scope_and_consumer_authority`.
10. **Host limits**: IF an interaction tool, fresh child or authorized operation is unavailable, THEN the coordinator
    MUST disclose actual coverage and the concrete blocker without claiming independent execution or native isolation.
    Review: orchestration fallback and role return instructions.
11. **Verification**: WHEN reporting an improvement, the coordinator MUST distinguish actual changed states and checks
    from design inference and unavailable coverage. Review only: completion and representative instruction scenarios.
12. **Qualified completion**: WHEN a normal improvement request finishes, the coordinator SHOULD return the changed
    interface or flow and verification status, or preserve useful partial work with a concrete blocker.
    Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
13. **Independent installation**: The bundle MUST install through dist/catalog without agt, docs or spec packages.
    Test: `packages/devkit-catalog/tests/e2e/bundles/uiux_improve/test_installed_consumer.py`.
14. **Artifact preservation**: WHEN the bundle is removed or reselected, sync MUST preserve user-owned design artifacts.
    Tests: `test_removal_preserves_user_artifacts_and_other_selected_assets` and the installed-consumer test.

Instruction review verifies stated behavior, not model obedience, aesthetic quality or superiority over one agent.
Selection changes neither the development approach nor the consumer's execution authority. The distribution-owned
root bundle inventory can name the selection; the bundle supplies no design guidance fragment or constitution.

## 4. Interfaces and Data Contracts

Select `uv run devkit add uiux-improve` or uiux-improve:core, then explicitly invoke `/uiux-improve <goal>`.
Registration is `uiux-improve = "devkit_catalog.uiux_improve"`. No new command, code or runtime is added.
The bundle needs no devkit-spec or devkit-docs installation; consuming projects retain their own workflow requirements.

The entry routes optional reads to `references/design-guidance.md` and `references/orchestration.md`. Local roles
are designer, unconventional-designer, reference-researcher and critic. Only selected bodies are loaded. Each return
contains status (completed, partial or failed), inspected identities, concrete work, assumptions and unverified
areas; research includes source provenance, and critique includes evidence, failure conditions and repairs.
A failed or absent role supplies no findings. The coordinator owns synthesis, retained output and product changes.

Without a requested destination, the result stays in conversation. Product artifacts follow consumer ownership;
no retained document kind, mandatory design brief or persistent memory is introduced.
