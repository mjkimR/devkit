---
id: SPEC-async-e2e-verification
title: Asynchronous E2E Verification
summary: "Provide isolated asynchronous native commands with persistent evidence and guarded cancellation and cleanup. Use tier-aware selection and background observation for local-orchestrated E2E."
status: completed
created: 2026-11-06
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-async-e2e-verification] Asynchronous E2E Verification

## 1. Problem Statement & Motivation

Handed off from proposal PROP-async-e2e-verification on 2026-11-06.
- **Preserved Materials**: `docs/materials/2026-11/20261106-async-e2e-verification`

### 1. Background & Hypothesis

Long E2E runs block local-orchestrated integration. `scripts/affected_tests.py` excludes many E2E paths, but
explicit data mappings, edited E2E tests and its full fallback can still include them. `--e2e` adds E2E rather
than selecting only that tier. Synchronous iteration therefore lacks an explicit non-E2E boundary.

`CAP-DLV-delivery-workflows` section 4.8 and `ADR-post-merge-verification` require landed verification before
completion. The git-operator reports Git effects with verification pending; the Host accepts test results.
The existing `devkit run` captures bounded output synchronously and stops its process group on interruption.
It does not manage detached test runs (`CAP-CMP-bounded-execution`).

The hypothesis is that selective E2E in an isolated fixed-commit environment lets the Host start independent
work before E2E finishes. Batching can reduce repeat runs. Asynchrony alone reduces neither test execution time
nor CPU consumption. `docs/materials/2026-11/20261106-async-e2e-verification/planning-evidence.md` records bounded measurements and their limits.

#### 1.1 Execution mechanism and operating guidance

Devkit provides isolated asynchronous command execution, fixed-commit environment preparation and result inspection.
The executor does not need to know whether a caller uses local-orchestrated work, a cloud PR or another workflow.
It reports what command ran, where it ran and its actual outcome; the caller owns test timing and delivery decisions.
There is no local/cloud policy selection, route registry, profile mapping or corresponding configuration switch.

Devkit itself uses local-orchestrated development. Its local-orch skill needs concrete instructions for launching
E2E, proceeding with independent work, collecting results and prioritizing repairs. Include that integration here.
Client local/cloud operating examples and their tradeoffs belong to the dependent test-management playbook as
recommendations, without adding a product-level completion policy or configuring client CI.

#### 1.2 Scope and non-goals

- Include one harness-owned isolated command lifecycle under `devkit exec` and devkit's tier-aware affected selector.
- Preserve existing `devkit run` synchronous execution, interruption and bounded-output behavior.
- Include local-orch usage guidance and devkit's own local adoption.
- Exclude local/cloud policy selection, new consumer completion contracts and test-profile configuration.
- Exclude cloud-pr use by devkit itself, CI workflow edits, external autohub implementation and release changes.
- Exclude replacing unit/integration with E2E, a mandatory verifier subagent and git-operator test supervision.
- Exclude a distributed scheduler, environment pool, container platform, Windows background execution and global locks.
- Exclude broad test deletion, fixture optimization and relabelling integration tests as cheap without measurements.
- Exclude test-playbook changes, retained in dependent `PROP-test-playbook-verification-policy`.
- Planning changes only this proposal bundle. Active contracts and production behavior change during Development.

## 2. User Stories

As an agent, start native verification at a fixed commit, continue independent work and collect persistent evidence before declaring delivery complete.

## 3. Non-Goals

Scope Excluded: cloud orchestration and CI implementation, Windows, schedulers, profile maps, implicit environment cleanup, changed compact semantics and client completion policy.

## Approved design and evidence

### 2. Planning Decisions and Evidence

