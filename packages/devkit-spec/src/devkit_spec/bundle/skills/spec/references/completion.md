# Common Completion and Knowledge Classification

Read this when approaching review or completion, and before any gate or Git action.

Every task MUST compare the final diff, the requirements, the check results and the Living Spec impact before reporting completion. Before reporting completion or integration, classify the Living Spec impact: authorized contract changes go to capabilities/stories, structural changes to architecture, architecture decisions and lasting policy changes that override a MUST to ADRs, existing policy changes to rules/playbooks. New general rules and reusable procedures are optional promotions: draft first and request only decisions beyond existing authorization. A no-impact change needs a reason, not a new document.

## Policy

Read `devkit spec policy` before deciding gate or Git actions:

- `[GATE_POLICY: dev-integration policy=ask]`: present the verified result, then obtain the user's OK:
  - Local MCP integration: call `integration_integrate` directly. Its native confirmation, bound to the verified source commit, the confirmation target and (within that call) its descendants, and the merge/cleanup scope, is the user's OK for this gate: ask no separate chat approval and do not require `integration_prepare` first. A waiting `gate:dev-integration` permits this call; do not assert `--given dev-integration` before native acceptance.
  - CLI fallback: a conversational OK unless already authorized. A PR: its ready state, to which a runner binds the gate.
  - The OK is never written to a file (`ADR-integration-approval-asserted`): for a spec bundle pass `--given dev-integration` to each `devkit workflow next --unit <dir>` after it, and name the OK (`mcp-elicitation` when confirmed through `integration_integrate`) as the authority in the integration report.
  - An objection takes the stage's return path (`devkit workflow return --unit <dir> --to review-refine --note "..."`); an objection about direction is a close ([classification](classification.md) §4).
- `policy=auto`: once review, reconciliation and required checks pass, at every effort, the policy delegates the gate: `devkit workflow next` lists `[GATE_PASSED: dev-integration ... source=policy]` (JSON `passed_gates`), the basis the integration report cites. Never describe policy delegation as a human approval or review.
- Neither value grants commit, publication, merge or deletion authority; explicit user instructions and platform protections still apply.
- `GIT_POLICY` (worktree, pull request and branch cleanup): read [git policy](git-policy.md) and decide before the first edit.

## Reconciliation record

Create the spec's `reconcile.md` by PR preparation with `reconcile_id`, `status: pending|resolved`, and `targets` (`file`, `resolution: modified|waived`, `rationale` for a waiver). Set resolved only after every target is reflected in the comparison diff or has a waiver of at least 20 non-whitespace Unicode characters; required contract mismatches cannot be waived. Empty targets need no-impact reasoning in the body. Keep resolved records in place after integration and mark the spec completed.

## Checks and commits

`git commit` runs the commit gate on the index (`devkit rules check --staged` reproduces it); `devkit rules check --ci --base <ref>` checks merge-base through HEAD (default `origin/main`). The rules check structure and form, and require each `modified` target of a resolved record to be changed on the branch; they do not prove semantic impact. The commit gate counts the staged diff together with the branch's earlier commits since its merge base, so a target an earlier commit changed (the ADR the handoff promoted) needs no second edit.

Intermediate commits pass the same gate; a `pending` reconcile record is allowed while the spec is not `completed`. An intermediate commit grants no merge authority and is never final completion evidence: the final cumulative check runs on the integrated head, and `dev-integration` still requires the Living Spec reflection and the resolved and completed states.

Before the native approval, prepare the task branch against the base, re-verify changed paths and run the cumulative check; this changes no base ref and cleans nothing up. After `dev-integration`, the `integrate` stage (`spec-integrate`) integrates the base branch, re-verifies only what conflict resolution changed, confirms the reconcile record and runs the cumulative check; it does not restart code review and adds no workflow gate. Delegated support roles return the fields in [envelope](envelope.md) and never change the index or HEAD.

