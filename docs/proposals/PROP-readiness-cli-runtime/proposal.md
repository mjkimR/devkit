---
id: PROP-readiness-cli-runtime
title: Validate branch CLI contracts with an explicit readiness runtime
summary: "Use an explicitly selected runtime outside cleanup scope to check branch CLI citations, without automatic source execution or weaker citation checks."
status: reviewing
created_at: 2026-10-28
target_area: capabilities/integration/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/
    - packages/devkit-spec/src/devkit_spec/features/delivery/usecases/
    - packages/devkit/tests/integration/features/integration/
    - packages/devkit-spec/tests/e2e/features/delivery/
    - docs/capabilities/integration/
    - docs/decisions/
  excludes:
    - packages/devkit-mcp/
    - packages/devkit/src/devkit_agt/features/integration/
task_kind: bugfix
workflow: sdd-proposal
---

# [PROP-readiness-cli-runtime] Validate branch CLI contracts with an explicit readiness runtime

## 1. Background & Hypothesis

`FB-readiness-cli-contract-checks-the-base-runtime` records a branch that added `--given` and documented it in the
same commit. Branch rules passed, while retained-base preparation rejected citations against the base Click tree.
`RULE-cli-contract` checks the running CLI, and the readiness provider runs that rule against committed source or
prospective-result bytes. Snapshotting the files does not snapshot their runtime.

`CAP-INT-mcp-services` already permits a separately authorized source-built runtime outside the worktree being
removed. The smallest direction is to make that explicit invocation usable for CLI changes, explain ambiguous
citation failures accurately, and preserve actual citation checks on every preparation and execution. The decision is
proposed in `PADR-explicit-readiness-cli-surface`; no runtime is built or executed during this Planning turn.

## 2. Technical Spike Questions

- **Q1, settled technically**: A missing command or option is evidence about the running Click tree, not proof of an
  invalid source citation or proof of runtime incompatibility. Preserve failure and disclose that distinction.
- **Q2, recommendation**: Select the runtime explicitly by invoking its installed executable from retained base.
  Keep actual Click-tree validation. Do not add a persistent selector, child-process execution service or branch
  metadata that substitutes a claim for validation.
- **Q3, settled technically after Challenger**: Repeated actual citation checking is sufficient for this fix.
  Retain existing request digest and readiness comparison. Do not require identical runtimes or introduce a
  whole-tree fingerprint; a changed runtime that still validates all checked citations is not itself a defect.

The Scout evidence and option comparison are in `materials/runtime-options.md`. No business question blocks
finishing the design; acceptance of the proposed direction remains the Host's `plan-accept` boundary.

## 3. Proposed Design & Impact

### Explicit invocation and recovery

The default remains the installed retained runtime. If it cannot recognize a citation, readiness MUST continue to
refuse with `INTEGRATION_NOT_READY`. The diagnostic MUST name `RULE-cli-contract`, citation location and unresolved
command or option, and explain that the selected runtime's CLI is the reference. It MUST NOT assert a proven runtime
mismatch merely because the source changes CLI files. The recovery is to correct an invalid citation, or obtain
separate Host authority to build and install a compatible runtime outside cleanup scope and prepare again with it.
The latter path still rejects a genuinely invalid citation.

The Host invokes the explicitly selected installed executable for both preparation and integration. For example,
`/retained/runtime/bin/devkit integration prepare dev-example --task-kind session --task-id dev-example -w /retained/base`
uses a retained installation and retained base independently. After authority under the owning policy, the same
executable runs integration with the prepared digest. This is an invocation pattern, not an automatic build command.
The runtime MUST be non-editable and its installed code and dependencies MUST remain accessible after cleanup.
A virtual environment outside the removed worktree with editable links into it does not satisfy this condition.
Development MUST verify this retained-installation recipe with wheel installations before documenting it as tested.

`INTEGRATION_RUNTIME_IN_WORKTREE`, receipt-reader checks and import-runtime checks retain their existing order and
meaning. Explicit runtime selection does not grant build, network, publication or integration authority. When the Host deliberately selects another runtime, prepare again. Under `ask`, present the resulting scope and
obtain authority for that scope; the existing digest precondition still rejects changed request contents. Under
`auto`, re-evaluate the retained base policy. No claim is made that equal digests prove identical environments. Automatic source runtime selection or execution is excluded.

### Check context and freshness

For a configured, enabled `RULE-cli-contract`, readiness MUST obtain a usable Click root or fail closed; the ordinary
library behavior of returning no violations without a root is not evidence of a readiness check. The CLI-contract
owner SHOULD expose a small public helper for root availability, without importing `devkit_dist.cli`. The provider
consumes it through the owning feature's public export. Ordinary library callers retain their existing behavior.
If the rule is disabled by existing project policy, the root precondition does not silently re-enable it.