| Spike | Settled direction | Evidence or remaining validation |
| :--- | :--- | :--- |
| Q1 Selection | Independent tier and impact scope; conservative fallback stays inside the selected tier | Selector source and existing selector regressions; section 3.1 |
| Q2 Cost | Measure bounded suites now; require same-machine synchronous/async comparison during Development | `docs/materials/2026-11/20261106-async-e2e-verification/planning-evidence.md`; no whole-suite speedup claim |
| Q3 Owner | A separate `devkit exec` group for isolated native commands, with test-specific choices in caller commands/guidance | `ADR-isolated-test-runs`; interface alternatives below |
| Q4 Runtime | Detached POSIX supervisor, persistent evidence, no daemon/reboot guarantee | Process survival probes and failure injection are Development checks |
| Q5 Isolation | Execution-only detached checkout, independent dependency environment and run-specific temporary resources | Worktree revision support exists; test-environment allocation is added explicitly |
| Q6 Evidence | Results name the exact tested SHA; local-orch tracks outstanding changes and completion | Sections 3.2 and 3.4 |
| Q7 Recovery | Distinguish setup, test failure, interruption and unknown; preserve evidence on cleanup | Section 3.3; no automatic retry, replay or rollback |
| Q8 Boundaries | `devkit_agt.features.isolated_execution` with declared worktree/project dependencies | Section 3.5; no other feature edge is approved |
| Q9 Operating examples | Local/cloud scheduling recommendations move to the dependent playbook, without runtime policy selection | `PROP-test-playbook-verification-policy` |
| Q10 Command mapping | Pass native argv directly after `--`; reuse existing worktree setup, without a test-profile map in config | Section 3.3 |
| Q11 Waiting and cleanup | `wait <run-id> --clean` observes one execution and returns its preserved result plus guarded cleanup outcome | Section 3.3; no notification daemon |

The existing revision-aware worktree preparation is reusable, but its activity-branch semantics are not execution
identity. Extend worktree ownership for execution-only checkout creation/removal instead of creating synthetic SDD
Units. Setup and sync warnings prevent a test run from becoming ready. The background lifecycle does not reuse
the compact runner's interruption ownership or its pruned log store. Tests are the first consumer; builds and
other project-native commands use the same mechanism without a test-specific mode.

The preliminary decision titled "Separate local and cloud verification completion" is withdrawn. A formal
consumer-policy split and supersession of the existing landed-verification ADR exceed the requested mechanism.
Retain one execution-lifecycle PADR. Local/cloud operating examples remain in the dependent playbook.

Interface and ownership choices below are the recommended direction for `plan-accept`, rather than claims about
an existing command. Direct native command passing remains the selected interface; profile mapping is not added.

### 3. Proposed Design & Impact

#### 3.1 Tier-aware test selection

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
runs before merge; ordinary worker iterations need not repeat it. Consumer CI requirements remain owned by
that repository.

#### 3.2 Local-orch usage guidance

Update the source local-orch skill and relevant integration/completion references to use the execution mechanism.
This is an agent procedure, not an executor policy mode. Devkit's own local-orch consumption uses the procedure;
client repositories retain their own checks and commands.

1. Before the first merge, save the target SHA for affected selection. After selected merges, synchronize landed
   dependencies and managed assets in fresh processes, repair and commit stale generated artifacts, then run
   unit/integration and required lint, types, rules and frontend checks synchronously.
2. Determine required E2E from the accumulated change interval. When selection is nonempty and no E2E is running,
   launch it at the fixed landed SHA before beginning the next independent task. A selected merge batch has a
   bounded unit set. When selection is empty, record the reason instead of claiming a test pass.
3. The Host launches `exec wait <run-id> --clean` through its execution tool's background facility to collect the
   result and reclaim the checkout without repeated agent-driven polling. The Host can start independent work
   before that waiter finishes. Recommend
   one active E2E run initially to limit CPU/resource contention; this is scheduling advice, not a CLI-wide
   admission limit or hidden queue. A verifier subagent is optional; git-operator keeps Git lifecycle duties.
4. If more changes land while a run is active, preserve the outstanding interval. Finish the active run rather
   than repeatedly cancelling to chase HEAD. Collect it and dispatch the accumulated selection before another
   merge. Do not let an indefinitely growing batch postpone E2E forever.
5. Check results before each merge, on observed completion and at batch/session completion. On an observed
   failure, hold new merges and prioritize repair; independent branch work can continue. Repair the landed
   state and recheck the accumulated interval without automatic rollback or merge replay.
6. A waiter completion is evidence to inspect, not an automatic merge decision. Keep required verification
   pending until results are collected. Record run IDs, tested SHA, batch baseline,
   outstanding units and next collection step in recoverable Host notes. After context loss, inspect stored runs
   and merge history; uncertain coverage uses full fallback rather than comparing main to itself.

