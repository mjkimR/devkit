---
id: PROP-workflow-record-auto-commit
title: Automatic commits for workflow records
summary: "Adds an explicit command that commits one authored workflow envelope with a deterministic Unit-based message. Preserves write-only authoring, existing hooks and manual commits for combined changes."
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
    - docs/decisions/
  excludes:
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

## 2. Planning Findings

- **Invocation:** Select a separate command, `devkit workflow envelope commit --unit DIR --file envelopes/NAME.yaml`.
  It commits one existing record and never allocates an envelope sequence. Existing authoring commands and library
  calls remain write-only. `PADR-explicit-envelope-commits` compares the alternatives.
- **Commit boundary:** Limit the first implementation to one new, authored envelope. Multiple pending envelopes or
  accompanying code, feedback or document changes use an ordinary combined commit. Automatic mode is an explicit
  call selected by the executor, not an inferred property of a stage or a new workflow exit requirement.
- **Git behavior:** Use the normal index and ordinary Git commit with a generated message. Refuse dirty paths other
  than the selected file, including other untracked files that Git does not ignore. Permit that file already staged
  only when index bytes match its worktree bytes, so a failed hook can be retried. Preserve the staged file on failure.
- **Recovery:** A repeat invocation uses the same file. If its exact bytes are already present in HEAD and the
  checkout is otherwise clean, report `already_committed` without making another commit. Refuse modified tracked
  envelopes rather than recording an overwrite of immutable history.
- **Evidence:** The existing ancestor primitive compares envelope `diff_scope.head` values, not equality to current
  HEAD. The integration provider reads the final-report from the committed source snapshot. Keep those evidence
  fields unchanged; integration preparation follows the record commit. A local commit hook rewrote both observed
  Planning commits' SHAs, so report `git rev-parse HEAD` after hooks, never a SHA parsed from Git's progress text.

`MAT-workflow-record-commit-planning` records inspected source, alternatives and validation limits. No latency or
cost benchmark is required for this feature; acceptance concerns avoided manual message authoring and correct Git
scope. Development runs its acceptance checks at the same head with explicit commit mode omitted as the baseline.

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

### Selected interface and behavior

The command takes one `--file`, relative to the resolved Unit, naming an immediate file under `envelopes/`.
There is no implicit latest selection, glob, multi-file option, `--message`, or authoring `--commit` flag.
For example:

```bash
uv run devkit workflow envelope commit --unit specs/2026-10/20261030-example --file envelopes/final-report-01.yaml
```

1. Resolve a Unit inside the current Git worktree with a tracked, bound anchor and an initial commit. Require an
   attached branch and no merge, rebase, cherry-pick, revert, unmerged index or existing index lock. Refuse an
   externally supplied alternate Git index. Validate repository identity and prerequisites before staging anything.
2. Resolve the literal file inside that Unit's real `envelopes/` directory. Refuse path escapes, symlinks, ignored
   files and filenames that do not match the envelope contract. Parse it with existing envelope/reference checks.
   Require nonempty summary and stage, a stage declared by the workflow, and current workflow/segment identity.
   These conditions exclude unchanged skeletons without adding a persisted authoring-provenance format.
   Completed, failed and needs-input records are eligible when otherwise valid; recording is not a pass.
3. Derive a safe slug from the tracked anchor's `SPEC-<slug>` or `PROP-<slug>` ID, never the branch name. Missing or
   unsupported IDs receive an actionable refusal; custom workflows can still author and commit records manually.
   Fix the subject template as `chore(workflow): record <slug> <kind>-<NN>` and put the workflow ID, segment and stage
   in the body. Record identity keeps the subject shorter than including the stage too. No truncation or repository
   message-policy bypass is added; a rejecting message hook returns its existing failure for manual handling.
4. Check that every Git-visible dirty path is the selected envelope. Other staged, unstaged or untracked changes
   cause refusal. For a new envelope, accept either an untracked file or an index addition whose bytes equal the
   file. Reject partial staging. For an unchanged tracked file, return `already_committed` only when HEAD contains
   exactly those bytes and the checkout is otherwise clean; do not claim this command created its containing commit.
5. Stage only that literal file and invoke ordinary `git commit` with an argument vector and the generated message.
   Keep normal hooks, identity and configured signing. Git owns its normal index locking; require one active writer
   per worktree and recheck HEAD and selected bytes immediately before mutation. No global lock service is added.
6. Observe HEAD after hooks. A successful result requires one new commit parented by the captured HEAD, exactly the
   selected added path with the expected blob, and a clean index/worktree. Permit hooks that rewrite commit metadata.
   Unexpected content/ref movement or remaining changes is a partial result requiring inspection, never an automatic
   reset, amend or retry. Preserve every observed file and ref on failure.
7. Keep authored record bytes, sequence and `diff_scope` unchanged. If no commit was created, retry this exact command
   only after the reported cause is fixed. When the result is uncertain, inspect HEAD/index/worktree first. A refusal
   or unavailable host permission stops that operation; it never changes tools or skips hooks to continue.

### Result and error contract

