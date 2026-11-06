# Delegation Patterns for Adaptive Development

## 1. Purpose and Evidence Boundary

This material compares design patterns for `PROP-adaptive-swarm-development`. It is a design comparison against
repository contracts, not a benchmark or a fresh audit of upstream implementations. The upstream repository links
below are retained as investigation leads. Their current behavior, agent counts and runtime guarantees have not
been independently verified in this Planning refinement.

- [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT): investigate role-oriented task decomposition.
- [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent): investigate host-integrated orchestration.
- [Yeachan-Heo/oh-my-codex](https://github.com/Yeachan-Heo/oh-my-codex): investigate coding-agent coordination.
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents): investigate reusable role documents.
- [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents): investigate specialist contracts.
- [wshobson/agents](https://github.com/wshobson/agents): investigate agent/role packaging.

No claim about comparative speed, correctness, dependency weight or filesystem isolation follows from these links.

## 2. Repository Evidence

| Existing contract or source | Observation | Design consequence |
| :--- | :--- | :--- |
| `CAP-DLV-adaptive-development` | Already covers implementation and optional product roles; excludes mandatory hierarchy and model routing | Add optional execution delegation rather than redefine adaptive work as a fixed pipeline |
| `adaptive_dev/bundle/bundle.toml` in devkit-catalog | Registers product-clarifier, product-researcher and usage-reviewer | Preserve these agents; zero-subagent installation is not the baseline |
| `CAP-DIST-agent-projections` | Neutral contracts project per host; emulated/unverified status is explicit | Registered agents do not establish universal native enforcement |
| `CAP-DIST-sync-and-transactions` | Bundle-qualified policy keys select existing subagent model levels | Reuse model policy; do not invent Pro/Flash routing or savings figures |
| `ARCH-04-delivery-strategy` | SDD includes worker delegation and depth-two review | Nesting is an existing repository pattern, not a unique swarm advantage |
| `ARCH-05-2-components` | Catalog bundles own self-contained content without runtime modules | Keep archetypes and role files in the owning bundle; no shared orchestration service |

The inspected intake baseline is commit `5a89b2eaebfe4559ce17cb533ed0a8382ac0fb77`.
Native runtime behavior was not exercised by reading these contracts.

## 3. Independent Design Axes

### Agent registration

| Choice | Reuse and extension | Cost or limitation |
| :--- | :--- | :--- |
| General agents with role overlays | Add task instructions without registering a persona | Invocation settings and capabilities depend on the host API |
| Prefixed execution archetypes with role overlays | Reuse stable execution contracts and add project specialists | Adds persistent metadata and host projection maintenance |
| Core domain agents with a role catalog | Direct recurring specialist calls | Domain decisions become public agent contracts |
| Every persona registered | Per-persona native configuration | Largest registry and maintenance surface |

The recommended default is prefixed execution archetypes with role overlays. General-agent overlays remain a
fallback. A project adds a registered specialist when its recurring execution contract warrants one.

### Delegation topology

| Choice | Suitable condition | Coordination cost |
| :--- | :--- | :--- |
| Direct | Small or inseparable task | Host performs the work |
| Flat | Independent bounded assignments | Host coordinates each result |
| Host → role lead → child | Lead has useful independent subtasks and capacity is available | Additional context handoff, aggregate verification and occupied slots |

A role lead can use the same public archetypes as a flat assignment. No additional lead agent type is necessary.
Registration and nesting are not competing architecture models.

## 4. Failure Cases to Exercise

1. **Capacity exhaustion**: waiting role leads occupy all available slots. The Host counts leads and children together
   and assigns child allowances before dispatch; insufficient capacity uses direct or sequential work.
2. **Parent/child writes**: a lead edits a checkout while its child owns it. Concurrent writing children use separate
   worktrees; parent integration starts after children finish.
3. **Permission mismatch**: a role asks a read-only agent to write. Reject the assignment or select a compatible
   agent; role text cannot expand permissions.
4. **Semantic integration conflict**: individually passing branches assume incompatible interfaces. Verify the combined
   result and repair before reporting completion; worktree isolation does not eliminate this case.
5. **Interruption**: children retain unmerged commits or dirty files. Preserve source identities, ownership and resume
   facts before cleanup; do not delete incomplete work automatically.
6. **Minimal installation**: docs/catalog lacks harness commands. Follow project checks and Git procedures, or serialize;
   do not silently add a dependency on SDD or the harness.
7. **Unavailable nesting**: the native runtime cannot create a grandchild. Flatten assignments and disclose the gap;
   do not alter host configuration.

## 5. Measurement Plan and Limits

Use one representative task with the same completion checks to exercise direct, flat and nested execution. Record
host/version, source SHA, task split, model settings, actual permission status, available slots, commands and outcomes.
Only compare runtime token/cost/latency metrics when exposed and comparable; otherwise mark them unmeasured.
Include a failure or interrupted run rather than measuring only successful execution.

No benchmark was run in this refinement. The removed token estimates, 70% savings claim, zero-conflict assertions
and universal native-sandbox claims had no supporting measurement in the proposal bundle.
