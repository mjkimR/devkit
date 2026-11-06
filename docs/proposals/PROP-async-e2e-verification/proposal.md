---
id: PROP-async-e2e-verification
title: Asynchronous E2E Verification
summary: "Separate local-base verification with Host-managed asynchronous E2E from cloud-base delivery with premerge PR CI and accepted nightly detection of integration failures. Keep worker iteration lightweight and define route-specific evidence, recovery and completion."
status: reviewing
created_at: 2026-11-06
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - scripts/
    - justfile
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/
    - docs/architecture/
    - docs/decisions/
    - AGENTS.md
  excludes:
    - packages/devkit-viewer/
    - .github/workflows/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-async-e2e-verification] Asynchronous E2E Verification

## 1. Background & Hypothesis

Long E2E runs block useful work during branch verification and after local-orchestrated merges. The requested
outcome is less blocking time and fewer unnecessary E2E executions while retaining required coverage. No
execution-time measurements have been collected for this proposal.

`scripts/affected_tests.py` excludes most E2E paths by default, but includes them for E2E edits and explicit data
mappings. Its `mode=full` fallback runs the full suite. `--e2e` includes E2E alongside other selected tests; it
is not an E2E-only selector. Existing separation therefore does not guarantee a lightweight synchronous run.

`CAP-DLV-delivery-workflows` and `ADR-post-merge-verification` require final verification before delivery
completion and permit one verification after a selected batch of merges and repairs. The git-operator returns
Git effects with verification pending. The Host retains final verification responsibility.

The hypothesis is that synchronous unit/integration checks plus selective asynchronous E2E can shorten the
Host's blocked time. Fixed-commit isolation and durable evidence let subsequent work proceed while verification
remains pending. E2E still runs when needed. Asynchrony alone does not reduce CPU time or execution count.

### Scope and non-goals

The intended outcome is a verification policy with two explicit delivery scenarios: local-base with an active
Host and cloud-base through cloud-pr without a continuously available Host. Both keep worker iteration lightweight.
Direct Host management is recommended for local background runs. CLI ownership remains a Planning choice.
The distinction follows delivery ownership and completion policy, not merely the machine executing a worker.

- Exclude replacing unit/integration checks with E2E alone; their coverage is complementary.
- Exclude a mandatory verification subagent or test-supervision duties for git-operator.
- Exclude a distributed scheduler, environment pool, container platform or global locking service.
- Exclude blanket test deletion, broad fixture rewrites and treating every integration test as cheap.
- Include the cloud-base CI timing and risk-acceptance contract; exclude CI workflow implementation and release
  changes in this draft. Scheduled full CI remains a backstop, not local completion evidence.
- Exclude test-playbook revision, tracked separately by `PROP-test-playbook-verification-policy`.
- Exclude implementation or active policy changes during this Backlog task.

## 2. Technical Spike Questions

- **Q1 — Selection:** Which changes require E2E before merge, after merge or no E2E? How should explicit data
  mappings, E2E edits and uncertain dependency graphs behave with independent tier and impact-scope selection?
- **Q2 — Cost:** Measure elapsed time, setup cost and resource usage of representative test runs. Identify
  expensive integration tests without assuming directory tier is an exact cost classification.
- **Q3 — Execution owner:** Is a repository script sufficient, or does reuse across consumer projects justify
  a devkit CLI? Compare recovery behavior and implementation cost with existing execution facilities.
- **Q4 — Runtime:** What survives a tool call ending, Host context loss or host application exit on supported
  platforms? State the persistence guarantee; a subagent does not inherently make a process durable.
- **Q5 — Isolation:** Define setup for a fixed-commit worktree, independent virtual environment and generated
  assets. Identify shared ports, temporary paths or external services requiring separate treatment.
- **Q6 — Completion:** Map tested SHAs, accumulated changes and pending units as main advances. Define when a
  later run covers intervening merges without granting success to untested descendants.
- **Q7 — Recovery:** Distinguish test failure, setup failure, interruption and unknown process state. Define
  cancellation, evidence retention, safe cleanup and handling of unavailable execution permissions.
- **Q8 — Ownership:** If a CLI is selected, choose its owning feature and required declared dependencies under
  `ARCH-05-2-components`. Narrow the candidate paths before handoff; this draft approves no new feature edge.
