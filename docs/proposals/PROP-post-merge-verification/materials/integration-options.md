# Integration options and source evidence

Read-only Scout inspected Planning head `1ed573b2cee19be3c112b85e1d3ae65fe4120d65`.
The before/after tree was `2dd491e59c20c932aeb6474d6f76cbee1e8211f5`. No runtime migration was executed.

| Option | Benefit | Cost | Decision |
| --- | --- | --- | --- |
| Existing target-runtime checks | Pre-land content refusal | Upgrade mismatch and scratch-runtime recovery | Replace |
| Automatic runtime verifier | Central sequence execution | Installation/subprocess/retry protocol | Excluded |
| Host final checks, deferred cleanup | Retains task checkout during failure | Additional cleanup phase | Not selected |
| Host final checks, current scoped cleanup | Existing commands and bounded Git operation | Repair after cleanup uses target/history | Selected |

Scout recommended deferred cleanup. The Host selected current scoped cleanup because the final commit and Git
history survive it, the agreed recovery occurs on the target, and another cleanup phase adds no required test input.
The Challenger must test that assumption against partial/unknown PR results and task-specific cleanup effects.

## Evidence inventory

- `CAP-INT-mcp-services` runtime contract, lines 152-163: target-installed runtime evaluates source rules;
  no automatic source-runtime build. Recovery/PR clauses, lines 170-186: partial effects and unknown outcomes.
- `CAP-GOV-evaluation-lifecycle` section 6: source receipt pins rule bytes, not the package code they import.
- `CAP-DLV-delivery-workflows` integration-provider section, lines 635 onward: source/merged snapshot readiness.
- `ADR-local-and-pull-request-integration` moved-target/PR and evidence clauses: readiness before landing and
  repeated result checks; preserve source pinning, platform checks and no cleanup on unknown remote outcomes.
- `ADR-delivery-approval-and-lifecycle-authority` decision drivers: readiness immediately before effects alongside
  independent approval/policy safeguards.
- `ADR-test-selection-and-ci` repository-test policy: later batch/nightly combined-head checks outside batches.
- `packages/devkit/src/devkit_agt/features/integration/cli.py:54`: prepare/integrate task metadata and claims.
- `packages/devkit/src/devkit_agt/features/integration/usecases/service.py:574`: existing cleanup after landing;
  lines 651-704: target-runtime guards/readiness/receipt checks.
- `packages/devkit/src/devkit_agt/features/integration/repositories/rule_runtime.py:1`: both source changes and
  consumer release upgrades can require missing imports.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py:192`: distinct acceptance
  preview must survive the generic integration simplification.

Scout examined incoming references for the touched core integration/worktree/delivery/governance contracts and
three decisions. Its unverified areas are exhaustive proposal-acceptance implementation and per-client setup
commands. Development must cover acceptance regression and use each client's documented setup procedure.
