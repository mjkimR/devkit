---
id: CAP-DLV-uiux-improvement
title: Software interface UI/UX improvement
summary: "An opt-in UI/UX skill improves software interfaces with object framing, optional local perspectives or user-selected Impeccable, and task-approved outside-workflow or consumer-workflow implementation with checks and qualified reporting."
area: delivery
status: active
created_at: 2026-11-05
usecases:
  - UC-improve-an-interface-and-user-flow
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md
---

# [CAP-DLV-uiux-improvement] Software interface UI/UX improvement

## 1. Summary

The `app-uiux-improve` catalog bundle supplies an explicitly invoked entry for improving software interfaces and their
user flows: web and desktop applications, dashboards, admin tools, settings and responsive views. Before a change
restructures views or flows, the coordinator frames the affected domain objects (OOUX: objects, relationships, CTAs,
attributes), from the consumer's glossary, object register and UX documents when they exist. It implements inline,
optionally with local design perspectives, and, when the user selects it, delegates craft work to one session of the
separately installed Impeccable skill, before or after its own changes. It announces an outside-workflow procedure
and obtains explicit task approval, or follows the consumer workflow the user chooses. Both retain product
constraints, host permissions and applicable checks.
Alternatives, research and criticism are optional means, not a required final report.
`ADR-uiux-improvement-workflow-boundary` records the local-role and delivery-authority decision, and
`ADR-impeccable-session-authority` the bounded Impeccable session and user-requested setup and cleanup.
`ADR-uiux-task-approved-run` records task route choice, verification and remaining authority.

## 2. Scope and Boundary

- **In-Scope**: focused task/interface inspection, proportionate object framing (from the consumer's OOUX documents
  when present), coherent flow and visual design, optional independent perspectives, user-selected Impeccable
  delegation with coordinator acceptance, user-requested Impeccable setup and cleanup, requested implementation,
  representative usage checks and qualified reporting.
- **Out-of-Scope**: runtime tools and native projections (`CAP-DIST-agent-projections`), consumer workflow/policy
  authority and the consumer's OOUX documents (the consuming project), Impeccable's installer, commands, hooks,
  detector and file conventions (the upstream Impeccable project), general solution ideation and sourced research
  entry behavior (other skills), and non-software design domains such as presentation decks, game graphics and video.
- **Scope Excluded**: global specialists, always-loaded design instruction, persistent role memory, automatic
  companion skill invocation, vendored external prompt text, new delivery records or mandatory research, scores,
  comparisons and debate rounds.

## 3. Business Rules and Policies

1. **Opt-in distribution**: WHERE app-uiux-improve:core is selected, sync MUST deploy one skill and four local role
   files without registered specialist subagents; the bundle's human usage guide (`bundle/README.md`) is not
   deployed. Test: `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`.
2. **Explicit invocation**: The bundle MUST declare `invocation = "user"` and an explicit-only entry guard.
   Tests: `test_explicit_selection_projects_local_roles_and_user_only_entry` and `CAP-DIST-agent-projections`.
3. **Consumer authority**: WHEN requested changes are implemented, including accepted delegated changes and
   requested setup/cleanup, the coordinator MUST follow the route the user approved for this task while preserving
   product constraints and host permissions (`ADR-uiux-task-approved-run`). The selected consumer workflow retains
   its required steps, reviews and approvals. Test: `test_task_route_approval_is_explicit_reused_and_bounded`.
4. **Goal-driven improvement**: WHEN the entry runs, the coordinator SHOULD select flow, interaction and visual work
   serving the supplied goal, constraints and inspected artifacts rather than require an exhaustive audit. WHEN a
   request adds, merges or reorders views or flows, the coordinator SHOULD name the affected objects, relationships,
   CTAs and attributes before layout or styling; a local change proceeds without that pass. WHERE the consumer keeps a
   glossary, object register or UX documents, the framing SHOULD read them, and otherwise it frames in conversation;
   the skill names these paths as an optional convention and depends on no `devkit-docs` concept (rule 13).
   Review: `test_framing_is_proportionate_and_reads_ooux_documents_only_where_present` and representative instruction
   scenarios.
5. **Narrower request**: WHERE the request is review-only, the coordinator MUST finish with findings and no product edits.
   Test: `test_entry_preserves_improvement_scope_and_consumer_authority`.
