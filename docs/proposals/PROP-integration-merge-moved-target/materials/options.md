# Options for merging a moved target at integration

Planning evidence for `PROP-integration-merge-moved-target`; sources are `envelopes/scout-01.yaml` and
`envelopes/scout-02.yaml` (paths relative to the repository root at plan base `fdba6646`).

## Where a moved target is refused today

| Path | Check | Moved `main` refused |
| --- | --- | --- |
| Local prepare and composed acceptance | `plan_finish` containment (`packages/devkit/src/devkit_agt/features/worktree/usecases/planning.py:104-108`) | yes, `WORKTREE_MERGE_NOT_FF` |
| Local integrate (advance after prepare) | `_land` rebuild with `advance=True` (`packages/devkit/src/devkit_agt/features/integration/usecases/service.py:616-641`) | no; conflict is `WORKTREE_MERGE_CONFLICT` |
| `ff-only` build | `packages/devkit/src/devkit_agt/features/worktree/services/merging.py:137-142` | yes, by definition |
| `devkit worktree finish --merge` | `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:1160-1164` | yes (no readiness provider) |
| Pull-request prepare | `packages/devkit/src/devkit_agt/features/integration/usecases/pull_request.py:140,156-160` | yes |
| Worker inspection, scope inputs, cleanup, handoff | fork-point or HEAD equality checks | no |
| Readiness `_unit_advance` | target changed the unit directory since the merge base (`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py:380-392`) | yes, a real overlap |

## Options

| Option | Evidence | Cost | Risk | Open questions |
| --- | --- | --- | --- | --- |
| Keep containment | Two manual base merges with reruns in one run on 2026-10-30 | none | ceremony stays | none |
| A: drop the refusal, check only at integrate | prepare digest from the source (`service.py:73-81,208`); integrate compares the result digest (`service.py:639-640`); `SPEC_POLICY` binds the result's `[tool.spec]` (`integration.py:372-377`) | small: `planning.py`, guard base | a target that changed an effective policy key or `[tool.spec]` refuses after approval on every retry until the base is merged; conflicts and CI-rule drift surface after the confirmation | none |
| B: prospective build at prepare (selected) | build, guards, readiness, digest and receipt checks already exist for later advances (`service.py:616-641`; PR execute `pull_request.py:360-379`) | medium: prepare runs `merge-tree` and CI rules on the result; digest excludes result-bound readiness; unsigned prospective build | Git 2.38 needed at prepare for a moved target; accept runs delivery readiness only after its acceptance commit | none blocking |
| B2: tree-only prospective check | `IntegrationContext.result_sha` and `providers.check` bind a commit (`contracts.py:70-71`, `providers.py:162-164`) | high: provider contract change | none beyond B | rejected for cost |
| C: merge the target into the task branch automatically | rewrites the approved source; checkout mid-merge | medium | conflicts left in the worktree; new approval per source | rejected |

B is selected because A's policy-digest failure is not a conflict or a failing check yet would refuse every retry,
and B moves conflicts and CI-rule drift before the user's confirmation. B would lose to A if the prepare-time cost of
CI rules on the result became prohibitive; no measurement exists, and the same rules already run at integrate.

## Batch test run

| Option | Evidence | Cost | Risk |
| --- | --- | --- | --- |
| Nightly CI only | `docs/development/ci-cd.md:5-11` | none | combined head untested for up to a day; failure not attributed |
| Per-unit rerun after each merge | `ADR-test-selection-and-ci` rejected a mandatory full suite per integration | one run per unit | repeats the cost the light merge removes |
| One run after the batch in `spec-orchestrate` Completion (selected) | `CAP-HARN-agent-guidance` "Repository verification policy": shipped skills follow the repository's policy | one run per batch | a selection miss still waits for nightly CI |
| CLI helper | devkit owns no repository test command | new command | none beyond the skill step |
