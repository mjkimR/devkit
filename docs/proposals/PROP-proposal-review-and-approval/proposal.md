---
id: PROP-proposal-review-and-approval
title: Proposal review reports and unified plan-accept MCP approval
summary: "Generate PADR-focused proposal review reports in the shared workspace and provide a native MCP plan-accept confirmation that links the report and selects accept-only or combined handoff."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-20
target_area: capabilities/delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-autonomous-backlog-and-orchestration
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/
    - packages/devkit-viewer/src/devkit_viewer/
    - docs/capabilities/delivery/
    - docs/capabilities/viewer/
    - docs/development/reference/
    - packages/devkit-spec/tests/
    - packages/devkit-viewer/tests/
    - packages/devkit-viewer/frontend/
    - packages/devkit/src/devkit/integration/
    - packages/devkit/tests/integration/
    - docs/capabilities/integration/
    - docs/capabilities/harness/
    - docs/decisions/
  excludes:
    - packages/devkit-dist/src/devkit/distribution/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-proposal-review-and-approval] Proposal review reports and unified plan-accept MCP approval

## 1. Background & Hypothesis

Parallel Planning results need a durable, concise briefing outside the Host conversation. A user should review
PADR choices in the configured language and explicitly choose acceptance with immediate Development or acceptance
alone. The report supplies evidence, never approval. The selected design is recorded in
`PADR-source-bound-review-reports-and-explicit-lifecycle-approval`.

## 2. Technical Spike Conclusions

- Existing `handoff_mcp.py` validates an accepted committed proposal on a clean retained base, snapshots policy,
  requests a native form and rechecks the preview before effects. Preserve those guards and reuse its domain logic.
- Integration already owns readiness, Git identities, policy and scoped cleanup. A combined operation needs an
  internal composition seam, not a forged affirmative callback or caller-supplied approval token. No second dialog
  follows an affirmative combined form; no separate tool can inherit that approval.
- `CAP-VIEW-repository-viewer` and `ADR-read-only-local-server-over-git-refs` currently exclude ignored files.
  Report reading therefore requires a narrow ADR supersession at handoff; ordinary Git endpoints stay unchanged.
- `ADR-shared-language-preference-with-bounded-approval-content` resolves form language once, preserves machine
  values and source quotations, and does not promise control of host chrome or automatic source translation.
- `PROP-worker-shared-state-mcp` is an unaccepted Planning dependency, not an implemented API. The Host-supplied
  interface snapshot is a provisional integration contract; Development waits for its acceptance and implemented
  adapter, or returns for scope clarification if that contract changes.

## 3. Selected Design & Impact

### Report producer and immutable identity

The Host produces the report after validating the final committed Planning worker range, including final envelopes.
It reads `proposal.md`, every current PADR, relevant support/reverify envelopes and scope from that exact commit.
A domain-owned report template contains: title and one-line outcome; source SHA and language; each PADR's problem,
choice, rejected alternatives and consequences; boundary impacts; applied Planning efforts and support coverage;
open decisions, waived findings and unverified areas; recommended `dev_effort`; proposed approval effects.
Previously approved decisions remain identified; changed/new PADRs receive emphasis without hiding other decisions.
The agent authors the semantic briefing in `ko` or `en`; the library validates structure/identity, not semantic
truth. No LLM dependency or translation service is added. Source citations retain IDs and exact evidence text.
The Host compares the briefing against all source decisions before publication. Missing mandatory sections or an
unaccounted PADR refuses publication. Report content cannot override workflow readiness or grant approval.

Add domain CLI `devkit spec proposal report <slug> --source-sha <sha> --body-file <path-or-dash>` and MCP
`spec_proposal_report` with `slug`, `source_sha`, `body`. Language is resolved from the owning workspace, never
caller authority; `auto` maps to English for deterministic approval content. The consumer verifies that the source
is a real full Git commit (40 or 64 hexadecimal characters), is the current clean Planning branch HEAD for
plan-accept, or the accepted base HEAD for standalone handoff, and contains the expected proposal and its records.
It publishes through the dist-owned `SharedArtifactAdapter` (`put/get/list/sweep`) using
`repo/kind=proposal-review/slug/source_sha/language/content_sha256`. Results contain the exact immutable URI,
server `generation_id`, content digest, source SHA, language, created/expiry timestamps and optional viewer URL.
Local MCP uses the same domain service and adapter as CLI; no filesystem path is an artifact identity.

