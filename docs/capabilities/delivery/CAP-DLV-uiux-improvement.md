---
id: CAP-DLV-uiux-improvement
title: Software interface UI/UX improvement
summary: "An opt-in UI/UX skill improves interfaces through approved routes and capability-gated Impeccable relay. Its POSIX helper links tracked context per worktree and checks drift while preserving consumer content and setup authority."
area: delivery
status: active
created_at: 2026-11-05
usecases:
  - UC-improve-an-interface-and-user-flow
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md
  - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/scripts/link-impeccable-context.sh
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
`ADR-impeccable-session-authority` the bounded Impeccable session and user-requested setup and cleanup, and
`ADR-impeccable-question-relay` the capability-gated question relay.
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

1. **Opt-in distribution**: WHERE app-uiux-improve:core is selected, sync MUST deploy one skill including its context-link script and four local role
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
   A task focus orders work; the coordinator MUST derive non-goals only from user-stated constraints or explicit
   deferrals. Tests: `test_framing_is_proportionate_and_reads_ooux_documents_only_where_present` and
   `test_brief_focus_precedence_and_acceptance_preserve_the_approved_goal`.
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
    the user wants; installation follows rule 19 (`ADR-impeccable-session-authority`). IF a child cannot load it,
    THEN the coordinator MUST report observed current-project plugin enablement, native availability and the
    user-operated fallback without prescribing cache-file loading or an unauthorized enablement change
    (`ADR-impeccable-question-relay`). Tests: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted`
    and `test_relay_failure_reporting_preserves_authority_and_honest_coverage`.
11. **Verification**: WHEN reporting an improvement on either route, the coordinator MUST report before/after
    interface verification and applicable project-check outcomes separately from design inference and unavailable
    coverage. WHEN the local branch build is executable, the coordinator MUST inspect that build before edits and
    verify it after edits with the same representative task/data and a re-runnable capture method; a deployed
    environment supplies at most a baseline. WHERE a live backend is costly or shared, a repeatable mock MAY drive
    that branch build; the report MUST label mocked coverage as mocked, not an end-to-end check, and name missing
    live coverage. WHEN changing color, the coordinator and assigned designer roles MUST compute effective-color
    contrast with color-space conversion and opacity/compositing, reporting numeric ratios per key pair/state,
    applicable consumer criteria and missing measurement coverage. An estimate establishes no measured contrast.
    The bundle adds no mandatory independent review; every review required by the selected consumer
    workflow remains required. Tests: `test_task_route_approval_is_explicit_reused_and_bounded`,
    `test_verification_targets_the_changed_branch_and_qualifies_mocks` and
    `test_color_work_requires_computed_effective_color_contrast`; review only: model behavior and live outcomes.
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
    workflow steps required by the selected route, pass a self-contained brief (goal, framing result with read-only
    OOUX paths or conversation framing, read-only consumer drafts or specifications, absolute working directory,
    recorded base, edit list, unchanged concerns, context-file permissions, commands excluding `live`, stop condition
    and expected return), and make no product edits until the session returns. `PRODUCT.md` or `DESIGN.md` changes
    require the user's explicit file/action direction. The session leaves index, HEAD and files outside its permitted
    classes unchanged (`ADR-impeccable-session-authority`). The brief MUST state that authorized brief and consumer
    specification content controls craft defaults, returning conflicts between authorized sources for a decision.
    WHEN local-only `PRODUCT.md` or `DESIGN.md` is untracked or excluded and the session runs elsewhere, the brief
    MUST pass absolute read-only paths, without inferring copy, commit, ignore or removal authority.
    Answer-free refinement uses a fresh child loading Impeccable through the host's skill mechanism. Interactive
    question relay MUST use native loading and same-child continuation observed for the actual host/project;
    documentation, inherited skill names and cache reads do not establish them. `shape` and `critique` additionally
    require the child's nested-role capabilities needed by the loaded command. Unavailable or unverified required
    capabilities and lost continuation use the user-operated session, without reconstructed writing children or
    claimed equivalent inline roles (`ADR-impeccable-question-relay`).
    The relay's first phase MUST only inspect and draft the complete question packet, with no retained-file, product,
    index or HEAD writes. Its packet names each question and supplies source paths/passages for document-derived
    suggested answers. Before the same child writes, the coordinator MUST obtain confirmation of every answer,
    including every pre-fill; one explicit confirmation of the complete visible packet is valid, while silence,
    omitted answers and gaps-only confirmation are not. Confirmed answers stay unchanged. New questions or changed
    relevant source facts, file state, answers or scope return for affected-answer confirmation before dependent
    writes. Partial execution is reported against the recorded base without blind replay or unsolicited reversion.
    Tests: `test_interactive_relay_requires_native_capabilities_and_every_user_answer`,
    `test_relay_failure_reporting_preserves_authority_and_honest_coverage`,
    `test_brief_focus_precedence_and_acceptance_preserve_the_approved_goal` and
    `test_local_context_and_plugin_diagnosis_stay_workflow_neutral`; review only: live model/host behavior.
17. **Coordinator acceptance**: WHEN a session returns, the coordinator MUST compare the working directory with the
    recorded base, take only changes matching both the edit list and approved goal scope into verification, report
    an in-list but out-of-scope change without accepting it, and report session output and other changes
    without reverting or deleting them on its own initiative, and report a moved HEAD, missing base or unobservable
    ignored path as unverifiable attribution or limited coverage. It MUST report each stale consumer OOUX or UX
    document, the affected statement and a concrete separate follow-up through the documentation process where
    present or a separate documentation task otherwise. The skill run MUST NOT edit those documents or create a
    follow-up record without a separate request (`ADR-uiux-task-approved-run`).
    Tests: `test_impeccable_delegation_is_selected_briefed_routed_and_accepted` and
    `test_brief_focus_precedence_and_acceptance_preserve_the_approved_goal`.
18. **Consumer context files**: WHEN a session creates or changes `PRODUCT.md`, `DESIGN.md` or shared `.impeccable/`
    context files, the coordinator MUST report them as consumer-owned with upstream's retention guidance
    (`ADR-impeccable-session-authority`). Local-only context reads MUST preserve that ownership and retention choice
    without inferring a new copy, commit, ignore or removal action. Tests:
    `test_project_files_setup_and_cleanup_follow_the_users_request` and
    `test_local_context_and_plugin_diagnosis_stay_workflow_neutral`.
19. **User-requested setup and cleanup**: WHERE the user requests it, the coordinator MAY install Impeccable through an
    upstream route that needs no prompt answers (otherwise it hands the user the exact command), add upstream's
    recommended ignore entries confined to `.impeccable/` paths after showing the exact lines, remove Impeccable
    runtime or session output the user names, run the context-link helper to create absent root context links and
    add only `/PRODUCT.md`, `/DESIGN.md`, `/.impeccable` to the resolved local Git exclude file after showing these
    exact lines, or add to `PRODUCT.md` a reference section naming the consumer's OOUX
    documents without copying them; it MUST NOT take any of these actions on its own initiative. `PRODUCT.md` and
    `DESIGN.md` MUST change, by the coordinator or a permitted session, only on the user's explicit direction. The
    coordinator MAY run read-only helper checks while gathering context. The action follows rule 3
    (`ADR-impeccable-session-authority`, `ADR-impeccable-context-links`).
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

23. **Detector evidence**: IF Impeccable reports `hasVisualImplementation=false`, THEN the coordinator MUST treat
    detection as advisory and inspect the actual target path, UI code and executable local branch build, reporting
    detector limits separately from inspected evidence without inferring absent UI or promising that `--target`
    guarantees discovery. Test: `test_impeccable_limits_require_evidence_and_authorized_continuation`.
24. **Capability brief**: WHEN preparing an Impeccable brief, the coordinator MUST name actual observed capabilities,
    unavailable or unverified capabilities and stop conditions for missing required probes/capabilities, questions,
    conflicts and denied operations. The brief supplies task boundaries, not a passed upstream check or authority
    to override one. Test: `test_impeccable_limits_require_evidence_and_authorized_continuation`.
25. **Unavailable autonomy probe**: IF a child cannot run a live probe required by `AUTONOMY_DIRECTIVE_CHECK`, THEN
    the coordinator MUST report the unavailable probe and stop dependent Impeccable work, without claiming a pass
    or substituting brief stop conditions for the requirement. Continuation uses the user-operated session or
    already authorized/user-chosen inline work, preserving native loading, every-answer confirmation and host
    permissions on their applicable routes; inline work claims no Impeccable execution or probe result.
    Test: `test_impeccable_limits_require_evidence_and_authorized_continuation`.
26. **Supported audit persistence**: WHEN attempting audit persistence, the coordinator MUST inspect installed
    supported help/interface first and use only a supported operation within existing permissions. IF
    `audit-storage write` is unsupported, THEN the session MUST return audit findings and coverage in its report
    with persistence marked unavailable, without invented/retried commands, guessed replacements, unrequested
    files or installation changes. Test: `test_impeccable_limits_require_evidence_and_authorized_continuation`.

27. **Context-link helper**: WHEN the optional helper runs, it MUST implement the fixed-entry, source preflight,
    classification, stable-code/action and exit contracts in section 4.1. Tests:
    `packages/devkit-catalog/tests/integration/bundles/test_impeccable_context_links.py`.
28. **Read-only context inspection**: WHERE `--check` is given, the helper MUST leave filesystem, index and HEAD
    unchanged, creating no temporary file or lock. Test: `test_links_are_relative_idempotent_and_checked_without_writes`.
29. **Bounded context setup**: WHEN link mode runs with quiescent managed root entries and source, the helper MUST
    preserve occupied root entries, source bytes and unrelated exclude bytes while creating only absent relative
    links and missing exact exclude lines. Noncooperating concurrent writers are unsupported; the coordinator
    stops its own writers before requested setup. Tests: `test_check_reports_every_unresolved_state_and_preserves_root`,
    `test_excludes_preserve_unterminated_bytes_deduplicate_and_respect_lock`.
30. **Source retention ownership**: WHEN `.impeccable` is linked, the coordinator MUST leave source-side runtime
    ignore policy and content changes with the consumer; root-link exclusion grants no additional content authority.
    Test: `test_context_link_setup_and_check_keep_consumer_authority`.

Instruction review verifies stated behavior, not model obedience, aesthetic quality or superiority over one agent.
Selection changes neither the development approach nor the consumer's execution authority. The distribution-owned
root bundle inventory can name the selection; the bundle supplies no design guidance fragment or constitution.

## 4. Interfaces and Data Contracts

Select `uv run devkit add app-uiux-improve` or app-uiux-improve:core, then explicitly invoke `/app-uiux-improve <goal>`.
Registration is `app-uiux-improve = "devkit_catalog.app_uiux_improve"`. The helper is skill content; no devkit command or Python runtime feature is added.
The bundle needs no devkit-spec or devkit-docs installation; consuming projects retain their own workflow requirements.

The entry routes optional reads to `references/design-guidance.md` (object framing, its conditional sources, design
lenses and baseline craft checks) and `references/orchestration.md` (local roles and the Impeccable brief, routing,
acceptance and user-requested setup and cleanup), and to `references/impeccable-limits.md` when preparing an
Impeccable brief or handling detector, autonomy-probe or audit-persistence limits. That reference mitigates local
handling; it fixes no upstream runtime behavior. Local roles are designer, unconventional-designer,
reference-researcher and critic. Only selected bodies are loaded. Each role return contains status (completed,
partial or failed), inspected identities, concrete work, assumptions and unverified areas; research includes source
provenance, and critique includes evidence, failure conditions and repairs. A failed or absent role supplies no
findings. An Impeccable session return lists changed files, commands run, detector or audit results, session output,
degraded coverage and blockers. The coordinator owns synthesis, acceptance and retained output; product changes follow
rules 3, 16, 17 and 19–22.

Without a requested destination, the result stays in conversation. Product artifacts follow consumer ownership;
no retained document kind, mandatory design brief or persistent memory is introduced. The bundle's human usage guide
is `bundle/README.md` beside `bundle.toml`, linked from the catalog README and from no agent-read file.

### 4.1 Context-link helper

`sh <installed-skill>/scripts/link-impeccable-context.sh [--check] [--] [<source-dir>]` uses POSIX sh/utilities and
Git. Default source is `docs/materials/impeccable`; relative arguments resolve from the physical current worktree
root. A source must be an existing physical in-worktree directory below the root and outside Git metadata, with no
control characters. Present `PRODUCT.md`/`DESIGN.md` entries must be regular unlinked readable files; present
`.impeccable` must be an unlinked readable/searchable directory. Missing entries are optional. Invalid preflight
and `core.symlinks=false` return exit 2 before mutation. Each link target is the normalized relative source plus its
fixed entry name. Equivalent absolute or differently spelled existing targets are wrong targets.

Classification order is tracked root, absent source, absent root, root nonlink, dangling link, literal target.
A tracked root stays tracked. Replaced regular files compare with `cmp`; matching directories compare with Git's
read-only no-index diff, disabling external diff/textconv and mode differences. Comparison diagnostics/unsupported
exits are inspection failure. Literal target capture preserves newline bytes and never prints raw target data.

| Stable code | Meaning | Action |
| --- | --- | --- |
| `LINK_CREATED`, `LINK_OK`, `LINK_ABSENT` | Created, correct, or source/root both absent | `NONE` |
| `LINK_MISSING` | Source present, root absent | `RUN_LINK` |
| `LINK_STALE`, `LINK_DANGLING`, `LINK_WRONG_TARGET` | Source absent with root link, missing target, or different literal target | `INSPECT_LINK` |
| `LINK_OCCUPIED` | Source absent with root nonlink | `INSPECT_ROOT` |
| `LINK_REPLACED` | Source present with root file/directory; `content=equal|differs|type_mismatch` | `MERGE_INTO_SOURCE` |
| `LINK_TRACKED` | Root entry is tracked by Git | `UNTRACK_MANUALLY` |
| `EXCLUDE_ADDED`, `EXCLUDE_OK`, `EXCLUDE_MISSING` | Exact exclude appended, present, or missing in check mode | `NONE`, `NONE`, `RUN_LINK` |
| `LINK_ARGUMENT_INVALID`, `LINK_NOT_WORKTREE`, `LINK_SYMLINKS_DISABLED`, `LINK_SOURCE_INVALID` | Invalid input or unsupported checkout/source | `FIX_INPUT`, `USE_WORKTREE`, `ENABLE_SYMLINKS`, `FIX_SOURCE` |
| `LINK_INSPECTION_FAILED`, `LINK_IO_FAILED`, `LINK_EXCLUDE_BUSY` | Inspection, I/O or held helper lock | `INSPECT_FILES`, `CHECK_PERMISSIONS`, `RETRY_AFTER_UNLOCK` |

Stdout emits fixed-entry `[CONTEXT_LINK: ... code=... action=...]`, `[CONTEXT_EXCLUDE: ... code=... action=...]`
records and one terminal `[CONTEXT_LINK_RESULT: mode=link|check code=... exit=... action=...]`.
Clean result is `LINK_CLEAN`/`NONE` exit 0; unresolved states are `LINK_PROBLEMS`/`INSPECT_REPORTED` exit 1;
inability to run uses the specific failure code/action and exit 2. Stderr carries bounded failure details. There is
no JSON mode. Successful link-mode repairs do not count as problems. Other occupied entries do not stop eligible
links; I/O failure stops with already reported partial effects retained, without rollback or automatic repair.

Excludes are resolved with `git rev-parse --git-path info/exclude`, shared by linked worktrees. Missing exact
`/PRODUCT.md`, `/DESIGN.md`, `/.impeccable` lines are appended without duplicates, adding a separator newline when
needed and retaining existing bytes. Updates hold an adjacent `info/exclude.impeccable-context.lock` directory
created exclusively; an existing lock refuses before exclude writes, and only the creator releases its lock.
The helper never stages/untracks, edits root `.gitignore`, creates context content or installs source-side ignores.