6. **Optional perspectives**: WHEN selecting work, the coordinator MAY keep a small request inline or select useful
   local roles without a fixed cast, alternative count, numeric score or proof-of-benefit experiment.
   Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
7. **Role packet**: WHEN delegating to a local role, the coordinator MUST pass the resolved absolute local role path,
   goal, relevant facts/artifacts, hard constraints, permitted actions, stop condition and expected return to a
   `role-worker` subagent, or to the host's general subagent (`general-purpose` on Claude Code) for an assignment
   that interacts with a running UI. IF `role-worker` is unavailable, THEN the coordinator MUST stop that delegation
   and report the missing subagent and its cause (`ADR-role-worker-subagent`).
   Test: `test_entry_preserves_improvement_scope_and_consumer_authority`; review: representative payload.
8. **Independent context**: WHERE the host supports fresh children, the coordinator SHOULD use fresh context without
   parent conversation inheritance and withhold peer conclusions from independent first passes.
   Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
9. **Role authority**: WHEN a local role runs, it MUST return suggestions or evidence while leaving product source,
   retained files, index and HEAD unchanged; the delegated Impeccable session is not a local role and rules 15 to 18
   govern it (`ADR-impeccable-session-authority`). Review: local role text and
   `test_entry_preserves_improvement_scope_and_consumer_authority`.
10. **Host limits**: IF an interaction tool, fresh child or authorized operation is unavailable, THEN the coordinator
    MUST disclose actual coverage and the concrete blocker without claiming independent execution or native isolation.
    IF Impeccable is unavailable, THEN the coordinator MUST name the upstream install routes and continue inline when
    the user wants; installation follows rule 19 (`ADR-impeccable-session-authority`).
    Review: orchestration fallback, role return instructions and
    `test_impeccable_delegation_is_selected_briefed_routed_and_accepted`.
11. **Verification**: WHEN reporting an improvement on either route, the coordinator MUST report before/after
    interface verification and applicable project-check outcomes separately from design inference and unavailable
    coverage. The bundle adds no mandatory independent review; every review required by the selected consumer
    workflow remains required. Test: `test_task_route_approval_is_explicit_reused_and_bounded`; review only: actual
    model behavior and representative instruction scenarios.
12. **Qualified completion**: WHEN a normal improvement request finishes, the coordinator SHOULD return the changed
    interface or flow and verification status, selected route, stale-document follow-up and remaining unauthorized
    Git effects, or preserve useful partial work with a concrete blocker.
    Review: `test_entry_preserves_improvement_scope_and_consumer_authority`.
13. **Independent installation**: The bundle MUST install through dist/catalog without agt, docs or spec packages.
    Test: `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/test_installed_consumer.py`.
14. **Artifact preservation**: WHEN the bundle is removed or reselected, sync MUST preserve user-owned design artifacts.
    Tests: `test_removal_preserves_user_artifacts_and_other_selected_assets` and the installed-consumer test.
15. **User-selected delegation**: WHERE the user has not selected the Impeccable track, the coordinator MUST NOT start
    an Impeccable session or load or invoke Impeccable in its own context; an installed Impeccable permits an offer,
    and output of a hook the user installed is consumer check evidence (`ADR-impeccable-session-authority`).
    Review: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted`.
16. **Session brief and routing**: WHEN delegating to Impeccable, the coordinator MUST complete pre-implementation
    workflow steps required by the selected route, pass a self-contained brief (goal, the framing result citing the OOUX documents
    by path read-only or the conversation framing, consumer drafts or specifications by path read-only, absolute
    working directory, recorded base, edit list, unchanged concerns, context-file permission with `PRODUCT.md` or
    `DESIGN.md` only on the user's explicit direction, routed commands excluding `live`, stop condition, expected
    return) and make no product edits until the session returns. A fresh child MUST run only refinement commands that
    need no user answers, loading Impeccable through the host's skill mechanism, and MUST return any upstream question
    or load failure as a blocker; new work, `init`, `shape`, `critique` and any blocked command run in a session the
    user operates. The session leaves index, HEAD and files outside its permitted classes unchanged
    (`ADR-impeccable-session-authority`). Review: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted`.
