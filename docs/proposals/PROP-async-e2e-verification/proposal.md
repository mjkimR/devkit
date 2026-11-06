---
id: PROP-async-e2e-verification
title: Asynchronous E2E Verification
summary: "Define Host-managed asynchronous E2E for devkit's local-orchestrated development and reusable client verification guidance. Client cloud-pr delivery accepts nightly detection of broken merge combinations without postmerge CI."
status: reviewing
created_at: 2026-11-06
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - scripts/affected_tests.py
    - justfile
    - packages/devkit/src/devkit_agt/features/worktree/
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit/pyproject.toml
    - packages/devkit/README.md
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - .devkit/architecture.toml
    - docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    - docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    - docs/capabilities/harness/
    - docs/capabilities/worktree/
    - docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    - docs/architecture/ARCH-04-2-delivery-policy.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/development/reference/
    - docs/decisions/
    - AGENTS.md
  excludes:
    - packages/devkit-viewer/
    - .github/workflows/
    - .github/scripts/
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-async-e2e-verification] Asynchronous E2E Verification

## 1. Background & Hypothesis

Long E2E runs block local-orchestrated integration. `scripts/affected_tests.py` excludes many E2E paths, but
explicit data mappings, edited E2E tests and its full fallback can still include them. `--e2e` adds E2E rather
than selecting only that tier. Synchronous iteration therefore lacks an explicit non-E2E boundary.

`CAP-DLV-delivery-workflows` section 4.8 and `ADR-post-merge-verification` require landed verification before
completion. The git-operator reports Git effects with verification pending; the Host accepts test results.
The existing `devkit run` captures bounded output synchronously and stops its process group on interruption.
It does not manage detached test runs (`CAP-CMP-bounded-execution`).

The hypothesis is that selective E2E in an isolated fixed-commit environment lets the Host start independent
work before E2E finishes. Batching can reduce repeat runs. Asynchrony alone reduces neither test execution time
nor CPU consumption. `materials/planning-evidence.md` records bounded measurements and their limits.

### 1.1 Separate product delivery from consumer policy

| Concern | devkit repository itself | Client repositories consuming devkit |
| :--- | :--- | :--- |
| Delivery pattern | Local-orchestrated only | Local-base or explicitly selected cloud-pr scenario |
| After local merge | Synchronous unit/integration and required ancillary checks; selective asynchronous E2E | Same local completion model when local-base is selected |
| Cloud PR CI and automatic merge | No cloud-pr adoption or PR CI rollout | Consumer CI and automation own required PR CI, rework, automatic merge and nightly repair dispatch |
| Nightly | Existing full backstop | Consumer-defined cadence; accepted delayed combination-failure detection under cloud policy |
| Assets delivered here | Local execution capability, repository commands and guidance | Reusable guidance and scenario contract; no client CI is configured by this change |

Neither worker location nor the presence of a PR chooses cloud risk acceptance. A local Host integrating via a PR
still follows the local completion contract. Operational modes remain transient under
`ARCH-04-2-delivery-policy`. Consumer verification instructions declare the permitted scenarios; the active
workflow selects one explicitly and reports it. This proposal adds no persistent `cloud-pr` mode setting.

### 1.2 Scope and non-goals

- Include one harness-owned local test-run lifecycle and devkit's tier-aware affected selector.
- Include route-specific delivery guidance and a cloud client risk-acceptance contract.
- Exclude cloud-pr use by devkit itself, CI workflow edits, external autohub implementation and release changes.
- Exclude replacing unit/integration with E2E, a mandatory verifier subagent and git-operator test supervision.
- Exclude a distributed scheduler, environment pool, container platform, Windows background execution and global locks.
- Exclude broad test deletion, fixture optimization and relabelling integration tests as cheap without measurements.
- Exclude test-playbook changes, retained in dependent `PROP-test-playbook-verification-policy`.
- Planning changes only this proposal bundle. Active contracts and production behavior change during Development.

## 2. Planning Decisions and Evidence