The executor does not implement those merge/completion decisions or automatically dispatch workers. The Host
applies the repository's existing requirements and distinguishes an actual pass from launch success.

#### 3.3 Isolated command interface and lifecycle

`devkit_agt.features.isolated_execution` owns `devkit exec`. Existing `devkit run [OPTIONS] COMMAND...` remains
unchanged. It executes synchronously in the current directory and preserves its interruption/output behavior.

| Interface alternative | Assessment |
| :--- | :--- |
| Extend `run` with lifecycle subcommands | Arbitrary command forwarding would compete with subcommand parsing; rejected |
| Add `run` flags plus a `runs` management group | Preserves parsing but splits isolated execution across two namespaces; rejected |
| A test-only group | Does not reflect generic setup, argv and result handling; rejected |
| Separate `exec start/list/status/logs/wait/cancel/clean` group | Selected; one isolated-execution namespace and no changes to the existing run entry |

Proposed commands, unavailable until Development:

```sh
devkit exec start --ref <fixed-sha> -- just test-affected --tier e2e --base <baseline-sha>
devkit exec list
devkit exec status <run-id>
devkit exec logs <run-id> --tail 100
devkit exec wait <run-id> [--clean] [--timeout <seconds>]
devkit exec cancel <run-id>
devkit exec clean <run-id>
```

`start` resolves `--ref` to an exact commit, persists the request and launches a detached supervisor.
Every `exec start` prepares a fixed-commit worktree and executes asynchronously; separate `--isolate` or `--async`
switches are unnecessary in this group. It returns a run ID while state is `preparing`. The caller passes any
affected-selection baseline to its native command; `exec` has no `--base` selector or test-completion logic.
Checkout/setup and the native command run in the background. The supervisor
owns the captured run definition, not mutable files in main. Project setup comes from the existing worktree setup
configuration, with an explicit per-run `--setup` override. Native test argv follows `--`; devkit does not invent
pytest, uv, just, service provisioning or a test-profile configuration system for consumers. The command passed
after `--` is the test command; no `--profile` option or test-profile table is introduced in `config.toml`.

Worktree owns fixed-commit detached execution checkout creation and guarded removal. Execution checkouts have no SDD Unit,
merge, push or post-finish hooks. Their path is a unique sibling of the retained base; a manifest binds the path
to this run. Setup runs in that checkout and creates its own environment. Scrub inherited `VIRTUAL_ENV` and
project-environment overrides that would redirect dependencies to main; record project setup requirements.
Restore managed assets with locked sync where applicable. Setup/sync failure is `setup_failed`, never a warning
that allows the command to start. Do not copy `.env` or credentials implicitly.

Give each run a private temporary directory and run ID. Resource-dependent commands use disposable data and
isolated services or ephemeral ports supplied by the project. The caller checks resource suitability before
launch: the executor cannot infer whether arbitrary command argv shares a database or fixed port with other work.

Persist manifests and logs under the repository's common Git directory, outside disposable checkouts. Store
repository identity, run ID, fixed SHA, argv, setup command, runtime identity, environment path, process
identity, timestamps, phase, terminal outcome, exit code and logs. Writes use atomic replacement. Keep the
captured launcher/runtime usable while main changes; command dependencies come from the fixed checkout. Inspect
and bounded log retrieval work from a later Host process. `list` returns run IDs and current states, including
outstanding and terminal executions, so context loss does not hide results. `status` inspects one run ID.

| Outcome | Meaning and next action |
| :--- | :--- |
| `preparing` / `running` | No terminal result yet; caller inspects again |
| `passed` | Actual native command exited zero; apply only to its tested SHA/scope |
| `failed` | Native command ran and failed; return its exit code and evidence to the caller |
| `setup_failed` | Checkout, runtime, setup or locked sync could not complete; repair prerequisites and start a new run |
| `cancelled` / `interrupted` | No passing evidence; inspect retained logs and decide a new run |
| `unknown` | No terminal record and no positively identified live supervisor; investigate, never infer success |

