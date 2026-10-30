# Dispatching recurring lifecycle jobs

Create `git-operator` on the first lifecycle job for this Host conversation and repository through
`spec-delegate`'s [host route](../../spec-delegate/references/hosts.md). Reuse its exact agent identity for later
jobs through the host's native continuation (Codex `collaboration.followup_task`, Claude Code Agent resume,
Antigravity's supported continuation). Do not build a daemon or async scheduler. If identity or continuation is
unavailable, start a fresh instance from current observations and repeat current job authority; never infer it
from remembered approvals. After Host context loss rebuild the job from CLI/Git observations and current authority.

The Host keeps user decisions, unit scheduling, worker acceptance, semantic decisions and verification of returned
effects. Planning/Development workers remain one-shot. Before cleanup, quiesce writers and confirm their results;
no two writers may own one worktree. Serialize conflicting jobs within this conversation without promising a
global repository lock.

Each dispatch supplies the role contract's fields: operation, absolute repository/base/worktree, Unit/branch,
current source/target refs, exact intended_effects, current authority, allowed_boundaries, writers_quiesced,
expected_checks, prepared_digest where required, route and separate publication_authority. Repeat these for
every job even when the same operator remembers the Unit. A read-only job has no mutation authority.

Accept only a result with identity and observed refs matching the job, completed_effects and remaining_effects,
checks, blocker_codes and the original cli_result separately from role status. Verify effects with current CLI/Git
observations. Before starting a worker on a `prepare-worktree` or `handoff` result, compare its
`checks.worker_input` (`head`, `dirty_paths`) with your own `git -C <worktree> rev-parse HEAD` and
`status --porcelain`; start it only on a clean HEAD that is `checks.worker_input.head` or a descendant made only of
your own commits since (the post-handoff link fixes); an exit code alone never stands for ready input. `completed` requires every requested effect and check. A zero-exit partial cleanup with remaining
effects is `needs_input` or `failed`, never completed. Inspect unknown/partial state before dispatching a supported,
already-authorized remainder. Return changed scope/refs, dirty resources, active writers, source preparation,
semantic conflicts or denied permission to the Host. Normal integration already includes cleanup; dispatch no
redundant cleanup job.

The source contract selects `level: lean`: Sonnet medium, gpt-6.1-terra medium and Flash with effort omitted.
Existing project overrides remain available; no prompt-based effort emulation applies. Projection checks do not
prove live execution on every host. On emulated/unverified routes explicitly report contract/path checks and
per-operation permission requests as substitutes, never as native guarantees.

Direct mode follows existing procedures. If native spawning/continuation or needed permissions are unavailable,
use the documented fresh-instance/direct fallback only where host trust and authority permit; never bypass a refusal.
Operation-specific instructions and raw logs stay with the operator in
[operating procedures](git-operator-operations.md).
