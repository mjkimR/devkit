# Coverage and resource assessment

## 1. Establish the native contract

Read the consumer's agent guide, test guide, runner scripts and CI triggers. Record each command's selected scope,
its prerequisites and whether it is an iteration aid or a required completion check. Preserve affected-selection
fallbacks and final integrated-result checks. Nightly or manually dispatched CI is additional evidence only when
it actually ran. A Python pass establishes neither browser behavior nor native/storage compatibility.

## 2. Inspect before execution

Read collection hooks and fixtures before invoking collection. Identify environment/configuration sources, shared
or disposable databases, model downloads/providers, temporary files, subprocesses, ports and async socket wakeups.
A database guard in one fixture does not protect other URL inputs. Distinguish a disposable schema from a safe
server/account choice. Clarify unknown inputs instead of printing credentials or guessing that serial is safe.

For example, a marker-based `test-fast` command can include embedded database and async tests: retain the marker
name, inspect their fixture requirements and report unavailable sockets before execution. An optional hardware
case can skip according to its contract; an unavailable required database check remains an unmet gate.

## 3. Findings and proposed changes

Record one row per concrete problem: location, observed boundary/resource, consequence, evidence, disposition,
proposed paths and expected validation. A short suite alone is not a reason to create recipes; a long suite alone
is not permission to remove coverage. Keep ownership and commands that already satisfy the consumer's needs.
Keep benchmark/stress work separate when its existing contract separates it; do not classify tests by latency.

## 4. Report fields

- Inspected repository/revision/dirty paths and selected roots/goal; environment requirements and known limits.
- Native iteration and completion commands, observed resources and coverage gaps.
- Actual command/result pairs with required checks passed, failed or `not_run`; optional skips and missing coverage.
- Findings and keep/defer/change decisions, exact candidate paths, destinations and remaining approvals/checks.
- Measured runner evidence only when collected; otherwise no improvement claim. Keep raw logs outside versioned
  documents and use short summaries with evidence locations. No automatic publication or source archive.

For a non-Python example, an existing `npm test` plus `npm run check` remains the native test/type boundary.
Read its package scripts and fixtures first; label this as an example rather than a real application result.