- **Q9 — Cloud recovery:** Define the concrete recipient and dispatch mechanism for failed PR CI and nightly
  repair requests when the Host is absent. Record nightly cadence, missed-run visibility and repair ownership.
  These questions do not reopen the accepted risk of a broken merged base before nightly detection.
- **Q10 — Policy mapping:** Define how consumers select local-base or cloud-base and report completion under
  that policy. Identify the ADR changes needed to bound existing final-landed-verification requirements.

## 3. Proposed Design & Impact

### 3.1 Test selection and execution timing

Separate test tier (`unit+integration`, `e2e`, `all`) from impact scope (`affected`, `full`). Preserve conservative
full fallback within each selected tier: uncertainty expands synchronous coverage to all unit/integration tests
and asynchronous coverage to all required E2E tests.

Workers on both routes run unit/integration frequently and E2E only when needed for their change. Required lint,
types, rules and frontend checks remain applicable. Cloud PR CI is a separate gate that includes required E2E;
worker-side selectivity does not remove that gate.

| Delivery point | Local-base / local-orchestrated | Cloud-base / cloud-pr |
| :--- | :--- | :--- |
| Worker iteration | Worktree unit/integration, with relevant E2E when needed | PR work unit/integration, with relevant E2E when needed |
| Before merge | Required branch checks | PR CI including E2E; failure requests rework and prevents automatic merge |
| Merge | Host-managed integration | Automatic merge after required PR CI passes |
| Immediately after merge | Synchronize runtime and generated assets; unit/integration synchronously, required E2E asynchronously | No immediate postmerge CI |
| Later failure handling | Host prioritizes repair and holds new merges when failure is observed | Nightly tests detect merged-base failures and request follow-up repair |
| Work completion | Required synchronous and asynchronous results collected for the covered landed scope | Required PR CI passes and automatic merge succeeds; nightly recovery is subsequent work |

Local synchronous tests reuse their development environment. Local background tests use a fixed-commit
environment because main's files and dependencies can change during execution. Save the target SHA before the
first merge for affected selection; comparing main to itself is invalid.

### 3.2 Cloud-base risk acceptance

Cloud-base is a batch-oriented delivery scenario without a continuously available Host. It explicitly accepts
that individually passing PRs can break main when combined. It requires neither validation against the latest
base's prospective merge result nor an immediate postmerge CI run. A merge queue or forced base refresh is not
a prerequisite of this scenario. A passing PR run proves only its actual tested revision and scope.

Nightly tests detect accumulated integration defects after landing. Main may remain broken between merge and
nightly detection and until repair completes. The policy records the accepted risk, nightly cadence and repair
request recipient/mechanism. A nightly failure creates follow-up repair work; it does not retroactively turn a
completed PR into a pending local asynchronous verification job. Nightly is not claimed as proof before it runs.

The absence of an immediate postmerge check is intentional under this selected policy, not an unmet gate.
A failed required PR check still prevents automatic merge and triggers rework. Planning specifies the dispatch
mechanism and evidence without assuming that a main agent will observe the failure in an active session.

### 3.3 Local Host scheduling and responsibility

The Host starts background execution and checks results before new merges and at work-batch completion. On
failure, it holds new merges and prioritizes repair. Independent workers may continue work. If failure becomes
visible after another merge, retain its original SHA and verify the accumulated landed state after repair.

Start with one active E2E run per Host/repository. Accumulate required changes for the next run instead of
launching one per merge. Finish active runs rather than repeatedly cancelling to chase HEAD. The next selection
includes all outstanding changes since the relevant successful baseline. Planning defines a dispatch boundary
that prevents indefinite deferral. Collect the final required run before reporting affected work complete.

| Executor option | Assessment |
| :--- | :--- |
| Host-managed background process | Recommended initial approach; no delegation overhead for simple execution and result collection |
| Reusable verification subagent | Optional when multiple runs or failure analysis burden the Host; returns evidence and first diagnosis, while development workers own fixes |
| git-operator supervising tests | Not recommended; long test supervision competes with lifecycle jobs and expands its current responsibility |

All options require the same isolation and evidence. A subagent does not inherently improve test speed, process
survival or permissions. The Host retains result acceptance and completion decisions under every option.

### 3.4 Minimal local execution lifecycle

If a CLI is selected, one request prepares the environment and starts execution. The Host should not manually
assemble environment allocation, launch and bookkeeping for each run. Reuse project-defined setup and test
commands; generic devkit behavior should not force every consumer to use uv, pytest or just.

