# Asynchronous execution and scheduling recommendations

## 1. Preserve the consumer's verification contract

Recommend asynchronous separation only after establishing independently runnable groups with complete required
coverage. Keep existing required commands synchronous when the split is unclear, unseparated or overlapping.
Consultation and scheduling recommendations still apply to combined synchronous/CI commands and suites without
E2E; do not infer an E2E requirement from these examples.
Use the consumer's documented command prefix and native-compatible execution/CI tools; devkit, a harness, a spec
workflow and a verifier subagent are optional. Introduce no local/cloud mode, profile map or policy selector.
Keep concrete merge scheduling and integration authority with the consumer's existing orchestrator.
Use the user's responsiveness, resource and failure-detection preferences to explain the recommended arrangement;
clarify missing observer/repair availability when it changes that recommendation. These examples do not ask the
user to choose a local/cloud policy mode, and preference answers authorize no configuration edits.

## 2. Active local Host example

Recommend frequent worker unit/integration checks and selective E2E when needed to demonstrate changed behavior.
After approved landing, recommend the established light synchronous group, including required native checks,
then selected asynchronous E2E when independently runnable. Keep required verification pending while independent
work proceeds; bounded merge batches can overlap waiting only within the consumer's existing completion rules.

Have the direct Host retain each tested SHA, native command, selection baseline, covered interval and run ID.
Have the Host collect results and prioritize repair at the next failed or unknown result check; hold further
merges then. Keep the earliest baseline for outstanding changes when accumulating batches. If A runs while main
advances to C, report A as A and keep the added interval outstanding. A passing ancestor does not satisfy C's
required verification; establish the consumer's required current-head coverage before declaring completion.
Use an explicit empty selection only when the native selector actually reports it for the complete outstanding
interval; never invent absent E2E coverage.

Start with one outstanding run when CPU, setup or service contention warrants it. Allow more only with measured
capacity and independent resource namespaces; this advice is not an executor limit. An optional verifier can
collect or diagnose evidence. Keep Git operators restricted to Git lifecycle work; the Host owns collection,
repair routing and completion.

## 3. Cloud PR example without an active Host

Recommend worker unit/integration and necessary selective E2E where it exists, followed by the consumer's required
PR CI including its existing required E2E coverage. A combined native command can supply that coverage; require no
new E2E definition for a suite without it. Preserve the merge block on failed required PR CI, rework the change and rerun required checks. With the
consumer's existing authority, automatic merge follows passing required PR checks. This example intentionally
has no immediate postmerge CI: separate passing PRs can break the combined main until nightly detection.

Explain that accepted risk and the actual nightly trigger/delay. Do not make latest-base prospective merge tests,
forced base refresh, merge queues, immediate postmerge CI or an always-on Host prerequisites for this example.
An intentionally absent postmerge check is different from an unavailable required check. Preserve a consumer's
existing required final integrated-result checks; propose any requirement change through the same decision round.
This is a scheduling recommendation with accepted risk, not a new completion-policy mode.

Name the consumer's existing nightly repair mechanism and responsible workflow. For example, if failed nightly
jobs create repair issues in that repository, route the failing SHA, native command, coverage and logs into that
issue for the next repair worker; rerun the consumer's required repair checks. If no repair mechanism is documented,
report the gap and propose one in the same decision round. Require no adapter or recipient schema. A later nightly
failure is follow-up repair evidence, not proof that the merged combination passed earlier.

## 4. Optional devkit execution example

When `devkit exec` is available, inspect installed help and setup/resource prerequisites before use. Resolve a full
locally available fixed commit SHA; pass the native argv after `--`. Use the consumer's documented invocation
prefix in place of bare `devkit` below. These generic placeholders are examples, not executable consumer commands:

```sh
devkit exec start --ref <full-commit-sha> -- <native-command> <native-args>
devkit exec wait <run-id> --clean --format json
```

Run the waiter through the execution tool as a background call, then continue independent work. Collect its final
result from the tool's completion delivery; if that tool does not deliver completion, collect later with
`devkit exec status <run-id>` or `devkit exec wait <run-id> --format json`. CLI launch alone provides no push
notification to an agent. Record the native result and cleanup result separately; launch, pending, unknown and
cleanup success establish no test pass. Keep the original negative outcome and retained logs when cleanup fails.

Keep the checkout by default when native artifacts are needed for diagnosis; omit `--clean` in that case.
`wait --clean` requests guarded cleanup only after a durable terminal result. `wait` timeout or interruption ends
observation only; it neither cancels execution nor removes the environment. If stopping is required, use
`devkit exec cancel <run-id>` and confirm managed execution stopped; cancellation retains the checkout. Use
`devkit exec clean <run-id>` only for an eligible inactive environment; unknown ownership is not cleanup authority.
Execution manifests and logs remain readable after cleanup. Record cleanup failure independently of the original
execution result and retain the next collection/repair action. Host process-kill policies, app exit and reboot
provide no process-survival guarantee.

## 5. Evidence before recommendation

Compare the same revision, selected coverage, environment and outcome before claiming improvement. Measure setup
and resource contention as well as native duration and Host blocking. Overlapping verification can reduce waiting
without reducing run count, duration or CPU. Without comparable results, report the evidence limit and promote no
default tuning. Report assessment completion separately from actual test passes and native delivery completion.