| Spike | Settled direction | Evidence or remaining validation |
| :--- | :--- | :--- |
| Q1 Selection | Independent tier and impact scope; conservative fallback stays inside the selected tier | Selector source and existing selector regressions; section 3.1 |
| Q2 Cost | Measure bounded suites now; require same-machine synchronous/async comparison during Development | `materials/planning-evidence.md`; no whole-suite speedup claim |
| Q3 Owner | A reusable `devkit test` lifecycle, with project-owned native commands | `PADR-isolated-test-runs`; scout alternatives |
| Q4 Runtime | Detached POSIX supervisor, persistent evidence, no daemon/reboot guarantee | Process survival probes and failure injection are Development checks |
| Q5 Isolation | Test-only detached checkout, independent dependency environment and run-specific temporary resources | Worktree revision support exists; test-environment allocation is added explicitly |
| Q6 Completion | Coverage uses an explicit baseline and exact tested SHA; outstanding descendants require selection/recheck | Sections 3.3 and 3.5 |
| Q7 Recovery | Distinguish setup, test failure, interruption and unknown; preserve evidence on cleanup | Section 3.4; no automatic retry, replay or rollback |
| Q8 Boundaries | `devkit_agt.features.test_execution` with declared worktree/project dependencies | Section 3.6; no other feature edge is approved |
| Q9 Cloud recovery | Consumer CI events route to its automation owner; autohub is the ecosystem adapter, outside this repo | Section 3.2; no client was supplied to validate activation |
| Q10 Policies | devkit local-only; client selects a documented scenario without changing operational mode config | `PADR-delivery-verification-routes` |

The existing revision-aware worktree preparation is reusable, but its activity-branch semantics are not test-run
identity. Extend worktree ownership for test-only checkout creation/removal instead of creating synthetic SDD
Units. Setup and sync warnings prevent a test run from becoming ready. The background lifecycle does not reuse
the compact runner's interruption ownership or its pruned log store.

No user question remains about the accepted cloud risk. Interface and ownership choices below are the recommended
direction for `plan-accept`, rather than claims about an existing command.

## 3. Proposed Design & Impact

### 3.1 Tier-aware test selection

Add `--tier unit-integration|e2e|all` to `just test-affected`, defaulting to `unit-integration`. Keep `--e2e` as a
compatibility alias for `--tier all`; contradictory combinations fail with an argument code. Impact selection
continues to return `partial`, `full` or `none`. There is no second dependency graph in the background runner.

Apply the tier after expanding broad package/test directories, including explicit data targets and full fallback.
A unit/integration selection cannot pass a parent directory that would collect E2E. Include embedded rule tests
under `src/` in the non-E2E tier. Preserve ancillary lint, types, rules and frontend commands independently.
When a selected tier has no tests, report `none` with a selection reason and do not invoke pytest with no paths.

| Change | Worker/local synchronous run | E2E disposition |
| :--- | :--- | :--- |
| E2E test or its mapped inputs changed | Unit/integration only in this invocation | Run the relevant E2E on the branch when demonstrating the changed behavior; final local selection still applies |
| Product boundary, packaging, hooks or cross-feature behavior | Affected unit/integration | Run selected E2E; uncertain impact expands to all E2E |
| Shared foundation or unmapped input | All unit/integration | All E2E, asynchronously after local merge |
| Only documents or assets with no E2E dependency | Affected unit/integration and required asset checks | Omit with the selector reason |

The E2E-required decision uses the E2E-only selection over the same accumulated change interval. A manual skip
cannot turn a nonempty required selection into success. A required premerge reproduction or acceptance check
runs before merge; ordinary worker iterations need not repeat it. Client PR CI remains its separate required gate.

### 3.2 Client cloud risk acceptance

Both client routes keep worker iterations focused on unit/integration, with E2E when the change needs it.
For an explicitly selected client cloud-pr scenario:

1. Required PR CI includes E2E. A failure or unavailable required check blocks automatic merge.
2. The client's CI observer requests rework against the PR head and includes check URL, tested SHA and failure evidence.
3. Passing required PR CI and confirmed automatic merge complete that PR's work.
4. There is no immediate postmerge CI and no requirement to test the latest base's prospective merge result,
   force a base refresh or introduce a merge queue.
5. Nightly tests detect combination failures later. Main can remain broken until detection and repair.

Consumer verification instructions name the PR check set, automatic-merge owner, nightly workflow/cadence/timezone,
last-success and missed-run visibility, and repair destination. CI completion/failure events feed the consumer's
automation owner; in the documented ecosystem this is autohub. A failed PR produces PR rework; failed nightly
produces follow-up repair against the nightly SHA with logs. Delivery retries deduplicate by run/check identity.
If dispatch fails, the CI/automation record remains visibly undelivered for that owner to recover. No local Host
session is presumed. These are adapter obligations and walkthrough checks, not implemented webhooks in this scope.

