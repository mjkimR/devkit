---
id: PADR-explicit-readiness-cli-surface
title: Validate CLI citations with an explicitly selected retained runtime
summary: "For branch CLI additions, we reuse explicit retained-runtime invocation and repeat actual citation validation, to preserve readiness without automatic source execution, accepting a separately authorized runtime build."
proposal: PROP-readiness-cli-runtime
status: draft
created_at: 2026-10-28
---

# [PADR-explicit-readiness-cli-surface] Validate CLI citations with an explicitly selected retained runtime

- **Status**: Draft
- **Involved Components/Capabilities**: `CAP-INT-mcp-services`, `ARCH-05-2-components`, `RULE-cli-contract`

## 1. Context & Problem Statement

Readiness materializes branch files, but `RULE-cli-contract` uses the running invocation's Click tree. Branch CLI
additions fail under an older retained runtime. `CAP-INT-mcp-services` already permits explicitly building a
compatible installation outside removal scope with separate authority. Its target-built-runtime wording needs
this exception stated beside the default. A missing option does not prove whether a citation is invalid or the
selected runtime is incompatible. Library rule evaluation without a Click root currently checks no citations.

## 2. Decision Drivers

- Validate actual commands and options, including installed plugins reached by citations.
- Preserve readiness, retained-base policy authority and source/result snapshot checks.
- Preserve the prohibition on automatic source runtime selection or execution.
- Keep runtime code and dependencies available through worktree cleanup.
- Avoid new process, manifest or plugin traversal contracts when existing execution suffices.

## 3. Considered Options

1. Keep target-runtime-only checks: no build cost, but valid branch additions remain impossible to prepare there.
2. Explicitly invoke a compatible retained installation: uses the existing recovery boundary and repeated actual
   validation; needs a separately authorized build and precise failure guidance.
3. Add a runtime-path flag and child checker: retains a target executor but adds process and trust protocols beyond
   the existing whole-process recovery path.
4. Read source-supplied CLI metadata or statically extract decorators: avoids source imports, but does not prove
   installed CLI/plugin semantics. A producer's claim is insufficient replacement evidence.
5. Fingerprint the complete runtime CLI tree: detects differing trees but forces lookup of unvisited plugins and
   adds semantic canonicalization unrelated to whether repeated in-scope checks actually pass.
6. Skip checks on CLI-changing branches or build their runtime automatically: conflicts with stated constraints.

## 4. Decision Outcome

Recommend option 2. The Host explicitly invokes a compatible installed executable for prepare and integrate from
retained base. It obtains build/execution authority separately. Integration never builds or selects a source
runtime itself. Installation is non-editable and retained beyond cleanup.

Each readiness evaluation still validates actual targeted citations, including the prospective result. For enabled
CLI-contract checking, require a usable Click root rather than accepting a no-context library result as proof.
Preserve configured exclusions, unchecked command paths and lazy lookup of only paths reached by checked citations.
Keep existing `CI_RULES` evidence, request digest and readiness comparison. Equal passing evidence does not attest
identical environments; this bugfix requires repeated valid citations, not a provenance mechanism.

Unknown citations remain failures against the selected runtime. Explain both recoveries without falsely choosing
one: repair an invalid citation, or separately authorize/select a compatible retained installation and prepare
again. Preserve runtime-location, receipt-reader and import-runtime guards and their ordering. Runtime selection
never grants authority or relaxes digest checks.

This clarifies and extends `CAP-INT-mcp-services` with the CLI failure/recovery and check-context contract. It does
not supersede `ADR-host-cli-lifecycle-authority`: the Host still carries conversational decisions under `ask`, and
retained base policy still supplies `auto` authority.

## 5. Consequences

Valid additions can pass through an existing explicit-runtime route, while bad citations continue to fail.
No extra plugin subtree is loaded to construct an environment fingerprint. Host build/install work remains manual
and separately authorized. Source provenance and complete environment identity are not attested. A runtime-path
selector becomes relevant only if a later accepted requirement prohibits whole-process recovery.

## 6. Confirmation

Development extends rule-local tests, spec readiness e2e tests and integration digest/guard fixtures. Proposal
AC1–AC7 cover real additions, invalid citations, stale digests, configured exemptions/lazy plugins, unavailable Click
roots, retained wheel cleanup and consumer upgrades. Review confirms no automatic execution, readiness bypass or
authority change. Review only for build provenance and separately granted Host authority; no attestation mechanism
is added.
