# Planning evidence

## Repository scope and evidence

The repository base is `6df79c1c`; the Planning branch started at `dc1d7eca`. No production test/runtime source
changed during this investigation. Proposal/PADR content was being authored in the worktree while bounded
measurements ran; these are indicative costs, not a controlled before/after optimization benchmark.

- `scripts/affected_tests.py:470-517` selects impact before excluding most E2E. Explicit mappings and E2E edits
  bypass that exclusion. Full fallback returns no paths and the command delegates an unscoped full run
  (`:569-585`). Tier filtering must therefore also expand parent/full selections.
- `scripts/module.sh:93-99` performs `uv sync` for setup. `:109-115` uses the synchronous compact command runner.
- `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:254-280,297-372` resolves a requested
  revision, creates its checkout, runs project setup and restores locked managed assets. Setup/sync failures
  become notices for activity worktrees, which is insufficient to start a verified test run.
- `packages/devkit/src/devkit_agt/features/worktree/usecases/configured.py:27-50` exposes activity creation without
  the revision argument. An execution-only checkout API must retain worktree ownership without synthetic SDD Units.
- `packages/devkit/src/devkit_agt/features/compact/usecases/execute.py:164-186,225-280,437-467` owns synchronous
  command interruption and pruned logs. Reusing it as a detached manager would change its contract.
- `.github/workflows/ci.yml:9-18` declares reusable/manual CI, without push or PR triggers.
- `.github/workflows/nightly.yml:3-10,17-35` schedules 04:17 Asia/Seoul and calls reusable CI.
  `.github/scripts/nightly-ci.cjs:1-17` compares the scheduled SHA with the latest successful nightly wrapper.
- `ARCH-04-1-ecosystem-boundaries` sections 4-5 place cloud CI observation, remote dispatch and merge in autohub.
  `ARCH-04-2-delivery-policy` section 1 keeps operational modes transient. Neither is authority to configure an
  unnamed client or implement an external adapter in this repository.
- `ADR-post-merge-verification` and `CAP-DLV-delivery-workflows` section 4.8 currently require collected landed
  checks. The refined proposal preserves that boundary and adds asynchronous launch/collection instructions for
  local-orch; client operating examples are recommendations in the dependent playbook.

## Ownership alternatives

| Option | Reuse and cost | Risk and disposition |
| :--- | :--- | :--- |
| Repository script | Thin just recipe; lowest command registration cost | Lifecycle duplicated by client repositories; retain only as a measurement fixture |
| Separate `devkit exec` CLI | Worktree/project facilities; new command, state, supervisor, cleanup and tests | More implementation work; recommended for reusable environment issuance and result inspection |
| Dedicated verifier agent | Fresh diagnosis context | Still needs the same process/evidence infrastructure; optional only |
| git-operator or compact expansion | Existing actors/runner | Mixes Git jobs or synchronous interruption semantics with supervision; rejected |

The Scout returned repository evidence only. It wrote no files. During that call the Host created two PADR
scaffolds; the only new paths at return were those command-created scaffolds, with HEAD unchanged. This is an
emulated read-only boundary, not a native sandbox guarantee. Process survival and external resources remain
Development validation work.

## Bounded measurements

Machine: the local macOS Planning worktree. Commands used the worktree environment via `uv run --no-active`,
without xdist. Each row has one warmup and three measured repetitions. Wall time includes interpreter/CLI startup.
Every sample exited zero. These commands do not establish full-suite latency or peak resource consumption.

| Command set | Warmup (s) | Samples (s) | Median (s) | Executed result per sample |
| :--- | ---: | :--- | ---: | :--- |
| Affected selection/list | 0.160 | 0.116, 0.116, 0.115 | 0.116 | Selection only; no pytest |
| Document integration | 1.479 | 0.588, 0.606, 0.588 | 0.588 | 15 passed |
| Affected-selector E2E | 41.194 | 41.128, 39.211, 40.910 | 40.910 | 80 passed |

Exact command sets:

```sh
uv run --no-active python scripts/affected_tests.py --base 6df79c1c --list
uv run --no-active pytest -q \
  packages/devkit-docs/tests/integration/package/test_documented_codes.py \
  packages/devkit-spec/tests/integration/package/test_documented_codes.py \
  packages/devkit/tests/integration/features/rules/test_docs.py \
  packages/devkit/tests/integration/features/workflow/test_library.py \
  packages/devkit/tests/integration/package/test_documented_codes.py \
  tools/devkit-dev/tests/integration/test_bundle_citations.py
uv run --no-active pytest -q packages/devkit/tests/e2e/package/test_affected_tests.py
```

The selector E2E includes real subprocess/CLI checks, but does not represent every E2E suite. The document
integration set is a relevant bounded sample, not evidence that all integration tests are cheap. No speedup,
execution-count reduction, environment setup cost, CPU/memory benefit or full-suite classification is established.

## Development measurement and probe protocol

1. In the Development worktree, compare one fixed revision, command, environment, test selection and resource
   limits with the asynchronous path disabled/enabled. Warm up each path and take three comparable repetitions.
2. Record environment preparation, launch-return time, native command time, Host blocked time and peak resources
   separately. Report added environment/CPU cost alongside reduced blocking; do not promise a fixed speed ratio.
3. A test-owned latch proves that launch returns and independent work can finish while the native command is
   still running. This ordering check is deterministic and does not depend on timing a very short command.
4. Separate process probes cover launch-call completion, parent exit, missing terminal record, interruption,
   ownership mismatch and cleanup on macOS/Linux. Host application descendant-kill behavior and reboot survival
   remain outside the persistence guarantee.
5. Consumer fixtures use native test/build and non-pytest commands to verify that the lifecycle does not force Python test
   conventions. No real client, paid provider, external database or credentials are used.
6. Verify local-orch launch/collection and repair-priority guidance separately from runtime tests. Client local/cloud
   recommendations belong to the dependent playbook and do not create executor policy modes or profile maps.

## Interface refinement

`devkit run --help` confirms the current single-command shape, `devkit run [OPTIONS] COMMAND...`. Its parser
forwards arbitrary native argv and its interruption contract stops the command group. The root CLI has no
`exec` command at this Planning revision. Use a separate `devkit exec` group for isolated asynchronous execution
and its start/list/status/logs/cancel/clean operations. Do not extend `run` with subcommands or split launch into
`run` and inspection into `runs`. Test selection stays in the passed command; no profile or local/cloud setting
is introduced. Existing bounded measurements remain evidence about the initial E2E consumer, not a generic
build benchmark.