17. **Coordinator acceptance**: WHEN a session returns, the coordinator MUST compare the working directory with the
    recorded base, take only listed product-file changes into verification, report session output and other changes
    without reverting or deleting them on its own initiative, and report a moved HEAD, missing base or unobservable
    ignored path as unverifiable attribution or limited coverage. It MUST report each stale consumer OOUX or UX
    document, the affected statement and a concrete separate follow-up through the documentation process where
    present or a separate documentation task otherwise. The skill run MUST NOT edit those documents or create a
    follow-up record without a separate request (`ADR-uiux-task-approved-run`).
    Review: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted`.
18. **Consumer context files**: WHEN a session creates or changes `PRODUCT.md`, `DESIGN.md` or shared `.impeccable/`
    context files, the coordinator MUST report them as consumer-owned with upstream's retention guidance
    (`ADR-impeccable-session-authority`). Review: `test_project_files_setup_and_cleanup_follow_the_users_request`.
19. **User-requested setup and cleanup**: WHERE the user requests it, the coordinator MAY install Impeccable through an
    upstream route that needs no prompt answers (otherwise it hands the user the exact command), add upstream's
    recommended ignore entries confined to `.impeccable/` paths after showing the exact lines, remove Impeccable
    runtime or session output the user names, or add to `PRODUCT.md` a reference section naming the consumer's OOUX
    documents without copying them; it MUST NOT take any of these actions on its own initiative. `PRODUCT.md` and
    `DESIGN.md` MUST change, by the coordinator or a permitted session, only on the user's explicit direction. The
    action follows rule 3 (`ADR-impeccable-session-authority`).
    Review: `test_project_files_setup_and_cleanup_follow_the_users_request`.
20. **Task route choice**: WHEN implementation or requested setup/cleanup enters the skill, the coordinator MUST
    announce the outside-workflow procedure and obtain explicit task approval or follow the consumer workflow the
    user chooses, before product edits or write-capable delegation. An exact prior route instruction is reused;
    without an answer or approval channel dependent edits wait. Review-only work needs no route choice.
    Test: `test_task_route_approval_is_explicit_reused_and_bounded`.
21. **Scope growth**: WHEN work adds a surface or behavior beyond the approved goal or changes a user constraint,
    the coordinator MUST obtain a new user decision before the dependent edit. An in-goal file addition or
    implementation choice alone is not scope growth. Test: `test_task_route_approval_is_explicit_reused_and_bounded`.
22. **Git effects**: WHEN commit, integration or publication lacks current task authority, the coordinator MUST
    present the verified result and obtain authority once for the named remaining effects before acting. Route
    choice alone grants none; exact prior authority is reused. Test: `test_task_route_approval_is_explicit_reused_and_bounded`.

Instruction review verifies stated behavior, not model obedience, aesthetic quality or superiority over one agent.
Selection changes neither the development approach nor the consumer's execution authority. The distribution-owned
root bundle inventory can name the selection; the bundle supplies no design guidance fragment or constitution.

## 4. Interfaces and Data Contracts

Select `uv run devkit add app-uiux-improve` or app-uiux-improve:core, then explicitly invoke `/app-uiux-improve <goal>`.
Registration is `app-uiux-improve = "devkit_catalog.app_uiux_improve"`. No new command, code or runtime is added.
The bundle needs no devkit-spec or devkit-docs installation; consuming projects retain their own workflow requirements.

The entry routes optional reads to `references/design-guidance.md` (object framing, its conditional sources, design
lenses and baseline craft checks) and `references/orchestration.md` (local roles and the Impeccable brief, routing,
acceptance and user-requested setup and cleanup). Local roles are designer, unconventional-designer,
reference-researcher and critic. Only selected bodies are loaded. Each role return contains status (completed,
partial or failed), inspected identities, concrete work, assumptions and unverified areas; research includes source
provenance, and critique includes evidence, failure conditions and repairs. A failed or absent role supplies no
findings. An Impeccable session return lists changed files, commands run, detector or audit results, session output,
degraded coverage and blockers. The coordinator owns synthesis, acceptance and retained output; product changes follow
rules 3, 16, 17 and 19–22.

Without a requested destination, the result stays in conversation. Product artifacts follow consumer ownership;
no retained document kind, mandatory design brief or persistent memory is introduced. The bundle's human usage guide
is `bundle/README.md` beside `bundle.toml`, linked from the catalog README and from no agent-read file.