Support local macOS and Linux initially. The supervisor separates its session, stdin and log descriptors from
the initiating call. Returning from a tool call or losing Host conversation context does not intentionally cancel
it. Host-enforced descendant termination, application exit policies, OS shutdown and machine reboot have no
survival guarantee. Records remain recoverable. Development verifies the supported boundary with separate-process
probes; it does not turn a subagent or detached PID into a durability claim.

Cancellation and environment recovery are separate effects. `cancel` requests termination during preparation
or native execution and returns the actual cancellation outcome. It does not remove the worktree. The supervisor
stops setup/native commands through its positively identified process ownership, gives termination a bounded grace
period, escalates where safe and confirms that managed writers have exited before marking the run cancelled.
A bare stored PID or exit of only the launcher is insufficient. Cover nested wrappers such as `devkit run`, which
owns another process group, and commands whose leader exits before children. If ownership or termination cannot
be confirmed, retain the environment and report the unresolved state. Commands that intentionally detach beyond
the managed process boundary require project cooperation; this is worktree isolation, not OS containment.

Completed, failed and cancelled runs retain their environments by default. `clean` is an explicit request to
remove an inactive run-owned checkout after identity/dirty checks. It preserves the manifest, result summary and
logs outside that checkout, and refuses active, unknown, unrelated or unexpectedly dirty environments. Cleanup
is idempotent: an already-cleaned run remains inspectable and reports that no checkout removal remains.
No expiry-driven or implicit on-completion cleanup is added. Native artifacts still inside the checkout are
removed by successful cleanup; callers retain the environment when they need those artifacts for diagnosis.

`wait <run-id>` handles per-run observation inside the CLI instead of requiring the agent to invoke `status`
repeatedly. It periodically checks stored state and process identity until a terminal outcome is available, then
returns the bounded result summary, tested SHA, native exit code and retained log locations. A run that is already
terminal returns immediately. `--clean` additionally requests guarded checkout cleanup after a trustworthy terminal
result is persisted and managed processes are confirmed inactive. It applies after success, failure, setup failure
or confirmed cancellation, provided the ordinary clean guards pass. Preserve the command result before deleting
its checkout and emit one final response containing separate execution and cleanup outcomes. Under JSON this is
one object. A cleanup failure never replaces or rewrites the recorded execution result.

Without `--clean`, waiting preserves the environment. On unknown execution or `--timeout`, return an actionable
non-success result and retain the environment; do not cancel or clean it. Interrupting the waiter stops only that
observer, not the detached execution. Cleanup already in progress remains recorded and re-inspectable; a later
explicit clean retries only its safe remaining effects. Multiple waiters may inspect the same execution; serialize
per-run cleanup so that repeated wait/clean requests do not remove resources twice or touch unrelated paths.

The intended local usage is `start` followed by one background `wait --clean`. The execution tool may deliver its
completion event and output to the Host; the CLI itself provides no push notification into an agent conversation.
On tools without such delivery, a later result lookup is still necessary. Waiter observation and resource cleanup
do not become a worker scheduler: the Host still chooses subsequent work, coverage and failure repairs. No test
profile, local/cloud setting, daemon or remote notification integration is introduced.

No force-delete, automatic retry of native commands or automatic rollback is included. A denied sandbox operation
retains its actual code and state; do not skip required work or reroute the operation.

Text output uses stable `EXECUTION_*` sentinels/codes; JSON returns one object. Launch success is exit 0 with pending
state, not a test pass. `status` returns 0 for pending/pass, 1 for a known negative result and 2 for unknown or
unreadable execution; the payload always carries the exact state. Native exit codes remain separate. Invalid input
or inability to start returns 2. Logs remain bounded (`--tail`, default 100); raw output stays at its recorded path.
For `wait`, exit 0 requires a successful command and successful requested cleanup; known negative execution
returns 1. Unknown state, wait timeout or refused/failed requested cleanup returns 2 with the original execution
result and separate observer/cleanup code retained. Native exit codes remain in the result rather than becoming
the observer's exit code. Detailed field/code names are finalized in the Development spec under `ARCH-08-1-agent-output` and
`CAP-ADV-agent-advisory-protocol`.

#### 3.4 Evidence and local-orch completion

