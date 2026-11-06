# Verification evidence

## Scope and evidence limits

This unit authors a consumer playbook; it does not invoke test-management on devkit or change consumer suites.
The walkthrough below is instruction reasoning, not executed consumer tests, real CI evidence or a performance
measurement. No speedup or tuning promotion is claimed. Repository tests exercise isolated deployment and static
self-containment, not the decisions an agent will make in a consumer repository.

## Before/after method

The disabled-change baseline is accepted head b559c6dfce24075ff7d9a1b754ccdd74f5601312, inspected with
`git show <baseline>:<playbook-path>` without checking it out. Compare the same scenario inputs with the authored
source. The baseline has three playbook files and no execution reference/load condition; the changed source has
four files and one conditional execution reference. Baseline explicit invocation, resource safety, single decision
round and pytest comparison constraints were present and are retained. Baseline contains no independent-group
coverage split, fixed-SHA pending/descendant accounting, local/cloud scheduling/repair examples, wait/cleanup
semantics or explicit repository-evidence-plus-user-aims recommendation step. The changed instructions cover each
below. This before/after is a qualitative instruction-coverage measurement, not a client performance result.

## Procedural walkthrough

| AC | Scenario input | Expected instruction path and result | Source evidence |
| --- | --- | --- | --- |
| AC-01 | Consumer uses native scripts; devkit may be absent | Keep native commands and checks; optional generic fixed-SHA argv examples require no profile map or mode | SKILL section 2; execution sections 1/4 |
| AC-02 | Local run at A stays pending while main advances to C; then A passes or fails | Host retains SHA/baseline/run/coverage, collects later, holds merges and repairs failure/unknown, keeps C interval outstanding; A is never relabelled C | execution section 2; assessment report fields |
| AC-03 | Required DB prerequisite unavailable, optional hardware skip, failed native check, unknown run | Required not_run/unmet gate and failure/pending stay visible; optional omitted coverage is named; follow-up uses native workflow | SKILL constraints/decision/report; assessment sections 4/5/6 |
| AC-04 | Non-Python npm test includes browser cases; costly integration and cheap E2E exist | Read code/scripts/config/CI; keep native ownership; inventory coverage/cost/resources/independence separately | assessment sections 1/3/4 and final example |
| AC-05 | Parallel candidate has unequal IDs/skips or no comparable timing; overlapping runs wait less | Keep settings; compare same revision/set/environment, IDs/outcomes/skips/setup/cleanup and metrics; no speedup/default promotion | pytest sections 1/2; execution section 5 |
| AC-06 | Asset is retrieved without invocation; later invoked assessment gets unanswered edits | No assessment on retrieval; invocation permits assessment only; one change-decision round retains pending candidates, normal integration approval | SKILL entry/section 3/section 4 |
| AC-07 | Cloud PRs pass separately but combined main breaks; no active Host/postmerge CI | Required PR checks then auto merge under existing authority; explain nightly detection delay and accepted broken-combination risk without adding prospective merge/base refresh/queue/immediate CI prerequisites | execution section 3 |
| AC-08 | Required PR CI fails; later nightly fails; another consumer requires integrated-result verification | Preserve failed-PR merge block and rework; route nightly evidence to existing repair issue/workflow; retain the other consumer's final required check unless changed through existing decision round | execution section 3; assessment section 5 |
| AC-09 | Async recommendations absent, then requested; optional harness/spec/devkit absent | Load execution only for async/scheduling; no reference-to-reference links or external bundle/document assumptions; native runner remains valid | SKILL section 2; execution section 1; isolated bundle tests |
| AC-10 | Wait timeout/interruption, unknown execution, explicit cancel, cleanup failure after negative run | Observation ending does not cancel/remove; confirm managed stop, retain checkout; guarded cleanup only eligible inactive environment, original outcome/logs retained; tool delivery or later collection, optional verifier/Git-only operator | execution sections 2/4 |
| AC-11 | Unseparated or unclear suite, overlapping broad commands, no E2E; alternatively documented independent groups | Existing required commands stay synchronous absent established split; combined synchronous/CI or no-E2E suites still receive consultation/scheduling advice; async separation alone needs independent groups; no fabricated E2E/empty coverage; restructuring is a decision candidate | assessment sections 1/3; execution sections 1/2 |
| AC-12 | Repo already identifies commands/resources; responsiveness or delayed-detection tolerance is missing | Read code/tests/fixtures/scripts/CI first; ask only decision-relevant missing aims in a concise bundle; synthesize prioritized evidence-backed arrangement/reasons/tradeoffs; compare viable alternative where meaningful, keep current if favored; proposed edits/validation use same single change-decision round | SKILL sections 1/2/3/4; assessment section 2; execution section 1 |

The walkthrough confirms instruction paths for all twelve ACs. Existing native requirements remain authoritative;
accepted nightly risk describes the example, not a replacement for a consumer-required final check. Preference
clarification supplies recommendation context and is neither edit consent nor an additional policy-mode gate.

## Executed checks

Initial sync_start: `uv run devkit sync --check` PASS exit=0 before first edit, no drift. Source sync after edits:
PASS create=0 update=0 remove=0 seed=0; maintenance remained unselected and no tracked sync outputs were produced.

At parent HEAD 51a02d1638a08f0caadeb487a20beb7d65410ac1 plus the described source/unit working diff:

