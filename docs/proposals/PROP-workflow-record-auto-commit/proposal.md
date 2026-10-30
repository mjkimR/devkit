---
id: PROP-workflow-record-auto-commit
title: Automatic commits for workflow records
summary: "Adds explicit automatic commits for authored workflow envelopes, using deterministic messages derived from the Unit slug and record identity. Preserves existing source-change, approval and integration boundaries."
status: reviewing
created_at: 2026-10-30
target_area: delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit/tests/unit/features/workflow/
    - packages/devkit/tests/integration/features/workflow/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - docs/capabilities/delivery/
    - docs/usecases/delivery/
  excludes:
    - docs/decisions/
    - packages/devkit/src/devkit_agt/features/gate/
    - packages/devkit/src/devkit_agt/features/worktree/
    - packages/devkit/src/devkit_agt/features/integration/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-workflow-record-auto-commit] Automatic commits for workflow records

## 1. Background & Hypothesis

Workflow record commands know which Unit and record they write, but the executor still stages those files,
invents a commit message and runs Git. For stages that only persist an envelope, message authoring adds a
repeated decision without describing a new implementation change.

The inspected implementation and guidance establish these boundaries:

- `sdd-spec-feature.md` requires plain `git commit` at every stage boundary. `sdd-session-feature.md` requires a
  plain commit before integration approval. These instructions live under
  `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/`.
- `WriteEnvelopeUseCase.execute` in
  `packages/devkit/src/devkit_agt/features/workflow/usecases/envelopes.py` writes the next envelope and returns
  its Unit, file, kind, sequence, status and skeleton flag. It neither stages nor commits the file.
- `RecordAnswerUseCase` in `packages/devkit/src/devkit_agt/features/workflow/usecases/answers.py` writes a decision
  record without committing it. Proposal acceptance also requires its status and gate record committed together
  under `CAP-DLV-proposal-incubation`.
- Merge messages already have a deterministic template, `chore(merge): integrate <branch> into <target>`, in
  `packages/devkit/src/devkit_agt/features/worktree/services/merging.py`. That implementation creates integration
  commits; it is not a general record-commit operation.

Hypothesis: an explicit automatic-commit path for authored envelopes removes routine staging and message
composition while retaining existing hooks and authorization. The Unit slug plus stage, kind and sequence
provides enough identity for a record-only commit. Source changes still need a message describing their behavior.
No reduction in latency, tokens or total cost has been measured.

`CAP-DLV-workflow-envelopes`, `CAP-DLV-workflow-orchestration` and `CAP-GATE-commit-gates` are the current contracts.
`PROP-local-orch-resource-manager` delegates existing Git/lifecycle operations to a reusable agent; this proposal
adds a deterministic CLI operation and does not require that role. `PROP-maintenance-history` publishes maintenance
records on a separate remote branch and does not cover local Unit envelope commits.

## 2. Technical Spike Questions

- **Q1 — Invocation:** Should authoring commands accept `--commit`, or should a separate command commit a known
  record after writing? Prefer explicit opt-in at eligible workflow call sites; retain write-only library behavior
  and existing CLI behavior when commit mode is absent. Compare retry behavior before choosing the interface.
- **Q2 — Commit boundary:** Which envelope-only call sites can opt in without separating a record from source or
  document changes it must accompany? Determine how several related envelopes share one stage-boundary commit.
- **Q3 — Git behavior:** What is the simplest implementation that commits only the declared files, preserves
  existing index/worktree content, runs normal hooks and respects signing and repository message policy?
  Prefer refusing ambiguous dirty state over introducing a custom index transaction framework.
- **Q4 — Recovery and evidence:** How does a failed commit retry the existing envelope without allocating another
  sequence? Distinguish the envelope's reviewed `diff_scope.head` from the resulting record commit SHA, and verify
  that adding a record commit does not invalidate final review or integration preparation.

## 3. Proposed Design & Impact

### Candidate assessment

