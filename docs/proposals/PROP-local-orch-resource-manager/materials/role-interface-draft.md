# Lifecycle resource manager interface draft

This is Planning input for the spec bundle role, not an installed agent contract.

## Host dispatch

Create `resource-manager` on the first lifecycle job for this conversation/repository. Reuse its exact agent
identity for later jobs; a missing identity starts a new instance with current state. Use the host's native
subagent continuation rather than an additional daemon. Keep the main conversation for decisions and coordination.

Each job contains:

- `operation`: prepare-worktree, handoff, prepare-integration, execute-integration, cleanup or inspect-recovery.
- Absolute repository/base/worktree paths, branch and Unit identity, relevant source/target refs.
- Exact intended effects and the Host-carried authority for this job, or a read-only preparation request.
- Prepared digest where applicable; route and separately authorized publication effects.
- Whether writers have been quiesced, expected checks/evidence and the scope of permitted mutations.

The minimum payload repeats current authority/identity even when the manager remembers the unit.
The Host verifies the returned effects and retains result acceptance.

## Manager procedure

1. Read the operating reference for this operation. Confirm identity and current state before mutation.
2. Stop at missing authority, unexpected scope, dirty resources, active writers or unavailable host permission.
3. Run the existing guarded operation with exact arguments. Use the retained base for commands that remove
   worktrees. Do not reconstruct cleanup with raw force operations.
4. Inspect unknown or partial effects before choosing only the remaining supported operation. Preserve recovery
   identity; return unverified repair commands rather than executing them.
5. Return a concise result. Do not ask the user directly or supply business approval.

The manager does not author production fixes, resolve semantic conflicts, reinterpret acceptance, change policy
or grant publication. Source preparation/reconciliation belongs to the implementer or Host. A readiness refusal
returns the required work and evidence without claiming completion.

## Result

Return `status: completed|needs_input|failed`, repository/Unit identity, observed source/target refs, completed
effects, remaining effects, checks and stable blocker/advisory codes. A process exit of zero does not override a
partial status. Report whether any output or host evidence was unavailable. Full command output stays in the
manager context or retained task evidence; it does not enter the main conversation unless the Host needs it.

These are role message fields, not a new persisted journal or CLI schema. Keep default summary within one short
paragraph plus parallel effect/check entries; allow necessary details for a material decision.
