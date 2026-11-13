---
id: PROP-uiux-improve-pilot-fit
title: app-uiux-improve run model and pilot fixes
summary: "Lets app-uiux-improve run its own lightweight improvement loop outside the consumer's development workflow by default, with an announced opt-in, and fixes the question routing, host loading, verification-target, brief-hygiene, context-file, invocation and contrast gaps a consumer pilot exposed."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-13
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/
    - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py
    - packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/
  excludes:
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit-dist/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-uiux-improve-pilot-fit] app-uiux-improve run model and pilot fixes

## 1. Background & Hypothesis

`app-uiux-improve` 0.1.6 ran once in a consumer SDD repository for a whole-surface color-system refresh, with the
user-selected Impeccable track. `MAT-uiux-improve-pilot` holds the observations, workarounds and run shape; the
finding IDs below (A1 to A7) refer to it. The bundle's design held up where it was exercised: independent role passes
converged, the brief and edit-list acceptance stayed clean, and running direction synthesis before the consumer
workflow meant the spec captured an approved direction. The gaps are in the run model and in instructions the pilot
had to improvise around.

### Headline: the consumer development workflow does not fit a whole-surface improvement

`CAP-DLV-uiux-improvement` rule 3 requires the coordinator to carry every requested change through the consumer's
existing workflow (`ADR-uiux-improvement-workflow-boundary` clause 2, kept by `ADR-impeccable-session-authority`). In
the pilot that meant a `spec`-depth Unit through `specify`, `build-verify`, `review-refine`, `living-spec-draft` and
integration.

- Cost: 18 branch commits; eight record one envelope each and two change only the spec status.
- Fit: the direction emerged iteratively (role passes, user picks, reviewer findings, polish). The up-front contract
  kept needing amendments during `build-verify`, and each amendment then needed a separate authority record. A
  Host-invented Non-Goal had to be lifted mid-way.
- Value to keep: the UX reviewer caught a semantic defect, code review caught a test gap, and reconcile kept the UX
  documents in step.

devkit already treats one class of whole-surface work differently: `overall-refactor` runs `sdd-overall-refactor`
without a Unit, proposal or spec bundle (`ADR-delivery-classification`). A whole-surface UI/UX improvement has a
similar shape: its scope is a surface, not a contract, and its direction is found by iteration.

Hypothesis: if the skill, by default, runs its own lightweight loop and tells the user so before starting, with an
opt-in to the repository workflow, a whole-surface improvement costs a fraction of the bookkeeping. The loop is
inspect, independent role passes, user picks, implement (inline or Impeccable), project checks and before/after
verification. Keeping UX review, code review and a documentation hand-off as independent checks inside that loop
retains the value the workflow added.

### Further gaps

1. Interactive Impeccable commands (A1). The skill routes `init`, `shape` and `critique` to a session the user
   operates, because "no actor answers on the user's behalf" (`ADR-impeccable-session-authority`). The pilot instead
   split `init` in a child: phase 1 scanned and drafted the question round without writes. The coordinator then
   pre-filled answers from the OOUX documents and asked the user only the gaps. Phase 2 resumed the same child to
   write. The user still decided every answer the documents did not settle, and the round trip stayed inside one
   conversation.
2. Host loading (A2). A fresh Claude Code child could not load a plugin-installed Impeccable through the Skill tool,
   which `ADR-impeccable-session-authority` left unverified. Reading `SKILL.md` and `reference/*.md` from the plugin
   cache worked twice. The skill says to return this as a blocker. Related: `AUTONOMY_DIRECTIVE_CHECK` asks a child
   for a live probe it cannot run. `impeccable context` needs `--target <ui path>` in a monorepo and still reported
   `hasVisualImplementation=false`.
3. Verification target (A3). SKILL step 2 says "using the running UI when available" without saying which build. The
   coordinator chose the deployed environment, which cannot show branch changes. A local dev server of the branch
   build with Playwright API mocking and a re-runnable before/after harness worked and kept the shared database out
   of the run.
4. Brief and spec hygiene (A4a to A4c).
   - Task focus ("color first") became a Non-Goal that contradicted `PRODUCT.md`.
   - The brief did not state precedence when an Impeccable craft rule conflicted with the spec.
   - Acceptance compared the change only with the edit list, so an in-list but out-of-scope fix passed.
5. Local-only context files (A5). Git-excluded `PRODUCT.md` and `DESIGN.md` do not exist in a fresh worktree, and
   Impeccable `init` advises committing them. An in-place branch under `worktree=auto` sidestepped it.
6. Invocation guard (A6). After a mid-session install, the user's natural-language agreement could not invoke a
   `disable-model-invocation: true` skill. "Run only when the user explicitly invokes this entry" does not say
   whether such agreement counts.
7. Contrast (A7). A designer role's approximate contrast estimate passed a 2.06:1 pair that a computed OKLCH to sRGB
   check caught.

## 2. Technical Spike Questions