Preserve existing file targeting, per-path `exclude` and `unchecked_commands`, argument/option semantics and lazy
lookup of paths that checked citations actually reach. Readiness MUST NOT enumerate uncited or exempt plugin
subtrees. An error encountered while checking an in-scope citation remains a refusal through existing rule/provider
handling. No new whole-tree plugin availability prerequisite is introduced.

The provider retains normal `CI_RULES`, source/result SHA evidence and existing disclosure/digest binding. Prepare,
integrate and prospective-result checks each evaluate actual citations against the selected running runtime.
`Readiness.comparable()` and supplied digest checks remain unchanged. A runtime change that causes a citation to
fail still blocks readiness before effects. Equal passing evidence proves the repeated checks passed; it does not
prove identical interpreters, implementation code or package provenance. Such identity is not required by this fix.

### Contract reflection and Development scope

`CAP-INT-mcp-services` needs an in-place clarification: the default runtime is target-built, while an explicitly
selected retained compatible installation is already allowed. Add the failure distinction,
retained installation requirement and prepare/integrate recovery to that contract. Its existing ban on integration
selecting or building source runtimes remains. Keep `RULE-cli-contract` guide and tests beside the rule. Promote
`PADR-explicit-readiness-cli-surface` at handoff under the normal proposal lifecycle.

Production scope stays in the CLI-contract feature and the spec readiness provider. Existing integration models
and service digest comparison remain unchanged. Tests may extend their integration
fixtures to prove stale evidence and existing guards. Follow `ARCH-05-2-components` for public feature exports,
layering and test ownership. This remains one M-sized bugfix and `dev_effort: medium`.

### Scope excluded

- No skip-readiness flag, rule suppression, silent CI substitution or automatic source execution.
- No static AST CLI extractor, persisted branch CLI manifest, runtime cache, launcher, installer or build service.
- No generic runtime provenance attestation, dependency/environment identity, CLI fingerprint or security sandbox.
- No MCP changes, provider ownership changes, receipt migration or integration authority changes.

## 4. Lifecycle & Retirement Criteria

Development starts only after proposal acceptance and handoff. Its spec MUST cover these acceptance scenarios:

- **AC1**: Given a branch adding a real option and its citation, the retained old runtime refuses; an explicitly
  selected retained wheel installation containing that option passes preparation and prospective-result readiness.
- **AC2**: Given that compatible runtime and a misspelled citation, readiness still refuses with the exact citation
  location. The diagnostic does not claim the source is necessarily wrong or runtime incompatibility is proven.
- **AC3**: Given a prepared request, a changed source, target or existing digest-bound evidence still refuses with
  a supplied old digest. Selecting another runtime never suppresses readiness or bypasses that precondition.
- **AC4**: Given a compatible runtime, configured per-path excludes and unchecked command paths keep their current
  semantics. An uncited or exempt lazy plugin is never loaded by a new traversal; an in-scope invalid citation or
  encountered plugin error remains a refusal.
- **AC5**: Given enabled CLI-contract checking and no usable Click root, readiness fails closed. The ordinary
  out-of-CLI library rule behavior stays unchanged; explicitly disabled rules remain governed by existing policy.
- **AC6**: Running from the removed worktree still refuses. A retained non-editable installation remains usable
  after source-worktree cleanup. `ask` stale-digest and retained-base `auto` authority still apply.
- **AC7**: Exercise a consumer fixture with a locked devkit upgrade and synchronized projected citations. Record
  which projected files are targeted; assert valid additions pass and invalid citations fail whenever in scope.

Verify rule tests, relevant provider/e2e and integration tests, lint/type checks, `just test-affected` and governance
checks during Development. Planning validates document boundaries and envelopes only; it does not claim these
scenarios have run. No timing or count improvement is claimed, so no base benchmark is required.

## Planning decisions

- Recommend explicit whole-process runtime invocation and repeated actual citation validation. The existing
  retained executor route is reused; the source does not select its own judge automatically.
- Remove the initial full-tree fingerprint design after Challenger identified incomplete semantics and unnecessary
  uncited-plugin failures. It is not required to establish the repeated citation checks this bugfix needs.
- Reject source-declared metadata as equivalent citation proof. Reconsider it only if a separate accepted design
  can establish the same actual command/option semantics and freshness.

## Source feedback

- `FB-readiness-cli-contract-checks-the-base-runtime` is promoted to this proposal. Planning does not resolve it or
  claim implementation; Development owns its acceptance checks.