No client repository is configured or certified here. A consumer without that wiring can review the scenario,
but cannot claim that automatic rework or repair is active. Devkit's own unchanged nightly schedule is 04:17
Asia/Seoul; it runs full CI when the scheduled head differs from the last successful nightly head. That schedule
is evidence about devkit, not a default silently imposed on clients. PR CI is not currently a devkit trigger.

The intentionally absent merged-result/postmerge checks are not unmet gates under this client policy. A later
nightly failure creates new repair work and does not retroactively make the completed PR a local pending run.
Passing PR CI proves only the revision and scope it actually tested.

### 3.3 Local Host scheduling

After each selected merge or merge batch, synchronize dependencies from landed declarations and use fresh
processes. Check generated assets, regenerate and commit stale artifacts, then run required unit/integration,
lint, types, rules and frontend checks synchronously. Save the premerge target SHA before the first merge.

The Host directly launches required E2E through the test-run CLI. Git-operator continues bounded lifecycle jobs;
a verification subagent is optional for diagnosis, not required for scheduling or process survival.

- Allow one preparing/running E2E run per repository. A second start returns the active run identity; it does not
  create a hidden queue. Reserve the slot atomically for concurrent callers.
- If idle, dispatch required E2E after the synchronous checks for the selected merge batch and before beginning
  the next independent task. A deliberate batch has a fixed selected unit set, not an indefinitely growing queue.
- If busy, accumulate later changes. After collecting the active result, dispatch the accumulated interval before
  another merge. Finish the current run instead of cancelling repeatedly to chase HEAD.
- Check results before every merge, when a tool reports completion and at batch/session completion. The Host
  can continue independent work while a result is pending. There is no continuous observer when the Host is absent.
- On an observed failure, hold new merges, prioritize repair and retain the original failing SHA. Workers can
  continue independent branch work. Repair the current landed state, then recheck the accumulated interval.

Record the batch start, outstanding unit IDs, run IDs, last collected successful coverage and next collection
step in the Host's recoverable batch notes. Run manifests preserve each launched interval. After context loss,
recover from manifests and the actual merge history. If the outstanding interval cannot be established, select
full coverage; never infer a baseline from current main itself.

### 3.4 Minimal local execution lifecycle

`devkit_agt.features.test_execution` owns `devkit test`. Proposed commands, unavailable until Development:

```sh
devkit test start --ref <fixed-sha> --base <baseline-sha> -- just test-affected --tier e2e --base <baseline-sha>
devkit test status [<run-id>]
devkit test logs <run-id> --tail 100
devkit test cancel <run-id>
devkit test clean <run-id>
```

`start` resolves both SHAs before returning, validates their ancestry, persists the request and launches a detached
supervisor. It returns while state is `preparing`; checkout/setup and tests run in the background. The supervisor
owns the captured run definition, not mutable files in main. Project setup comes from the existing worktree setup
configuration, with an explicit per-run `--setup` override. Native test argv follows `--`; devkit does not invent
pytest, uv, just, service provisioning or a second profile configuration system for consumers.

Worktree owns fixed-commit detached test checkout creation and guarded removal. Test checkouts have no SDD Unit,
merge, push or post-finish hooks. Their path is a unique sibling of the retained base; a manifest binds the path
to this run. Setup runs in that checkout and creates its own environment. Scrub inherited `VIRTUAL_ENV` and
project-environment overrides that would redirect dependencies to main; record project setup requirements.
Restore managed assets with locked sync where applicable. Setup/sync failure is `setup_failed`, never a warning
that allows tests to start. Do not copy `.env` or credentials implicitly.

Give each run a private temporary directory and run ID. Resource-dependent commands use disposable data and
isolated services or ephemeral ports. File isolation alone does not isolate an external database or fixed port;
unsupported shared resources prevent that run from being dispatched until the project supplies isolation.

Persist manifests and logs under the repository's common Git directory, outside disposable checkouts. Store
repository identity, run ID, fixed SHA, baseline, argv, setup command, runtime identity, environment path, process
identity, timestamps, phase, terminal outcome, exit code and logs. Writes use atomic replacement. Keep the
captured launcher/runtime usable while main changes; test dependencies come from the fixed checkout. Inspect
and bounded log retrieval work from a later Host process. `status` without an ID lists outstanding and terminal
runs so context loss does not hide results.