- **Q1 (main design question)**: How does the skill relate to a configured development workflow? Candidates:
  - (a) default outside the workflow: announce up front that the skill's own loop runs instead of the repository
    workflow, offer the opt-in, and proceed after the user's approval;
  - (b) ask each time which mode to use, with no default;
  - (c) a dedicated lightweight devkit workflow for whole-surface improvement, analogous to `sdd-overall-refactor`,
    which keeps the recorded gates but not a Unit.

  Settle whether the skill states explicitly that it proceeds outside an established methodology even when one is
  configured. Settle which checks stay mandatory in the loop (independent UX review, independent code review,
  project checks, before/after verification). Settle whether a local change keeps rule 3 unchanged. Each option
  conflicts with `CAP-DLV-uiux-improvement` rule 3, `ADR-uiux-improvement-workflow-boundary` clause 2 and the
  consumer-authority clauses of `ADR-impeccable-session-authority`, so the outcome needs a superseding ADR.
- **Q2**: Outside the workflow, who supplies commit, integration and publication authority? Direction: ask for each
  Git effect explicitly, because the workflow no longer grants it. Settle how this interacts with a consumer's
  `worktree` and `pull_request` policy and with a host that has no approval channel.
- **Q3**: How does Living Spec and UX document impact reach the repository? Direction: keep the existing report-only
  rule (rule 17) and hand the report to the repository workflow as a follow-up documentation task. Settle whether the
  hand-off names a concrete next step (for example a `spec`-depth doc-sync task) or only reports.
- **Q4**: Can a coordinator-relayed question route for interactive commands (gap 1) coexist with "no actor answers
  on the user's behalf"? Settle what counts as pre-filling from documents versus answering for the user. Settle
  whether the user must confirm pre-filled answers, and whether `shape` and `critique` (two isolated sub-agents) fit
  the same split. This needs a partial supersession of `ADR-impeccable-session-authority`.
- **Q5**: Is a plugin-cache file-read fallback (gap 2) an acceptable documented route, or does it bypass the host's
  skill mechanism in a way the ADR meant to forbid? Verify on Codex as well as Claude Code, and decide how the brief
  handles `AUTONOMY_DIRECTIVE_CHECK` and `impeccable context --target`.

## 3. Proposed Design & Impact

Directions, not final wording; Planning settles each.

1. Run model (Q1 to Q3). The default proceeds as option (a) unless Planning picks another:
   - At entry, state the mode in one line, offer the repository workflow as an opt-in, and proceed after the user
     approves.
   - Keep independent UX review and code review as optional checks the coordinator offers in the loop.
   - Ask for commit, integration and publication authority per effect.
   - End with the stale-document report and a named hand-off to the repository workflow.
   - Rewrite rule 3 for the chosen mode and write a superseding ADR.
2. Question route (Q4). For `init`, and for other commands if Planning confirms, add a two-phase child route: phase 1
   scans and drafts questions without writes; the coordinator pre-fills from cited documents and asks the user the
   gaps (and confirmation if Planning requires it); phase 2 resumes the same child to write. Write a partial
   supersession of `ADR-impeccable-session-authority` for the routing clause.
3. Host loading (Q5). Record the Claude Code observation in the ADR consequences and the README troubleshooting
   table. If Planning accepts the fallback, document the plugin-cache read as a route the brief names. The brief
   template names `impeccable context --target <ui path>` for monorepos and says how to treat
   `AUTONOMY_DIRECTIVE_CHECK` in a child.
4. Verification target. SKILL step 2 and step 8 say to inspect and verify the branch build running locally. When the
   backend is costly or shared, stub it (for example API mocking in the browser driver). Keep a re-runnable
   before/after capture. A deployed environment is at most a baseline.
5. Brief and spec hygiene.
   - Non-Goals carry only user-stated constraints or explicit deferrals; a task focus is not a prohibition.
   - The brief states precedence when Impeccable craft rules conflict with the brief or spec.
   - Acceptance compares the accepted change with the spec's or request's scope as well as the edit list, and
     reports an in-list but out-of-scope change.
6. Local-only context files. When `PRODUCT.md` or `DESIGN.md` is untracked or excluded, prefer an in-place branch
   under `worktree=auto`, or pass main-checkout absolute paths read-only. Tell the session to skip Impeccable's
   commit advice unless the user decides otherwise.
7. Invocation. Clarify what "explicitly invokes" covers. Candidate: the user's explicit agreement in the same
   conversation to run this skill after the coordinator named it counts, because a mid-session install leaves no
   slash command to type. Confirm against `CAP-DIST-agent-projections` semantics.
8. Contrast. `design-guidance.md` and the designer roles recommend a computed contrast check (color-space conversion,
   not an approximation) for color work, and report the measured ratio for each key pair.

Impact: `CAP-DLV-uiux-improvement` (rules 3, 10, 16, 17 and new rules), `UC-improve-an-interface-and-user-flow`,
one or two new ADRs, the bundle's `SKILL.md`, `references/orchestration.md`, `references/design-guidance.md`, roles
and README, and the bundle tests. Option (c) of Q1 would also touch the delivery workflow definitions
(`CAP-DLV-delivery-workflows`) and `packages/devkit-spec/`; if Planning picks it, raise the size or split the work.
Spec and envelope tooling friction from the same pilot is recorded as separate feedback, not here.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to `sdd-spec-feature` on
  `dev-uiux-improve-pilot-fit`. The proposal is deleted there, its decisions become ADRs (including the superseding
  ADR for Q1), and `MAT-uiux-improve-pilot` moves to `docs/materials/`.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