- `just test catalog tests/integration/bundles/test_bundles.py`: PASS 38 tests, including actual isolated maintenance
  preset deployment, four-file expectation, conditional loading, one-level references and self-containment budget.
- `just test-affected --base 72dcf58181c421a2904cc6acde54d4f6a673788c`: PASS 143 unit/integration tests, partial selection
  of 17 paths with selector full fallback retained. Repeated after consultation source update: PASS 143.
- `just lint-check catalog`: PASS Ruff check and 85 formatted files after formatting the changed assertion.
- `just check catalog`: PASS 0 errors/warnings. Production changes are Markdown; Python test change is structural.
- `uv run devkit rules check --ci --base 72dcf58181c421a2904cc6acde54d4f6a673788c`: PASS 22 rules on the initial source draft.
- `uv run devkit rules check --phase hygiene <source-playbook-directory>`: PASS 25 rules; unit rules PASS 22.
- `uv build --offline --package devkit-catalog --wheel --out-dir scratch/wheel`: PASS; ZipFile inspection confirmed
  all four packaged playbook files including references/execution.md. Later source wording retains same package paths.
- `uv run devkit generated check`: PASS checked=2 stale=0 skipped=0 at 51a02d1638a0; sync --check PASS no drift.

An initial `just test catalog integration/bundles/test_bundles.py` was rejected by the runner's area parser before
pytest; using the documented package-relative tests path passed. Initial unprivileged lint could not write the
sibling-worktree cache; the approved rerun exposed a formatting issue, repaired only in the owned test file.
These failures do not establish a test pass. Final committed-content checks and independent review follow below.

## Committed source verification and review

Source HEAD adbb4860a79089329c5921321231c4bc110b5a80: rules CI against retained baseline
72dcf58181c421a2904cc6acde54d4f6a673788c PASS 22; generated check PASS checked=2 stale=0 skipped=0.
Selected isolated E2E used `uv run devkit exec start --ref adbb4860a79089329c5921321231c4bc110b5a80 -- just test-affected --base 72dcf58181c421a2904cc6acde54d4f6a673788c --tier e2e`.
Run ID 43c8203ece6d47fc9dff06e585d55a47 completed PASS exit=0, four selected catalog paths, 4 passed in 5.74s.
Background `uv run devkit exec wait 43c8203ece6d47fc9dff06e585d55a47 --clean --format json` returned
observer=completed, cleanup=cleaned / EXECUTION_CLEANED. Original log/result retained under shared Git
`devkit/executions/43c8203ece6d47fc9dff06e585d55a47/`. The read of that own execution log is outside the
worker worktree and is verification evidence, not a read of another source checkout.

Independent medium code-reviewer PASS, no findings, exact reviewed source head adbb4860 and accepted audit base
b559c6df. Before/after temporary-index trees both 3aefe842089a22b2175f242b1f8aa148ed863951; actual HEAD and clean
status unchanged. Reviewer read no repository source/documents outside the worktree and made no probes/writes.
Boundary enforcement was emulated through absolute paths, explicit scoped payload and snapshot comparison.

## Source precision repair after initial review

The Host identified that execution section 1's independent-group condition could incorrectly gate all scheduling
examples, including ordinary cloud PR/nightly consultation for combined commands. Returned to build-verify,
narrowed the prerequisite to asynchronous separation and explicitly kept combined synchronous/CI and no-E2E
consultation valid. Cloud wording refers to existing/applicable E2E rather than creating a new tier requirement.
This repairs AC-11 precision without changing the accepted cloud risk or native required checks. Initial source
E2E evidence remains exact to adbb4860; the changed source receives its own verification below.

## Repaired source verification

Source HEAD bb1563952f4ece53dc2559c9e60b8e0643b2cf8d includes the AC-11 repair and both Living Spec drafts.
Affected unit/integration verification against 72dcf58181c421a2904cc6acde54d4f6a673788c PASS 144 on the same
precommit content, partial selection of 18 paths, full fallback retained. Rules CI at committed bb156395 PASS 22;
hygiene PASS 25, generated check checked=2 stale=0 and sync --check zero drift. Offline wheel rebuilt into
scratch/wheel-final contains all four playbook files; execution.md bytes exactly match final source.

Selected E2E launched with `uv run devkit exec start --ref bb1563952f4ece53dc2559c9e60b8e0643b2cf8d -- just test-affected --base 72dcf58181c421a2904cc6acde54d4f6a673788c --tier e2e`.
Run 888835679daa456fbd08df20b84cb758 PASS exit=0, 4 selected paths / 4 passed in 6.88s. Background
`uv run devkit exec wait 888835679daa456fbd08df20b84cb758 --clean --format json` returned observer=completed and
cleanup=cleaned / EXECUTION_CLEANED. Original logs/results remain under shared Git
`devkit/executions/888835679daa456fbd08df20b84cb758/`; reading this own run log is the only added external-worktree
verification read. Earlier adbb4860 results remain labelled to their actual SHA.

Fresh independent review02 PASS at bb156395, no findings; original twelve criteria traced and the exact no-E2E
failure condition verified. Reviewer before/after snapshot f49c4c2261ddc2ca5ded518259a6163cc8094a22 unchanged,
clean HEAD unchanged, outside_reads empty. No probes or source writes. Entrypoint derivation offered the playbook
directory and structure test; rejected both because existing SKILL.md is the single doorway for each contract.
The implementer's reflected targets are complete; separate reconciliation verification follows.