| Outcome | Meaning and next action |
| :--- | :--- |
| `preparing` / `running` | Pending; inspect again before a merge or completion |
| `passed` | Actual native command exited zero; apply only to its tested SHA/scope |
| `failed` | Native command ran and failed; hold local merges and repair |
| `setup_failed` | Checkout, runtime, setup or locked sync could not complete; repair prerequisites and start a new run |
| `cancelled` / `interrupted` | No passing evidence; inspect retained logs and decide a new run |
| `unknown` | No terminal record and no positively identified live supervisor; investigate, never infer success |

Support local macOS and Linux initially. The supervisor separates its session, stdin and log descriptors from
the initiating call. Returning from a tool call or losing Host conversation context does not intentionally cancel
it. Host-enforced descendant termination, application exit policies, OS shutdown and machine reboot have no
survival guarantee. Records remain recoverable. Development verifies the supported boundary with separate-process
probes; it does not turn a subagent or detached PID into a durability claim.

Cancellation signals only a positively identified owned supervisor/process group; a bare stored PID is
insufficient. Unknown ownership prevents signalling and cleanup. `clean` removes only an inactive run-owned
checkout after identity/dirty checks, preserving manifests and logs. It refuses active, unknown, unrelated or
unexpectedly dirty environments. No force-delete, automatic retry, automatic evidence pruning or automatic rollback
is included. A denied sandbox operation remains pending with its actual code; do not skip tests or reroute it.

Text output uses stable `TEST_RUN_*` sentinels/codes; JSON returns one object. Launch success is exit 0 with pending
state, not a test pass. `status` returns 0 for pending/pass, 1 for a known negative result and 2 for unknown or
unreadable execution; the payload always carries the exact state. Native exit codes remain separate. Invalid input
or inability to start returns 2. Logs remain bounded (`--tail`, default 100); raw output stays at its recorded path.
Detailed field/code names are finalized in the Development spec under `ARCH-08-1-agent-output` and
`CAP-ADV-agent-advisory-protocol`.

### 3.5 Coverage and completion

A local run records interval B..A and executes the selection against A's fixed files. A pass at A never claims B's
untested descendant C passed. For accumulated later changes, compute selection from the earliest still-uncovered
baseline to the current landed SHA; do not overwrite it merely because an intermediate partial run passed.

At final local completion, the current landed HEAD has passing required synchronous results and either passing
required E2E at that HEAD or an explicit empty E2E selection for the uncovered interval. If main advances after
an E2E result, inspect the complete added interval: run required selected tests at the later HEAD or record why
selection requires no E2E. Report every actual checked SHA; do not relabel an older result as execution at HEAD.
Generated repair commits are part of this interval. Launch, cleanup or the merge CLI's successful exit does not
complete verification.

Client cloud completion reports required PR checks, tested PR revision, confirmed merge and selected risk policy.
It makes no claim that the merged combination passed. Required unavailable PR checks remain unmet; checks
intentionally absent under that policy do not. `PADR-delivery-verification-routes` partially supersedes
`ADR-post-merge-verification` for this client completion boundary while retaining local obligations.

### 3.6 Ownership and reconciliation

The broad parent paths in frontmatter exist because the feature/test directories do not yet exist. Development
writes only these narrowed responsibilities, plus generated projections produced by authorized sync:

| Owner | Planned files/responsibility |
| :--- | :--- |
| `devkit_agt.features.test_execution` | New `cli`, typed `BaseUseCase` operations, run model, supervisor/process and manifest repositories; unit/integration/E2E tests mirroring this feature |
| `devkit_agt.features.worktree` | Test-only fixed-commit checkout preparation/removal API and focused tests; existing activity start/finish behavior retained |
| Package registration | `packages/devkit/pyproject.toml`, package README and `.devkit/architecture.toml` |
| Repository selection | `scripts/affected_tests.py`, thin justfile documentation and existing selector regressions |
| Consumer guidance | Source spec bundle completion, worktree, integration, orchestration and proposal-acceptance guidance; focused integration tests |
| Living Spec | Delivery completion/proposal acceptance, harness execution/guidance, worktree allocation and component/role-policy boundaries; CLI quick reference and PADR promotion |
| devkit consumption | `AGENTS.md` verification instructions explicitly local-orchestrated; no cloud CI adoption |