These command names are illustrative only, not existing commands or an accepted interface:

```sh
devkit test start --ref <commit-sha> --profile e2e --base <baseline-sha>
devkit test status <run-id>
devkit test logs <run-id>
devkit test clean <run-id>
```

Persist repository identity, fixed SHA, baseline, selected scope, commands, environment path, execution state,
timestamps, exit code and log locations. Keep evidence outside disposable environments. Separate preparation
failure, test failure and interrupted/unknown execution from success. Unknown execution stays pending investigation.
Cleanup preserves active runs and unrelated worktrees.

A repository script may establish the model first if its setup remains project-specific. Planning chooses one
initial implementation rather than parallel script and CLI schedulers. Any CLI follows
`CAP-ADV-agent-advisory-protocol` and `CAP-CLI-agent-cli-toolkit` with stable codes and deterministic actions.
Ordinary synchronous tests need no fresh environment allocation for every invocation.

### 3.5 Policy and evidence

Keep Git effects, verification evidence and policy-specific completion distinct. Success at A does not prove
its descendant B. Local batch coverage follows the actual tested commit and selected tests; required local
E2E remains pending until collected. Cloud completion follows the PR gate and merge, with merged-base stability
explicitly left to nightly detection. An E2E omission records a selection reason rather than an assumed pass.

Reconcile the retained design with `CAP-DLV-delivery-workflows`, `CAP-HARN-agent-guidance`,
`ADR-post-merge-verification`, source orchestration/integration guidance and repository verification instructions.
A lasting policy change needs a preliminary decision and the corresponding ADR on graduation. Explicitly bound
existing final-landed-verification requirements by route: retain local runtime synchronization, generated repairs
and final verification; document the cloud-base exception and its accepted detection delay. Recovery uses no
merge replay or automatic rollback. This draft does not silently change the active repository policy.

### 3.6 Expected acceptance scenarios

Planning refines these proposed scenarios into executable checks and measurement thresholds.

- **AC-1:** Given uncertain impact, selecting either tier expands to its full coverage without silently running
  the heavy tier in the synchronous phase.
- **AC-2:** Given either worker route, iteration uses unit/integration and relevant E2E when needed. Required
  premerge E2E evidence can come from branch checks or cloud PR CI; unrelated worker runs may omit it with reason.
- **AC-3:** Given a run for A, advancing main to B and synchronizing B's dependencies leaves A's files and
  environment isolated; the result still names A.
- **AC-4:** Given running E2E, another independent task starts before it finishes. Compare blocked time and total
  resource cost against the synchronous baseline rather than assuming an improvement.
- **AC-5:** Given intervening merges, the next run includes outstanding changes and no untested descendant is
  reported verified. Required verification is not deferred indefinitely.
- **AC-6:** Given a failed local result, the Host's next result check holds new merges, prioritizes repair and keeps
  completion pending until repaired coverage passes.
- **AC-7:** Given Host context loss or interruption, stored execution identity and evidence are recoverable;
  unknown execution is not success.
- **AC-8:** Given a completed run, cleanup retains readable evidence and leaves active or unrelated environments
  intact.
- **AC-9:** Given cloud-base with passing required PR CI including E2E, automatic merge completes the PR work
  without requiring latest-base merge-result validation or immediate postmerge CI.
- **AC-10:** Given failed required PR CI, automatic merge remains blocked and a rework request is routed without
  relying on an active Host session.
- **AC-11:** Given passing PRs whose combination breaks main, nightly detects the failure and routes follow-up
  repair with tested revision and failure evidence. The report states the accepted detection delay and does not
  claim the merged combination passed before nightly ran.
- **AC-12:** Given the cloud-base policy is selected, absence of immediate postmerge CI is not reported as an
  unmet gate. The same omission under local-base still leaves required local verification pending.

## 4. Lifecycle & Retirement Criteria

Retain this proposal as a Backlog draft. Planning measures representative costs, resolves spike questions,
chooses script or CLI ownership and narrows implementation boundaries. L estimates one integrated verification
capability. Independent platform work or unrelated test optimization requires a separate scope decision.

Acceptance follows direction review through the proposal workflow; Development starts through handoff. Graduation
reconciles the retained verification contracts and reports measured results without unmeasured speedup claims.
The dependent test-playbook proposal adopts the delivered policy and actual interfaces afterwards.
