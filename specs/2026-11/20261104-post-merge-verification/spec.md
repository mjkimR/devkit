---
id: SPEC-post-merge-verification
title: Verify integration after merging with the resulting runtime
summary: Verify the landed result with its declared devkit runtime after branch checks, and simplify integration preparation, recovery and CLI usage.
status: in-progress
created: 2026-11-04
related_capabilities: [CAP-INT-mcp-services, CAP-DLV-delivery-workflows, CAP-DLV-proposal-planning]
related_usecases: [UC-drive-development-to-integration, UC-plan-and-hand-off-a-proposal]
workflow: sdd-spec-feature
---

# [SPEC-post-merge-verification] Verify integration after merging with the resulting runtime

## 1. Problem Statement & Motivation

Handed off from proposal PROP-post-merge-verification on 2026-11-04.
- **Preserved Materials**: `docs/materials/2026-11/20261104-post-merge-verification`
- Target Docs Blueprint: `PROP-post-merge-verification-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Integration evaluates source rules and workflow content with the target checkout's installed devkit. A branch can
pass its own checks but fail integration because that runtime lacks its CLI, rule imports or receipt reader.
This affects devkit self-development and client upgrades. Ordinary client feature work usually uses the same
runtime on both branches; retaining the target version supplies no distinct compatibility benefit in that case.

The selected direction is branch verification, Git integration, then final verification with the landed content's
runtime. A failing final check leaves the work unfinished and is repaired on the target. A temporarily failing
target is an accepted operational trade-off. Its frequency has not been measured.

This is one lifecycle change delivered by one spec, including CLI simplification, failure recovery and guidance.
The local base at Planning start is `main` at `675f31df`; this proposal has no prerequisites.

## 2. User Stories

- **US-1**: As a Host, I want approved Git effects to land without interpreting source content through an older runtime, so upgrades can be verified with their declared runtime.
- **US-2**: As a user, I want delivery completion to identify passing final checks and the checked landed HEAD, so a successful merge cannot hide an unfinished verification or handoff.

## 3. Non-Goals

1. **Scope Excluded**: No test runner, runtime installer, verification ledger, automatic rollback, merge replay, new feature dependency, CI/release redesign or unrelated worktree finish redesign.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Landed runtime and completion
- **Given** a passing source branch with unchanged tool dependencies.
- **When** the Host integrates it and synchronizes the landed environment.
- **Then** final required checks run in fresh processes and the completion report names their commands, outcomes and checked target HEAD.

### [AC-02] Consumer upgrades and dogfood
- **Given** passing source content whose CLI, rule imports or receipt schema the target runtime cannot interpret.
- **When** Git approval conditions hold and integration runs.
- **Then** integration invokes no content readiness, rule runtime, receipt validation or content finish guards; final checks use the landed runtime.

### [AC-03] Failure after landing
- **Given** a confirmed merge followed by a failing final check.
- **When** the Host recovers within the agreed scope.
- **Then** delivery stays unfinished until target repair and recheck pass, preserving landed history without automatic rollback or merge replay.

### [AC-04] Environment failure
- **Given** setup or tool imports fail after landing.
- **When** final verification cannot run.
- **Then** the Host reports unfinished verification, repairs setup or tooling and reruns required checks; missing checks never count as passed or skipped successes.

### [AC-05] Git authority and concurrency
- **Given** stale source or digest, disallowed route, dirty target, revoked authority or an unknown PR outcome.
- **When** integration attempts further effects.
- **Then** retained Git and approval protections refuse unsafe effects; unknown PR landing preserves recovery state without another merge request or cleanup.

### [AC-06] Reduced CLI
- **Given** an explicit source branch and optional route and digest.
- **When** prepare or integrate runs without task metadata or provider configuration.
- **Then** the command is accepted; removed task-kind, task-id, unit and claims options produce argument errors, PR text derives from the branch, and unknown integration configuration keys produce actionable diagnostics.

### [AC-07] Acceptance and fresh handoff
- **Given** a proposal whose direction conditions and explicit acceptance authority hold.
- **When** accept_and_handoff merges its acceptance.
- **Then** acceptance records remain validated, verification is pending, handoff is not started, requested mode and authorized scope and effort remain in its continuation, and no old-process handoff evaluator runs after landing.

### [AC-08] Batches and generated changes
- **Given** several landed units and generated-file or repair commits.
- **When** the Host runs final verification.
- **Then** affected tests use the saved premerge target SHA against the final HEAD with full fallback and required frontend checks; all units remain pending until that head passes.

### [AC-09] Cleanup and honest effects
- **Given** confirmed, partial or unknown Git effects.
- **When** integration returns JSON or text.
- **Then** confirmed landing reports verification=pending and its actual revision; unperformed or unknown landing reports verification=not_started, scoped cleanup retains identity checks, and partial failure preserves exact effects and exit semantics.

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1 — Verification owner:** The Host runs existing project commands after landing. Devkit adds no test runner,
  runtime installer, verification database or pass-token protocol.
- **Q2 — Runtime:** Use the landed dependency declaration and existing project setup command in a fresh process.
  Client repos install their locked tool packages; devkit self-development uses its landed workspace packages.
  The old integration process never reloads Python modules or validates new CLI content after moving the target.
- **Q3 — Cleanup:** Keep the existing scoped cleanup within integration. A merged commit survives branch/worktree
  deletion, and repair occurs on the target. Deferring cleanup would add a phase without supplying code needed for
  final checks. Keep the worktree only when an existing safety condition refuses cleanup.
- **Q4 — CLI:** Remove merge-time readiness-provider inputs and checks. Keep explicit approval preparation, Git
  identities, route controls and honest partial-effect results. Proposal acceptance remains a separate operation.

Scout evidence and compared alternatives are in `docs/materials/2026-11/20261104-post-merge-verification/integration-options.md`.

### 3. Proposed Design & Impact

#### 3.1 Selected procedure

1. The Host verifies the source branch with its own runtime: project tests, lint/types as required, rules, review
   and SDD completion checks. Existing checks and unresolved-question/problem handling still apply here.
2. Under `ask`, prepare and approve the concrete Git effects. Under `auto`, execute under the retained base policy.
   Integration checks Git identity, clean/locked worktree conditions, conflicts and merge/PR authority.
3. Merge and perform the existing authorized cleanup. The result reports the actual landed revision and completed
   effects, with final verification explicitly pending. An exit zero proves these effects only.
4. The Host synchronizes the target environment from its landed dependency declarations and starts fresh commands.
   Synchronize deployed bundles when required, regenerate stale tracked artifacts, and commit those changes.
5. Run required final project checks on the resulting target HEAD. Record that HEAD, commands and outcomes in the
   final report. Any repair or generated-file commit precedes the checks that cover it.
6. Only a passing final verification permits a successful delivery-completion report. On failure, repair within
   the agreed task and recheck. A revert is a deliberate recovery choice subject to existing authority, never an
   automatic rollback or reset of unrelated commits.

The target checkout must have no unrelated edits before setup or repair. A moved HEAD invalidates a claim that the
current head passed: inspect the additional changes and refresh affected checks before reporting completion.
A missing dependency, setup failure or broken devkit import is unfinished verification, not a passed or skipped test.
Use the repository's direct test commands when the devkit wrapper is itself broken; repair the tool before required
rule/workflow checks can pass. Do not replay a completed merge to retry a final check.

#### 3.2 Verification policy and batching

Use each client repository's required checks; do not prescribe this repository's `just` recipes to clients.
For this repository, record the target SHA before the first merge and run `just test-affected --base <that SHA>` on
the final target, preserving its full fallback and frontend checks. Also run required lint/type checks and final
rules with the synchronized runtime. Run generated-artifact checks and commit needed regeneration before testing.
Never compare `main` to itself with the selector's default base after merging.

For a local-orchestrated batch, final verification may run once after all selected merges and in-scope repairs.
Record the batch-start target SHA. Every landed unit remains pending final verification until the combined head
passes. A failure is repaired and rechecked; recording feedback alone does not complete the batch. Nightly CI stays
as the full-suite backstop, not a substitute for these final checks.

For a PR, retain required platform checks/reviews and confirm the actual landing before cleanup or final checks.
Synchronize the local target to the observed landed commit under the existing route's authority. Check that commit
or a clearly reported descendant including subsequent changes. Unknown merge outcomes preserve recovery state and
never trigger another merge request or cleanup. No force push, admin bypass or implicit publication is introduced.

#### 3.3 CLI and implementation simplification

Proposed public invocation (normative target, not available in the existing CLI):

```text
uv run devkit integration prepare <branch> [--route local|pull-request]
uv run devkit integration integrate <branch> [--route local|pull-request] [--expected-digest <digest>]
```

Keep workspace, output and verbosity options. Keep the digest required under `ask` and optional under `auto`.
Remove `--task-kind`, `--task-id`, `--unit` and `--claims` from these two commands. They currently feed readiness;
they must not be replaced by heuristic inference or hidden session claims. PR creation bodies and merge messages
use deterministic text derived directly from the explicit source branch. Test both publication calls without task
metadata. Update callers and help together.

Remove merge-time readiness-provider discovery, evidence comparison, source snapshot evaluation and mandatory
`[integration] provider` selection from the integration path. Existing `provider` configuration may remain as an
ignored legacy value with documented migration; unknown integration keys must retain actionable diagnostics.
Retain any internal types needed by proposal acceptance instead of mechanically deleting all provider code.

Defer rule/CLI compatibility, receipt/schema consistency and content finish guards to branch/final verification.
This includes guards that parse source workflow envelopes with the target runtime; leaving those before merge
would retain the same incompatibility through another call path. The Host still checks source workflow holds before
approval, using that source runtime. Existing unrelated `worktree finish --merge` behavior is outside the redesign.

Keep the common merge/policy/identity/concurrency primitives, PR confirmation and scoped cleanup. The merge digest
binds Git effects and retained approval policy; it no longer binds content-readiness evidence. Policy changes must
not grant their own merge authority. Preserve source-tip pinning and the existing allowed target-advance semantics.
Keep generated-conflict seeding where the installed registry understands it; an unknown artifact receives ordinary
Git conflict handling rather than a speculative runtime build. Full receipt validation follows synchronization.

Proposal `accept` retains direction eligibility, decision recording, report identity and its explicit authority.
Decouple its acceptance-specific preview from generic integration readiness. Its resulting merge also receives
Host-led final checks. No proposal-acceptance gate is silently dropped to simplify the merge CLI.

For `accept_and_handoff`, acceptance and merge return with final verification pending; no handoff evaluator runs
in that process after landing. The result retains requested mode, authorized handoff scope, selected effort and
an actionable continuation: synchronize/check the landed head, then use the existing handoff command in a fresh
process. Report acceptance and merge as completed effects and handoff as not started. The Host reuses existing
handoff authority for unchanged scope; changed content/effects require the existing scope revalidation. Do not
label handoff completed or emit its worktree/commit fields before it occurs. `accept_only` ends after acceptance
and its final verification. Add a fixture proving no old-process handoff evaluation after landing.

#### 3.4 Result and recovery contract

The CLI returns stable machine-readable Git-effect state and the actual landed revision. Add an explicit
`verification: pending` result field on known successful landings; an unknown/unperformed landing has
`verification: not_started`. The Host's later report owns passed/failed final verification; the merge CLI does not
persist or infer it. Existing `status: completed` means the requested Git/cleanup effects completed, not that final
project checks passed. Text output includes the same verification field.

Retain exit `2` before any effect when the operation cannot run and exit `1` for an error after partial effects.
Retain warning/strict behavior and exact completed-effect reporting. A partial cleanup result names remaining
cleanup without asking to remerge. Final-check failures are reported by the actual check command and the Host.
Cleanup may complete before a failing final check; the report must say both facts explicitly.

#### 3.6 Boundaries and verification

Development changes the integration/worktree paths needed for this lifecycle, their tests, devkit-spec delivery
and agent assets, package entry-point declarations, integration configuration and the Living Spec targets. The broad
package boundaries are inventory limits; tasks must name narrower file scopes. No new feature dependency edge,
package, test tier, scheduler, runtime installer, persistent verification ledger or unrelated CLI cleanup is proposed.
Publication/release gates remain unchanged. No automatic reset or rollback is added.

Verify with meaningful CLI and integration fixtures for old/new runtimes, local/PR outcomes, proposal acceptance,
cleanup and source holds; use command spies to prove integration does not execute removed content checks. Exercise
final-check failure and recovery in temporary Git repositories. Validate the Host-led sequence by guidance tests
and a recorded end-to-end walkthrough; do not claim the CLI enforces external test completion. Run lint, types,
`just test-affected --base <base>` and rules on the implementation. No performance or failure-rate claim is made.

### 4. Lifecycle & Retirement Criteria

`ADR-post-merge-verification` partially supersedes integration/content-readiness and deferred-final-testing clauses
of the named ADRs. It preserves approval authority, Git identities, publication limits and partial-effect recovery.
Planning acceptance authorizes the detailed direction and CLI removals. Development effort is high because the
public command and integration contracts change. Handoff produces one implementation spec; completion requires
implementation, review, Living Spec reconciliation and final verification evidence.


## 6. Development assumptions and baseline

The accepted input is `810adf730993710119ab351b4bbbdce7d716ad98`; inspecting its integration path confirms the Planning premise: preparation and landing call readiness providers, rule/receipt checks and content finish guards. No scope-breaking base change was found. Measure direct content-check call sites in the accepted input and implementation without checking out the base; regression spies verify the after behavior. The expected after count is zero. The Host owns external final test execution, not the merge CLI.
