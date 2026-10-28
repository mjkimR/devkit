# Runtime options and evidence

Planning inspected worktree head `bfab43d8a9d00aa26a6a7081e0d25f0cb5b742d9`, based on
`6ffb1ea17a1ee861318925ebd585d03777f2c637`. No source runtime, install or temporary probe was executed.

| Option | Evidence and benefit | Cost or failure | Recommendation |
| --- | --- | --- | --- |
| Retained target runtime only | Existing current Click tree and no additional install. | Cannot recognize branch additions, as `FB-readiness-cli-contract-checks-the-base-runtime` records. | Keep the default, not the sole recovery. |
| Explicit compatible installed executable | Existing `CAP-INT-mcp-services` recovery already permits separately authorized source-built code outside cleanup. Actual Click validation remains. | Host must build a retained installation; Existing repeated citation checks and digest guards must remain. | Recommended, with accurate diagnostics and required live check context. |
| Per-invocation runtime-path selector with subprocess worker | Could retain target integration engine and use another CLI checker. | Adds launch protocol, output validation, lifecycle and trust split; unnecessary while whole-process recovery is allowed. | Exclude from this bounded fix. |
| Source-supplied deterministic CLI manifest or AST extraction | Could avoid importing source code inside retained process. | No existing artifact proves installed plugin resolution, argument semantics or actual CLI behavior; declaration alone can bless invalid citations. | Reject as equivalent correctness evidence. |
| Automatic branch runtime build or skipped rule | Removes the observed refusal. | Violates retained integration's no automatic source judge or required readiness constraint. | Excluded by scope. |

## Source locations

- `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/rule.py:60-101`: root comes from
  current Click invocation; absent root returns no violations. Lines 103-178 describe command lookup, options,
  arguments, placeholders and passthrough behavior.
- `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py:139-153`: readiness evaluates
  linter rules and retains their failures. Lines 460-513 select committed source/prospective-result snapshots and
  build evidence; the snapshot does not replace the executing command tree.
- `packages/devkit/src/devkit_agt/features/integration/usecases/service.py:199-203`: interpreter/prefix guard
  protects the worktree being removed. It is not proof that an external virtualenv has no editable imports there.
- `packages/devkit/src/devkit_agt/features/integration/services/providers.py:118-137`: provider identity uses
  entry-point name/value and distribution version. Equal versions can contain different CLI surfaces.
- `packages/devkit/src/devkit_agt/features/integration/models/contracts.py:78-106,147-170`: evidence is hashed into
  the request and non-target-bound evidence is compared at builds. Existing freshness checks remain; identical runtime provenance is not proved or required.
- `packages/devkit/src/devkit_agt/features/integration/repositories/rule_runtime.py:134-157`: rule import checks
  concern receipt-listed synchronized imports, not arbitrary command/option compatibility.
- `packages/devkit/src/devkit_agt/features/integration/models/errors.py:65-74`: existing mismatch recovery names
  a separately authorized source runtime outside the worktree, with no readiness skip.

## Verification limits

Scout was read-only. Before/after Git tree snapshots matched
`757a0942f912848b708c39f34c669e4a6c80b8f8`, with unchanged HEAD. No read outside its worktree was reported.
A runtime wheel build, plugin traversal implementation and consumer projected-file targeting remain Development
verification. No runtime fingerprint or provenance attestation is proposed. Readiness repeats actual in-scope validation. No native role/path enforcement is claimed for the Codex emulated route.

## Challenger fold

Challenger identified that the initial full-tree fingerprint omitted group/leaf semantics and would eagerly load
uncited or exempt plugins. The final design removes that mechanism. Repeated actual citation validation is the
required outcome; environment identity is not needed to solve the source-feedback case. Both findings are closed
by removal, with AC4 preserving lookup/exemption semantics and AC5 covering missing check context.
Before/after Challenger tree snapshots matched `ddc6be6657747d0be61478b22d86b2186dccf0d4`, with unchanged HEAD.
No out-of-worktree reads were reported.