Approve only `test_execution -> devkit_agt.features.worktree` and
`test_execution -> devkit_dist.features.project` as new feature edges. Worktree keeps its existing project edge.
No reverse dependency from worktree, integration, compact or spec to test execution is required. Invoke existing
project wrappers as commands rather than importing compact internals. Generic integration remains Git-only.

A harness capability will own the test-run contract and its entrypoints; use the existing document index to choose
its final ID during Development. Local/cloud policy is restated in `CAP-DLV-delivery-workflows` section 4.8 and
`CAP-HARN-agent-guidance`; proposal acceptance in `CAP-DLV-proposal-planning` follows the same route distinction.
Partial supersession keeps the unaffected Git/authority/recovery clauses of `ADR-post-merge-verification` active.
Read authoring context before later source asset edits. This Planning run edits no deployed guidance.

### 3.7 Acceptance and validation plan

- **AC-1:** Given E2E edits, explicit data mappings, broad directories, unknown inputs and shared foundations,
  unit/integration selection collects no E2E, E2E selection collects only E2E, and full fallback preserves each tier.
  Empty tiers do not trigger an unscoped pytest run. Preserve embedded rule and frontend checks.
- **AC-2:** Given either worker route, guidance runs unit/integration frequently and relevant E2E when required;
  failed required client PR CI blocks merge independently of worker selectivity.
- **AC-3:** Given a run at A and main advancing to B with changed dependencies, A's files/environment/runtime remain
  fixed and its result names A. A setup/sync failure prevents command execution.
- **AC-4:** Given a controlled E2E command waiting on a test-owned latch, start returns and another independent task
  completes before releasing that latch. Record setup/start/command/Host-blocked time and resource cost against a
  synchronous run on the same revision, command and test set; correctness is ordering, not an arbitrary speed ratio.
- **AC-5:** Given merges while a run is active, only one run is preparing/running, the next interval retains all
  outstanding changes and no descendant is reported tested by an ancestor pass. A batch cannot defer dispatch forever.
- **AC-6:** Given a failed local result, the next Host result check holds merges and prioritizes repair. Repair then
  checks the accumulated state without merge replay or automatic rollback.
- **AC-7:** Given a completed launch call and a separate status process, evidence remains readable. Simulate parent
  exit, interrupted supervisor, missing terminal record and reused PID; unknown execution never passes or kills an
  unrelated process. Document OS/host survival limits.
- **AC-8:** Given cleanup, active/unknown/unrelated/dirty environments are preserved; an eligible run loses only its
  own checkout while logs and manifest remain readable.
- **AC-9:** Given an explicitly configured client cloud scenario, required PR CI including E2E plus automatic merge
  completes PR work without latest-base merged-result validation or immediate postmerge CI.
- **AC-10:** Given failed/missing client PR CI, a contract walkthrough retains the merge block and routes rework with
  check/run identity. Label external dispatch unexecuted unless validated in that consumer.
- **AC-11:** Given passing PRs whose combination breaks main, a client walkthrough routes the nightly failure as
  subsequent repair and reports accepted detection delay, evidence and dispatch owner without assuming an active Host.
- **AC-12:** Given devkit itself, repository instructions use only local-orchestrated completion. Client cloud options
  never waive devkit's required checks. Guidance distinguishes an intentionally absent cloud check from a missing gate.

Keep the measured synchronous baseline reproducible in the Development worktree with the async path disabled.
Do not check out a different revision or compare different test selections to claim a speedup. Product-process
probes and native test runs are separate evidence from agent-guidance walkthroughs. New public CLI behavior
justifies `dev_effort: high`; platform process probes and a consumer fixture cover it without modifying a real client.

## 4. Lifecycle & Retirement Criteria

Planning compares implementation owners, records bounded evidence, drafts both PADRs, and folds an independent
Challenger review before direction acceptance. The work remains one L-sized verification capability. Broad test
performance tuning, a distributed runner or external cloud adapter implementation requires separate scope.

`plan-accept` approves this direction and its partial policy supersession; handoff separately authorizes Development.
This run grants neither acceptance nor implementation authority. Development writes its spec, plan and tasks,
then implements, reviews and reconciles the actual behavior and evidence. Keep the dependent playbook proposal
in Backlog until the prerequisite policy and execution contract land and pass required local verification.