In devkit's local-orch use, the caller records interval B..A and passes a command that selects tests against A's
fixed files. A pass at A never claims A's untested descendant C passed. For accumulated later changes, compute selection from the earliest still-uncovered
baseline to the current landed SHA; do not overwrite it merely because an intermediate partial run passed.

At final local completion, the current landed HEAD has passing required synchronous results and either passing
required E2E at that HEAD or an explicit empty E2E selection for the uncovered interval. If main advances after
an E2E result, inspect the complete added interval: run required selected tests at the later HEAD or record why
selection requires no E2E. Report every actual checked SHA; do not relabel an older result as execution at HEAD.
Generated repair commits are part of this interval. Launch, cleanup or the merge CLI's successful exit does not
complete verification.

The same execution mechanism can be called from any workflow without a local/cloud mode flag. Delivery
completion stays with the caller and its existing repository instructions. The follow-up playbook explains
recommended local and cloud arrangements; it does not create mandatory product policy alternatives.

#### 3.5 Ownership and reconciliation

The broad parent paths in frontmatter exist because the feature/test directories do not yet exist. Development
writes only these narrowed responsibilities, plus generated projections produced by authorized sync:

| Owner | Planned files/responsibility |
| :--- | :--- |
| `devkit_agt.features.isolated_execution` | `exec` CLI including wait/optional cleanup, typed `BaseUseCase` operations, run model, supervisor/process and manifest repositories; unit/integration/E2E tests mirroring this feature |
| `devkit_agt.features.worktree` | Execution-only fixed-commit checkout preparation/removal API and focused tests; existing activity start/finish behavior retained |
| Package registration | `packages/devkit/pyproject.toml`, package README and `.devkit/architecture.toml`; add only the `exec` harness command name to dist CLI discovery diagnostics and focused plugin tests |
| Repository selection | `scripts/affected_tests.py`, thin justfile documentation and existing selector regressions |
| Local-orch integration | Source spec bundle local-orch skill and relevant integration/completion references; focused guidance tests |
| Living Spec | Harness execution/guidance, local-orch verification procedure, worktree allocation and component boundaries; CLI quick reference and execution PADR promotion |
| devkit consumption | `AGENTS.md` verification instructions explicitly local-orchestrated; no cloud CI adoption |

Approve only `isolated_execution -> devkit_agt.features.worktree` and
`isolated_execution -> devkit_dist.features.project` as new feature edges. Worktree keeps its existing project edge.
No reverse dependency from worktree, integration, compact or spec to isolated execution is required. Invoke existing
project wrappers as commands rather than importing compact internals. Generic integration remains Git-only.

A harness capability will own the isolated-command contract and its entrypoints; use the existing document index to choose
its final ID during Development. `CAP-DLV-delivery-workflows` section 4.8 and `CAP-HARN-agent-guidance` explain
local-orch usage while preserving the existing final-verification boundary. Asynchronous execution does not
require superseding `ADR-post-merge-verification`: independent work may proceed while required results remain
pending, and completion still collects them. Client completion policies and cloud automation are outside this
proposal. Read authoring context before later source asset edits; this Planning run edits no deployed guidance.

Keep the measured synchronous baseline reproducible in the Development worktree with the async path disabled.
Do not check out a different revision or compare different test selections to claim a speedup. Product-process
probes and native test runs are separate evidence from agent-guidance walkthroughs. New public CLI behavior
justifies `dev_effort: high`; platform process probes and a consumer fixture cover it without modifying a real client.

### 4. Lifecycle & Retirement Criteria

Planning compares implementation owners, records bounded evidence, retains the execution PADR and folds an
independent Challenger review before direction acceptance. The work remains one L-sized isolated-execution capability with E2E as its first consumer. Broad test
performance tuning, a distributed runner or external cloud adapter implementation requires separate scope.

`plan-accept` approves the execution capability and local-orch integration direction. Handoff separately
authorizes Development.
This run grants neither acceptance nor implementation authority. Development writes its spec, plan and tasks,
then implements, reviews and reconciles the actual behavior and evidence. Keep the dependent playbook proposal
in Backlog until the prerequisite execution contract and local usage land and pass required local verification.


## Acceptance Criteria

### [AC-01] E2E edits