Storage is the shared dependency's readable Markdown envelope, at most 1 MiB including metadata, with fixed 7-day
TTL. Identical live retries retain metadata; expired content creates a new generation and never revives the old URI.
The report consumer uses exact URI `get`, not implicit latest or directory scanning. Before showing a form and again
after reply, validate repository, kind, slug, real source SHA, language, digest and expiry against the request.
Changed source/language, missing or expired content refuses approval and returns `PROPOSAL_REVIEW_REFRESH_REQUIRED`
with an action to regenerate and request a fresh form. Do not regenerate during a pending form or transfer its reply.
Read/list/view never publish, extend expiry, clean up or grant authority. Publication leaves tracked files clean.

### Native approval and effect scope

Add `spec_plan_accept(slug, report_uri)` on the retained local MCP service. The tool prepares a request binding the
reviewed Planning SHA, base SHA, Git identities, effective policy, exact report URI/digest/language, proposal slug,
cleanup targets, merge route and configured setup command. Its message includes title, one-line summary, PADR IDs,
Planning effort/support gaps, `dev_effort`, report link, and all effects below even if form schema labels are hidden.
The form requires `approve=true`, `mode=accept_and_handoff|accept_only` (default combined), and
`activity_effort=low|medium|high` defaulted from `dev_effort` (ignored for accept-only). Only native action `accept`
and valid values authorize the selected effects. A declined, cancelled, disconnected or unavailable form leaves
proposal status, gates, Git, worktrees and report untouched. Hold is not rejection; explicit proposal rejection
continues through its own existing workflow. Unanswered worker questions or unresolved problems refuse preparation.

This first delivery combines only the local merge route. Required-PR policy returns a deterministic refusal and
points to the existing separately approved PR flow; no downgrade, push or remote authority is inferred. Cloud
continues existing explicit conversation/CLI approval paths and does not invoke native forms.

Effects are a sequence, not a transaction:

1. Recheck exact source/base, report, environment, policy and clean worktrees after confirmation. Any change means
   `PROPOSAL_APPROVAL_STALE` and zero lifecycle mutations. Acquire existing operation locks and recheck at effects.
2. Write proposal acceptance and `plan-accept` user gate, then commit through the normal gate on `plan-<slug>`.
   Only this service-created acceptance descendant is covered; compare the exact expected acceptance/gate delta.
   Any other source change stops. Failure preserves dirty or committed state and reports it; never force commit.
3. Integrate that committed acceptance result with existing integration readiness, checks and cleanup guards.
   A changed base before merge stops for fresh approval; this combined flow deliberately has no moving-target
   allowance. No skip flags, direct merge bypass, or substituted generic confirmation callbacks are introduced.
4. For `accept_only`, stop with accepted proposal on base. For combined mode, pin the verified landed base and
   start `dev-<slug>` at that revision, run configured setup and handoff, then scope registration. Report the selected
   effort as run input. Setup/sync notices requiring recovery stop before handoff as the current service does.
5. Cleanup only explicitly disclosed Planning worktree/local branch according to existing policy and safety guards.
   Failed handoff preserves created Development worktree and accepted base; no rollback or deletion of user content.

Internal typed composition binds permitted actions to one service invocation, with process-local progress and guards
before each effect. It is not a public approval credential. No approval survives restart or a partial return.
Result fields include `status` (`accepted`, `handed_off`, `held`, `blocked`, `needs_recovery`), completed step names,
observed source/acceptance/landed SHAs, worktree paths, errors/notices and deterministic next action. On partial
return, a fresh call inspects actual state and asks only for remaining effects, displaying completed effects.
Never replay acceptance commits, create a second dev branch or treat branch existence as completed handoff.
An existing dev worktree is validated with its unit and recorded provenance before offering recovery; mismatch
refuses. A crash requires independent Git/worktree inspection and fresh approval, not reconstructed authority.

Standalone `spec_handoff` remains for already accepted proposals. It accepts an exact report URI and validates
against current accepted base HEAD; stale/expired/missing reports request explicit Host regeneration before the form.
Its concise message replaces raw proposal dumping, while retaining all setup/worktree effects and selected effort.
Acceptance by Backlog does not skip report or explicit Development approval.

### Read-only review and interactive refinement

Add an optional exact-artifact route to the running local viewer, using only its registered repository's configured
local shared adapter. A URL such as `/review/<repo-id>/<generation-id>` binds an immutable record; the backend
resolves only that registered repository and exact generation, verifies `kind=proposal-review`, and calls read-only
`get`. It accepts no disk path, adapter name, remote URL, Git revision expression or sweep action from HTTP input.
Missing/expired records return a stable unavailable page with refresh instructions for the Host; the viewer never
regenerates them. Retain loopback binding, Host checks, no CORS and GET-only behavior. Render Markdown with existing
sanitization, no executable source content. The report displays source SHA, language and expiry prominently and is
not an assertion that the branch remains current. Remote adapters and generic shared-store browsing are excluded.
No automatic viewer launch or daemon is added. When no viewer runs, return the exact artifact URI for Host retrieval
and a readable Markdown presentation; host-specific clickable URI support remains explicitly unverified.

