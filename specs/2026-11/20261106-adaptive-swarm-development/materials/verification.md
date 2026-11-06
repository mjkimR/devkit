# Development verification and bounded semantic evidence

## Source and baseline

Accepted input fc02ef0ac798a8a2efc7c9f41ac0480f9c91dd07; retained main baseline 441bfde9603497c652d9cd6aac7c2688f0a2603a. Compared baseline manifest through git show (no checkout) with head manifest and actual bundle plan/projection tests: core grows from six to nine assets; public subagents from three to six, giving nine versus eighteen native files across three hosts. The new agents preset selects exactly three archetypes and nine native files. Recorded Planning prototype projected four agents/twelve files; that was prototype registration evidence, not shipped/runtime behavior. Current integration tests reproduce policy/extension/collision/preset isolation against shipped contracts. No performance baseline or speedup is asserted.

## Checks on source

- Integration: 12 tests PASS, real sync/projection/model policy and transactional collision preservation.
- Affected unit/integration at c1996ba434b8988612f5bc9aba707115ce8ff46d content: 146 PASS; command `UV_CACHE_DIR=/tmp/devkit-uv-cache just test-affected --base 441bfde9603497c652d9cd6aac7c2688f0a2603a`, mode=partial, 17 paths, full fallback retained. Later source edit only corrected installed E2E selection.
- Catalog lint/format and Pyright PASS; CI rules PASS on source commit c1996ba4. Repeat current required checks after docs before return.
- Installed E2E at de3e9af5634125e9ab16ebbcfb69fbc35a7e1ad0: command `UV_CACHE_DIR=/tmp/devkit-uv-cache just test-affected --base 441bfde9603497c652d9cd6aac7c2688f0a2603a --tier e2e`, partial selection of four installed consumers, 4 PASS in 9.79s. Adaptive test builds actual wheels without devkit-spec and checks agents-only under SDD. Log: /tmp/devkit-run-1000/c956a11347c1/20261106-222413-uv-run-jqu6jmhb.log.

## Execution supervision exception

Isolated run 9c1f721c93e6402fb1a5cebd278cfad2 at c1996ba434b8988612f5bc9aba707115ce8ff46d failed before setup/tests with `established group leader identity changed`. `exec wait --clean --format json` returned exit 2, phase/outcome/observer unknown and managed identity unresolved. No result.json or test result was produced. Host's supported cancel also returned unknown. Checkout and records remain preserved; no cleanup, cancellation success or passing result is claimed. Host authorized the established native E2E command synchronously after corrected source commit. This is a scheduling exception only; required E2E coverage is unchanged. No executor source or settings changed.

## Actual role-file coding exercise

The delivery worker acted as role lead with two generic leaf helpers reading the authored swarm-worker contract and builder overlay by absolute source path. Session count was Host + lead + two leaves = four; leaves received depth=2, allowance=0 and no children. This is generic contract emulation, not native registered-role invocation. Parent made no concurrent writes in either leaf checkout; all fixtures remain under the assigned ignored probes/aggregate-fixture path.

Host created a separate fixture repository and two writing worktrees. Seed 2a29a77ae4f6fcd4b71b8ef63d114698df3eb187 has json_mode.py and binary_mode.py disabled; full unittest checks at most one mode is enabled. Host alone handled fixture worktree setup and serial aggregation, with no real delivery-branch integration.

- wt-json owned only json_mode.py; leaf changed False to True, ran `PYTHONDONTWRITEBYTECODE=1 python -m unittest -v` (1 PASS), committed f010281eca271f7376b13d41a2a87ade71b2c05a and returned clean. Hypothetical push overlay was rejected as incompatible; no push attempted.
- wt-binary owned only binary_mode.py; leaf changed False to True, ran `python -B -m unittest -v` (1 PASS), committed 7a81cea46c1619a26c3fdf8d3aa92b56758d6926 and returned clean. With allowance=0 it completed directly without nesting or settings changes.
- Host serially merged both fixture results into combined-probe 03a7502fe9a9d1af62d1f3de69687842504e9355. JSON alone passed; combined unittest exited 1: `AssertionError: 2 not less than or equal to 1` at test_modes.py:7. This was a semantic aggregate failure, not a Git merge conflict. Fixture-base remained at seed; both leaf commits/worktrees were retained.
- Bounded repair/checkpoint follow-up asked binary leaf to disable its mode and stop before commit. It returned quiescent at HEAD 7a81cea46c1619a26c3fdf8d3aa92b56758d6926 with binary_mode.py dirty True→False and 1 passing local test. No commit, deletion, reset or cleanup occurred. Host verified that checkpoint and copied the returned binary repair into its own combined-probe checkout without editing the leaf. Combined unittest then PASS 1, exit 0; fixture repair commit 594bae1fcaf0125f37170f0ff5143f8dfd056433 retains the aggregate repair. The leaf remains dirty at its original HEAD and fixture-base remains at seed. The intentionally dirty checkpoint remains preserved. This is deliberate interruption simulation, not native process cancellation, and local repair pass does not establish aggregate repair.

## Authority and limits

Caller remained SDD throughout; no adaptive entry or approach change was invoked. Overlays narrowed ownership and could not grant push. Explicit absolute boundaries and actual Git comparisons substitute for native path confinement. Native named-role runtime invocation, Claude Code/Antigravity execution, native interruption/confinement, broad reliability, token cost and performance remain unverified. Packaging/projection success does not upgrade those claims.

Review snapshot before and after code-reviewer was c9170672895997c71a27de180558d5f587c37cf2; actual source/index/HEAD remained unchanged. Reviewer found only Given/When/Then formatting and trailing blank-line cleanup, fixed without changing behavior or coverage.