Reconcile verification is a `reconcile-check` envelope at `living-spec-draft` at every effort ([effort](effort.md), [review loop](review-loop.md)), naming who verified, the evidence and any omission reason; fix findings and write a new check. Recheck impact after review fixes or changed inputs; return `reconcile.md` to pending for new targets. Review final docs and governance changes too. Never automatically delete a dirty worktree. Implementation complete, committed, integrated and session ended are distinct facts.

`session` depth (session: no records) still runs the checks and the effort's review. Its commit is a plain `git commit` before `dev-integration` (the approval covers committed work; a PR is pushed then), without `spec-integrate`, except on the base branch with no PR under `dev-integration = ask`: there start `dev-<slug>`, or get the approval before committing ([git policy](git-policy.md)). Work the user's authorized scope; do not silently abandon remaining work for a session time limit.

## Source feedback resolution

Only `open` feedback is actionable. `promoted` is terminal once handed to identified follow-up work; progress
belongs to that destination, and finishing it MUST NOT convert the source to `resolved`. `resolved` is terminal
for a directly addressed and verified observation without promotion, in either a session or a spec task.
Terminal source references remain traceability: they require no completion disposition, re-verification or edits.

Before reporting completion, review only explicitly linked open sources addressed directly by the task against
the final diff and verification. For a spec, record their outcomes in `reconcile.md` at `living-spec-draft`; for a
session, do this at `report-session` before its commit and report outcomes without creating a new artifact.
This obligation applies even with requested-only capture or `collect-feedback` off.

- Change an open direct-fix source to `resolved` only when the authorized implementation fully addresses it and
  applicable tests/review verify the result. Append a Disposition naming the SPEC ID (or changed session paths),
  implemented outcome and concrete verification evidence. Unrelated feedback found by a sweep is not authorized.
- Partial, deferred or unverified direct fixes stay open; report remaining scope and destination. Required work
  still in the agreed scope cannot be deferred to claim completion.
- Handoff, planning, document checks or integration alone are not fix verification. A branch resolution does not
  assert integration; the implementation and FB update reach the base through normal integration.
- Recheck only resolutions made by this task if later changes invalidate their evidence; restore those sources to
  open and explain remaining work before completion. Do not revisit pre-existing terminal sources.
- Capture never changes status. A separate hygiene session is not needed for an authorized direct fix. Only open
  sources requiring updates belong in delegated write scope; the Host handles an out-of-boundary disposition.

## Deferred Work Handoff

Before deleting a source proposal or reporting completion, find concrete work its roadmap or the final scope explicitly retains for later. Each such follow-up MUST be tracked, by default as feedback for Backlog (`/spec-feedback`), or as a draft proposal when concrete enough: link or update a matching open `PROP-...` (`devkit spec search "<topic>" --kind proposal`), else `devkit spec proposal new <slug>`. Record the source, remaining scope, reason for deferral, dependencies or restart conditions, and expected acceptance checks; group work with the same outcome.

Reference the destination `FB-...` or `PROP-...` by full ID from the source `reconcile.md` (or a `session` task's final report), and from a proposal back to the retained source spec or Git history if the original proposal is removed; a future-work paragraph in a capability document is no handoff. Verify the destination exists (`devkit spec list feedback` or `devkit spec list proposal`) before claiming it is tracked. Drafting a follow-up neither accepts it nor authorizes implementation.

Required acceptance criteria or defects still in the agreed scope MUST remain open; never move them to a proposal to claim completion. The handoff is part of completion in every route.

Native MCP approval belongs to the Host after it validates worker boundaries, committed scope and required checks.
Workers return that evidence and do not ask for business approval. When the optional runtime, connection or negotiated
form UI is unavailable, use intentional installation/connection or an independently authorized explicit CLI/PR route;
missing UI is not approval. Cloud execution exposes read-only inspection and cannot use interactive or resume tools.
The owning configuration workspace controls this restriction, independently of source-branch provenance.