| Operation | Automatic-commit suitability | Boundary |
| :--- | :--- | :--- |
| `final-change-report` | First candidate | Only the final-report envelope remains to persist after verified source and document commits. |
| Review/reverify or support-role envelope | Candidate when record-only | If fixes or proposal edits accompany the result, keep the existing combined commit. |
| `collect-feedback` with no findings | Candidate when record-only | A sweep that changes feedback files needs an explicit multi-file boundary; an envelope alone is insufficient. |
| Worker/answer/resolution envelope | Conditional | Commit only when accompanying work is already committed; never detach unfinished work or a fix from its required record. |
| Decision records and proposal acceptance | Assessed, excluded from initial implementation | Acceptance couples status and authority records; slug-derived text alone cannot represent that operation safely. |
| Implementation, Living Spec edits, rejection or reclassification | Keep existing message authoring | Describe actual changes and preserve required user reasons; emergency commits retain their separate procedure. |
| Merge/integration | Already automated | Keep the existing merge template and guarded integration route. |

### Recommended first scope

- Add explicit commit support for fully authored, schema-valid envelopes. Skeleton generation remains write-only.
  `completed`, `needs_input` and `failed` describe the recorded run; committing them grants no pass or approval.
- Derive the slug from the bound Unit identity rather than the branch name. Derive the record identity from the
  actual written kind and sequence. A non-normative subject example is
  `chore(workflow): record workflow-record-auto-commit final-change-report final-report-01`.
  Planning settles formatting and compatibility with repository message conventions.
- Prefer a clean starting index and no unrelated worktree changes for automatic mode. Commit only the explicitly
  identified envelope files. If accompanying edits exist, return a stable actionable refusal and use the existing
  manual combined commit. Do not stage the whole Unit or repository implicitly.
- Use ordinary Git commit hooks and configured signing. A hook or permission refusal leaves the authored envelope
  available for inspection and recovery. Never retry with `--no-verify`, claim a commit happened, reset user changes
  or remove the record to hide the failure.
- Report written paths, generated subject, resulting commit SHA and partial failure state through existing agent
  output conventions. Validate knowable Git prerequisites before writing. A retry after record creation targets
  that same record rather than silently creating another envelope.
- Keep read-only commands (`next`, `check`, `show`) free of commits. Writing or committing a record does not grant
  `plan-accept`, `proposal-handoff`, `dev-integration`, push, merge or branch-cleanup authority.
- Update source workflow and skill call sites that meet the record-only boundary. Preserve manual stage-boundary
  commits elsewhere. Keep library authoring usable outside Git; explicit commit mode reports that Git is required.
  Reconcile the retained behavior into delivery capabilities and use cases.

### Expected acceptance checks

- **AC1 — Deterministic identity:** Given the same Unit slug, stage and record identity, the generated subject is
  identical regardless of branch naming. Different Units remain distinguishable.
- **AC2 — Exact scope:** Given an eligible authored envelope, commit mode creates a commit containing only the
  declared record files. Existing staged or unrelated dirty content causes refusal without committing that content.
- **AC3 — Hook and failure recovery:** A rejected hook, signing failure or interrupted commit produces an accurate
  partial result. After inspecting Git state, a supported retry commits the existing record without duplicating it.
- **AC4 — Compatibility:** Without commit mode, authoring remains write-only, including outside Git. Skeletons and
  read-only commands never create commits. Record status does not become approval or successful stage evidence.
- **AC5 — Workflow continuity:** Exercise an eligible final-report stage and one review/reverify stage through
  readiness checks. Keep evidence anchored to the reviewed source revision and identify the later record commit
  separately. A stage with accompanying code or document edits retains its combined manual commit.

### Non-goals

**Scope Excluded:** LLM-generated source commit messages, automatic commits for all file-writing commands,
decision/acceptance transactions, automatic production changes, hook bypass, new approval policy, push or merge
automation, changes to the existing integration template, and a persistent Git service or general recovery framework.

## 4. Lifecycle & Retirement Criteria

This is a queued draft, sized M for one feature spanning the workflow operation and its spec-bundle call sites.
Planning and Development each start with a medium effort recommendation. Planning settles invocation, multi-record
boundaries, recovery and evidence semantics before direction acceptance. No implementation or direction acceptance
is included in adding this draft.

On acceptance, hand off to one feature spec with the selected interface and eligible call sites. Completion requires
the acceptance checks and delivery-contract reconciliation. On rejection, retain `status: rejected` and the user's
reason through the existing proposal retirement procedure.