Text success is one `[ENVELOPE_COMMIT: unit=... file=... outcome=committed|already_committed head=...]` line.
JSON success is one object with `unit`, `file`, `outcome`, `head`, `subject` and `notices`; `subject` is the generated
message subject for a new commit and null for `already_committed`, which makes no claim about the existing message.
Failures use Agent Advisory Protocol blocks and stable codes, with exact file and recovery command targets.

- `ENVELOPE_COMMIT_INVALID` (exit 2): unsupported Unit/file, invalid or skeleton record, modified history or partial
  staging. No staging or commit occurs.
- `ENVELOPE_COMMIT_STATE` (exit 2): non-Git/detached/in-progress repository, conflicting index environment, unrelated
  changes or changed preconditions. No staging or commit occurs.
- `ENVELOPE_COMMIT_FAILED` (exit 2): commit execution, hooks or signing failed. Report whether staging occurred,
  before/after HEAD and the retained path. No successful commit is claimed from the process exit status alone.
- `ENVELOPE_COMMIT_UNCERTAIN` (exit 2): postconditions fail or the resulting commit cannot be established. Name the
  observed refs/paths and an inspection action; do not suggest blindly rerunning authoring or committing again.

Diagnostic logs stay on stderr through the existing CLI boundary. Exact underlying hook/Git diagnostics remain
available without claiming that their messages are stable codes. An unchanged already-committed record returns 0.
The `next`, `check` and `show` commands stay read-only. No new gate, stage pass, push or merge authority is inferred.

### Call sites, architecture and delivery

Use the command after final-report authoring when it is the only pending file, and after review/reverify authoring
when it is the only pending file. Cover both feature and bugfix workflow references. Feedback with no findings is
eligible under the same condition. A Planning return normally writes feedback plus worker envelopes together, so
it retains a combined manual commit. Source fixes, Living Spec changes, emergency commits and acceptance transactions
retain their existing procedures. A schema check cannot prove these semantic boundaries; caller guidance and review
must keep a record with changes the workflow requires it to accompany.

Add a typed `BaseUseCase.execute` operation under `devkit_agt.features.workflow.usecases`, Git I/O under that feature's
repositories, and message/eligibility policy in its services. CLI handles arguments and result rendering only.
Reuse foundation Git execution and existing envelope parsing; add no dependency from agt to devkit-spec.
Only source assets under the spec bundle change; deployment outputs follow normal sync during Development.
`CAP-DLV-workflow-envelopes`, `CAP-DLV-cli-and-output`, `CAP-DLV-delivery-workflows` and affected delivery use cases
receive the retained contract. The `docs/decisions/` boundary permits promotion of the new PADR, not edits to existing
accepted decisions. Gate, worktree and integration engines remain outside implementation scope.

### Expected acceptance checks

- **AC1 — Deterministic identity:** The same anchor slug, workflow, segment, stage and record identity yield the same
  message on differently named branches. Different Unit slugs remain distinguishable; unsupported anchor IDs refuse.
- **AC2 — Exact scope:** A new valid envelope creates one commit adding exactly that file. Unrelated staged,
  unstaged/untracked content, partial staging, path escapes, symlinks, ignored files and modified historical envelopes
  refuse before mutation. A valid failed or needs-input record commits without satisfying a pass or approval gate.
- **AC3 — Recovery and hooks:** A rejecting pre-commit or commit-msg hook and signing failure preserve the existing
  record and report retained index state. Retry commits that same file without duplication. Repeating after success
  returns already_committed. A hook rewriting metadata reports actual final HEAD; hook content changes, unexpected
  HEAD movement and interrupted/unknown outcomes do not claim success or reset state.
- **AC4 — Compatibility:** Existing authoring remains write-only, including outside Git. Skeleton and invalid current
  workflow/segment records refuse automatic commit. Read-only commands do not commit. Test result rendering and
  actionable refusals for non-Git, detached and in-progress repositories and a supplied alternate index.
- **AC5 — Workflow continuity:** Exercise final-report and review/reverify paths through normal workflow readiness
  checks with their evidence SHAs unchanged. Prepare integration only after record commit; verify a changed HEAD
  invalidates any older preparation. Retain a combined manual commit for accompanying source/document changes and
  multi-record Planning returns. Validate both feature and bugfix source guidance and sync projections.

Runtime acceptance needs new unit and integration tests under the declared workflow test paths. Bundle guidance
checks live under the declared spec-bundle integration tests. Run lint, type checks and `just test-affected` in
Development; Planning checks document rules, links, envelopes and the affected existing tests only.

### Non-goals

**Scope Excluded:** LLM-generated source commit messages, automatic commits for all file-writing commands,
decision/acceptance transactions, automatic production changes, hook bypass, new approval policy, push or merge
automation, changes to the existing integration template, and a persistent Git service or general recovery framework.

## 4. Lifecycle & Retirement Criteria

Planning selects the explicit single-envelope commit command in PADR-explicit-envelope-commits. Size remains M,
with medium Development effort for Git failure behavior and cross-package agent guidance. The independent challenger
review, its disposition and the current run records accompany the direction-acceptance request. No production code,
direction acceptance or Development handoff occurs in this Planning run.

On acceptance, hand off to one feature spec with the selected interface and eligible call sites. Completion requires
the acceptance checks and delivery-contract reconciliation. On rejection, retain `status: rejected` and the user's
reason through the existing proposal retirement procedure.
