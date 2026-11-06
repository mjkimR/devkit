# Coverage and resource assessment

## 1. Establish the native contract

Read the consumer's agent guide, test guide, scripts, runner configuration and actual CI commands/triggers.
Record each native command, selected coverage, exclusions, overlapping coverage, required/optional status,
prerequisites and trigger separately. Preserve affected-selection full fallbacks and required final
integrated-result checks. Nightly or manually dispatched CI establishes evidence only when it actually ran.
A Python pass establishes neither browser behavior nor native/storage compatibility.

Inspect what broad commands such as `npm test` or `pytest tests` collect; they can already include browser/E2E
coverage. Directory names and tier labels prove neither E2E existence, cost nor independent runnability.
Keep expensive integration tests under their existing ownership; cheap E2E tests need not be a heavy group.
Record measured duration and setup cost independently of semantics and resource isolation.

## 2. Clarify aims and recommend

Use code, tests, fixtures, scripts and CI for facts available in the repository. Ask only for missing aims that
change the recommendation, in a concise bundle: desired responsiveness, resource budget, tolerated delayed
failure detection or combined-main breakage, and observer/repair availability when relevant. Do not require every
answer when the decision does not depend on it. Keep unknown resource safety separate: leave affected execution
blocked until its boundary is clarified.

Prioritize the user's aims and synthesize a recommended arrangement from them and the observed contract. Explain
coverage, latency, resource cost and failure-detection tradeoffs. Where meaningful, compare the current setup and
a viable alternative; prescribe no option count. Recommend keeping the current setup when evidence favors it.
State remaining constraints and bounded candidate paths/validation with the recommendation in the existing single
change-decision round. Preference clarification supplies context, not consent to edits or integration authority.

## 3. Establish execution groups

Recommend frequent existing unit/integration iteration and selective premerge E2E when needed to demonstrate
changed behavior. Preserve required lint, types, rules, frontend and other native checks and conservative full
fallbacks. Do not replace light iteration with a blanket full-E2E policy.

Before recommending asynchronous separation, establish independently runnable groups from supported native
commands and map their combined coverage to every existing required check. Identify what the synchronous group
excludes and what the deferred group covers. Resolve overlapping commands before proposing deferral; adding a
duplicate E2E invocation establishes no reduced blocking or reduced run count.

If the suite is unseparated, unclear or has no independently runnable subset, keep its existing required commands
synchronous. Do not require an E2E definition, fabricate empty coverage or automatically restructure the suite.
Assess a proposed restructuring as a candidate with exact scope, coverage and validation in the same decision
round. Existing required checks remain until a decided change is routed and implemented through native workflow.

## 4. Inspect before execution

Read collection hooks and fixtures before invoking collection. Identify environment/configuration sources, shared
or disposable databases, model downloads/providers, temporary files, subprocesses, ports and async socket wakeups.
A database guard in one fixture does not protect other URL inputs. Distinguish a disposable schema from a safe
server/account choice. Clarify unknown inputs instead of printing credentials or guessing that serial is safe.
Check isolation between overlapping runs as well as workers within one run; a per-worker name alone can collide
across runs. Confirm that an active run's source and dependencies cannot change when the consumer's branch moves.

For example, a marker-based `test-fast` command can include embedded database and async tests: retain the marker
name, inspect its fixture requirements and report unavailable sockets before execution. An optional hardware
case can skip according to its contract; an unavailable required database check remains an unmet gate.

## 5. Findings and proposed changes

Record one row per concrete problem: location, observed boundary/resource, consequence, evidence, disposition,
proposed paths and expected validation. A short suite alone is not a reason to create recipes; a long suite alone
is not permission to remove coverage. Keep ownership and commands that already satisfy the consumer's needs.
Keep benchmark/stress work separate when its existing contract separates it; do not classify tests by latency.

Treat intentionally absent checks separately from unavailable required checks. Scheduling examples do not remove
a consumer's required final integrated-result check. Route a proposed requirement change through the same decision
round and native approvals; report the existing requirement until that change is authorized and implemented.

## 6. Report fields

- Inspected repository/revision/dirty paths and selected roots/goal; environment requirements and known limits.
- Native iteration/completion commands and triggers; coverage, exclusions, overlap and independent-group evidence.
- Exact tested SHA, command, selection baseline where applicable, environment, status, exit code and log location.
- Required checks passed, failed, pending or `not_run`; optional skips and the coverage they do not establish.
- Pending run IDs, outstanding coverage and next collection actions; an ancestor's pass establishes only that SHA.
- Prioritized user aims, repository evidence, recommended arrangement/reasons, meaningful alternatives and limits.
- Findings and keep/defer/change decisions, exact candidate paths, validation, destinations and remaining approvals/checks.
- Comparable measurements of Host blocking, run count, native execution, setup and resource contention separately.

Claim no speedup or default tuning promotion without comparable evidence. Overlap can reduce Host blocking while
preserving run count and native duration or increasing CPU and setup cost. Label examples/walkthroughs separately
from executed tests and performance evidence. Keep raw logs outside versioned reports and retain concise evidence
locations; require no publication, source archive or history service.

For a non-Python example, existing `npm test` and `npm run check` remain the native test/type boundary. Read their
scripts and fixtures before proposing groups; `npm test` can already include browser coverage. An unknown split
keeps both required commands synchronous. This is an example, not an actual application result.
