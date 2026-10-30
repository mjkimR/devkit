---
id: MAT-git-operator-development-evidence
title: Git-operator selected-model and lifecycle verification
summary: "Records Terra medium native continuation, guarded CLI mutation fixtures and a same-head role-disabled Host-burden comparison, separating replay and projection evidence from unmeasured mutation reliability, cost and latency."
status: active
created_at: 2026-10-30
---

# [MAT-git-operator-development-evidence] Git-operator selected-model and lifecycle verification

## Method and boundaries

`SPEC-local-orch-resource-manager` uses the accepted lean preset. The native Codex collaboration API was requested
with `model: gpt-6.1-terra`, `reasoning_effort: medium`, `fork_turns: none`. Named git-operator was unavailable in the
running tool registry, so a generic native subagent read the absolute effective contract. This is an emulated
route, not native role/path enforcement. The role used absolute worktree cwd and Git paths, current authority
and read-only jobs. Final matched-job `git status --short` was empty both before and after the agent returned;
no mutation was authorized to the probe. Effective source was read before sync and the installed contract after sync.

Exact native agent identity: `/root/resource_manager_dev/lean_operator_probe`. All four jobs used this identity;
later jobs used `collaboration.followup_task`, not a new spawn. This is continuation evidence in the current Codex
runtime. It does not test fresh-session named-role loading or provider-side model attestation.

## Repeated selected-model jobs

| Job | Input and actual action | Observed result | Evidence category |
| --- | --- | --- | --- |
| 1 | Read-only inspect-recovery at e302a20e89dcaec76afd45720c93c13037b1ea14 with active Development writer | Correct branch/refs, build-verify, tasks 0/2, 7 dirty paths; no mutation | Live read-only |
| 2 | Supplied partial CLI result, exit 0, merge reported landed, cleanup outstanding; active writer and no cleanup authority | needs_input; preserved CLI partial/exit 0 and outstanding worktree/branch effects; required Host inspection, quiescence and authority | Instructed replay; no actual merge |
| 3 | Installed contract, live state plus the same partial replay | Full result fields; current refs and 12 dirty paths; needs_input for replay cleanup, explicitly unmerged live state | Live read-only plus labeled replay |
| 4 | Matched read-only inspection at f6b55d073eea197c33dfb8129720167c8048af0c | completed for inspection; branch and refs match, 0 dirty paths, build-verify and tasks 1/2; no cleanup attempted | Live read-only |

Job 2 requested a field subset and returned that subset. Jobs 3–4 explicitly requested the complete role message
and returned identity, observed_refs, effects, checks, blockers, cli_result and unverified_areas. The probes did not
exercise lost-identity recovery, mutation retries or sandbox denial live. Those remain contract/review coverage.
The partial replay did not claim that a merge actually occurred.

## Same-head role-disabled comparison

Both modes inspected head f6b55d073eea197c33dfb8129720167c8048af0c and main
72002bdef9e6626f0ac0b4bf1d39ceb2aac53a8b, with no checkout or base mutation. With the role disabled the
implementer directly ran these commands; with it enabled job 4 ran exactly the same sequence:

1. `git -C <worktree> branch --show-current`
2. `git -C <worktree> rev-parse HEAD main`
3. `git -C <worktree> status --short`
4. `uv run --no-active devkit workflow next --unit specs/2026-10/20261030-local-orch-resource-manager`

All four commands exited 0. Their stdout lengths were 32, 82, 0 and 486 UTF-8 bytes, respectively (600 total);
stderr was empty. Both modes found the same branch, refs, clean tree, build-verify stage and tasks 1/2.

| Bounded burden proxy | Role disabled | Role enabled |
| --- | --- | --- |
| Operational CLI calls in Host context for the matched job | 4 | 0, plus one dispatch and result acceptance |
| Unplanned Host intervention/repair for the matched job | 0 | 0 |
| Instruction boundary for recurring worktree/integration jobs | 9,488 rendered UTF-8 bytes in worktree reference + spec-integrate | 2,956 UTF-8 bytes in dispatch reference |
| Raw command output entering Host context | 600 bytes | None required; structured role result replaces it |

Instruction byte counts use the installed local rendered files at this head. They measure the documented reading
boundary, not a randomized session experiment or a complete prompt. The enabled result itself repeats full
identity and authority-related fields and can be larger than the 600-byte raw output of this short job. Dispatch
payload, contract, nested context and acceptance observations add total tokens. Four repeated jobs establish
native identity reuse and correct bounded decisions; they do not demonstrate net token/cost savings, lower
latency, conversation availability or superiority in multi-unit mutation work. Neither mode required a human
intervention in this sample.

## Guarded mutation fixtures and checks

`uv run pytest packages/devkit/tests/integration/features/integration/test_cli.py -q -k
'integrate_cli_executes_after_host_conversation or integrate_cli_retries_observed_cleanup_without_merging_twice or
integrate_cli_refuses_source_changed_after_preparation or integrate_cli_refuses_target_changed_after_preparation or
partial_cleanup_warning_exits_zero_and_errors_print_last' --basetemp /private/tmp/devkit-git-operator-lifecycle`
passed 5 tests (15 deselected). These existing pytest-managed isolated Git fixtures performed real local
integration/cleanup and tested partial recovery and stale-ref refusal through the unchanged CLI. They are engine
mutation evidence, not Terra-driven mutation evidence. No activity repository merge, cleanup or branch deletion
was performed by these fixtures.

`just test-affected --base main` retained its full fallback and selected partial mode: 1,486 passed. Lint/format
and Pyright passed; sync --check and cumulative rules passed before the evidence-only stage commit. The focused
contract tests verify registration, all-host lean projections, existing project overrides, per-job authority,
Host ownership and zero-exit partial cleanup mapping. Every tracked sync output was `.devkit/installation.json`.

## Limits

Claude Code Sonnet medium and Antigravity Flash were projection-tested, not live exercised. Flash has effort
omitted; no high-effort guarantee or prompt-based effort emulation applies. Terra's actual lifecycle mutation,
cross-host continuation, native denial handling and missing-identity recovery remain unexercised. Tokens, cost,
reliable end-to-end latency and conversation availability were unavailable/unmeasured. Historical Luna/Sol
Planning evidence remains historical and is not transferred to Terra.