A dedicated `spec-review-proposal` skill supports Q&A from the exact proposal/PADRs and report. It obtains the Host's
exclusive Planning worktree ownership before edits; no competing worker writes. Requested design changes are
committed through Planning, reviewed at the activity effort, and produce a new source-bound report. Accepted plans
are not silently edited or reverted to reviewing; a direction change goes through the existing follow-up workflow.
Local orchestration checks that devkit MCP and required report/approval tools are connected before using this path;
if absent, request connection and pause dependent operations, with no silent CLI fallback. Cloud uses CLI; full
MCP-invisible cloud rendering belongs to `PROP-cloud-agent-rendering`.

### Boundaries and delivery

`devkit-spec` owns report validation/template, orchestration, forms, guidance and tests. `devkit.integration` owns the
minimal typed in-process composition seam and its guard tests; it imports no SDD models. The optional viewer owns
read-only report routing and page rendering. No SDK or retained registration redesign is needed. The existing
parent directories listed in frontmatter include tests, frontend rebuild artifacts and eventual ADR promotion;
new module filenames will be chosen in Development. Reconcile `CAP-DLV-proposal-incubation`,
`CAP-INT-mcp-services`, `CAP-HARN-agent-guidance`, `CAP-VIEW-repository-viewer` and their quick references.
The viewer exception supersedes only the Git-only read restriction in `ADR-read-only-local-server-over-git-refs`;
its no-write/no-approval and existing Git endpoint contracts remain intact.

## 4. Acceptance Evidence and Non-Goals

- AC1: Publish a complete ko/en briefing from a committed Planning HEAD; verify all PADRs and effort/envelope
  coverage, exact identity and clean tracked state. Reject false SHA, mismatched slug/repo/language, oversized or
  incomplete content. Live retry returns the same generation; expiry requires a different one.
- AC2: Exercise both native form choices. Accept-only records/commits user acceptance and merges without creating
  a dev branch. Combined performs acceptance, checked merge and handoff with one native confirmation, disclosing
  cleanup/setup and returning effort. Decline/cancel/missing form and open worker questions perform no effects.
- AC3: Change source, base, policy, environment or report expiry while the form waits; prove refusal before effects.
  Inject commit, merge, cleanup, setup and handoff failures; results identify exact completed effects and recovery.
  A retry/restart never reuses authority or duplicates acceptance/worktrees. Required-PR refuses local combination.
- AC4: Standalone handoff of a previously accepted proposal uses a fresh report bound to current base and one
  explicit form; stale reports request refresh without implicit writes or raw proposal dumping.
- AC5: Viewer displays exactly one valid report and remains read-only for get/list/expiry, traversal and wrong-repo
  attempts. Keep existing Git endpoints and HTTP protections; sanitize hostile Markdown. Verify no adapter writes.
- AC6: Local orchestration without connected required MCP tools requests connection; cloud CLI remains usable.
  Review guidance preserves single worktree ownership, commits edits and refreshes the source-bound report.

Development effort remains medium: cross-package domain composition requires mandatory initial code review and
independent reconciliation; no external consumer API or irreversible data migration changes are planned. Tests
cover service seams with injected faults and form replies, viewer routes/sanitization and language parity. Run lint,
types, `just test-affected`, governance and viewer lint/check/test/build for changed frontend assets. A live harmless
form/link observation is separate from protocol tests; unobserved host UI fidelity must remain reported.

Non-goals: production remote storage; MCP transport/registration changes; viewer write/chat/LLM endpoints;
translated tracked documents; general Markdown translation; remote PR integration in the combined tool; durable
approval credentials; atomic rollback across Git and setup; removal of standalone handoff; cloud template redesign.

## 5. Lifecycle & Retirement Criteria

Ready for plan-accept after the medium challenger pass and resolution of its findings. Development waits for
`PROP-worker-shared-state-mcp` implementation; the report uses its local adapter and public protocol seam only.
Acceptance of this proposal does not accept that dependency or authorize any merge/handoff now. Its replacement
ADR and capability updates are produced through normal handoff/reconciliation. No business question beyond the
Host's plan-accept remains unless the challenger exposes a decision that cannot be settled within this intent.
