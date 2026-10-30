# Git-operator operating procedures

Read only the operation requested by the current job. Existing CLI checks own readiness, digests, routes and
cleanup identity; a role prompt cannot relax them. The Host retains business authority.

| Operation | Guarded procedure |
| --- | --- |
| `prepare-worktree` | From the retained base, run `uv run devkit worktree status` and scope inspection. With exact create/attach/setup authority run `uv run devkit worktree start <branch>` or `--existing-branch <branch> --unit <dir>`. Follow its returned path/setup. Return path, branch, HEAD, setup checks and `checks.worker_input`. A preparation list runs its items in the listed order, checks the retained base HEAD against the dispatched base ref before each and stops at the first item that is not completed; later items are not attempted. |
| `handoff` | From the retained base, inspect accepted proposal, refs and current proposal-handoff authority. Run `uv run devkit spec proposal handoff <slug> --effort <level>`. Return created worktree/Unit, the handoff `commit`, moved materials, ref checks and `checks.worker_input`; inspect status after partial effects before any supported retry. On `SPEC_HANDOFF_COMMIT_REFUSED` return the commit output and dirty paths to the Host; never commit or rerun the handoff yourself. |
| `prepare-integration` | Run `uv run devkit integration prepare <branch> --task-kind unit --task-id <id> --unit <dir> --route <route> --format json` from the retained base. Return exact scope/digest/readiness without mutation. Required source fixes and reconciliation return to the Host/implementer. |
| `execute-integration` | With exact current authority, run `uv run devkit integration integrate <branch> --task-kind unit --task-id <id> --unit <dir> --route <route> --expected-digest <digest>` from the retained base. Under retained-base auto policy the digest is optional; auto permits only local integration. Verify landing and included cleanup. |
| `cleanup` | Only for an inspected merged resource with remaining authorized cleanup, run `uv run devkit worktree finish <branch> --local-only` from the retained base. Use an owning extension's command only for the exact reported remaining target. Never reconstruct cleanup with force deletion. |
| `inspect-recovery` | Read `uv run devkit worktree status`, current refs, CLI advisory codes and relevant PR state where authorized. Return completed/remaining effects and supported next operation; inspection alone grants no repair authority. |

Planning acceptance is no operator job: the Host runs the composed `uv run devkit spec proposal accept <slug>
--by user|policy --mode accept_only|accept_and_handoff` itself, which already includes integration and cleanup.

Under ask policy the Host first presents source, target, report and effects and obtains conversational approval.
The digest is a concurrency guard, not an approval credential. Separate publication authority is required for a PR
or remote effect. Never write the user's integration OK to a file.

Local preparation merges a conflict-free moved target itself. For integration source preparation (a base merge after
a reported conflict or failing check, conflict decisions, required checks and Living Spec), return the exact work to
the Host/implementer using `spec-integrate` steps 1–4. Do not edit production sources.
If source code must run readiness, report `INTEGRATION_RULE_RUNTIME_MISMATCH` and the need for an authorized retained
runtime outside the removed worktree. No tool, path or runtime change may evade a refusal.

After unknown/partial results, inspect current source/target and cleanup identity. If merge landed, do not repeat
integration: execute only supported remaining cleanup within current authority. A moved target, changed digest or
expanded effects return to the Host for a fresh decision. Preserve original CLI exit/status/effects and stable
codes, including `INTEGRATION_CLEANUP_INCOMPLETE`. A zero exit may still leave cleanup incomplete. For a post-finish
extension failure inspect the exact extension target before the owning command; never add an unrelated cleanup job.

After bundle changes land, base synchronization is a separate explicit intended effect with appropriate path
permission. The Host accepts results and reports actual approval/policy authority; the operator grants none.