- **Given** E2E edits.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Explicit data mappings, broad directories, unknown inputs and shared foundations, unit/integration selection collects no E2E, E2E selection collects only E2E, and full fallback preserves each tier. Empty tiers do not trigger an unscoped pytest run. Preserve embedded rule and frontend checks.

### [AC-02] local-orch work

- **Given** local-orch work.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** The source skill explains synchronous unit/integration, selective asynchronous E2E, continued independent work, result collection and repair priority. It uses the delivered command interface.

### [AC-03] a run at A and main advancing to B with changed dependencies

- **Given** a run at A and main advancing to B with changed dependencies.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** A's files/environment/runtime remain fixed and its result names A. A setup/sync failure prevents command execution.

### [AC-04] a controlled E2E command waiting on a test-owned latch

- **Given** a controlled E2E command waiting on a test-owned latch.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Start returns and another independent task completes before releasing that latch. Record setup/start/command/Host-blocked time and resource cost against a synchronous run on the same revision, command and test set; correctness is ordering, not an arbitrary speed ratio.

### [AC-05] merges while a run is active

- **Given** merges while a run is active.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** The local-orch procedure retains all outstanding changes for the next selection and never reports descendants tested by an ancestor pass. The procedure bounds dispatch; the initial one-run recommendation does not become a mandatory executor concurrency policy.

### [AC-06] a failed local result

- **Given** a failed local result.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** The next Host result check holds merges and prioritizes repair. Repair then checks the accumulated state without merge replay or automatic rollback.

### [AC-07] a completed launch call and a separate status process

- **Given** a completed launch call and a separate status process.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Evidence remains readable. Simulate parent exit, interrupted supervisor, missing terminal record and reused PID; unknown execution never passes or kills an unrelated process. Document OS/host survival limits.

### [AC-08] cleanup

- **Given** cleanup.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Active/unknown/unrelated/dirty environments are preserved; an eligible run loses only its own checkout while logs and manifest remain readable.

### [AC-09] an arbitrary native command

- **Given** an arbitrary native command.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** `start` runs the argv passed after `--` with project setup. There is no test-profile mapping or local/cloud selection in the CLI or config; native test, build and non-pytest fixtures use the same interface. A test baseline, if needed, belongs to the passed command.

### [AC-10] devkit itself

- **Given** devkit itself.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Repository instructions use local-orchestrated consumption. The executor reports command evidence without deciding merge approval, delivery completion or cloud CI behavior.

### [AC-11] existing `devkit run` invocations

- **Given** existing `devkit run` invocations.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Current-directory execution, argument forwarding, bounded output and interruption cleanup remain unchanged. The separate `exec` group owns isolated execution lifecycle; list/status let a fresh process locate and inspect retained executions.

### [AC-12] cancellation during setup or native execution

- **Given** cancellation during setup or native execution.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Terminate and verify managed process groups before confirming cancellation. A nested compact wrapper, a surviving child, unknown ownership or reused PID cannot cause premature cleanup or signalling of unrelated processes. Cancel itself retains the checkout.

### [AC-13] a terminal run

- **Given** a terminal run.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** `wait` returns its bounded persisted result without agent-driven status polling. `wait --clean` removes only an eligible checkout and reports execution and cleanup separately; a failed command retains its failure evidence after cleanup, and a cleanup refusal retains its original execution outcome.

### [AC-14] waiter interruption

- **Given** waiter interruption.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Timeout, unknown state or concurrent waiters, execution is not implicitly cancelled and unsafe cleanup does not occur. Repeated cleanup is idempotent. Waiting without `--clean` retains the checkout, and completed executions have no unsolicited automatic cleanup.

### [AC-15] a Host using background `wait --clean`

- **Given** a Host using background `wait --clean`.
- **When** the applicable lifecycle operation or guidance walkthrough runs.
- **Then** Local-orch guidance explains result collection through the execution tool and its notification limits. CLI completion alone does not imply an agent received a push event or made a delivery/repair decision.

## Development assumptions

The carried premises still hold at the handoff base. Use a captured standard-library supervisor and captured worktree execution module; neither imports the mutable project after launch. Process identity uses OS start identity and argv, with conservative unknown-state refusal. macOS runtime probes are available; Linux execution remains unverified locally. CLI-only output has no human-operated screens.
